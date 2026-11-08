# «¿Y si construyes un puente colgante?»: primer plano de un coche cruzando entre los tirantes y la cámara sube al cable; el
# puente se desmonta y se ve el estrecho en corte (agua profunda, fondo marino). Pilar imposible en medio, dos torres que suben
# (regla de 227 m y rascacielos de 70 plantas), un trozo de tablero que cae, cables dibujados de orilla a orilla, bobina
# gigante que la grúa no puede subir, rueda que hila el cable alambre a alambre, corte del cable con sus alambres, alambre
# que da tres vueltas a la Tierra, el cable que arranca del suelo, bloques de anclaje enterrados, tirantes y tablero por tramos
# y el camino del peso: tirantes → cable → torres → suelo.
import bpy, bmesh, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("puente")
SKY = (0.09, 0.08, 0.16); SEA = (0.08, 0.33, 0.42); SEA_TOP = (0.1, 0.38, 0.48); SOIL = (0.42, 0.31, 0.24); SOIL2 = (0.33, 0.24, 0.19)
ROCK = (0.36, 0.33, 0.35); GRASS = (0.2, 0.33, 0.24); HILL = (0.16, 0.2, 0.22); RED = (0.86, 0.3, 0.17); RED2 = (0.7, 0.22, 0.13)
CONC = (0.74, 0.74, 0.72); ROAD = (0.22, 0.23, 0.26); STEEL = (0.72, 0.75, 0.8); GOLD = (1.0, 0.78, 0.25); GHOST = (0.9, 0.93, 1.0)
LEJOS = (0, 0, -500)
XT, XA, XS = 50.0, 80.0, 57.0       # torres, anclajes, orilla
ZD, ZT, ZS, ZM = 6.7, 22.7, 23.0, 7.6  # tablero, torre, silla del cable, punto bajo del cable
YC = 1.35                             # cables y tirantes (delante / detrás)
YF = -4.0                             # plano del corte
DETC = Vector((42, -17, 25))         # pieza ampliada del cable
EARTH = Vector((0, 34, 47)); ER = 10.0
RNG = random.Random(11)

def alpha(o, a):
    m = o.active_material; m.diffuse_color = (*m.diffuse_color[:3], a); m.surface_render_method = 'BLENDED'

def show(o, on):
    o.hide_render = not on
    for c in o.children: show(c, on)

