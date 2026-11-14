# Capa 2D de «¿Guardas la leche en la puerta de la nevera?»
# Pastillas (motion → fotografía): cada una entra ≤0,5 s después del corte de su plano y como mucho 2 por plano.
#  pastilla 22 °C sobre el aire que entra arriba, plano 17,1 · pastilla 200 neveras sobre la isla, plano 28,2
#  pastilla 1,9 °C sobre el termómetro de arriba, plano 30,8 · pastilla 5,2 °C sobre el termómetro de la puerta, plano 33,9
#  pastilla 6 de 10 y 4 °C sobre la fila de neveras, plano 38,4 · pastilla días 17 → 14 y °C 4 → 6 sobre el cartón, plano 45,4.
# Juego de la cifra: tarjeta arriba (no tapa la puerta del primer segundo, que está en el centro), mini arriba-izquierda.
# Ninguna pastilla coincide con la revelación (36,6-38,1) ni con un rótulo de pieza.
from _ovbase import *
from marcas import cargar
T, DUR = cargar("nevera")
SUB_ESTILO = "centro"
SUB_Y = 0.50
KEYWORDS = {"leche", "puerta", "nevera", "peor", "grados", "balda", "arriba", "frío", "caliente", "abajo", "cocina",
            "veintidós", "fondo", "lejísimos", "doscientas", "neveras", "uno", "coma", "nueve", "cinco", "dos", "tres",
            "seis", "diez", "puertas", "cuatro", "bacterias", "cartón", "diecisiete", "días", "menos", "yogures",
            "medio", "salsas", "refrescos", "más"}

def pastilla(C, ctx, t, v, u, a, b, A, key, dx=0, dy=-120, desde=None, dec=0, dur=0.9, size=62, lo=560):
    x, y = A(key); C.pastilla(ctx, t, v, u, a, b, clampx(x + dx, 280), clampy(y + dy, lo, 1380), desde=desde, dec=dec, dur=dur, size=size)

def tarjeta_resuelta(C, ctx, t):
    """tras la revelación la tarjeta no se va: se queda en la esquina con el 3,3 en verde y vuelve grande
    (sin volver a contar) en «¿Te has acercado?»"""
    a0, b0, fin = T("seis de cada") - 0.4, T("te has acercado") - 0.3, T("sígueme")
    if t < a0 or t > fin: return
    m = C.ease((t - a0) / 0.45) if t < b0 else 1 - C.ease((t - b0) / 0.45)
    G, M = (C.W / 2, C.H * 0.33), (C.W * 0.21, C.H * 0.205)
    cx, cy = G[0] + (M[0] - G[0]) * m, G[1] + (M[1] - G[1]) * m
    C._tarjeta_cifra(ctx, cx, cy, 1 - 0.45 * m, "¿TE HAS ACERCADO?" if m < 0.5 else "LA CIFRA", C.miles(3.3, 1),
                     "°C MÁS EN LA PUERTA", C.GREEN, alpha=min(1.0, (fin - t) / 0.3))

