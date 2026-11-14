# «¿A qué altura cuelga el puente de Vizcaya?» (Lo que esconde tu ciudad)
# Maqueta de la ría en corte: la isla va de x=-12 a 12 (Portugalete a la izquierda, Getxo a la derecha) y de y=0 a 8;
# la ría corre a lo largo de Y entre x=-6,5 y 6,5 y la cara delantera (y=0) enseña el agua, el fondo y las capas de tierra.
# Escala: 1 unidad = 10 m. Torres de hierro de 61 m (6,1) en x=±8, viga de 160 m (16) a 45 m sobre el agua (4,5),
# cables de suspensión a las torres y a los anclajes de tierra, carro con ruedas en la viga y barquilla colgada
# casi a ras del muelle (z=0,6) con 6 coches y la gente. Un barco grande sube la ría por debajo.
# Planos (fotografía → motion; esquina libre arriba-izquierda, que ocupa el mini del juego desde 2,6 s):
#  0,0 barquilla deslizándose en primer plano con un coche · 2,0 se abre · 4,7 Portugalete · 6,2 Getxo · 7,6 barco grande
#  10,2 puente normal altísimo · 13,6 rampas larguísimas · 16,7 maqueta vacía (1893) · 20,7 torres que suben · 24,5 viga
#  27,5 plano amplio · 29,2 revelación: altura de la viga · 32,7 edificio de 15 plantas al lado · 34,9 tú en el muelle
#  36,4 carriles · 38,3 barquilla · 40,1 cables · 43,3 coches y gente · 46,6 cruza · 48,4 barco por debajo · 51,8 UNESCO
#  54,8-63 cierre · 64 vuelta al primer plano de la barquilla.
import bpy, math, sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from modelos import *
from maqueta import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("transbordador")
XT = 8.0; HT = 6.1; ZV = 4.5; ZQ = 0.6; YP = 4.0; XR = 6.5      # torres, altura, viga, muelle, eje del puente, orilla
HIERRO = (0.72, 0.22, 0.20); HIERRO2 = (0.55, 0.16, 0.15); CABLE = (0.30, 0.31, 0.34); AGUA = PAL["agua"]
BX0, BX1 = -XR + 0.9, XR - 0.9                                     # recorrido de la barquilla

def back(x):
    x = max(0.0, min(1.0, x)); c = 1.70158; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

def construido(t):
    """0 = solo la ría (de «mil ochocientos» a «levanta»), 1 = puente entero"""
    return 0.0 if T("pero por la") - 0.2 < t < T("levanta") else 1.0

def torre_h(t):
    if T("pero por la") - 0.2 < t < T("levanta"): return 0.0
    if t < T("las une") and t > T("levanta") - 0.1: return seg(t, T("levanta"), T("de sesenta", fin=True) + 0.4)
    return 1.0

def viga_l(t):
    if T("pero por la") - 0.2 < t < T("las une"): return 0.0
    if T("las une") <= t < T("y aquí viene"): return seg(t, T("las une"), T("ciento sesenta", fin=True) + 0.5)
    return 1.0

def bx(t):
    """posición de la barquilla (x)"""
    a = T("cruza la"); b = T("los barcos pasan")
    if a - 0.1 < t < b + 3.0: return mix(BX0, BX1, seg(t, a, b + 2.5))
    return BX0 + 0.6 + 0.9 * math.sin(t * 0.35)