def prism(pts, y0, y1, color, unique=False):
    me = bpy.data.meshes.new("pr"); bm = bmesh.new()
    a = [bm.verts.new((x, y0, z)) for x, z in pts]; b = [bm.verts.new((x, y1, z)) for x, z in pts]
    bm.faces.new(a); bm.faces.new(list(reversed(b)))
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n; bm.faces.new((a[j], a[i], b[i], b[j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("pr", me); bpy.context.collection.objects.link(o)
    return setup(o, color, unique=unique)

def curve(pts, r, color, unique=True):
    cu = bpy.data.curves.new("c", 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = r; cu.bevel_resolution = 2; cu.use_fill_caps = True
    sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts): sp.points[i].co = (p[0], p[1], p[2], 1)
    o = bpy.data.objects.new("c", cu); bpy.context.collection.objects.link(o)
    return setup(o, color, unique=unique)

def curve_set(o, pts):
    sp = o.data.splines[0]
    for i, p in enumerate(pts): sp.points[i].co = (p[0], p[1], p[2], 1)

def arrow(col, r=0.35, L=4.0, unique=False):
    e = empty(LEJOS)
    cyl(r, L, (0, 0, L / 2), col, parent=e, v=12, unique=unique)
    bpy.ops.mesh.primitive_cone_add(radius1=r * 2.6, radius2=0, depth=r * 5, location=(0, 0, L + r * 2.5), vertices=16)
    setup(bpy.context.object, col, parent=e, unique=unique)
    return e

def aim(o, p, d, s=1.0):
    o.location = p; o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(Vector(d).normalized())
    s = max(s, 0.001); o.scale = (s, s, s)

def hide_bar(o): bar_set(o, LEJOS, Vector(LEJOS) + Vector((0, 0, 0.01)))

# ---------------- geometría del cable ----------------
def cable_z(x, lift=0.0):
    ax = abs(x)
    if ax <= XT: return ZM + (ZS - ZM) * (x / XT) ** 2
    u = (ax - XT) / (XA - XT)
    return mix(ZS, 1.6, u) - 1.4 * math.sin(math.pi * u) + lift * u ** 3

XS_C = [float(x) for x in range(-80, 81)]
def cable_pts(y, lift=0.0, dz=0.0):
    out = []
    for x in XS_C:
        ax = abs(x); u = max(0.0, (ax - XT) / (XA - XT)); xx = x - math.copysign(lift * 0.5 * u ** 3, x)
        out.append((xx, y, cable_z(x, lift) + dz))
    return out
BASE = cable_pts(0)
CUM = [0.0]
for a, b in zip(BASE, BASE[1:]): CUM.append(CUM[-1] + (Vector(b) - Vector(a)).length)
def along(s, y=0.0, dz=0.0):
    d = max(0.0, min(1.0, s)) * CUM[-1]
    for i in range(len(CUM) - 1):
        if d <= CUM[i + 1]:
            u = (d - CUM[i]) / max(CUM[i + 1] - CUM[i], 1e-6)
            p = Vector(BASE[i]).lerp(Vector(BASE[i + 1]), u); return Vector((p.x, y, p.z + dz)), (Vector(BASE[i + 1]) - Vector(BASE[i])).normalized()
    return Vector((BASE[-1][0], y, BASE[-1][2] + dz)), Vector((1, 0, 0))

SEABED = [(-XS, 1.5), (-54, -1.5), (-48, -3.2), (-40, -6.5), (-28, -10), (-12, -12), (0, -12.4), (12, -12), (28, -10), (40, -6.5),
          (48, -3.2), (54, -1.5), (XS, 1.5)]
def seabed_z(x):
    for (a, za), (b, zb) in zip(SEABED, SEABED[1:]):
        if a <= x <= b: return mix(za, zb, (x - a) / (b - a))
    return 1.5

DECK_X = [-78 + 4 * k for k in range(40)]
SUSP_X = [x for x in range(-78, 79, 2) if abs(abs(x) - XT) > 1.2]
def rank(x): return min(abs(x - XT), abs(x + XT))   # orden de montaje: de las torres hacia fuera

CARS = [(-34.0, -0.85, 3.4, (0.95, 0.85, 0.3)), (-12.0, -0.85, 3.4, (0.3, 0.6, 0.95)), (14.0, -0.85, 3.4, (0.95, 0.95, 0.95)),
        (40.0, -0.85, 3.4, (0.4, 0.85, 0.5)), (30.0, 0.85, -3.1, (0.9, 0.35, 0.35)), (-5.0, 0.85, -3.1, (0.95, 0.6, 0.2)),
        (-45.0, 0.85, -3.1, (0.6, 0.5, 0.9)), (-60.0, -0.85, 3.4, (0.85, 0.85, 0.9))]
P_HIL = 5.3
def wheel_s(t):
    ph = max(0.0, t - T("así que lo hilas")) / P_HIL; n = int(ph); f = ph - n
    return f if n % 2 == 0 else 1 - f

def car_x(k, t):
    x0, _, v, _ = CARS[k]; x = x0 + v * t
    return ((x + 78) % 156) - 78

def build():
    sc, cam = scene_setup(world=SKY, shadow=0.32, light_rot=60)
    S = {"cam": cam}
    # terreno en corte: fondo marino, orillas, colinas
    prism([(-130, -70)] + [(-130, 1.5)] + SEABED + [(130, 1.5), (130, -70)], YF, 200, SOIL)
    for k in range(60):
        x = RNG.uniform(-125, 125); z = RNG.uniform(-21, min(-0.5, seabed_z(x) - 0.8))
        box((RNG.uniform(1.2, 3.0), 0.05, RNG.uniform(0.3, 0.7)), (x, YF - 0.02, z), SOIL2, rot=(0, RNG.uniform(-0.3, 0.3), 0))
    box((260, 0.1, 48), (0, YF - 0.03, -46), ROCK)
    for k in range(30): sph(RNG.uniform(0.8, 2.0), (RNG.uniform(-125, 125), YF - 0.05, RNG.uniform(-29, -23)), (0.3, 0.28, 0.3), scale=(1.4, 0.1, 1), seg=10)
    for sx in (-1, 1):
        box((73, 204, 0.4), (sx * (XS + 36.5), 98, 1.7), GRASS)
        for k in range(7):
            sph(RNG.uniform(12, 22), (sx * RNG.uniform(75, 125), RNG.uniform(25, 120), RNG.uniform(-6, 0)), HILL, scale=(1.3, 1, 0.55), seg=20)
        for k in range(14):   # casitas con luces en la orilla
            x = sx * RNG.uniform(92, 120); y = RNG.uniform(6, 40); h = RNG.uniform(1.2, 3.5)
            box((2.2, 2.2, h), (x, y, 1.9 + h / 2), (0.3, 0.3, 0.36))
            box((0.5, 0.05, 0.4), (x, y - 1.13, 1.9 + h * 0.7), (1.0, 0.85, 0.45))
    S["agua"] = prism([(-XS, 1.5)] + SEABED[1:-1] + [(XS, 1.5), (XS, 0), (-XS, 0)], YF, 200, SEA, unique=True); alpha(S["agua"], 0.62)
    box((2 * XS, 204, 0.02), (0, 98, -0.01), SEA_TOP)
    S["olas"] = [box((RNG.uniform(1.5, 4), 0.12, 0.04), LEJOS, (0.35, 0.6, 0.7)) for _ in range(26)]
    S["olas_p"] = [(RNG.uniform(-54, 54), RNG.uniform(-3, 60), RNG.uniform(0, 6.28)) for _ in S["olas"]]
    # cimientos de las torres (siempre: están bajo el agua)
    for sx in (-1, 1):
        zb = seabed_z(sx * XT)
        box((5, 6, 1.2 - zb + 0.8), (sx * XT, 0, (zb - 0.8 + 1.2) / 2), CONC)
    # torres
    S["torres"] = []
    for sx in (-1, 1):
        e = empty((sx * XT, 0, 1.2)); S["torres"].append(e)
        for y in (-YC, YC):
            box((1.3, 1.0, ZT - 1.2), (0, y, (ZT - 1.2) / 2), RED, parent=e)
            box((1.6, 1.3, 1.4), (0, y, 0.7), RED2, parent=e)
            box((1.7, 0.5, 0.7), (0, y, ZT - 0.9), RED2, parent=e)   # silla
        for z, h in ((ZD - 1.6, 1.4), (12.0, 1.1), (16.4, 1.0), (20.2, 0.9), (ZT - 1.6, 0.8)):
            box((1.1, 2 * YC, h), (0, 0, z - 1.2), RED, parent=e)
    # rascacielos (comparación de altura)
    S["rasca"] = empty((-66, -1.0, 1.9)); r = S["rasca"]
    box((5, 5, ZT + 1.2), (0, 0, (ZT + 1.2) / 2), (0.45, 0.55, 0.7), parent=r)
    S["plantas"] = []
    for k in range(14):
        o = box((5.08, 5.08, 0.18), (0, 0, 1.6 * (k + 1)), (0.9, 0.85, 0.55), parent=r, unique=True); S["plantas"].append(o)
    # pilar imposible
    S["pilar"] = cyl(1.6, 1, LEJOS, (0.95, 0.3, 0.3), unique=True)
    # trozo de tablero que cae + salpicadura
    S["trozo"] = empty(LEJOS); box((24, 2.9, 0.3), (0, 0, -0.15), ROAD, parent=S["trozo"]); box((24, 3.0, 0.8), (0, 0, -0.65), RED, parent=S["trozo"])
    S["salpica"] = torus(4, 0.4, LEJOS, (0.85, 0.95, 1.0), unique=True)
    # cables: plano (fantasma), definitivo, cable de tiro, alambre que va hilando
    S["fant"] = [curve(cable_pts(y), 0.09, GHOST) for y in (-YC, YC)]
    for o in S["fant"]: alpha(o, 0.65); o.data.bevel_factor_mapping_end = 'SPLINE'
    S["cable"] = [curve(cable_pts(y), 0.14, RED) for y in (-YC, YC)]
    for o in S["cable"]: o.data.bevel_factor_mapping_end = 'SPLINE'
    S["tiro"] = [curve(cable_pts(y, dz=1.0), 0.025, (0.25, 0.25, 0.28)) for y in (-YC, YC)]
    S["hilo"] = [curve(cable_pts(y, dz=0.15), 0.04, GOLD) for y in (-YC, YC)]
    for o in S["hilo"]: o.data.bevel_factor_mapping_start = 'SPLINE'; o.data.bevel_factor_mapping_end = 'SPLINE'
    S["ruedas"] = []
    for y in (-YC, YC):
        e = empty(LEJOS); S["ruedas"].append(e)
        torus(0.55, 0.08, (0, 0, 0), (0.95, 0.95, 0.95), parent=e, rot=(math.pi / 2, 0, 0))
        for k in range(3): box((1.05, 0.06, 0.06), (0, 0, 0), (0.6, 0.6, 0.65), parent=e, rot=(0, k * math.pi / 3, 0))
        cyl(0.12, 0.25, (0, 0, 0), GOLD, parent=e, rot=(math.pi / 2, 0, 0))
    # barcaza con la bobina gigante y la grúa
    S["barca"] = empty((4, 9, 0.2)); b = S["barca"]
    box((14, 7, 1.3), (0, 0, 0), (0.3, 0.32, 0.36), parent=b); box((14.2, 7.2, 0.3), (0, 0, 0.6), (0.85, 0.7, 0.2), parent=b)
    box((0.8, 0.8, 11), (5.5, 0, 6), (0.95, 0.75, 0.15), parent=b)
    S["pluma"] = empty((5.5, 0, 11.3), parent=b)
    o = bar_obj((0.95, 0.75, 0.15), 0.35, parent=S["pluma"]); bar_set(o, (0, 0, 0), (-9.0, 0, 1.5))
    S["gancho"] = bar_obj((0.15, 0.15, 0.17), 0.06, parent=b)
    S["bobina"] = empty((-3.5, 0, 2.2), parent=b)
    torus(2.4, 1.5, (0, 0, 0), STEEL, parent=S["bobina"])
    for k in range(3): torus(2.4 + (k - 1) * 0.9, 0.12, (0, 0, 1.45), (0.55, 0.57, 0.62), parent=S["bobina"])
    # tirantes y tablero
    S["tir"] = [(x, y, bar_obj((0.9, 0.35, 0.2), 0.05)) for x in SUSP_X for y in (-YC, YC)]
    S["tramos"] = []
    for x in DECK_X:
        e = empty((x, 0, ZD)); S["tramos"].append(e)
        box((4.02, 2.9, 0.25), (0, 0, -0.125), ROAD, parent=e)
        box((4.02, 3.0, 0.8), (0, 0, -0.65), RED, parent=e)
        for y in (-1.46, 1.46): box((4.02, 0.08, 0.18), (0, y, 0.1), (0.95, 0.5, 0.3), parent=e)
        box((1.2, 0.06, 0.01), (0, 0, 0.01), (0.95, 0.95, 0.9), parent=e)
    S["coches"] = []
    for x0, y, v, col in CARS:
        e = empty(LEJOS); S["coches"].append(e)
        box((0.46, 0.21, 0.12), (0, 0, 0.11), col, parent=e)
        box((0.24, 0.19, 0.1), (-0.03 if v > 0 else 0.03, 0, 0.21), (0.2, 0.25, 0.32), parent=e)
        for dx in (-0.14, 0.14):
            for dy in (-0.1, 0.1): cyl(0.045, 0.03, (dx, dy, 0.05), (0.08, 0.08, 0.08), parent=e, rot=(math.pi / 2, 0, 0), v=12)
        box((0.02, 0.15, 0.03), (0.23 * (1 if v > 0 else -1), 0, 0.12), (1.0, 0.95, 0.7), parent=e)
    # bloques de anclaje
    S["anclas"] = []
    for sx in (-1, 1):
        e = empty((sx * (XA + 3.5), 0, -4.0)); S["anclas"].append(e)
        box((10, 8.2, 12.2), (0, -0.1, 0), CONC, parent=e)
        for z in (-3.5, 0.0, 3.5): box((10.04, 8.3, 0.12), (0, -0.1, z), (0.62, 0.62, 0.6), parent=e)
    # flechas de fuerza
    S["fl_tira"] = [arrow((0.95, 0.25, 0.25), 0.3, 4.0, True) for _ in range(4)]
    S["fl_baja"] = [arrow((0.95, 0.25, 0.25), 0.35, 4.0) for _ in range(4)]
    S["fl_tir"] = []
    for _ in range(24):
        bpy.ops.mesh.primitive_cone_add(radius1=0.3, radius2=0, depth=0.7, location=LEJOS, vertices=12, rotation=(math.pi, 0, 0))
        S["fl_tir"].append(setup(bpy.context.object, GOLD))
    S["flujo"] = [sph(0.28, LEJOS, GOLD, seg=10) for _ in range(40)]
    S["flujo_t"] = [sph(0.3, LEJOS, GOLD, seg=10) for _ in range(16)]
    # pieza ampliada del cable (corte con sus alambres)
    S["det"] = empty(DETC); d = S["det"]
    cyl(2.45, 6, (0, 3.0, 0), RED, parent=d, rot=(math.pi / 2, 0, 0))
    cyl(2.25, 0.1, (0, -0.02, 0), (0.12, 0.12, 0.14), parent=d, rot=(math.pi / 2, 0, 0))
    S["bandas"] = []
    NB = 9; pitch = 0.105; rw = 0.048
    meshes = [[] for _ in range(NB)]
    for i in range(-24, 25):
        for j in range(-24, 25):
            x = (i + 0.5 * (j % 2)) * pitch; z = j * pitch * 0.866; rr = math.hypot(x, z)
            if rr < 2.18: meshes[min(NB - 1, int(rr / 2.18 * NB))].append((x, z))
    for pts in meshes:
        me = bpy.data.meshes.new("w"); bm = bmesh.new()
        for x, z in pts:
            vs = [bm.verts.new((x + rw * math.cos(a * math.tau / 8), -0.08, z + rw * math.sin(a * math.tau / 8))) for a in range(8)]
            bm.faces.new(list(reversed(vs)))
        bm.to_mesh(me); bm.free()
        o = bpy.data.objects.new("w", me); bpy.context.collection.objects.link(o); o.parent = d
        setup(o, (0.82, 0.84, 0.88)); S["bandas"].append(o)
    S["uno"] = cyl(0.075, 0.1, (1.68, -0.14, 0.42), GOLD, parent=d, rot=(math.pi / 2, 0, 0), unique=True)
    # la Tierra y el alambre que la envuelve
    S["tierra"] = empty(EARTH); te = S["tierra"]
    S["globo"] = empty((0, 0, 0), parent=te)
    sph(ER, (0, 0, 0), (0.18, 0.42, 0.82), parent=S["globo"], seg=48)
    rr = random.Random(5)
    for k in range(11):
        th, ph = rr.uniform(0, math.tau), rr.uniform(-0.9, 0.9)
        n = Vector((math.cos(ph) * math.cos(th), math.cos(ph) * math.sin(th), math.sin(ph)))
        o = sph(rr.uniform(2.2, 3.8), n * (ER - 0.4), (0.3, 0.65, 0.35), parent=S["globo"], scale=(1.3, 1, 0.3), seg=16)
        o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(n)
    for sz in (-1, 1): sph(3.2, (0, 0, sz * (ER - 0.9)), (0.95, 0.97, 1.0), parent=S["globo"], scale=(1, 1, 0.3), seg=16)
    turns = 129000 / 40075; pts = []
    for k in range(700):
        u = k / 699; th = u * turns * math.tau; al = mix(0.35, 1.05, u)
        pts.append(tuple(EARTH + (ER + 0.35) * Vector((math.cos(th), math.sin(th) * math.cos(al), math.sin(th) * math.sin(al)))))
    S["vuelta"] = curve(pts, 0.3, GOLD); S["vuelta"].data.bevel_factor_mapping_end = 'SPLINE'
    dyn = [cam, S["agua"], S["olas"], S["torres"], S["rasca"], S["pilar"], S["trozo"], S["salpica"], S["barca"], S["ruedas"],
           [o for _, _, o in S["tir"]], S["tramos"], S["coches"], S["anclas"], S["fl_tira"], S["fl_baja"], S["fl_tir"], S["flujo"],
           S["flujo_t"], S["det"], S["tierra"]]
    join_static(dyn)
    return sc, S

# --------------------------------------------------------------------------------------------------
def pose(t, S):
    t_desm, t_prim, t_entre, t_nopu, t_torr, t_cerca = T("vamos a colgarlo"), T("primero"), T("entre las dos"), T("no puedes"), T("así que levantas"), T("una cerca")
    t_sf, t_227, t_rasc, t_70, t_solas = T("en el puente"), T("doscientos"), T("como un rascacielos"), T("setenta"), T("pero las torres")
    t_tiend, t_pero, t_subir, t_hilas, t_rueda = T("así que tiendes"), T("pero un cable"), T("ni subir"), T("así que lo hilas"), T("con una rueda")
    t_cada, t_cinco, t_jun, t_cur, t_estir, t_salen, t_tres = T("cada cable"), T("cinco"), T("juntos"), T("y aquí"), T("si estiras"), T("salen"), T("más de tres")
    t_tira, t_much, t_ata, t_bloq, t_cuel, t_ellos, t_peso, t_sube, t_emp = (T("pero el cable"), T("muchísima"), T("así que en cada"), T("bloques"),
        T("ahora cuelgas"), T("y de ellos"), T("el peso"), T("sube por"), T("y empuja"))
    full0 = t < t_desm + 0.15                    # puente completo del principio
    dz = seg(t, t_desm + 0.1, t_desm + 1.0)      # desmontaje
    # olas
    for o, (x, y, ph) in zip(S["olas"], S["olas_p"]):
        o.location = (x + 0.6 * math.sin(t * 0.7 + ph), y + 0.3 * math.cos(t * 0.5 + ph), 0.02)
    # torres
    for k, e in enumerate(S["torres"]):
        if t < t_prim: u = 1 - dz
        else:
            a = t_torr + 0.1 if k == 0 else t_cerca
            u = seg(t, a, a + 1.3)
        e.scale = (1, 1, max(u, 0.001)); show(e, u > 0.01)
    # rascacielos
    rz = win01(t, t_rasc - 0.4, t_solas + 0.2, 0.6, 0.5)
    S["rasca"].location = (-66, -1.0, 1.9 - 26 * (1 - rz)); show(S["rasca"], rz > 0.01)
    nf = keyed(t, [(t_rasc, 0), (T("plantas", fin=True), 14)])
    for k, o in enumerate(S["plantas"]): o.hide_render = not (k < nf and rz > 0.01)
    # pilar imposible
    pu = seg(t, t_nopu - 0.1, t_nopu + 0.6) * (1 - seg(t, t_torr - 0.5, t_torr))
    if pu > 0.01:
        zt = ZD; zb = mix(ZD, seabed_z(0), pu); S["pilar"].location = (0, 0, (zt + zb) / 2); S["pilar"].scale = (1, 1, max(zt - zb, 0.01))
        set_color(S["pilar"], (0.95, 0.3, 0.3) if (t - t_nopu) % 0.4 < 0.25 or t < t_nopu + 0.7 else (0.6, 0.15, 0.15))
    else: S["pilar"].location = LEJOS
    # trozo de tablero que cae
    if t_solas - 0.1 < t < t_tiend + 0.3:
        u = seg(t, t_solas + 0.9, t_solas + 1.7)
        z = ZD - 0.2 * math.sin((t - t_solas) * 9) * (1 - u) - 9 * u * u
        S["trozo"].location = (0, 0, z); S["trozo"].rotation_euler = (0.25 * u, 0, 0.0); show(S["trozo"], z > -1.5)
        S["trozo"].scale = (1, 1, 1) if t > t_solas + 0.25 else (seg(t, t_solas - 0.1, t_solas + 0.25),) * 3
    else: S["trozo"].location = LEJOS
    sp = (t - (t_solas + 1.6))
    if 0 < sp < 1.2:
        S["salpica"].location = (0, 0, 0.1); s = 1 + 4 * sp; S["salpica"].scale = (s, s * 0.6, 1); S["salpica"].hide_render = False
    else: S["salpica"].location = LEJOS
    # cable fantasma (plano) y cable real
    gu = seg(t, t_tiend + 0.2, T("por encima", fin=True))
    hil = seg(t, t_hilas, t_cada)                # avance del hilado (grosor)
    for o in S["fant"]:
        o.data.bevel_factor_end = max(gu, 0.001); o.hide_render = not (t_tiend < t < t_cada + 0.5 and gu > 0.005)
    lift = 2.6 * seg(t, t_tira + 0.3, t_much + 0.4) * (1 - seg(t, t_bloq, t_bloq + 1.2))
    lift += 0.25 * math.sin(t * 22) * win01(t, t_much - 0.2, t_ata, 0.3, 0.3)
    for k, o in enumerate(S["cable"]):
        y = (-YC, YC)[k]
        if t < t_prim:
            o.hide_render = dz > 0.98; o.data.bevel_factor_end = max(1 - dz, 0.001); o.data.bevel_depth = 0.14
            curve_set(o, cable_pts(y))
        else:
            on = t > t_hilas
            o.hide_render = not on; o.data.bevel_factor_end = 1.0
            o.data.bevel_depth = mix(0.02, 0.14, hil)
            curve_set(o, cable_pts(y, lift))
            set_color(o, tuple(mix(c, d, seg(t, t_jun, t_jun + 1.5)) for c, d in zip(STEEL, RED)))
    # hilado: rueda que va y viene
    sp_on = t_hilas - 0.1 < t < t_cada + 4.5
    n = int(max(0.0, t - t_hilas) / P_HIL); s = wheel_s(t)
    for k in range(2):
        y = (-YC, YC)[k]
        tr, hl, wh = S["tiro"][k], S["hilo"][k], S["ruedas"][k]
        tr.hide_render = not sp_on; hl.hide_render = not sp_on
        if sp_on:
            p, dvec = along(s, y, 0.75)
            wh.location = p; wh.rotation_euler = (0, -math.atan2(dvec.z, dvec.x) - t * 12 * (1 if n % 2 == 0 else -1), 0)
            if n % 2 == 0: hl.data.bevel_factor_start = 0.0; hl.data.bevel_factor_end = max(s, 0.002)
            else: hl.data.bevel_factor_start = min(s, 0.998); hl.data.bevel_factor_end = 1.0
        else: wh.location = LEJOS
        show(wh, sp_on)
    # barcaza y bobina
    bon = t_pero - 0.6 < t < t_hilas + 0.6
    S["barca"].location = (4, 9, 0.2) if bon else LEJOS; show(S["barca"], bon)
    if bon:
        up = seg(t, t_pero + 0.6, t_pero + 1.6) * (1 - seg(t, t_subir - 0.1, t_subir + 0.3))
        shake = 0.08 * math.sin(t * 40) * up
        S["bobina"].location = (-3.5, 0, 2.2 + 0.55 * up + shake)
        S["barca"].rotation_euler = (0, -0.05 * up + 0.01 * math.sin(t * 2), 0); S["barca"].location = (4, 9, 0.2 - 0.35 * up)
        S["pluma"].rotation_euler = (0, -0.09 * up, 0)
        bar_set(S["gancho"], (-3.5, 0, 3.9 + 0.55 * up), (-3.5 + 0.3 * up, 0, 12.6 - 1.2 * up))
    # tirantes y tablero
    for x, y, o in S["tir"]:
        if full0:
            u = 1.0 - dz; zc = cable_z(x); bar_set(o, (x, y, zc), (x, y, mix(zc, ZD, u))) if u > 0.01 else hide_bar(o)
        else:
            a = t_cuel + rank(x) / 29 * 1.7; u = seg(t, a, a + 0.35)
            if u > 0.01:
                zc = cable_z(x, lift) ; bar_set(o, (x, y, zc), (x, y, mix(zc, ZD, u)))
            else: hide_bar(o)
    for x, e in zip(DECK_X, S["tramos"]):
        if t < t_prim:
            fall = seg(t, t_desm + 0.05 * (abs(x) % 9), t_desm + 0.7 + 0.05 * (abs(x) % 9))
            e.location = (x, 0, ZD - 12 * fall * fall); e.rotation_euler = (0.3 * fall * (1 if x % 8 else -1), 0, 0); show(e, fall < 0.7)
        else:
            a = t_ellos - 0.1 + rank(x) / 29 * 1.1; u = seg(t, a, a + 0.45)
            e.location = (x, 0, ZD - 7 * (1 - u)); e.rotation_euler = (0, 0, 0); show(e, u > 0.02)
    # coches
    for k, e in enumerate(S["coches"]):
        x0, y, v, _ = CARS[k]; x = car_x(k, t)
        on = (t < t_desm + 0.1) or (t > t_ellos + 1.6 and (rank(x) / 29 * 1.1 + t_ellos + 0.5 < t))
        e.location = (x, y, ZD + 0.0) if on else LEJOS; e.rotation_euler = (0, 0, 0 if v > 0 else math.pi); show(e, on)
    # anclajes enterrados
    for k, e in enumerate(S["anclas"]):
        sx = (-1, 1)[k]; u = seg(t, t_ata + 0.6, t_bloq + 0.6) if t >= t_prim else 0.0
        on = t < t_prim or u > 0.01
        e.location = (sx * (XA + 3.5), 0, -4.0 - 16 * (1 - u)) if t >= t_prim else (sx * (XA + 3.5), 0, -4.0)
        if t < t_prim: e.location = (sx * (XA + 3.5), 0, -4.0 - 16 * dz)
        show(e, on and (t >= t_prim or dz < 0.98))
    # flechas: el cable tira hacia dentro
    fa = win01(t, t_tira + 0.2, t_cuel + 0.3, 0.4, 0.4)
    gr = seg(t, t_bloq + 0.4, t_bloq + 1.2)
    for k, o in enumerate(S["fl_tira"]):
        sx = (-1, 1)[k // 2]; y = (-YC, YC)[k % 2] - (0.9 if k % 2 == 0 else -0.9)
        if fa > 0.01:
            x = sx * 74.0; p = Vector((x, y, cable_z(x, lift) + 0.2)); x2 = sx * 70.0; d = Vector((x2, y, cable_z(x2, lift))) - p
            sc_ = (0.6 + 0.6 * seg(t, t_much - 0.3, t_much + 0.4)) * fa * (1 - 0.45 * gr)
            aim(o, p, d, sc_); show(o, True)
            for c in o.children: set_color(c, tuple(mix(a, b, gr) for a, b in zip((0.95, 0.25, 0.25), (0.3, 0.9, 0.45))))
        else: o.location = LEJOS; show(o, False)
    # camino del peso
    t1 = t > t_peso - 0.2
    sus = [x for x in SUSP_X if abs(x) < 46 and x % 6 == 0][:24]
    for k, o in enumerate(S["fl_tir"]):
        if t1 and k < len(sus):
            x = sus[k]; zc = cable_z(x); u = (t * 0.8 + k * 0.37) % 1
            o.location = (x, -YC - 0.05, mix(zc - 0.4, ZD + 0.5, u)); o.hide_render = False
            s_ = seg(t, t_peso - 0.2, t_peso + 0.3); o.scale = (s_, s_, s_)
        else: o.location = LEJOS
    t2 = t > t_sube - 0.2
    for k, o in enumerate(S["flujo"]):
        if t2:
            side = 1 if k % 2 else -1; u = (t * 0.45 + (k // 2) / 20) % 1
            x = side * XT * u; o.location = (x, -YC, cable_z(x) + 0.05); o.hide_render = False
            s_ = seg(t, t_sube - 0.2, t_sube + 0.3); o.scale = (s_, s_, s_)
        else: o.location = LEJOS
    t3 = t > t_emp - 0.2
    for k, o in enumerate(S["flujo_t"]):
        if t3:
            sx = 1 if k % 2 else -1; yy = -YC; u = (t * 0.5 + (k // 2) / 8) % 1
            o.location = (sx * XT, yy - 0.6, mix(ZT - 0.5, seabed_z(sx * XT) - 0.5, u)); o.hide_render = False
            s_ = seg(t, t_emp - 0.2, t_emp + 0.3); o.scale = (s_, s_, s_)
        else: o.location = LEJOS
    fb = seg(t, t_emp, t_emp + 0.6)
    for k, o in enumerate(S["fl_baja"]):
        sx = (-1, 1)[k // 2]
        if fb > 0.01:
            p = Vector((sx * XT + (k % 2 - 0.5) * 2.4, YF - 0.6, seabed_z(sx * XT) + 2.2)); aim(o, p, (0, 0, -1), fb * (0.75 + 0.1 * math.sin(t * 6)))
            show(o, True)
        else: o.location = LEJOS; show(o, False)
    # pieza ampliada del cable
    dt = win01(t, t_cada - 0.3, t_cur + 0.5, 0.6, 0.5)
    S["det"].location = DETC if dt > 0.01 else LEJOS; S["det"].scale = (max(dt, 0.001),) * 3; show(S["det"], dt > 0.01)
    nb = keyed(t, [(t_cada + 0.1, 0.5), (T("dos alambres", fin=True), len(S["bandas"]))])
    if dt > 0.01:
        for k, o in enumerate(S["bandas"]): o.hide_render = k >= nb
        u1 = win01(t, t_cinco - 0.1, t_cur, 0.3, 0.3); S["uno"].hide_render = u1 < 0.02
        S["uno"].scale = (1 + 1.5 * u1, 1, 1 + 1.5 * u1)
    S["det"].rotation_euler = (0, 0.25 * math.sin(t * 0.6), 0)
    # la Tierra
    eo = win01(t, t_cur + 0.2, t_tira + 0.4, 0.8, 0.6)
    S["tierra"].location = EARTH if eo > 0.01 else LEJOS; show(S["tierra"], eo > 0.01); S["tierra"].scale = (max(eo, 0.001),) * 3
    S["globo"].rotation_euler = (0, 0, t * 0.35)
    wu = seg(t, t_estir + 0.3, T("tres vueltas", fin=True) - 0.2)
    S["vuelta"].hide_render = not (eo > 0.5 and wu > 0.002); S["vuelta"].data.bevel_factor_end = max(wu, 0.002)
    apply_cam(S["cam"], *cam_state(t, CAM(), drift=0.5))

def VD(at, dist, yaw, pitch, lens=32):
    at = Vector(at); y, p = math.radians(yaw), math.radians(pitch)
    return (tuple(at + dist * Vector((math.sin(y) * math.cos(p), -math.cos(y) * math.cos(p), math.sin(p)))), tuple(at), lens)

_CAM = None
def CAM():
    global _CAM
    if _CAM: return _CAM
    k = []
    def add(t, v): k.append((t,) + v)
    def follow(t, back=1.3, side=-2.4, up=0.65, lens=24):
        x = car_x(0, t); return ((x - back, side, ZD + up), (x + 1.2, -0.85, ZD + 0.25), lens)
    add(0.0, follow(0.0)); add(1.0, follow(1.0, 1.4, -2.5, 0.75)); add(2.0, follow(2.0, 1.6, -2.7, 1.0))
    xc = car_x(0, 3.4)
    add(T("colgado"), ((xc - 3.5, -5.0, 9.5), (xc + 1.0, -YC, cable_z(xc + 1.0) - 0.6), 26))
    add(T("alambres") + 0.2, ((xc - 4.0, -6.0, 12.0), (xc + 2.5, -YC, cable_z(xc + 2.5)), 28))
    add(T("y si tuvieras") + 0.4, VD((-22, 0, 8), 118, -60, 12, 30))
    add(T("vamos a colgarlo"), VD((-20, 0, 6), 125, -58, 13, 30))
    add(T("primero") + 0.2, VD((-22, 0, 1), 118, -58, 15, 30))
    add(T("entre las dos") + 1.5, VD((-20, 0, 0), 120, -54, 15, 30))
    add(T("no puedes") + 0.6, VD((-4, 0, -1), 66, -36, 12, 30))
    add(T("así que levantas") + 0.8, VD((-18, 0, 5), 98, -54, 12, 30))
    add(T("en el puente") + 0.2, VD((-57, 0, 12.5), 58, -16, 4, 34))
    add(T("setenta", fin=True), VD((-58, 0, 12.5), 56, -24, 6, 34))
    add(T("pero las torres") + 0.3, VD((-16, 0, 8), 84, -50, 10, 27))
    add(T("así que tiendes") + 0.6, VD((-22, 0, 8), 118, -58, 12, 30))
    add(T("por encima", fin=True), VD((-18, 0, 9), 112, -52, 13, 30))
    add(T("pero un cable") + 0.7, VD((3, 9, 3), 36, -24, 17, 30))
    add(T("ni subir", fin=True), VD((3, 9, 3), 33, -14, 15, 30))
    th = T("así que lo hilas")
    for q in range(1, 15):
        tq = th + 0.35 * q
        if tq > T("cada cable") - 0.2: break
        w, _ = along(wheel_s(tq), -YC, 0.75)
        add(tq, (tuple(w + Vector((-2.5, -9.5, 2.5))), tuple(w + Vector((0.5, 0, -0.8))), 26))
    add(T("cada cable") + 0.5, (tuple(DETC + Vector((1.5, -10.8, 2.4))), tuple(DETC + Vector((0.2, 0, 1.2))), 32))
    add(T("juntos") + 0.6, (tuple(DETC + Vector((0.3, -11.0, 2.0))), tuple(DETC + Vector((0, 0, 1.0))), 32))
    add(T("y aquí") - 0.3, (tuple(DETC + Vector((0.0, -11.8, 2.2))), tuple(DETC + Vector((0, 0, 1.1))), 32))
    add(T("y aquí") + 0.3, (tuple(DETC + Vector((-0.3, -12.5, 2.6))), tuple(DETC + Vector((0, 0, 1.2))), 32))
    add(T("y aquí") + 1.2, VD(EARTH + Vector((0, 0, 3)), 50, -8, 8, 32))
    add(T("más de tres") + 1.2, VD(EARTH + Vector((0, 0, 3)), 46, 10, 12, 32))
    add(T("pero el cable") + 0.6, VD((-68, 0, 8), 36, -34, 12, 30))
    add(T("muchísima") + 0.4, VD((-70, 0, 6), 33, -26, 11, 30))
    add(T("bloques") - 0.2, VD((-79, 0, -1.5), 40, -12, 8, 30))
    add(T("enterrados", fin=True), VD((-77, 0, 0), 42, -18, 9, 30))
    add(T("ahora cuelgas") + 0.6, VD((-24, 0, 9), 78, -62, 12, 30))
    add(T("y de ellos") + 1.0, VD((-22, 0, 9), 80, -56, 12, 30))
    add(T("el peso") + 0.6, VD((-36, 0, 12), 52, -36, 8, 30))
    add(T("sube por") + 0.4, VD((-30, 0, 13), 62, -30, 9, 30))
    add(T("y empuja") + 0.8, VD((-44, 0, 6), 62, -22, 6, 30))
    add(DUR - 0.6, VD((-12, 0, 6), 140, -52, 11, 30))
    add(DUR + 3, VD((-12, 0, 6), 145, -50, 11, 30))
    _CAM = k; return k

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v)
    xc = car_x(0, t)
    return {"coche": Pj((xc, -0.85, ZD + 0.4)), "cable": Pj((car_x(0, 3.4) + 2.5, -YC, cable_z(car_x(0, 3.4) + 2.5) + 0.4)),
            "orL": Pj((-XS, YF, 1.5)), "orR": Pj((XS, YF, 1.5)), "fondo": Pj((0, YF, -12.4)), "sup": Pj((0, YF, 0)),
            "pilar": Pj((0, 0, ZD + 1)), "torreL": Pj((-XT, -YC, ZT + 0.4)), "baseL": Pj((-XT, -YC, 0)), "torreR": Pj((XT, -YC, ZT + 0.4)),
            "rasca": Pj((-66, -3.5, ZT + 3)), "trozo": Pj((0, 0, ZD + 1.5)), "bobina": Pj((0.5, 6, 4.6)), "grua": Pj((9.5, 9, 12)),
            "rueda": Pj(tuple(along(wheel_s(t), -YC, 1.6)[0])),
            "detL": Pj(tuple(DETC + Vector((-2.45, -0.1, 0)))), "detR": Pj(tuple(DETC + Vector((2.45, -0.1, 0)))),
            "detB": Pj(tuple(DETC + Vector((0, -0.1, -2.45)))), "detT": Pj(tuple(DETC + Vector((0, -0.1, 2.45)))),
            "uno": Pj(tuple(DETC + Vector((1.68, -0.15, 0.42)))), "tierra": Pj(tuple(EARTH + Vector((0, 0, ER + 1.5)))),
            "tierraB": Pj(tuple(EARTH + Vector((0, 0, -ER - 1.5)))),
            "finL": Pj((-74, -YC, cable_z(-74) + 1.5)), "ancla": Pj((-XA - 3.5, YF, -4.0)), "tir": Pj((-30, -YC, 9.5)),
            "tablero": Pj((-14, -1.5, ZD - 0.6)), "cimL": Pj((-XT, YF, seabed_z(-XT) + 1)), "cableM": Pj((-26, -YC, cable_z(-26) + 0.6))}

if __name__ == "__main__":
    run("puente", build, pose, anchors)
