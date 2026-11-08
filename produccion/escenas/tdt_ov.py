# Capa 2D de «Así funciona la TDT»
from _ovbase import *
from marcas import cargar
T, DUR = cargar("tdt")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"tele", "canales", "antena", "señal", "torre", "ondas", "radio", "recta", "luz", "empaquetados", "frecuencia",
            "ceros", "unos", "múltiple", "barrido", "megahercios", "lista", "uno", "cinco", "cadenas", "nada", "ultra",
            "definición", "dvb-t", "datos", "hueco", "antigua", "menú", "búsqueda", "automática", "frecuencias", "nueva"}

def ss(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def keyed(t, keys):
    if t <= keys[0][0]: return keys[0][1]
    for (a, va), (b, vb) in zip(keys, keys[1:]):
        if a <= t <= b: return va + (vb - va) * ss((t - a) / max(b - a, 1e-4))
    return keys[-1][1]

def needle_f(t):   # la misma aguja que en la escena 3D
    t0, t1 = T("escucha"), T("megahercios", fin=True)
    u = ss((t - t0) / (t1 - t0)); return 470 + 224 * u

def overlay(ctx, t, A, C):
    Y, R, G, B = C.YL, C.RED, C.GREEN, (0.4, 0.95, 0.85)
    Yb = H * 0.265
    # cambio de canal al principio
    for a, b, n in ((0.0, 0.74, 3), (0.74, 1.42, 4)):
        if a <= t < b: C.badge(ctx, f"CANAL {n}", W / 2, Yb, min(1, (t - a) / 0.12 + 0.6) if a else 1.0, (1, 1, 1), size=78)
    if 1.42 <= t < T("la antena") - 0.1:
        C.badge(ctx, "✗ CANAL 5", W / 2, Yb, win(t, 1.42, T("la antena") - 0.1), R, size=78)
    badge(C, ctx, t, T("está bien") - 0.1, T("mira cómo"), "✓ ANTENA", G, size=78)
    label(C, ctx, t, T("mira cómo") + 0.3, T("desde una"), "SEÑAL", A, "cable", dx=150, dy=0, size=60)
    label(C, ctx, t, T("una torre"), T("salen ondas") + 0.6, "TORRE", A, "torre", dx=0, dy=-170, size=64)
    # velocidad de la luz
    a0, a1 = T("velocidad") - 0.2, T("hasta la antena") + 1.0
    if a0 <= t < a1:
        v = keyed(t, [(a0, 0), (T("luz", fin=True), 300000)])
        C.badge(ctx, f"{int(round(v)):,} KM/S".replace(",", "."), W / 2, Yb, win(t, a0, a1), BEAM_C, size=80)
    # canales y múltiple
    a0, a1 = T("en una sola"), T("comprimidos")
    if a0 <= t < a1:
        n = int(keyed(t, [(a0, 0), (T("canales", 2, fin=True), 5)]) + 0.5)
        C.badge(ctx, f"498 MHz · {n} CANALES", W / 2, Yb, win(t, a0, a1), B, size=70)
    a0, a1 = T("comprimidos"), T("a ese paquete")
    if a0 <= t < a1:
        C.badge(ctx, "0101 1100 1011", W / 2, Yb, win(t, a0, a1), (1, 1, 1), size=74)
    label(C, ctx, t, T("múltiple") - 0.1, T("tu tele no") - 0.3, "MÚLTIPLE", A, "pkt", dx=0, dy=-140, size=66)
    # barrido de frecuencias
    a0, a1 = T("hace un barrido"), T("desde entonces")
    if a0 <= t < a1:
        f = needle_f(t)
        C.badge(ctx, f"{int(round(f))} MHz", W / 2, Yb, win(t, a0, a1), Y, size=92)
    a0, a1 = T("el uno") - 0.1, T("y aquí")
    if a0 <= t < a1:
        C.badge(ctx, "CANAL 1 · 498 MHz", W / 2, Yb, win(t, a0, a1), Y, size=72)
    # el cambio del 5 de noviembre
    a0, a1 = T("el jueves"), T("cinco cadenas")
    if a0 <= t < a1:
        mm = "07:59" if t < T("ocho") + 0.2 else "08:00"
        C.badge(ctx, f"JUE 5 NOV · {mm}", W / 2, Yb, win(t, a0, a1), (1, 1, 1), size=74)
    a0, a1 = T("cinco cadenas"), T("tu tele va")
    if a0 <= t < a1:
        mv = a0 + 0.2; n = sum(1 for k in range(5) if t > mv + 0.3 * k + 0.9)
        C.badge(ctx, f"{n}/5 CADENAS MOVIDAS", W / 2, Yb, win(t, a0, a1), B, size=68)
    a0, a1 = T("tu tele va"), T("además")
    if a0 <= t < a1:
        if t < T("y no encuentra"): C.badge(ctx, "CANAL 1 · 498 MHz", W / 2, Yb, win(t, a0, a1), Y, size=72)
        else: C.badge(ctx, "✗ SIN SEÑAL", W / 2, Yb, win(t, T("y no encuentra"), a1), R, size=84)
    # DVB-T2
    label(C, ctx, t, T("ultra") , T("con un sistema"), "4K", A, "t2", dx=-40, dy=-200, size=72)
    label(C, ctx, t, T("el dvbt") - 0.1, T("si tu tele es"), "DVB-T2", A, "t2", dx=-90, dy=-200, size=66)
    p = win(t, T("mete") + 0.2, T("si tu tele es"))
    if p:
        x0, y0 = A("t2l"); x1, _ = A("t2r")
        C.arrow_dim(ctx, x0 - 6, x1 + 6, y0 + 40, B, p, lw=6)
        C.outlined(ctx, "8 MHz", (x0 + x1) / 2, y0 + 110, 50, fill=B, stroke=10, alpha=p)
    badge(C, ctx, t, T("si tu tele es") + 0.2, T("la solución"), "✗ DVB-T2", R, size=80)
    # solución
    a0, a1 = T("búsqueda") + 0.3, T("no hace")
    if a0 <= t < a1:
        r1 = T("frecuencias", fin=True); v = 100 * ss((t - a0) / (r1 - a0))
        C.badge(ctx, f"BUSCANDO {int(round(v))} %", W / 2, Yb, win(t, a0, a1), G if v >= 99.5 else Y, size=76)
    badge(C, ctx, t, T("no hace") + 0.2, DUR + 1, "✓ MISMA ANTENA", G, size=76)

BEAM_C = (1.0, 0.9, 0.4)

def sfx_events(C):
    E = [(0.08, C.s_bleep(1400), 0.6), (0.74, C.s_bleep(1400), 0.6), (1.42, C.s_bleep(1400), 0.6), (1.62, C.s_fail(), 0.35)]
    E += [(T("está bien"), C.s_win(), 0.3), (T("mira cómo"), C.s_whoosh(), 0.4), (T("una torre"), C.s_whoosh(), 0.45),
          (T("salen ondas"), C.s_buzz(1.2), 0.25), (T("viajan en"), C.s_whoosh(), 0.35), (T("hasta la antena"), C.s_pop(), 0.45),
          (T("van empaquetados"), C.s_pop(), 0.4), (T("comprimidos"), C.s_buzz(1.0), 0.2), (T("múltiple"), C.s_clank(), 0.35),
          (T("tu tele no") - 0.4, C.s_whoosh(), 0.4)]
    t0, t1 = T("escucha"), T("megahercios", fin=True)
    for k in range(10): E.append((t0 + (t1 - t0) * k / 10, C.s_bleep(700 + 60 * k), 0.35))
    E += [(T("y apunta") + 0.3 * k, C.s_pop(), 0.25) for k in range(7)]
    E += [(T("el uno") - 0.1, C.s_bleep(1400), 0.6), (T("salta"), C.s_coin(), 0.4), (T("y aquí"), C.s_whoosh(), 0.35),
          (T("el jueves"), C.s_pop(), 0.4), (T("ocho"), C.s_coin(), 0.35)]
    E += [(T("cinco cadenas") + 0.2 + 0.3 * k, C.s_whoosh(0.35), 0.3) for k in range(5)]
    E += [(T("tu tele va") + 0.3, C.s_bleep(1400), 0.6), (T("y no encuentra"), C.s_fail(), 0.45), (T("ultra"), C.s_pop(), 0.4),
          (T("el dvbt"), C.s_clank(), 0.35), (T("mete"), C.s_pop(), 0.35), (T("si tu tele es"), C.s_fail(), 0.4),
          (T("menú") - 0.05, C.s_bleep(1400), 0.6), (T("búsqueda") + 0.1, C.s_bleep(1400), 0.6)]
    r0, r1 = T("búsqueda") + 0.3, T("frecuencias", fin=True)
    for k in range(8): E.append((r0 + (r1 - r0) * k / 8, C.s_bleep(700 + 80 * k), 0.3))
    E += [(r1, C.s_win(), 0.4), (T("sígueme"), C.s_whoosh(), 0.4)]
    return E
