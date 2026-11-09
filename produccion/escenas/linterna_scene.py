# «Si tuvieras que inventar una linterna sin pilas…»: una mano agita una linterna en corte (el imán va y viene por la bobina y
# el led brilla); se desmonta; el led apagado, un enchufe y una pila tachados y tu mano; el experimento de Faraday (imán que entra
# en una bobina, 1831); se monta pieza a pieza: tubo, hilo de cobre que se enrolla, imán que entra, pasadas lentas y rápidas con
# flechas de corriente; agitar; corriente a tirones (un sentido, el otro, nada); diodos; condensador que se llena; una bombilla
# antigua lo vacía en un segundo; el led; 30 s de agitar → 5 min de luz; se apaga y vuelves a agitar; linterna de manivela con
# imán giratorio; una pila vieja tachada; final con la linterna agitándose y alumbrando.
import bpy, bmesh, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from mathutils import Vector, Matrix
import linterna_ov as OV

K = OV.K; DUR = OV.DUR
BG = (0.06, 0.07, 0.1); FLOOR = (0.1, 0.11, 0.15)
BODY = (0.32, 0.36, 0.44); BODY_IN = (0.62, 0.66, 0.74); COPPER = (0.9, 0.52, 0.25); RED = (0.92, 0.25, 0.25); BLUE = (0.25, 0.5, 0.95)
STEEL = (0.72, 0.74, 0.78); PCB = (0.15, 0.55, 0.3); DARK = (0.12, 0.12, 0.14); CAPC = (0.2, 0.35, 0.8); CHARGE = (0.35, 0.95, 0.5)
SKIN = (0.93, 0.7, 0.58); LEDOFF = (0.55, 0.58, 0.62); LEDON = (1.0, 0.98, 0.85); BEAM = (1.0, 0.93, 0.6); YEL = (1.0, 0.82, 0.16)
LEJOS = Vector((0, 80, -300))
TH = math.radians(-62)                       # inclinación de la linterna (cabeza arriba a la derecha)
CT, ST = math.cos(TH), math.sin(TH)
FAR = Vector((-30, 0, 0)); CRK = Vector((30, 0, 0))
FONT = os.path.expanduser("~/.fonts/Poppins-Bold.ttf")

def Pw(x, z=0.0, y=0.0, off=0.0):
    """punto local de la linterna → mundo (sin la sacudida)"""
    x = x + off
    return Vector((x * CT + z * ST, y, -x * ST + z * CT))

def font(o):
    if os.path.exists(FONT):
        try: o.data.font = bpy.data.fonts.load(FONT, check_existing=True)
        except Exception: pass

def shell(o, th, inner, cutter):
    m = o.modifiers.new("sol", "SOLIDIFY"); m.thickness = th; m.offset = -1
    o.data.materials.append(mat(inner)); m.material_offset = 1; m.material_offset_rim = 1
    b = o.modifiers.new("cut", "BOOLEAN"); b.operation = 'DIFFERENCE'; b.object = cutter
    return o

def tube_mesh(r, x0, x1, color, parent, cutter, inner=BODY_IN, th=0.08, caps=False):
    o = cyl(r, x1 - x0, ((x0 + x1) / 2, 0, 0), color, parent=parent, rot=(0, math.pi / 2, 0), v=40)
    if not caps:
        bm = bmesh.new(); bm.from_mesh(o.data)
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if len(f.verts) > 4], context='FACES_ONLY'); bm.to_mesh(o.data); bm.free()
    return shell(o, th, inner, cutter)

def half(o):
    """borra la mitad delantera (y<0) de una malla: corte limpio sin booleana"""
    bm = bmesh.new(); bm.from_mesh(o.data)
    mw = o.matrix_basis
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if (mw @ v.co).y < -0.02], context='VERTS'); bm.to_mesh(o.data); bm.free()
    return o

def path_pts(pts, color, r, parent):
    bars = []
    for a, b in zip(pts, pts[1:]):
        o = bar_obj(color, r, parent=parent); bar_set(o, a, b); bars.append(o)
    return bars

def polyline_at(pts, u):
    L = [(Vector(b) - Vector(a)).length for a, b in zip(pts, pts[1:])]; tot = sum(L); d = u * tot
    for (a, b), l in zip(zip(pts, pts[1:]), L):
        if d <= l: return Vector(a).lerp(Vector(b), d / max(l, 1e-6)), (Vector(b) - Vector(a)).normalized()
        d -= l
    return Vector(pts[-1]), (Vector(pts[-1]) - Vector(pts[-2])).normalized()

