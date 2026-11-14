# Capa 2D de «¿Cuánta agua bebible hace la desaladora del Llobregat?»
# Pastillas (motion → fotografía): entran ≤0,3 s después del corte de su plano, como mucho 2 por plano, por debajo de y=560.
#  60 bar sobre el manómetro (23,6) · 2,3 bar sobre la rueda (25,1) · 100 litros en la entrada (28,1) · 45 litros en el depósito (30)
#  55 litros sobre la salmuera (32,1) · 100 → 50 % de energía sobre la barra (37,4) · 80 piscinas (46) · 60 hm³ al año (49,4).
# Juego: la tarjeta no desaparece tras la revelación (se queda en la esquina con la cifra en verde y vuelve en «¿Te has acercado?»).
# Rótulos de pieza (9), nunca a la vez que una pastilla.
from _ovbase import *
from marcas import cargar
T, DUR = cargar("desaladora")
SUB_ESTILO = "centro"
SUB_Y = 0.50
KEYWORDS = {"desaladora", "llobregat", "agua", "bebible", "metros", "cúbicos", "barcelona", "ríos", "lluvia", "mar", "sal",
            "membrana", "ósmosis", "inversa", "bomba", "sesenta", "bar", "veinticinco", "presión", "rueda", "coche", "cien",
            "litros", "cuarenta", "cinco", "potable", "salmuera", "mitad", "energía", "doscientos", "mil", "ochenta",
            "piscinas", "olímpicas", "hectómetros", "dos", "nueve", "ciudad"}

def pastilla(C, ctx, t, v, u, a, b, A, key, dx=0, dy=-110, desde=None, dec=0, dur=0.9, size=62, lo=560):
    x, y = A(key); C.pastilla(ctx, t, v, u, a, b, clampx(x + dx, 280), clampy(y + dy, lo, 1380), desde=desde, dec=dec, dur=dur, size=size)

def tarjeta_resuelta(C, ctx, t):
    a0, b0, fin = T("son") - 0.3, T("te has acercado") - 0.3, T("dime") + 0.4
    if t < a0 or t > fin: return
    m = C.ease((t - a0) / 0.45) if t < b0 else 1 - C.ease((t - b0) / 0.45)
    G, M = (C.W / 2, C.H * 0.22), (C.W * 0.21, C.H * 0.205)
    cx, cy = G[0] + (M[0] - G[0]) * m, G[1] + (M[1] - G[1]) * m
    C._tarjeta_cifra(ctx, cx, cy, 1 - 0.45 * m, "¿TE HAS ACERCADO?" if m < 0.5 else "LA CIFRA", C.miles(200000), "M³ AL DÍA", C.GREEN,
                     alpha=min(1.0, (fin - t) / 0.3))

def overlay(ctx, t, A, C):
    C.cifra_juego(ctx, t, 200000, "M³ AL DÍA", T("cuánta agua"), T("saca hasta"), T("son") - 0.3, grande=(C.W / 2, C.H * 0.22))
    tarjeta_resuelta(C, ctx, t)
    # rótulos de pieza (uno cada vez)
    C.rotulo(ctx, t, "MAR MEDITERRÁNEO", T("el mar"), T("así que sacas") - 0.2)
    C.rotulo(ctx, t, "TOMA DE AGUA", T("así que sacas") + 0.2, T("pero lleva") - 0.2)
    C.rotulo(ctx, t, "SAL", T("sal"), T("y así no") + 0.6)
    C.rotulo(ctx, t, "MEMBRANA", T("membrana"), T("membrana") + 1.5)
    C.rotulo(ctx, t, "ÓSMOSIS INVERSA", T("ósmosis"), T("pero el agua no") - 0.1)
    C.rotulo(ctx, t, "BOMBA", T("bomba"), T("hasta sesenta") - 0.4)
    C.rotulo(ctx, t, "RECUPERADOR DE PRESIÓN", T("recuperas"), T("salmuera") - 0.15)
    C.rotulo(ctx, t, "SALMUERA", T("salmuera"), T("y ahorras") - 0.3)
    C.rotulo(ctx, t, "PLANTA DESALADORA", T("la planta"), T("saca hasta") - 0.6)
    # cifras
    pastilla(C, ctx, t, 60, "bar", T("hasta sesenta") - 0.1, T("pero de cada") - 0.25, A, "man", desde=1, dur=1.0)
    pastilla(C, ctx, t, 2.3, "bar", T("más de veinticinco") - 0.1, T("pero de cada") - 0.25, A, "rueda", desde=0, dec=1, dur=0.8)
    pastilla(C, ctx, t, 100, "litros", T("pero de cada") - 0.1, T("y el resto") - 0.25, A, "entrada", desde=0, dur=0.9)
    pastilla(C, ctx, t, 45, "litros", T("salen cuarenta") - 0.1, T("y el resto") - 0.25, A, "tanque", desde=0, dur=1.2)
    pastilla(C, ctx, t, 55, "litros", T("y el resto") - 0.1, T("así que recuperas") - 0.25, A, "salmuera", desde=0, dur=1.0)
    pastilla(C, ctx, t, 50, "% energía", T("y ahorras") - 0.1, T("y aquí viene") - 0.2, A, "barra", desde=100, dur=1.4)
    pastilla(C, ctx, t, 80, "piscinas", T("son") - 0.1, T("al año") - 0.25, A, "pisc", dy=-160, desde=0, dur=2.4)
    pastilla(C, ctx, t, 60, "hm³ al año", T("al año") - 0.1, T("te has acercado") - 0.3, A, "pisc", dy=-160, desde=0, dur=1.2)
    # clics y chispas
    x, y = A("bomba"); C.chispa(ctx, t, x, y, T("una bomba") + 0.1, r=70)
    x, y = A("membrana"); C.chispa(ctx, t, x, y, T("sesenta bar", fin=True), r=70, col=(0.6, 0.85, 1.0))
    x, y = A("rec"); C.chispa(ctx, t, x, y, T("así que recuperas") + 0.3, r=60)

