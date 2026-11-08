# «Así funciona una caldera de condensación»: caldera de pared en corte, con la llama azul encendiéndose en primer plano
# y el agua empezando a circular; el grifo y el termostato que la despiertan; gas, llama, intercambiador que se pone al rojo,
# bomba que empuja el agua al radiador (debajo) y la vuelta más fría; el humo (CO2 + vapor de agua) que las calderas
# antiguas tiraban por la chimenea con su calor; el segundo intercambiador, por donde pasa primero el agua fría de la
# vuelta; el vapor que se condensa en gotas y calienta el agua, la bandeja y el tubo que gotea por debajo; y al final
# la llama un poco más pequeña (−25 % de gas).
import bpy, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("caldera")
BG = (0.10, 0.085, 0.10); WALL = (0.25, 0.215, 0.21); TILE = (0.30, 0.26, 0.25); FLOOR = (0.28, 0.2, 0.15)
WHITE = (0.93, 0.93, 0.91); INNER = (0.78, 0.8, 0.82); CHAMB = (0.13, 0.13, 0.16); TUBE = (0.62, 0.66, 0.72); TUBEHOT = (1.0, 0.42, 0.18)
COPPER = (0.85, 0.5, 0.3); GASC = (1.0, 0.82, 0.15); FLAME = (0.2, 0.42, 1.0); FLAME2 = (0.65, 0.85, 1.0)
COLDW = (0.25, 0.55, 1.0); HOTW = (1.0, 0.25, 0.15); SMOKEH = (1.0, 0.55, 0.22); CO2C = (0.42, 0.42, 0.47); VAPC = (0.97, 0.97, 1.0)
COOLS = (0.55, 0.68, 0.85); DROP = (0.3, 0.65, 1.0); PUMP = (0.22, 0.42, 0.8); RAD = (0.9, 0.9, 0.88); RADHOT = (1.0, 0.62, 0.45)
CHROME = (0.78, 0.8, 0.84); LEJOS = (0, 0, -900)
RNG = random.Random(11)

# ---- recorridos del agua (x, z, en radiador?) ----
RAD_IN = [(-17.5, 40), (-17.5, -30), (-32, -30), (-32, -41), (-26, -41)]
RAD_ZZ = [(-26, -41, 1), (24, -46, 1), (-24, -54, 1), (24, -62, 1), (-24, -70, 1), (26, -75, 1)]
RET = [(26, -75), (32, -75), (32, -30), (14, -30), (14, 0)]
COIL1 = [(15, 30), (-15, 30), (-15, 35), (15, 35), (15, 40), (-15, 40)]
COIL2 = [(15, 51), (-15, 51), (-15, 57), (15, 57)]
def P2(lst, rad=False):
    return [(p[0], p[1], (len(p) > 2 and p[2]) or rad) for p in lst]
# temperatura de cada vértice (°C)
LOOP_A = ([(14, 0, 0, 40), (14, 10, 0, 40), (14, 20, 0, 40), (17.5, 20, 0, 40), (17.5, 30, 0, 40)] +
          [(x, z, 0, 40 + 30 * i / 5) for i, (x, z) in enumerate(COIL1)] +
          [(x, z, 0, 70) for x, z in RAD_IN[0:]] + [(x, z, 1, 70 - 30 * i / 5) for i, (x, z, _) in enumerate(RAD_ZZ)] +
          [(x, z, 0, 40) for x, z in RET[1:]])
LOOP_B = ([(14, 0, 0, 40), (14, 10, 0, 40), (14, 20, 0, 40), (19.5, 20, 0, 40), (19.5, 51, 0, 40)] +
          [(x, z, 0, 40 + 12 * i / 3) for i, (x, z) in enumerate(COIL2)] + [(17.5, 57, 0, 52), (17.5, 30, 0, 52)] +
          [(x, z, 0, 52 + 18 * i / 5) for i, (x, z) in enumerate(COIL1)] +
          [(x, z, 0, 70) for x, z in RAD_IN[0:]] + [(x, z, 1, 70 - 30 * i / 5) for i, (x, z, _) in enumerate(RAD_ZZ)] +
          [(x, z, 0, 40) for x, z in RET[1:]])

def prep(loop):
    P = [Vector((x, 2.0 if r else -1.45, z)) for x, z, r, _ in loop]; Tm = [v for *_, v in loop]
    L = [(b - a).length for a, b in zip(P, P[1:])]; S = [0.0]
    for l in L: S.append(S[-1] + l)
    return P, Tm, S
PA, TA, SA = prep(LOOP_A); PB, TB, SB = prep(LOOP_B)
def at_s(P, Tm, S, s):
    s = s % S[-1]
    for i in range(len(P) - 1):
        if S[i] <= s <= S[i + 1]:
            u = (s - S[i]) / max(S[i + 1] - S[i], 1e-6); return P[i].lerp(P[i + 1], u), mix(Tm[i], Tm[i + 1], u)
    return P[-1], Tm[-1]
