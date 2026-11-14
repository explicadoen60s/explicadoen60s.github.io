# «¿Cuántos kilómetros de túnel unen Atocha con Chamartín?» (Lo que esconde tu ciudad)
# Maqueta de Madrid en corte: la isla ocupa x∈[0,8], y∈[0,16]; la cara de corte izquierda (x=0) va por el eje del túnel
# (a lo largo de Y). Al sur (y≈0) la estación de Atocha, al norte (y≈16) la de Chamartín, cada una con su túnel corto y su tren.
# Debajo del centro: metro (sección redonda), colectores y cimientos de los edificios. Escala vertical: 1 unidad = 5 m
# (el túnel va a 55 m = 11 unidades). La tuneladora de presión de tierras une los dos túneles; después pasa el AVE.
# Planos (fotografía → motion; esquina libre arriba-izquierda, que ocupa el mini del juego desde 2,6 s):
#  0,0 rueda de corte girando en primer plano · 2,0 se abre · 5,4 maqueta entera · 7,9 Atocha con su tren · 9,8 Chamartín
#  11,9 no se tocan (plano amplio) · 13,1 viajero por la calle · 16,2 flecha hacia abajo · 17,9 metro · 19,2 colectores/cimientos
#  20,5 bajas (flecha de 55 m) · 24,1 edificio de 18 plantas boca abajo · 26,8 la calle se hunde · 29,8 tuneladora
#  32,9 presión en el frente (primer plano) · 34,9 túnel hecho · 36,6 revelación · 39 vías · 42 julio 2022 · 44,3 euros
#  47,2 el AVE cruzando · 51 de Galicia a Andalucía · 54,6-64 cierre (planos amplios) · 64,5 vuelta al primer plano de la rueda.
import bpy, math, sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from modelos import *
from maqueta import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("tunelave")
ZC = -11.0; RB = 1.15; RI = 1.05; ZD = ZC - 0.55; RS = 1.12; LSH = 1.4 * RS
YA, YB = 3.0, 13.0                       # final del túnel de Atocha y principio del de Chamartín
HORM = (0.74, 0.74, 0.72); NUEVO = (0.88, 0.88, 0.86)
AZUL_ATO = (0.30, 0.55, 0.85); VERDE_CHA = (0.35, 0.72, 0.45)

def back(x):
    x = max(0.0, min(1.0, x)); c = 1.70158; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

def fase(t):
    """'abre' (rueda del principio y del bucle), 'antes' (dos redes sin unir), 'pasa' (la tuneladora avanza), 'final'"""
    if t < T("madrid") - 0.3 or t > T("así que ya sabes") - 0.2: return "abre"
    if t < T("así que usas") - 0.1: return "antes"
    if t < T("y aquí viene"): return "pasa"
    return "final"

def yf(t):
    """frente de la tuneladora"""
    if fase(t) == "abre":
        tt = t if t < 20 else t - T("así que ya sabes") + 0.2
        return 8.2 + 0.25 * tt
    return keyed(t, [(T("así que usas"), YA + 0.2), (T("que sujeta"), 7.5), (T("y aquí viene"), YB + 0.3)])

