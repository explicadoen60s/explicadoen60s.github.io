# «¿Qué profundidad tiene el muro que protege la Sagrada Familia del AVE?» (Lo que esconde tu ciudad)
# Maqueta en esquina: la isla ocupa x∈[0,12], y∈[0,12]; cara de corte izquierda (x=0) por el eje del túnel (va a lo largo de Y)
# y cara de corte delantera (y=0) que enseña en sección el túnel, el primer pilote (40 m) y las capas de tierra.
# Escala: 1 unidad = 5 m. Templo genérico de torres aguja (estilizado, más bajo que el real para que quepa en la maqueta).
# Planos (fotografía → motion; esquina libre arriba-izquierda salvo indicación):
#  0,0 rueda de la tuneladora girando en primer plano · 1,4 se abre · 3 maqueta: la máquina va hacia el templo
#  4,9-9 pregunta (plano amplio que deriva) · 9,4 el AVE dentro del túnel · 11,9 Sants–Sagrera a lo largo · 14,9 6 km
#  17,1 calle Mallorca · 19,5 junto al templo · 20,9 tiembla · 22,3 grietas (primer plano) · 23,9 plano amplio · 25,6 bajo tierra
#  27,3 pilotadora perforando · 28,6 agujeros en fila desde arriba · 30,1 1,5 m (primer plano) · 32,5 hormigón y acero en sección
#  34,2 pilotes · 35,4 pantalla de 240 m a lo largo · 38,8 profundidad (40 m) en la cara delantera · 42 edificio de 13 pisos boca abajo
#  45 flechas: la tierra empuja el muro · 47,5 el templo intacto · 48,6 llega la tuneladora · 50,3 12 m · 52 junto a la fachada
#  54,7 sensores · 58 resultado · 60 el AVE pasa · 62-70 cierre · 70,7 vuelta al primer plano de la rueda.
import bpy, math, sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from modelos import *
from maqueta import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("avesagrada")
ZC = -4.0; RB = 1.22; RI = 1.12; ZD = ZC - 0.6; RS = 1.19; LSH = 1.4 * RS
XP = 2.6; RP = 0.15; NP = 40; PROF = 8.0          # pilotes: x, radio (1,5 m de ancho), número, profundidad (40 m)
PIEDRA = (0.89, 0.81, 0.64); PIEDRA2 = (0.80, 0.71, 0.55); HORM = (0.74, 0.74, 0.72); HUECO = (0.22, 0.17, 0.14)

def back(x):
    x = max(0.0, min(1.0, x)); c = 1.70158; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

def fase(t):
    """'abre' (máquina del principio), 'final' (túnel hecho con el AVE), 'antes' (sin túnel), 'pasa' (llega la tuneladora)"""
    if t < T("escribe") + 0.9 or t > T("sígueme"): return "abre"
    if t < T("pero el camino") - 0.2 or t > T("y el resultado"): return "final"
    if t < T("después llega"): return "antes"
    return "pasa"

def yf(t):
    if t > T("sígueme"): t = t - T("sígueme")
    if fase(t) == "abre": return 9.8 - 0.22 * t
    return keyed(t, [(T("después llega"), 7.6), (T("en octubre"), 4.6), (T("los sensores"), 2.6), (T("y el resultado"), 0.6)])

def tk(k):
    """momento en que se perfora el pilote k"""
    if k == 0: return T("haces agujeros")
    return T("uno pegado") + (k - 1) * (T("y esa pantalla") - T("uno pegado")) / (NP - 1)

