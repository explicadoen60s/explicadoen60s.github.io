# «¿Cuántos kilómetros de tubos llevan el agua a tu grifo en Madrid?» (Lo que esconde tu ciudad): maqueta de día sobre una isla
# de terreno. A la izquierda la sierra (río Lozoya, presa y embalse, 12 presas pequeñas más), en medio la potabilizadora y el canal,
# a la derecha la ciudad con un corte delante que enseña el depósito enterrado, las tuberías bajo la calle y la cocina con el grifo.
# El globo con los tubos en fila hasta Australia flota en el cielo, detrás de la maqueta.
# Planos (fotografía → motion; esquina libre arriba-izquierda salvo que se diga):
#  0,0 grifo en primer plano, la maneta se levanta y sale el chorro · 1,8 fregadero y chorro · 3,3 cocina y corte (tarjeta arriba)
#  5,9 tuberías en el corte · 8,1 maqueta entera · 10,2 sierra (1858) · 12,8 río Lozoya · 15,4 presa que sube · 17,7 trece presas
# 18,7 embalse que se llena y flechas de presión · 21,1 agua turbia · 23,6 canal a la potabilizadora · 26,6 depósitos que filtran
# 28,7 canal · 30,2 llega a la ciudad · 31,4 ciudad pide agua · 33,9 sol de mañana · 35,0 cena · 36,3 depósito en corte
# 39,6 300 depósitos · 42,2 Bravo Murillo · 44,0 se llena (180.000 m³) · 46,3 tubería · 47,8 subida a la cocina
# 49,4 globo · 51,3 tubo hacia Australia · 53,5 Australia · 55,9 ciudad con gente · 59,0 vuelta · 59,9 maqueta entera
# 62,2 corte · 64,0 cocina · 65,4 grifo · 67,1 mismo plano que el primero (bucle).
import bpy, math, sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from modelos import *
from maqueta import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("canalmadrid")
AGUA = PAL["agua"]; TURBIA = (0.55, 0.58, 0.38); LAGO = (0.36, 0.62, 0.70); HORM = PAL["hormigon"]; TUBO = (0.62, 0.66, 0.72)
G = Vector((2.5, 12.0, 5.2)); GR = 2.2
GRIFO = Vector((6.75, -3.12, 0.50))
CANAL1 = [(-4.1, -1.9), (-2.9, -2.05), (-2.45, -1.45)]
CANAL2 = [(-0.55, -1.25), (-0.3, -2.2), (0.1, -3.3)]
CANAL1_3 = poly([(x, y, 0.06) for x, y in CANAL1]); CANAL2_3 = poly([(x, y, 0.06) for x, y in CANAL2])
RED = [(2.7, -3.5, -0.55), (6.75, -3.5, -0.55), (6.75, -3.5, -0.15)]
RED3 = poly(RED)
TANQUES = [(-2.2, -1.2), (-1.55, -1.2), (-0.9, -1.2)]

def unit(color, unique=False): return box((1, 1, 1), LEJOS, color, unique=unique)

def strip(o, a, b, w, h, z0=0.0, frac=1.0):
    a, b = Vector((a[0], a[1], 0)), Vector((b[0], b[1], 0)); d = b - a; L = d.length
    f = max(0.0, min(1.0, frac))
    if f < 1e-3 or h < 1e-4: o.hide_render = True; return
    o.hide_render = False; Lv = L * f + w * 0.5
    o.location = a + d.normalized() * (Lv / 2 - w * 0.25) + Vector((0, 0, z0 + h / 2))
    o.rotation_euler = (0, 0, math.atan2(d.y, d.x)); o.scale = (Lv, w, h)

def gp(lat, lon, r=1.0):
    la, lo = math.radians(lat), math.radians(lon - 65)
    return Vector((math.cos(la) * math.sin(lo), -math.cos(la) * math.cos(lo), math.sin(la))) * r

def montana(loc, r, h, seed=0):
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=r, depth=h, location=(loc[0], loc[1], h / 2), rotation=(0, 0, seed))
    setup(bpy.context.object, (0.52, 0.62, 0.48))
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=r * 0.32, depth=h * 0.32, location=(loc[0], loc[1], h * 0.84 + 0.01), rotation=(0, 0, seed))
    setup(bpy.context.object, (0.98, 0.98, 1.0))

