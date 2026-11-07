# Capa 2D de «Si tuvieras que inventar el paraguas automático…»
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("paraguas")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"botón", "golpe", "inventarlo", "mochila", "tela", "varillas", "ocho", "abajo", "tirante", "pieza", "flor", "largo",
            "tubos", "mitad", "bolsillo", "mil", "novecientos", "veintiocho", "muelle", "tú", "clic", "gancho", "comprimido",
            "suelta", "estira", "instante"}

def sg(t, a, b):
    x = max(0.0, min(1.0, (t - a) / (b - a))); return x * x * (3 - 2 * x)

def bar(C, ctx, t, a, b, frac, col, title, y):
    p = win(t, a, b)
    if not p: return
    w, h = 560, 40; x0 = W / 2 - w / 2
    C.rrect(ctx, x0 - 12, y - 12, w + 24, h + 24, 20); ctx.set_source_rgba(0.13, 0.15, 0.19, 0.92 * p); ctx.fill()
    C.rrect(ctx, x0, y, max(h, w * frac), h, 14); ctx.set_source_rgba(*col, p); ctx.fill()
    C.badge(ctx, title, W / 2, y - 58, p, col, size=56)

def carga(t):
    c = sg(t, T("cuando cierras"), T("clic", fin=True))
    return c * (1 - sg(t, T("el muelle se estira"), T("en un instante", fin=True)))

def overlay(ctx, t, A, C):
    Y, R, G, B = C.YL, C.RED, C.GREEN, (0.45, 0.8, 1.0)
    BY = H * 0.265
    label(C, ctx, t, 0.2, T("y tu paraguas"), "BOTÓN", A, "button", dx=-160, dy=-120, size=62)
    a0, a1 = T("una tela"), T("pero las varillas")
    if a0 <= t < a1:
        n = min(8, int(sg(t, a0, a0 + 0.2 * 8 + 0.3) * 8 + 0.5)) if t < T("con ocho") else 8
        C.badge(ctx, "%d VARILLAS" % n, W / 2, BY, win(t, a0, a1), Y, size=78)
    if T("pero las varillas") <= t < T("así que a cada"):
        C.badge(ctx, "✗", W / 2, BY, win(t, T("se doblan"), T("así que a cada")), R, size=110)
    a0, a1 = T("un tirante"), T("al subirla")
    if a0 <= t < a1:
        n = min(8, int(sg(t, a0, a0 + 0.12 * 8 + 0.3) * 8 + 0.5))
        C.badge(ctx, "%d TIRANTES" % n, W / 2, BY, win(t, a0, a1), (1.0, 0.65, 0.25), size=78)
    label(C, ctx, t, T("una pieza"), T("pero sigue"), "CORREDERA", A, "runner", dx=-230, dy=0, size=56)
    a0, a1 = T("pero sigue"), T("así que haces")
    if a0 <= t < T("así nació"):
        e = 1 - sg(t, T("así que haces"), T("dentro de otro", fin=True))
        cm = 30 + 30 * e + 25 * (1 - sg(t, T("y las varillas se"), T("por la mitad", fin=True)))
        C.badge(ctx, "%d CM" % round(cm), W / 2, BY, win(t, a0, T("así nació")), B, size=86)
    a0, a1 = T("así nació"), T("y aquí viene")
    if a0 <= t < a1:
        v = 1900 + 28 * sg(t, T("en mil"), T("veintiocho", fin=True))
        C.badge(ctx, "%d" % round(v), W / 2, BY, win(t, a0, a1), Y, size=96)
    a0, a1 = T("cuando cierras"), T("y tú no")
    if a0 <= t < a1:
        c = carga(t); col = R if c > 0.95 else (Y if c > 0.4 else G)
        bar(C, ctx, t, a0, a1, c, col, "MUELLE %d %%" % round(100 * c), BY + 40)
    label(C, ctx, t, T("el muelle que") + 0.2, T("cuando cierras"), "MUELLE", A, "spring", dx=-200, dy=0, size=60)
    label(C, ctx, t, T("hasta oír"), T("aprietas"), "CLIC", A, "spring", dx=180, dy=260, size=72)
    label(C, ctx, t, T("y un gancho"), T("al pulsar"), "GANCHO", A, "hook", dx=-220, dy=60, size=60)
    a0, a1 = T("y abre las"), T("sígueme")
    if a0 <= t < a1:
        n = int(8 * sg(t, T("y abre las"), T("en un instante", fin=True)) + 0.5)
        C.badge(ctx, "%d / 8" % n, W / 2, BY + 160, win(t, a0, a1), Y, size=80)

def sfx_events(C):
    E = [(0.45, C.s_clank(), 0.5), (T("y tu paraguas") + 0.05, C.s_whoosh(0.5), 0.6), (T("se abre") + 0.3, C.s_thud(), 0.5),
         (T("vamos a inventarlo"), C.s_whoosh(), 0.45), (T("pero las varillas") + 0.4, C.s_fail(), 0.35), (T("al subirla"), C.s_whoosh(), 0.4),
         (T("como una flor"), C.s_win(), 0.35), (T("así que haces") + 0.5, C.s_clank(), 0.4), (T("por la mitad"), C.s_clank(), 0.4),
         (T("veintiocho"), C.s_coin(), 0.4), (T("el muelle que"), C.s_whoosh(), 0.35), (T("clic"), C.s_clank(), 0.6),
         (T("y un gancho") + 0.3, C.s_clank(), 0.5), (T("el botón"), C.s_pop(), 0.5), (T("se suelta"), C.s_clank(), 0.45),
         (T("el muelle se estira"), C.s_whoosh(0.5), 0.6), (T("en un instante"), C.s_thud(), 0.5), (T("sígueme"), C.s_whoosh(), 0.4)]
    for k in range(8): E.append((T("una tela") + 0.2 * k, C.s_pop(), 0.25))
    for k in range(8): E.append((T("un tirante") + 0.12 * k, C.s_bleep(700 + 50 * k), 0.15))
    return E
