# Capa 2D de «¿Cuántos kilómetros de tubos llevan el agua a tu grifo en Madrid?» (Lo que esconde tu ciudad)
# Pastillas previstas (motion → fotografía), todas en el tercio de arriba (y ≤ H*0.33) y apartadas del eje del objeto:
#  13 presas sobre la sierra (cuenta de 1 a 13) · 1.000 millones de m³ sobre el embalse · % de demanda sobre la ciudad (sube a 100)
#  300 depósitos sobre la ciudad · 180.000 m³ sobre el depósito de Bravo Murillo · 7 millones de personas sobre la ciudad.
#  Juego de la cifra: tarjeta grande arriba (H*0.27, encima del grifo y del globo), mini arriba a la izquierda; 17.000 km al revelar.
from _ovbase import *
from marcas import cargar
T, DUR = cargar("canalmadrid")
SUB_ESTILO = "centro"
SUB_Y = 0.50
KEYWORDS = {"grifo", "madrid", "agua", "kilómetros", "tubos", "río", "lozoya", "sierra", "mil", "ochocientos", "cincuenta", "ocho",
            "presas", "trece", "millones", "metros", "cúbicos", "embalse", "planta", "potabilizadora", "filtran", "desinfectan",
            "canales", "tuberías", "depósitos", "trescientos", "bravo", "murillo", "ciento", "ochenta", "diecisiete", "australia",
            "siete", "personas", "calle"}

def pastilla(C, ctx, t, v, u, a, b, A, key, dx=160, dy=-170, desde=0, dec=0, dur=0.9, size=64):
    x, y = A(key); C.pastilla(ctx, t, v, u, a, b, max(600, min(W - 300, x + dx)), clampy(y + dy, 470, 620), desde=desde, dec=dec, dur=dur, size=size)

def overlay(ctx, t, A, C):
    C.cifra_juego(ctx, t, 17000, "KM DE TUBERÍAS", T("cuántos kilómetros"), T("si los pones"), T("sígueme"), dec=0,
                  grande=(W / 2, H * 0.27))
    # rótulos de pieza (uno cada vez)
    C.rotulo(ctx, t, "GRIFO", 0.3, 1.8)
    C.rotulo(ctx, t, "RÍO LOZOYA", T("río lozoya"), T("río lozoya") + 1.6)
    C.rotulo(ctx, t, "PRESA", T("presas"), T("presas") + 1.5)
    C.rotulo(ctx, t, "EMBALSE", T("embalse"), T("embalse") + 1.4)
    C.rotulo(ctx, t, "POTABILIZADORA", T("planta potabilizadora"), T("planta potabilizadora") + 1.6)
    C.rotulo(ctx, t, "CANAL", T("canales"), T("canales") + 1.3)
    C.rotulo(ctx, t, "DEPÓSITO", T("depósitos enterrados"), T("depósitos enterrados") + 1.4)
    C.rotulo(ctx, t, "TUBERÍAS", T("tubos bajo"), T("tubos bajo") + 1.4)
    # año
    p = win(t, T("en mil"), T("la traen") + 1.2)
    if p: x, y = A("sierra"); C.callout(ctx, "AÑO 1858", max(560, min(W - 300, x + 120)), clampy(y - 200, 470, 620), p, size=62)
    # contadores
    pastilla(C, ctx, t, 13, "presas", T("trece") - 0.3, T("pero el agua del"), A, "sierra", desde=1, dur=1.2)
    pastilla(C, ctx, t, 1000, "millones de m³", T("casi mil") - 0.1, T("pero el agua del") + 0.6, A, "lago", dx=-60, dy=-120, dur=1.4)
    pastilla(C, ctx, t, 100, "% de agua pedida", T("todos abren"), T("así que guardas"), A, "ciudad", dx=0, desde=25, dur=1.6)
    pastilla(C, ctx, t, 300, "depósitos", T("trescientos") - 0.2, T("uno de ellos"), A, "ciudad", dx=0, dur=1.2)
    pastilla(C, ctx, t, 180000, "m³", T("guarda ciento") + 0.2, T("baja por"), A, "dep", dx=60, dy=-260, dur=1.6)
    C.pastilla(ctx, t, 7, "millones de personas", T("siete millones") - 0.1, T("te has"), W / 2, H * 0.405, desde=0, dur=1.0, size=60)
    # clics
    x, y = A("grifo"); C.chispa(ctx, t, x, y, 0.3, r=60)
    x, y = A("presa"); C.chispa(ctx, t, x, y - 30, T("construyes") + 1.3, r=70)
    x, y = A("dep"); C.chispa(ctx, t, x, y, T("enterrados", fin=True), r=70)
    x, y = A("aus"); C.chispa(ctx, t, x, y, T("australia", fin=True) - 0.2, r=60)
    x, y = A("grifo"); C.chispa(ctx, t, x, y, T("sígueme") + 0.3, r=60)

