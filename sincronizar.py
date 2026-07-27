#!/usr/bin/env python3
"""
sincronizar.py — genera marcas de karaoke a partir de un audio y su letra.

    python sincronizar.py cancion.mp3 letra.txt
    python sincronizar.py --carpeta-audio Audios --carpeta-letras Letras

letra.txt: una línea de la canción por línea del archivo. Las líneas vacías y
las que van entre corchetes ([Coro], [Verso 1]) se ignoran.

Salida: marcas.json (para la app Cortafuego) y cancion.lrc (estándar de karaoke).
En modo carpeta, cada canción se empareja por nombre (letra "NN_Titulo.txt" con
el audio "Titulo.mp3") y se escribe en --carpeta-salida (por defecto "Marcas").

Estrategia, en orden de importancia:
  1. Separación de voz          — aísla el canto del acompañamiento
  2. Detección de actividad     — encuentra CUÁNDO se canta, sin transcribir
  3. Auto-similitud musical     — ubica coros y versos repetidos
  4. Reconocimiento de voz      — sólo para anclar el primer tramo de cada sección
  5. Grilla de pulso + ataques  — pule las décimas

El paso 4 es el más lento y el menos decisivo. Con --rapido se omite: el script
pide un ancla manual por sección y el resto sale de la estructura.
"""
import argparse, json, os, re, subprocess, sys, time, unicodedata
from difflib import SequenceMatcher

import numpy as np
from scipy.io import wavfile
from scipy.signal import stft
from scipy.ndimage import uniform_filter1d


# ---------------------------------------------------------------- utilidades
def log(msg): print(msg, flush=True)

def norm(s):
    s = unicodedata.normalize('NFD', s.lower())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return re.sub(r"[^a-z0-9ñ ]", ' ', s)

def leer_letra(ruta):
    lineas, seccion, secciones = [], 'Sección 1', []
    for cruda in open(ruta, encoding='utf-8'):
        t = cruda.strip()
        if not t:
            continue
        if t.startswith('[') and t.endswith(']'):
            seccion = t[1:-1].split('-')[0].strip()
            continue
        lineas.append(t)
        secciones.append(seccion)
    return lineas, secciones

def a_wav(entrada, salida, sr=44100, mono=False):
    cmd = ['ffmpeg', '-v', 'error', '-i', entrada, '-ar', str(sr)]
    if mono: cmd += ['-ac', '1']
    subprocess.run(cmd + [salida, '-y'], check=True)
    return salida

def leer_mono(ruta):
    sr, x = wavfile.read(ruta)
    if x.ndim > 1: x = x.mean(axis=1)
    x = x.astype(np.float32)
    return sr, x / (np.abs(x).max() + 1e-9)


# ------------------------------------------------------ 1. separación de voz
def separar_voz(mp3, tmp):
    destino = os.path.join(tmp, 'sep', 'htdemucs', os.path.splitext(os.path.basename(mp3))[0], 'vocals.wav')
    if os.path.exists(destino):
        log('  voz ya separada, se reutiliza')
        return destino
    log('  separando voz (puede tardar varios minutos en CPU)...')
    r = subprocess.run([sys.executable, '-m', 'demucs', '-n', 'htdemucs', '--two-stems=vocals',
                        '-d', 'cpu', '--segment', '7', '-j', '1',
                        '-o', os.path.join(tmp, 'sep'), mp3],
                       capture_output=True, text=True)
    if not os.path.exists(destino):
        log('  no se pudo separar la voz; se sigue con la mezcla completa')
        log('  (' + (r.stderr or '').strip().splitlines()[-1][:120] + ')' if r.stderr else '')
        return None
    return destino


