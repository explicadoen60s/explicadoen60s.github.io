# «¿Cuántos metros de diámetro tenía la tuneladora de la M-30?» (Lo que esconde tu ciudad): maqueta de Madrid sobre una
# isla de terreno cortada justo por el eje del túnel (cara de corte en y=0, se ve medio túnel por dentro).
# Escala: 1 unidad = 5 m. Rueda de 15,2 m = 3,04 u; edificio de 5 pisos al lado para comparar.
# Planos (fotografía → motion; esquina libre arriba-izquierda salvo indicación):
#  0,0 coche dentro del túnel en primer plano, moviéndose · 1,5 se abre: el túnel bajo el parque · 2,6 maqueta entera
#  4,3-9 pregunta (plano amplio que deriva) · 9,7 antes: la M-30 al aire libre junto al río · 11,5 río y coches
#  13,4 humo de los coches (primer plano) · 14,8 la ciudad cortada · 16,5 flecha: bajo tierra · 18,6 obrero cavando a mano
#  21,2 llega la tuneladora · 22,9 rueda de corte girando (primer plano) · 25,5 muerde la tierra · 26,6 cinta con tierra
#  28,9 brazo y anillos · 31,6 anillos a lo largo · 34 la máquina entera (3.200 t) · 37,6 rueda de frente
#  39,3 flechas del diámetro (15,2 m) · 40,9 edificio de 5 pisos al lado · 43,7 el tren de remolques (148 m)
#  46,2 avanza deprisa (46 m/día) · 48,6 plano amplio (3,5 km) · 50,6 dentro: tres carriles · 53,5 arriba, el parque
#  55,2 parque junto al río · 57,4-66 cierre (plano amplio que deriva) · 66 vuelta al primer plano del coche en el túnel.
import bpy, math, sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from modelos import *
from maqueta import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("m30tunel")
ZC = -2.4; RB = 1.52; RI = 1.40; ZD = ZC - 0.75; X0, X1 = -13.0, 13.0
RS = 1.48                                   # radio del escudo de la tuneladora
LSH = 1.4 * RS                              # largo del escudo
VC = 1.446                                  # velocidad de los coches del túnel (vuelve al mismo sitio al final)
HORM = (0.74, 0.74, 0.72)

def back(x):
    x = max(0.0, min(1.0, x)); c = 1.70158; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

def final(t): return t < T("antes la") or t > T("dentro")
def parque_on(t): return t < T("antes la") or t > T("y arriba")

def xf(t):
    return keyed(t, [(T("así que traes"), -3.2), (T("muerde"), -2.8), (T("la tuneladora del"), -0.6), (T("y de largo"), 0.6),
                     (T("avanzaba"), 1.6), (T("así cavó", fin=True) + 1.2, 10.5)])