def sfx_events(C):
    # ningún efecto dentro de una cifra dicha (sesenta bar, veinticinco, cien, cuarenta y cinco, dos mil nueve, doscientos mil,
    # ochenta, sesenta hectómetros): van al inicio de cada frase o en las pausas
    E = [(0.0, C.s_thud(), 0.45), (0.05, C.s_whoosh(), 0.4), (0.1, C.s_buzz(2.4), 0.12),
         (T("desaladora") - 0.15, C.s_whoosh(), 0.3), (T("barcelona") - 0.25, C.s_whoosh(), 0.3), (T("y poca") - 0.2, C.s_fail(), 0.25),
         (T("pero tiene") - 0.25, C.s_whoosh(), 0.3), (T("así que sacas") - 0.25, C.s_whoosh(), 0.3), (T("así que sacas") + 0.4, C.s_buzz(1.2), 0.12),
         (T("pero lleva") - 0.2, C.s_pop(), 0.3), (T("y así no"), C.s_fail(), 0.3), (T("así que usas") - 0.25, C.s_whoosh(), 0.3),
         (T("tan fina"), C.s_tick(), 0.4), (T("se llama") - 0.2, C.s_pop(), 0.3), (T("pero el agua no") - 0.2, C.s_thud(), 0.35),
         (T("así que una bomba") - 0.25, C.s_whoosh(), 0.3), (T("una bomba") + 0.1, C.s_clank(), 0.45), (T("una bomba") + 0.3, C.s_buzz(1.4), 0.15),
         (T("más de veinticinco") - 0.3, C.s_pop(), 0.3), (T("pero de cada") - 0.3, C.s_whoosh(), 0.3), (T("salen cuarenta") - 0.3, C.s_pop(), 0.3),
         (T("y el resto") - 0.25, C.s_whoosh(), 0.3), (T("con más sal") - 0.2, C.s_bleep(420), 0.2), (T("así que recuperas") - 0.25, C.s_whoosh(), 0.3),
         (T("así que recuperas") + 0.3, C.s_clank(), 0.35), (T("y ahorras") - 0.3, C.s_pop(), 0.3), (T("y aquí viene") - 0.25, C.s_whoosh(), 0.35),
         (T("la planta") - 0.25, C.s_whoosh(), 0.3), (T("son") - 0.4, C.s_whoosh(), 0.3), (T("al año") - 0.3, C.s_pop(), 0.3),
         (T("cada día", fin=True) + 0.05, C.s_coin(), 0.3), (T("te has acercado") - 0.25, C.s_whoosh(), 0.35), (T("dime") - 0.25, C.s_pop(), 0.3),
         (T("y si quieres") - 0.25, C.s_whoosh(), 0.3), (T("lo más pedido") - 0.25, C.s_pop(), 0.3), (T("sígueme") - 0.25, C.s_whoosh(), 0.4),
         (T("así que ya sabes") - 0.25, C.s_whoosh(), 0.35), (T("la desaladora del", 2) - 0.3, C.s_thud(), 0.3)]
    E += [(T("cuánta agua"), C.s_pop(), 0.5), (T("al día", 2, fin=True) + 0.05, C.s_win(), 0.4)]   # sin tictac encima de la cifra dicha
    return E
