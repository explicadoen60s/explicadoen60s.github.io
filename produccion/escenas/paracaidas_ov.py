# Capa 2D de «Si tuvieras que inventar un paracaídas»
# Pastillas previstas (motion → fotografía): velocidad junto al cuerpo (x+230, tercio superior), superficie de la tela
# encima de ella, % de apertura junto al deslizador, 200 → 22 km/h junto al cuerpo, altímetro junto a los pies.
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("paracaidas")
SUB_ESTILO = "frase"
KEYWORDS = {"avión", "doce", "segundos", "doscientos", "kilómetros", "hora", "aire", "arriba", "superficie", "tela", "cuerdas",
            "espalda", "tirón", "mochila", "paracaídas", "pequeñito", "paraguas", "anillas", "apertura", "cúpula", "ala", "celdas",
            "hincha", "rígida", "colchón", "asas", "veintidós", "tres", "metros", "suelo", "frena", "andando", "velocidad"}

def overlay(ctx, t, A, C0):
    C = Guard(C0)
    # rótulos de pieza
    C.rotulo(ctx, t, "TELA", T("una tela"), T("una tela") + 1.5)
    C.rotulo(ctx, t, "MOCHILA", T("mochila"), T("mochila") + 1.5)
    C.rotulo(ctx, t, "EXTRACTOR", T("paracaídas pequeñito"), T("paracaídas pequeñito") + 1.7)
    C.rotulo(ctx, t, "DESLIZADOR", T("un trozo"), T("un trozo") + 1.8)
    C.rotulo(ctx, t, "CELDAS", T("tiene celdas"), T("tiene celdas") + 1.6)
    C.rotulo(ctx, t, "MANDOS", T("dos asas"), T("dos asas") + 1.5)
    # velocidad en caída libre 0 → 200 km/h y segundos
    x, y = A("cuerpo")
    C.pastilla(ctx, t, 200, "km/h", -0.2, T("vamos a") - 0.1, clampx(x + 240, 300), clampy(y - 260, 470), desde=0, dur=4.0)
    C.pastilla(ctx, t, 12, "s", 1.0, T("vamos a") - 0.1, clampx(x - 240, 300), clampy(y - 260, 470), desde=0, dur=3.2, size=60)
    # superficie de la tela
    x, y = A("tela")
    C.pastilla(ctx, t, 13, "m²", T("cuanto más"), T("así que coges") + 0.4, clampx(x + 200, 300), clampy(y - 170, 470), desde=1, dur=1.7)
    # tirón
    if T("a esa velocidad") + 0.3 <= t < T("de verdad", fin=True) + 0.2:
        x, y = A("cuerpo"); C.chispa(ctx, t, x, y - 40, T("a esa velocidad") + 0.3, r=110, col=(1, 0.3, 0.25))
        C.callout(ctx, "¡TIRÓN!", clampx(x + 160), clampy(y - 230, 470), win(t, T("a esa velocidad") + 0.3, T("de verdad", fin=True) + 0.2), size=64)
    # extractor: clic al salir
    x, y = A("piloto"); C.chispa(ctx, t, x, y, T("y la sacas") + 0.3, r=70)
    # apertura lenta con el deslizador
    x, y = A("slider")
    C.pastilla(ctx, t, 100, "% abierto", T("se queda arriba"), T("y aquí viene"), clampx(x + 200, 320), clampy(y - 150, 470), desde=25, dur=2.4, size=62)
    # celdas que se hinchan: presión
    x, y = A("ala")
    C.pastilla(ctx, t, 100, "% hinchada", T("el aire entra"), T("así no solo"), clampx(x, 320), clampy(y - 200, 470), desde=25, dur=1.6, size=62)
    # velocidad bajo el ala 200 → 22
    x, y = A("cuerpo")
    C.pastilla(ctx, t, 22, "km/h", T("la velocidad baja"), T("pero para tocar"), clampx(x + 250, 300), clampy(y - 250, 470), desde=200, dur=3.2, size=76)
    # altímetro hasta el suelo
    x, y = A("pies")
    if T("a unos tres") - 0.6 <= t < T("aterrizas", fin=True) + 0.4:
        v = keyed01(t, [(T("a unos tres") - 0.6, 9.0), (T("metros del"), 3.0), (T("el ala se"), 2.0), (T("aterrizas"), 0.0)])
        C.pastilla(ctx, t, v, "m", T("a unos tres") - 0.6, T("aterrizas", fin=True) + 0.4, clampx(x + 230, 300), clampy(y - 120, 470, 1300), dec=0)
    x, y = A("pies"); C.chispa(ctx, t, x, y, T("aterrizas") + 0.1, r=80)
    x, y = A("mando"); C.chispa(ctx, t, x, y, T("tiras de las dos") + 0.4, r=55)

