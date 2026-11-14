# «Las aspas de tu aspiradora no chupan» (formato A, error común)
# Salón de maqueta (1 unidad = 1 m) sobre una isla cortada (tarima, hormigón, tierra) con sofá, alfombra, planta y ventana.
# Aspiradora de trineo en el suelo, cortada por la mitad (se ve desde -Y, cantos crema): delante el depósito con el polvo,
# en medio el filtro plisado y detrás el motor con el ventilador (aspas que giran) y la rejilla de salida.
# La manguera y el tubo también van en corte hasta la boquilla sobre la alfombra. Bolitas azules = aire, grises = polvo.
# Flechas rojas: el aire de la habitación empuja hacia la boquilla; el ventilador echa aire por detrás.
# Planos (fotografía → motion; esquina libre arriba-izquierda, que ocupa el mini del juego desde 5,3 s):
#  0,0 aspas girando en primer plano con flechas de salida · 2,7 aspiradora entera · 5,3 salón · 7,2 ventilador y motor
#  11,2 30.000 rpm · 14,2 aire que sale por detrás · 17,1 dentro quedan pocas bolitas · 19,6 menos presión
#  21,7 la habitación empuja (flechas grandes) · 24,5 polvo que entra por la boquilla · 27,5 nada tira · 30,1 revelación
#  36,1 filtro · 40,3 filtro de 3 años (gris) · 44,9 motor · 47,4 depósito · 49 a la mitad · 52,2 menos aire
#  55,9 salón · 58,4 vacía el depósito y lava el filtro · 61,2 cierre · 68,3 vuelta a las aspas.
import bpy, math, sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from modelos import *
from maqueta import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("aspiradora")
CUERPO = (0.30, 0.55, 0.88); GRIS = (0.62, 0.64, 0.68); OSCURO = (0.22, 0.23, 0.26); AIRE = (0.35, 0.70, 1.0)
POLVO = (0.55, 0.52, 0.48); FILTRO = (0.97, 0.97, 0.95); SUCIO = (0.45, 0.42, 0.38); DEP = (0.72, 0.88, 0.96)
ZA = 0.17; RA = 0.15                                        # eje y radio del cuerpo
XF = 0.02                                                    # filtro
CAMINO = poly([(1.02, -0.02, 0.025), (0.95, -0.02, 0.04), (0.82, -0.02, 0.62), (0.62, -0.02, 0.78), (0.45, -0.02, 0.62),
               (0.36, -0.02, 0.32), (0.30, -0.02, ZA), (0.12, -0.02, ZA), (XF, -0.02, ZA), (-0.12, -0.02, ZA),
               (-0.3, -0.02, ZA), (-0.6, -0.02, ZA + 0.05)])
N_AIRE, N_POLVO = 44, 26

def back(x):
    x = max(0.0, min(1.0, x)); c = 1.70158; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

def sucio(t):
    """filtro sucio (0..1)"""
    return seg(t, T("si lleva meses"), T("pasa peor", fin=True)) * (1 - seg(t, T("y lava"), T("el filtro", 2, fin=True)))

def lleno(t):
    """nivel del depósito (0..0,5)"""
    base = 0.12 * seg(t, T("ese aire pesa"), T("la empujan", fin=True))
    mitad = 0.5 * seg(t, T("cuando llega"), T("la mitad", fin=True))
    return max(base, mitad) * (1 - seg(t, T("vacía"), T("ahora mismo", fin=True)))

def caudal(t):
    """1 = aire pasando normal; baja con el filtro sucio y el depósito lleno"""
    return 1.0 - 0.14 * sucio(t) - 0.6 * max(0.0, lleno(t) - 0.12) * (t > T("con el depósito"))

def rpm(t):
    return 1.0