def arrow(color):
    bpy.ops.mesh.primitive_cone_add(radius1=0.13, radius2=0, depth=0.3, vertices=12, location=(0, 0, 0)); o = bpy.context.object
    setup(o, color, unique=False); o.rotation_mode = 'QUATERNION'; o.location = LEJOS; return o

def place_arrow(o, p, d, s=1.0):
    o.location = p; o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d); o.scale = (s, s, s)

# trazados de cables (coordenadas locales de la linterna)
LEAD = [(-0.85, 0, -1.03), (-3.55, 0, -1.03), (-3.55, 0, -0.62), (-4.1, 0, -0.62)]
LEAD2 = [(0.85, -0.02, -1.16), (-3.75, -0.02, -1.16), (-3.75, -0.02, -0.75), (-4.3, -0.02, -0.75)]
TOPW = [(-3.45, -0.1, 0.55), (-3.45, -0.1, 0.72), (3.9, -0.1, 0.72), (3.9, -0.1, 0.3), (4.05, -0.1, 0.12)]

def hand(parent):
    e = empty((0, 0, 0), parent=parent)
    sph(1.0, (-1.95, 1.8, 0.15), SKIN, parent=e, scale=(1.05, 0.65, 1.15))
    for i, x in enumerate((-2.55, -2.12, -1.7, -1.3)):
        L = 1.55 - 0.15 * abs(i - 1.3)
        cyl(0.19, L + 0.4, (x, 1.45 - L / 2, 1.08), SKIN, parent=e, rot=(math.pi / 2, 0, 0), v=16)
        sph(0.19, (x, 1.25 - L, 1.0), SKIN, parent=e)
    cyl(0.22, 1.3, (-1.75, -0.2, -1.14), SKIN, parent=e, rot=(0, math.pi / 2, 0), v=16)
    sph(0.22, (-1.1, -0.2, -1.14), SKIN, parent=e)
    sph(0.5, (-2.4, 1.2, -1.2), SKIN, parent=e, scale=(1.2, 1.4, 0.8))
    o = cyl(0.75, 4.0, (-2.6, 3.0, -1.2), (0.25, 0.32, 0.55), parent=e, rot=(math.radians(70), 0, 0))
    return e

