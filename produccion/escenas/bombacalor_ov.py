# Capa 2D de «¿Cuánto calor saca tu aire acondicionado de cada kWh de luz?»
# Pastillas previstas (motion → fotografía), todas encima de su pieza y fuera del subtítulo del centro:
# 5 °C sobre la calle (cuenta de 12 a 5) · −50 °C sobre el tubo (cuenta de 0 a −50) · gas −10 °C frente a calle 5 °C en la
# máquina exterior · gas −2 → 75 °C sobre el compresor · salón 17 → 22 °C · 1 kWh de luz sobre el enchufe · 0 → 4 kWh de
# calor junto al split (bajo la tarjeta del juego) · radiador 1 kWh → 1 kWh. Juego de la cifra: tarjeta arriba, mini arriba-izquierda.
from _ovbase import *
from marcas import cargar
T, DUR = cargar("bombacalor")
SUB_ESTILO = "centro"
SUB_Y = 0.50
KEYWORDS = {"frío", "aire", "acondicionado", "calor", "kilovatio", "kilovatios", "luz", "calle", "cinco", "grados", "resistencia",
            "radiador", "circuito", "gas", "cincuenta", "cero", "máquina", "balcón", "tubo", "compresor", "aprieta", "caliente",
            "salón", "ventilador", "ventiladores", "habitación", "cuatro", "uno", "verano", "revés", "fuera", "dentro"}

def pastilla(C, ctx, t, v, u, a, b, A, key, dx=0, dy=-130, desde=None, dec=0, dur=0.9, size=64, lo=300):
    x, y = A(key); C.pastilla(ctx, t, v, u, a, b, clampx(x + dx, 300), clampy(y + dy, lo, 1350), desde=desde, dec=dec, dur=dur, size=size)

def overlay(ctx, t, A, C):
    # juego de la cifra
    C.cifra_juego(ctx, t, 4, "kWh DE CALOR POR 1 DE LUZ", T("cuánto calor"), T("por eso"), T("sígueme"), dec=0)
    # rótulos de pieza (uno cada vez)
    C.rotulo(ctx, t, "RESISTENCIA", T("resistencia"), T("resistencia") + 1.5)
    C.rotulo(ctx, t, "RADIADOR", T("como un radiador"), T("pero no"))
    C.rotulo(ctx, t, "CIRCUITO CERRADO", T("circuito"), T("circuito") + 1.6)
    C.rotulo(ctx, t, "MÁQUINA EXTERIOR", T("en la máquina"), T("en la máquina") + 1.5)
    C.rotulo(ctx, t, "COMPRESOR", T("compresor"), T("compresor") + 1.5)
    C.rotulo(ctx, t, "SPLIT DEL SALÓN", T("salón") - 0.3, T("salón") + 1.3)
    C.rotulo(ctx, t, "VENTILADOR", T("un ventilador"), T("un ventilador") + 1.3)
    C.rotulo(ctx, t, "VÁLVULA", T("el gas", 3), T("el gas", 3) + 1.4)
    # cifras
    pastilla(C, ctx, t, 5, "°C en la calle", T("cómo saca"), T("mucha gente"), A, "calle", dy=-110, desde=12, dur=1.6)
    pastilla(C, ctx, t, -50, "°C hierve", T("ese gas hierve") + 0.3, T("fuera", 2), A, "gas", dy=-150, desde=0, dur=1.6)
    pastilla(C, ctx, t, 5, "°C calle", T("el gas está"), T("el gas se lo"), A, "calle", dy=-110)
    pastilla(C, ctx, t, -10, "°C gas", T("más frío") - 0.2, T("el gas se lo"), A, "ext", dy=-150, desde=5, dur=1.2)
    pastilla(C, ctx, t, 75, "°C gas", T("al apretarlo"), T("salón"), A, "comp", dy=-170, desde=-2, dur=1.8)
    pastilla(C, ctx, t, 22, "°C salón", T("y el calor sale"), T("y empieza"), A, "sala", dy=-200, desde=17, dur=2.0)
    pastilla(C, ctx, t, 1, "kWh de luz", T("la luz solo"), T("lo traslada"), A, "enchufe", dy=-140, desde=0, dur=0.6)
    pastilla(C, ctx, t, 1, "kWh de luz", T("de luz", 2), T("un radiador eléctrico"), A, "enchufe", dy=-140, desde=0, dur=0.5, size=56, lo=820)
    pastilla(C, ctx, t, 4, "kWh de calor", T("te da unos"), T("un radiador eléctrico"), A, "split", dx=180, dy=260, desde=0, dur=1.0, lo=820)
    pastilla(C, ctx, t, 1, "kWh → 1 de calor", T("un radiador eléctrico"), T("pero al revés", fin=True), A, "rad", dy=-170, desde=0, dur=0.8, size=56, lo=820)
    # tachón de la resistencia que no existe
    p = win(t, T("pero no"), T("dentro hay"))
    if p: x, y = A("split"); C.callout(ctx, "NO LLEVA", clampx(x), clampy(y - 120, 300), p, size=62)
    # clics y golpes
    x, y = A("split"); C.chispa(ctx, t, x, y + 40, 1.6, r=60)
    x, y = A("comp"); C.chispa(ctx, t, x, y, T("aprieta"), r=70); C.chispa(ctx, t, x, y, T("aprieta") + 0.5, r=55)
    x, y = A("tubo"); C.chispa(ctx, t, x, y, T("el gas", 3) + 0.4, r=50)

