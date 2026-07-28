
import json, os, re, sys, unicodedata
os.environ.setdefault('KMP_DUPLICATE_LIB_OK', 'TRUE')
from faster_whisper import WhisperModel

def norm(s):
    s = unicodedata.normalize('NFD', s.lower())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return re.sub(r"[^a-z0-9\u00f1 ]", ' ', s)

cfg = json.load(open(sys.argv[1], encoding='utf-8'))
m = WhisperModel('base', device='cpu', compute_type='int8')
out = []
for f in cfg['archivos']:
    for pr in (cfg['prompt'], None):
        segs, _ = m.transcribe(f, language='es', word_timestamps=True, vad_filter=False,
                               beam_size=5, temperature=0.0,
                               condition_on_previous_text=False, initial_prompt=pr)
        out.append([[norm(w.word).strip(), float(w.start)]
                    for s in segs for w in (s.words or []) if norm(w.word).strip()])
json.dump(out, open(sys.argv[2], 'w'))