def build():
    sc, cam = scene_setup(world=PAL["cielo"], shadow=0.25, light_rot=60); entorno_claro(sc)
    S = {"cam": cam}
    nubes(9, (0, 6, 3.6), 6, 1.0, 1.0, s=1.1, seed=2)
    isla(3.4, 2.4, (0.2, 0.5, 0.0), capas=[(PAL["madera"], 0.06), (PAL["hormigon"], 0.16), (PAL["tierra"], 0.3), (PAL["tierra2"], 0.34)])
    for k in range(10): box((0.008, 2.4, 0.004), (-1.4 + k * 0.34, 0.5, 0.002), (0.74, 0.52, 0.30))
    box((3.4, 0.1, 2.2), (0.2, 1.65, 1.1), PAL["pared"]); box((3.4, 0.102, 0.03), (0.2, 1.65, 2.185), PAL["corte"])
    caja((0.8, 0.06, 0.7), (-0.6, 1.59, 1.35), (0.62, 0.82, 0.95), r=0.03)
    caja((0.86, 0.08, 0.05), (-0.6, 1.58, 1.0), (0.97, 0.97, 0.97), r=0.01)
    sofa((-0.7, 1.2, 0.0), 1.0, color=(0.95, 0.55, 0.40))
    planta((1.6, 1.3, 0.0), 1.5)
    S["alfombra"] = alfombrilla((0.95, 0.25, 0.005), 1.0, 0.8, color=(0.55, 0.75, 0.70))
    mesita((1.55, -0.3, 0.0), 0.9)
    # cuerpo de la aspiradora cortado (mitad trasera hueca) con tapas
    medio_tubo([(-0.27, 0, ZA), (0.27, 0, ZA)], RA, 0.012, CUERPO, eje=(0, 1, 0))
    for x, c in ((-0.275, OSCURO), (0.275, CUERPO)):
        m = medio_tubo([(x - 0.006, 0, ZA), (x + 0.006, 0, ZA)], 0.0, RA + 0.012, c, eje=(0, 1, 0))
    for x in (-0.2, 0.2):
        for y in (-0.12, 0.12): cilindro(0.04, 0.03, (x, y, 0.04), OSCURO, rot=(math.pi / 2, 0, 0), r=0.008)
    caja((0.12, 0.03, 0.04), (0.0, 0.0, ZA + RA + 0.03), OSCURO, r=0.012)          # asa
    # rejilla de salida (detrás)
    for k in range(5): caja((0.012, 0.13, 0.012), (-0.282, 0.06, ZA - 0.1 + 0.05 * k), (0.4, 0.42, 0.45), r=0.003)
    # depósito transparente (azul claro) y el polvo
    medio_tubo([(0.08, 0, ZA), (0.25, 0, ZA)], RA - 0.02, 0.006, DEP, eje=(0, 1, 0))
    S["polvo_dep"] = caja((0.16, 0.12, 1.0), LEJOS, POLVO, r=0.01, unique=True)
    # filtro plisado (media luna de pliegues)
    S["filtro"] = []
    for k in range(9):
        z = ZA - 0.12 + k * 0.03
        o = caja((0.035, 0.12, 0.022), (XF + (0.01 if k % 2 else -0.01), 0.06, z), FILTRO, r=0.004, unique=True)
        o.rotation_euler = (0, 0.5 if k % 2 else -0.5, 0); S["filtro"].append(o)
    caja((0.05, 0.13, 0.02), (XF, 0.06, ZA - 0.14), (0.85, 0.85, 0.85), r=0.005); caja((0.05, 0.13, 0.02), (XF, 0.06, ZA + 0.14), (0.85, 0.85, 0.85), r=0.005)
    # motor y ventilador
    cilindro(0.07, 0.12, (-0.2, 0.04, ZA), (0.80, 0.55, 0.25), rot=(0, math.pi / 2, 0), r=0.01)        # motor (cobre)
    for k in range(6): caja((0.1, 0.004, 0.012), (-0.2, 0.04 + 0.07 * math.cos(k), ZA + 0.07 * math.sin(k)), (0.55, 0.35, 0.15), r=0.002)
    cilindro(0.008, 0.08, (-0.11, 0.04, ZA), GRIS, rot=(0, math.pi / 2, 0))
    S["fan"] = fan = empty((-0.08, 0.04, ZA)); fan.rotation_mode = 'XYZ'
    cilindro(0.025, 0.03, (0, 0, 0), OSCURO, fan, rot=(0, math.pi / 2, 0), r=0.006)
    for k in range(7):
        a = k * math.tau / 7
        b = caja((0.02, 0.012, 0.1), (0, 0.06 * math.cos(a), 0.06 * math.sin(a)), PAL["rojo"] if k == 0 else (0.95, 0.80, 0.25), fan, r=0.004)
        b.rotation_euler = (a - math.pi / 2, 0.45, 0)
    # manguera, tubo y boquilla (en corte)
    medio_tubo([(0.28, 0, ZA), (0.36, 0, 0.32), (0.45, 0, 0.62), (0.62, 0, 0.78), (0.82, 0, 0.62)], 0.035, 0.008, (0.40, 0.42, 0.46), eje=(0, 1, 0))
    medio_tubo([(0.82, 0, 0.62), (0.95, 0, 0.06)], 0.025, 0.006, (0.75, 0.77, 0.80), eje=(0, 1, 0))
    caja((0.14, 0.26, 0.04), (1.0, 0.04, 0.03), OSCURO, r=0.015)                      # boquilla
    caja((0.03, 0.06, 0.06), (0.83, 0.04, 0.62), OSCURO, r=0.01)                      # empuñadura
    # aire (azul) y polvo (gris)
    S["aire"] = [sph(0.011, LEJOS, AIRE, seg=10) for _ in range(N_AIRE)]
    S["polvo"] = [bola(0.009, LEJOS, POLVO, sub=1) for _ in range(N_POLVO)]
    S["fuera"] = [sph(0.013, LEJOS, AIRE, seg=10) for _ in range(30)]                  # aire de la habitación
    S["fsal"] = [flecha3d(LEJOS, (-1, 0, 0.15), 0.18, 0.012) for _ in range(3)]
    S["fhab"] = [flecha3d(LEJOS, (0, 1, -0.2), 0.2, 0.013) for _ in range(3)]
    S["fpolvo"] = flecha3d(LEJOS, (-1, 0, 0), 0.22, 0.016)
    S["mano"] = empty(LEJOS)
    caja((0.06, 0.06, 0.08), (0, 0, 0), (0.96, 0.78, 0.64), S["mano"], r=0.02)
    cilindro(0.03, 0.3, (0.0, -0.1, 0.12), (0.4, 0.6, 0.9), S["mano"], rot=(0.8, 0, 0), r=0.01)
    dyn = [cam, S["alfombra"], S["polvo_dep"], S["filtro"], S["fan"], S["aire"], S["polvo"], S["fuera"], S["fsal"], S["fhab"], S["fpolvo"], S["mano"]]
    join_static(dyn)
    return sc, S