def build():
    sc, cam = scene_setup(world=PAL["cielo"], shadow=0.25); entorno_claro(sc)
    S = {"cam": cam}
    nubes(9, (6, 18, 9), 10, 2, 1.0, s=1.7, seed=8)
    capas = [(PAL["cesped"], 0.12), (PAL["tierra"], 2.0), (PAL["tierra2"], 3.6), ((0.62, 0.50, 0.40), 3.8)]
    z = 0.0; S["suelo"] = []
    for col, g in capas:
        S["suelo"].append(box((12, 12, g), (6, 6, z - g / 2), col)); z -= g
    S["bore"] = cyl(RB, 1.0, LEJOS, PAL["corte"], rot=(math.pi / 2, 0, 0), v=48, unique=True)
    S["bore"].hide_render = True; S["bore"].display_type = 'WIRE'
    for o in S["suelo"]: cortar(o, S["bore"])
    # calle Mallorca (encima del túnel) y acera con los pilotes
    caja((2.4, 12, 0.05), (1.2, 6, 0.02), PAL["asfalto"], r=0.01)
    for i in range(14): caja((0.05, 0.4, 0.01), (1.2, 0.5 + i * 0.85, 0.05), (1, 1, 1), r=0.003)
    caja((1.6, 12, 0.1), (3.2, 6, 0.05), (0.84, 0.83, 0.80), r=0.02)
    caja((8.0, 12, 0.04), (8.0, 6, 0.02), (0.90, 0.88, 0.82), r=0.01)            # plaza del templo
    for k in range(5): arbol((3.7, 1.0 + k * 2.4, 0.1), 0.75, seed=k)
    S["coches"] = [coche(LEJOS, 0.42, color=c, rot=(math.pi / 2 if i % 2 else -math.pi / 2)) for i, c in
                   enumerate((PAL["rojo"], (0.2, 0.45, 0.85), PAL["amarillo"], (0.95, 0.95, 0.95)))]
    # templo de torres aguja (genérico)
    S["templo"] = empty((7.2, 5.6, 0.04))
    tp = S["templo"]
    caja((4.8, 6.2, 2.4), (0, 0, 1.2), PIEDRA, tp, r=0.08)
    for sg in (-1, 1):
        r_ = caja((5.2, 3.5, 0.12), (sg * 1.25, 0, 3.05), PIEDRA2, tp, r=0.04); r_.rotation_euler = (0, sg * 0.55, 0)
    for k in range(5):
        caja((0.14, 0.04, 1.4), (-1.8 + k * 0.9, -3.12, 1.3), (0.62, 0.78, 0.92), tp, r=0.02)   # vidrieras
    cilindro(0.38, 0.06, (0, -3.12, 2.6), (0.98, 0.78, 0.45), tp, rot=(math.pi / 2, 0, 0), r=0.02)  # rosetón
    def torre(x, y, h, rad, top):
        cilindro(rad, h * 0.62, (x, y, h * 0.31), PIEDRA, tp, r=rad * 0.2)
        for j in range(4): caja((rad * 0.5, 0.03, h * 0.08), (x, y - rad - 0.005, h * (0.16 + 0.12 * j)), PIEDRA2, tp, r=0.01)
        bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=rad * 1.02, radius2=rad * 0.12, depth=h * 0.42, location=(x, y, h * 0.62 + h * 0.21))
        o = bpy.context.object; setup(o, PIEDRA2, tp, smooth=True)
        bola(rad * 0.45, (x, y, h * 1.04), top, tp)
    for x, h in ((-1.9, 6.6), (-0.7, 7.4), (0.7, 7.4), (1.9, 6.6)): torre(x, -2.7, h, 0.36, PAL["amarillo"])
    for x, y in ((-1.2, -0.6), (1.2, -0.6), (-1.2, 1.6), (1.2, 1.6)): torre(x, y, 8.4, 0.42, PAL["rojo"])
    torre(0, 0.5, 10.6, 0.6, (0.98, 0.98, 0.98))
    for x in (-1.9, 1.9): torre(x, 2.7, 6.0, 0.34, PAL["amarillo"])
    S["grietas"] = []
    for k, (x, z_, a) in enumerate(((-1.4, 0.9, 0.5), (0.4, 1.4, -0.6), (1.6, 0.6, 0.9))):
        g = caja((0.05, 0.03, 0.9), (7.2 + x, 5.6 - 3.13, z_), (0.25, 0.15, 0.12), r=0.01, unique=True); g.rotation_euler = (0, a, 0)
        S["grietas"].append(g)
    S["sensores"] = [bola(0.12, (7.2 + x, 5.6 - 3.15, z_), (0.3, 0.9, 0.4), unique=True) for x, z_ in
                     ((-2.0, 0.6), (-0.6, 1.9), (0.8, 0.9), (2.1, 1.8), (-2.4, 3.6), (2.4, 3.6))]
    # túnel: anillos (medio tubo a lo largo de Y, se ve desde -X), calzada de vías y el AVE
    S["anillos"] = []
    for k in range(20):
        a = k * 0.6
        S["anillos"].append((a, medio_tubo([(0, a, ZC), (0, a + 0.56, ZC)], RI, RB - RI, HORM, eje=(1, 0, 0))))
    S["losa"] = caja((0.95, 12, 0.12), (0.47, 6, ZD - 0.06), (0.62, 0.62, 0.60), r=0.01)
    S["vias"] = [caja((0.04, 12, 0.04), (x, 6, ZD + 0.02), (0.55, 0.57, 0.62), r=0.005) for x in (0.25, 0.65)]
    S["ave"] = empty(LEJOS)
    for k in range(3):
        caja((0.62, 2.0, 0.7), (0.45, k * 2.08, ZD + 0.43 - ZD), (0.98, 0.98, 0.98), S["ave"], r=0.16)
        caja((0.64, 2.0, 0.08), (0.45, k * 2.08, 0.32), PAL["rojo"], S["ave"], r=0.02)
        caja((0.64, 1.7, 0.16), (0.45, k * 2.08, 0.6), (0.35, 0.45, 0.6), S["ave"], r=0.05)
    bola(0.34, (0.45, -1.0, 0.42), (0.98, 0.98, 0.98), S["ave"], escala=(0.95, 2.0, 1.0))
    # tuneladora
    S["tbm"] = tuneladora(LEJOS, RS, rot=-math.pi / 2, vagones=2)
    S["rueda"] = tuneladora_pieza(S["tbm"], "rueda")
    S["nuevo"] = medio_tubo([(0, 0, 0), (0, 0.56, 0)], RI, RB - RI, (0.86, 0.86, 0.84), eje=(1, 0, 0), unique=True)
    # pilotadora y pilotes
    S["rig"] = empty(LEJOS)
    caja((0.9, 1.0, 0.35), (0.25, 0, 0.3), PAL["amarillo"], S["rig"], r=0.08)
    for sy in (-1, 1): caja((1.1, 0.22, 0.22), (0.25, sy * 0.45, 0.11), (0.22, 0.23, 0.26), S["rig"], r=0.08)
    caja((0.4, 0.5, 0.4), (0.45, 0, 0.65), (0.3, 0.45, 0.75), S["rig"], r=0.08)
    caja((0.12, 0.12, 3.0), (-0.15, 0, 1.6), PAL["rojo"], S["rig"], r=0.03)
    S["barrena"] = cilindro(0.08, 1.6, (0, 0, 0), (0.6, 0.62, 0.66), r=0.02)
    S["tapas"] = [cilindro(RP, 0.03, LEJOS, HUECO, r=0.008, unique=True) for _ in range(NP)]
    S["seccion"] = caja((2 * RP, 0.03, 1.0), LEJOS, HUECO, r=0.01, unique=True)       # primer pilote cortado en la cara delantera
    S["acero"] = [caja((0.025, 0.035, 1.0), LEJOS, (0.95, 0.45, 0.15), r=0.005) for _ in range(3)]
    # comparación y flechas
    S["edif13"] = empty(LEJOS)
    edificio((0, 0, 0), pisos=13, s=1.44, parent=S["edif13"], color=(0.86, 0.90, 0.95), ancho=1.4, fondo=1.2)
    S["fprof"] = flecha3d(LEJOS, (0, 0, -1), PROF, 0.12)
    S["empuje"] = [flecha3d(LEJOS, (1, 0, 0), 1.0, 0.09) for _ in range(3)]
    S["bajo"] = flecha3d(LEJOS, (0, 0, -1), 1.6, 0.12)
    dyn = [cam, S["suelo"], S["bore"], S["coches"], S["templo"], S["grietas"], S["sensores"], [o for _, o in S["anillos"]], S["losa"],
           S["vias"], S["ave"], S["tbm"], S["nuevo"], S["rig"], S["barrena"], S["tapas"], S["seccion"], S["acero"], S["edif13"],
           S["fprof"], S["empuje"], S["bajo"]]
    join_static(dyn)
    return sc, S

