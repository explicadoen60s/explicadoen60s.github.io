# Capa 2D de «Tu cinturón… ¿cuánto pesas en un choque?»
# Pastillas (motion → fotografía), tercio de arriba, lado derecho (el mini del juego ocupa arriba-izquierda):
#  0,45 g junto al péndulo (16-19,9) · 30 ms junto al pretensor (28,6-32,5) · 50 km/h sobre el coche (34-35,3)
#  · 5-7 cm junto al carrete con la barra de torsión (40,8-44). La revelación (3.000 kg) la hace la tarjeta del juego, con la
#  flecha roja del cuerpo creciendo a la vez. Errores (44,4-48,2) con callouts cortos; al final ✓ en hombro y cadera.
from _ovbase import *
from marcas import cargar
T, DUR = cargar("cinturon")
SUB_ESTILO = "centro"
SUB_Y = 0.50
KEYWORDS = {"cinturón", "choque", "carrete", "correa", "clava", "péndulo", "bolita", "gancho", "frena", "cero", "coma", "cuarenta",
            "cinco", "gravedad", "diente", "rueda", "pretensor", "pirotécnica", "treinta", "milésimas", "cincuenta", "tres", "mil",
            "kilos", "costillas", "limitador", "siete", "centímetros", "floja", "torcida", "brazo", "abrigo", "holgura", "hombro",
            "cadera", "banda", "plana"}

def pastilla(C, ctx, t, v, u, a, b, A, key, dx=0, dy=-150, desde=0, dec=0, dur=0.9, size=66, lo=560, hi=760):
    x, y = A(key); C.pastilla(ctx, t, v, u, a, b, clampx(x + dx, 360), clampy(y + dy, lo, hi), desde=desde, dec=dec, dur=dur, size=size)

def overlay(ctx, t, A, C):
    juego_completo(C, ctx, t, 3000, "KG EN UN CHOQUE", T("cuánto pesas"), T("tu cuerpo"), T("te has acercado"), T("sígueme"),
                   grande=(C.W / 2, C.H * 0.30))
    # rótulos de pieza
    C.rotulo(ctx, t, "CARRETE", 0.2, 1.4)
    C.rotulo(ctx, t, "PÉNDULO", T("un péndulo"), T("una bolita") - 0.05)
    C.rotulo(ctx, t, "GANCHO", T("sobre un gancho"), T("cuando el coche") - 0.05)
    C.rotulo(ctx, t, "DIENTE", T("un diente"), T("y la correa") - 0.05)
    C.rotulo(ctx, t, "PRETENSOR", T("el pretensor"), T("una carga") - 0.05)
    C.rotulo(ctx, t, "LIMITADOR", T("el limitador"), T("cede") + 0.6)
    # cifras
    pastilla(C, ctx, t, 0.45, "g", T("cero coma") - 0.1, T("así que un diente") - 0.1, A, "pend", dx=120, dy=-220, dec=2, dur=1.4)
    pastilla(C, ctx, t, 30, "milésimas", T("en treinta") - 0.1, T("y aquí viene") - 0.1, A, "pret", dx=240, dy=-260, dur=0.6)
    pastilla(C, ctx, t, 50, "km/h", T("y aquí viene"), T("tu cuerpo") - 0.6, A, "coche", dx=160, dy=-60, dur=1.2)
    pastilla(C, ctx, t, 7, "cm de correa", T("entre cinco") - 0.1, T("y tú la llevas") - 0.1, A, "ret", dx=230, dy=-260, desde=5, dur=1.0)
    # clics
    x, y = A("diente"); C.chispa(ctx, t, x, y, T("se clava") - 0.1, r=70); C.chispa(ctx, t, x, y, T("encaja"), r=70)
    C.chispa(ctx, t, x, y, T("se clava", 2) - 0.1, r=70)
    x, y = A("pret"); C.chispa(ctx, t, x, y, T("tira de ella"), r=90, col=(1, 0.7, 0.3))
    x, y = A("muro"); C.chispa(ctx, t, x, y, T("a cincuenta", fin=True) + 0.15, r=120, col=(1, 0.6, 0.4))
    x, y = A("hombro"); C.chispa(ctx, t, x, y, T("sobre el hombro") + 0.2, r=60, col=(0.4, 1.0, 0.5))
    x, y = A("cadera"); C.chispa(ctx, t, x, y, T("la cadera") + 0.1, r=60, col=(0.4, 1.0, 0.5))

def sfx_events(C):
    E = [(0.0, C.s_whoosh(), 0.5), (0.1, C.s_buzz(1.2), 0.1), (T("tira despacio"), C.s_whoosh(0.7), 0.3),
         (T("la correa sale"), C.s_buzz(0.8), 0.1), (T("se clava") - 0.1, C.s_clank(), 0.5), (T("dentro hay"), C.s_whoosh(), 0.3),
         (T("una bolita"), C.s_pop(), 0.3), (T("cuando el coche"), C.s_whoosh(0.8), 0.35), (T("se inclina"), C.s_bleep(520), 0.25),
         (T("cero coma") - 0.3, C.s_tick(), 0.3), (T("encaja"), C.s_clank(), 0.5), (T("pero si el golpe"), C.s_whoosh(), 0.3),
         (T("el pretensor"), C.s_pop(), 0.3), (T("tira de ella"), C.s_thud(), 0.6), (T("en treinta") - 0.3, C.s_tick(), 0.3),
         (T("y aquí viene"), C.s_whoosh(0.9), 0.4), (T("a cincuenta", fin=True) + 0.05, C.s_thud(), 0.5),
         (T("pero tanta"), C.s_fail(), 0.3), (T("el limitador"), C.s_pop(), 0.3),
         (T("cede"), C.s_buzz(0.9), 0.12), (T("y tú la llevas"), C.s_whoosh(), 0.3), (T("torcida"), C.s_bleep(300), 0.22),
         (T("bajo el brazo"), C.s_bleep(300), 0.22), (T("sobre un abrigo"), C.s_bleep(300), 0.22), (T("esa holgura"), C.s_whoosh(), 0.3),
         (T("quítate"), C.s_pop(), 0.3), (T("sobre el hombro") + 0.2, C.s_win(), 0.35), (T("te has acercado"), C.s_whoosh(), 0.35),
         (T("y si quieres"), C.s_whoosh(), 0.3), (T("lo más pedido"), C.s_pop(), 0.35), (T("sígueme"), C.s_whoosh(), 0.4),
         (T("así que ya sabes"), C.s_whoosh(), 0.35), (T("se clava", 2) - 0.1, C.s_clank(), 0.45)]
    E += C.sfx_cifra(T("cuánto pesas"), T("tu cuerpo"))
    return E