def build():
    sc, cam = scene_setup(world=PAL["cielo"], shadow=0.25); entorno_claro(sc)
    S = {"cam": cam}
    nubes(9, (0, 16, 5.5), 12, 1.5, 1.0, s=1.6, seed=3)
    # terreno: cuatro capas cortadas por el eje del túnel (la cara de corte es y=0)
    capas = [(PAL["cesped"], 0.12), (PAL["tierra"], 1.3), (PAL["tierra2"], 2.6), ((0.62, 0.50, 0.40), 2.4)]
    z = 0.0; S["suelo"] = []
    for col, g in capas:
        S["suelo"].append(box((X1 - X0, 7.6, g), (0, 3.8, z - g / 2), col)); z -= g
    S["bore"] = cyl(RB, 1.0, (0, 0, ZC), PAL["corte"], rot=(0, math.pi / 2, 0), v=48, unique=True)
    S["bore"].hide_render = True; S["bore"].display_type = 'WIRE'
    for o in S["suelo"]: cortar(o, S["bore"])
    # río Manzanares con orillas, y la ciudad al otro lado
    box((X1 - X0, 1.5, 0.08), (0, 4.0, -0.02), PAL["agua"])
    for yy in (3.2, 4.8): caja((X1 - X0, 0.12, 0.16), (0, yy, 0.0), (0.8, 0.8, 0.78), r=0.03)
    rnd = random.Random(4); cols = [PAL["pared"], (0.98, 0.85, 0.6), (0.93, 0.74, 0.62), (0.80, 0.88, 0.95), PAL["rosa"]]
    x = -11.8
    while x < 12.5:
        edificio((x, 6.4, 0.0), pisos=rnd.randint(4, 7), s=0.95, color=rnd.choice(cols), ancho=1.9, fondo=1.4)
        x += 2.25
    for k in range(10): arbol((-12 + k * 2.6, 5.1, 0.0), 0.7, seed=k)
    # M-30 en superficie (antes) con coches y humo
    S["calle"] = calle(X1 - X0, (0, 1.3, 0.0), ancho=1.6)
    S["sup"] = [coche(LEJOS, 0.56, color=c) for c in (PAL["rojo"], (0.2, 0.45, 0.85), PAL["amarillo"], (0.95, 0.95, 0.95), (0.3, 0.7, 0.4), PAL["rosa"])]
    S["humo"] = [sph(0.14, LEJOS, (0.55, 0.55, 0.58), seg=10) for _ in range(12)]
    # parque encima (después)
    S["parque"] = caja((X1 - X0, 2.5, 0.06), (0, 1.3, 0.04), (0.42, 0.78, 0.34), r=0.02)
    S["sendero"] = caja((X1 - X0, 0.35, 0.03), (0, 1.0, 0.085), (0.93, 0.84, 0.66), r=0.01)
    S["arb"] = [arbol((X0 + 0.8 + k * 1.55, 1.75 + (0.35 if k % 2 else -0.15), 0.06), 0.8, seed=20 + k) for k in range(16)]
    S["paseo"] = [persona(LEJOS, 0.35, ropa=c) for c in ((0.9, 0.4, 0.3), (0.3, 0.5, 0.9))]
    # obrero cavando a mano
    S["obrero"] = persona(LEJOS, 0.8, ropa=(1.0, 0.55, 0.1))
    S["pico"] = caja((0.07, 0.07, 0.7), LEJOS, (0.5, 0.35, 0.2), r=0.01)
    S["bore_mano"] = cyl(0.75, 1.0, LEJOS, PAL["corte"], rot=(0, math.pi / 2, 0), unique=True); S["bore_mano"].hide_render = True
    for o in S["suelo"]: cortar(o, S["bore_mano"])
    # anillos de hormigón (dovelas): medio tubo por anillo
    S["anillos"] = []; n = int((X1 - X0) / 0.6)
    for k in range(n):
        a = X0 + k * 0.6
        o = medio_tubo([(a, 0, ZC), (a + 0.56, 0, ZC)], RI, RB - RI, HORM); S["anillos"].append((a, o))
    # calzada con tres carriles
    S["calzada"] = caja((X1 - X0, 1.2, 0.1), (0, 0.6, ZD - 0.05), PAL["asfalto"], r=0.01)
    S["rayas"] = [caja((0.35, 0.04, 0.012), (X0 + 0.3 + i * 0.8, y, ZD + 0.006), (1, 1, 1), r=0.003) for y in (0.4, 0.8) for i in range(32)]
    S["tc"] = [coche(LEJOS, 0.32, color=c) for c in ((0.2, 0.45, 0.85), PAL["rojo"], PAL["amarillo"], (0.95, 0.95, 0.95), (0.3, 0.7, 0.4), PAL["rosa"], (0.6, 0.4, 0.8))]
    # tuneladora
    S["tbm"] = tuneladora(LEJOS, RS, vagones=5)
    S["rueda"] = tuneladora_pieza(S["tbm"], "rueda"); S["brazo"] = tuneladora_pieza(S["tbm"], "brazo")
    S["tierra"] = [caja((0.16, 0.16, 0.12), LEJOS, PAL["tierra"], r=0.03) for _ in range(12)]
    S["nuevo"] = medio_tubo([(0, 0, 0), (0.56, 0, 0)], RI, RB - RI, (0.96, 0.86, 0.62), unique=True)
    # comparaciones y flechas
    S["edif5"] = empty(LEJOS); edificio((0, 0, 0), pisos=5, s=1.3, parent=S["edif5"], color=(0.98, 0.85, 0.6), ancho=1.6, fondo=1.3)
    S["fup"] = flecha3d(LEJOS, (0, 0, 1), RB, 0.07); S["fdn"] = flecha3d(LEJOS, (0, 0, -1), RB, 0.07)
    S["fbaja"] = flecha3d(LEJOS, (0, 0, -1), 2.2, 0.14)
    S["favance"] = flecha3d(LEJOS, (1, 0, 0), 1.6, 0.1)
    dyn = [cam, S["suelo"], S["bore"], S["calle"], S["sup"], S["humo"], S["parque"], S["sendero"], S["arb"], S["paseo"], S["obrero"],
           S["pico"], S["bore_mano"], [o for _, o in S["anillos"]], S["calzada"], S["rayas"], S["tc"], S["tbm"], S["tierra"], S["nuevo"],
           S["edif5"], S["fup"], S["fdn"], S["fbaja"], S["favance"]]
    join_static(dyn)
    return sc, S