# ------------------------------------------ 2. actividad vocal (frases)
def detectar_frases(ruta_voz, min_hueco=0.28, min_largo=0.22):
    sr, x = leer_mono(ruta_voz)
    H, W = int(sr*0.010), int(sr*0.040)
    n = (len(x) - W)//H
    rms = np.array([np.sqrt((x[i*H:i*H+W]**2).mean()) for i in range(n)], dtype=np.float32)
    db = uniform_filter1d(20*np.log10(rms + 1e-7), 9)
    t = np.arange(n)*H/sr
    piso, techo = np.percentile(db, 20), np.percentile(db, 97)
    act = db > piso + 0.30*(techo - piso)

    def limpiar(m, hueco, largo):
        m = m.copy(); i = 0
        while i < len(m):                       # cerrar huecos cortos
            if not m[i]:
                j = i
                while j < len(m) and not m[j]: j += 1
                if 0 < i and j < len(m) and (j-i) < hueco: m[i:j] = True
                i = j
            else: i += 1
        i = 0
        while i < len(m):                       # borrar destellos
            if m[i]:
                j = i
                while j < len(m) and m[j]: j += 1
                if (j-i) < largo: m[i:j] = False
                i = j
            else: i += 1
        return m

    act = limpiar(act, int(min_hueco/0.010), int(min_largo/0.010))
    frases, i = [], 0
    while i < len(act):
        if act[i]:
            j = i
            while j < len(act) and act[j]: j += 1
            frases.append((float(t[i]), float(t[min(j, len(t)-1)])))
            i = j
        else: i += 1
    return frases


# --------------------------------------------------- 3. auto-similitud
def rasgos(ruta):
    sr, x = leer_mono(ruta)
    f, t, Z = stft(x, fs=sr, nperseg=2048, noverlap=1536)
    S = np.log1p(np.abs(Z)*50)
    bandas = np.logspace(np.log10(60), np.log10(6000), 41)
    idx = [int(np.argmin(np.abs(f-b))) for b in bandas]
    F = np.stack([S[idx[i]:idx[i+1]+1].mean(axis=0) for i in range(len(idx)-1)])
    return F/(np.linalg.norm(F, axis=0, keepdims=True) + 1e-9), float(t[1]-t[0])

def buscar_repeticion(F, hop, ini, fin, evitar, n=1):
    a, b = int(ini/hop), int(fin/hop)
    T = F[:, a:b]; L = T.shape[1]
    if L < 10 or F.shape[1] - L < 10: return []
    p = np.array([float((T*F[:, s:s+L]).sum()/L) for s in range(F.shape[1]-L)])
    ts = np.arange(len(p))*hop
    for e0, e1 in evitar:
        p[(ts > e0-6) & (ts < e1+6)] = -1
    out = []
    for _ in range(n):
        k = int(np.argmax(p))
        out.append((float(ts[k]), float(p[k])))
        p[max(0, k-int(8/hop)):k+int(8/hop)] = -1
    return out


