# Capa 2D de «¿Y si construyes una carretera?»
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("carretera")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"camiones", "cuarenta", "cuatro", "toneladas", "blanda", "aplasta", "peso", "rodillos", "vibran", "piedra", "asfalto",
            "agrieta", "zahorra", "encajan", "veinticinco", "centímetros", "base", "intermedia", "rodadura", "tres", "treinta",
            "plana", "tejado", "dos", "ciento", "pendiente", "cunetas", "tubos", "agua", "grieta", "congela", "nueve", "rompe",
            "camión", "bache", "baches", "invierno"}

def sg(t, a, b):
    x = max(0.0, min(1.0, (t - a) / (b - a))); return x * x * (3 - 2 * x)

def bar(C, ctx, t, a, b, frac, col, title, y):
    p = win(t, a, b)
    if not p: return
    w, h = 560, 40; x0 = W / 2 - w / 2
    C.rrect(ctx, x0 - 12, y - 12, w + 24, h + 24, 20); ctx.set_source_rgba(0.13, 0.15, 0.19, 0.92 * p); ctx.fill()
    C.rrect(ctx, x0, y, max(h, w * frac), h, 14); ctx.set_source_rgba(*col, p); ctx.fill()
    C.badge(ctx, title, W / 2, y - 58, p, col, size=56)

def overlay(ctx, t, A, C):
    Y, R, G, B = C.YL, C.RED, C.GREEN, (0.45, 0.8, 1.0)
    BY = H * 0.265
    if T("pasan camiones") <= t < T("vamos a construir"):
        v = 44 * sg(t, T("de hasta"), T("toneladas", fin=True))
        C.badge(ctx, "%d T" % round(v), W / 2, BY, win(t, T("pasan camiones"), T("vamos a construir")), Y, size=100)
    label(C, ctx, t, T("primero quitas"), T("pero la tierra"), "TIERRA BLANDA", A, "z2", dx=-120, dy=-250, size=56)
    if T("pero la tierra") <= t < T("así que la compactas"):
        C.badge(ctx, "✗", W / 2, BY, win(t, T("se aplasta"), T("así que la compactas")), R, size=110)
    a0, a1 = T("así que la compactas"), T("pero si echas")
    if a0 <= t < a1:
        f = sg(t, T("con rodillos"), T("como una piedra", fin=True))
        bar(C, ctx, t, a0, a1, f, G if f > 0.9 else Y, "COMPACTADO %d %%" % round(100 * f), BY + 40)
    if T("pero si echas") <= t < T("así que pones"):
        C.badge(ctx, "✗", W / 2, BY, win(t, T("se agrieta"), T("así que pones")), R, size=110)
    label(C, ctx, t, T("zahorra"), T("una capa de"), "ZAHORRA", A, "z1", dx=60, dy=-120, size=60)
    a0, a1 = T("una capa de"), T("ahora sí")
    if a0 <= t < a1:
        cm = 25 * sg(t, a0, T("veinticinco", fin=True)) + 25 * sg(t, T("y otra más") - 0.3, T("y otra más") + 0.5)
        C.badge(ctx, "%d CM" % round(cm), W / 2, BY, win(t, a0, a1), Y, size=92)
    a0, a1 = T("primero", 2), T("si la carretera")
    if a0 <= t < a1:
        cm = 15 * sg(t, T("una gruesa") - 0.2, T("de base", fin=True)) + 12 * sg(t, T("una intermedia") - 0.2, T("intermedia", fin=True)) \
             + 3 * sg(t, T("la de rodadura") - 0.2, T("rodadura", fin=True))
        C.badge(ctx, "ASFALTO %d CM" % round(cm), W / 2, BY, win(t, a0, a1), Y, size=78)
    label(C, ctx, t, T("una gruesa"), T("y arriba"), "BASE", A, "ab", dx=-80, dy=150, size=58)
    label(C, ctx, t, T("una intermedia"), T("y arriba") + 0.4, "INTERMEDIA", A, "ai", dx=-60, dy=-150, size=54)
    label(C, ctx, t, T("la de rodadura"), T("en las carreteras"), "RODADURA 3 CM", A, "ar", dx=0, dy=-160, size=54)
    if T("si la carretera") <= t < T("así que le das"):
        C.badge(ctx, "0 %", W / 2, BY, win(t, T("si la carretera"), T("así que le das")), R, size=96)
    a0, a1 = T("así que le das"), T("y aquí viene")
    if a0 <= t < a1:
        v = 2 * sg(t, T("un dos"), T("pendiente", fin=True))
        C.badge(ctx, "◢ %d %% ◣" % round(v) if False else "%d %%" % round(v), W / 2, BY, win(t, a0, a1), G, size=96)
    label(C, ctx, t, T("cunetas"), T("tubos que") + 0.2, "CUNETA", A, "ditch", dx=-60, dy=-140, size=58)
    label(C, ctx, t, T("tubos que"), T("y aquí viene"), "TUBO", A, "pipe", dx=-60, dy=140, size=58)
    a0, a1 = T("y al hacerse"), T("luego pasa")
    if T("se congela") <= t < a1:
        v = 100 + 9 * sg(t, T("y al hacerse"), T("ciento más", fin=True))
        C.badge(ctx, "VOLUMEN %d %%" % round(v), W / 2, BY, win(t, T("se congela"), a1), B if v < 105 else R, size=76)
        C.badge(ctx, "-3 °C", W / 2, BY + 140, win(t, T("por la noche"), a1), B, size=70)
    if T("luego pasa") <= t < T("por eso hay"):
        C.badge(ctx, "44 T", W / 2, BY, win(t, T("luego pasa"), T("por eso hay")), Y, size=90)
    if T("por eso hay") <= t < T("sígueme") + 0.6:
        n = int(6 * sg(t, T("por eso hay"), T("por eso hay") + 1.5) + 0.5)
        C.badge(ctx, "%d BACHES" % n, W / 2, BY, win(t, T("por eso hay"), T("sígueme") + 0.6), R, size=84)

def sfx_events(C):
    E = [(0.0, C.s_buzz(7.0), 0.22), (T("toneladas"), C.s_thud(), 0.5), (T("vamos a construir"), C.s_whoosh(), 0.45),
         (T("primero quitas"), C.s_whoosh(), 0.4), (T("se aplasta"), C.s_thud(), 0.55), (T("con rodillos"), C.s_buzz(4.0), 0.3),
         (T("como una piedra"), C.s_win(), 0.35), (T("se agrieta"), C.s_fail(), 0.4), (T("piedra machacada"), C.s_thud(), 0.45),
         (T("y otra más"), C.s_thud(), 0.45), (T("una gruesa"), C.s_thud(), 0.4), (T("una intermedia"), C.s_thud(), 0.4),
         (T("la de rodadura"), C.s_thud(), 0.4), (T("treinta"), C.s_coin(), 0.4), (T("de tejado"), C.s_whoosh(), 0.35),
         (T("cunetas"), C.s_pop(), 0.35), (T("es el agua"), C.s_fail(), 0.35), (T("se congela"), C.s_pop(), 0.35),
         (T("empuja"), C.s_clank(), 0.45), (T("rompe"), C.s_clank(), 0.5), (T("luego pasa"), C.s_buzz(2.0), 0.35),
         (T("y arranca"), C.s_thud(), 0.6), (T("por eso hay"), C.s_pop(), 0.35), (T("sígueme"), C.s_whoosh(), 0.4)]
    return E