def ver(o, on):
    o.hide_render = not on
    for c in o.children_recursive: c.hide_render = not on

def pose(t, S):
    fin = final(t); x_f = xf(t)
    maq = T("así que traes") - 0.1 < t <= T("dentro")
    # hueco del túnel
    if fin: a, b = X0 - 0.5, X1 + 0.5
    elif maq: a, b = X0 - 0.5, x_f
    else: a, b = None, None
    if a is None: S["bore"].location = LEJOS
    else: S["bore"].location = ((a + b) / 2, 0, ZC); S["bore"].scale = (1, 1, max(b - a, 0.01))
    # obrero a mano
    mano = T("meterla") < t < T("así que traes")
    if mano:
        L = 1.2 + 0.4 * seg(t, T("pero cavar"), T("así que traes"))
        S["bore_mano"].location = (X0 - 0.3 + L / 2, 0, ZC - 0.7); S["bore_mano"].scale = (1, 1, L)
        S["obrero"].location = (X0 - 0.3 + L - 0.45, 0.3, ZC - 1.45); S["obrero"].rotation_euler = (0, 0.25 * math.sin(t * 9), -math.pi / 2)
        S["pico"].location = (X0 - 0.3 + L - 0.15, 0.22, ZC - 0.85 + 0.15 * math.sin(t * 9)); S["pico"].rotation_euler = (0, 0.9 + 0.5 * math.sin(t * 9), 0)
    else:
        S["bore_mano"].location = LEJOS; S["obrero"].location = LEJOS; S["pico"].location = LEJOS
    # anillos
    hasta = X1 + 1 if fin else (x_f - LSH + 0.2 if maq else X0 - 1)
    nuevo = None
    ult = None
    for a0, o in S["anillos"]:
        o.hide_render = not (a0 + 0.56 < hasta)
        if not o.hide_render: ult = (a0, o)
    S["nuevo"].location = LEJOS
    if maq and ult is not None and t > T("muerde"):
        u = ((t - T("detrás")) * 1.2) % 1.0
        ult[1].hide_render = True
        S["nuevo"].location = (ult[0], 0, ZC + 0.7 * (1 - ss(min(1, u * 1.5))))
    # tuneladora
    if maq:
        pop = back(min(1, (t - T("así que traes")) / 0.5))
        S["tbm"].location = (x_f, 0, ZC); S["tbm"].scale = (max(pop, 0.01),) * 3
        vel = 6 if t < T("avanzaba") else 14
        S["rueda"].rotation_euler.x = t * (1.5 if t < T("delante") else 3.0) * (vel / 6)
        S["brazo"].rotation_euler.x = 1.2 * math.sin(t * 2.2)
    else: S["tbm"].location = LEJOS
    # tierra por la cinta
    cinta = maq and T("muerde") - 0.3 < t < T("avanzaba")
    for k, c in enumerate(S["tierra"]):
        if cinta:
            u = ((t * 0.35 + k / 12) % 1.0); c.location = (x_f - 0.6 - u * 8.0, RS * 0.25, ZC + RS * 0.48 + 0.12); c.rotation_euler.z = k
        else: c.location = LEJOS
    # superficie: carretera o parque
    ver(S["calle"], not parque_on(t))
    pq = 1.0 if t < T("antes la") else seg(t, T("y arriba"), T("donde antes", fin=True))
    for o in (S["parque"], S["sendero"]): o.hide_render = pq < 0.02
    for k, e in enumerate(S["arb"]):
        g = 1.0 if t < T("antes la") else seg(t, T("y arriba") + 0.1 * k, T("y arriba") + 0.1 * k + 0.6)
        e.scale = (max(g, 0.001),) * 3; ver(e, g > 0.01)
    for k, p in enumerate(S["paseo"]):
        if pq > 0.5:
            xx = -8 + ((t * 0.5 + k * 9) % 16); p.location = (xx if k == 0 else -xx, 1.0 + 0.12 * k, 0.1 + 0.02 * abs(math.sin(t * 8)))
            p.rotation_euler.z = -math.pi / 2 if k == 0 else math.pi / 2
        else: p.location = LEJOS
    for k, c in enumerate(S["sup"]):
        if not parque_on(t):
            d = 1 if k % 2 == 0 else -1; xx = ((t * 2.2 + k * 4.1) % 26) - 13
            c.location = (xx * d, 0.85 if d > 0 else 1.75, 0.04); c.rotation_euler.z = 0 if d > 0 else math.pi
        else: c.location = LEJOS
    humo = T("ruido") - 0.2 < t < T("así que decides") + 0.6
    for k, h in enumerate(S["humo"]):
        if humo:
            c = S["sup"][k % 6].location; u = (t * 0.7 + k * 0.37) % 1.0
            h.location = (c.x - 0.9 * (1 if k % 2 == 0 else -1) - u * 0.4, c.y, 0.35 + u * 1.3); h.scale = (0.6 + u * 1.4,) * 3
        else: h.location = LEJOS
    # calzada y coches del túnel
    S["calzada"].hide_render = not fin
    for r in S["rayas"]: r.hide_render = not fin
    for k, c in enumerate(S["tc"]):
        if fin:
            lane = (0.2, 0.6, 1.0)[k % 3] if k else 0.6
            xx = X0 + 0.6 + ((t * VC * (1 + 0.08 * (k % 3)) + 8.6 + k * 3.7) % 24.6)
            if k == 0: xx = X0 + ((t * VC + 8.6) % 24)
            c.location = (xx, lane, ZD); c.rotation_euler.z = 0
        else: c.location = LEJOS
    # flechas
    if T("así que decides") - 0.1 < t < T("pero cavar"):
        u = seg(t, T("así que decides"), T("así que decides") + 0.6)
        S["fbaja"].location = (0, 1.3, 2.6 - 0.5 * ((t * 1.5) % 1.0)); S["fbaja"].scale = (u + 0.01,) * 3
    else: S["fbaja"].location = LEJOS
    if T("quince") - 0.2 < t < T("y de largo"):
        u = seg(t, T("quince") - 0.2, T("quince") + 0.6)
        for f, sg in ((S["fup"], 1), (S["fdn"], -1)):
            f.location = (x_f + 0.4, -0.2, ZC + sg * 0.03); f.scale = (1, 1, max(u, 0.01))
    else: S["fup"].location = LEJOS; S["fdn"].location = LEJOS
    if T("avanzaba") - 0.1 < t < T("dentro"):
        S["favance"].location = (x_f + 0.6 + 0.4 * ((t * 1.6) % 1.0), -0.2, ZC + RS + 0.5); S["favance"].scale = (1,) * 3
    else: S["favance"].location = LEJOS
    if T("más alta") - 0.1 < t < T("y de largo") + 0.2:
        u = back(min(1, (t - T("más alta") + 0.1) / 0.5))
        S["edif5"].location = (x_f + 2.3, -1.6, ZC - RB); S["edif5"].scale = (1, 1, max(u, 0.01))
    else: S["edif5"].location = LEJOS
    apply_cam(S["cam"], *cam_lin(t, CAM(), drift=0.03))

