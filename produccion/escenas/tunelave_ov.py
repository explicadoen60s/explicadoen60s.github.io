# Capa 2D de «¿Cuántos kilómetros de túnel unen Atocha con Chamartín?» (Lo que esconde tu ciudad)
# Pastillas (motion → fotografía), en el tercio de arriba, lejos del mini del juego (arriba-izquierda):
#  55 m junto a la flecha de profundidad (22,2-24) · 18 plantas sobre el edificio boca abajo (24,1-26,8)
#  · 338 M€ sobre el túnel (44,3-47,1) · 120 km/h sobre el AVE (47,2-51). Callouts: ATOCHA / CHAMARTÍN sobre las estaciones,
#  JULIO 2022 y GALICIA → ANDALUCÍA. La tarjeta del juego (7,3 km) arriba; se encoge a la esquina de arriba a la izquierda.
from _ovbase import *
from marcas import cargar
T, DUR = cargar("tunelave")
SUB_ESTILO = "centro"
SUB_Y = 0.50
KEYWORDS = {"kilómetros", "túnel", "atocha", "chamartín", "madrid", "dos", "redes", "alta", "velocidad", "sur", "norte", "estación",
            "metro", "colectores", "cimientos", "cincuenta", "cinco", "metros", "dieciocho", "plantas", "tierra", "calle", "hundirse",
            "tuneladora", "presión", "siete", "coma", "tres", "vías", "ancho", "internacional", "ave", "julio", "veintidós",
            "trescientos", "treinta", "ocho", "millones", "euros", "ciento", "veinte", "hora", "galicia", "andalucía", "tren"}

def pastilla(C, ctx, t, v, u, a, b, A, key, dx=0, dy=-150, desde=0, dec=0, dur=0.9, size=66, lo=430, hi=700):
    x, y = A(key); C.pastilla(ctx, t, v, u, a, b, clampx(x + dx, 330), clampy(y + dy, lo, hi), desde=desde, dec=dec, dur=dur, size=size)

def overlay(ctx, t, A, C):
    juego_completo(C, ctx, t, 7.3, "KM DE TÚNEL", T("cuántos kilómetros"), T("el túnel mide"), T("te has acercado"), T("sígueme"), dec=1)
    # rótulos de pieza (uno cada vez)
    C.rotulo(ctx, t, "TUNELADORA", 0.3, 2.3)
    C.rotulo(ctx, t, "METRO", T("hay metro"), T("colectores") - 0.05)
    C.rotulo(ctx, t, "COLECTORES", T("colectores"), T("cimientos") - 0.05)
    C.rotulo(ctx, t, "CIMIENTOS", T("cimientos"), T("así que bajas") - 0.1)
    C.rotulo(ctx, t, "PRESIÓN DE TIERRAS", T("de presión"), T("que sujeta") + 1.4)
    C.rotulo(ctx, t, "ANCHO INTERNACIONAL", T("de ancho"), T("como el ave", fin=True))
    # estaciones
    p = win(t, T("a atocha"), T("los del norte") - 0.1)
    if p: x, y = A("atocha"); C.callout(ctx, "ATOCHA", clampx(x, 300), clampy(y - 90, 600, 1100), p, size=58)
    p = win(t, T("a chamartín"), T("pero no se") + 0.6)
    if p: x, y = A("chamartin"); C.callout(ctx, "CHAMARTÍN", clampx(x, 300), clampy(y - 90, 600, 1100), p, size=58)
    # cifras
    pastilla(C, ctx, t, 55, "m bajo la calle", T("hasta") - 0.1, T("más hondo") - 0.1, A, "medio", dx=260, dy=-250, dur=1.2)
    pastilla(C, ctx, t, 18, "plantas", T("más hondo"), T("pero la tierra"), A, "edif_top", dx=0, dy=-140, dur=1.4)
    pastilla(C, ctx, t, 338, "millones de €", T("costó"), T("y los trenes") - 0.1, A, "tunel", dx=60, dy=-260, dur=1.6)
    pastilla(C, ctx, t, 120, "km/h máx.", T("y los trenes"), T("ahora") - 0.1, A, "tren", dx=40, dy=-180, dur=1.8)
    p = win(t, T("lo abrieron"), T("costó") - 0.1)
    if p: x, y = A("tunel"); C.callout(ctx, "JULIO 2022", clampx(x + 60, 320), C.H * 0.22, p, size=62)
    p = win(t, T("de galicia"), T("te has acercado") - 0.1)
    if p: C.callout(ctx, "GALICIA – ANDALUCÍA", C.W / 2, C.H * 0.31, p, size=60)
    # clics y golpes
    x, y = A("sur"); C.chispa(ctx, t, x, y, T("a atocha", fin=True) - 0.1, r=60)
    x, y = A("norte"); C.chispa(ctx, t, x, y, T("a chamartín", fin=True) - 0.1, r=60)
    x, y = A("calle")
    for k in range(3): C.chispa(ctx, t, x, y, T("hundirse") + 0.25 * k, r=60, col=(1, 0.5, 0.4))
    x, y = A("fondo"); C.chispa(ctx, t, x, y, T("metros", 1, fin=True), r=70)
    x, y = A("via"); C.chispa(ctx, t, x, y, T("y lleva") + 0.4, r=55)

def sfx_events(C):
    E = [(0.0, C.s_whoosh(), 0.35), (0.05, C.s_buzz(2.4), 0.15), (T("madrid") - 0.2, C.s_whoosh(0.7), 0.4),
         (T("los trenes"), C.s_buzz(1.4), 0.12), (T("a atocha", fin=True) - 0.1, C.s_clank(), 0.4),
         (T("los del norte"), C.s_buzz(1.2), 0.12), (T("a chamartín", fin=True) - 0.1, C.s_clank(), 0.4),
         (T("pero no se"), C.s_fail(), 0.35), (T("para seguir"), C.s_pop(), 0.3), (T("hay que"), C.s_whoosh(), 0.35),
         (T("hay metro"), C.s_pop(), 0.35), (T("cimientos"), C.s_pop(), 0.35),
         (T("así que bajas"), C.s_whoosh(0.8), 0.4), (T("hasta") - 0.3, C.s_tick(), 0.35), (T("más hondo"), C.s_thud(), 0.45),
         (T("pero la tierra"), C.s_whoosh(), 0.3), (T("hundirse"), C.s_fail(), 0.35), (T("así que usas") - 0.1, C.s_whoosh(), 0.4),
         (T("así que usas") + 0.4, C.s_buzz(2.0), 0.15), (T("que sujeta"), C.s_thud(), 0.4),
         (T("y lleva") + 0.4, C.s_clank(), 0.4), (T("lo abrieron"), C.s_pop(), 0.35), (T("costó") - 0.2, C.s_coin(), 0.4),
         (T("y los trenes") - 0.2, C.s_whoosh(0.8), 0.4),          (T("ahora"), C.s_whoosh(), 0.35), (T("ya no te"), C.s_win(), 0.35), (T("te has acercado"), C.s_whoosh(), 0.35),
         (T("dime en"), C.s_bleep(620), 0.25), (T("y si quieres"), C.s_whoosh(), 0.3), (T("lo más pedido"), C.s_pop(), 0.35),
         (T("sígueme"), C.s_whoosh(), 0.4), (T("así que ya sabes"), C.s_whoosh(), 0.35)]
    E += C.sfx_cifra(T("cuántos kilómetros"), T("el túnel mide"))
    return E
