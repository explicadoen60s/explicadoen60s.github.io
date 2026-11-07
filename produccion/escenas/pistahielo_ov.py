# Capa 2D de «¿Y si construyes una pista de hielo?»
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("pistahielo")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"quince", "grados", "suelo", "nivelado", "tubos", "zigzag", "anticongelante", "diez", "cero", "golpe", "burbujas",
            "grietas", "capas", "milímetro", "doce", "veinte", "transparente", "blanco", "líneas", "sellarlo", "tres", "centímetros",
            "cinco", "seis", "tierra", "hincha", "levanta", "aislante", "calefacción", "rayan", "rasca", "caliente",
            "cuatrocientos", "ochocientos", "litros", "media", "hora", "lista"}

def sg(t, a, b):
    x = max(0.0, min(1.0, (t - a) / (b - a))); return x * x * (3 - 2 * x)

def nl(t):
    a, b = T("una se congela"), T("hasta doce")
    if t < T("así que la echas"): return 0
    if t < a: return 1 if t >= T("de apenas") else 0
    if t < b: return 1 + int(5 * sg(t, a, b))
    n = 6 + int(14 * sg(t, b, T("veinte capas", fin=True)))
    if t >= T("y otra vez"): n = 20 + int(4 * sg(t, T("y otra vez"), T("dentro", fin=True)))
    return min(n, 24)

def overlay(ctx, t, A, C):
    Y, R, G, B = C.YL, C.RED, C.GREEN, (0.45, 0.8, 1.0)
    BY = H * 0.265
    if T("aunque") <= t < T("vamos a congelar"):
        v = 15 * sg(t, T("aunque"), T("grados", fin=True))
        C.badge(ctx, "FUERA %d °C" % round(v), W / 2, BY, win(t, T("aunque"), T("vamos a congelar")), (1.0, 0.65, 0.25), size=80)
    label(C, ctx, t, T("pones un suelo"), T("encima"), "HORMIGÓN", A, "conc", dx=-40, dy=110, size=58)
    label(C, ctx, t, T("tiendes"), T("por ellos"), "TUBOS", A, "pipe", dx=0, dy=-150, size=62)
    a0, a1 = T("por ellos"), T("pero si echas")
    if a0 <= t < a1:
        v = 15 - 25 * sg(t, T("enfriado"), T("bajo cero", fin=True))
        C.badge(ctx, "%d °C" % round(v), W / 2, BY, win(t, a0, a1), B, size=96)
    if T("pero si echas") <= t < T("así que la echas"):
        C.badge(ctx, "✗", W / 2, BY, win(t, T("se congela mal"), T("así que la echas")), R, size=110)
    a0, a1 = T("de apenas"), T("pero el hielo")
    if a0 <= t < a1:
        C.badge(ctx, "CAPA %d" % max(1, nl(t)), W / 2, BY, win(t, a0, a1), B, size=86)
        if t < T("una se congela"): C.badge(ctx, "1 MM", W / 2, BY + 140, win(t, a0, T("una se congela")), Y, size=72)
    if T("pero el hielo") <= t < T("así que,"):
        C.badge(ctx, "TUBOS A LA VISTA", W / 2, BY, win(t, T("y se ven"), T("así que,")), R, size=64) if False else None
    a0, a1 = T("cuando tiene"), T("y otra vez")
    if a0 <= t < a1:
        C.badge(ctx, "2 CM", W / 2, BY, win(t, a0, a1), Y, size=86)
    a0, a1 = T("y otra vez"), T("y aquí viene")
    if a0 <= t < T("al final"):
        C.badge(ctx, "CAPA %d" % nl(t), W / 2, BY, win(t, a0, T("al final")), B, size=86)
    if T("al final") <= t < a1:
        cm = 2 + 1 * sg(t, T("el hielo mide"), T("tres centímetros", fin=True))
        if t >= T("al aire"): cm = 3 + 3 * sg(t, T("hasta cinco"), T("o seis", fin=True))
        if t >= T("y se mantiene"): cm = 3
        C.badge(ctx, "%d CM" % round(cm), W / 2, BY, win(t, T("al final"), a1), Y, size=90)
        if t >= T("y se mantiene"):
            v = -10 + 5 * sg(t, T("y se mantiene"), T("bajo cero", 2, fin=True))
            C.badge(ctx, "%d °C" % round(v), W / 2, BY + 150, win(t, T("y se mantiene"), a1), B, size=80)
    a0, a1 = T("el frío baja"), T("pero los patines")
    if a0 <= t < a1:
        v = 8 - 10 * sg(t, T("el agua del suelo"), T("se congela", 4, fin=True))
        v += 10 * sg(t, T("pero de calefacción"), T("puesta", fin=True))
        C.badge(ctx, "TIERRA %d °C" % round(v), W / 2, BY, win(t, a0, a1), B if v < 0.5 else (1.0, 0.6, 0.25), size=74)
    label(C, ctx, t, T("y levanta"), T("así que debajo"), "+2 CM", A, "ice", dx=0, dy=-150, size=70)
    label(C, ctx, t, T("del aislante"), T("pero de calefacción"), "AISLANTE", A, "ins", dx=0, dy=-110, size=56)
    label(C, ctx, t, T("pero de calefacción"), T("pero los patines"), "CALEFACCIÓN", A, "heat", dx=0, dy=150, size=56)
    a0, a1 = T("entre cuatrocientos"), T("y en media")
    if a0 <= t < a1 + 0.3:
        v = 400 + 400 * sg(t, T("y ochocientos") - 0.3, T("litros", fin=True))
        C.badge(ctx, "%d L" % round(v), W / 2, BY, win(t, a0, a1 + 0.3), B, size=90)
    a0, a1 = T("y en media"), T("sígueme") + 0.8
    if a0 <= t < a1:
        v = 30 * (1 - sg(t, T("y en media"), T("estar lista", fin=True)))
        C.badge(ctx, ("%d MIN" % round(v)) if v > 0.5 else "✓ LISTA", W / 2, BY, win(t, a0, a1), G, size=86)

def sfx_events(C):
    E = [(0.0, C.s_whoosh(1.0), 0.35), (1.4, C.s_whoosh(0.8), 0.3), (T("vamos a congelar"), C.s_whoosh(), 0.45),
         (T("pones un suelo"), C.s_thud(), 0.5), (T("bajo cero"), C.s_coin(), 0.4), (T("de golpe"), C.s_whoosh(), 0.4),
         (T("y grietas"), C.s_fail(), 0.4), (T("una se congela"), C.s_pop(), 0.35), (T("otra, se congela"), C.s_pop(), 0.35),
         (T("veinte capas"), C.s_coin(), 0.4), (T("lo pintas"), C.s_whoosh(), 0.4), (T("las líneas"), C.s_pop(), 0.35),
         (T("tres centímetros"), C.s_coin(), 0.35), (T("se hincha"), C.s_thud(), 0.5), (T("levanta la pista"), C.s_fail(), 0.4),
         (T("pero de calefacción"), C.s_win(), 0.4), (T("rayan"), C.s_buzz(1.0), 0.25), (T("una máquina"), C.s_buzz(5.0), 0.25),
         (T("litros"), C.s_coin(), 0.35), (T("estar lista"), C.s_win(), 0.4), (T("sígueme"), C.s_whoosh(), 0.4)]
    for k in range(14): E.append((T("hasta doce") + 0.1 * k, C.s_bleep(500 + 30 * k), 0.1))
    return E