COIL_S0 = SA[5]; COIL_S1 = SA[10]

def poly(pts, u):
    P = [Vector(p) for p in pts]; L = [(b - a).length for a, b in zip(P, P[1:])]; s = u * sum(L)
    for a, b, l in zip(P, P[1:], L):
        if s <= l: return a.lerp(b, s / max(l, 1e-6))
        s -= l
    return P[-1]

def arrow(col, r=0.45, L=5.0):
    e = empty(LEJOS)
    cyl(r, L, (0, 0, L / 2), col, parent=e, v=12)
    bpy.ops.mesh.primitive_cone_add(radius1=r * 2.6, radius2=0, depth=r * 5, location=(0, 0, L + r * 2.5), vertices=16); setup(bpy.context.object, col, parent=e)
    return e
def aim(o, p, d, s=1.0):
    o.location = p; o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(Vector(d).normalized())
    s = max(s, 0.001); o.scale = (s, s, s)
def show(o, on):
    o.hide_render = not on
    for c in o.children: show(c, on)
def hide_bar(o): bar_set(o, LEJOS, Vector(LEJOS) + Vector((0, 0, 0.01)))
def grow_bar(o, a, b, u):
    if u <= 0.01: hide_bar(o)
    else: bar_set(o, a, Vector(a).lerp(Vector(b), u))

def pipe_path(pts, col, r, y=0.0):
    out = []
    for (x0, z0), (x1, z1) in zip(pts, pts[1:]):
        o = bar_obj(col, r); bar_set(o, (x0, y, z0), (x1, y, z1)); out.append(o)
    for x, z in pts[1:-1]: sph(r, (x, y, z), col, seg=12)
    return out

SMK = [(RNG.uniform(-11, 11), RNG.uniform(-3.5, 2.5), k % 2, RNG.uniform(0.9, 1.35), RNG.uniform(0, 6.28)) for k in range(46)]
DRP = [(RNG.choice((51, 57)), RNG.uniform(-13, 13)) for _ in range(22)]
FLX = [-12 + 3 * k for k in range(9)]

