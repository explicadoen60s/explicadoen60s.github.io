# Capa 2D de «Así funciona tu ratón»
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("raton")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"mil", "quinientas", "fotos", "led", "luz", "roja", "rozando", "sombra", "lente", "cámara", "dieciocho", "trescientos",
            "veinticuatro", "manchas", "compara", "anterior", "izquierda", "derecha", "chip", "flecha", "diecisiete", "cristal", "quieta"}

def sg(t, a, b):
    x = max(0.0, min(1.0, (t - a) / (b - a))); return x * x * (3 - 2 * x)
def miles(v): return f"{int(round(v)):,}".replace(",", ".")

def overlay(ctx, t, A, C):
    Y, R, G, B = C.YL, C.RED, C.GREEN, (0.45, 0.8, 1.0)
    BY = H * 0.265
    if t < T("mira por dentro") + 0.3:
        C.badge(ctx, "FOTOS: " + miles(1500 * max(0.0, t - 0.1)), W / 2, BY, win(t, 0.1, T("mira por dentro") + 0.3), Y, size=78)
    label(C, ctx, t, T("es un led"), T("ilumina") - 0.1, "LED", A, "led", dx=-170, dy=-120, size=66)
    label(C, ctx, t, T("ilumina") + 0.3, T("así cada"), "LED", A, "ledB", dx=-40, dy=-200, size=62)
    label(C, ctx, t, T("pelusa"), T("encima hay"), "PELUSA", A, "pel", dx=-150, dy=-240, size=54)
    label(C, ctx, t, T("fibra"), T("encima hay"), "FIBRA", A, "fib", dx=40, dy=-330, size=54)
    label(C, ctx, t, T("arañazo"), T("encima hay"), "ARAÑAZO", A, "scr", dx=110, dy=170, size=54)
    if T("hacen una") <= t < T("encima hay"):
        C.badge(ctx, "SOMBRAS: %d" % round(6 * sg(t, T("hacen una"), T("sombra", fin=True))), W / 2, BY, win(t, T("hacen una"), T("encima hay")), Y, size=72)
    label(C, ctx, t, T("lente"), T("pero no es"), "LENTE", A, "lens", dx=250, dy=40, size=58)
    label(C, ctx, t, T("diminuta") - 0.3, T("tiene solo"), "CÁMARA", A, "chip", dx=0, dy=-230, size=60)
    if T("pero no es") <= t < T("tiene solo"):
        C.badge(ctx, "MÓVIL: 12.000.000 PX", W / 2, BY, win(t, T("pero no es"), T("tiene solo")), B, size=66)
    if T("tiene solo") <= t < T("con eso"):
        n = round(18 * sg(t, T("tiene solo"), T("píxeles", fin=True)))
        C.badge(ctx, "%d × 18" % n, W / 2, BY, win(t, T("tiene solo"), T("con eso")), B, size=88)
        if t >= T("trescientos"):
            C.badge(ctx, miles(324 * sg(t, T("trescientos"), T("veinticuatro", fin=True))) + " PX", W / 2, BY + 150, win(t, T("trescientos"), T("con eso")), Y, size=80)
    if T("el ratón no guarda") <= t < T("compara cada"):
        C.badge(ctx, "FOTO Nº " + miles(1 + 1500 * (t - T("el ratón no guarda"))), W / 2, BY, win(t, T("el ratón no guarda"), T("compara cada")), Y, size=74)
        C.badge(ctx, "✗ GUARDADAS: 0", W / 2, BY + 140, win(t, T("ninguna"), T("compara cada")), R, size=62)
    label(C, ctx, t, T("compara cada") + 0.3, T("es que tú") - 0.3, "ANTES", A, "gridO", dx=0, dy=-110, size=58)
    label(C, ctx, t, T("compara cada") + 0.3, T("es que tú") - 0.3, "AHORA", A, "gridN", dx=0, dy=-110, size=58)
    if T("si las manchas") <= t < T("es que tú") - 0.3:
        v = round(3 * sg(t, T("si las manchas"), T("izquierda", fin=True))); C.badge(ctx, ("X: -%d PX" % v) if v else "X: 0 PX", W / 2, BY, win(t, T("si las manchas"), T("es que tú") - 0.3), Y, size=80)
    if T("es que tú") <= t < T("un chip"):
        C.badge(ctx, "RATÓN: +%d" % round(3 * sg(t, T("es que tú"), T("derecha", fin=True))), W / 2, BY, win(t, T("es que tú"), T("un chip")), G, size=84)
    if T("un chip") <= t < T("y se lo manda"):
        v = round(3 * sg(t, T("calcula"), T("desplazado", fin=True)))
        C.badge(ctx, "X: +%d   Y: 0" % v, W / 2, BY, win(t, T("un chip"), T("y se lo manda")), Y, size=80)
    if T("que mueve") <= t < T("así que") - 0.2:
        v = min(3, int(4 * sg(t, T("que mueve"), T("lo mismo", fin=True)) + 1e-6))
        C.badge(ctx, "+%d PX" % v, W / 2, BY, win(t, T("que mueve"), T("así que") - 0.2), G, size=84)
    if T("cuantas más") <= t < T("los de videojuegos"):
        C.badge(ctx, "1.500 / S", W / 2, BY, win(t, T("cuantas más"), T("los de videojuegos") + 0.05), Y, size=88)
    if T("los de videojuegos") <= t < T("por eso falla"):
        v = 1500 + 15500 * sg(t, T("los de videojuegos"), T("diecisiete", fin=True) + 0.4)
        C.badge(ctx, miles(v) + " / S", W / 2, BY, win(t, T("los de videojuegos"), T("por eso falla")), G, size=88)
    label(C, ctx, t, T("cristal") - 0.2, T("es tan liso"), "CRISTAL", A, "glass", dx=0, dy=170, size=62)
    if T("es tan liso") <= t < T("la cámara ve") - 0.3:
        C.badge(ctx, "SOMBRAS: 0", W / 2, BY, win(t, T("es tan liso"), T("la cámara ve") - 0.3), R, size=76)
    if T("la cámara ve") - 0.3 <= t < T("y la flecha"):
        C.badge(ctx, "X: 0   Y: 0", W / 2, BY, win(t, T("la cámara ve") - 0.3, T("y la flecha")), R, size=80)
    if T("y la flecha") <= t < T("sígueme"):
        C.badge(ctx, "✗ +0 PX", W / 2, BY, win(t, T("y la flecha"), T("sígueme")), R, size=84)

