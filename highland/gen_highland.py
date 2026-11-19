"""Genera cada frase del vídeo de Highland con la voz del dueño (Qwen3-TTS, igual que produccion/voz.py)."""
import json, sys, numpy as np, soundfile as sf, torch
from pathlib import Path
from qwen_tts import Qwen3TTSModel
R = Path(__file__).resolve().parent
ref = R / "ref"   # grabación de referencia nueva (19-nov)
m = Qwen3TTSModel.from_pretrained("Qwen/Qwen3-TTS-12Hz-1.7B-Base", device_map="cpu", dtype=torch.float32)
p = m.create_voice_clone_prompt(ref_audio=str(ref / "referencia.wav"), ref_text=(ref / "referencia.txt").read_text(encoding="utf-8").strip(), x_vector_only_mode=False)
g = json.load(open(R / "guion.json", encoding="utf-8"))
out = Path("/tmp/hl"); out.mkdir(exist_ok=True)
for n in map(int, sys.argv[1].split(",")):
    for j, t in enumerate(g[n - 1]["tts"]):
        wavs, sr = m.generate_voice_clone(text=t, language="Spanish", voice_clone_prompt=p, temperature=0.8)
        sf.write(out / f"s{n:02d}_{j}.wav", np.asarray(wavs[0], dtype="float32").squeeze(), sr)
        print(n, j, t, flush=True)