def build():
    sc, cam = scene_setup(world=BG, shadow=0.38, light_rot=20)
    S = {"cam": cam}
    # pared alicatada y suelo
    box((320, 2, 260), (0, 17, 25), WALL)
    for x in range(-150, 151, 12): box((0.35, 0.3, 260), (x, 15.9, 25), TILE)
    for z in range(-84, 150, 12): box((320, 0.3, 0.35), (0, 15.9, z), TILE)
    box((320, 200, 2), (0, -84, -87), FLOOR)
    # carcasa de la caldera en corte
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -25, 50)); cut = bpy.context.object; cut.scale = (60, 38, 82); cut.hide_render = True
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -10, 92)); cut2 = bpy.context.object; cut2.scale = (20, 20, 30); cut2.hide_render = True
    S["cut"] = [cut, cut2]
    def cutobj(o, cutter, th=1.2, inner=INNER):
        bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        m = o.modifiers.new("sol", "SOLIDIFY"); m.thickness = th; m.offset = -1
        o.data.materials.append(mat(inner)); m.material_offset = 1; m.material_offset_rim = 1
        b = o.modifiers.new("cut", "BOOLEAN"); b.operation = 'DIFFERENCE'; b.object = cutter
    S["casing"] = box((44, 30, 80), (0, 0, 40), WHITE); cutobj(S["casing"], cut)
    # panel de mandos (parte baja que no se corta)
    box((30, 0.6, 5), (0, -15.1, 4.5), (0.2, 0.21, 0.24))
    S["pantalla"] = box((9, 0.4, 3.2), (-6, -15.5, 4.5), (0.25, 0.75, 1.0), unique=True)
    for k in range(3): cyl(1.1, 0.8, (5 + 4 * k, -15.6, 4.5), (0.85, 0.85, 0.87), rot=(math.pi / 2, 0, 0))
    # cámara de combustión (fondo oscuro para que resalte la llama)
    box((40, 1, 66), (0, 9, 45), CHAMB)
    box((32, 1.0, 0.8), (0, 4, 44.5), (0.3, 0.3, 0.34))
    # salida de humos (chimenea cortada por la mitad)
    S["flue"] = cyl(4.2, 26, (0, 0, 92), (0.72, 0.74, 0.78), v=40); cutobj(S["flue"], cut2, th=0.6, inner=(0.4, 0.41, 0.45))
    cyl(5.2, 1.2, (0, 0, 80.6), (0.55, 0.56, 0.6))
    S["cap"] = cyl(6.5, 1.0, (0, 0, 108), (0.55, 0.56, 0.6))
    cone = bpy.ops.mesh.primitive_cone_add(radius1=6, radius2=0.5, depth=3, location=(0, 0, 110.2), vertices=32); setup(bpy.context.object, (0.55, 0.56, 0.6))
    for sx in (-1, 1): box((0.6, 0.6, 3), (sx * 4.5, 0, 106.5), (0.55, 0.56, 0.6))
    box((12, 0.6, 1.2), (0, -6.5, 74), (0.5, 0.5, 0.55))
    # quemador, electrodo y gas
    box((28, 5, 2.2), (0, 0, 21), (0.4, 0.41, 0.45))
    for x in FLX: box((1.6, 3, 0.5), (x, 0, 22.2), (0.15, 0.15, 0.17))
    cyl(0.25, 4, (-14.5, -1.5, 23.5), (0.85, 0.85, 0.85), rot=(0, 0.4, 0))
    S["chispa"] = sph(1.0, LEJOS, (1.0, 0.95, 0.5), seg=10)
    pipe_path([(4, -24), (4, 11), ], GASC, 1.0)
    pipe_path([(4, 15), (4, 20)], GASC, 1.0)
    box((5, 4.5, 5), (4, 0, 13), (0.3, 0.31, 0.35)); cyl(1.2, 1.0, (4, -2.6, 13), GASC, rot=(math.pi / 2, 0, 0))
    S["gas"] = [sph(0.75, LEJOS, GASC, seg=8) for _ in range(12)]
    # llamas
    S["llamas"] = []
    for x in FLX:
        e = empty((x, 0, 22.4))
        bpy.ops.mesh.primitive_cone_add(radius1=1.25, radius2=0.05, depth=5.5, location=(0, 0, 2.75), vertices=16); setup(bpy.context.object, FLAME, parent=e)
        bpy.ops.mesh.primitive_cone_add(radius1=0.7, radius2=0.05, depth=3.0, location=(0, -0.7, 1.5), vertices=12); setup(bpy.context.object, FLAME2, parent=e)
        S["llamas"].append(e)
    # intercambiador principal (serpentín) con material compartido
    m1 = mat(TUBE, unique=True); S["coil1"] = []
    for (x0, z0), (x1, z1) in zip(COIL1, COIL1[1:]):
        o = bar_obj(None, 1.3); o.data.materials.append(m1); bar_set(o, (x0, 0, z0), (x1, 0, z1)); S["coil1"].append(o)
    for x, z in COIL1[1:-1]:
        o = sph(1.3, (x, 0, z), None, seg=12); o.data.materials.append(m1); S["coil1"].append(o)
    for k in range(-14, 15, 2): box((0.3, 5, 11.5), (k, 1.5, 35), (0.5, 0.52, 0.56))   # aletas
    # tuberías interiores del circuito A
    pipe_path([(14, -2), (14, 20), (17.5, 20), (17.5, 30), (15, 30)], COPPER, 1.2)
    pipe_path([(-15, 40), (-17.5, 40), (-17.5, -2)], COPPER, 1.2)
    # bomba
    S["bomba"] = empty((14, 0, 13)); b = S["bomba"]
    cyl(4.0, 5, (0, 0, 0), PUMP, parent=b, rot=(math.pi / 2, 0, 0)); cyl(2.6, 4, (0, 4.5, 0), (0.3, 0.32, 0.38), parent=b, rot=(math.pi / 2, 0, 0))
    cyl(3.3, 0.3, (0, -2.6, 0), (0.12, 0.14, 0.2), parent=b, rot=(math.pi / 2, 0, 0))
    S["rodete"] = empty((0, -2.85, 0), parent=b)
    for k in range(5): box((5.6, 0.3, 0.9), (0, 0, 0), (0.9, 0.9, 0.92), parent=S["rodete"], rot=(0, k * math.pi / 5, 0))
    cyl(0.8, 0.5, (0, -0.1, 0), (0.95, 0.75, 0.2), parent=S["rodete"], rot=(math.pi / 2, 0, 0))
    # tuberías exteriores y radiador (debajo)
    pipe_path([(-17.5, -2), (-17.5, -30), (-32, -30), (-32, -41), (-26.5, -41)], COPPER, 1.2)
    pipe_path([(26.5, -75), (32, -75), (32, -30), (14, -30), (14, -2)], COPPER, 1.2)
    S["rad"] = []; mr = mat(RAD, unique=True)
    for k in range(13):
        o = rounded_slab(3.4, 8, 1.4, 40, (-24 + 4 * k, 2, -78), None); o.data.materials.append(mr); S["rad"].append(o)
    for z in (-42, -74):
        o = cyl(1.4, 52, (0, 2, z), None, rot=(0, math.pi / 2, 0)); o.data.materials.append(mr); S["rad"].append(o)
    for x in (-18, 18): box((2, 6, 2), (x, 10, -50), (0.4, 0.4, 0.42))
    cyl(1.6, 3, (-26.5, 2, -41), CHROME, rot=(0, math.pi / 2, 0)); cyl(1.6, 3, (26.5, 2, -75), CHROME, rot=(0, math.pi / 2, 0))
    S["agua"] = [sph(0.95, LEJOS, COLDW, seg=10, unique=True) for _ in range(84)]
    # flechas de calor
    S["fcal"] = [arrow((1.0, 0.3, 0.2), 0.35, 3.0) for _ in range(5)]
    S["frad"] = [arrow((1.0, 0.35, 0.25), 0.55, 6.0) for _ in range(4)]
    S["fchim"] = [arrow((1.0, 0.3, 0.2), 0.8, 7.0) for _ in range(3)]
    S["fcond"] = [arrow((1.0, 0.35, 0.2), 0.25, 1.8) for _ in range(6)]
    # humo
    S["humo"] = [sph(r, LEJOS, SMOKEH, seg=10, unique=True) for (_, _, _, r, _) in SMK]
    # segundo intercambiador (aparece) + tuberías nuevas
    S["inter2"] = empty((0, 0, 54)); i2 = S["inter2"]; m2 = mat(TUBE, unique=True); S["m2o"] = None
    for (x0, z0), (x1, z1) in zip(COIL2, COIL2[1:]):
        o = bar_obj(None, 1.3, parent=i2); o.data.materials.append(m2); bar_set(o, (x0, 0, z0 - 54), (x1, 0, z1 - 54)); S["m2o"] = o
    for x, z in COIL2[1:-1]:
        o = sph(1.3, (x, 0, z - 54), None, parent=i2, seg=12); o.data.materials.append(m2)
    for k in range(-14, 15, 2): box((0.3, 5, 9.5), (k, 1.5, 0), (0.5, 0.52, 0.56), parent=i2)
    S["nuevas"] = [bar_obj(COPPER, 1.2) for _ in range(4)]
    S["bandeja"] = empty((0, 0, 46.5)); bj = S["bandeja"]
    box((36, 6, 0.7), (0, 1, 0), (0.6, 0.62, 0.66), parent=bj, rot=(0, -0.03, 0))
    box((36, 0.6, 1.6), (0, -2, 0.5), (0.6, 0.62, 0.66), parent=bj, rot=(0, -0.03, 0))
    S["dren"] = [bar_obj((0.95, 0.95, 0.97), 0.8) for _ in range(4)]
    S["gotas"] = [sph(1.0, LEJOS, DROP, seg=10) for _ in DRP]
    S["goteo"] = [sph(0.8, LEJOS, DROP, seg=10) for _ in range(4)]
    S["charco"] = cyl(2.2, 0.4, (-6, 2, -31.5), DROP, unique=True)
    bpy.ops.mesh.primitive_cone_add(radius1=1.0, radius2=2.8, depth=3, location=(-6, 2, -31), vertices=24); setup(bpy.context.object, (0.92, 0.92, 0.94))
    o = bar_obj((0.92, 0.92, 0.94), 0.9); bar_set(o, (-6, 2, -32), (-6, 2, -36)); o = bar_obj((0.92, 0.92, 0.94), 0.9); bar_set(o, (-6, 2, -36), (-6, 14, -36))
    # grifo y fregadero (izquierda), termostato
    box((26, 18, 1.5), (-52, 6, -31), (0.85, 0.85, 0.86)); box((22, 14, 7), (-52, 6, -35), (0.7, 0.72, 0.75))
    box((26, 18, 1.0), (-52, 6, -30.4), (0.92, 0.92, 0.92))
    box((20, 12, 0.5), (-52, 6, -30.1), (0.55, 0.57, 0.6))
    cyl(2.2, 1, (-52, 15.2, -12), CHROME, rot=(math.pi / 2, 0, 0)); cyl(1.4, 4, (-52, 13, -12), CHROME, rot=(math.pi / 2, 0, 0))
    o = bar_obj(CHROME, 0.9); bar_set(o, (-52, 11, -12), (-52, 4, -13)); o = bar_obj(CHROME, 0.9); bar_set(o, (-52, 4, -13), (-52, 2.5, -16))
    S["palanca"] = empty((-52, 12, -10)); box((1.2, 7, 1.0), (0, -3.2, 0.4), CHROME, parent=S["palanca"]); sph(0.9, (0, -6.6, 0.4), (0.9, 0.2, 0.2), parent=S["palanca"])
    S["chorro"] = bar_obj((0.55, 0.8, 1.0), 0.55, unique=True)
    S["vaho"] = [sph(1.3, LEJOS, (0.95, 0.95, 0.97), seg=8) for _ in range(5)]
    S["termostato"] = empty((-52, 15, 14)); ts = S["termostato"]
    rounded_slab(9, 12, 2, 1.6, (0, 0, 0), (0.95, 0.95, 0.95), parent=ts).rotation_euler = (math.pi / 2, 0, 0)
    S["tpant"] = box((6.6, 0.4, 4.6), (0, -1.75, 1.6), (0.15, 0.2, 0.28), parent=ts, unique=True)
    S["tdial"] = cyl(1.7, 0.6, (0, -1.9, -3.2), (0.8, 0.8, 0.82), parent=ts, rot=(math.pi / 2, 0, 0))
    dyn = [cam, S["cut"], S["casing"], S["pantalla"], S["flue"], S["chispa"], S["gas"], S["llamas"], S["coil1"], S["bomba"], S["rad"],
           S["agua"], S["fcal"], S["frad"], S["fchim"], S["fcond"], S["humo"], S["inter2"], S["nuevas"], S["bandeja"], S["dren"],
           S["gotas"], S["goteo"], S["charco"], S["palanca"], S["chorro"], S["vaho"], S["termostato"]]
    join_static(dyn)
    return sc, S

