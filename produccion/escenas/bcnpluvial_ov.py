# Capa 2D de «¿Cuánta agua de tormenta cabe bajo Barcelona?» (Lo que esconde tu ciudad, parte 3)
# Pastillas previstas (motion → fotografía), todas en el tercio de arriba y desplazadas del eje de su pieza:
# 0 → 55.000 m³ sobre el depósito Joan Miró (sube con el agua) · 1 → 3 depósitos sobre el central · % lleno sobre el
# depósito izquierdo y luego el derecho (compuertas) · 85 → 10 % al vaciarse hacia la depuradora · 3 → 15 depósitos sobre la
# ciudad · 0 → 190 piscinas · 0 → 60.000 m³ sobre el depósito de 2028. Juego de la cifra: 477.000 m³ (tarjeta arriba).
from _ovbase import *
from marcas import cargar
T, DUR = cargar("bcnpluvial")
SUB_ESTILO = "centro"
SUB_Y = 0.50
KEYWORDS = {"barcelona", "agua", "tormenta", "calle", "ciudad", "montaña", "mar", "calles", "cuesta", "alcantarillas", "tapas",
            "caja", "hormigón", "parque", "depósito", "depósitos", "joan", "miró", "cincuenta", "cinco", "mil", "metros", "cúbicos",
            "sensores", "tuberías", "compuertas", "depuradora", "quince", "cuatrocientos", "setenta", "siete", "ciento", "noventa",
            "piscinas", "olímpicas", "veintiocho", "sesenta", "lluvia"}

def pastilla(C, ctx, t, v, u, a, b, A, key, dx=160, dy=-170, desde=0, dec=0, dur=0.9, size=66):
    x, y = A(key); x, y = clampx(x + dx, 300), clampy(y + dy, 520, 1300)
    if y < 600 and x < 580: x = 580          # no tapar la tarjeta pequeña del juego (arriba a la izquierda)
    C.pastilla(ctx, t, v, u, a, b, x, y, desde=desde, dec=dec, dur=dur, size=size)

def overlay(ctx, t, A, C):
    # juego de la cifra
    C.cifra_juego(ctx, t, 477000, "m³ BAJO BARCELONA", T("cuánta agua"), T("juntos guardan"), T("sígueme"), dec=0)
    # rótulos de pieza (uno cada vez)
    C.rotulo(ctx, t, "ALCANTARILLAS", T("pero las alcantarillas"), T("pero las alcantarillas") + 1.6)
    C.rotulo(ctx, t, "DEPÓSITO", T("así que cavas") + 0.6, T("así que cavas") + 2.3)
    C.rotulo(ctx, t, "JOAN MIRÓ", T("el depósito joan"), T("el depósito joan") + 1.5)
    C.rotulo(ctx, t, "SENSORES", T("sensores"), T("sensores") + 1.5)
    C.rotulo(ctx, t, "COMPUERTAS", T("y unas compuertas") + 0.4, T("y unas compuertas") + 2.0)
    C.rotulo(ctx, t, "DEPURADORA", T("hacia la depuradora"), T("hacia la depuradora") + 1.5)
    # 55.000 m³ del depósito Joan Miró: cuenta mientras se llena
    pastilla(C, ctx, t, 55000, "m³", T("el agua de la"), T("pero uno solo") + 0.6, A, "depA", dx=180, dy=-200, dur=T("guarda cincuenta", fin=True) - T("el agua de la"))
    # número de depósitos
    pastilla(C, ctx, t, 3, "depósitos", T("así que construyes"), T("y los conectas") + 0.3, A, "depA", dx=0, dy=-240, desde=1, dur=1.2)
    # compuertas: se llena primero el de la izquierda, luego el de la derecha
    pastilla(C, ctx, t, 100, "% lleno", T("y unas compuertas") + 0.4, T("se llena") + 0.6, A, "depB", dx=160, dy=-190, dur=T("se llena") - T("y unas compuertas"))
    pastilla(C, ctx, t, 70, "% lleno", T("se llena") + 0.6, T("cuando pasa"), A, "depC", dx=-160, dy=-190, dur=1.4)
    # vaciado hacia la depuradora
    pastilla(C, ctx, t, 10, "% lleno", T("el agua sale poco"), T("hoy barcelona") - 0.2, A, "depura", dx=-200, dy=-200, desde=85, dur=3.0)
    # 15 depósitos
    pastilla(C, ctx, t, 15, "depósitos", T("hoy barcelona"), T("juntos guardan") - 0.6, A, "ciudad", dx=0, dy=-260, desde=3, dur=1.8)
    # 190 piscinas olímpicas
    # (después de la revelación la tarjeta del juego ocupa el centro de arriba: estas pastillas van justo debajo)
    C.pastilla(ctx, t, 190, "piscinas olímpicas", T("unas ciento") - 0.1, T("y en dos mil") - 0.1, W / 2, H * 0.435, dur=1.8, size=62)
    # depósito de 2028: 60.000 m³
    p = win(t, T("y en dos mil"), T("de sesenta") - 0.1)
    if p: C.callout(ctx, "2028", W / 2, H * 0.435, p, size=64)
    C.pastilla(ctx, t, 60000, "m³ en 2028", T("de sesenta") - 0.1, T("te has") + 0.4, W / 2, H * 0.435, dur=1.2)
    # clics y golpes
    x, y = A("tapa")
    for k in range(3): C.chispa(ctx, t, x + (k - 1) * 0, y, T("y el agua sale") + 0.2 * k, r=55)
    x, y = A("depA"); C.chispa(ctx, t, x, y, T("así que cavas") + 1.2, r=70)
    x, y = A("tunel"); C.chispa(ctx, t, x, y, T("se llena") + 1.0, r=50)
    x, y = A("depD"); C.chispa(ctx, t, x, y, T("y en dos mil") + 1.2, r=60)