def build():
    sc, cam = scene_setup(world=BG, shadow=0.35)
    S = {"cam": cam}
    box((200, 0.2, 200), (0, 6, 0), FLOOR)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -10, 0)); cutter = bpy.context.object; cutter.scale = (200, 20, 200); cutter.hide_render = True
    S["cutter"] = cutter
    # ---- linterna (ejes locales: x a lo largo del tubo) ----
    fl = empty((0, 0, 0)); fl.rotation_euler = (0, TH, 0); S["fl"] = fl
    P = {}
    P["tube"] = tube_mesh(0.9, -4.7, 3.6, BODY, fl, cutter, th=0.08)
    P["cap"] = e = empty((0, 0, 0), parent=fl)              # tapa trasera
    shell(cyl(0.9, 0.3, (-4.85, 0, 0), BODY, parent=e, rot=(0, math.pi / 2, 0), v=40), 0.08, BODY_IN, cutter)
    # bobina: vueltas que aparecen una a una
    S["turns"] = []
    for i in range(16):
        tt = []
        for R_ in (1.0, 1.2):
            o = torus(R_, 0.1, (-0.85 + 1.7 * i / 15, 0, 0), COPPER if R_ < 1.1 else (0.97, 0.6, 0.3), parent=fl, rot=(0, math.pi / 2, 0)); half(o); tt.append(o)
        S["turns"].append(tt)
    # imán
    S["mag"] = m = empty(LEJOS, parent=fl)
    cyl(0.55, 0.7, (-0.35, 0, 0), BLUE, parent=m, rot=(0, math.pi / 2, 0))
    cyl(0.55, 0.7, (0.35, 0, 0), RED, parent=m, rot=(0, math.pi / 2, 0))
    for s, x in (("S", -0.35), ("N", 0.35)):
        o = text3d(s, (x, -0.56, 0), 0.45, (1, 1, 1), parent=m, extrude=0.01, rot=(math.pi / 2, 0, -TH * 0), unique=True); font(o)
        o.rotation_euler = (math.pi / 2, -TH, 0)
    # topes (muelles) en los extremos
    P["bump"] = e = empty((0, 0, 0), parent=fl)
    for x0, d in ((-2.85, -1), (2.85, 1)):
        for j in range(4): torus(0.4, 0.06, (x0 + d * 0.13 * j, 0, 0), STEEL, parent=e, rot=(0, math.pi / 2, 0))
    # cables de la bobina
    P["leads"] = e = empty((0, 0, 0), parent=fl)
    path_pts(LEAD, COPPER, 0.045, e); path_pts(LEAD2, (0.75, 0.4, 0.2), 0.045, e)
    # placa con diodos
    P["board"] = e = empty((0, 0, 0), parent=fl)
    box((1.5, 0.08, 1.3), (-3.85, 0.35, 0), PCB, parent=e)
    for (x, z) in ((-4.3, 0.3), (-4.3, -0.3), (-4.0, 0.3), (-4.0, -0.3)):
        cyl(0.08, 0.34, (x, 0.22, z), DARK, parent=e, v=12); cyl(0.085, 0.06, (x, 0.22, z + 0.12), (0.85, 0.85, 0.88), parent=e, v=12)
    # condensador cortado, con la carga dentro
    P["capa"] = e = empty((0, 0, 0), parent=fl)
    o = cyl(0.32, 1.05, (-3.4, 0.12, 0), CAPC, parent=e, v=32); shell(o, 0.05, (0.75, 0.8, 0.95), cutter)
    S["charge"] = box((0.5, 0.4, 1.0), (-3.4, 0.14, -0.48), CHARGE, parent=fl, unique=True)
    # cable de arriba (al led)
    P["topw"] = e = empty((0, 0, 0), parent=fl)
    path_pts(TOPW, (0.85, 0.2, 0.2), 0.04, e)
    # bombilla antigua
    P["bulb"] = e = empty((0, 0, 0), parent=fl)
    cyl(0.25, 0.35, (4.0, 0, 0), STEEL, parent=e, rot=(0, math.pi / 2, 0))
    S["glass"] = sph(0.45, (4.55, 0, 0), (0.85, 0.88, 0.9), parent=e, unique=True)
    # cabeza: reflector + led + cristal
    P["head"] = e = empty((0, 0, 0), parent=fl)
    o = cyl(1.12, 1.25, (4.2, 0, 0), BODY, parent=e, rot=(0, math.pi / 2, 0), v=40); shell(o, 0.1, BODY_IN, cutter)
    bpy.ops.mesh.primitive_cone_add(radius1=0.3, radius2=1.0, depth=0.9, vertices=40, location=(4.25, 0, 0), rotation=(0, math.pi / 2, 0))
    o = bpy.context.object; setup(o, (0.85, 0.87, 0.9), parent=e); half(o)
    S["led"] = sph(0.2, (3.95, 0, 0), LEDOFF, parent=e, unique=True)
    # haz de luz
    bpy.ops.mesh.primitive_cone_add(radius1=1.0, radius2=1.9, depth=3.0, vertices=40, location=(0, 0, 0), rotation=(0, math.pi / 2, 0))
    S["beam"] = o = bpy.context.object; setup(o, BEAM, unique=True); o.parent = fl
    for v in o.data.vertices: v.co.z += 1.5           # base en x=0 local tras rotar
    o.location = (4.82, 0, 0)
    S["parts"] = P
    S["hand"] = hand(fl)
    # flechas de corriente
    S["arr1"] = [arrow(YEL) for _ in range(6)]
    S["arr2"] = [arrow(CHARGE) for _ in range(6)]
    # ---- enchufe y pila ----
    S["plug"] = e = empty(LEJOS)
    box((0.9, 0.9, 1.1), (0, 0, 0), (0.92, 0.92, 0.94), parent=e)
    for x in (-0.22, 0.22): cyl(0.07, 0.6, (x, 0, 0.8), STEEL, parent=e, v=12)
    cyl(0.14, 2.5, (0, 0, -1.7), (0.9, 0.9, 0.92), parent=e, v=12)
    S["bat"] = e = empty(LEJOS)
    S["batb"] = cyl(0.42, 1.9, (0, 0, 0), (0.18, 0.18, 0.2), parent=e, unique=True)
    S["batt"] = cyl(0.43, 0.5, (0, 0, 0.75), (0.85, 0.55, 0.25), parent=e, unique=True)
    cyl(0.15, 0.15, (0, 0, 1.05), STEEL, parent=e)
    S["crust"] = [sph(0.12 + 0.05 * (j % 3), (0.3 * math.cos(j * 1.7), -0.25 - 0.1 * math.sin(j), 0.85 - 0.18 * j), (0.82, 0.88, 0.75), parent=e, unique=True) for j in range(6)]
    # ---- experimento de Faraday ----
    S["far"] = e = empty(FAR)
    for i in range(12): torus(1.25, 0.09, (-1.1 + 2.2 * i / 11, 0, 0), COPPER, parent=e, rot=(0, math.pi / 2, 0))
    cyl(1.05, 2.4, (0, 0, 0), (0.85, 0.75, 0.55), parent=e, rot=(0, math.pi / 2, 0))
    path_pts([(1.2, 0, -1.25), (2.6, 0, -1.25), (2.6, 0, -2.6)], COPPER, 0.05, e)
    path_pts([(-1.2, 0, -1.25), (-1.6, 0, -2.6)], COPPER, 0.05, e)
    S["fmag"] = m = empty(FAR + Vector((-5, -0.0, 0)))
    box((1.6, 0.7, 0.7), (-0.8, 0, 0), BLUE, parent=m); box((1.6, 0.7, 0.7), (0.8, 0, 0), RED, parent=m)
    for s, x in (("S", -0.8), ("N", 0.8)):
        o = text3d(s, (x, -0.36, 0), 0.45, (1, 1, 1), parent=m, extrude=0.01, rot=(math.pi / 2, 0, 0), unique=True); font(o)
    # ---- linterna de manivela ----
    S["crk"] = e = empty(CRK)
    o = box((5.0, 2.0, 3.2), (0, 0, 0), (0.95, 0.55, 0.15), parent=e); shell(o, 0.1, (0.98, 0.85, 0.65), cutter)
    S["rotor"] = r = empty(CRK + Vector((0.6, 0.1, 0)))
    cyl(0.75, 0.6, (0, 0, 0), STEEL, parent=r, rot=(math.pi / 2, 0, 0))
    box((0.7, 0.2, 1.4), (-0.36, -0.32, 0), BLUE, parent=r); box((0.7, 0.2, 1.4), (0.36, -0.32, 0), RED, parent=r)
    for sx in (-1, 1):
        for j in range(7): torus(0.55, 0.07, (0.6 + sx * (1.05 + 0.12 * j), 0.1, 0), COPPER, parent=e, rot=(0, math.pi / 2, 0))
    for sx in (-1, 1): box((0.25, 0.6, 1.2), (0.6 + sx * 1.0, 0.1, 0), (0.45, 0.45, 0.5), parent=e)
    S["gear"] = g = empty(CRK + Vector((-1.2, 0.2, -0.3)))
    cyl(0.75, 0.25, (0, 0, 0), STEEL, parent=g, rot=(math.pi / 2, 0, 0))
    for j in range(16):
        a = j / 16 * math.tau; box((0.16, 0.25, 0.18), (0.82 * math.cos(a), 0, 0.82 * math.sin(a)), STEEL, parent=g, rot=(0, -a, 0))
    S["crank"] = c = empty(CRK + Vector((-1.2, -1.2, -0.3)))
    box((0.3, 0.2, 1.8), (0, 0, 0.8), DARK, parent=c); cyl(0.2, 0.7, (0, -0.4, 1.6), (0.9, 0.3, 0.25), parent=c, rot=(math.pi / 2, 0, 0))
    cyl(0.12, 1.2, (0, 0.5, 0), STEEL, parent=c, rot=(math.pi / 2, 0, 0))
    S["cled"] = sph(0.3, CRK + Vector((2.6, 0, 0.6)), LEDOFF, unique=True)
    bpy.ops.mesh.primitive_cone_add(radius1=0.5, radius2=1.6, depth=3.0, vertices=32, location=CRK + Vector((4.1, 0, 0.6)), rotation=(0, math.pi / 2, 0))
    S["cbeam"] = o = bpy.context.object; setup(o, BEAM, unique=True)
    dyn = [cam, cutter, fl, S["arr1"], S["arr2"], S["plug"], S["bat"], S["far"], S["fmag"], S["crk"], S["rotor"], S["gear"], S["crank"],
           S["cled"], S["cbeam"]]
    join_static(dyn)
    return sc, S