# --------------------------------------------------------------------------------------------------
def flame_level(t):
    on1 = seg(t, -0.25, 0.3) * (1 - seg(t, T("abres") - 0.15, T("abres") + 0.25))
    on2 = seg(t, T("se enciende una") + 0.1, T("se enciende una") + 0.5)
    lvl = max(on1, on2)
    return lvl * (1 - 0.25 * seg(t, T("gastan") - 0.1, T("menos", fin=True)))
def ignite_t(t):
    return -2.0 if t < T("abres") else T("se enciende una") + 0.1

def cmix(a, b, u): return tuple(x + (y - x) * u for x, y in zip(a, b))

def wcolor(temp, hf):
    temp = 40 + (temp - 40) * hf if temp > 40 else temp
    u = max(0, min(1, (temp - 30) / 40))
    return tuple(mix(c, h, u) for c, h in zip(COLDW, HOTW))

def pose(t, S):
    t_abr, t_sube, t_gas, t_enc, t_encima, t_calien = T("abres"), T("o sube"), T("entra gas"), T("se enciende una"), T("encima"), T("que se calienta")
    t_bomba, t_rads, t_casa, t_vuelve = T("una bomba"), T("radiadores"), T("que calientan"), T("y vuelve")
    t_pero, t_co2, t_vap, t_ant, t_conel = T("pero al quemar"), T("dióxido"), T("vapor"), T("las calderas antiguas"), T("y con él")
    t_nuev, t_seg, t_donde, t_enfr, t_liq, t_cond, t_suelta = T("así que las nuevas"), T("segundo"), T("donde llega"), T("el humo se enfría"), T("líquido"), T("y al condensarse"), T("suelta")
    t_poreso, t_gotea, t_curioso, t_gastan = T("por eso"), T("gotea"), T("y aquí"), T("gastan")
    hook = t < t_abr
    fl = flame_level(t)
    for k, e in enumerate(S["llamas"]):
        f = 0.85 + 0.15 * math.sin(t * 19 + k * 2.1) + 0.06 * math.sin(t * 41 + k)
        e.scale = (max(fl, 0.001), max(fl, 0.001), max(fl * f, 0.001)); e.hide_render = fl < 0.02
    # chispa del encendido
    sp = (0.0 <= t < 0.3) or (t_enc - 0.15 < t < t_enc + 0.25)
    S["chispa"].location = (-12.8, -2.2, 24.5) if sp and int(t * 30) % 2 == 0 else LEJOS
    # gas
    gas_on = (t < t_abr - 0.1) or (t > t_gas - 0.1)
    for k, o in enumerate(S["gas"]):
        u = (t * 0.9 + k / 12) % 1
        o.location = poly([(4, -1.5, -24), (4, -1.5, 11), (4, -3, 13), (4, -1.5, 15), (4, -1.5, 20.5)], u) if gas_on else LEJOS
    # calor del intercambiador
    hf = 1.0 if hook else seg(t, t_calien - 0.4, t_calien + 0.9)
    hf *= 1 if t < t_abr - 0.2 or t > t_enc else 1 - seg(t, t_abr - 0.2, t_abr + 0.6)
    set_color(S["coil1"][0], tuple(mix(c, h, 0.75 * hf * max(fl, 0.3)) for c, h in zip(TUBE, TUBEHOT)))
    # agua circulando
    loopB = t > t_donde
    P, Tm, Sm = (PB, TB, SB) if loopB else (PA, TA, SA)
    water_on = hook or t > t_encima - 0.2
    spd = 22.0
    vis_len = 1e9
    if not hook and t < t_vuelve + 1.5:
        coil_len = COIL_S1 - COIL_S0
        vis_len = coil_len + max(0, t - t_bomba) * (SA[-1] - coil_len) / max(t_vuelve + 1.2 - t_bomba, 0.1)
    ret_cold = seg(t, T("para que") - 0.2, T("volver fría", fin=True))
    for k, o in enumerate(S["agua"]):
        if not water_on: o.location = LEJOS; continue
        s = k / len(S["agua"]) * Sm[-1] + t * spd * (1 if (hook or t > t_bomba) else 0.35)
        p, temp = at_s(P, Tm, Sm, s)
        if not loopB:
            rel = (s - COIL_S0) % Sm[-1]
            if rel > vis_len: o.location = LEJOS; continue
        o.location = p
        if temp <= 40.5: temp = 40 - 10 * ret_cold
        set_color(o, wcolor(temp, hf))
    rot = t * 14 if (hook or t > t_bomba - 0.3) else 0
    S["rodete"].rotation_euler = (0, rot, 0)
    pu = win01(t, t_bomba, t_bomba + 0.8, 0.2, 0.5); s = 1 + 0.12 * pu; S["bomba"].scale = (s, s, s)
    # radiador
    rh = 1.0 if hook else seg(t, t_casa - 0.8, t_casa + 0.6)
    set_color(S["rad"][0], tuple(mix(c, h, 0.6 * rh) for c, h in zip(RAD, RADHOT)))
    rf = win01(t, t_casa - 0.3, t_pero, 0.4, 0.4) + win01(t, T("sesenta") - 0.3, T("desde dos"), 0.4, 0.4)
    for k, a in enumerate(S["frad"]):
        u = (t * 0.6 + k / 4) % 1
        if rf > 0.02: aim(a, Vector((-18 + 12 * k, -4, -36 + 14 * u)), (0, 0, 1), rf * 1.0 * math.sin(math.pi * u) + 0.001)
        else: a.location = LEJOS
    # calor llama → tubo
    cf = win01(t, t_calien - 0.5, t_bomba + 0.4, 0.3, 0.4)
    for k, a in enumerate(S["fcal"]):
        u = (t * 1.2 + k / 5) % 1
        if cf > 0.02: aim(a, Vector((-12 + 6 * k, -3.0, 25.5 + 2.5 * u)), (0, 0, 1), cf * math.sin(math.pi * u) + 0.001)
        else: a.location = LEJOS
    # humo
    t_ig = ignite_t(t); cool = seg(t, t_enfr, t_liq + 0.5) if loopB else 0.0
    smoke_on = fl > 0.3
    rate = 0.26
    for k, (o, (x0, y0, kind, r, ph)) in enumerate(zip(S["humo"], SMK)):
        u = (t * rate + k / len(SMK)) % 1
        if not smoke_on or (t - t_ig) * rate < u: o.location = LEJOS; continue
        w = 1.4 * math.sin(t * 2 + ph)
        pts = [(x0, y0, 27), (x0 * 0.95 + w, y0, 44), (x0 * 0.9 - w, y0, 60), (x0 * 0.35, y0 * 0.5, 70), (w * 0.3, -1.2, 79),
               (w * 0.3, -1.2, 104), (w * 2 + 3 * math.sin(ph), -1.2, 122)]
        p = poly(pts, u); o.location = p
        z = p.z
        heat = 1.0 if z < 44 else (0.62 if z < 60 else 0.62 * (1 - cool))
        if kind == 0: base = cmix(SMOKEH, CO2C, seg(t, t_co2, t_co2 + 0.5) * 0.85)
        else: base = cmix(SMOKEH, VAPC, seg(t, t_vap, t_vap + 0.5) * 0.85)
        if z > 44: base = tuple(mix(b, h, 0.25 * heat) for b, h in zip(base, SMOKEH))
        if z > 60 and cool > 0: base = tuple(mix(b, c, 0.7 * cool) for b, c in zip(base, COOLS))
        sc_ = r
        if kind == 1 and cool > 0 and z > 52: sc_ = r * max(0.001, 1 - cool * seg(z, 52, 60))
        if z > 104: sc_ *= max(0.001, 1 - (z - 104) / 18)
        o.scale = (sc_ / r, sc_ / r, sc_ / r); set_color(o, base)
    # flechas de calor por la chimenea (calderas antiguas)
    ch = win01(t, t_conel - 0.3, t_nuev + 0.3, 0.3, 0.4)
    for k, a in enumerate(S["fchim"]):
        u = (t * 0.7 + k / 3) % 1
        if ch > 0.02: aim(a, Vector((-9 + 9 * k, -2, 104 + 8 * u)), (0, 0, 1), ch * math.sin(math.pi * u) + 0.001)
        else: a.location = LEJOS
    # segundo intercambiador
    g2 = seg(t, t_nuev + 0.4, t_seg + 0.6)
    S["inter2"].location = (0, 0, 54) if g2 > 0.01 else LEJOS; show(S["inter2"], g2 > 0.01)
    S["inter2"].scale = (max(g2, 0.001), 1, max(g2, 0.001))
    c2 = seg(t, t_suelta - 0.2, t_suelta + 1.2) * 0.5
    set_color(S["m2o"], tuple(mix(c, h, c2) for c, h in zip(TUBE, TUBEHOT)))
    np_ = seg(t, t_seg + 0.2, t_donde + 0.3)
    for o, (a, b) in zip(S["nuevas"], (((14, 0, 20), (19.5, 0, 20)), ((19.5, 0, 20), (19.5, 0, 51)), ((19.5, 0, 51), (15, 0, 51)), ((15, 0, 57), (17.5, 0, 57)))):
        grow_bar(o, a, b, np_)
    # bandeja y drenaje
    bd = seg(t, t_enfr - 0.3, t_enfr + 0.4)
    S["bandeja"].location = (0, 0, 46.5) if bd > 0.01 else LEJOS; show(S["bandeja"], bd > 0.01); S["bandeja"].scale = (max(bd, 0.001), 1, 1)
    DREN = [(-18.5, 4, 46.5), (-20.5, 4, 46.5), (-20.5, 4, 2.5), (-6, 4, 2.5), (-6, 4, -14)]
    for k, o in enumerate(S["dren"]):
        grow_bar(o, DREN[k], DREN[k + 1], seg(t, t_enfr + 0.1 * k, t_enfr + 0.5 + 0.1 * k))
    drops_on = loopB and t > t_liq - 0.3
    for k, (o, (zr, xr)) in enumerate(zip(S["gotas"], DRP)):
        if not drops_on: o.location = LEJOS; continue
        tt = t - (t_liq - 0.3) - k * 0.12
        if tt < 0: o.location = LEJOS; continue
        u = (tt * 0.22) % 1
        if u < 0.12:
            g = u / 0.12; o.location = (xr, -1.4, zr - 1.5); s = 0.2 + 0.8 * g
        elif u < 0.22:
            g = (u - 0.12) / 0.10; z0 = zr - 1.5; o.location = (xr, -1.4 + 2.4 * g, mix(z0, 47.4, g * g)); s = 1
        else:
            g = (u - 0.22) / 0.78
            o.location = poly([(xr, 1.0, 47.4), (-18.5, 2.5, 47.6), (-20.5, 2.5, 46.5), (-20.5, 2.5, 2.5), (-6, 2.5, 2.5), (-6, 2.5, -14), (-6, 2.0, -15.5)], g); s = 0.8
        o.scale = (s, s, s * 1.15)
    # goteo por debajo
    dr = t > t_poreso - 1.0
    for k, o in enumerate(S["goteo"]):
        u = (t * 0.9 + k / 4) % 1
        if dr: o.location = (-6, 2.0, -15.5 - 14 * u * u) if u < 0.98 else LEJOS; s = 0.6 + 0.4 * min(1, u * 5); o.scale = (s * 0.8, s * 0.8, s * 1.3)
        else: o.location = LEJOS
    cc = seg(t, t_poreso, t_curioso + 2) if dr else 0
    S["charco"].scale = (max(cc, 0.001), max(cc, 0.001), 1); S["charco"].hide_render = cc < 0.02
    # flechas de calor de la condensación
    cd = win01(t, t_cond - 0.2, t_poreso, 0.3, 0.4)
    for k, a in enumerate(S["fcond"]):
        u = (t * 1.3 + k / 6) % 1; zr = 51 if k % 2 else 57
        if cd > 0.02: aim(a, Vector((-12 + 5 * k, -2.6, zr - 3.4 + 1.6 * u)), (0, 0, 1), cd * math.sin(math.pi * u) + 0.001)
        else: a.location = LEJOS
    # grifo y termostato
    op = seg(t, t_abr - 0.2, t_abr + 0.4) * (1 - seg(t, t_gas + 1.5, t_gas + 2.2))
    S["palanca"].rotation_euler = (0, 0, -0.9 * op)
    if op > 0.3:
        L = 13.5 * min(1, (op - 0.3) / 0.4) + 0.3 * math.sin(t * 30); bar_set(S["chorro"], (-52, 2.5, -16.5), (-52, 2.5, -16.5 - L))
    else: hide_bar(S["chorro"])
    hv = seg(t, t_enc + 0.3, t_enc + 1.5) * op
    for k, o in enumerate(S["vaho"]):
        u = (t * 0.5 + k / 5) % 1
        if hv > 0.05: o.location = (-52 + 3 * math.sin(k * 2 + u * 4), 2.0, -26 + 22 * u); s = hv * math.sin(math.pi * u) + 0.001; o.scale = (s, s, s)
        else: o.location = LEJOS
    S["tdial"].rotation_euler = (math.pi / 2, 0, -1.6 * seg(t, t_sube + 0.2, t_sube + 1.2))
    set_color(S["tpant"], tuple(mix(a, b, seg(t, t_sube + 0.2, t_sube + 0.8)) for a, b in zip((0.15, 0.2, 0.28), (0.95, 0.55, 0.2))))
    set_color(S["pantalla"], (0.25, 0.75, 1.0) if fl > 0.3 else (0.12, 0.2, 0.26))
    apply_cam(S["cam"], *cam_state(t, CAM(), drift=0.35))

