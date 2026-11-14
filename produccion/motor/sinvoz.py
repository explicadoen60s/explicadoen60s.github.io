#!/usr/bin/env python3
"""Formato D · Simulación (sin voz): convierte escenas/<n>_rotulos.json en lo que el motor espera de la voz.
- <n>_words.json: cada palabra de cada rótulo con su tiempo (repartidas dentro del rótulo), para que T("palabra") funcione.
- <n>_voz.wav: silencio de la duración total (el sonido lo ponen sfx_events y la música).
Uso: python3 sinvoz.py <nombre>   (en la carpeta de trabajo, con <nombre>_rotulos.json copiado)"""
import json, sys, wave, re

n = sys.argv[1]
rot = json.load(open(f"{n}_rotulos.json", encoding="utf-8"))
words = []
for t0, t1, txt in rot:
    ps = txt.replace("*", "").split()
    paso = max(0.12, (t1 - t0 - 0.4) / max(1, len(ps)))
    for i, p in enumerate(ps):
        a = t0 + 0.1 + i * paso
        words.append([round(a, 3), round(a + paso * 0.9, 3), p])
dur = max(r[1] for r in rot)
json.dump({"dur": dur, "words": words}, open(f"{n}_words.json", "w"), ensure_ascii=False)
SR = 44100
with wave.open(f"{n}_voz.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(b"\x00\x00" * int((dur + 0.5) * SR))
print("sinvoz", n, dur, len(words))
