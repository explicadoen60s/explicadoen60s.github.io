"""Genera la voz de un guion con la voz del dueño del canal (clon de timbre con Qwen3-TTS, gratis y local).

Uso:  python3 produccion/voz.py <nombre> [<nombre> …]
Lee   produccion/escenas/<nombre>.txt   (solo el texto que se locuta)
Crea  produccion/escenas/<nombre>.mp3

Referencia de la voz: produccion/voz/referencia.wav (15 s de la voz del dueño) + referencia.txt (lo que dice).
Modo ICL: copia el timbre y también su forma de narrar (entonación). Acabado «TikTok»: +8 % de velocidad,
más presencia y compresión.
"""
import re, subprocess, sys, tempfile
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parent
ESCENAS = RAIZ / "escenas"
REF = RAIZ / "voz" / "referencia.wav"
REF_TXT = RAIZ / "voz" / "referencia.txt"
# Acabado más natural (encargo de sonido, 12-nov): menos acelerado (1,05), sin agudos chillones (de-esser y menos realce),
# graves cálidos y un poco de «sala» casi imperceptible para que no suene a voz seca de ordenador.
ACABADO = ("atempo=1.05,highpass=f=70,equalizer=f=180:t=q:w=1:g=1.5,equalizer=f=3200:t=q:w=1.2:g=1.5,deesser=i=0.4:m=0.5:f=0.5,"
           "aecho=0.9:0.25:18|31:0.05|0.03,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120,loudnorm=I=-15:TP=-1.5")
MODELO = "Qwen/Qwen3-TTS-12Hz-1.7B-Base"
PAUSA = {".": 0.28, "?": 0.38, "!": 0.32, "…": 0.45, ":": 0.25}   # silencio tras cada trozo según cómo acaba (respira como una persona)
TEMPERATURA = 0.85    # algo menos que 1: entonación más estable, menos sílabas raras
MAX_CHARS = 200       # tamaño de cada trozo (frases completas): más corto = menos deriva de la voz

_modelo = _prompt = None


def _cargar():
    global _modelo, _prompt
    if _modelo is None:
        import torch
        from qwen_tts import Qwen3TTSModel
        torch.set_num_threads(max(1, (torch.get_num_threads())))
        _modelo = Qwen3TTSModel.from_pretrained(MODELO, device_map="cpu", dtype=torch.float32)
        _prompt = _modelo.create_voice_clone_prompt(ref_audio=str(REF), ref_text=REF_TXT.read_text(encoding="utf-8").strip(), x_vector_only_mode=False)
    return _modelo, _prompt


def trozos(texto):
    frases = [f.strip() for f in re.split(r"(?<=[.?!…:])\s+", texto.strip()) if f.strip()]
    out, actual = [], ""
    for f in frases:
        if actual and len(actual) + len(f) + 1 > MAX_CHARS:
            out.append(actual); actual = f
        else:
            actual = f"{actual} {f}".strip()
    if actual:
        out.append(actual)
    return out


def recortar(a, sr, umbral=0.012):
    """Quita el silencio que el modelo deja al principio y al final de cada trozo (las pausas las pone PAUSA)."""
    v = np.abs(a); idx = np.where(v > umbral * (v.max() or 1))[0]
    if len(idx) == 0: return a
    i0 = max(0, idx[0] - int(0.03 * sr)); i1 = min(len(a), idx[-1] + int(0.06 * sr))
    return a[i0:i1]


def generar(nombre):
    texto = (ESCENAS / f"{nombre}.txt").read_text(encoding="utf-8").strip()
    m, prompt = _cargar()
    partes, sr = [], 24000
    for t in trozos(texto):
        wavs, sr = m.generate_voice_clone(text=t, language="Spanish", voice_clone_prompt=prompt, temperature=TEMPERATURA)
        a = recortar(np.asarray(wavs[0], dtype="float32").squeeze(), sr)
        fin = t.rstrip()[-1:] if t.rstrip() else "."
        partes += [a, np.zeros(int(PAUSA.get(fin, 0.25) * sr), dtype="float32")]
    audio = np.concatenate(partes[:-1])
    import soundfile as sf
    with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
        sf.write(tmp.name, audio, sr)
        salida = ESCENAS / f"{nombre}.mp3"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", tmp.name, "-af", ACABADO,
                        "-ar", "44100", "-b:a", "160k", str(salida)], check=True)
    print(f"voz {nombre}: {len(audio) / sr:.1f} s")
    return salida


if __name__ == "__main__":
    for n in sys.argv[1:]:
        generar(n)
