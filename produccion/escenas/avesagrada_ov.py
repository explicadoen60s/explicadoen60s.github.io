# Capa 2D de «¿Qué profundidad tiene el muro que protege la Sagrada Familia del AVE?» (Lo que esconde tu ciudad)
# Pastillas previstas (motion → fotografía), en el tercio de arriba y apartadas del eje de la pieza:
#  6 km sobre el túnel (14,9-17 s) · 1,5 m sobre el primer pilote (30,1-32,5 s) · 240 m sobre la fila de pilotes (35,4-38,8 s)
#  · 13 pisos sobre el edificio boca abajo (42-45 s) · 12 m sobre la tuneladora (50,3-52 s). Callouts: SANTS / SAGRERA en los
#  extremos del túnel y OCTUBRE 2010. La tarjeta del juego (40 m) va arriba y se encoge a la esquina de arriba a la izquierda.
from _ovbase import *
from marcas import cargar
T, DUR = cargar("avesagrada")
SUB_ESTILO = "centro"
SUB_Y = 0.50
KEYWORDS = {"tuneladora", "barcelona", "sagrada", "familia", "profundidad", "muro", "ave", "ciudad", "tierra", "sants", "sagrera",
            "seis", "kilómetros", "túnel", "calle", "mallorca", "templo", "suelo", "piedra", "agujeros", "metro", "medio", "ancho",
            "hormigón", "acero", "pilotes", "pantalla", "doscientos", "cuarenta", "metros", "edificio", "trece", "pisos", "abajo",
            "doce", "diámetro", "octubre", "fachada", "sensores", "milímetro", "daño", "trenes"}

def pastilla(C, ctx, t, v, u, a, b, A, key, dx=0, dy=-150, desde=0, dec=0, dur=0.9, size=66):
    x, y = A(key); C.pastilla(ctx, t, v, u, a, b, clampx(x + dx, 330), clampy(y + dy, 430, 640), desde=desde, dec=dec, dur=dur, size=size)

def overlay(ctx, t, A, C):
    C.cifra_juego(ctx, t, 40, "METROS BAJO TIERRA", T("qué profundidad"), T("y esa pantalla"), T("sígueme"))
    # rótulos (uno cada vez)
    C.rotulo(ctx, t, "TUNELADORA", 0.3, 2.3)
    C.rotulo(ctx, t, "SAGRADA FAMILIA", T("directa") + 0.5, T("qué profundidad") - 0.1)
    C.rotulo(ctx, t, "AVE", T("el ave"), T("el ave") + 1.4)
    C.rotulo(ctx, t, "CALLE MALLORCA", T("la calle"), T("justo al lado") + 0.6)
    C.rotulo(ctx, t, "MURO", T("un muro"), T("haces agujeros") - 0.1)
    C.rotulo(ctx, t, "PILOTES", T("son los"), T("juntos") + 0.4)
    C.rotulo(ctx, t, "PANTALLA", T("una pantalla"), T("una pantalla") + 1.5)
    C.rotulo(ctx, t, "SENSORES", T("los sensores"), T("los sensores") + 1.6)
    # cifras
    pastilla(C, ctx, t, 6, "km de túnel", T("casi seis") - 0.1, T("pero el camino"), A, "tunel", dx=180, dur=1.0)
    pastilla(C, ctx, t, 1.5, "m de ancho", T("cada uno"), T("los rellenas"), A, "pilote", dx=150, dec=1, dur=0.9)
    pastilla(C, ctx, t, 240, "m de largo", T("juntos"), T("y esa pantalla"), A, "fila", dx=120, dur=1.5)
    pastilla(C, ctx, t, 13, "pisos", T("como un edificio"), T("así", 2), A, "edif_top", dx=170, dy=-120, dur=1.0)
    pastilla(C, ctx, t, 12, "m de diámetro", T("de doce") - 0.1, T("en octubre"), A, "rueda", dx=150, dur=0.8)
    # extremos del túnel y fecha
    for key, txt in (("sants", "SANTS"), ("sagrera", "SAGRERA")):
        p = win(t, T("de la estación") + (0.0 if key == "sants" else 1.2), T("casi seis"))
        if p: x, y = A(key); C.callout(ctx, txt, clampx(x, 300), clampy(y - 120, 430, 900), p, size=56)
    p = win(t, T("en octubre"), T("los sensores"))
    if p: x, y = A("templo"); C.callout(ctx, "OCTUBRE 2010", clampx(x, 320), clampy(y - 200, 430, 640), p, size=60)
    # golpes y clics
    x, y = A("pilote"); C.chispa(ctx, t, x, y, T("haces agujeros") + 0.2, r=60); C.chispa(ctx, t, x, y, T("los rellenas") + 0.3, r=60)
    x, y = A("muro")
    for k in range(3): C.chispa(ctx, t, x, y, T("empuja el muro") + 0.25 * k, r=70)
    x, y = A("templo"); C.chispa(ctx, t, x, y, T("ningún"), r=90, col=(0.4, 1.0, 0.5))
    x, y = A("sensores")
    for k in range(3): C.chispa(ctx, t, x, y, T("cada milímetro") + 0.6 * k, r=50, col=(0.4, 1.0, 0.5))

def sfx_events(C):
    E = [(0.0, C.s_whoosh(), 0.35), (0.05, C.s_buzz(2.4), 0.15), (T("directa"), C.s_whoosh(0.7), 0.4),
         (T("el ave"), C.s_whoosh(), 0.4), (T("el ave") + 0.4, C.s_buzz(1.4), 0.15), (T("de la estación"), C.s_pop(), 0.4),
         (T("de la estación") + 1.2, C.s_pop(), 0.4), (T("casi seis") - 0.3, C.s_tick(), 0.4), (T("pero el camino"), C.s_whoosh(), 0.35),
         (T("justo al lado"), C.s_bleep(480), 0.25), (T("si el suelo"), C.s_thud(), 0.5), (T("la piedra") + 0.2, C.s_fail(), 0.4),
         (T("así que"), C.s_whoosh(), 0.35), (T("un muro"), C.s_thud(), 0.45), (T("haces agujeros") + 0.2, C.s_clank(), 0.4),
         (T("uno pegado"), C.s_buzz(1.4), 0.15), (T("cada uno") - 0.3, C.s_tick(), 0.4), (T("los rellenas") + 0.3, C.s_clank(), 0.45),
         (T("son los"), C.s_pop(), 0.4), (T("juntos") - 0.3, C.s_coin(), 0.4), (T("como un edificio"), C.s_whoosh(), 0.35),
         (T("pero hacia"), C.s_thud(), 0.4), (T("si la tierra"), C.s_buzz(1.0), 0.15), (T("empuja el muro"), C.s_thud(), 0.5),
         (T("y no el templo"), C.s_win(), 0.35), (T("después llega"), C.s_whoosh(), 0.4), (T("de doce") - 0.3, C.s_tick(), 0.4),
         (T("en octubre"), C.s_pop(), 0.4), (T("los sensores"), C.s_bleep(880), 0.25), (T("cada milímetro"), C.s_bleep(990), 0.2),
         (T("y el resultado"), C.s_whoosh(), 0.35), (T("ningún"), C.s_win(), 0.45), (T("hoy los"), C.s_whoosh(0.8), 0.4),
         (T("dime en"), C.s_bleep(620), 0.25), (T("y si quieres"), C.s_whoosh(), 0.3), (T("lo más pedido"), C.s_pop(), 0.35),
         (T("sígueme"), C.s_whoosh(), 0.4)]
    E += C.sfx_cifra(T("qué profundidad"), T("y esa pantalla"))
    return E