def grow(o, s):
    s = max(1e-3, s); o.scale = (s, s, s)

def appear(t, a, d=0.4):
    u = seg(t, a, a + d); return u * (1 + 0.2 * math.sin(min(1, max(0, (t - a - d) / 0.3)) * math.pi))

def pose(t, S):
    k = K; P = S["parts"]; fl = S["fl"]
    built = t < k["vamos"] or t >= k["tubo"]
    gone = 1 - seg(t, k["vamos"], k["vamos"] + 0.6)         # desmontaje al principio
    # sacudida del tubo
    off = OV.shake_off(t)
    fl.location = Vector((CT, 0, -ST)) * off
    def vis(a): return gone if t < k["vamos"] + 1 else appear(t, a)
    grow(P["tube"], vis(k["tubo"])); grow(P["cap"], vis(k["tubo"] + 0.2))
    for i, tt in enumerate(S["turns"]):
        a = k["enrollas"] + 0.2 + i * (k["metes"] - k["enrollas"] - 0.4) / 16
        s = gone if t < k["vamos"] + 1 else seg(t, a, a + 0.15)
        for o in tt: grow(o, s)
    grow(P["bump"], vis(k["metes"] + 1.0)); grow(P["leads"], vis(k["cada"]))
    grow(P["board"], vis(k["diodos"])); grow(P["capa"], vis(k["cond"]))
    grow(P["topw"], vis(k["bombilla"]))
    bulb = appear(t, k["bombilla"]) * (1 - seg(t, k["led"], k["led"] + 0.3)) if t > k["vamos"] + 1 else 0.0
    grow(P["bulb"], bulb)
    headv = vis(k["led"]) if t > k["vamos"] + 1 else gone
    if k["vamos"] + 0.6 < t < k["tubo"]:      # el led apagado, solo, mientras faltan electricidad y pilas
        headv = 1 - seg(t, k["truco"], k["truco"] + 0.4)
    grow(P["head"], headv)
    # imán
    mx = OV.mag_x(t)
    mv = gone if t < k["vamos"] + 1 else (1.0 if t > k["metes"] else 0.0)
    S["mag"].location = Vector((mx, 0, 0)) if mv > 0.01 else LEJOS
    grow(S["mag"], max(mv, 1e-3) if mv > 0.01 else 1)
    # carga del condensador
    L = OV.level(t)
    cv = P["capa"].scale.x
    S["charge"].scale = (cv, cv, max(1e-3, L * 0.96 * cv)); S["charge"].location = (-3.4, 0.14, -0.48 + 0.48 * L * cv * 0 )
    S["charge"].location = (-3.4, 0.14, -0.48 * cv + 0.48 * L * cv)
    # brillo
    b = OV.bright(t)
    bulb_on = k["bombilla"] + 0.6 <= t < k["led"]
    set_color(S["glass"], tuple(mix(c0, c1, b if bulb_on else 0) for c0, c1 in zip((0.85, 0.88, 0.9), (1.0, 0.85, 0.35))))
    set_color(S["led"], tuple(mix(c0, c1, 0 if bulb_on else b) for c0, c1 in zip(LEDOFF, LEDON)))
    bb = b if (P["head"].scale.x > 0.5 or bulb_on) else 0.0
    S["beam"].scale = (max(1e-3, bb),) * 3
    S["beam"].location = (4.82 if not bulb_on else 5.0, 0, 0)
    # flechas de corriente en el cable de la bobina
    e = OV.emf(t); a1 = abs(e) > 1.0 and P["leads"].scale.x > 0.5
    rect = t > k["diodos"] + 0.8
    for i, o in enumerate(S["arr1"]):
        if a1:
            ph = (i / 6 + 0.6 * t * (1 if e > 0 else -1)) % 1.0
            p, d = polyline_at(LEAD, ph); d = d if e > 0 else -d
            place_arrow(o, fl.matrix_world @ Vector(p), fl.matrix_world.to_3x3() @ d, min(1.4, 0.6 + abs(e) / 15))
        else: o.location = LEJOS
    for i, o in enumerate(S["arr2"]):
        on = b > 0.05 and P["topw"].scale.x > 0.5 and (k["bombilla"] < t < k["otras"] or t > k["ninguna"])
        if on:
            ph = (i / 6 + 0.5 * t) % 1.0; p, d = polyline_at(TOPW, ph)
            place_arrow(o, fl.matrix_world @ Vector(p), fl.matrix_world.to_3x3() @ d, 1.0)
        else: o.location = LEJOS
    # mano
    hv = 0.0
    if t < k["vamos"]: hv = 1.0
    elif k["mano"] - 0.2 < t < k["truco"] + 0.3: hv = appear(t, k["mano"] - 0.2) * (1 - seg(t, k["truco"], k["truco"] + 0.3))
    elif k["agitas"] - 0.4 < t < k["otras"]: hv = seg(t, k["agitas"] - 0.4, k["agitas"]) * (1 - seg(t, k["otras"] - 0.4, k["otras"]))
    elif t > k["ninguna"] + 1.5: hv = seg(t, k["ninguna"] + 1.5, k["sig"] - 0.1)
    if k["vamos"] < t < k["vamos"] + 0.6: hv = gone
    S["hand"].location = (0, 0, 0) if hv > 0.01 else LEJOS
    S["hand"].location = Vector((0, 4.0 * (1 - hv), -3.0 * (1 - hv))) if hv > 0.01 else LEJOS
    # enchufe y pila
    HW = Pw(4.2)
    if k["enchufe"] - 0.1 < t < k["truco"] + 0.4:
        sp = appear(t, k["enchufe"]) * (1 - seg(t, k["truco"], k["truco"] + 0.4))
        S["plug"].location = HW + Vector((-2.1, 0.5, -1.6)); grow(S["plug"], sp); S["plug"].rotation_euler = (0, 0.3, 0.3 * math.sin(t * 2))
        S["bat"].location = HW + Vector((2.0, 0.5, -1.6)); grow(S["bat"], appear(t, k["enchufe"] + 0.4) * (1 - seg(t, k["truco"], k["truco"] + 0.4)))
        S["bat"].rotation_euler = (0, -0.3, 0)
    elif t > k["ninguna"] - 0.2:
        S["bat"].location = Pw(-2.0) + Vector((3.2, -0.6, 0.0)); grow(S["bat"], appear(t, k["ninguna"] - 0.2) * (1 - seg(t, k["sig"], k["sig"] + 0.4)))
        S["bat"].rotation_euler = (0, 0.2, 0.15)
        S["plug"].location = LEJOS
    else: S["plug"].location = LEJOS; S["bat"].location = LEJOS
    old = seg(t, k["ninguna"] + 0.5, k["ninguna"] + 1.8)
    set_color(S["batb"], tuple(mix(a, b_, old) for a, b_ in zip((0.18, 0.18, 0.2), (0.35, 0.33, 0.22))))
    set_color(S["batt"], tuple(mix(a, b_, old) for a, b_ in zip((0.85, 0.55, 0.25), (0.45, 0.5, 0.35))))
    for j, c in enumerate(S["crust"]): grow(c, old * (0.6 + 0.4 * math.sin(j)) if old > 0.02 else 1e-3)
    # Faraday: el imán entra y sale de la bobina
    if k["truco"] - 0.5 < t < k["tubo"] + 0.5:
        u = t - k["truco"] - 0.3
        x = -3.4 + 2.6 * (0.5 - 0.5 * math.cos(max(0, u) * 4.2)) if u > 0 else -3.4
        S["fmag"].location = FAR + Vector((x, 0, 0))
    else: S["fmag"].location = LEJOS
    # manivela
    ang = OV.crank_ang(t)
    S["crank"].rotation_euler = (0, ang, 0); S["gear"].rotation_euler = (0, ang, 0); S["rotor"].rotation_euler = (0, -ang * 4, 0)
    cb = 1.0 if t > k["otras"] + 1.0 else 0.0
    set_color(S["cled"], LEDON if cb else LEDOFF)
    S["cbeam"].scale = (max(1e-3, cb),) * 3
    apply_cam(S["cam"], *cam_state(t, CAM(k), drift=0.03))

