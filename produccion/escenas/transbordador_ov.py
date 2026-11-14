# Capa 2D de «¿A qué altura cuelga el puente de Vizcaya?» (Lo que esconde tu ciudad)
# Pastillas (motion → fotografía), en el tercio de arriba y lejos del mini del juego (arriba-izquierda):
#  61 m sobre la torre (22,9-24,5) · 160 m sobre la viga (24,5-27,5) · 15 plantas junto al edificio (32,7-34,9)
#  · 6 coches y 200 pasajeros sobre la barquilla (43,3-46,6) · 1,5 min sobre la barquilla que cruza (46,6-48,4).
# Callouts: PORTUGALETE / GETXO sobre cada orilla, 1893 y UNESCO 2006. La tarjeta del juego (45 m) arriba.
from _ovbase import *
from marcas import cargar
T, DUR = cargar("transbordador")
SUB_ESTILO = "centro"
SUB_Y = 0.50
KEYWORDS = {"altura", "puente", "vizcaya", "metros", "portugalete", "getxo", "ría", "barcos", "bilbao", "altísimo", "rampas",
            "larguísimas", "torres", "hierro", "sesenta", "uno", "viga", "ciento", "cuarenta", "cinco", "agua", "edificio", "quince",
            "plantas", "carriles", "barquilla", "cables", "acero", "seis", "coches", "doscientos", "pasajeros", "minuto", "medio",
            "unesco", "patrimonio", "mil", "ochocientos", "noventa", "tres"}

def pastilla(C, ctx, t, v, u, a, b, A, key, dx=0, dy=-150, desde=0, dec=0, dur=0.9, size=66, lo=430, hi=720):
    x, y = A(key); C.pastilla(ctx, t, v, u, a, b, clampx(x + dx, 330), clampy(y + dy, lo, hi), desde=desde, dec=dec, dur=dur, size=size)

def overlay(ctx, t, A, C):
    juego_completo(C, ctx, t, 45, "M SOBRE EL AGUA", T("a qué altura"), T("la viga cuelga"), T("te has acercado"), T("sígueme"))
    # rótulos de pieza (uno cada vez)
    C.rotulo(ctx, t, "BARQUILLA", 0.3, 2.3)
    C.rotulo(ctx, t, "TORRES DE HIERRO", T("levanta"), T("de sesenta") - 0.05)
    C.rotulo(ctx, t, "VIGA", T("las une"), T("las une") + 1.5)
    C.rotulo(ctx, t, "CARRILES", T("carriles"), T("y por ellos") - 0.05)
    C.rotulo(ctx, t, "BARQUILLA", T("una barquilla"), T("va colgada") - 0.05)
    C.rotulo(ctx, t, "CABLES DE ACERO", T("cables"), T("casi a ras") + 0.6)
    # orillas
    p = win(t, T("portugalete"), T("pero por la") - 0.1)
    if p: x, y = A("porto"); C.callout(ctx, "PORTUGALETE", clampx(x, 320), clampy(y - 80, 600, 1100), p, size=56)
    p = win(t, T("y getxo"), T("pero por la") - 0.1)
    if p: x, y = A("getxo"); C.callout(ctx, "GETXO", clampx(x, 300), clampy(y - 80, 600, 1100), p, size=56)
    p = win(t, T("en mil"), T("levanta") - 0.1)
    if p: C.callout(ctx, "1893", C.W / 2, C.H * 0.32, p, size=72)
    p = win(t, T("en dos mil"), T("te has acercado") - 0.1)
    if p: C.callout(ctx, "UNESCO 2006", C.W / 2, C.H * 0.31, p, size=64)
    # cifras
    pastilla(C, ctx, t, 61, "m de alto", T("de sesenta") - 0.1, T("las une") - 0.1, A, "torre", dx=170, dy=-100, dur=1.0)
    pastilla(C, ctx, t, 160, "m de viga", T("las une"), T("y aquí viene") - 0.1, A, "viga", dx=120, dy=-220, dur=1.6)
    pastilla(C, ctx, t, 15, "plantas", T("como un edificio"), T("pero tú") - 0.1, A, "edif", dx=110, dy=-120, dur=1.2)
    pastilla(C, ctx, t, 6, "coches", T("caben"), T("cruza la") - 0.1, A, "barq", dx=-130, dy=-260, dur=0.9)
    pastilla(C, ctx, t, 200, "pasajeros", T("doscientos") - 0.2, T("cruza la") - 0.1, A, "barq", dx=170, dy=-160, dur=1.0, size=58)
    pastilla(C, ctx, t, 1.5, "min", T("cruza la"), T("los barcos pasan") + 0.6, A, "barq", dx=0, dy=-240, dec=1, dur=1.0)
    # clics
    x, y = A("viga"); C.chispa(ctx, t, x, y, T("ciento sesenta", fin=True) + 0.4, r=70)
    x, y = A("carril"); C.chispa(ctx, t, x, y, T("carriles", fin=True), r=60)
    x, y = A("barq"); C.chispa(ctx, t, x, y, T("y por ellos") + 0.5, r=70)

def sfx_events(C):
    E = [(0.0, C.s_whoosh(), 0.35), (0.05, C.s_buzz(2.0), 0.12), (T("portugalete") - 0.1, C.s_whoosh(), 0.35),
         (T("portugalete") + 0.3, C.s_pop(), 0.35), (T("y getxo"), C.s_pop(), 0.35), (T("pero por la"), C.s_bleep(260), 0.3),
         (T("así que un"), C.s_whoosh(0.8), 0.35), (T("altísimo"), C.s_fail(), 0.3), (T("rampas"), C.s_whoosh(), 0.3),
         (T("larguísimas"), C.s_fail(), 0.3), (T("así que alberto"), C.s_whoosh(), 0.35), (T("en mil") - 0.25, C.s_pop(), 0.35),
         (T("levanta"), C.s_clank(), 0.4), (T("de sesenta") - 0.3, C.s_tick(), 0.35),
         (T("las une"), C.s_whoosh(), 0.35), (T("ciento sesenta", fin=True) + 0.4, C.s_clank(), 0.4),
         (T("como un edificio"), C.s_thud(), 0.4), (T("pero tú"), C.s_whoosh(), 0.3), (T("carriles", fin=True), C.s_clank(), 0.4),
         (T("y por ellos") + 0.5, C.s_thud(), 0.4), (T("cables"), C.s_pop(), 0.3), (T("caben"), C.s_pop(), 0.35),
         (T("doscientos") - 0.3, C.s_tick(), 0.35), (T("cruza la"), C.s_whoosh(), 0.35), (T("los barcos pasan"), C.s_bleep(260), 0.3),
         (T("sin enterarse"), C.s_win(), 0.35), (T("la unesco"), C.s_coin(), 0.4), (T("te has acercado"), C.s_whoosh(), 0.35),
         (T("dime en"), C.s_bleep(620), 0.25), (T("y si quieres"), C.s_whoosh(), 0.3), (T("lo más pedido"), C.s_pop(), 0.35),
         (T("sígueme"), C.s_whoosh(), 0.4), (T("así que ya sabes"), C.s_whoosh(), 0.35)]
    E += C.sfx_cifra(T("a qué altura"), T("la viga cuelga"))
    return E