def pose(t, S):
    q = caudal(t); r = rpm(t)
    S["fan"].rotation_euler = (t * 38.0 * r + (0 if r else 0), 0, 0)
    for o in S["filtro"]: set_color(o, tuple(mix(a, b, sucio(t)) for a, b in zip(FILTRO, SUCIO)))
    lv = lleno(t)
    if lv > 0.005:
        h = 0.26 * lv; S["polvo_dep"].location = (0.165, 0.05, ZA - 0.12 + h / 2); S["polvo_dep"].scale = (1, 1, h)
    else: S["polvo_dep"].location = LEJOS
    # aire dentro: recorre el camino; «menos aire dentro» = menos bolitas dentro del cuerpo
    L = largo(CAMINO); poco = seg(t, T("pero así"), T("que antes", fin=True))
    rnd = random.Random(4)
    for k, b in enumerate(S["aire"]):
        ph = rnd.random(); sp = rnd.uniform(0.85, 1.15)
        s = ((t * 0.55 * q * sp + ph) % 1.0) * L
        p = at(CAMINO, s)
        dentro = -0.27 < p.x < 0.27 and p.z < 0.35
        if dentro and poco > 0.01 and k % 3 != 0 and t < T("así que no compres"): b.location = LEJOS; continue
        b.location = p + Vector((0, 0.03 * math.sin(k * 1.7), 0.02 * math.cos(k * 2.3)))
    # polvo: entra por la boquilla (empujado) y cae al depósito
    empuja = seg(t, T("y empuja el polvo") - 0.3, T("boquilla", fin=True))
    rp = random.Random(9)
    for k, b in enumerate(S["polvo"]):
        if empuja < 0.01: b.location = LEJOS; continue
        ph = rp.random(); u = (t * 0.32 * q + ph) % 1.0
        s = u * at_s(0.12)
        p = at(CAMINO, s)
        if s > at_s(0.12) * 0.92: p = Vector((0.12 + 0.1 * rp.random(), -0.01, ZA - 0.11 + 0.24 * lleno(t) * 2 + 0.01))
        b.location = p + Vector((0, 0.02 * math.sin(k), 0))
    # aire de la habitación: empuja hacia la boquilla
    hab = win01(t, T("así que el aire") - 0.2, T("y aquí viene"), 0.4, 0.4) + 0.6 * win01(t, T("vacía") - 0.2, T("te has acercado"), 0.3, 0.3)
    rf = random.Random(6)
    for k, b in enumerate(S["fuera"]):
        if hab < 0.01: b.location = LEJOS; continue
        ang = rf.uniform(-1.2, 1.2); d0 = rf.uniform(0.35, 0.7); u = (t * 0.6 * q + rf.random()) % 1.0
        dd = d0 * (1 - u) + 0.04
        b.location = (1.0 + dd * math.sin(ang), 0.04 - dd * math.cos(ang) * 0.9, 0.03 + 0.25 * (1 - u) * rf.random()); b.scale = (hab,) * 3
    for k, f in enumerate(S["fhab"]):
        if hab > 0.01:
            a = (-0.6, 0.0, 0.6)[k]; d = 0.42 - 0.08 * ((t * 1.5 + k * 0.3) % 1.0)
            f.location = (1.0 + d * math.sin(a), 0.04 - d * math.cos(a), 0.08); f.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(Vector((-math.sin(a), math.cos(a), -0.15)))
            f.scale = (hab * (0.7 + 0.5 * seg(t, T("ese aire pesa"), T("la empujan", fin=True))),) * 3
        else: f.location = LEJOS
    # flechas de salida (detrás): crecen con el caudal
    sal = 1.0 if t > 0 else 0
    for k, f in enumerate(S["fsal"]):
        f.location = (-0.3 - 0.06 * ((t * 2 + k * 0.33) % 1.0), 0.05, ZA - 0.07 + 0.07 * k); f.scale = (max(0.4 + 0.6 * q * r, 0.05) * sal,) * 3
    fp = win01(t, T("nada tira") - 0.2, T("y aquí viene"), 0.3, 0.3)
    S["fpolvo"].location = (1.18, 0.04, 0.05) if fp > 0.01 else LEJOS; S["fpolvo"].scale = (fp + 0.01,) * 3
    # mano que vacía el depósito / sujeta la empuñadura
    mn = win01(t, T("vacía") - 0.3, T("te has acercado") - 0.2, 0.3, 0.3)
    S["mano"].location = (0.83, -0.05, 0.66) if mn > 0.01 else LEJOS
    S["alfombra"].location = S["alfombra"].location
    apply_cam(S["cam"], *cam_lin(t, CAM(), drift=0.004))