def V_(at, d, lens=35, h=0.6, x=0.0):
    at = Vector(at); return (tuple(at + Vector((x, -d, h))), tuple(at), lens)

def CAM(k):
    c = []
    def add(t, v): c.append((t,) + v)
    WHOLE = Pw(0.0) + Vector((0, 0, 0.5))
    HW = Pw(4.2)
    WD = 24
    add(0.0, V_(Pw(-0.9) + Vector((0, 0, -0.9)), 9.5))
    add(1.6, V_(Pw(-0.4) + Vector((0, 0, -1.0)), 12))
    add(k["vamos"] - 0.3, V_(WHOLE, WD))
    add(k["vamos"] + 0.6, V_(WHOLE + Vector((0, 0, 0.8)), WD - 1))
    add(k["nec"], V_(HW + Vector((0, 0, -0.8)), 9))
    add(k["enchufe"], V_(HW + Vector((0, 0, -1.2)), 11))
    add(k["mano"], V_(HW + Vector((-0.3, 0, -2.4)), 15))
    add(k["truco"], V_(HW + Vector((-0.3, 0, -2.4)), 15.5))
    add(k["truco"] + 0.5, V_(FAR + Vector((-0.3, 0, -1.2)), 15))
    add(k["truco"] + 1.0, V_(FAR + Vector((-0.3, 0, -1.2)), 15.2))
    add(k["tubo"] - 1.1, V_(FAR + Vector((-0.3, 0, -1.2)), 15.5))
    add(k["tubo"] - 0.6, V_(FAR + Vector((-0.3, 0, -1.2)), 15.6))
    add(k["tubo"] - 0.1, V_(Pw(-0.3) + Vector((0, 0, -0.6)), 14))
    add(k["enrollas"], V_(Pw(-0.3) + Vector((0, 0, -0.6)), 13))
    add(k["metes"], V_(Pw(-0.8) + Vector((0, 0, -0.6)), 13.5))
    add(k["cada"], V_(Pw(0.0) + Vector((0, 0, -0.6)), 12))
    add(k["agitas"] - 0.2, V_(Pw(-0.5) + Vector((0, 0, -0.6)), 13))
    add(k["tirones"], V_(Pw(-0.6) + Vector((0, 0, -0.7)), 13.5))
    add(k["diodos"] + 0.2, V_(Pw(-3.0) + Vector((0, 0, -0.6)), 10.5))
    add(k["cond"] + 0.2, V_(Pw(-2.8) + Vector((0, 0, -0.6)), 10.5))
    add(k["curioso"], V_(WHOLE, WD))
    add(k["led"], V_(WHOLE + Vector((0.2, 0, 0.3)), WD - 0.5))
    add(k["treinta"], V_(WHOLE, WD))
    add(k["otras"] - 0.15, V_(WHOLE, WD + 0.5))
    add(k["otras"] + 0.35, V_(CRK + Vector((1.5, 0, -1.0)), 22))
    add(k["otras"] + 0.8, V_(CRK + Vector((1.5, 0, -1.0)), 22))
    add(k["ninguna"] - 0.8, V_(CRK + Vector((1.7, 0, -1.0)), 22.5))
    add(k["ninguna"] - 0.3, V_(CRK + Vector((1.7, 0, -1.0)), 22.5))
    add(k["ninguna"] + 0.2, V_(WHOLE + Vector((0.3, 0, 0)), WD + 0.5))
    add(k["sig"], V_(WHOLE, WD))
    add(DUR + 2, V_(WHOLE, WD - 1))
    return c

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v); M = S["fl"].matrix_world
    L = lambda x, z=0.0: Pj(M @ Vector((x, -0.3, z)))
    return {"coil": L(0.0, 1.0), "mag": L(OV.mag_x(t), -0.5), "diodes": L(-4.15, -0.3), "cap": L(-3.4, 0.3), "bulb": L(4.6, 0.3),
            "led": L(4.0, 0.3), "tube": L(-1.0, 0.9), "plug": Pj(S["plug"].location), "bat": Pj(S["bat"].location),
            "crank": Pj(CRK + Vector((-1.2, -1.2, 1.3))), "rotor": Pj(CRK + Vector((0.6, -0.5, 0.3)))}

if __name__ == "__main__":
    run("linterna", build, pose, anchors)
