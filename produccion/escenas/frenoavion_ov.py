# Capa 2D de «Así frena un avión de 60 toneladas» (Avión, parte 2). Sin juego de la cifra (guion anterior al 12-nov).
# Pastillas previstas (motion → fotografía), siempre encima de su pieza y en la mitad de arriba:
#  velocidad sobre la rueda o el avión (250 → 0 km/h, baja en cada fase) · 60 t sobre el avión (0 → 60)
#  −40 % sobre la balanza · temperatura sobre la pila de discos (20 → 1.000 °C) · minutos sobre la rueda (0 → 30 min)
#  apretones del ABS sobre la pila (cuenta cada apretón) · ACERO / CARBONO junto a los platos de la balanza.
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("frenoavion")
SUB_ESTILO = "centro"
SUB_Y = 0.50
KEYWORDS = {"avión", "pista", "doscientos", "cincuenta", "kilómetros", "hora", "segundos", "sesenta", "toneladas", "frenos",
            "placas", "alas", "sustentación", "peso", "ruedas", "rueda", "motores", "motor", "compuertas", "aire", "revés", "coche",
            "discos", "carbono", "giran", "quietos", "aprietan", "cuarenta", "ciento", "acero", "calor", "mil", "grados", "rojo",
            "temperatura", "media", "bloquea", "ordenador", "milésimas", "freno", "abs", "empujón"}

def pastilla(C, ctx, t, v, u, a, b, A, key, dy=-130, desde=None, dec=0, dur=0.8, size=66):
    if t < a or t > b: return
    x, y = A(key); C.pastilla(ctx, t, v, u, a, b, clampx(x, 300), clampy(y + dy, 430, int(H * 0.40)), desde=desde, dec=dec, dur=dur, size=size)

def _keyed(t, ks):
    if t <= ks[0][0]: return ks[0][1]
    for (a, va), (b, vb) in zip(ks, ks[1:]):
        if a <= t <= b:
            u = (t - a) / (b - a); u = u * u * (3 - 2 * u); return va + (vb - va) * u
    return ks[-1][1]

def kmh(t):
    return _keyed(t, [(0, 250), (12.6, 250), (18.5, 218), (22.5, 205), (28.0, 150), (36.6, 132), (39.5, 85), (55.0, 40), (65.5, 14), (68.6, 0.0)])

def overlay(ctx, t, A, C):
    # rótulos de pieza (uno cada vez)
    C.rotulo(ctx, t, "AEROFRENOS", T("se levantan"), T("se levantan") + 1.7)
    C.rotulo(ctx, t, "INVERSOR DE EMPUJE", T("se abren"), T("se abren") + 1.8)
    C.rotulo(ctx, t, "DISCOS DE CARBONO", T("discos"), T("discos") + 1.8)
    C.rotulo(ctx, t, "ROTORES", T("unos giran"), T("unos giran") + 1.1)
    C.rotulo(ctx, t, "ESTÁTORES", T("otros están"), T("otros están") + 1.0)
    C.rotulo(ctx, t, "PISTONES", T("se aprietan"), T("se aprietan") + 1.3)
    C.rotulo(ctx, t, "ANTIBLOQUEO", T("un ordenador"), T("un ordenador") + 1.8)
    C.rotulo(ctx, t, "ABS", T("como el abs") + 0.3, T("como el abs") + 1.5)
    # velocidad: 250 km/h al tocar pista y luego baja en cada fase (solo en los planos del avión)
    for a, b, key in ((0.15, T("y tiene"), "rueda"), (T("y tiene"), T("cómo frena"), "avion"), (T("todo el peso"), T("luego"), "avion"),
                      (T("el motor sigue"), T("y por último"), "motor"), (T("por eso no"), T("sígueme") - 0.1, "avion")):
        pastilla(C, ctx, t, kmh(t), "km/h", a, b, A, key, desde=0 if a < 1 else None, dur=0.9)
    # 60 toneladas
    pastilla(C, ctx, t, 60, "toneladas", T("algo de"), T("lo primero"), A, "avion", desde=0, dur=1.2)
    # carbono: 40 % menos que el acero
    pastilla(C, ctx, t, -40, "% de peso", T("cuarenta") - 0.2, T("y aguanta"), A, "bal", dy=-150, desde=0, dur=1.2)
    p = win(t, T("el carbono pesa") + 0.4, T("y aguanta"))
    if p:
        x, y = A("bal")
        C.callout(ctx, "ACERO", clampx(x - 230, 220), clampy(y + 200, 430, int(H * 0.42)), p, size=48)
        C.callout(ctx, "CARBONO", clampx(x + 230, 260), clampy(y + 90, 430, int(H * 0.42)), p, size=48)
    # temperatura de los discos
    pastilla(C, ctx, t, 1000, "°C", T("pueden pasar"), T("y el calor"), A, "pila", dy=-200, desde=20, dur=1.6)
    pastilla(C, ctx, t, 30, "min", T("después de"), T("y si una"), A, "rg", dy=-120, desde=0, dur=3.8)
    # ABS: cuenta los apretones
    if T("suelta") <= t <= T("por eso no"):
        n = 0
        if t > T("vuelve a"): n = 1
        if t > T("muchas veces"): n = 1 + int((t - T("muchas veces")) * 3.0 + 0.25)
        n = min(n, 1 + int((T("como el abs", fin=True) + 0.3 - T("muchas veces")) * 3.0 + 0.25))
        if n: pastilla(C, ctx, t, n, "apretones", T("vuelve a"), T("por eso no"), A, "pila", dy=-200, dur=0.01)
    # rueda bloqueada
    p = win(t, T("bloquea") - 0.1, T("un ordenador"))
    if p:
        x, y = A("marca"); C.callout(ctx, "BLOQUEADA", clampx(x, 300), clampy(y - 170, 430, int(H * 0.40)), p, size=56)
    # clics y golpes
    x, y = A("rueda"); C.chispa(ctx, t, x, y + 60, 0.85, r=70); C.chispa(ctx, t, x, y + 60, T("agarran") , r=60)
    x, y = A("pila")
    C.chispa(ctx, t, x, y + 80, T("se aprietan") + 0.2, r=80)
    C.chispa(ctx, t, x, y + 80, T("vuelve a") + 0.15, r=70)
    if T("muchas veces") < t < T("como el abs", fin=True) + 0.3:
        k = (t - T("muchas veces")) * 3.0
        C.chispa(ctx, t, x, y + 80, T("muchas veces") + math.floor(k) / 3.0 + 0.08, r=60)
    x, y = A("motor"); C.chispa(ctx, t, x, y + 40, T("compuertas") , r=60)
    x, y = A("ala"); C.chispa(ctx, t, x, y + 40, T("se levantan") + 0.4, r=60)
    x, y = A("rueda"); C.chispa(ctx, t, x, y + 60, T("sígueme") + 0.85, r=70)