def VD(at, dist, yaw, pitch, lens=40):
    at = Vector(at); y, p = math.radians(yaw), math.radians(pitch)
    return (tuple(at + dist * Vector((math.sin(y) * math.cos(p), -math.cos(y) * math.cos(p), math.sin(p)))), tuple(at), lens)

_CAM = None
def CAM():
    global _CAM
    if _CAM: return _CAM
    k = []
    def add(t, v): k.append((t,) + v)
    add(0.0, VD((-2, 0, 25), 40, -18, 12))
    add(1.6, VD((0, 0, 30), 52, -8, 10))
    add(T("sabías"), VD((0, 0, 44), 105, 10, 8))
    add(T("mira por"), VD((0, 0, 40), 92, -6, 6))
    add(T("abres") + 0.2, VD((-50, 4, -16), 58, -18, 14))
    add(T("o sube") + 0.4, VD((-50, 12, 12), 44, -10, 4))
    add(T("entra gas") + 0.1, VD((2, 0, 16), 62, -14, 8))
    add(T("encima") + 0.2, VD((0, 0, 32), 64, 10, 10))
    add(T("una bomba"), VD((8, 0, 22), 82, 14, 6))
    add(T("radiadores") + 0.2, VD((0, 0, -16), 190, 6, 4))
    add(T("que calientan") + 0.5, VD((0, 0, -50), 112, -10, 10))
    add(T("y vuelve") + 0.6, VD((10, 0, -20), 150, 10, 6))
    add(T("pero al quemar") + 0.3, VD((0, 0, 32), 78, -10, 8))
    add(T("vapor") , VD((0, 0, 46), 84, 8, 6))
    add(T("las calderas antiguas") + 0.4, VD((0, 0, 98), 118, -6, 6))
    add(T("y con él") + 0.5, VD((0, 0, 106), 100, 8, 4))
    add(T("así que las nuevas") + 0.4, VD((0, 0, 52), 74, -8, 6))
    add(T("donde llega") + 0.2, VD((4, 0, 38), 112, 12, 6))
    add(T("el humo se enfría") + 0.2, VD((0, 0, 54), 58, -14, 8))
    add(T("y al condensarse") + 0.3, VD((0, 0, 52), 56, 10, 8))
    add(T("por eso") + 0.2, VD((-6, 0, 10), 82, -10, 10))
    add(T("gotea") + 0.3, VD((-6, 0, -10), 56, 12, 8))
    add(T("y aquí") + 0.3, VD((0, 0, 50), 135, -6, 4))
    add(T("no crea") , VD((0, 0, 52), 128, 8, 4))
    add(T("es que") + 0.6, VD((0, 0, 58), 82, -6, 4))
    add(T("para que") + 0.2, VD((10, 0, 36), 90, 14, 6))
    add(T("sesenta") , VD((0, 0, -30), 175, 0, 5))
    add(T("desde dos") + 0.3, VD((0, 0, 30), 150, -14, 6))
    add(T("gastan") + 0.2, VD((0, 0, 28), 78, -4, 8))
    add(DUR, VD((0, 0, 32), 150, 8, 6))
    add(DUR + 3, VD((0, 0, 32), 160, 10, 6))
    _CAM = k; return k

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v)
    return {"llama": Pj((0, -2, 27)), "gas": Pj((4, -3, 6)), "coil": Pj((0, -2, 41.5)), "bomba": Pj((14, -4, 13)),
            "rad": Pj((0, -3, -40)), "ida": Pj((-17.5, -1.5, -14)), "vuelta": Pj((14, -1.5, -14)), "termo": Pj((-52, 13, 15.5)),
            "grifo": Pj((-52, 2, -14)), "humo": Pj((0, -2, 66)), "chim": Pj((0, 0, 112)), "inter2": Pj((0, -2, 58.5)),
            "bandeja": Pj((-10, -2, 46)), "tubo": Pj((-6, 2, -10)), "ret2": Pj((19.5, -1.5, 36)), "pant": Pj((-6, -15.5, 4.5))}

if __name__ == "__main__":
    run("caldera", build, pose, anchors)
