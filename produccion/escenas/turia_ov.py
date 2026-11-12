# Capa 2D de «Valencia movió un río entero» (Lo que esconde tu ciudad, parte 2)
# Pastillas previstas (motion → fotografía): 9 km sobre el parque, 3.700 m³/s sobre el río y piscinas olímpicas debajo,
# 5 m sobre la calle inundada, 12 km y 175 m sobre el cauce nuevo, 5.000 frente a 3.700 m³/s y 5.000 → 0 cuando se seca.
from _ovbase import *
from marcas import cargar
T, DUR = cargar("turia")
SUB_ESTILO = "centro"
KEYWORDS = {"valencia", "parque", "nueve", "kilómetros", "río", "turia", "ciudad", "agua", "mil", "novecientos", "cincuenta", "siete",
            "tres", "setecientos", "metros", "cúbicos", "segundo", "cauce", "cinco", "muros", "doce", "ciento", "setenta", "ancho",
            "muro", "tierra", "carreteras", "tren", "puentes", "seco", "vacío", "autopista", "jardín", "campos", "bici", "árboles", "fondo"}

def pastilla(C, ctx, t, v, u, a, b, A, key, dx=0, dy=-120, desde=0, dec=0, dur=0.9, size=68):
    x, y = A(key); C.pastilla(ctx, t, v, u, a, b, clampx(x + dx, 300), clampy(y + dy, 430, 1350), desde=desde, dec=dec, dur=dur, size=size)

def overlay(ctx, t, A, C):
    # rótulos (uno cada vez)
    C.rotulo(ctx, t, "TURIA", T("el turia"), T("el turia") + 1.6)
    C.rotulo(ctx, t, "CAUCE NUEVO", T("excavas"), T("excavas") + 1.7)
    C.rotulo(ctx, t, "MURO DE TIERRA", T("cierras"), T("cierras") + 1.8)
    C.rotulo(ctx, t, "PUENTES", T("levantas puentes"), T("levantas puentes") + 1.5)
    C.rotulo(ctx, t, "CAUCE VIEJO", T("y el cauce viejo"), T("y el cauce viejo") + 1.6)
    C.rotulo(ctx, t, "JARDÍN DEL TURIA", T("así que hoy"), T("así que hoy") + 1.8)
    # 9 km de parque
    pastilla(C, ctx, t, 9, "km", 0.2, T("que antes", fin=True) + 0.3, A, "parque", dur=1.6)
    # año de la riada
    p = win(t, T("pero en mil"), T("llegaron"))
    if p: x, y = A("arriba"); C.callout(ctx, "OCTUBRE 1957", clampx(x), clampy(y - 170, 430), p, size=62)
    # caudal de la riada y su comparación
    pastilla(C, ctx, t, 3700, "m³/s", T("llegaron"), T("y el agua se metió"), A, "rio", dy=-150, dur=2.0)
    pastilla(C, ctx, t, 1.5, "piscinas olímpicas cada segundo", T("cúbicos") + 0.3, T("y el agua se metió"), A, "rio", dy=-40, dec=1, dur=0.8, size=54)
    # agua en las calles
    pastilla(C, ctx, t, 5, "m de agua", T("en algunas"), T("podrías hacer"), A, "calle", dy=-160, dur=1.6)
    # cauce nuevo
    pastilla(C, ctx, t, 12, "km", T("doce") - 0.1, T("ciento"), A, "nuevo", dy=-150, dur=1.0)
    pastilla(C, ctx, t, 175, "m de ancho", T("ciento") - 0.1, T("pero el agua siempre"), A, "ancho", dy=-150, dur=1.6)
    # capacidad del cauce nuevo frente a la riada
    pastilla(C, ctx, t, 5000, "m³/s", T("cinco mil") - 0.2, T("y casi todo"), A, "nuevo", dy=-170, dur=2.0)
    pastilla(C, ctx, t, 3700, "m³/s en 1957", T("más que aquella"), T("y casi todo"), A, "nuevo", dy=-60, dur=0.01, size=52)
    pastilla(C, ctx, t, 0, "m³/s", T("y casi todo"), T("y el cauce viejo"), A, "nuevo", dy=-150, desde=5000, dur=1.8)
    # 9 km de jardín
    pastilla(C, ctx, t, 9, "km de jardín", T("con campos"), T("si has paseado"), A, "viejo", dy=-170, dur=1.4)
    # golpes y clics
    x, y = A("muro"); C.chispa(ctx, t, x, y, T("de tierra"), r=70)
    x, y = A("puentes"); C.chispa(ctx, t, x, y, T("levantas puentes") + 0.35, r=60)

def sfx_events(C):
    E = [(0.0, C.s_whoosh(), 0.4), (0.1, C.s_buzz(2.0), 0.15), (0.4, C.s_tick(), 0.3), (T("que antes"), C.s_pop(), 0.4),
         (T("cómo se mueve"), C.s_whoosh(), 0.35), (T("el turia"), C.s_pop(), 0.4), (T("casi siempre"), C.s_bleep(480), 0.2),
         (T("pero en mil"), C.s_thud(), 0.5), (T("pero en mil") + 0.6, C.s_buzz(2.6), 0.18), (T("llegaron") - 0.3, C.s_tick(), 0.4),
         (T("el cauce no"), C.s_fail(), 0.4), (T("y el agua se metió"), C.s_whoosh(0.8), 0.45), (T("en algunas") - 0.3, C.s_tick(), 0.4),
         (T("podrías hacer"), C.s_clank(), 0.45), (T("pero el río"), C.s_fail(), 0.35), (T("así que decides"), C.s_whoosh(), 0.4),
         (T("excavas"), C.s_thud(), 0.45), (T("excavas") + 0.6, C.s_clank(), 0.3), (T("doce") - 0.3, C.s_tick(), 0.4),
         (T("ciento") - 0.3, C.s_pop(), 0.45), (T("pero el agua siempre"), C.s_whoosh(), 0.35), (T("cierras"), C.s_thud(), 0.5),
         (T("de tierra"), C.s_clank(), 0.45), (T("y el agua gira"), C.s_whoosh(0.8), 0.4), (T("pero por encima"), C.s_bleep(620), 0.25),
         (T("levantas puentes") + 0.35, C.s_pop(), 0.45), (T("levantas puentes") + 1.05, C.s_pop(), 0.45), (T("levantas puentes") + 1.75, C.s_pop(), 0.45),
         (T("y aquí viene"), C.s_whoosh(), 0.35), (T("cinco mil") - 0.3, C.s_tick(), 0.4), (T("más que aquella"), C.s_win(), 0.4),
         (T("y casi todo"), C.s_whoosh(), 0.3), (T("esperando"), C.s_coin(), 0.35), (T("y el cauce viejo"), C.s_pop(), 0.4),
         (T("querían"), C.s_thud(), 0.4), (T("pero los vecinos"), C.s_fail(), 0.35), (T("así que hoy"), C.s_win(), 0.4),
         (T("con campos"), C.s_pop(), 0.35), (T("carriles bici"), C.s_pop(), 0.35), (T("si has paseado"), C.s_whoosh(), 0.35),
         (T("fondo"), C.s_coin(), 0.4), (T("sígueme"), C.s_whoosh(), 0.4)]
    return E