def CAM():
    k = Claves(); add = k.add
    car0 = lambda t: X0 + ((t * VC + 8.6) % 24)
    ini = V((car0(0.6) + 0.3, 0.6, ZD + 0.25), (-1.6, -1.9, 0.45), 32)
    add(0.0, V((car0(0.0) + 0.4, 0.6, ZD + 0.25), (-1.5, -1.9, 0.45), 32)); add(1.2, ini)
    add(T("y de repente"), V((-2.0, 0.6, ZC + 0.3), (0.6, -5.5, 1.0), 32))
    add(T("bajo tierra"), V((0.0, 1.5, -1.2), (0.5, -11.5, 7.0), 30))
    add(T("cuántos metros"), V((-1.5, 1.5, -1.0), (3.0, -11.0, 8.0), 30))
    add(T("diámetro"), V((-2.5, 1.0, -1.6), (4.0, -9.0, 5.0), 32))
    add(T("escribe"), V((1.5, 1.5, -1.2), (-3.5, -11.0, 7.5), 30))
    add(T("acabe"), V((0.0, 2.0, -0.8), (-1.0, -10.0, 8.5), 30))
    add(T("antes la"), V((0.0, 2.5, 0.0), (0.0, -9.0, 5.5), 30))
    add(T("al aire libre"), V((-2.0, 2.6, 0.2), (-1.0, -5.5, 2.6), 34))
    add(T("ruido"), V((1.0, 1.3, 0.4), (-0.5, -3.5, 1.4), 38))
    add(T("cortando"), V((0.5, 3.0, 0.5), (2.0, -7.0, 4.5), 32))
    add(T("así que decides"), V((0.0, 1.3, -1.0), (0.5, -10.5, 6.0), 30))
    add(T("bajo tierra", 2, fin=True), V((X0 + 2.5, 1.0, ZC + 0.5), (4.0, -8.0, 3.5), 30))
    add(T("pero cavar"), V((X0 + 1.2, 0.3, ZC - 0.9), (2.4, -3.4, 1.2), 34))
    add(T("es lentísimo"), V((X0 + 1.3, 0.3, ZC - 0.9), (1.6, -2.6, 0.4), 38))
    add(T("así que traes"), V((-4.5, 0.3, ZC), (1.5, -8.5, 1.6), 32))
    add(T("delante"), V((-2.9, 0.0, ZC), (2.6, -2.6, 0.5), 36))
    add(T("cuchillas"), V((-2.8, 0.0, ZC), (2.2, -1.6, -0.6), 40))
    add(T("muerde"), V((-3.0, 0.2, ZC + 0.3), (2.4, -2.8, 1.0), 36))
    add(T("y una cinta"), V((-6.5, 0.3, ZC + 0.8), (0.0, -5.0, 2.0), 34))
    add(T("detrás"), V((-4.6, 0.3, ZC + 0.4), (-1.6, -4.2, 0.8), 36))
    add(T("así el túnel"), V((-8.0, 0.4, ZC), (2.5, -4.5, 1.0), 34))
    add(T("la tuneladora del"), V((-4.0, 0.0, ZC), (1.0, -10.0, 2.0), 30))
    add(T("toneladas"), V((-5.0, 0.0, ZC), (-1.5, -9.0, 3.0), 30))
    add(T("y su rueda"), V((-0.6, 0.0, ZC), (3.4, -3.6, 0.3), 36))
    add(T("quince"), V((0.0, 0.0, ZC), (3.8, -6.0, 0.6), 32))
    add(T("más alta"), V((1.0, -1.0, ZC), (1.5, -10.5, 0.8), 30))
    add(T("y de largo"), V((-5.0, 0.0, ZC), (-1.0, -8.5, 1.6), 32))
    add(T("ciento", fin=True), V((-8.0, 0.0, ZC), (1.0, -8.5, 1.6), 32))
    add(T("avanzaba"), V((2.5, 0.0, ZC), (2.0, -9.0, 2.2), 30))
    add(T("así cavó"), V((0.0, 1.5, -1.5), (0.0, -14.0, 7.5), 28))
    add(T("dentro"), V((2.0, 0.6, ZD + 0.2), (-1.4, -2.4, 0.6), 34))
    add(T("cada tubo", fin=True) + 0.4, V((3.0, 0.6, ZD + 0.2), (1.2, -2.2, 0.8), 36))
    add(T("y arriba"), V((0.0, 2.0, 0.2), (0.5, -6.0, 3.0), 32))
    add(T("ahora hay"), V((-2.0, 2.6, 0.3), (-1.0, -4.0, 1.6), 36))
    add(T("te has acercado"), V((0.0, 1.5, -1.2), (1.5, -11.5, 6.5), 30))
    add(T("dime en"), V((-3.0, 2.5, 0.0), (0.5, -6.0, 3.0), 34))
    add(T("y si quieres"), V((-1.0, 1.5, -1.2), (-2.5, -11.0, 7.5), 30))
    add(T("lo más pedido"), V((-2.0, 0.8, -1.8), (0.5, -8.0, 3.5), 30))
    add(T("sígueme"), V((car0(T("sígueme")) + 0.4, 0.6, ZD + 0.25), (-1.5, -1.9, 0.45), 32))
    add(DUR + 1, V((car0(DUR + 1) + 0.4, 0.6, ZD + 0.25), (-1.5, -1.9, 0.45), 32))
    return k.k

def anchors(sc, S, t):
    cam = S["cam"]; P = lambda v: proj(sc, cam, v); x_f = xf(t)
    return {"rueda": P((x_f + 0.2, 0, ZC)), "maquina": P((x_f - 3.0, 0, ZC + RS)), "tren": P((x_f - 6.0, 0, ZC + RS)),
            "carretera": P((0, 1.3, 0.4)), "tunel": P((2.5, 0.6, ZD + 0.4)), "edif": P((x_f + 2.3, -1.6, ZC - RB + 2.9)),
            "parque": P((-1.0, 1.4, 0.8)), "rio": P((-1.0, 4.0, 0.3)), "obrero": P((X0 + 1.0, 0.3, ZC - 0.3)), "anillo": P((x_f - LSH - 0.3, 0.3, ZC + RI))}

if __name__ == "__main__":
    run("m30tunel", build, pose, anchors)