def sfx_events(C):
    t0 = T("muchas veces"); t1 = T("como el abs", fin=True) + 0.3
    E = [(0.0, C.s_whoosh(), 0.4), (0.05, C.s_buzz(2.0), 0.15), (0.85, C.s_thud(), 0.55), (T("y tiene"), C.s_whoosh(), 0.35),
         (T("cómo frena"), C.s_whoosh(), 0.35), (T("algo de") - 0.3, C.s_tick(), 0.35), (T("vamos a"), C.s_whoosh(), 0.35),
         (T("lo primero"), C.s_pop(), 0.35), (T("se levantan"), C.s_whoosh(), 0.3), (T("se levantan") + 0.4, C.s_clank(), 0.45),
         (T("rompen"), C.s_fail(), 0.35), (T("todo el peso"), C.s_whoosh(), 0.3), (T("cae sobre"), C.s_thud(), 0.5),
         (T("agarran"), C.s_clank(), 0.4), (T("luego"), C.s_whoosh(), 0.35), (T("compuertas"), C.s_clank(), 0.45),
         (T("desvían"), C.s_buzz(1.6), 0.18), (T("el motor sigue"), C.s_whoosh(), 0.3), (T("al revés"), C.s_bleep(420), 0.25),
         (T("y por último"), C.s_whoosh(), 0.35), (T("pero no son"), C.s_whoosh(), 0.3), (T("dentro de"), C.s_whoosh(0.7), 0.4),
         (T("discos"), C.s_pop(), 0.4), (T("unos giran"), C.s_bleep(600), 0.22), (T("otros están"), C.s_bleep(400), 0.22),
         (T("se aprietan") + 0.2, C.s_clank(), 0.5), (T("y aquí viene"), C.s_whoosh(), 0.35), (T("el carbono pesa"), C.s_thud(), 0.45),
         (T("cuarenta") - 0.4, C.s_coin(), 0.4), (T("y aguanta"), C.s_whoosh(), 0.3), (T("en un despegue"), C.s_whoosh(), 0.35),
         (T("pueden pasar") - 0.3, C.s_buzz(1.2), 0.2), (T("se ponen"), C.s_win(), 0.4), (T("y el calor"), C.s_whoosh(), 0.3),
         (T("después de"), C.s_tick(), 0.35), (T("hasta media") - 0.3, C.s_coin(), 0.4), (T("y si una"), C.s_whoosh(), 0.35),
         (T("bloquea"), C.s_fail(), 0.45), (T("un ordenador"), C.s_pop(), 0.4), (T("milésimas"), C.s_bleep(880), 0.22),
         (T("suelta"), C.s_whoosh(0.4), 0.3), (T("vuelve a") + 0.15, C.s_clank(), 0.4), (T("como el abs"), C.s_whoosh(), 0.3),
         (T("por eso no"), C.s_whoosh(), 0.35), (T("solo ese"), C.s_pop(), 0.35), (T("empujón"), C.s_thud(), 0.35),
         (T("sígueme"), C.s_whoosh(), 0.4), (T("sígueme") + 0.85, C.s_thud(), 0.45)]
    k = 0
    while t0 + k / 3.0 + 0.08 < t1:
        if k: E.append((t0 + k / 3.0 + 0.08, C.s_tick(), 0.3))
        k += 1
    return E
