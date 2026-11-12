# Capa 2D de «¿Hasta dónde llega tu wifi de 5 GHz?» (Wifi, parte 3)
# Pastillas previstas (motion → fotografía), en el tercio de arriba y desplazadas del eje del objeto:
# 2.400 millones/s sobre la onda amarilla (≈ x 700, y 560) · 5.000 millones/s sobre la azul · % de señal tras el pladur
# (100 → 50) y tras el ladrillo (100 → 18 → 6 en 5 GHz) sobre cada pared · 45 m sobre el anillo amarillo (y ≈ 450).
# El juego de la cifra va grande en H*0.33 (el router queda abajo, en H*0.68) y mini en la esquina de arriba a la izquierda.
# KEYWORDS: 33 (piezas, materiales y cifras con plurales).
from _ovbase import *
from marcas import cargar
T, DUR = cargar("wifi5ghz")
SUB_ESTILO = "centro"
SUB_Y = 0.50
KEYWORDS = {"router", "frecuencias", "metros", "cinco", "gigahercios", "móvil", "redes", "wifi", "dos", "coma", "cuatro", "mil",
            "cuatrocientos", "millones", "doble", "vibraciones", "datos", "rápida", "onda", "pladur", "ladrillo", "hormigón", "nevera",
            "obstáculo", "señal", "tabique", "mitad", "macizo", "quinta", "cuarenta", "quince", "habitación", "paredes"}

def pastilla(C, ctx, t, v, u, a, b, A, key, dx=0, dy=-140, desde=None, dec=0, dur=0.9, size=64):
    x, y = A(key); C.pastilla(ctx, t, v, u, a, b, clampx(x + dx, 300), clampy(y + dy, 330, 640), desde=desde, dec=dec, dur=dur, size=size)

def overlay(ctx, t, A, C):
    C.cifra_juego(ctx, t, 15, "METROS EN 5 GHz", T("hasta cuántos"), T("la de cinco solo"), T("sígueme"), dec=0)
    # rótulos de pieza (uno cada vez)
    C.rotulo(ctx, t, "ROUTER", 0.15, 1.9)
    C.rotulo(ctx, t, "PLADUR", T("el pladur"), T("el ladrillo") - 0.05)
    C.rotulo(ctx, t, "LADRILLO", T("el ladrillo"), T("el hormigón") - 0.05)
    C.rotulo(ctx, t, "HORMIGÓN", T("el hormigón"), T("tu nevera") - 0.05)
    C.rotulo(ctx, t, "NEVERA", T("tu nevera"), T("tu nevera") + 1.3)
    C.rotulo(ctx, t, "LADRILLO MACIZO", T("y una pared"), T("y una pared") + 1.6)
    # bandas en la lista del móvil
    p = win(t, T("muchas veces") + 0.4, T("la de dos coma") - 0.3)
    if p: x, y = A("phone"); C.callout(ctx, "2,4 GHz  ·  5 GHz", clampx(x), clampy(y - 230, 330, 640), p, size=54)
    # vibraciones por segundo
    pastilla(C, ctx, t, 2400, "millones/s", T("dos mil") - 0.2, T("la de cinco", 2) - 0.1, A, "s24", dx=60, dy=-130, desde=0, dur=1.8)
    pastilla(C, ctx, t, 5000, "millones/s", T("la de cinco", 2), T("pero hay una"), A, "s5", dx=60, dy=-150, desde=2400, dur=1.2)
    p = win(t, T("y caben"), T("pero hay una"))
    if p:
        x, y = A("s24"); C.callout(ctx, "2,4 GHz", clampx(x + 250, 320), clampy(y + 40, 330, 900), p, size=50)
        x, y = A("s5"); C.callout(ctx, "5 GHz", clampx(x + 250, 320), clampy(y + 60, 330, 1300), p, size=50)
    # la señal que se queda cada pared
    pastilla(C, ctx, t, 50, "% señal", T("un tabique"), T("y una pared") - 0.1, A, "pladur", dx=140, dy=-160, desde=100, dur=1.6)
    pastilla(C, ctx, t, 18, "% señal", T("deja pasar"), T("y en cinco"), A, "ladrillo", dx=140, dy=-160, desde=100, dur=1.6)
    pastilla(C, ctx, t, 6, "% en 5 GHz", T("y en cinco"), T("por eso", 2), A, "ladrillo", dx=140, dy=-160, desde=18, dur=1.2)
    # alcance
    pastilla(C, ctx, t, 45, "m en 2,4 GHz", T("cuarenta y cinco") - 0.3, T("la de cinco solo") - 0.2, A, "r45", dy=-60, desde=0, dur=1.2)
    # clics: cada obstáculo que se nombra y el cambio de red
    for k, key in (("el pladur", "pladur"), ("el ladrillo", "ladrillo"), ("el hormigón", "horm"), ("tu nevera", "nevera")):
        x, y = A(key); C.chispa(ctx, t, x, y, T(k) + 0.1, r=60)
    x, y = A("phone"); C.chispa(ctx, t, x, y - 40, T("la de cinco", 5) + 0.1, r=55)
    C.chispa(ctx, t, x, y - 40, T("la de dos coma", 3) + 0.2, r=55, col=(1.0, 0.85, 0.3))

def sfx_events(C):
    E = [(0.0, C.s_whoosh(), 0.35), (0.05, C.s_buzz(1.8), 0.15), (T("en dos"), C.s_bleep(880), 0.25),
         (T("escribe"), C.s_whoosh(), 0.35), (T("mira la"), C.s_whoosh(), 0.35), (T("muchas veces"), C.s_pop(), 0.4),
         (T("una acaba"), C.s_bleep(1200), 0.25), (T("la de dos coma") - 0.3, C.s_whoosh(), 0.35), (T("dos mil") - 0.4, C.s_buzz(1.6), 0.15),
         (T("la de cinco", 2) - 0.25, C.s_buzz(1.2), 0.18), (T("más vibraciones"), C.s_whoosh(), 0.3), (T("y caben"), C.s_pop(), 0.4),
         (T("y caben") + 0.4, C.s_pop(), 0.35), (T("por eso la"), C.s_coin(), 0.4), (T("pero hay una"), C.s_fail(), 0.4),
         (T("cuanto más"), C.s_whoosh(), 0.3), (T("el pladur"), C.s_thud(), 0.45), (T("el ladrillo"), C.s_thud(), 0.45),
         (T("el hormigón"), C.s_thud(), 0.5), (T("tu nevera"), C.s_clank(), 0.45), (T("cada obstáculo"), C.s_whoosh(), 0.35),
         (T("un tabique") - 0.3, C.s_tick(), 0.4), (T("la mitad"), C.s_thud(), 0.4), (T("y una pared") - 0.3, C.s_whoosh(), 0.3),
         (T("deja pasar") - 0.3, C.s_tick(), 0.4), (T("y en cinco") - 0.3, C.s_fail(), 0.4), (T("por eso", 2), C.s_whoosh(0.8), 0.4),
         (T("cuarenta y cinco") - 0.4, C.s_tick(), 0.4), (T("entonces"), C.s_whoosh(), 0.35), (T("en la misma"), C.s_pop(), 0.4),
         (T("la de cinco", 5) + 0.1, C.s_win(), 0.35), (T("con dos"), C.s_whoosh(0.7), 0.35), (T("la de dos coma", 3) + 0.2, C.s_coin(), 0.4),
         (T("pídelo"), C.s_pop(), 0.35), (T("sígueme"), C.s_whoosh(), 0.4)]
    E += C.sfx_cifra(T("hasta cuántos"), T("la de cinco solo"))
    return E