def sfx_events(C):
    E = [(0.0, C.s_whoosh(), 0.4), (0.05, C.s_buzz(1.5), 0.15), (1.6, C.s_clank(), 0.4), (T("modo calor"), C.s_bleep(880), 0.25),
         (T("parece magia"), C.s_whoosh(), 0.35), (T("cómo saca"), C.s_tick(), 0.3), (T("mucha gente"), C.s_whoosh(), 0.3),
         (T("resistencia") - 0.1, C.s_buzz(0.8), 0.2), (T("como un radiador"), C.s_pop(), 0.4), (T("pero no"), C.s_fail(), 0.45),
         (T("dentro hay"), C.s_whoosh(), 0.35), (T("circuito"), C.s_pop(), 0.4), (T("ese gas hierve"), C.s_bleep(400), 0.25),
         (T("fuera", 2), C.s_whoosh(), 0.35), (T("el gas está"), C.s_pop(), 0.35), (T("así que el aire"), C.s_whoosh(0.8), 0.35),
         (T("le pasa calor"), C.s_coin(), 0.35), (T("el gas se lo"), C.s_whoosh(), 0.3), (T("luego"), C.s_thud(), 0.45),
         (T("aprieta"), C.s_clank(), 0.5), (T("aprieta") + 0.5, C.s_clank(), 0.4), (T("al apretarlo"), C.s_buzz(1.6), 0.2),
         (T("y ese gas"), C.s_whoosh(), 0.35), (T("salón") - 0.3, C.s_pop(), 0.4), (T("un ventilador"), C.s_buzz(1.2), 0.18),
         (T("y el calor sale"), C.s_win(), 0.3), (T("el gas", 3) + 0.4, C.s_tick(), 0.4), (T("y empieza"), C.s_whoosh(), 0.35),
         (T("la luz solo"), C.s_bleep(660), 0.25), (T("no fabrica"), C.s_fail(), 0.3), (T("lo traslada"), C.s_whoosh(0.8), 0.4),
         (T("te da unos") - 0.3, C.s_pop(), 0.35), (T("un radiador eléctrico") - 0.3, C.s_thud(), 0.4),
         (T("en verano"), C.s_whoosh(), 0.35), (T("pero al revés"), C.s_coin(), 0.35), (T("te has acercado"), C.s_whoosh(), 0.35),
         (T("pídelo"), C.s_pop(), 0.35), (T("sígueme"), C.s_whoosh(), 0.4)]
    E += C.sfx_cifra(T("cuánto calor"), T("por eso"))
    return E