def sfx_events(C):
    E = [(0.0, C.s_clank(), 0.35), (0.25, C.s_buzz(2.2), 0.15), (T("y el agua sale"), C.s_pop(), 0.35),
         (T("escribe"), C.s_whoosh(), 0.35), (T("madrid no tiene"), C.s_whoosh(0.7), 0.4), (T("en mil") - 0.3, C.s_bleep(520), 0.25),
         (T("la traen"), C.s_whoosh(), 0.35), (T("río lozoya"), C.s_pop(), 0.35), (T("construyes"), C.s_thud(), 0.5),
         (T("construyes") + 1.3, C.s_clank(), 0.45), (T("hoy son"), C.s_whoosh(), 0.35)]
    E += [(T("hoy son") + 0.1 * k, C.s_pop(), 0.25) for k in range(0, 12, 3)]
    E += [(T("guardan casi") - 0.2, C.s_buzz(1.6), 0.15), (T("pero el agua del"), C.s_fail(), 0.35),
          (T("así que la mandas"), C.s_whoosh(), 0.35), (T("filtran") - 0.25, C.s_bleep(700), 0.25), (T("desinfectan"), C.s_coin(), 0.35),
          (T("luego viaja"), C.s_whoosh(0.8), 0.4), (T("pero en madrid"), C.s_whoosh(), 0.35), (T("todos abren") - 0.2, C.s_tick(), 0.35),
          (T("por la mañana") - 0.2, C.s_bleep(880), 0.25), (T("y a la hora") - 0.1, C.s_bleep(600), 0.25),
          (T("así que guardas"), C.s_thud(), 0.45), (T("enterrados", fin=True), C.s_clank(), 0.4),
          (T("más de trescientos") - 0.3, C.s_whoosh(), 0.35), (T("grandes y"), C.s_pop(), 0.35), (T("uno de ellos"), C.s_whoosh(), 0.35),
          (T("guarda ciento") - 0.3, C.s_buzz(1.8), 0.15), (T("y desde ahí"), C.s_whoosh(), 0.35), (T("tubos bajo"), C.s_tick(), 0.35),
          (T("si los pones") - 0.3, C.s_whoosh(0.7), 0.4), (T("casi la distancia"), C.s_whoosh(), 0.35),
          (T("australia", fin=True) - 0.2, C.s_win(), 0.4), (T("para casi"), C.s_whoosh(), 0.35), (T("personas"), C.s_pop(), 0.35),
          (T("dime en"), C.s_whoosh(), 0.35), (T("y si quieres"), C.s_whoosh(), 0.3), (T("lo más pedido"), C.s_tick(), 0.3),
          (T("sígueme"), C.s_clank(), 0.35), (T("sígueme") + 0.3, C.s_whoosh(), 0.35)]
    E += C.sfx_cifra(T("cuántos kilómetros"), T("si los pones"))
    return E