def sfx_events(C):
    E = [(0.0, C.s_whoosh(0.8), 0.3), (T("mira por dentro"), C.s_whoosh(), 0.4), (T("le das"), C.s_whoosh(0.7), 0.4), (T("es un led"), C.s_pop(), 0.4),
         (T("ilumina"), C.s_whoosh(), 0.4), (T("pelusa"), C.s_pop(), 0.3), (T("fibra"), C.s_pop(), 0.3), (T("arañazo"), C.s_pop(), 0.3),
         (T("lente"), C.s_pop(), 0.35), (T("diminuta"), C.s_bleep(880), 0.3), (T("tiene solo"), C.s_whoosh(), 0.4), (T("veinticuatro"), C.s_coin(), 0.4),
         (T("compara cada"), C.s_whoosh(), 0.4), (T("izquierda"), C.s_pop(), 0.4), (T("derecha"), C.s_pop(), 0.4), (T("y se lo manda"), C.s_whoosh(), 0.4),
         (T("así que"), C.s_whoosh(), 0.35), (T("diecisiete"), C.s_win(), 0.4), (T("cristal"), C.s_thud(), 0.45), (T("la cámara ve"), C.s_fail(), 0.35),
         (T("quieta"), C.s_fail(), 0.35), (T("sígueme"), C.s_whoosh(), 0.4)]
    for k in range(10): E.append((T("el ratón no guarda") + 0.15 * k, C.s_bleep(700 + 30 * k), 0.1))
    for k in range(3): E.append((T("que mueve") + (T("lo mismo", fin=True) - T("que mueve")) * (k + 1) / 4, C.s_bleep(900), 0.2))
    return E