_AT = {}
def at_s(x):
    """longitud del camino hasta la x indicada (primer cruce, ya dentro del cuerpo)"""
    if x not in _AT:
        L = largo(CAMINO); s = 0.0
        while s < L and not (at(CAMINO, s).x < x and at(CAMINO, s).z < 0.25): s += 0.005
        _AT[x] = s
    return _AT[x]

FAN = (-0.1, 0.0, ZA); TODO = (0.35, 0.0, 0.3); FIL = (XF, 0.0, ZA); DEPO = (0.16, 0.0, ZA); BOQ = (1.0, 0.0, 0.05)

def CAM():
    k = Claves(); add = k.add
    ini = V(FAN, (0.02, -0.42, 0.06), 40)
    add(0.0, V(FAN, (0.0, -0.36, 0.04), 42)); add(1.6, ini)
    add(T("a cuántos") - 0.1, V(TODO, (-0.3, -1.6, 0.45), 32))
    add(T("escribe"), V((0.4, 0.4, 0.5), (-0.8, -2.8, 0.9), 28))
    add(T("llevas años"), V(TODO, (0.5, -1.4, 0.35), 32))
    add(T("dentro un"), V(FAN, (-0.240, -0.800, 0.192), 38))
    add(T("gira hasta"), V(FAN, (0.080, -0.512, 0.048), 44))
    add(T("cada vuelta"), V((-0.2, 0.0, ZA), (-1.024, -1.280, 0.256), 36))
    add(T("pero así"), V((0.05, 0.0, ZA), (0.000, -1.920, 0.461), 34))
    add(T("menos aire significa"), V((0.05, 0.0, ZA), (0.768, -1.536, 0.307), 36))
    add(T("así que el aire"), V(BOQ, (-0.6, -1.0, 0.45), 32))
    add(T("ese aire pesa"), V(BOQ, (0.15, -1.0, 0.35), 34))
    add(T("y empuja el polvo") + 0.4, V((0.85, 0.0, 0.4), (-0.3, -1.0, 0.1), 34))
    add(T("nada tira"), V(BOQ, (0.5, -0.9, 0.3), 34))
    add(T("y aquí viene"), V(TODO, (-0.2, -1.5, 0.35), 32))
    add(T("dentro baja"), V((0.05, 0.0, ZA), (0.512, -1.920, 0.384), 34))
    add(T("frente a"), V(BOQ, (-0.3, -0.9, 0.3), 34))
    add(T("pero ahora"), V(FIL, (-0.080, -0.608, 0.096), 42))
    add(T("en una prueba"), V(FIL, (0.192, -0.544, 0.064), 44))
    add(T("tu aspiradora rinde"), V(FAN, (-0.192, -0.640, 0.160), 40))
    add(T("con el depósito"), V(DEPO, (0.160, -0.672, 0.128), 40))
    add(T("el aire ya"), V(DEPO, (-0.192, -0.640, 0.080), 42))
    add(T("más polvo"), V(TODO, (0.2, -1.4, 0.3), 32))
    add(T("así que no compres"), V((0.4, 0.4, 0.6), (-0.9, -2.8, 1.0), 28))
    add(T("vacía"), V(DEPO, (0.320, -0.800, 0.240), 38))
    add(T("y lava"), V(FIL, (-0.128, -0.608, 0.096), 42))
    add(T("te has acercado"), V((0.4, 0.4, 0.5), (-0.8, -2.8, 0.9), 28))
    add(T("y si quieres"), V(BOQ, (-0.4, -1.0, 0.4), 32))
    add(T("lo más pedido"), V(TODO, (0.6, -1.5, 0.5), 32))
    add(T("sígueme"), V(TODO, (-0.4, -1.4, 0.3), 32))
    add(T("así que ya sabes") - 0.2, V(FAN, (0.0, -0.36, 0.04), 42))
    add(DUR - 0.8, ini)
    add(DUR + 1, ini)
    return k.k

def anchors(sc, S, t):
    cam = S["cam"]; P = lambda v: proj(sc, cam, v)
    return {"fan": P((-0.08, 0.0, ZA + 0.12)), "fil": P((XF, 0.0, ZA + 0.16)), "dep": P((0.16, 0.0, ZA + 0.16)), "boq": P((1.0, 0.0, 0.12)),
            "salida": P((-0.36, 0.0, ZA + 0.05)), "cuerpo": P((0.0, 0.0, ZA + RA + 0.08)), "hab": P((1.0, -0.3, 0.3))}

if __name__ == "__main__":
    run("aspiradora", build, pose, anchors)