def ver(o, on):
    o.hide_render = not on
    for c in o.children_recursive: c.hide_render = not on

def pose(t, S):
    f = fase(t); y_f = yf(t)
    tuneles = {"abre": (y_f, 12.5), "final": (-0.5, 12.5), "pasa": (y_f, 12.5), "antes": None}[f]
    if tuneles is None: S["bore"].location = LEJOS
    else:
        a, b = tuneles; S["bore"].location = (0, (a + b) / 2, ZC); S["bore"].scale = (1, 1, max(b - a, 0.01))
    desde = -1 if f == "final" else (y_f + LSH - 0.2 if f in ("abre", "pasa") else 99)
    nuevo = None
    for a0, o in S["anillos"]:
        o.hide_render = a0 < desde
        if not o.hide_render and a0 < desde + 0.6: nuevo = a0
    if f in ("abre", "pasa") and nuevo is not None:
        u = (t * 1.3) % 1.0; S["nuevo"].location = (0, nuevo - 0.6, ZC + 0.5 * (1 - ss(u)))
    else: S["nuevo"].location = LEJOS
    for o in [S["losa"]] + S["vias"]: o.hide_render = f != "final"
    # tuneladora
    if f in ("abre", "pasa"):
        pop = 1.0 if f == "abre" else back(min(1, (t - T("después llega")) / 0.5))
        S["tbm"].location = (0, y_f, ZC); S["tbm"].scale = (max(pop, 0.01),) * 3
        S["rueda"].rotation_euler.x = t * 2.4
        for c in S["tbm"].children:
            if c is not S["rueda"]: c.hide_render = (y_f - c.location.x * pop) > 12.4
    else: S["tbm"].location = LEJOS
    # AVE
    if f == "final":
        yy = 13.0 - ((t * 3.2) % 20.0); S["ave"].location = (0, yy, ZD); ver(S["ave"], True)
        for c in S["ave"].children: c.hide_render = not (-0.6 < yy + c.location.y < 12.4)
    else: S["ave"].location = LEJOS
    # coches por la calle
    for k, c in enumerate(S["coches"]):
        d = 1 if k % 2 else -1; yy = ((t * 1.3 + k * 3.1) % 12.6) - 0.3
        c.location = (0.75 if d > 0 else 1.65, yy if d > 0 else 12 - yy, 0.05)
    # el suelo se mueve: el templo tiembla y salen grietas
    temb = seg(t, T("si el suelo"), T("si el suelo") + 0.3) * (1 - seg(t, T("así que"), T("así que") + 0.3))
    S["templo"].location = (7.2 + 0.04 * temb * math.sin(t * 47), 5.6, 0.04)
    S["templo"].rotation_euler = (0.01 * temb * math.sin(t * 31), 0, 0)
    for k, g in enumerate(S["grietas"]):
        u = seg(t, T("la piedra") + 0.2 * k, T("la piedra") + 0.2 * k + 0.4) * (1 - seg(t, T("antes de cavar"), T("antes de cavar") + 0.4))
        g.scale = (1, 1, max(u, 0.001)); g.hide_render = u < 0.01
    # sensores: parpadean
    son = T("los sensores") - 0.1 < t < T("hoy los")
    for k, s_ in enumerate(S["sensores"]):
        s_.hide_render = not son; s_.scale = (1 + 0.5 * max(0, math.sin(t * 9 + k)),) * 3
    # pilotadora y pilotes
    perfora = T("haces agujeros") - 0.4 < t < T("y esa pantalla") + 0.3
    if perfora:
        k_act = max([k for k in range(NP) if tk(k) <= t] or [0])
        ry = (k_act + 0.5) * 2 * RP
        if k_act == 0: ry = 2 * RP * 0.5
        S["rig"].location = (XP + 0.15, ry, 0.1); S["rig"].rotation_euler.z = math.pi
        S["barrena"].location = (XP, ry, 0.1 + 0.8 - 0.5 * ((t * 2) % 1.0)); S["barrena"].rotation_euler.z = t * 8
    else: S["rig"].location = LEJOS; S["barrena"].location = LEJOS
    lleno = (0.70, 0.70, 0.68)
    for k, tp in enumerate(S["tapas"]):
        if t < tk(k) or t < T("haces agujeros") - 0.1: tp.location = LEJOS; continue
        tp.location = (XP, RP + k * 2 * RP, 0.115)
        fill = max(tk(k) + 0.5, T("los rellenas") + 0.05 * k)
        set_color(tp, lleno if t > fill else HUECO)
    # sección del primer pilote en la cara delantera: se perfora, se rellena y lleva acero
    if t > T("haces agujeros") - 0.1:
        d = PROF * seg(t, T("haces agujeros"), T("cada uno"))
        S["seccion"].location = (XP, -0.02, -d / 2 + 0.05); S["seccion"].scale = (1, 1, max(d, 0.01))
        set_color(S["seccion"], lleno if t > T("los rellenas") + 0.3 else HUECO)
        for j, a in enumerate(S["acero"]):
            u = seg(t, T("los rellenas") + 0.3 + 0.15 * j, T("son los"))
            if u > 0.01:
                a.location = (XP - 0.09 + 0.09 * j, -0.04, 0.05 - PROF * u / 2); a.scale = (1, 1, PROF * u)
            else: a.location = LEJOS
    else:
        S["seccion"].location = LEJOS
        for a in S["acero"]: a.location = LEJOS
    # flecha de profundidad (40 m)
    if T("y esa pantalla") - 0.1 < t < T("así", 2):
        u = seg(t, T("y esa pantalla"), T("profundidad", 2, fin=True))
        S["fprof"].location = (XP + 0.45, -0.3, 0.1); S["fprof"].scale = (1, 1, max(u, 0.01))
    else: S["fprof"].location = LEJOS
    if T("así que") - 0.1 < t < T("haces agujeros"):
        u = seg(t, T("así que"), T("así que") + 0.5)
        S["bajo"].location = (XP, 1.0, 2.4 - 0.4 * ((t * 1.5) % 1.0)); S["bajo"].scale = (u + 0.01,) * 3
    else: S["bajo"].location = LEJOS
    # edificio de 13 pisos boca abajo
    if T("como un edificio") - 0.1 < t < T("así", 2) + 0.3:
        u = back(min(1, (t - T("como un edificio") + 0.1) / 0.6))
        S["edif13"].location = (5.4, -1.2, 0.0); S["edif13"].rotation_euler = (0, math.pi, 0); S["edif13"].scale = (1, 1, max(u, 0.01))
    else: S["edif13"].location = LEJOS
    # la tierra empuja el muro, no el templo
    if T("así", 2) - 0.1 < t < T("después llega"):
        u = seg(t, T("si la tierra"), T("empuja el muro", fin=True))
        for k, fl in enumerate(S["empuje"]):
            fl.location = (RB + 0.1 + 0.55 * u - 0.12 * math.sin(t * 6 + k) * (1 - u), -0.3, ZC + 1.2 - 1.2 * k); fl.scale = (1,) * 3
    else:
        for fl in S["empuje"]: fl.location = LEJOS
    apply_cam(S["cam"], *cam_lin(t, CAM(), drift=0.03))