class Guard:
    """evita la escala 0 de la pastilla justo en su primer instante"""
    def __init__(self, C): self.C = C
    def __getattr__(self, k): return getattr(self.C, k)
    def pastilla(self, ctx, t, valor, unidad, a, b, *r, **kw):
        if t >= a + 0.01: self.C.pastilla(ctx, t, valor, unidad, a, b, *r, **kw)

def keyed01(t, ks):
    if t <= ks[0][0]: return ks[0][1]
    for (a, va), (b, vb) in zip(ks, ks[1:]):
        if a <= t <= b:
            u = (t - a) / max(b - a, 1e-4); u = u * u * (3 - 2 * u); return va + (vb - va) * u
    return ks[-1][1]

def sfx_events(C):
    E = [(0.0, C.s_whoosh(1.2), 0.5), (0.2, C.s_buzz(4.0), 0.12), (T("doscientos") - 0.4, C.s_tick(), 0.4),
         (T("vamos a"), C.s_pop(), 0.4), (T("necesitas que"), C.s_whoosh(), 0.35), (T("hacia arriba"), C.s_pop(), 0.35),
         (T("cuanto más"), C.s_whoosh(), 0.35), (T("más aire"), C.s_coin(), 0.35), (T("así que coges"), C.s_whoosh(0.8), 0.45),
         (T("y la atas"), C.s_clank(), 0.4), (T("pero si se abre"), C.s_whoosh(), 0.35), (T("a esa velocidad") + 0.3, C.s_thud(), 0.7),
         (T("de verdad") - 0.1, C.s_fail(), 0.4), (T("así que la doblas"), C.s_whoosh(), 0.35), (T("mochila"), C.s_clank(), 0.45),
         (T("y la sacas") + 0.3, C.s_pop(), 0.5), (T("del tamaño"), C.s_bleep(660), 0.25), (T("ese pequeño"), C.s_whoosh(0.9), 0.4),
         (T("pero aún"), C.s_fail(), 0.35), (T("así que pones"), C.s_pop(), 0.4), (T("anillas"), C.s_clank(), 0.4),
         (T("se queda arriba"), C.s_whoosh(1.0), 0.35), (T("unos segundos", fin=True), C.s_win(), 0.35), (T("y aquí viene"), C.s_whoosh(), 0.4),
         (T("es un ala"), C.s_pop(), 0.5), (T("tiene celdas"), C.s_tick(), 0.35), (T("el aire entra"), C.s_whoosh(), 0.35),
         (T("las hincha"), C.s_pop(), 0.45), (T("colchón"), C.s_thud(), 0.4), (T("y giras"), C.s_whoosh(), 0.35),
         (T("la velocidad baja") - 0.3, C.s_tick(), 0.35), (T("veintidós") - 0.35, C.s_coin(), 0.35), (T("pero para tocar"), C.s_whoosh(1.0), 0.4),
         (T("a unos tres") - 0.3, C.s_bleep(880), 0.25), (T("tiras de las dos") + 0.4, C.s_clank(), 0.45), (T("el ala se"), C.s_whoosh(), 0.4),
         (T("aterrizas") + 0.1, C.s_thud(), 0.6), (T("aterrizas") + 0.4, C.s_win(), 0.4), (T("sígueme"), C.s_whoosh(), 0.4)]
    return E