def build():
    sc, cam = scene_setup(world=PAL["cielo"], shadow=0.25); entorno_claro(sc)
    S = {"cam": cam}
    nubes(9, (4, 22, 9), 12, 2, 1.0, s=1.7, seed=4)
    capas = [(PAL["cesped"], 0.12), (PAL["tierra"], 2.2), ((0.68, 0.50, 0.32), 3.4), (PAL["tierra2"], 4.0), ((0.60, 0.48, 0.38), 4.8)]
    z = 0.0; S["suelo"] = []
    for col, g in capas:
        S["suelo"].append(box((8, 16, g), (4, 8, z - g / 2), col)); z -= g
    S["boreA"] = cyl(RB, 1.0, LEJOS, PAL["corte"], rot=(math.pi / 2, 0, 0), v=48, unique=True)
    S["boreB"] = cyl(RB, 1.0, LEJOS, PAL["corte"], rot=(math.pi / 2, 0, 0), v=48, unique=True)
    for b in (S["boreA"], S["boreB"]): b.hide_render = True; b.display_type = 'WIRE'
    for o in S["suelo"]: cortar(o, S["boreA"]); cortar(o, S["boreB"])
    # calle sobre el túnel, aceras, edificios, árboles y coches
    caja((2.0, 16, 0.05), (1.0, 8, 0.02), PAL["asfalto"], r=0.01)
    for i in range(18): caja((0.05, 0.4, 0.01), (1.0, 0.4 + i * 0.88, 0.05), (1, 1, 1), r=0.003)
    caja((1.0, 16, 0.1), (2.5, 8, 0.05), (0.84, 0.83, 0.80), r=0.02)
    cols = ((0.95, 0.86, 0.72), (0.86, 0.90, 0.95), (0.98, 0.78, 0.62), (0.92, 0.92, 0.88), (0.80, 0.88, 0.82))
    for k, (y, p) in enumerate(((4.6, 6), (6.6, 8), (8.6, 5), (10.6, 7), (5.6, 4), (9.6, 6))):
        x = 4.2 if k < 4 else 6.6
        edificio((x, y, 0.0), pisos=p, s=1.0, color=cols[k % 5], ancho=1.6, fondo=1.4)
    for k in range(6): arbol((2.8, 3.8 + k * 1.6, 0.1), 0.6, seed=k)
    S["coches"] = [coche(LEJOS, 0.38, color=c, rot=(math.pi / 2 if i % 2 else -math.pi / 2)) for i, c in
                   enumerate((PAL["rojo"], (0.2, 0.45, 0.85), PAL["amarillo"], (0.95, 0.95, 0.95)))]
    # estaciones: Atocha (sur, bóveda) y Chamartín (norte, caja con marquesina)
    caja((3.6, 2.4, 1.4), (5.2, 1.4, 0.7), (0.93, 0.80, 0.66), r=0.06)
    cilindro(1.2, 3.4, (5.2, 1.4, 1.4), (0.70, 0.85, 0.95), rot=(0, math.pi / 2, 0), r=0.05)
    for k in range(5): caja((0.06, 0.04, 0.8), (3.8 + k * 0.7, 0.18, 0.6), (0.55, 0.75, 0.90), r=0.01)
    planta((3.2, 0.6, 0.1), 1.0); planta((7.2, 0.6, 0.1), 1.0)
    caja((3.6, 2.4, 1.8), (5.2, 14.6, 0.9), (0.88, 0.90, 0.92), r=0.06)
    caja((4.0, 2.8, 0.12), (5.2, 14.6, 1.86), (0.40, 0.45, 0.52), r=0.03)
    for k in range(4):
        for j in range(2): caja((0.5, 0.04, 0.4), (3.9 + k * 0.85, 13.38, 0.55 + j * 0.65), (0.62, 0.80, 0.94), r=0.01)
    # andenes dentro de los dos túneles cortos
    for y0, col in ((1.5, AZUL_ATO), (14.5, VERDE_CHA)):
        caja((0.35, 2.6, 0.5), (0.8, y0, ZD + 0.1), (0.85, 0.84, 0.80), r=0.02)
        caja((0.36, 2.6, 0.05), (0.8, y0, ZD + 0.36), col, r=0.01)
    # lo que hay debajo del centro: metro (sección), colectores y cimientos
    S["metro"] = empty((0, 0, 0))
    for yy in (6.2, 9.8):
        torus(0.55, 0.08, (-0.02, yy, -3.2), HORM, S["metro"], rot=(0, math.pi / 2, 0))
        cilindro(0.5, 0.03, (-0.02, yy, -3.2), (0.25, 0.22, 0.24), S["metro"], rot=(0, math.pi / 2, 0))
        caja((0.04, 0.7, 0.45), (-0.05, yy, -3.3), (0.95, 0.35, 0.30), S["metro"], r=0.06)
    S["colect"] = empty((0, 0, 0))
    for yy in (4.6, 8.0, 11.4):
        torus(0.3, 0.06, (-0.02, yy, -1.3), (0.55, 0.58, 0.62), S["colect"], rot=(0, math.pi / 2, 0))
        cilindro(0.28, 0.03, (-0.02, yy, -1.3), (0.30, 0.42, 0.55), S["colect"], rot=(0, math.pi / 2, 0))
    S["cimientos"] = empty((0, 0, 0))
    for yy in (4.0, 5.2, 7.1, 8.3, 10.2, 11.0):
        caja((0.06, 0.22, 2.4), (-0.02, yy, -1.3), (0.80, 0.80, 0.78), S["cimientos"], r=0.02)
    # túnel: anillos (medio tubo a lo largo de Y, se ve desde -X), losa de vías
    S["anillos"] = []
    for k in range(28):
        a = -0.5 + k * 0.6
        S["anillos"].append((a, medio_tubo([(0, a, ZC), (0, a + 0.58, ZC)], RI, RB - RI, HORM, eje=(1, 0, 0))))
    S["losas"] = []
    for k in range(17):
        y0 = -0.5 + k * 1.0
        S["losas"].append((y0, caja((0.95, 1.0, 0.1), (0.47, y0 + 0.5, ZD - 0.05), (0.62, 0.62, 0.60), r=0.005)))
    S["vias"] = [caja((0.04, 17, 0.04), (x, 8, ZD + 0.02), (0.55, 0.57, 0.62), r=0.005) for x in (0.27, 0.67)]
    # trenes: el del sur, el del norte (antes) y el AVE (después)
    def tren(col, frente=1):
        e = empty(LEJOS)
        for k in range(3):
            caja((0.62, 2.0, 0.7), (0.47, -frente * k * 2.08, 0.43), (0.98, 0.98, 0.98), e, r=0.16)
            caja((0.64, 2.0, 0.08), (0.47, -frente * k * 2.08, 0.32), col, e, r=0.02)
            caja((0.64, 1.7, 0.16), (0.47, -frente * k * 2.08, 0.6), (0.35, 0.45, 0.6), e, r=0.05)
        bola(0.34, (0.47, frente * 1.0, 0.42), (0.98, 0.98, 0.98), e, escala=(0.95, 2.0, 1.0))
        return e
    S["tsur"] = tren(AZUL_ATO, 1); S["tnorte"] = tren(VERDE_CHA, -1); S["ave"] = tren(PAL["rojo"], 1)
    # tuneladora
    S["tbm"] = tuneladora(LEJOS, RS, rot=-math.pi / 2, vagones=2)
    S["rueda"] = tuneladora_pieza(S["tbm"], "rueda")
    S["nuevo"] = medio_tubo([(0, 0, 0), (0, 0.58, 0)], RI, RB - RI, NUEVO, eje=(1, 0, 0), unique=True)
    # viajero con maleta
    S["viajero"] = empty(LEJOS)
    persona((0, 0, 0), 0.55, S["viajero"], ropa=(0.95, 0.55, 0.25))
    caja((0.12, 0.18, 0.22), (0.12, 0.0, 0.11), (0.25, 0.45, 0.85), S["viajero"], r=0.03)
    # flechas y comparación
    S["fbaja"] = flecha3d(LEJOS, (0, 0, -1), 1.6, 0.12)
    S["fprof"] = flecha3d(LEJOS, (0, 0, -1), -ZC, 0.14)
    S["fcalle"] = [flecha3d(LEJOS, (0, 0, -1), 1.2, 0.09) for _ in range(3)]
    S["fpres"] = [flecha3d(LEJOS, (0, 1, 0), 0.9, 0.08) for _ in range(3)]
    S["hund"] = caja((2.0, 2.4, 0.06), LEJOS, PAL["asfalto"], r=0.01, unique=True)
    S["edif18"] = empty(LEJOS)
    edificio((0, 0, 0), pisos=18, s=1.43, parent=S["edif18"], color=(0.86, 0.90, 0.95), ancho=1.4, fondo=1.2)
    dyn = [cam, S["suelo"], S["boreA"], S["boreB"], S["coches"], S["metro"], S["colect"], S["cimientos"], [o for _, o in S["anillos"]],
           [o for _, o in S["losas"]], S["vias"], S["tsur"], S["tnorte"], S["ave"], S["tbm"], S["nuevo"], S["viajero"], S["fbaja"],
           S["fprof"], S["fcalle"], S["fpres"], S["hund"], S["edif18"]]
    join_static(dyn)
    return sc, S