def build():
    sc, cam = scene_setup(world=PAL["cielo"], shadow=0.25); entorno_claro(sc)
    S = {"cam": cam}
    nubes(9, (0, 16, 4.5), 11, 1.6, 1.0, s=1.5, seed=3)
    nubes(4, (-9, 6, 4.0), 2, 1.0, 2.0, s=1.2, seed=21)
    # ---- isla con el corte delante de la ciudad ----
    cut = cortador((7.4, 1.2, 1.6), (3.9, -3.6, -0.95))
    capas = []
    z = 0.0
    for col, g in ((PAL["cesped"], 0.12), (PAL["tierra"], 1.0), (PAL["tierra2"], 0.9)):
        o = box((16.0, 8.0, g), (0, 0, z - g / 2), col); cortar(o, cut); capas.append(o); z -= g
    # ---- sierra ----
    for i, (x, y, r, h) in enumerate([(-7.5, 3.45, 0.55, 1.6), (-6.6, 3.55, 0.65, 2.1), (-5.6, 3.4, 0.5, 1.5), (-4.7, 3.55, 0.7, 2.3),
                                      (-3.7, 3.45, 0.55, 1.7), (-2.8, 3.6, 0.45, 1.2)]):
        montana((x, y), r, h, seed=i)
    bola(1.0, (-7.4, -0.5, 0), (0.50, 0.70, 0.40), escala=(0.65, 1.3, 0.75))
    bola(1.0, (-3.2, -0.5, 0), (0.50, 0.70, 0.40), escala=(0.6, 1.3, 0.75))
    bola(1.0, (-6.6, 0.9, 0), (0.50, 0.70, 0.40), escala=(1.1, 0.45, 0.6))
    bola(1.0, (-4.3, 0.9, 0), (0.50, 0.70, 0.40), escala=(1.0, 0.45, 0.6))
    caja((0.2, 2.8, 0.03), (-5.4, 2.0, 0.02), AGUA, r=0.01)                                 # río Lozoya
    caja((3.0, 2.3, 0.01), (-5.3, -0.5, 0.004), (0.62, 0.55, 0.40), r=0.003)                   # fondo del valle
    S["lago"] = box((3.0, 2.2, 1.0), LEJOS, LAGO, unique=True)
    S["presa"] = caja((3.2, 0.22, 0.55), (-5.3, -1.71, 0.275), HORM, unique=True)
    caja((3.3, 0.06, 0.05), (-5.3, -1.84, 0.02), (0.6, 0.6, 0.62))
    S["fp"] = [flecha3d(LEJOS, (0, -1, 0), 0.6, 0.05) for _ in range(3)]
    S["minis"] = []
    k = 0
    for y in (1.75, 2.35, 2.95):
        for x in (-7.5, -6.7, -4.6, -3.8):
            e = empty(LEJOS); cilindro(0.26, 0.04, (0, 0, 0.02), LAGO, e); caja((0.5, 0.07, 0.16), (0, -0.27, 0.08), HORM, e)
            S["minis"].append((e, (x, y))); k += 1
    for i in range(10):
        r = random.Random(i); arbol((r.uniform(-7.8, -2.6), r.uniform(-3.8, -2.2), 0), 0.45, seed=i)
    # ---- potabilizadora ----
    caja((1.2, 0.7, 0.5), (-1.4, -0.25, 0.25), (0.98, 0.98, 0.98))
    caja((1.26, 0.76, 0.06), (-1.4, -0.25, 0.52), (0.30, 0.55, 0.85))
    for x in (-1.75, -1.4, -1.05): ventana((x, -0.61, 0.3), 0.6)
    S["tq"] = []; S["burb"] = []
    for x, y in TANQUES:
        cilindro(0.3, 0.3, (x, y, 0.15), HORM)
        cilindro(0.24, 0.02, (x, y, 0.295), (0.55, 0.5, 0.45))
        S["tq"].append(cilindro(0.245, 0.03, LEJOS, TURBIA, unique=True))
        S["burb"] += [sph(0.025, LEJOS, (1, 1, 1), seg=8) for _ in range(5)]
    for (x0, y0), (x1, y1) in zip(TANQUES, TANQUES[1:]):
        tubo([(x0 + 0.28, y0, 0.2), (x1 - 0.28, y1, 0.2)], 0.05, TUBO)
    # ---- canales ----
    S["c1"], S["c2"] = [], []
    for pts, lst in ((CANAL1, S["c1"]), (CANAL2, S["c2"])):
        for a, b in zip(pts, pts[1:]):
            o = unit((0.80, 0.80, 0.78)); strip(o, a, b, 0.32, 0.05, 0.0)
            lst.append(unit(AGUA))
    S["fc"] = [flecha3d(LEJOS, (1, 0, 0), 0.45, 0.04) for _ in range(2)]
    S["pc"] = [sph(0.03, LEJOS, (0.88, 0.95, 1.0), seg=8) for _ in range(10)]
    # ---- ciudad ----
    rnd = random.Random(5); cols = [PAL["pared"], PAL["rosa"], (0.98, 0.85, 0.55), (0.75, 0.85, 0.95), (0.95, 0.7, 0.5), (0.85, 0.92, 0.8)]
    for x in (1.5, 2.5, 3.5, 4.5, 5.5, 6.5):
        caja((0.26, 6.2, 0.02), (x, 0.6, 0.012), PAL["asfalto"], r=0.004)
    for y in (-1.4, -0.4, 0.6, 1.6, 2.6):
        caja((7.2, 0.26, 0.022), (4.1, y, 0.013), PAL["asfalto"], r=0.004)
    for x in (1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0):
        for y in (-1.9, -0.9, 0.1, 1.1, 2.1, 3.1):
            if x <= 2.0 and y < -1.0:
                for k in range(3): arbol((x + rnd.uniform(-0.3, 0.3), y + rnd.uniform(-0.3, 0.3), 0), 0.38, seed=k + int(x * 10))
                continue
            u = rnd.random(); c = rnd.choice(cols); giro = rnd.choice((0, math.pi / 2, math.pi, -math.pi / 2))
            if u < 0.22: casa((x, y, 0), 0.38, pared=c, rot=giro)
            elif u < 0.3: arbol((x, y, 0), 0.4, seed=int(x * 7 + y * 3))
            else: edificio((x, y, 0), pisos=rnd.randint(3, 7), s=0.42, color=c, rot=giro, ancho=1.5, fondo=1.4)
    calle(5.4, (2.9, -3.3, 0), ancho=0.5)
    S["drops"] = [sph(0.1, LEJOS, AGUA, seg=10) for _ in range(10)]
    S["marks"] = []
    pos = [(x, y) for x in (1.5, 2.5, 3.5, 4.5, 5.5, 6.5) for y in (-0.4, 0.6, 1.6, 2.6)] + [(-1.0, 1.5), (-2.0, 1.8), (0.3, 0.8), (-0.4, 2.6)]
    for x, y in pos:
        e = empty(LEJOS); cilindro(0.15, 0.06, (0, 0, 0.03), (0.22, 0.52, 0.92), e); cilindro(0.09, 0.02, (0, 0, 0.07), (0.85, 0.9, 0.98), e)
        S["marks"].append((e, (x, y)))
    S["gente"] = []
    rr = random.Random(9)
    for k in range(24):
        x = rr.choice((1.5, 2.5, 3.5, 4.5, 5.5, 6.5)) + rr.uniform(-0.08, 0.08); y = rr.uniform(-1.8, 3.4)
        if k % 2: x, y = rr.uniform(0.8, 7.2), rr.choice((-1.4, -0.4, 0.6, 1.6, 2.6)) + rr.uniform(-0.08, 0.08)
        e = empty(LEJOS); persona((0, 0, 0), 0.3, parent=e, ropa=rr.choice([(0.25, 0.5, 0.85), PAL["rojo"], PAL["amarillo"], (0.3, 0.7, 0.4)]))
        S["gente"].append((e, (x, y)))
    S["sol"] = sph(0.6, LEJOS, (1.0, 0.86, 0.3), seg=16)
    # ---- depósito enterrado en el corte ----
    caja((2.2, 0.9, 0.08), (1.6, -3.5, -1.61), HORM)
    caja((2.2, 0.08, 1.4), (1.6, -3.05, -0.95), HORM)
    for x in (0.5, 2.7): caja((0.08, 0.9, 1.4), (x, -3.5, -0.95), HORM)
    caja((2.3, 0.95, 0.08), (1.6, -3.5, -0.25), HORM)
    for x in (1.05, 1.6, 2.15): cilindro(0.06, 1.3, (x, -3.45, -0.93), (0.86, 0.86, 0.84))
    for (sx, sy, sz, lx, lz) in ((2.3, 0.03, 0.05, 1.6, -0.21), (2.3, 0.03, 0.05, 1.6, -1.65), (0.05, 0.03, 1.45, 0.47, -0.93), (0.05, 0.03, 1.45, 2.73, -0.93)):
        caja((sx, sy, sz), (lx, -3.96, lz), PAL["corte"], r=0.005)
    S["dep"] = box((2.1, 0.8, 1.0), LEJOS, AGUA, unique=True)
    # ---- tuberías bajo la calle (medio tubo: se ve el agua dentro) ----
    medio_tubo(RED, 0.075, 0.02, TUBO); tubo(RED, 0.045, AGUA, tapas=True)
    medio_tubo([(0.2, -3.5, -0.6), (0.5, -3.5, -0.6)], 0.075, 0.02, TUBO); tubo([(0.2, -3.5, -0.6), (0.5, -3.5, -0.6)], 0.045, AGUA, tapas=True)
    for x in (3.5, 4.6, 5.5):
        pts = [(x, -3.5, -0.55), (x, -3.5, -0.15)]; medio_tubo(pts, 0.05, 0.015, TUBO); tubo(pts, 0.03, AGUA, tapas=True)
    S["pt"] = [sph(0.028, LEJOS, (0.9, 0.97, 1.0), seg=8) for _ in range(16)]
    S["ft"] = flecha3d(LEJOS, (1, 0, 0), 0.5, 0.04)
    S["fu"] = flecha3d(LEJOS, (0, 0, 1), 0.3, 0.03)
    # ---- cocina en corte con el grifo ----
    caja((1.8, 1.0, 0.04), (6.75, -3.45, 0.02), PAL["madera"])
    azulejos(1.8, 1.0, (6.75, -2.93, 0.54), color=PAL["menta"], paso=0.12, junta=0.008)
    for x in (5.85, 7.65): caja((0.06, 1.05, 1.06), (x, -3.45, 0.53), PAL["pared"])
    caja((1.9, 1.1, 0.06), (6.75, -3.45, 1.08), PAL["pared"])
    caja((1.2, 0.36, 0.36), (6.75, -3.13, 0.2), (0.45, 0.62, 0.86))
    for x in (6.45, 7.05): caja((0.56, 0.02, 0.3), (x, -3.32, 0.2), (0.52, 0.69, 0.91), r=0.01); caja((0.08, 0.02, 0.015), (x, -3.34, 0.32), (0.85, 0.86, 0.88), r=0.004)
    caja((1.26, 0.4, 0.04), (6.75, -3.13, 0.4), PAL["encimera"])
    caja((0.46, 0.28, 0.012), (6.75, -3.18, 0.422), (0.80, 0.82, 0.86), r=0.004)
    caja((0.40, 0.22, 0.008), (6.75, -3.18, 0.428), (0.55, 0.58, 0.63), r=0.003)
    planta((7.2, -3.05, 0.42), 0.35); planta((6.25, -3.03, 0.42), 0.25, maceta=PAL["rosa"])
    cilindro(0.025, 0.14, (6.75, -3.02, 0.49), (0.82, 0.84, 0.88), r=0.008)
    cilindro(0.015, 0.13, (6.75, -3.08, 0.555), (0.82, 0.84, 0.88), rot=(math.pi / 2, 0, 0), r=0.005)
    cilindro(0.017, 0.03, (6.75, -3.14, 0.545), (0.82, 0.84, 0.88), r=0.005)
    S["maneta"] = empty((6.75, -3.02, 0.565))
    caja((0.022, 0.1, 0.016), (0, 0.045, 0.006), (0.82, 0.84, 0.88), S["maneta"], r=0.006)
    S["chorro"] = bar_obj((0.55, 0.80, 1.0), 0.011)
    S["salp"] = [sph(0.008, LEJOS, (0.7, 0.88, 1.0), seg=8) for _ in range(6)]
    # ---- globo con los tubos en fila ----
    S["globo"] = empty(LEJOS)
    sph(GR, (0, 0, 0), (0.30, 0.58, 0.92), parent=S["globo"], seg=40)
    for lat, lon, r in ((50, 15, .55), (40, -4, .35), (60, 30, .5), (5, 20, .8), (-15, 25, .6), (50, 90, .95), (35, 70, .6), (20, 78, .4),
                        (12, 103, .35), (-25, 134, .55), (23, 47, .38), (62, 110, .7)):
        bola(r * 0.68, tuple(gp(lat, lon, GR - r * 0.45)), (0.42, 0.74, 0.36), S["globo"])
    S["pins"] = [sph(0.11, tuple(gp(40, -4, GR * 1.03)), PAL["rojo"], S["globo"]), sph(0.11, tuple(gp(-25, 134, GR * 1.03)), PAL["amarillo"], S["globo"])]
    A, B = gp(40, -4), gp(-25, 134)
    S["arc"] = [A.slerp(B, i / 40) * GR * 1.035 for i in range(41)]
    S["seg"] = [bar_obj((0.92, 0.93, 0.95), 0.075, parent=S["globo"]) for _ in range(40)]
    dyn = [cam, capas, cut, S["lago"], S["presa"], S["fp"], [e for e, _ in S["minis"]], S["tq"], S["burb"], S["c1"], S["c2"], S["fc"], S["pc"],
           S["drops"], [e for e, _ in S["marks"]], [e for e, _ in S["gente"]], S["sol"], S["dep"], S["pt"], S["ft"], S["fu"], S["maneta"],
           S["chorro"], S["salp"], S["globo"]]
    join_static(dyn)
    return sc, S

