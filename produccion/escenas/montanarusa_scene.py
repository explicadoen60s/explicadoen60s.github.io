# «¿Y si construyes una montaña rusa?»: arranca con el tren cayendo en picado hacia la cámara; después la vía se levanta
# pieza a pieza: estación, subida con cadena (altímetro), la cadena se rompe y el tren cae hacia atrás, dientes y el seguro
# que hace clac, la bajada (velocímetro), la colina donde el vagón saldría volando, las tres ruedas abrazando el raíl,
# el rizo redondo (× 6 tu peso) que se transforma en lágrima (× 4) y, al final, frenos de roce (chispas) frente a
# frenos magnéticos: aletas entre imanes, corrientes en remolino y el tren se para sin tocar nada.
import bpy, bmesh, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from mathutils import Vector, Matrix
import montanarusa_ov as OV

K = OV.K; DUR = OV.DUR
BG = (0.09, 0.1, 0.14); GROUND = (0.17, 0.19, 0.23); RAIL = (0.98, 0.62, 0.12); TIE = (0.32, 0.34, 0.4); SUPP = (0.55, 0.6, 0.68)
CAR = (0.9, 0.2, 0.22); CAR_D = (0.62, 0.12, 0.14); SEAT = (0.14, 0.15, 0.18); SKIN = (0.93, 0.72, 0.58); SHIRT = (0.25, 0.5, 0.95)
WHEEL = (0.18, 0.18, 0.2); HUB = (0.75, 0.77, 0.8); CHAIN = (0.45, 0.47, 0.52); TOOTH = (0.72, 0.75, 0.8); YL = (1.0, 0.82, 0.16)
RED = (0.92, 0.22, 0.2); GREEN = (0.25, 0.85, 0.45); MAG_R = (0.85, 0.2, 0.22); MAG_B = (0.22, 0.42, 0.9); FIN = (0.8, 0.82, 0.86)
PAD = (0.5, 0.36, 0.25); SPARK = (1.0, 0.65, 0.15); PLAT = (0.36, 0.38, 0.44); ROOF = (0.2, 0.45, 0.75); GHOST = (0.55, 0.57, 0.62)
LEJOS = Vector((0, -800, -800))
LW = Vector((400, 0, 0))                     # detalle de las ruedas
NL = 64                                      # tramos del rizo
CAR_GAP = 3.0

def V(p): return Vector(p)
def hide_bar(o): bar_set(o, LEJOS, LEJOS + Vector((0, 0, 0.01)))

def basis(d, m):
    p, t, lat, n = OV.frame(d, m)
    return V(p), V(t), V(lat), V(n)

def orient(o, t, lat, n):
    M = Matrix((t, lat, n)).transposed()
    o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = M.to_quaternion()

def cone(r, h, color, unique=False):
    bpy.ops.mesh.primitive_cone_add(radius1=r, radius2=0, depth=h, location=(0, 0, 0), vertices=16); o = bpy.context.object
    for vv in o.data.vertices: vv.co.z += h / 2
    return setup(o, color, None, True, unique)

def arrow(color, r, unique=False):
    return [bar_obj(color, r=r, unique=unique), cone(r * 2.6, r * 6, color, unique=unique)]

def put_arrow(a, p0, p1):
    p0, p1 = V(p0), V(p1); d = p1 - p0; L = d.length
    if L < 1e-3: hide_arrow(a); return
    hl = min(a[0]["r"] * 6, L * 0.6); q = p1 - d.normalized() * hl
    bar_set(a[0], p0, q); a[1].location = q; a[1].rotation_mode = 'QUATERNION'
    a[1].rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())

def hide_arrow(a):
    hide_bar(a[0]); a[1].location = LEJOS

def tooth_mesh(L, h, w, color):
    me = bpy.data.meshes.new("tooth"); bm = bmesh.new()
    a = [bm.verts.new(p) for p in ((0, -w, 0), (L, -w, 0), (L, -w, h))]
    b = [bm.verts.new(p) for p in ((0, w, 0), (L, w, 0), (L, w, h))]
    bm.faces.new((a[0], a[2], a[1])); bm.faces.new((b[0], b[1], b[2]))
    bm.faces.new((a[0], a[1], b[1], b[0])); bm.faces.new((a[1], a[2], b[2], b[1])); bm.faces.new((a[2], a[0], b[0], b[2]))
    bm.normal_update(); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("tooth", me); bpy.context.collection.objects.link(o)
    return setup(o, color)