def ver(o, on):
    o.hide_render = not on
    for c in o.children_recursive: c.hide_render = not on

def resalta(o, u):
    s = 1 + 0.25 * u
    o.scale = (s, 1, 1)

def pose(t, S):
    f = fase(t); y_f = yf(t)
    # agujeros: el túnel de Atocha llega hasta YA (o hasta la tuneladora); el de Chamartín empieza en YB
    a1 = {"antes": YA, "pasa": y_f, "abre": y_f, "final": 16.6}[f]
    S["boreA"].location = (0, (-0.6 + a1) / 2, ZC); S["boreA"].scale = (1, 1, a1 + 0.6)
    if f == "final": S["boreB"].location = LEJOS
    else: S["boreB"].location = (0, (YB + 16.6) / 2, ZC); S["boreB"].scale = (1, 1, 16.6 - YB)
    hecho = lambda a0: a0 + 0.58 <= a1 + 0.05 or a0 >= YB - 0.05 or f == "final"
    nuevo = None
    for a0, o in S["anillos"]:
        detras = a0 + 0.58 <= a1 - LSH + 0.2 if f in ("pasa", "abre") else hecho(a0)
        o.hide_render = not (detras or a0 >= YB - 0.05)
        if f in ("pasa", "abre") and not o.hide_render and a0 < YB - 0.05: nuevo = a0
    if f in ("pasa", "abre") and nuevo is not None:
        u = (t * 1.3) % 1.0; S["nuevo"].location = (0, nuevo + 0.6, ZC + 0.5 * (1 - ss(u)))
    else: S["nuevo"].location = LEJOS
    for y0, o in S["losas"]: o.hide_render = not (y0 + 1.0 <= a1 - (LSH if f in ("pasa", "abre") else 0) or y0 >= YB - 0.3)
    for o in S["vias"]: o.hide_render = f != "final"
    # tuneladora
    if f in ("abre", "pasa"):
        pop = 1.0 if f == "abre" else back(min(1, (t - T("así que usas")) / 0.5))
        S["tbm"].location = (0, y_f, ZC); S["tbm"].scale = (max(pop, 0.01),) * 3
        S["rueda"].rotation_euler.x = t * 2.6
        for c in S["tbm"].children:
            if c is not S["rueda"]: c.hide_render = (y_f - c.location.x * pop) < -0.5
    else: S["tbm"].location = LEJOS
    # trenes de antes: el del sur llega a Atocha, el del norte a Chamartín
    if f == "antes":
        ys = keyed(t, [(T("madrid"), -3.0), (T("a atocha", fin=True) - 0.3, 2.3)])
        yn = keyed(t, [(T("los trenes"), 19.0), (T("a chamartín", fin=True) - 0.2, 13.7)])
        S["tsur"].location = (0, ys, ZD); S["tnorte"].location = (0, yn, ZD)
        for c in S["tsur"].children: c.hide_render = not (-0.4 < ys + c.location.y < YA)
        for c in S["tnorte"].children: c.hide_render = not (YB < yn + c.location.y < 16.4)
    else:
        S["tsur"].location = LEJOS; S["tnorte"].location = LEJOS
    # AVE: cruza entero (después de la revelación)
    if f == "final":
        if t > T("y los trenes") - 0.6: yy = -2.0 + ((t - T("y los trenes") + 0.6) * 3.4) % 23.0
        else: yy = -3.0 + ((t - T("y aquí viene")) * 2.0) % 23.0
        S["ave"].location = (0, yy, ZD); ver(S["ave"], True)
        for c in S["ave"].children: c.hide_render = not (-0.4 < yy + c.location.y < 16.4)
    else: S["ave"].location = LEJOS
    # coches por la calle
    for k, c in enumerate(S["coches"]):
        d = 1 if k % 2 else -1; yy = ((t * 1.3 + k * 4.1) % 16.6) - 0.3
        c.location = (0.55 if d > 0 else 1.45, yy if d > 0 else 16 - yy, 0.05)
    # viajero: tiene que cambiar de estación por la calle
    if T("así que,") - 0.1 < t < T("hay que") + 0.2:
        u = seg(t, T("para seguir"), T("de estación", fin=True))
        S["viajero"].location = (2.5, mix(2.6, 13.4, u), 0.1); S["viajero"].rotation_euler.z = 0
        S["viajero"].location.z = 0.1 + 0.03 * abs(math.sin(t * 9))
    else: S["viajero"].location = LEJOS
    # metro, colectores y cimientos: se resaltan cuando se nombran
    S["metro"].location = (-0.03 * win01(t, T("hay metro") - 0.1, T("hay metro") + 1.0), 0, 0)
    for o, a in ((S["metro"], T("hay metro")), (S["colect"], T("colectores")), (S["cimientos"], T("cimientos"))):
        u = win01(t, a - 0.1, a + 1.0, 0.2, 0.4)
        o.location = (-0.15 * u, 0, 0); o.scale = (1, 1 + 0.12 * u, 1 + 0.12 * u)
    # flecha hacia abajo (unirlas por debajo)
    if T("hay que") - 0.1 < t < T("pero bajo"):
        u = back(min(1, (t - T("hay que") + 0.1) / 0.5))
        S["fbaja"].location = (-0.3, 8.0, 2.4 - 0.4 * ((t * 1.5) % 1.0)); S["fbaja"].scale = (u + 0.01,) * 3
    else: S["fbaja"].location = LEJOS
    # flecha de profundidad (55 m) y edificio de 18 plantas boca abajo
    if T("así que bajas") - 0.1 < t < T("pero la tierra"):
        u = seg(t, T("así que bajas"), T("metros", 1, fin=True))
        S["fprof"].location = (-0.4, 8.0, 0.1); S["fprof"].scale = (1, 1, max(u, 0.01))
    else: S["fprof"].location = LEJOS
    if T("más hondo") - 0.1 < t < T("pero la tierra") + 0.2:
        u = back(min(1, (t - T("más hondo") + 0.1) / 0.6))
        S["edif18"].location = (4.6, -1.8, 0.0); S["edif18"].rotation_euler = (0, math.pi, 0); S["edif18"].scale = (1, 1, max(u, 0.01))
    else: S["edif18"].location = LEJOS
    # la calle no puede hundirse: tramo que baja con flechas y vuelve cuando llega la tuneladora
    hu = win01(t, T("pero la tierra") + 0.2, T("que sujeta"), 0.6, 0.8)
    S["hund"].location = (1.0, 8.0, 0.025 - 0.35 * hu) if hu > 0.01 else LEJOS
    for k, fl in enumerate(S["fcalle"]):
        if hu > 0.01:
            fl.location = (1.0, 7.2 + 0.8 * k, 1.6 - 0.3 * ((t * 1.6 + k * 0.3) % 1.0)); fl.scale = (hu,) * 3
        else: fl.location = LEJOS
    # presión de tierras: el frente empuja contra la tierra mientras excava
    pr = win01(t, T("que sujeta") - 0.3, T("y aquí viene"), 0.3, 0.3)
    for k, fl in enumerate(S["fpres"]):
        if pr > 0.01 and f == "pasa":
            fl.location = (0.25, y_f + 0.25 + 0.15 * math.sin(t * 7 + k), ZC + 0.7 - 0.7 * k); fl.scale = (pr * (0.8 + 0.2 * math.sin(t * 5 + k)),) * 3
        else: fl.location = LEJOS
    apply_cam(S["cam"], *cam_lin(t, CAM(), drift=0.03))