# ------------------------------------------------------ 4. anclas por voz
def anclas_asr(ruta_voz, ruta_mezcla, lineas, prompt):
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        log('  faster-whisper no está instalado; se omiten las anclas por voz')
        return {}
    m = WhisperModel('base', device='cpu', compute_type='int8')
    pasadas = []
    for f in filter(None, [ruta_voz, ruta_mezcla]):
        for pr in (prompt, None):
            segs, _ = m.transcribe(f, language='es', word_timestamps=True, vad_filter=False,
                                   beam_size=5, temperature=0.0,
                                   condition_on_previous_text=False, initial_prompt=pr)
            pasadas.append([(norm(w.word).strip(), float(w.start))
                            for s in segs for w in (s.words or []) if norm(w.word).strip()])
    palabras, de_linea = [], []
    for i, ln in enumerate(lineas):
        for w in norm(ln).split():
            palabras.append(w); de_linea.append(i)

    def alinear(asr):
        n, mlen = len(palabras), len(asr)
        if mlen < 10: return {}
        GAP, BAND, NEG = -0.55, 200, -1e9
        prev = [NEG]*(mlen+1); prev[0] = 0.0
        for j in range(1, min(mlen, BAND)+1): prev[j] = prev[j-1]+GAP
        ptr = []
        for i in range(1, n+1):
            cur = [NEG]*(mlen+1)
            lo, hi = max(1, int(i*mlen/n)-BAND), min(mlen, int(i*mlen/n)+BAND)
            if lo == 1: cur[0] = prev[0]+GAP
            row = bytearray(mlen+1)
            for j in range(lo, hi+1):
                s = 1.0 if palabras[i-1] == asr[j-1][0] else SequenceMatcher(None, palabras[i-1], asr[j-1][0]).ratio()
                d, u, l = prev[j-1]+(2*s-0.75), prev[j]+GAP, cur[j-1]+GAP
                best, k = d, 1
                if u > best: best, k = u, 2
                if l > best: best, k = l, 3
                cur[j], row[j] = best, k
            ptr.append((lo, hi, row)); prev = cur
        res, i, j = {}, n, mlen
        while i > 0 and j > 0:
            lo, hi, row = ptr[i-1]
            if j < lo or j > hi: break
            k = row[j]
            if k == 1:
                s = 1.0 if palabras[i-1] == asr[j-1][0] else SequenceMatcher(None, palabras[i-1], asr[j-1][0]).ratio()
                if s >= 0.75: res[i-1] = asr[j-1][1]
                i -= 1; j -= 1
            elif k == 2: i -= 1
            else: j -= 1
        return res

    votos = {}
    for p in pasadas:
        for idx, t in alinear(p).items():
            votos.setdefault(idx, []).append(t)
    # consenso: sólo lo confirmado por 2+ pasadas
    por_linea = {}
    for idx, ts in votos.items():
        if len(ts) < 2: continue
        ts = sorted(ts)
        grupo = max((([u for u in ts if abs(u-t0) <= 0.6]) for t0 in ts), key=len)
        if len(grupo) >= 2:
            por_linea.setdefault(de_linea[idx], []).append(float(np.median(grupo)))
    return {li: float(np.median(v)) for li, v in por_linea.items()}


# ---------------------------------------------- 5. pulso y ataque exacto
def grilla_pulso(ruta_mezcla, dur):
    sr, x = leer_mono(ruta_mezcla)
    f, t, Z = stft(x, fs=sr, nperseg=1024, noverlap=768)
    S = np.log1p(np.abs(Z)*100)
    flujo = np.maximum(0, np.diff(S, axis=1)).sum(axis=0)
    flujo = uniform_filter1d(flujo, 3)
    flujo = np.maximum(0, flujo - uniform_filter1d(flujo, 60))
    hop = float(t[1]-t[0])
    ac = np.correlate(flujo, flujo, 'full')[len(flujo)-1:]
    lo, hi = int(0.30/hop), int(1.10/hop)
    per = float(np.argmax(ac[lo:hi]) + lo) * hop
    fases = np.arange(0, per, 0.005)
    def fuerza(ph):
        idx = ((np.arange(ph, len(flujo)*hop, per))/hop).astype(int)
        idx = idx[idx < len(flujo)]
        return flujo[idx].mean() if len(idx) else 0
    fase = float(fases[int(np.argmax([fuerza(p) for p in fases]))])
    pulsos = np.arange(fase, dur, per)
    return per, 60.0/per, np.sort(np.concatenate([pulsos, pulsos + per/2]))

def pie_ataque(rms, tt, sr, H, t):
    i = int(t*sr/H)
    n = len(rms)
    if i <= 0 or i >= n: return t
    ini = max(0, i - int(0.45*sr/H))
    tramo = rms[ini:i+int(0.10*sr/H)]
    if len(tramo) < 5 or tramo.max() < 1e-4: return t
    idx = np.where(tramo <= tramo.max()*0.15)[0]
    if not len(idx): return t
    nuevo = float(tt[min(ini+idx[-1], n-1)])
    return nuevo if 0 <= t-nuevo <= 0.40 else t


