# Capa 2D de «¿Pones la comida en el centro del microondas?»
# Pastillas (motion → fotografía): cada una entra ≤0,5 s después del corte de su plano y como mucho 2 por plano.
#  pastilla 75 °C sobre el borde del bol, plano 2,4 · pastilla 8 °C sobre el núcleo, plano 2,4
#  pastilla 2.450 millones/s sobre el magnetrón, plano 12,2 · pastilla 6 vueltas/min sobre el plato, plano 29,4
#  pastilla 85 cm por vuelta sobre el rastro del borde y 0 cm sobre el centro, plano 37,0 · pastilla 3 cm sobre el bol, plano 43,1
#  pastilla 12 cm → 6 cm sobre la regla, plano 54,4.
# Juego de la cifra: tarjeta arriba (no tapa el bol del primer segundo, que está en el centro), mini arriba-izquierda.
from _ovbase import *
from marcas import cargar
T, DUR = cargar("microcentro")
SUB_ESTILO = "centro"
SUB_Y = 0.50
KEYWORDS = {"comida", "centro", "microondas", "fría", "centímetros", "punto", "caliente", "botón", "magnetrón", "ondas",
            "dos", "mil", "cuatrocientos", "cincuenta", "millones", "segundo", "paredes", "metal", "suman", "calientan",
            "anulan", "calientes", "fríos", "plato", "seis", "vueltas", "minuto", "trampa", "frío", "medio", "tres",
            "chocolate", "derrite", "doce", "mitad", "anillo", "borde", "vacío", "remueve"}

def pastilla(C, ctx, t, v, u, a, b, A, key, dx=0, dy=-120, desde=None, dec=0, dur=0.9, size=62, lo=330):
    x, y = A(key); C.pastilla(ctx, t, v, u, a, b, clampx(x + dx, 280), clampy(y + dy, lo, 1380), desde=desde, dec=dec, dur=dur, size=size)

def overlay(ctx, t, A, C):
    C.cifra_juego(ctx, t, 6, "CM ENTRE PUNTOS CALIENTES", T("cada cuántos"), T("se derrite"), T("sígueme"), dec=0)
    # rótulos de pieza (uno cada vez)
    C.rotulo(ctx, t, "MAGNETRÓN", T("magnetrón"), T("magnetrón") + 1.6)
    C.rotulo(ctx, t, "PAREDES DE METAL", T("paredes"), T("paredes") + 1.4)
    C.rotulo(ctx, t, "PLATO GIRATORIO", T("gira el plato"), T("gira el plato") + 1.5)
    C.rotulo(ctx, t, "CHOCOLATE", T("de chocolate"), T("de chocolate") + 1.3)
    # cifras
    pastilla(C, ctx, t, 75, "°C fuera", T("por eso se queda") + 0.3, T("cada cuántos"), A, "borde", dx=-150, dy=-40, desde=20, dur=1.0, lo=980)
    pastilla(C, ctx, t, 8, "°C dentro", T("fría por") , T("cada cuántos"), A, "nucleo", dx=150, dy=170, desde=8, size=58, lo=1150)
    pastilla(C, ctx, t, 2450, "millones/s", T("vibran") + 0.3, T("rebotan"), A, "mag", dx=-120, dy=-90, desde=0, dur=2.4)
    pastilla(C, ctx, t, 6, "vueltas/min", T("unas seis"), T("pero hay"), A, "plato", dy=200, desde=0, dur=0.8, lo=1150)
    pastilla(C, ctx, t, 85, "cm por vuelta", T("no viaja"), T("si ahí cae"), A, "rastro", dy=-110, desde=0, dur=1.2, size=56)
    pastilla(C, ctx, t, 0, "cm el centro", T("solo gira"), T("si ahí cae"), A, "centro", dy=-150, size=56, lo=600)
    pastilla(C, ctx, t, 3, "cm", T("entran"), T("y a qué"), A, "bol", dy=-130, desde=0, dur=1.0)
    pastilla(C, ctx, t, 12, "cm", T("doce") - 0.2, T("la mitad"), A, "regla", dy=180, desde=0, dur=0.6, lo=1150)
    pastilla(C, ctx, t, 6, "cm", T("la mitad"), T("qué haces"), A, "regla", dy=180, desde=12, dur=0.8, lo=1150)
    # punto frío en el centro
    p = win(t, T("si ahí cae"), T("además"))
    if p: x, y = A("centro"); C.callout(ctx, "PUNTO FRÍO", clampx(x), clampy(y - 150, 600), p, size=56)
    p = win(t, T("deja el centro"), T("y a mitad"))
    if p: x, y = A("bol"); C.callout(ctx, "VACÍO", clampx(x), clampy(y + 60, 760), p, size=56)
    # clics y golpes
    x, y = A("boton"); C.chispa(ctx, t, x, y, T("pulsas") + 0.05, r=60)
    x, y = A("pared"); C.chispa(ctx, t, x, y, T("rebotan") + 0.1, r=50); C.chispa(ctx, t, x, y, T("metal"), r=45)
    x, y = A("bol"); C.chispa(ctx, t, x, y, T("remueve"), r=60)

def sfx_events(C):
    E = [(0.0, C.s_thud(), 0.45), (0.05, C.s_whoosh(), 0.4), (0.1, C.s_buzz(2.2), 0.12),
         (T("por eso se queda"), C.s_whoosh(), 0.35), (T("fría por"), C.s_fail(), 0.3), (T("escribe"), C.s_whoosh(), 0.3),
         (T("pulsas") + 0.05, C.s_clank(), 0.45), (T("magnetrón"), C.s_buzz(2.4), 0.2), (T("rebotan") + 0.1, C.s_pop(), 0.35),
         (T("metal"), C.s_pop(), 0.3), (T("y al cruzarse"), C.s_whoosh(), 0.35), (T("calientan", fin=True), C.s_coin(), 0.35),
         (T("no calientan"), C.s_fail(), 0.3), (T("tu microondas tiene"), C.s_whoosh(), 0.3), (T("gira el plato"), C.s_pop(), 0.35),
         (T("pero hay"), C.s_thud(), 0.45), (T("no viaja"), C.s_whoosh(), 0.3), (T("si ahí cae"), C.s_bleep(420), 0.25),
         (T("tu comida se"), C.s_fail(), 0.35), (T("entran"), C.s_whoosh(0.4), 0.3), (T("y a qué"), C.s_whoosh(), 0.3),
         (T("quita el plato"), C.s_whoosh(), 0.35), (T("de chocolate"), C.s_pop(), 0.35), (T("ponla en anillo"), C.s_pop(), 0.35),
         (T("pegada al borde"), C.s_pop(), 0.3), (T("remueve"), C.s_clank(), 0.4), (T("te has acercado"), C.s_whoosh(), 0.35),
         (T("pídelo"), C.s_pop(), 0.3), (T("sígueme"), C.s_whoosh(), 0.4), (T("ya sabes"), C.s_whoosh(), 0.35)]
    E += C.sfx_cifra(T("cada cuántos"), T("se derrite"))
    return E