def make_car(front):
    e = empty(LEJOS)
    box((2.5, 1.7, 0.75), (0, 0, 0.82), CAR, e)
    box((2.3, 1.74, 0.12), (0, 0, 1.2), CAR_D, e)
    box((0.22, 1.55, 0.75), (-0.75, 0, 1.55), SEAT, e)
    box((0.22, 1.55, 0.75), (0.45, 0, 1.55), SEAT, e)
    for x in (-0.35, 0.85):
        for y in (-0.38, 0.38):
            box((0.42, 0.5, 0.55), (x - 0.15, y, 1.5), SHIRT, e)
            sph(0.23, (x - 0.12, y, 2.03), SKIN, e)
            box((0.12, 0.55, 0.1), (x + 0.12, y, 1.62), YL, e)       # barra de seguridad
    if front: box((0.8, 1.7, 0.6), (1.35, 0, 0.75), CAR_D, e, rot=(0, 0.45, 0))
    for x in (-0.85, 0.85):
        for y in (-0.6, 0.6):
            box((0.55, 0.32, 0.36), (x, y, 0.32), WHEEL, e)
    fin = box((1.9, 0.08, 1.15), (0, 0, -0.275), FIN, e)
    return e, fin

def build():
    sc, cam = scene_setup(world=BG, shadow=0.32); cam.data.clip_start = 0.1
    S = {"cam": cam}; dyn = [cam]
    box((700, 700, 1), (40, 0, -0.5), GROUND)
    # estación (andén y tejado)
    box((15, 2.6, 1.15), (-44, -2.2, 0.575), PLAT)
    box((15, 2.6, 1.15), (-44, 2.2, 0.575), PLAT)
    for x in (-51, -37):
        for y in (-3.2, 3.2): cyl(0.15, 4.4, (x, y, 3.3), SUPP)
    box((16, 7.4, 0.3), (-44, 0, 5.6), ROOF)
    # ---------- vía principal (barras que aparecen al construir) ----------
    S["mrails"] = []                       # (d, barra, p0, p1)
    pts, cum, L = OV.path(1.0)
    dmain = L[5]; step = 1.2
    dd = 0.0
    while dd < dmain - 1e-3:
        d1 = min(dmain, dd + step)
        p0, t0, l0, n0 = basis(dd, 1.0); p1, t1, l1, n1 = basis(d1, 1.0)
        for s in (-1, 1):
            b = bar_obj(RAIL, r=0.15); S["mrails"].append((d1, b, p0 + l0 * 0.6 * s, p1 + l1 * 0.6 * s))
        dd = d1
    S["mties"] = []
    dd = 0.6
    while dd < dmain:
        p, t, lat, n = basis(dd, 1.0)
        o = box((0.35, 1.7, 0.2), (0, 0, 0), TIE); S["mties"].append((dd, o, p - n * 0.24, (t, lat, n))); dd += 2.4
    S["supp"] = []
    dd = 1.0
    while dd < dmain:
        p, t, lat, n = basis(dd, 1.0)
        if p.z > 2.8:
            b = bar_obj(SUPP, r=0.28); S["supp"].append((dd, b, p - n * 0.35))
        dd += 4.8
    # brazo de las columnas altas (dos patas en V)
    dyn += [[x[1] for x in S["mrails"]], [x[1] for x in S["mties"]], [x[1] for x in S["supp"]]]
    # ---------- rizo (cambia de forma) ----------
    S["lrails"] = [bar_obj(RAIL, r=0.15, unique=True) for _ in range(2 * NL)]
    S["lties"] = [box((0.35, 1.7, 0.2), LEJOS, TIE) for _ in range(NL // 2)]
    S["ghost"] = [bar_obj(GHOST, r=0.07) for _ in range(48)]
    S["lbase"] = [bar_obj(SUPP, r=0.35) for _ in range(4)]
    dyn += [S["lrails"], S["lties"], S["ghost"], S["lbase"]]
    # ---------- frenos ----------
    S["brails"] = []; S["bties"] = []
    d0 = L[7]
    for i in range(30):
        a = d0 + OV.BRAKE_LEN * i / 30; b_ = d0 + OV.BRAKE_LEN * (i + 1) / 30
        p0, t0, l0, n0 = basis(a + 0.01, 1.0); p1, t1, l1, n1 = basis(b_ - 0.01, 1.0)
        for s in (-1, 1):
            b = bar_obj(RAIL, r=0.15); S["brails"].append((b_, b, p0 + l0 * 0.6 * s, p1 + l1 * 0.6 * s))
    for i in range(24):
        dd = d0 + 1.2 + 2.5 * i
        p, t, lat, n = basis(dd, 1.0)
        tie = box((0.35, 1.7, 0.2), (0, 0, 0), TIE)
        posts = [bar_obj(TIE, r=0.08) for _ in range(2)]
        S["bties"].append((dd, tie, posts, p, lat, n, t))
    dyn += [[x[1] for x in S["brails"]], [x[1] for x in S["bties"]], [x[2] for x in S["bties"]]]
    S["mags"] = []
    for i in range(OV.MAG_N):
        dd = OV.v2d(OV.MAG_V, 1.0) + OV.MAG_STEP * i
        pair = [box((0.95, 0.22, 0.4), (0, 0, 0), MAG_R if i % 2 == 0 else MAG_B) for _ in range(2)]
        S["mags"].append((dd, pair))
    dyn += [[x[1] for x in S["mags"]]]
    S["pads"] = [box((1.0, 0.3, 0.45), LEJOS, PAD) for _ in range(2)]
    S["sparks"] = [sph(0.06, LEJOS, SPARK) for _ in range(22)]
    dyn += [S["pads"], S["sparks"]]
    # ---------- cadena y dientes de la subida ----------
    S["chain"] = [box((0.5, 0.14, 0.12), LEJOS, CHAIN) for _ in range(70)]
    S["teeth"] = [(dd, tooth_mesh(OV.TOOTH_LEN, OV.TOOTH_H, 0.1, TOOTH)) for dd in OV.teeth_d()]
    S["pawl"] = bar_obj(HUB, r=0.07); S["pawlpiv"] = cyl(0.12, 0.3, LEJOS, WHEEL, rot=(math.pi / 2, 0, 0))
    dyn += [S["chain"], [x[1] for x in S["teeth"]], S["pawl"], S["pawlpiv"]]
    S["dim"] = [bar_obj(YL, r=0.18) for _ in range(3)]
    dyn += [S["dim"]]
    # ---------- tren ----------
    S["cars"] = []; S["fins"] = []
    for i in range(3):
        e, fin = make_car(i == 0); S["cars"].append(e); S["fins"].append(fin)
    S["grav"] = arrow(YL, 0.22)
    S["force"] = arrow(RED, 0.28, unique=True)
    S["brk"] = arrow((0.96, 0.96, 0.98), 0.09)
    S["eddy"] = [torus(0.32, 0.04, LEJOS, YL) for _ in range(3)]
    S["edots"] = [sph(0.07, LEJOS, YL) for _ in range(12)]
    dyn += [S["cars"], S["grav"], S["force"], S["brk"], S["eddy"], S["edots"]]
    # ---------- detalle: ruedas abrazando el raíl ----------
    S["wd"] = wd = empty(LW)
    cyl(1.0, 30, (0, 12, 0), RAIL, wd, rot=(math.pi / 2, 0, 0))
    box((3.2, 30, 0.45), (-2.5, 12, 0), TIE, wd)
    cyl(1.0, 30, (-9, 12, 0), RAIL, wd, rot=(math.pi / 2, 0, 0))
    box((9.0, 4.4, 1.6), (-3.0, 0, 5.2), CAR, wd)
    box((9.0, 4.4, 0.25), (-3.0, 0, 6.1), CAR_D, wd)
    box((3.4, 2.2, 0.6), (1.0, 0.6, 3.7), (0.3, 0.32, 0.36), wd)            # soporte de las ruedas
    S["wplate"] = box((0.55, 2.2, 6.2), (2.9, 0.6, 0.65), (0.3, 0.32, 0.36), wd)
    S["warm"] = box((3.2, 0.5, 0.45), (1.3, 0.75, -1.8), (0.3, 0.32, 0.36), wd)
    S["wheels"] = []
    for loc, r, ax in (((0, -0.1, 1.85), 0.85, 'x'), ((1.75, -0.1, 0), 0.75, 'z'), ((0, -0.1, -1.8), 0.75, 'x')):
        we = empty(V(loc), wd)
        rot = (0, math.pi / 2, 0) if ax == 'x' else (0, 0, 0)
        cyl(r, 0.75, (0, 0, 0), WHEEL, we, rot=rot)
        cyl(r * 0.45, 0.8, (0, 0, 0), HUB, we, rot=rot)
        if ax == 'x': box((0.82, r * 0.18, r * 1.7), (0, 0, 0), HUB, we)
        else: box((r * 1.7, r * 0.18, 0.78), (0, 0, 0), HUB, we)
        S["wheels"].append((we, ax))
    dyn += [wd, S["wplate"], S["warm"]] + [w for w, _ in S["wheels"]]
    join_static(dyn)
    return sc, S

# ---------------- pose ----------------
def car_frames(t):
    m = OV.morph(t); dh = OV.v2d(OV.train_v(t), m)
    return m, [basis(dh - 1.4 - i * CAR_GAP, m) + (dh - 1.4 - i * CAR_GAP,) for i in range(3)]

def pose(t, S):
    m = OV.morph(t); rv = OV.reveal(t); _, _, Lm = OV.path(m)
    rd = OV.v2d(rv, m)
    # vía principal
    for d1, b, p0, p1 in S["mrails"]:
        if d1 <= rd + 0.6: bar_set(b, p0, p1)
        else: hide_bar(b)
    for dd, o, p, fr in S["mties"]:
        if dd <= rd: o.location = p; orient(o, *fr)
        else: o.location = LEJOS
    for dd, b, top in S["supp"]:
        g = max(0.0, min(1.0, (rd - dd) / 7.0))
        if g > 0.01: bar_set(b, V((top.x, top.y, 0)), V((top.x, top.y, top.z * g)))
        else: hide_bar(b)
    # rizo
    l5, l7 = Lm[5], Lm[7]
    show_loop = rd > l5 + 0.1
    for i in range(NL):
        a = l5 + (l7 - l5) * i / NL; b_ = l5 + (l7 - l5) * (i + 1) / NL
        rb0, rb1 = S["lrails"][2 * i], S["lrails"][2 * i + 1]
        if show_loop and b_ <= rd + 0.6:
            p0, t0, l0, n0 = basis(a, m); p1, t1, l1, n1 = basis(b_, m)
            bar_set(rb0, p0 - l0 * 0.6, p1 - l1 * 0.6); bar_set(rb1, p0 + l0 * 0.6, p1 + l1 * 0.6)
            f = 2 * math.pi * (i + 0.5) / NL
            col = RAIL
            if K["abajo2"] <= t < K["arriba2"] and (f < 0.9 or f > 2 * math.pi - 0.9): col = GREEN
            if K["arriba2"] <= t < K["cuatro"] + 0.2 and abs(f - math.pi) < 0.8: col = RED
            set_color(rb0, col); set_color(rb1, col)
        else: hide_bar(rb0); hide_bar(rb1)
    for i, o in enumerate(S["lties"]):
        dd = l5 + (l7 - l5) * (i + 0.5) / len(S["lties"])
        if show_loop and dd <= rd:
            p, tt, lat, n = basis(dd, m); o.location = p - n * 0.24; orient(o, tt, lat, n)
        else: o.location = LEJOS
    gshow = K["circulos"] <= t < K["parar"] - 0.2
    for i, b in enumerate(S["ghost"]):
        if gshow and i % 2 == 0:
            f0 = 2 * math.pi * i / 48; f1 = 2 * math.pi * (i + 1) / 48
            P = lambda f: V((OV.CX + OV.R0 * math.sin(f), -1.2, 1.5 + OV.R0 * (1 - math.cos(f))))
            bar_set(b, P(f0), P(f1))
        else: hide_bar(b)
    for i, b in enumerate(S["lbase"]):
        if show_loop:
            x = OV.CX + (-4.5, -1.5, 1.5, 4.5)[i]; y = (0.0, 0.0, 4.0, 4.0)[i]
            bar_set(b, V((x, y - 1.2, 0.0)), V((x, y + 1.2, 0.0)))
        else: hide_bar(b)
    # frenos
    for d1, b, p0, p1 in S["brails"]:
        if d1 <= rd + 0.6: bar_set(b, p0, p1)
        else: hide_bar(b)
    for dd, tie, posts, p, lat, n, tt in S["bties"]:
        if dd <= rd:
            tie.location = p - n * 1.05; orient(tie, tt, lat, n)
            for s, po in zip((-1, 1), posts): bar_set(po, p - n * 1.0 + lat * 0.6 * s, p - n * 0.1 + lat * 0.6 * s)
        else:
            tie.location = LEJOS
            for po in posts: hide_bar(po)
    for i, (dd, pair) in enumerate(S["mags"]):
        g = OV.sg(t, K["imanes"] + 0.1 + 0.08 * i, K["imanes"] + 0.5 + 0.08 * i)
        if g > 0.01:
            p, tt, lat, n = basis(dd, 1.0)
            for s, o in zip((-1, 1), pair):
                o.location = p - n * 0.72 + lat * 0.17 * s; orient(o, tt, lat, n); o.scale = (0.95 * g, 0.22, 0.4 * g)
        else:
            for o in pair: o.location = LEJOS
    # frenos de roce (pastillas que aprietan la aleta)
    dpad = OV.v2d(OV.PAD_V, 1.0)
    if K["parar"] + 0.4 <= t < K["imanes"]:
        p, tt, lat, n = basis(dpad, 1.0)
        sq = OV.sg(t, K["chirr"] - 0.3, K["chirr"] + 0.1)
        wear = 1 - 0.45 * OV.sg(t, K["chirr"], K["imanes"] - 0.4)
        for s, o in zip((-1, 1), S["pads"]):
            o.location = p - n * 0.45 + lat * s * (0.55 - 0.35 * sq + 0.15 * (1 - wear)); orient(o, tt, lat, n)
            o.scale = (1.0, 0.3 * wear, 0.45)
        rnd = random.Random(7)
        on = K["chirr"] <= t < K["imanes"] - 0.4
        for i, sp in enumerate(S["sparks"]):
            if on:
                ph = (t * 1.7 + rnd.random()) % 1.0; vx = rnd.uniform(-5, -2); vy = rnd.uniform(-3, 3); vz = rnd.uniform(1, 4)
                sp.location = p - n * 0.35 + tt * (vx * ph) + lat * (vy * ph) + n * (vz * ph - 4.9 * ph * ph)
            else: sp.location = LEJOS
    else:
        for o in S["pads"]: o.location = LEJOS
        for sp in S["sparks"]: sp.location = LEJOS
    # cadena
    _, _, L1 = OV.path(1.0)
    c0, c1 = OV.v2d(1.02, 1.0), OV.v2d(2.0, 1.0); cl = c1 - c0
    chain_on = (K["cadena"] - 0.2 <= t < K["grav"]) or t >= K["sig"] - 0.3
    run = t if t < K["rompe"] + 0.2 else (t - 2.0)
    for i, o in enumerate(S["chain"]):
        dd = c0 + (i * cl / len(S["chain"]) + 2.6 * run) % cl
        if chain_on and dd <= rd + 0.5 and (not OV.chain_broken(t) or True):
            p, tt, lat, n = basis(dd, 1.0); q = p - n * 0.02 - lat * 0.18
            if OV.chain_broken(t):
                dt = t - K["rompe"] - 0.2; dd2 = c0 + (i * cl / len(S["chain"]) + 2.6 * (K["rompe"] + 0.2)) % cl
                p, tt, lat, n = basis(dd2, 1.0); q = p - n * 0.02 - lat * 0.18
                q = q + V((0.4 * math.sin(i), -0.6 * dt * math.cos(i * 1.7), -4.9 * dt * dt))
                if q.z < 0.06: q.z = 0.06
            o.location = q; orient(o, tt, lat, n)
        else: o.location = LEJOS
    teeth_on = K["dientes"] - 0.05 <= t < K["grav"] or t >= K["sig"] - 0.3
    for i, (dd, o) in enumerate(S["teeth"]):
        g = 1.0 if t >= K["sig"] - 0.3 else OV.sg(t, K["dientes"] + 0.05 * i, K["dientes"] + 0.3 + 0.05 * i)
        if teeth_on and g > 0.01:
            p, tt, lat, n = basis(dd, 1.0); o.location = p - n * 0.1 + lat * 0.25; orient(o, tt, lat, n); o.scale = (1, 1, g)
        else: o.location = LEJOS
    # dimensión de 30 m
    if K["treinta"] - 0.1 <= t < K["pero1"]:
        u = OV.sg(t, K["treinta"], K["treinta"] + 0.8); x = 1.0; y = -3.0; top = 29.6 * u
        bar_set(S["dim"][0], V((x, y, 0)), V((x, y, max(0.05, top))))
        bar_set(S["dim"][1], V((x - 1.2, y, 0.02)), V((x + 1.2, y, 0.02)))
        bar_set(S["dim"][2], V((x - 1.2, y, top)), V((x + 1.2, y, top)))
    else:
        for b in S["dim"]: hide_bar(b)
    # tren
    m, CF = car_frames(t)
    fly = OV.flyoff(t)
    fins_on = t >= K["parar"] + 0.3
    for i, (e, (p, tt, lat, n, dc)) in enumerate(zip(S["cars"], CF)):
        lift = fly * (1.0 - 0.25 * i)
        e.location = p + n * lift; orient(e, tt, lat, n)
        if fly > 0: e.rotation_quaternion = e.rotation_quaternion @ Matrix.Rotation(0.12 * fly * (1 if i == 0 else -0.5), 4, 'X').to_quaternion()
        S["fins"][i].scale = (1.9, 0.08, 1.15) if fins_on else (0.001, 0.001, 0.001)
    # seguro (trinquete) del último vagón
    p2, t2, l2, n2, dc2 = CF[2]
    if K["dientes"] - 0.05 <= t < K["grav"] and OV.train_v(t) < 2.02:
        piv = p2 + t2 * (-1.25) + n2 * 0.5 + l2 * 0.25
        dtip = OV.v2d(OV.train_v(t), 1.0) - OV.PAWL_BACK
        h = -0.1
        for d0 in OV.teeth_d():
            if d0 <= dtip <= d0 + OV.TOOTH_LEN:
                h = -0.1 + OV.TOOTH_H * (dtip - d0) / OV.TOOTH_LEN
        pt, tt3, lt3, nt3 = basis(dtip, 1.0)
        tip = pt + nt3 * (h + 0.05) + lt3 * 0.25
        bar_set(S["pawl"], piv, tip); S["pawlpiv"].location = piv; orient(S["pawlpiv"], t2, n2, -l2)
        S["pawltip"] = tip
    else:
        hide_bar(S["pawl"]); S["pawlpiv"].location = LEJOS
    # flecha de la gravedad
    p0, t0, l0, n0, _ = CF[0]
    if K["grav"] <= t < K["curvas"] - 0.2:
        c = p0 + n0 * 1.2 + V((0, -1.3, 0)); put_arrow(S["grav"], c, c + V((0, 0, -3.2)))
    else: hide_arrow(S["grav"])
    # fuerza en el rizo
    g = OV.gforce(t)
    if g > 1.25 and K["redondo"] <= t < K["parar"]:
        top = p0 + n0 * (2.4 + 0.75 * g); put_arrow(S["force"], top, p0 + n0 * 2.4)
        set_color(S["force"][0], RED if (g > 4.6 and t < K["circulos"]) else GREEN); set_color(S["force"][1], RED if (g > 4.6 and t < K["circulos"]) else GREEN)
    else: hide_arrow(S["force"])
    # frenado magnético: corrientes en las aletas y flecha de frenado
    md0, md1 = OV.v2d(OV.MAG_V, 1.0) - 0.6, OV.v2d(OV.MAG_V, 1.0) + OV.MAG_STEP * (OV.MAG_N - 1) + 0.6
    braking = K["pasar"] - 0.2 <= t < K["elec"] + 0.2
    di = 0
    for i, (p, tt, lat, n, dc) in enumerate(CF):
        inside = md0 <= dc <= md1 and braking
        ring = S["eddy"][i]
        if inside:
            spd = max(0.0, OV.speed(t) / 48)
            c = p - n * 0.45 - lat * 0.07
            ring.location = c; ring.rotation_mode = 'QUATERNION'
            ring.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(lat)
            s = 0.6 + 0.4 * spd; ring.scale = (s, s, s)
            for j in range(4):
                a = 2 * math.pi * j / 4 + t * 6 * (0.3 + spd)
                S["edots"][4 * i + j].location = c + (tt * math.cos(a) + n * math.sin(a)) * 0.32 * s - lat * 0.03
        else:
            ring.location = LEJOS
            for j in range(4): S["edots"][4 * i + j].location = LEJOS
    if braking and OV.speed(t) > 2:
        p1_, t1_, l1_, n1_, _ = CF[1]
        c = p1_ + n1_ * 0.85 - l1_ * 0.95 + t1_ * 0.9; put_arrow(S["brk"], c, c - t1_ * (0.5 + 1.6 * OV.speed(t) / 48))
    else: hide_arrow(S["brk"])
    # detalle de las ruedas
    if K["ruedas"] - 0.1 <= t < K["rizo"]:
        S["wd"].location = LW + V((0, 0, 0.04 * math.sin(t * 37)))
        apps = (K["encima"], K["lados"] + 0.2, K["debajo"] + 0.2)
        for (we, ax), ta in zip(S["wheels"], apps):
            g = OV.sg(t, ta - 0.1, ta + 0.25); we.scale = (g, g, g) if g > 0.01 else (0.001,) * 3
            ang = t * 7
            we.rotation_euler = (ang, 0, 0) if ax == 'x' else (0, 0, ang)
        S["warm"].scale = (3.2, 0.5, 0.45) if t >= K["debajo"] else (0.001,) * 3
    else:
        S["wd"].location = LEJOS
    apply_cam(S["cam"], *camera(t))

# ---------------- cámara ----------------
def HP(t, m=None):
    return V(OV.head_pos(t))

def follow(t0, t1, off, toff, lens, step=0.5):
    ks = []; t = t0
    while t < t1 + 1e-6:
        h = HP(t); ks.append((t, tuple(h + V(off)), tuple(h + V(toff)), lens)); t += step
    return ks

_CAMS = None
def CAMS():
    global _CAMS
    if _CAMS is not None: return _CAMS
    k = K
    LP = lambda v, m=1.0: basis(OV.v2d(v, m), m)[0]
    tooth = LP(1.47)
    br = LP(OV.PAD_V); mg = LP(OV.MAG_V)
    CX = OV.CX
    _CAMS = [
        (0.0, [(0, (16.5, -6.0, 16.0), (11.0, 0, 23.5), 30), (1.2, (20, -8.5, 6.5), (20, 0, 7), 30), (2.4, (27, -11, 5.5), (32, 0, 3.5), 30),
               (k["vamos"] - 0.12, (36, -13, 7.5), (42, 0, 7.0), 30)]),
        (k["vamos"] - 0.1, [(0, (-30, -20, 9), (-42, 0, 1.5), 30), (k["primero"], (-33, -16, 7), (-41, 0, 1.5), 30),
                             (k["motor"], (-36, -9.5, 4.0), (-41, 0, 1.6), 30), (k["cadena"], (-35, -9, 4.0), (-40, 0, 1.8), 30)]),
        (k["cadena"], follow(k["cadena"], k["treinta"] - 0.2, (5, -13, 2.0), (0, 0, -0.5), 32)),
        (k["treinta"] - 0.1, [(0, (-9, -40, 16), (-7, 0, 14.5), 32), (k["pero1"] - 0.1, (-8, -38, 17), (-6, 0, 15.5), 32)]),
        (k["pero1"], follow(k["pero1"], k["dientes"] - 0.3, (5, -14, 3.0), (-2, 0, -1.0), 32)),
        (k["dientes"] - 0.2, [(0, tuple(tooth + V((4, -6.5, 5.0))), tuple(tooth + V((1, 0, 0))), 32),
                               (k["clac1"] - 0.3, tuple(tooth + V((3, -5.5, 4.5))), tuple(tooth + V((0, 0, 0))), 32)]),
        (k["clac1"] - 0.25, "pawl"),
        (k["arriba"], [(0, (-3, -13, 34), (6, 0, 27.5), 32), (k["grav"] - 0.05, (-2, -13, 34), (6, 0, 27.5), 32)]),
        (k["grav"], follow(k["grav"], k["curvas"] - 0.05, (6, -11, 0.5), (0, 0, -0.3), 30)),
        (k["curvas"], [(0, (34, -15, 7.5), (37.5, 0, 6.5), 32), (k["ruedas"] - 0.05, (39, -14, 9.0), (41, 0, 9.0), 32)]),
        (k["ruedas"] - 0.1, [(0, tuple(LW + V((8.5, -9.5, 5.0))), tuple(LW + V((0.4, 0, 0.6))), 38),
                              (k["rizo"] - 0.05, tuple(LW + V((7.0, -10.5, 4.2))), tuple(LW + V((0.4, 0, 0.4))), 38)]),
        (k["rizo"], [(0, (CX - 4, -40, 13), (CX + 2, 2, 13.5), 32), (k["aplasta"] - 0.4, (CX - 3, -38, 12), (CX + 1, 2, 13.0), 32),
                     (k["aplasta"] + 0.3, (CX - 7, -19, 4.5), (CX - 1.5, 1, 4.0), 30), (k["seis"] + 0.5, (CX - 6, -18, 4.5), (CX - 1, 1, 4.0), 30),
                     (k["curioso"], (CX, -40, 13.5), (CX, 2, 14), 32), (k["arriba2"] + 0.8, (CX + 1, -42, 14), (CX, 2, 14.0), 32),
                     (k["cuatro"] - 0.25, (CX + 1, -42, 14), (CX, 2, 14.0), 32)]),
        (k["cuatro"] - 0.2, [(0, (CX - 7, -19, 4.5), (CX - 1.5, 1, 4.0), 30), (k["cuatro"] + 1.0, (CX - 6, -18, 4.5), (CX - 1, 1, 4.0), 30),
                              (k["cuatro"] + 1.9, (CX, -42, 14), (CX, 2, 14.0), 32), (k["parar"] - 0.25, (CX + 1, -42, 14), (CX, 2, 14.0), 32)]),
        (k["parar"] - 0.2, [(0, tuple(br + V((-2, -15, 4.0))), tuple(br + V((-5, 0, 0))), 30),
                             (k["chirr"] - 0.3, tuple(br + V((1.5, -6.5, -0.25))), tuple(br + V((-0.5, 0, -0.45))), 30),
                             (k["imanes"] - 0.05, tuple(br + V((1.0, -6.3, -0.2))), tuple(br + V((-0.5, 0, -0.45))), 30)]),
        (k["imanes"], [(0, tuple(mg + V((-6, -10, 3.5))), tuple(mg + V((1, 0, -0.4))), 30), (k["aletas"], tuple(mg + V((-5, -6.5, 0.3))), tuple(mg + V((-3, 0, -0.45))), 30)]),
        (k["pasar"] - 0.2, follow(k["pasar"] - 0.2, k["sintocar"] + 0.3, (-4.4, -4.9, 0.1), (-4.4, 0, 1.0), 30)),
        (k["sintocar"] + 0.35, [(0, tuple(HP(k["sintocar"] + 0.3) + V((-4.4, -4.9, 0.1))), tuple(HP(k["sintocar"] + 0.3) + V((-4.4, 0, 1.0))), 30),
                                 (k["sig"] - 0.05, tuple(HP(k["sintocar"] + 0.3) + V((-3, -11, 3.5))), tuple(HP(k["sintocar"] + 0.3) + V((-5, 0, 0))), 30)]),
        (k["sig"], [(0, (-52, -48, 26), (22, 0, 11), 30), (DUR + 1, (-48, -52, 25), (24, 0, 11), 30)]),
    ]
    return _CAMS

def camera(t):
    segs = CAMS(); k = 0
    for i, (st, _) in enumerate(segs):
        if t >= st: k = i
    st, ks = segs[k]
    if ks == "pawl":
        m, CF = car_frames(t); p2, t2, l2, n2, _ = CF[2]
        piv = p2 + t2 * (-1.25) + n2 * 0.4
        pos = piv - l2 * 4.2 + n2 * 1.0 - t2 * 1.6; tgt = piv - t2 * 0.6 - n2 * 0.3
        return pos + V((0.01 * math.sin(t), 0, 0)), tgt, 34
    ks = [(st if a == 0 else a, p, q, l) for a, p, q, l in ks]
    if ks[-1][0] <= t: ks = ks + [(t + 1, ks[-1][1], ks[-1][2], ks[-1][3])]
    return cam_state(t, ks, drift=0.02)

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v)
    m, CF = car_frames(t); p0, t0, l0, n0, _ = CF[0]
    p1 = CF[1][0]
    tooth = basis(OV.v2d(1.47, 1.0), 1.0)
    pawl = S.get("pawltip", LEJOS)
    lt = OV.loop_pts(0.0)
    return {"train": Pj(p1 + n0 * 2.4 + V((0, 0, 0.5 * OV.flyoff(t)))), "chain": Pj(basis(OV.v2d(1.2, 1.0), 1.0)[0]),
            "dim": Pj(V((1.0, -3.0, 15.0))), "teeth": Pj(tooth[0]), "pawl": Pj(pawl),
            "w_top": Pj(LW + V((0, 0, 2.7))), "w_side": Pj(LW + V((2.6, 0, 0.3))), "w_up": Pj(LW + V((0, 0, -2.6))), "rail": Pj(LW + V((-0.9, -2, 0.3))),
            "ghost": Pj(V(lt[len(lt) // 2]) + V((0, -1.2, 0))), "pads": Pj(basis(OV.v2d(OV.PAD_V, 1.0), 1.0)[0]),
            "magnets": Pj(basis(OV.v2d(OV.MAG_V + 0.08, 1.0), 1.0)[0] - V((0, 0, 0.7))), "fin": Pj(p1 - n0 * 0.5)}

if __name__ == "__main__":
    run("montanarusa", build, pose, anchors)