def build():
    sc, cam = scene_setup(world=PAL["cielo"], shadow=0.25); entorno_claro(sc)
    S = {"cam": cam}
    nubes(10, (0, 16, 10), 14, 2, 1.0, s=1.8, seed=3)
    # orillas (isla cortada) y ría
    for sx in (-1, 1):
        xc = sx * (XR + 2.75)
        for col, z0, g in ((PAL["cesped"], ZQ, 0.1), (PAL["tierra"], ZQ - 0.1, 1.2), (PAL["tierra2"], ZQ - 1.3, 1.5), ((0.60, 0.48, 0.38), ZQ - 2.8, 1.4)):
            box((5.5, 8, g), (xc, 4, z0 - g / 2), col)
        caja((0.3, 8, ZQ + 1.6), (sx * (XR + 0.15), 4, ZQ - 0.8), (0.80, 0.78, 0.74), r=0.03)       # muro del muelle
        caja((2.2, 8, 0.06), (sx * (XR + 1.4), 4, ZQ + 0.03), (0.86, 0.84, 0.80), r=0.01)         # paseo
    box((13.0, 8, 1.8), (0, 4, -0.9 - 0.02), AGUA)
    box((13.0, 8, 1.4), (0, 4, -1.8 - 0.7), PAL["tierra2"])
    box((13.0, 8, 0.25), (0, 4, -1.8 + 0.12), (0.78, 0.70, 0.52))                                    # fondo de arena
    S["olas"] = [caja((0.6, 0.06, 0.02), LEJOS, (0.85, 0.93, 1.0), r=0.01) for _ in range(14)]
    # pueblos: Portugalete (izquierda) y Getxo (derecha)
    cols = ((0.97, 0.86, 0.70), (0.93, 0.74, 0.62), (0.86, 0.90, 0.93), (0.98, 0.95, 0.88), (0.96, 0.80, 0.55))
    for k, (x, y, p) in enumerate(((-10.4, 6.2, 5), (-8.9, 6.6, 4), (-11.2, 3.0, 3), (-9.8, 1.6, 4), (10.2, 6.4, 4), (11.2, 3.4, 5), (9.5, 1.8, 3))):
        edificio((x, y, ZQ), pisos=p, s=0.6, color=cols[k % 5], ancho=1.5, fondo=1.4)
    for k in range(4): arbol((-7.2 - 0.0 * k, 0.8 + 1.9 * k, ZQ), 0.5, seed=k); arbol((7.2, 1.2 + 1.9 * k, ZQ), 0.5, seed=k + 9)
    for x in (-7.4, 7.4):
        for y in (2.2, 5.8): farola((x, y, ZQ), 0.5)
    S["gente"] = []
    for k in range(6):
        p = persona((-9.0 + 0.35 * k, 3.0 + 0.25 * (k % 3), ZQ), 0.22, ropa=((0.95, 0.55, 0.25), (0.25, 0.5, 0.85), (0.4, 0.75, 0.4))[k % 3])
        S["gente"].append(p)
    # torres (4 patas de celosía cada una), crecen desde el suelo
    S["torres"] = []
    for sx in (-1, 1):
        e = empty((sx * XT, YP, ZQ)); S["torres"].append(e)
        for py in (-1, 1):
            for px in (-1, 1):
                cilindro(0.09, HT, (px * 0.45, py * 0.55, HT / 2), HIERRO, e, r=0.03)
            for j in range(7):                                    # travesaños y cruces
                z = 0.4 + j * 0.85
                caja((0.95, 0.06, 0.06), (0, py * 0.55, z), HIERRO2, e, r=0.02)
                d = caja((1.15, 0.05, 0.05), (0, py * 0.55, z + 0.42), HIERRO2, e, r=0.015); d.rotation_euler = (0, 0.75 * (1 if j % 2 else -1), 0)
        for j in range(4): caja((0.06, 1.15, 0.06), (0, 0, 0.6 + j * 1.6), HIERRO2, e, r=0.02)
        caja((1.2, 1.4, 0.18), (0, 0, HT), HIERRO2, e, r=0.04)                       # cabeza de la torre
        caja((1.3, 1.5, 0.3), (0, 0, 0.15), (0.80, 0.78, 0.74), e, r=0.04)           # zócalo de piedra
    # viga de 160 m (se estira desde el centro) con carriles por debajo
    S["viga"] = empty((0, YP, ZV))
    caja((16.0, 0.9, 0.12), (0, 0, 0.35), HIERRO, S["viga"], r=0.03)
    caja((16.0, 0.9, 0.12), (0, 0, -0.05), HIERRO, S["viga"], r=0.03)
    for i in range(33):
        x = -8 + i * 0.5
        for py in (-0.42, 0.42):
            d = caja((0.55, 0.04, 0.04), (x + 0.25, py, 0.15), HIERRO2, S["viga"], r=0.01); d.rotation_euler = (0, 0.7 if i % 2 else -0.7, 0)
    S["carriles"] = [caja((16.0, 0.06, 0.05), (0, YP + py, ZV - 0.12), (0.62, 0.64, 0.68), r=0.01, unique=True) for py in (-0.25, 0.25)]
    # cables de suspensión: de la cabeza de cada torre a la viga y al anclaje en tierra
    S["cables"] = []
    for sx in (-1, 1):
        top = Vector((sx * XT, YP, ZQ + HT))
        for py in (-0.5, 0.5):
            pts = [(sx * 11.5, YP + py, ZQ + 0.1), (top.x, YP + py, top.z)]
            S["cables"].append(tubo(pts, 0.03, CABLE))
            for k in range(1, 6):
                xv = sx * (XT - k * 1.3)
                S["cables"].append(tubo([(top.x, YP + py, top.z), (xv, YP + py * 0.9, ZV + 0.35)], 0.022, CABLE))
    caja((0.6, 1.4, 0.4), (-11.5, YP, ZQ + 0.15), (0.72, 0.72, 0.70), r=0.05); caja((0.6, 1.4, 0.4), (11.5, YP, ZQ + 0.15), (0.72, 0.72, 0.70), r=0.05)
    # carro, cables colgantes y barquilla
    S["carro"] = empty(LEJOS)
    caja((1.6, 0.8, 0.18), (0, 0, 0), (0.35, 0.36, 0.40), S["carro"], r=0.04)
    for i in range(4):
        for py in (-0.25, 0.25): cilindro(0.08, 0.05, (-0.6 + 0.4 * i, py, 0.1), (0.2, 0.2, 0.22), S["carro"], rot=(math.pi / 2, 0, 0), r=0.01)
    S["hilos"] = [cyl(0.018, 1.0, LEJOS, CABLE, v=8, unique=True) for _ in range(8)]
    S["barq"] = empty(LEJOS)
    caja((3.0, 1.5, 0.12), (0, 0, 0), (0.86, 0.84, 0.80), S["barq"], r=0.04)                 # plataforma
    caja((3.0, 0.08, 0.35), (0, -0.72, 0.2), (0.30, 0.50, 0.75), S["barq"], r=0.02)           # barandillas
    caja((3.0, 0.08, 0.35), (0, 0.72, 0.2), (0.30, 0.50, 0.75), S["barq"], r=0.02)
    for sx in (-1, 1):
        caja((0.5, 1.5, 0.9), (sx * 1.25, 0, 0.5), (0.95, 0.95, 0.93), S["barq"], r=0.05)     # casetas de pasajeros
        caja((0.52, 1.0, 0.25), (sx * 1.25, 0, 0.65), (0.62, 0.82, 0.95), S["barq"], r=0.03)
        caja((0.6, 1.6, 0.06), (sx * 1.25, 0, 0.98), (0.72, 0.22, 0.20), S["barq"], r=0.02)
    caja((0.3, 1.5, 0.08), (0, 0, 2.0), (0.35, 0.36, 0.40), S["barq"], r=0.03)               # cuadro de suspensión
    S["bcoches"] = []
    for k, c in enumerate((PAL["rojo"], (0.2, 0.45, 0.85), PAL["amarillo"], (0.95, 0.95, 0.95), (0.35, 0.7, 0.4), (0.9, 0.5, 0.2))):
        cc = coche(LEJOS, 0.3, color=c); S["bcoches"].append(cc)
    S["bgente"] = [persona(LEJOS, 0.22, ropa=((0.95, 0.55, 0.25), (0.25, 0.5, 0.85), (0.9, 0.3, 0.5))[k % 3]) for k in range(6)]
    # barco grande
    S["barco"] = empty(LEJOS)
    caja((1.6, 5.0, 0.8), (0, 0, 0.2), (0.25, 0.30, 0.45), S["barco"], r=0.25)
    caja((1.62, 5.0, 0.15), (0, 0, -0.1), PAL["rojo"], S["barco"], r=0.05)
    caja((1.3, 1.2, 1.0), (0, 1.6, 1.0), (0.97, 0.97, 0.97), S["barco"], r=0.08)
    for k in range(3): caja((0.6, 0.55, 0.45), (0.0, -1.6 + 0.65 * k, 0.83), ((0.95, 0.6, 0.2), (0.3, 0.6, 0.9), (0.4, 0.75, 0.4))[k], S["barco"], r=0.04)
    cilindro(0.18, 0.7, (0, 1.6, 1.8), PAL["amarillo"], S["barco"], r=0.04)
    # puente «normal» y rampas (fantasmas que aparecen y se van)
    S["alto"] = empty(LEJOS)
    for sx in (-1, 1): caja((0.5, 1.0, 9.0), (sx * 5.5, 0, 4.5), (0.85, 0.85, 0.83), S["alto"], r=0.05)
    caja((13.0, 1.2, 0.35), (0, 0, 9.0), (0.85, 0.85, 0.83), S["alto"], r=0.05)
    S["rampas"] = []
    for sx in (-1, 1):
        r_ = empty(LEJOS); caja((14.0, 1.2, 0.3), (sx * 7.0, 0, 0), (0.85, 0.85, 0.83), r_, r=0.05); S["rampas"].append(r_)
    S["edif15"] = edificio(LEJOS, pisos=15, s=0.71, color=(0.86, 0.90, 0.95), ancho=1.4, fondo=1.2)
    S["fmuelle"] = flecha3d(LEJOS, (1, 0, 0), 1.2, 0.08)
    S["rayas"] = [caja((0.1, 0.1, 0.02), LEJOS, PAL["amarillo"]) for _ in range(9)]               # regla de altura
    S["regla"] = box((0.06, 0.06, 1.0), LEJOS, PAL["amarillo"], unique=True)
    dyn = [cam, S["olas"], S["gente"], S["torres"], S["viga"], S["carriles"], S["cables"], S["carro"], S["hilos"], S["barq"], S["bcoches"],
           S["bgente"], S["barco"], S["alto"], S["rampas"], S["edif15"], S["fmuelle"], S["rayas"], S["regla"]]
    join_static(dyn)
    return sc, S