# ---------------- estado ----------------
def grifo_abierto(t):
    return seg(t, -0.3, 0.15) * (1 - seg(t, T("lo más pedido"), T("lo más pedido") + 0.3)) + seg(t, T("sígueme") - 0.3, T("sígueme") + 0.15)

def nivel_lago(t):
    h = 0.02 + 0.28 * seg(t, T("construyes") + 0.6, T("montaña", fin=True) + 0.5)
    return h + 0.16 * seg(t, T("guardan casi"), T("cúbicos", fin=True))

def pose(t, S):
    sky = PAL["cielo"]; ce = win01(t, T("y a la hora"), T("así que guardas") + 0.4, 0.4, 0.5)
    bpy.context.scene.world.color = lin(tuple(mix(a, b, ce) for a, b in zip(sky, (0.98, 0.72, 0.55))))
    # grifo, chorro y salpicaduras
    g = grifo_abierto(t)
    S["maneta"].rotation_euler.x = 0.55 * g
    if g > 0.25:
        L = 0.105 * min(1, (g - 0.25) / 0.3); top = Vector((6.75, -3.14, 0.53)); bar_set(S["chorro"], top, top - Vector((0, 0, L)))
        S["chorro"]["r"] = 0.011 * (0.6 + 0.4 * g)
        for k, p in enumerate(S["salp"]):
            u = (t * 2.2 + k / 6) % 1.0; a = k * 1.05
            p.location = (6.75 + math.cos(a) * 0.05 * u, -3.18 + math.sin(a) * 0.04 * u, 0.432 + 0.04 * math.sin(u * math.pi))
    else:
        bar_set(S["chorro"], LEJOS, Vector(LEJOS) + Vector((0, 0, 0.01)))
        for p in S["salp"]: p.location = LEJOS
    # embalse y presas
    hp = mix(0.12, 1.0, seg(t, T("construyes"), T("construyes") + 1.3))
    S["presa"].scale.z = hp; S["presa"].location.z = 0.275 * hp
    h = nivel_lago(t); S["lago"].location = (-5.3, -0.5, 0.02 + h / 2); S["lago"].scale = (3.0, 2.2, h)
    fp = win01(t, T("guardan casi"), T("pero el agua del"), 0.4, 0.4)
    for k, f in enumerate(S["fp"]):
        if fp > 0.01:
            f.location = (-6.3 + k, -0.9, nivel_lago(t) + 0.1); f.scale = (fp * (0.6 + 0.6 * seg(t, T("guardan casi"), T("cúbicos", fin=True))),) * 3
        else: f.location = LEJOS
    for k, (e, (x, y)) in enumerate(S["minis"]):
        a = T("hoy son") + 0.1 * k; u = seg(t, a, a + 0.25)
        if u > 0.01: e.location = (x, y, 0); e.scale = (u, u, u)
        else: e.location = LEJOS
    # canales
    f1 = seg(t, T("así que la mandas"), T("potabilizadora", fin=True)); f2 = seg(t, T("luego viaja"), T("enormes", fin=True))
    L1 = cumul2(CANAL1); L2 = cumul2(CANAL2)
    for i, (a, b) in enumerate(zip(CANAL1, CANAL1[1:])): strip(S["c1"][i], a, b, 0.22, 0.03, 0.03, frac=(f1 * L1[-1] - L1[i]) / (L1[i + 1] - L1[i]))
    for i, (a, b) in enumerate(zip(CANAL2, CANAL2[1:])): strip(S["c2"][i], a, b, 0.22, 0.03, 0.03, frac=(f2 * L2[-1] - L2[i]) / (L2[i + 1] - L2[i]))
    for k, f in enumerate(S["fc"]):
        path, ff = (CANAL1_3, f1) if k == 0 else (CANAL2_3, f2)
        if ff > 0.05 and t < T("así que guardas") + 2:
            s = min(ff * largo(path), (t * 0.5) % largo(path)); p = at(path, s); q = at(path, s + 0.05)
            f.location = (p.x, p.y, 0.16); f.rotation_quaternion = Vector((0, 0, 1)).rotation_difference((q - p).normalized())
        else: f.location = LEJOS
    for k, p in enumerate(S["pc"]):
        path, ff = (CANAL1_3, f1) if k < 5 else (CANAL2_3, f2)
        if ff > 0.05:
            s = ((k / 5 + t * 0.25) % 1.0) * largo(path) * ff; q = at(path, s); p.location = (q.x, q.y, 0.075)
        else: p.location = LEJOS
    # potabilizadora: los depósitos se llenan turbios y salen limpios
    for k, (o, (x, y)) in enumerate(zip(S["tq"], TANQUES)):
        if t > T("potabilizadora") - 0.2:
            o.location = (x, y, 0.29)
            c = seg(t, T("filtran") + 0.5 * k, T("desinfectan", fin=True) + 0.4 * k) * (0.5 + 0.25 * k)
            set_color(o, tuple(mix(a, b, c) for a, b in zip(TURBIA, AGUA)))
        else: o.location = LEJOS
    rb = random.Random(2)
    for k, b in enumerate(S["burb"]):
        x, y = TANQUES[k // 5]
        if T("filtran") < t < T("enormes"):
            u = (t * 1.3 + k * 0.21) % 1.0; b.location = (x + rb.uniform(-0.15, 0.15), y + rb.uniform(-0.15, 0.15), 0.3 + 0.12 * u); b.scale = ((1 - u),) * 3
        else: b.location = LEJOS
    # demanda: sol de la mañana, gotas que suben de los edificios
    if T("por la mañana") - 0.4 < t < T("así que guardas") + 0.5:
        u = seg(t, T("por la mañana") - 0.4, T("por la mañana") + 0.8); v = seg(t, T("y a la hora"), T("cena", fin=True))
        S["sol"].location = (mix(mix(-3, -1, u), 9, v), 7.0, mix(mix(1.0, 4.5, u), 2.2, v))
    else: S["sol"].location = LEJOS
    rd = random.Random(4)
    for k, d in enumerate(S["drops"]):
        x, y = rd.choice((1.0, 3.0, 4.0, 5.0, 6.0, 7.0)), rd.choice((-0.9, 0.1, 1.1, 2.1))
        if T("todos abren") < t < T("así que guardas") + 0.3:
            u = (t * 0.8 + k / 10) % 1.0; d.location = (x, y, 1.4 + 0.8 * u); d.scale = (max(0.01, math.sin(u * math.pi)),) * 3
        else: d.location = LEJOS
    # depósito enterrado
    fin_dep = T("cúbicos", 2, fin=True)
    if t < 8 or t > fin_dep: hd = 0.9
    elif t < T("así que guardas"): hd = 0.0
    else: hd = 0.02 + 0.5 * seg(t, T("así que guardas"), T("enterrados", fin=True)) + 0.38 * seg(t, T("guarda ciento"), fin_dep)
    if hd > 0.01: S["dep"].location = (1.6, -3.5, -1.57 + 1.2 * hd / 2); S["dep"].scale = (2.1, 0.8, 1.2 * hd)
    else: S["dep"].location = LEJOS
    for k, (e, (x, y)) in enumerate(S["marks"]):
        a = T("más de trescientos") + 0.05 * k; u = seg(t, a, a + 0.25)
        if u > 0.01: e.location = (x, y, 0.02 + 0.08 * math.sin(min(1, u) * math.pi)); e.scale = (u, u, u)
        else: e.location = LEJOS
    # tuberías: el agua corre hacia la cocina
    vel = 0.35 + 0.6 * win01(t, T("todos abren"), T("así que guardas"), 0.5, 0.5) + 0.6 * win01(t, T("y desde ahí"), T("si los pones"), 0.3, 0.3)
    S.setdefault("fase", 0.0)
    for k, p in enumerate(S["pt"]):
        s = ((k / 16 + t * vel * 0.12) % 1.0) * largo(RED3); q = at(RED3, s); p.location = (q.x, q.y - 0.035, q.z)
    if T("y desde ahí") - 0.2 < t < T("si los pones") + 0.2 or t < 8:
        s = (t * 0.9) % (largo(RED3) - 0.5); p = at(RED3, s); qq = at(RED3, s + 0.05)
        S["ft"].location = (p.x, -3.75, p.z); S["ft"].rotation_quaternion = Vector((0, 0, 1)).rotation_difference((qq - p).normalized())
        S["fu"].location = (6.75, -3.75, mix(-0.5, -0.35, (t * 1.2) % 1.0))
    else: S["ft"].location = LEJOS; S["fu"].location = LEJOS
    # globo y tubos en fila
    a0 = T("si los pones") - 0.3; a1 = T("para casi") + 0.6
    if a0 < t < a1:
        S["globo"].location = G; s = back01(seg(t, a0, a0 + 0.5)) * (1 - seg(t, a1 - 0.4, a1)); S["globo"].scale = (max(s, 0.01),) * 3
        S["globo"].rotation_euler.z = 0.05 * math.sin(t * 0.8)
        n = 40 * seg(t, T("si los pones") + 0.4, T("australia", fin=True))
        for i, b in enumerate(S["seg"]):
            f = max(0.0, min(1.0, n - i))
            if f > 0.01: bar_set(b, S["arc"][i], S["arc"][i].lerp(S["arc"][i + 1], f))
            else: bar_set(b, (0, 0, 0), (0, 0, 0.001)); b.hide_render = True; continue
            b.hide_render = False
    else: S["globo"].location = LEJOS
    # gente
    for k, (e, (x, y)) in enumerate(S["gente"]):
        a = T("siete millones") + 0.06 * k; u = seg(t, a, a + 0.25)
        if u > 0.01 and t < T("y si quieres"):
            e.location = (x, y, 0.025 + 0.03 * abs(math.sin(t * 8 + k))); e.scale = (u, u, u)
        else: e.location = LEJOS
    apply_cam(S["cam"], *cam_lin(t, CAM(), drift=0.006 if t < 3.2 or t > T("lo más pedido") - 0.3 else 0.02))

def back01(x): return 1 + 2.7 * (x - 1) ** 3 + 1.7 * (x - 1) ** 2 if x > 0 else 0.0

def cumul2(pts):
    L = [0.0]
    for a, b in zip(pts, pts[1:]): L.append(L[-1] + (Vector(b) - Vector(a)).length)
    return L

def CAM():
    k = Claves(); add = k.add
    ini = V((6.75, -3.12, 0.48), (0.32, -0.72, 0.16), 38)
    add(0.0, V((6.75, -3.12, 0.48), (0.32, -0.72, 0.16), 38))
    add(T("y el agua sale"), V((6.75, -3.13, 0.45), (-0.25, -0.55, 0.2), 40))
    add(T("cuántos kilómetros"), V((6.75, -3.3, 0.15), (0.0, -2.1, 0.45), 32))
    add(T("escribe"), V((5.0, -3.5, -0.5), (0.8, -2.8, 0.4), 30))
    add(T("madrid no tiene"), V((1.0, 0.0, 0.0), (3.0, -17.0, 10.0), 30))
    add(T("en mil"), V((-3.5, 0.0, 0.0), (2.0, -12.0, 7.0), 30))
    add(T("la traen"), V((-5.5, 1.5, 0.2), (1.0, -5.5, 3.5), 34))
    add(T("construyes"), V((-5.2, -1.6, 0.3), (1.6, -3.6, 1.6), 36))
    add(T("hoy son"), V((-5.6, 1.2, 0.2), (1.2, -7.5, 5.5), 30))
    add(T("guardan casi"), V((-5.2, -0.8, 0.25), (-4.2, -2.2, 2.2), 34))
    add(T("pero el agua del"), V((-5.0, -0.4, 0.35), (0.7, -2.8, 1.9), 38))
    add(T("así que la mandas"), V((-2.8, -1.4, 0.1), (-1.8, -4.0, 2.4), 34))
    add(T("filtran") - 0.3, V((-1.55, -1.2, 0.3), (0.3, -1.9, 1.4), 40))
    add(T("luego viaja"), V((-1.0, -2.4, 0.1), (-2.5, -4.0, 2.2), 32))
    add(T("canales"), V((0.6, -2.9, 0.0), (-1.5, -3.5, 1.8), 34))
    add(T("pero en madrid"), V((3.5, 0.5, 0.4), (1.5, -9.0, 6.5), 30))
    add(T("por la mañana"), V((4.0, 0.8, 0.6), (-2.5, -6.5, 3.5), 30))
    add(T("y a la hora"), V((3.5, 0.8, 0.6), (3.0, -6.5, 3.0), 30))
    add(T("así que guardas"), V((1.6, -3.4, -0.8), (0.4, -3.6, 0.8), 32))
    add(T("más de trescientos"), V((3.0, 0.5, 0.0), (0.5, -8.0, 8.0), 30))
    add(T("uno de ellos"), V((1.6, -3.5, -0.9), (-0.8, -2.6, 0.3), 38))
    add(T("guarda ciento"), V((1.6, -3.5, -0.9), (0.9, -2.4, 0.6), 38))
    add(T("y desde ahí"), V((4.0, -3.5, -0.5), (-1.5, -3.0, 0.6), 34))
    add(T("tubos bajo") - 0.2, V((6.6, -3.4, 0.0), (0.6, -2.4, 0.4), 36))
    add(T("si los pones"), V(tuple(G + Vector((0, 0, 1.1))), (0.0, -12.0, 0.6), 36))
    add(T("más de diecisiete"), V(tuple(G + Vector((0.2, 0, 1.0))), (0.7, -11.5, 0.5), 38))
    add(T("casi la distancia"), V(tuple(G + Vector((0.5, -0.4, 0.8))), (0.9, -11.0, 0.4), 40), T("australia", fin=True) - T("casi la distancia"))
    add(T("para casi"), V((3.5, 0.5, 0.3), (-3.0, -9.0, 6.0), 30))
    add(T("te has"), V((3.0, 0.5, 0.2), (3.5, -10.0, 7.0), 28))
    add(T("dime en"), V((0.0, 0.0, 0.0), (0.0, -18.0, 11.0), 28))
    add(T("y si quieres"), V((6.0, -3.4, 0.0), (1.5, -3.5, 1.0), 34))
    add(T("pídelo"), V((6.7, -3.3, 0.25), (-0.6, -1.6, 0.4), 34))
    add(T("lo más pedido"), V((6.75, -3.13, 0.45), (-0.25, -0.55, 0.2), 40))
    add(T("sígueme"), ini)
    add(DUR + 1, ini)
    return k.k

def anchors(sc, S, t):
    cam = S["cam"]; P = lambda v: proj(sc, cam, v)
    return {"grifo": P((6.75, -3.1, 0.58)), "sierra": P((-5.6, 2.3, 0.6)), "lago": P((-5.3, -0.4, 0.5)), "presa": P((-5.3, -1.7, 0.6)),
            "planta": P((-1.55, -1.2, 0.5)), "ciudad": P((3.8, 0.8, 1.5)), "dep": P((1.6, -3.5, -0.2)), "tubo": P((4.5, -3.5, -0.4)),
            "mad": P(tuple(G + gp(40, -4, GR * 1.05))), "aus": P(tuple(G + gp(-25, 134, GR * 1.05))), "globo": P(tuple(G + Vector((0, 0, GR))))}

if __name__ == "__main__":
    run("canalmadrid", build, pose, anchors)