def overlay(ctx, t, A, C):
    # la tarjeta se va tras la revelación (deja sitio a las pastillas) y vuelve en «¿Te has acercado?»
    C.cifra_juego(ctx, t, 3.3, "°C MÁS EN LA PUERTA", T("cuántos grados"), T("tres coma"), T("seis de cada") - 0.4, dec=1)
    tarjeta_resuelta(C, ctx, t)
    # rótulos de pieza (uno cada vez, nunca con una pastilla en pantalla)
    C.rotulo(ctx, t, "PUERTA", T("en la puerta") + 0.1, T("es el peor"))
    C.rotulo(ctx, t, "BALDA DE ARRIBA", T("balda de arriba"), T("balda de arriba") + 1.4)
    C.rotulo(ctx, t, "PANEL DEL FONDO", T("el frío sale") + 0.3, T("y la puerta queda"))
    C.rotulo(ctx, t, "BALDA DEL MEDIO", T("balda del medio"), T("al fondo"))
    C.rotulo(ctx, t, "AIRE FRÍO", T("el aire frío"), T("así que se cae") + 0.6)
    C.rotulo(ctx, t, "AIRE DE LA COCINA", T("y por arriba"), T("a unos") - 0.3)
    C.rotulo(ctx, t, "BACTERIAS", T("bacterias"), T("bacterias") + 1.3)
    C.rotulo(ctx, t, "CARTÓN DE LECHE", T("un cartón"), T("diecisiete") - 0.3)
    C.rotulo(ctx, t, "SALSAS Y REFRESCOS", T("salsas"), T("te has acercado") - 0.7)
    # cifras
    pastilla(C, ctx, t, 22, "°C", T("a unos") - 0.2, T("y qué es lo primero"), A, "techo", dy=-90, desde=0, dur=0.9)
    pastilla(C, ctx, t, 200, "neveras", T("investigadores") + 0.1, T("la balda de arriba", 2) - 0.15, A, "grid", dy=-160, desde=0, dur=1.8)
    pastilla(C, ctx, t, 1.9, "°C", T("la balda de arriba", 2) + 0.3, T("y la puerta", 2) - 0.1, A, "t1", dy=-60, desde=3.0, dec=1, dur=2.4)
    pastilla(C, ctx, t, 5.2, "°C", T("y la puerta", 2) + 0.2, T("tres coma") - 0.1, A, "t2", dy=-60, desde=3.0, dec=1, dur=1.6)
    pastilla(C, ctx, t, 6, "de 10", T("seis de cada"), T("pasaban") + 1.1, A, "fila", dy=-200, desde=0, dur=1.6)
    pastilla(C, ctx, t, 4, "°C o más", T("pasaban"), T("pasaban") + 1.1, A, "fila", dy=-70, size=54)
    pastilla(C, ctx, t, 17, "días", T("diecisiete") - 0.2, T("a seis grados"), A, "carton", dx=40, dy=-90, desde=0, dur=1.0)
    pastilla(C, ctx, t, 14, "días", T("a seis grados"), T("días menos", fin=True), A, "carton", dx=40, dy=-90, desde=17, dur=1.6)
    pastilla(C, ctx, t, 4, "°C", T("cuatro grados", 2), T("a seis grados"), A, "carton_lado", dx=-170, dy=60, size=54, lo=600)
    pastilla(C, ctx, t, 6, "°C", T("a seis grados"), T("días menos", fin=True), A, "carton_lado", dx=-170, dy=60, desde=4, size=54, lo=600)
    # textos cortos sobre la escena (no repiten el subtítulo)
    p = win(t, T("lejísimos"), T("y tú la abres"))
    if p: x, y = A("regla"); C.callout(ctx, "LEJOS DEL FRÍO", clampx(x), clampy(min(y - 120, C.H * 0.40), 420), p, size=54)
    p = win(t, T("ya sabes"), DUR + 1)
    if p: x, y = A("carton"); C.callout(ctx, "AQUÍ NO", clampx(x), clampy(y - 110, 420), p, size=60)
    # clics y golpes
    x, y = A("tirador"); C.chispa(ctx, t, x, y, T("abres") + 0.05, r=60)
    x, y = A("puerta"); C.chispa(ctx, t, x, y, T("la puerta", 3), r=70, col=(1, 0.75, 0.4))
    x, y = A("medio"); C.chispa(ctx, t, x, y, T("al fondo", fin=True) - 0.1, r=60)
    x, y = A("botes"); C.chispa(ctx, t, x, y, T("refrescos"), r=60)

def sfx_events(C):
    E = [(0.0, C.s_thud(), 0.45), (0.05, C.s_whoosh(), 0.4), (0.1, C.s_buzz(1.6), 0.1),
         (T("es el peor"), C.s_fail(), 0.3), (T("escribe"), C.s_whoosh(), 0.3),
         (T("abres") + 0.05, C.s_clank(), 0.45), (T("el aire frío"), C.s_whoosh(), 0.3), (T("se cae"), C.s_whoosh(0.7), 0.3),
         (T("y por arriba"), C.s_whoosh(), 0.3), (T("a unos") - 0.3, C.s_pop(), 0.3),
         (T("y qué es lo primero"), C.s_whoosh(), 0.3), (T("la puerta", 3), C.s_thud(), 0.45),
         (T("el frío sale") - 0.1, C.s_whoosh(), 0.3), (T("lejísimos"), C.s_bleep(380), 0.22),
         (T("y tú la abres"), C.s_clank(), 0.3), (T("varias veces"), C.s_clank(), 0.3), (T("al día"), C.s_clank(), 0.3),
         (T("investigadores") - 0.3, C.s_whoosh(), 0.35), (T("investigadores") + 0.2, C.s_tick(), 0.3),
         (T("la balda de arriba", 2) - 0.3, C.s_whoosh(), 0.3), (T("y la puerta", 2) - 0.3, C.s_whoosh(), 0.3),
         (T("seis de cada") - 0.3, C.s_whoosh(), 0.3), (T("diez") + 0.3, C.s_fail(), 0.3),
         (T("y con cada"), C.s_whoosh(), 0.3), (T("bacterias") + 0.2, C.s_buzz(1.2), 0.15),
         (T("un cartón") - 0.2, C.s_pop(), 0.3), (T("días menos", fin=True), C.s_fail(), 0.3),
         (T("qué haces") - 0.2, C.s_whoosh(), 0.35), (T("leche y yogures"), C.s_pop(), 0.3),
         (T("al fondo", fin=True) - 0.1, C.s_clank(), 0.4), (T("salsas"), C.s_pop(), 0.3), (T("refrescos"), C.s_pop(), 0.3),
         (T("te has acercado"), C.s_whoosh(), 0.35), (T("pídelo"), C.s_pop(), 0.3), (T("sígueme"), C.s_whoosh(), 0.4),
         (T("ya sabes"), C.s_whoosh(), 0.35), (T("la leche de tu"), C.s_fail(), 0.25)]
    E += [(T("cuántos grados"), C.s_pop(), 0.5), (T("grados más", fin=True) + 0.05, C.s_win(), 0.4)]   # sin tictac encima de «tres coma tres»
    return E