def ver(o, on):
    o.hide_render = not on
    for c in o.children_recursive: c.hide_render = not on

def pose(t, S):
    th = torre_h(t); vl = viga_l(t)
    for e in S["torres"]: e.scale = (1, 1, max(th, 0.001)); ver(e, th > 0.01)
    S["viga"].scale = (max(vl, 0.001), 1, 1); ver(S["viga"], vl > 0.01)
    car = 1.0 if t < T("pero por la") - 0.2 or t > T("de la viga cuelgan") - 0.1 else seg(t, T("de la viga cuelgan"), T("carriles", fin=True))
    car = 0.0 if T("pero por la") - 0.2 < t < T("de la viga cuelgan") - 0.1 else car
    for c in S["carriles"]: c.scale = (max(car, 0.001), 1, 1); c.hide_render = car < 0.01
    full = th > 0.99 and vl > 0.99
    for c in S["cables"]: c.hide_render = not full or (T("las une") - 0.1 < t < T("y aquí viene"))
    # barquilla, carro e hilos
    barca = car > 0.99 and (t < T("pero por la") - 0.2 or t > T("y por ellos") - 0.1)
    x = bx(t)
    if barca:
        pop = 1.0 if t < 20 or t > T("y por ellos") + 0.5 else back((t - T("y por ellos") + 0.1) / 0.6)
        S["carro"].location = (x, YP, ZV - 0.25); S["barq"].location = (x, YP, ZQ + 0.12 + 0.03 * math.sin(t * 1.7))
        S["barq"].scale = (pop,) * 3
        hil = 1.0 if t < 20 or t > T("va colgada") else seg(t, T("y por ellos"), T("va colgada"))
        for k, h in enumerate(S["hilos"]):
            px = -1.3 + (k % 4) * 0.87; py = -0.6 if k < 4 else 0.6
            top = ZV - 0.3; bot = ZQ + 0.12 + 2.0 * (1 - hil) + 0.2
            h.location = (x + px * 0.6, YP + py * 0.5, (top + bot) / 2); h.scale = (1, 1, max(top - bot, 0.01))
            h.rotation_euler = (math.atan2(py * 0.5 - py * 0.9, top - bot) * 0, 0, 0)
    else:
        S["carro"].location = LEJOS; S["barq"].location = LEJOS
        for h in S["hilos"]: h.location = LEJOS
    # coches y gente en la barquilla: entran cuando la voz lo dice (y van siempre en el bucle)
    nc = 6 if (t < 20 or t > T("doscientos") + 0.6) else int(round(6 * seg(t, T("caben"), T("seis coches", fin=True) + 0.4)))
    if t < 2.5: nc = 2
    for k, c in enumerate(S["bcoches"]):
        if barca and k < nc:
            c.location = (S["barq"].location.x - 0.9 + 0.6 * (k % 3) + 0.0, YP - 0.35 + 0.7 * (k // 3), S["barq"].location.z + 0.06)
        else: c.location = LEJOS
    ng = 6 if (t < 20 or t > T("doscientos") + 0.6) else int(round(6 * seg(t, T("doscientos"), T("pasajeros", fin=True))))
    for k, p in enumerate(S["bgente"]):
        if barca and k < ng:
            sx = -1 if k < 3 else 1
            p.location = (S["barq"].location.x + sx * (1.1 + 0.15 * (k % 3)), YP - 0.5 + 0.45 * (k % 3), S["barq"].location.z + 0.06)
        else: p.location = LEJOS
    # olas
    for k, o in enumerate(S["olas"]):
        u = (t * 0.25 + k * 0.137) % 1.0
        o.location = (-5.5 + (k * 0.83) % 11.0, 0.4 + u * 7.2, 0.012)
    # barco grande: sube la ría (al principio y cuando pasa por debajo del puente)
    bt = None
    if T("pero por la") - 0.3 < t < T("así que un") + 0.3: bt = seg(t, T("pero por la") - 0.3, T("así que un") + 0.3)
    if T("los barcos pasan") - 0.3 < t < T("en dos mil") + 0.6: bt = seg(t, T("los barcos pasan") - 0.3, T("en dos mil") + 0.6)
    if T("pero entonces") - 0.1 < t < T("así que alberto"): bt = 0.75
    if bt is not None:
        S["barco"].location = (0.5, mix(1.5, 10.5, bt), 0.0)
        for c in S["barco"].children: c.hide_render = not (0.2 < S["barco"].location.y + c.location.y < 7.8)
    else: S["barco"].location = LEJOS
    # puente normal altísimo y rampas larguísimas (fantasmas)
    al = win01(t, T("así que un") - 0.1, T("así que alberto") - 0.2, 0.4, 0.3)
    S["alto"].location = (0, 1.4, ZQ) if al > 0.01 else LEJOS; S["alto"].scale = (1, 1, max(back(al), 0.01))
    ra = win01(t, T("pero entonces") - 0.1, T("así que alberto") - 0.2, 0.3, 0.3)
    for sx, r_ in zip((-1, 1), S["rampas"]):
        if ra > 0.01:
            u = seg(t, T("rampas"), T("larguísimas", fin=True))
            r_.location = (sx * (6.5 + 0.0), 1.4, ZQ + 4.5); r_.rotation_euler = (0, sx * math.radians(mix(55, 22, u)), 0)
            r_.scale = (max(ra * mix(0.6, 1.3, u), 0.01), 1, 1)
        else: r_.location = LEJOS
    # regla de altura (de 0 a 45 m) y edificio de 15 plantas
    rg = win01(t, T("la viga cuelga") - 0.1, T("pero tú") + 0.1, 0.3, 0.3)
    if rg > 0.01:
        u = seg(t, T("a cuarenta"), T("sobre el agua", fin=True))
        h = max(ZV * u, 0.01)
        S["regla"].location = (2.2, YP - 0.6, h / 2); S["regla"].scale = (1, 1, h)
        for k, r_ in enumerate(S["rayas"]):
            z = k * 0.5
            r_.location = (2.2, YP - 0.6, z) if z <= h else LEJOS
    else:
        S["regla"].location = LEJOS
        for r_ in S["rayas"]: r_.location = LEJOS
    ed = win01(t, T("como un edificio") - 0.1, T("pero tú") + 0.2, 0.2, 0.3)
    S["edif15"].location = (3.6, YP + 0.2, 0.0) if ed > 0.01 else LEJOS; S["edif15"].scale = (1, 1, max(back(ed), 0.01))
    # flecha «tú tienes que cruzar»
    fm = win01(t, T("pero tú") - 0.1, T("así que de la"), 0.2, 0.3)
    S["fmuelle"].location = (-6.4, YP, ZQ + 0.5) if fm > 0.01 else LEJOS; S["fmuelle"].scale = (fm + 0.01,) * 3
    apply_cam(S["cam"], *cam_lin(t, CAM(), drift=0.03))

def CAM():
    k = Claves(); add = k.add
    ini = V((BX0 + 0.6, YP, ZQ + 0.8), (-2.2, -4.0, 0.9), 34)
    add(0.0, V((BX0 + 0.4, YP, ZQ + 0.7), (-1.6, -3.0, 0.5), 36)); add(1.8, ini)
    add(T("escribe"), V((0.0, YP, 2.8), (-6.0, -16.0, 4.5), 26))
    add(T("portugalete"), V((-9.5, 3.5, ZQ + 0.8), (2.0, -7.0, 3.0), 30))
    add(T("a cada lado"), V((9.5, 3.5, ZQ + 0.8), (-2.0, -7.0, 3.0), 30))
    add(T("pero por la") - 0.1, V((0.5, 3.0, 0.5), (-4.0, -9.0, 3.0), 30))
    add(T("así que un") - 0.1, V((0.0, 1.4, 5.0), (-2.0, -15.0, 1.0), 26))
    add(T("altísimo") - 0.2, V((5.5, 1.4, 4.5), (-1.5, -13.0, 0.5), 28))
    add(T("pero entonces"), V((7.0, 1.4, 3.0), (2.0, -12.0, 2.0), 26))
    add(T("así que alberto") - 0.2, V((-9.0, 3.0, 1.0), (3.0, -6.0, 2.5), 30))
    add(T("levanta"), V((-8.0, YP, 3.0), (5.0, -10.0, 1.5), 30))
    add(T("de sesenta"), V((-8.0, YP, 3.5), (4.0, -8.0, 2.5), 30))
    add(T("las une"), V((0.0, YP, 3.5), (2.0, -18.0, 3.0), 24))
    add(T("y aquí viene"), V((0.0, YP, 3.0), (-8.0, -20.0, 4.0), 24))
    add(T("la viga cuelga"), V((2.2, YP, 2.4), (-5.0, -9.5, 1.0), 28))
    add(T("como un edificio"), V((3.4, YP, 2.4), (1.5, -11.5, 1.2), 26))
    add(T("pero tú"), V((-7.0, YP, ZQ + 0.6), (-3.0, -4.0, 1.2), 32))
    add(T("así que de la"), V((0.0, YP, ZV - 0.2), (-3.0, -5.0, -0.8), 30))
    add(T("y por ellos"), V((BX0 + 0.4, YP, 2.4), (-3.0, -6.0, 0.6), 30))
    add(T("va colgada"), V((BX0 + 0.4, YP, 3.2), (2.8, -5.5, -0.5), 30))
    add(T("casi a ras"), V((BX0 + 0.6, YP, ZQ + 0.4), (0.8, -3.6, 0.5), 34))
    add(T("caben"), V((BX0 + 0.5, YP, ZQ + 0.3), (0.6, -2.8, 1.4), 34))
    add(T("cruza la"), V((-1.5, YP, 1.0), (0.5, -8.0, 1.6), 30))
    add(T("los barcos pasan"), V((1.0, 3.0, 1.5), (-5.0, -10.0, 1.0), 28))
    add(T("sin enterarse"), V((1.5, YP, 2.0), (6.0, -9.0, 1.0), 28))
    add(T("en dos mil"), V((0.0, YP, 3.0), (-7.0, -21.0, 5.0), 24))
    add(T("te has acercado"), V((0.0, YP, 3.0), (6.0, -20.0, 3.0), 24))
    add(T("dime en"), V((-9.5, 3.5, ZQ + 1.0), (3.0, -8.0, 3.5), 28))
    add(T("y si quieres"), V((9.5, 3.5, ZQ + 1.0), (-3.0, -8.0, 3.5), 28))
    add(T("lo más pedido"), V((0.0, YP, 3.0), (-6.0, -20.0, 3.0), 24))
    add(T("sígueme"), V((0.0, YP, 2.0), (-4.0, -11.0, 2.0), 28))
    add(T("así que ya sabes") - 0.2, V((BX0 + 0.4, YP, ZQ + 0.7), (-1.6, -3.0, 0.5), 36))
    add(DUR - 0.8, ini)
    add(DUR + 1, ini)
    return k.k

def anchors(sc, S, t):
    cam = S["cam"]; P = lambda v: proj(sc, cam, v); x = bx(t)
    return {"barq": P((x, YP, ZQ + 1.4)), "torre": P((-XT, YP, ZQ + HT + 0.3)), "viga": P((0.0, YP, ZV + 0.6)), "regla": P((2.2, YP, ZV)),
            "edif": P((3.6, YP, 11.0 * 0.71 * 0.42 + 0.5)), "porto": P((-9.5, 3.5, ZQ + 2.6)), "getxo": P((9.5, 3.5, ZQ + 2.6)),
            "barco": P((0.5, 4.0, 2.0)), "alto": P((0.0, 1.4, ZQ + 9.4)), "agua": P((0.0, 0.0, 0.0)), "carril": P((0.0, YP, ZV - 0.12))}

if __name__ == "__main__":
    run("transbordador", build, pose, anchors)