# ------------------------------------------------------------------- salida
def a_lrc(marcas, lineas, titulo, dur):
    def sello(t):
        m, s = int(t//60), int(t % 60)
        return "[%02d:%02d.%02d]" % (m, s, min(99, round((t % 1)*100)))
    out = ["[ti:%s]" % titulo, "[by:sincronizar.py]", ""]
    for k, (t, ln) in enumerate(zip(marcas, lineas)):
        if k and t - marcas[k-1] > 5:
            out.append(sello(marcas[k-1] + min(3.5, (t-marcas[k-1])*0.45)))
        out.append(sello(t) + ln)
    out.append(sello(min(dur, marcas[-1]+4)))
    return "\n".join(out)


# ------------------------------------------------------- una sola canción
def procesar_cancion(ruta_audio, ruta_letra, ruta_salida, tmp, rapido):
    os.makedirs(tmp, exist_ok=True)
    lineas, secciones = leer_letra(ruta_letra)
    titulo = os.path.splitext(os.path.basename(ruta_audio))[0].replace('_', ' ')
    log('letra: %d líneas en %d secciones' % (len(lineas), len(set(secciones))))

    mezcla = a_wav(ruta_audio, os.path.join(tmp, 'mezcla.wav'), 44100)
    dur = len(leer_mono(mezcla)[1]) / 44100.0
    log('audio: %.1f s' % dur)

    log('\n[1/5] separación de voz')
    voz = separar_voz(ruta_audio, tmp)
    voz16 = a_wav(voz, os.path.join(tmp, 'voz.wav'), 16000, True) if voz else None

    log('[2/5] detección de actividad vocal')
    frases = detectar_frases(voz or mezcla)
    log('  %d frases vocales' % len(frases))

    log('[3/5] anclas por reconocimiento de voz')
    prompt = ' '.join(lineas[:12])[:600]
    anclas = {} if rapido else anclas_asr(voz16, a_wav(mezcla, os.path.join(tmp, 'mez16.wav'), 16000, True), lineas, prompt)
    log('  %d líneas ancladas' % len(anclas))

    log('[4/5] estructura: secciones repetidas')
    F, hop = rasgos(mezcla)
    # agrupar líneas por sección
    bloques, act = [], None
    for i, s in enumerate(secciones):
        if s != act: bloques.append([i, i+1, s]); act = s
        else: bloques[-1][1] = i+1
    # una sección es "sólida" si tiene 3+ anclas
    solidas = [b for b in bloques if sum(1 for i in range(b[0], b[1]) if i in anclas) >= 3]
    inicios = {}
    for b in solidas:
        idx = sorted(i for i in range(b[0], b[1]) if i in anclas)
        inicios[tuple(b[:2])] = anclas[idx[0]] - (idx[0]-b[0])*0.30
    for b in bloques:
        clave = tuple(b[:2])
        if clave in inicios: continue
        gemela = next((s for s in solidas if s[2] == b[2] and (s[1]-s[0]) == (b[1]-b[0])), None)
        if gemela and tuple(gemela[:2]) in inicios:
            i0 = inicios[tuple(gemela[:2])]
            largo = (gemela[1]-gemela[0])*2.5
            evitar = [(i0, i0+largo)] + [(v, v+largo) for v in inicios.values()]
            hall = buscar_repeticion(F, hop, i0, min(i0+largo, dur-1), evitar, 1)
            if hall and hall[0][1] > 0.6:
                inicios[clave] = hall[0][0]
                log('  %s en %.1f s (similitud %.2f)' % (b[2], hall[0][0], hall[0][1]))

    # patrón interno de cada tipo de sección
    def patron(b):
        idx = sorted(i for i in range(b[0], b[1]) if i in anclas)
        if len(idx) < 3: return None
        base = anclas[idx[0]]
        pasos = [(anclas[k]-anclas[j])/(k-j) for j, k in zip(idx[:-1], idx[1:])]
        paso = float(np.median(pasos))
        return [anclas[b[0]+k]-base if (b[0]+k) in anclas else k*paso for k in range(b[1]-b[0])]

    marcas = [None]*len(lineas)
    for b in bloques:
        clave = tuple(b[:2])
        pat = patron(b) or next((patron(s) for s in solidas if s[2] == b[2] and patron(s)), None)
        ini = inicios.get(clave)
        if ini is None and any(i in anclas for i in range(b[0], b[1])):
            i0 = min(i for i in range(b[0], b[1]) if i in anclas)
            ini = anclas[i0] - (i0-b[0])*0.30
        if ini is None: continue
        for k, i in enumerate(range(b[0], b[1])):
            marcas[i] = anclas[i] if i in anclas else (ini + (pat[k] if pat and k < len(pat) else k*2.4))

    # rellenar lo que quede usando las frases vocales
    libres = [a_ for a_, _ in frases]
    for i in range(len(marcas)):
        if marcas[i] is None:
            prev = next((marcas[j] for j in range(i-1, -1, -1) if marcas[j] is not None), 0.0)
            cand = [o for o in libres if o > prev + 0.5]
            marcas[i] = cand[0] if cand else prev + 2.4

    log('[5/5] afinado: pulso y ataque exacto')
    per, bpm, grilla = grilla_pulso(mezcla, dur)
    log('  tempo %.1f BPM' % bpm)
    if voz:
        sr, v = leer_mono(voz)
        H, W = int(sr*0.005), int(sr*0.020)
        n = (len(v)-W)//H
        rms = uniform_filter1d(np.array([np.sqrt((v[i*H:i*H+W]**2).mean()) for i in range(n)], dtype=np.float32), 5)
        tt = np.arange(n)*H/sr
        marcas = [pie_ataque(rms, tt, sr, H, t) for t in marcas]
    marcas = [float(grilla[np.argmin(np.abs(grilla-t))]) if np.min(np.abs(grilla-t)) <= 0.12 else t
              for t in marcas]

    for i in range(len(marcas)):
        marcas[i] = max(0.0, min(marcas[i], dur-0.5))
        if i and marcas[i] < marcas[i-1]+0.40: marcas[i] = marcas[i-1]+0.40
    marcas = [round(t, 2) for t in marcas]

    sobre = sum(1 for t in marcas if any(x-0.45 <= t <= y for x, y in frases))
    pct = 100*sobre/len(marcas) if marcas else 0.0
    log('\nvalidación: %d de %d líneas caen sobre canto detectado (%.0f%%)'
        % (sobre, len(marcas), pct))

    json.dump({"v": 1, "titulo": titulo, "duracion": round(dur, 2), "marcas": marcas,
               "origen": "sincronizar.py"}, open(ruta_salida, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    lrc = os.path.splitext(ruta_salida)[0] + '.lrc'
    open(lrc, 'w', encoding='utf-8').write(a_lrc(marcas, lineas, titulo, dur))
    log('escrito: %s y %s' % (ruta_salida, lrc))

    return {'titulo': titulo, 'duracion': dur, 'lineas': len(marcas), 'validado_pct': pct}


# ---------------------------------------------------------- modo carpeta
EXT_AUDIO = ('.mp3', '.wav', '.m4a', '.flac', '.ogg')

def clave_norm(s):
    return ' '.join(norm(s).split())

def emparejar(carpeta_audio, carpeta_letras):
    """Empareja cada letra NN_Titulo.txt con su audio Titulo.mp3 por nombre normalizado."""
    letras = sorted(f for f in os.listdir(carpeta_letras) if f.lower().endswith('.txt'))
    audios = [f for f in os.listdir(carpeta_audio) if f.lower().endswith(EXT_AUDIO)]
    audio_por_clave = {clave_norm(os.path.splitext(f)[0]): f for f in audios}

    pares, sin_pareja = [], []
    for lf in letras:
        base = re.sub(r'^\d+[_\-\s]*', '', os.path.splitext(lf)[0]).replace('_', ' ')
        clave = clave_norm(base)
        audio = audio_por_clave.get(clave)
        if not audio:
            candidatos = [af for ac, af in audio_por_clave.items() if clave and (clave in ac or ac in clave)]
            candidatos = list(dict.fromkeys(candidatos))
            audio = candidatos[0] if len(candidatos) == 1 else None
        if audio:
            pares.append((lf, audio))
        else:
            sin_pareja.append(lf)
    return pares, sin_pareja

def barra(actual, total, ancho=28):
    llenos = int(ancho * actual / total) if total else ancho
    pct = int(100 * actual / total) if total else 100
    return '[%s%s] %d/%d (%d%%)' % ('#'*llenos, '-'*(ancho-llenos), actual, total, pct)

def modo_lote(carpeta_audio, carpeta_letras, carpeta_salida, tmp, rapido, forzar):
    os.makedirs(carpeta_salida, exist_ok=True)
    os.makedirs(tmp, exist_ok=True)
    pares, sin_pareja = emparejar(carpeta_audio, carpeta_letras)
    if sin_pareja:
        log('sin audio emparejado, se omiten: ' + ', '.join(sin_pareja))
    total = len(pares)
    log('\n%d canciones para sincronizar (de %d letras)\n' % (total, total + len(sin_pareja)))

    resumen = []
    for i, (letra_f, audio_f) in enumerate(pares, 1):
        nombre = os.path.splitext(letra_f)[0]
        salida_json = os.path.join(carpeta_salida, os.path.splitext(letra_f)[0] + '.json')
        ruta_audio = os.path.join(carpeta_audio, audio_f)
        ruta_letra = os.path.join(carpeta_letras, letra_f)

        log('\n' + '='*64)
        log(barra(i-1, total) + '  ' + nombre)
        log('='*64)

        if os.path.exists(salida_json) and not forzar:
            log('  ya existe, se salta (usa --forzar para rehacer)')
            resumen.append((nombre, 'saltada', ''))
            continue

        tmp_cancion = os.path.join(tmp, nombre)
        t0 = time.time()
        try:
            stats = procesar_cancion(ruta_audio, ruta_letra, salida_json, tmp_cancion, rapido)
            resumen.append((nombre, 'ok', '%.0f%% validado · %.0fs' % (stats['validado_pct'], time.time()-t0)))
        except Exception as e:
            log('  ERROR: %s' % e)
            resumen.append((nombre, 'error', str(e)[:90]))

    log('\n' + '='*64)
    log(barra(total, total) + '  listo')
    log('='*64)
    log('\nRESUMEN')
    for nombre, estado, detalle in resumen:
        log('  %-42s %-9s %s' % (nombre, estado, detalle))
    for lf in sin_pareja:
        log('  %-42s %-9s %s' % (os.path.splitext(lf)[0], 'sin audio', ''))
    ok = sum(1 for _, e, _ in resumen if e == 'ok')
    saltadas = sum(1 for _, e, _ in resumen if e == 'saltada')
    errores = sum(1 for _, e, _ in resumen if e == 'error')
    log('\n%d listas · %d saltadas · %d con error · %d sin audio' % (ok, saltadas, errores, len(sin_pareja)))


# --------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description='Sincroniza letras con audio: una canción, o una carpeta entera.')
    ap.add_argument('audio', nargs='?', help='archivo de audio (modo una canción)')
    ap.add_argument('letra', nargs='?', help='archivo de letra (modo una canción)')
    ap.add_argument('--rapido', action='store_true', help='omite el reconocimiento de voz')
    ap.add_argument('--tmp', default='.sync_tmp')
    ap.add_argument('--salida', default='marcas.json', help='(modo una canción) archivo de salida')
    ap.add_argument('--carpeta-audio', dest='carpeta_audio', help='carpeta con los audios (modo lote)')
    ap.add_argument('--carpeta-letras', dest='carpeta_letras', help='carpeta con las letras .txt (modo lote)')
    ap.add_argument('--carpeta-salida', dest='carpeta_salida', default='Marcas',
                     help='carpeta de salida en modo lote (por defecto "Marcas")')
    ap.add_argument('--forzar', action='store_true', help='en modo lote, rehace lo que ya tenga salida')
    a = ap.parse_args()

    if a.carpeta_audio or a.carpeta_letras:
        if not (a.carpeta_audio and a.carpeta_letras):
            sys.exit('--carpeta-audio y --carpeta-letras van siempre juntos')
        modo_lote(a.carpeta_audio, a.carpeta_letras, a.carpeta_salida, a.tmp, a.rapido, a.forzar)
    else:
        if not (a.audio and a.letra):
            sys.exit('faltan argumentos: pasa "audio letra", o usa --carpeta-audio/--carpeta-letras')
        procesar_cancion(a.audio, a.letra, a.salida, a.tmp, a.rapido)


if __name__ == '__main__':
    main()