def CAM():
    k = Claves(); add = k.add
    ini = V((0.0, 9.6, ZC), (-2.4, -1.9, 0.5), 34)
    add(0.0, V((0.0, 9.8, ZC), (-2.2, -1.7, 0.3), 36)); add(1.2, ini)
    add(T("directa"), V((3.0, 6.0, -0.5), (-13.0, -8.0, 4.0), 28))
    add(T("qué profundidad"), V((3.0, 6.0, -1.0), (-12.5, -10.0, 3.0), 28))
    add(T("la protege"), V((3.5, 6.0, 0.0), (-10.0, -12.0, 7.0), 28))
    add(T("escribe"), V((3.0, 6.0, -1.0), (-14.0, -7.0, 5.0), 28))
    add(T("el ave"), V((0.4, 5.0, ZC), (-5.5, -4.5, 1.8), 32))
    add(T("de la estación"), V((0.5, 6.0, ZC), (-10.0, -12.0, 3.0), 28))
    add(T("casi seis"), V((1.5, 6.0, -2.0), (-8.0, -14.0, 3.5), 28))
    add(T("pero el camino"), V((1.5, 4.0, 0.3), (-6.5, -7.5, 4.0), 32))
    add(T("justo al lado"), V((4.5, 4.0, 3.0), (-10.0, -10.0, 4.0), 30))
    add(T("si el suelo"), V((6.0, 2.5, 1.6), (-6.0, -6.0, 1.5), 34))
    add(T("la piedra"), V((7.0, 2.4, 1.4), (-2.0, -4.0, 0.6), 38))
    add(T("así que"), V((3.0, 5.0, -2.5), (-10.0, -12.0, 3.0), 28))
    add(T("construyes"), V((2.6, 2.0, -3.0), (-5.0, -8.0, 1.0), 32))
    add(T("haces agujeros"), V((2.6, 0.8, 0.3), (-3.0, -3.5, 2.6), 34))
    add(T("uno pegado"), V((2.6, 3.0, 0.0), (-2.0, -4.0, 4.5), 32))
    add(T("cada uno"), V((2.6, 0.3, -0.3), (-1.2, -2.0, 1.4), 40))
    add(T("los rellenas"), V((2.6, 0.0, -3.0), (-0.5, -4.5, 0.6), 34))
    add(T("son los"), V((2.6, 0.5, -3.5), (-2.0, -5.5, 2.0), 32))
    add(T("juntos"), V((2.6, 6.0, -0.5), (-2.0, -9.0, 6.0), 30))
    add(T("de largo"), V((2.6, 8.0, 0.0), (-4.0, -11.0, 5.0), 30))
    add(T("y esa pantalla"), V((2.6, 0.0, -4.5), (-3.5, -8.0, 0.5), 32))
    add(T("profundidad", 2), V((3.0, 0.0, -4.5), (-1.5, -10.0, -0.5), 30))
    add(T("como un edificio"), V((4.0, 0.0, -3.5), (-2.0, -15.0, 0.5), 28))
    add(T("pero hacia"), V((4.5, -1.0, -4.5), (0.0, -13.5, -1.0), 28))
    add(T("si la tierra"), V((1.8, 0.0, -4.0), (-2.0, -6.5, 0.8), 34))
    add(T("y no el templo"), V((4.0, 3.0, 0.5), (-7.0, -11.0, 2.5), 30))
    add(T("después llega"), V((0.3, 7.5, ZC), (-6.5, -5.0, 2.8), 30))
    add(T("de doce"), V((0.0, 5.0, ZC), (-3.6, -4.0, 0.8), 34))
    add(T("en octubre"), V((3.0, 4.0, -1.0), (-12.0, -6.0, 3.0), 28))
    add(T("los sensores"), V((7.0, 2.4, 1.8), (-4.0, -5.0, 1.2), 34))
    add(T("cada milímetro"), V((7.2, 2.4, 2.6), (2.5, -6.0, 2.0), 34))
    add(T("y el resultado"), V((5.0, 4.0, 2.0), (-9.0, -9.0, 4.0), 30))
    add(T("hoy los"), V((0.4, 5.0, ZC), (-5.0, -4.0, 1.6), 32))
    add(T("te has acercado"), V((3.0, 6.0, -0.5), (-13.0, -8.0, 3.0), 28))
    add(T("dime en"), V((6.0, 3.5, 2.5), (-8.0, -8.0, 3.0), 30))
    add(T("y si quieres"), V((3.0, 6.0, -1.0), (-11.0, -11.0, 4.0), 28))
    add(T("lo más pedido"), V((3.0, 6.0, -1.5), (-13.5, -7.0, 2.0), 28))
    add(T("sígueme"), V((0.0, 9.8, ZC), (-2.2, -1.7, 0.3), 36))
    add(DUR + 1, ini)
    return k.k

def anchors(sc, S, t):
    cam = S["cam"]; P = lambda v: proj(sc, cam, v); y_f = yf(t)
    return {"rueda": P((0.0, y_f, ZC + RS)), "tunel": P((0.3, 6.0, ZC + RB)), "sants": P((0.3, 0.0, ZC + RB)), "sagrera": P((0.3, 12.0, ZC + RB)),
            "calle": P((1.2, 6.0, 0.3)), "templo": P((7.2, 2.5, 3.0)), "pilote": P((XP, 0.0, 0.3)), "fila": P((XP, 8.0, 0.3)),
            "fondo": P((XP, 0.0, -PROF)), "muro": P((XP, 0.0, ZC)), "edif": P((5.4, -1.2, -PROF)), "edif_top": P((5.4, -1.2, 0.2)), "sensores": P((7.2, 2.4, 2.0))}

if __name__ == "__main__":
    run("avesagrada", build, pose, anchors)