def sfx_events(C):
    E = [(0.0, C.s_whoosh(), 0.35), (0.05, C.s_buzz(2.2), 0.12), (T("y el agua corre"), C.s_whoosh(0.7), 0.3),
         (T("barcelona está"), C.s_whoosh(), 0.35), (T("cuando cae"), C.s_thud(), 0.45), (T("cuando cae") + 0.4, C.s_buzz(2.4), 0.14),
         (T("el agua baja"), C.s_whoosh(0.7), 0.3), (T("pero las alcantarillas"), C.s_pop(), 0.4), (T("no dan abasto"), C.s_fail(), 0.35),
         (T("y el agua sale"), C.s_clank(), 0.45), (T("y el agua sale") + 0.2, C.s_pop(), 0.35), (T("y el agua sale") + 0.4, C.s_pop(), 0.35),
         (T("así que cavas"), C.s_whoosh(), 0.35), (T("así que cavas") + 1.2, C.s_thud(), 0.5), (T("enterrada"), C.s_bleep(420), 0.2),
         (T("cuando llueve"), C.s_whoosh(), 0.3), (T("el agua de la"), C.s_buzz(1.6), 0.14), (T("el depósito joan"), C.s_pop(), 0.4),
         (T("guarda cincuenta") - 0.35, C.s_coin(), 0.4), (T("pero uno solo"), C.s_fail(), 0.35), (T("así que construyes"), C.s_thud(), 0.45),
         (T("así que construyes") + 0.5, C.s_thud(), 0.4), (T("y los conectas"), C.s_clank(), 0.4), (T("sensores"), C.s_bleep(880), 0.25),
         (T("sensores") + 0.6, C.s_bleep(990), 0.2), (T("y unas compuertas"), C.s_clank(), 0.45), (T("se llena") + 1.0, C.s_clank(), 0.45),
         (T("cuando pasa"), C.s_win(), 0.35), (T("el agua sale poco"), C.s_whoosh(0.8), 0.35), (T("hacia la depuradora"), C.s_pop(), 0.4),
         (T("así no se"), C.s_coin(), 0.35), (T("hoy barcelona") - 0.3, C.s_whoosh(), 0.35)]
    E += [(T("hoy barcelona") + 0.12 * k, C.s_pop(), 0.22) for k in range(0, 15, 3)]
    E += [(T("unas ciento") - 0.35, C.s_whoosh(0.7), 0.35), (T("y en dos mil") - 0.2, C.s_whoosh(), 0.35), (T("y en dos mil") + 1.2, C.s_thud(), 0.45),
          (T("dime en"), C.s_pop(), 0.35), (T("pídelo"), C.s_whoosh(), 0.3), (T("lo más"), C.s_bleep(660), 0.2), (T("sígueme"), C.s_whoosh(), 0.4)]
    E += C.sfx_cifra(T("cuánta agua"), T("juntos guardan"))
    return E