def CAM():
    k = Claves(); add = k.add
    ini = V((0.0, 8.8, ZC), (-2.5, -2.0, 0.6), 34)
    add(0.0, V((0.0, 8.4, ZC), (-2.3, -1.6, 0.3), 36)); add(1.8, ini)
    add(T("escribe"), V((0.8, 8.4, ZC + 0.3), (-4.5, -3.0, 1.6), 32))
    add(T("madrid") - 0.2, V((3.0, 8.0, -4.0), (-17.0, -12.0, 8.0), 26))
    add(T("los trenes") - 0.2, V((0.5, 1.5, ZC), (-6.0, -4.5, 2.2), 32), hold=1.95)
    add(T("los del norte") - 0.1, V((0.5, 14.5, ZC), (-6.0, 4.5, 2.2), 32), hold=1.4)
    add(T("pero no se"), V((1.0, 8.0, -4.0), (-15.0, -7.0, 3.5), 28))
    add(T("así que,") - 0.1, V((2.5, 5.0, 0.3), (-6.0, -6.0, 3.5), 32))
    add(T("de estación"), V((2.5, 11.0, 0.3), (-6.0, -5.0, 3.0), 32))
    add(T("hay que"), V((1.0, 8.0, -2.0), (-12.0, -9.0, 5.0), 28))
    add(T("hay metro") - 0.2, V((0.0, 8.0, -3.0), (-5.5, -2.0, 1.0), 32))
    add(T("colectores") - 0.1, V((0.0, 7.6, -1.6), (-5.0, -3.5, 1.4), 32))
    add(T("así que bajas") - 0.2, V((0.0, 8.0, -5.5), (-14.0, -5.0, 1.5), 28))
    add(T("hasta"), V((0.0, 8.0, -6.0), (-15.0, -7.0, 0.0), 28))
    add(T("más hondo") - 0.2, V((3.5, 0.0, -5.0), (-6.0, -17.0, 1.5), 28))
    add(T("pero la tierra"), V((1.0, 8.0, 0.0), (-6.0, -5.5, 3.5), 30))
    add(T("la calle no"), V((1.0, 8.0, 0.0), (-4.0, -4.0, 2.0), 34), hold=T("así que usas") - T("la calle no") - 0.5)
    add(T("así que usas") - 0.1, V((0.2, YA + 1.0, ZC), (-6.0, -4.0, 2.0), 30))
    add(T("de presión"), V((0.2, 5.5, ZC), (-4.5, -3.0, 1.6), 32))
    add(T("que sujeta"), V((0.2, 7.2, ZC), (-3.0, -1.2, 0.8), 36))
    add(T("y aquí viene"), V((1.5, 8.0, -4.0), (-17.0, -12.0, 6.0), 26))
    add(T("el túnel mide"), V((1.0, 8.0, -5.0), (-19.0, -7.0, 4.0), 26))
    add(T("y lleva"), V((0.4, 7.0, ZD), (-3.0, -2.5, 1.0), 36))
    add(T("lo abrieron"), V((3.5, 8.0, -1.0), (-13.0, -12.0, 7.0), 28))
    add(T("costó") - 0.1, V((1.5, 8.0, -4.0), (-15.0, -9.0, 5.0), 26))
    add(T("y los trenes"), V((0.4, 2.5, ZD), (-4.0, -2.0, 1.2), 32))
    add(T("como máximo"), V((0.4, 10.0, ZD), (-4.0, -2.5, 1.5), 32))
    add(T("ahora"), V((1.0, 8.0, -4.5), (-18.0, -6.0, 5.0), 26))
    add(T("ya no te"), V((0.5, 13.0, ZC), (-7.0, 1.0, 2.5), 30))
    add(T("te has acercado"), V((1.5, 8.0, -4.0), (-17.0, -12.0, 6.0), 26))
    add(T("dime en"), V((4.0, 4.0, 1.0), (-9.0, -8.0, 5.0), 28))
    add(T("y si quieres"), V((3.5, 13.0, 1.0), (-9.0, 6.0, 5.0), 28))
    add(T("lo más pedido"), V((1.0, 8.0, -4.0), (-17.0, -8.0, 4.0), 26))
    add(T("sígueme"), V((0.5, 8.0, ZC), (-6.0, -5.0, 2.0), 30))
    add(T("así que ya sabes") - 0.2, V((0.0, 8.4, ZC), (-2.3, -1.6, 0.3), 36))
    add(DUR - 0.8, ini)
    add(DUR + 1, ini)
    return k.k

def anchors(sc, S, t):
    cam = S["cam"]; P = lambda v: proj(sc, cam, v); y_f = yf(t)
    ave = S["ave"].location
    return {"rueda": P((0.0, y_f, ZC + RS)), "tunel": P((0.3, 8.0, ZC + RB)), "atocha": P((5.2, 1.4, 2.8)), "chamartin": P((5.2, 14.6, 2.3)),
            "metro": P((0.0, 8.0, -3.2)), "calle": P((1.0, 8.0, 0.4)), "fondo": P((-0.4, 8.0, ZC)), "medio": P((-0.4, 8.0, ZC / 2)),
            "edif_top": P((4.6, -1.8, 0.2)), "edif_fondo": P((4.6, -1.8, ZC)), "via": P((0.47, 7.0, ZD + 0.1)),
            "tren": P((0.47, ave.y + 0.5, ZD + 0.9)), "sur": P((0.4, 1.0, ZC + RB)), "norte": P((0.4, 15.0, ZC + RB))}

if __name__ == "__main__":
    run("tunelave", build, pose, anchors)
