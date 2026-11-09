# «Si tuvieras que inventar la cerilla…»: macro de una cerilla rascando la tira de la caja (chispas y llama); manos
# frotando un palo sobre una tabla (humo, brasa); fósforo blanco junto a un termómetro que sube a 30 °C y prende solo;
# cerilla de cabeza blanca; bolsillo vaquero con cerillas que se encienden solas y humo verde (veneno); corte gigante de la
# tira (fósforo rojo + vidrio) y de la cabeza (clorato + azufre): al rascar, el rojo se vuelve blanco, chispa, flechas de
# oxígeno, llama; la llama de la cabeza se apaga, el palo se cubre de parafina y el fuego baja por la madera;
# cada mitad sola no hace nada; rascar contra una pared, nada; final con la cerilla ardiendo.
import bpy, bmesh, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector, Matrix, Euler

T0, DUR = cargar("cerilla")
_TC = {}
def T(k, n=1, fin=False):
    key = (k, n, fin)
    if key not in _TC: _TC[key] = T0(k, n, fin)
    return _TC[key]

BG = (0.07, 0.07, 0.09); TABLE = (0.27, 0.22, 0.2); SLEEVE = (0.16, 0.3, 0.6); SLEEVE2 = (0.95, 0.78, 0.2); DRAWER = (0.9, 0.86, 0.78)
STRIP = (0.42, 0.26, 0.16); WOOD = (0.9, 0.75, 0.5); WOOD_D = (0.62, 0.45, 0.28); HEADR = (0.72, 0.14, 0.12); HEAD_IN = (0.85, 0.42, 0.32)
PALE = (0.95, 0.92, 0.72); SKIN = (0.93, 0.72, 0.58); NAIL = (0.97, 0.86, 0.82); CHAR = (0.1, 0.09, 0.09)
ORANGE = (1.0, 0.5, 0.1); YELLOW = (1.0, 0.86, 0.3); HOT = (1.0, 0.97, 0.8); RED = (0.75, 0.08, 0.1); GLASS = (0.65, 0.9, 1.0)
WHITE = (0.96, 0.96, 0.98); SULF = (0.98, 0.85, 0.1); CYAN = (0.3, 0.85, 1.0); SMOKE = (0.55, 0.55, 0.58); GREENF = (0.45, 0.85, 0.35)
DENIM = (0.2, 0.32, 0.55); DENIM_D = (0.15, 0.24, 0.42); STITCH = (0.95, 0.65, 0.2); PLASTER = (0.82, 0.78, 0.7); PAR = (0.97, 0.93, 0.78)
GREY = (0.3, 0.31, 0.35); GLASSW = (0.85, 0.9, 0.95)
LEJOS = Vector((0, 300, -300))
LA = Vector((0, 0, 0)); LB = Vector((60, 0, 0)); LC = Vector((120, 0, 0)); LC2 = Vector((172, 0, 0)); LD = Vector((210, 0, 0)); LE = Vector((280, 0, 0))
STICK = 4.6

def hide_bar(o): bar_set(o, LEJOS, LEJOS + Vector((0, 0, 0.01)))

def cone(r, h, color, unique=False):
    bpy.ops.mesh.primitive_cone_add(radius1=r, radius2=0, depth=h, location=(0, 0, 0), vertices=16); o = bpy.context.object
    for vv in o.data.vertices: vv.co.z += h / 2
    return setup(o, color, None, True, unique)

def arrow(color, r):
    return [bar_obj(color, r=r), cone(r * 2.6, r * 6, color)]

def put_arrow(a, p0, p1):
    p0, p1 = Vector(p0), Vector(p1); d = p1 - p0; L = d.length
    if L < 1e-3: hide_arrow(a); return
    hl = min(a[0]["r"] * 6, L * 0.6); q = p1 - d.normalized() * hl
    bar_set(a[0], p0, q); a[1].location = q; a[1].rotation_mode = 'QUATERNION'
    a[1].rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())

def hide_arrow(a):
    hide_bar(a[0]); a[1].location = LEJOS

def flame():
    """llama estilizada (siempre hacia arriba); escala 1 = 1 unidad de alto aprox."""
    e = empty(LEJOS)
    sph(1, (0, 0, 0.62), ORANGE, e, scale=(0.25, 0.25, 0.55))
    c = cone(0.24, 0.8, ORANGE); c.parent = e; c.location = (0, 0, 0.95)
    sph(1, (0, -0.13, 0.45), YELLOW, e, scale=(0.17, 0.17, 0.38))
    sph(1, (0, -0.2, 0.2), HOT, e, scale=(0.1, 0.1, 0.12))
    return e

def put_flame(f, p, s, t, ph=0.0):
    if s < 0.02: f.location = LEJOS; return
    fl = 1 + 0.13 * math.sin(t * 23 + ph) + 0.07 * math.sin(t * 37 + 2 * ph)
    f.location = Vector(p) - Vector((0, 0, 0.12 * s)); f.scale = (s * (1 - 0.05 * math.sin(t * 29 + ph)), s, s * fl)
    f.rotation_euler = (0.06 * math.sin(t * 7 + ph), 0.08 * math.sin(t * 11 + ph), 0)

def make_match(head_col, fingers=True):
    """cerilla con la cabeza en el origen y el palo hacia +X local; dedos en la cola"""
    e = empty(LEJOS)
    box((STICK, 0.22, 0.22), (0.15 + STICK / 2, 0, 0), WOOD, e)
    h = sph(0.24, (0, 0, 0), head_col, e, scale=(1.45, 1.12, 1.12), unique=True)
    f = empty((STICK + 0.1, 0, 0), e)
    for z, s in (((0.88, 1), (-0.88, -1)) if fingers else ()):
        cyl(0.66, 2.6, (0, -0.9, z), SKIN, f, rot=(math.pi / 2, 0, 0))
        sph(0.66, (0, 0.4, z), SKIN, f)
        sph(0.5, (-0.25, 0.25, z + 0.38 * s), NAIL, f, scale=(0.75, 0.9, 0.3))
    par = box((1, 0.27, 0.27), LEJOS, PAR)
    ch = box((1, 0.29, 0.29), LEJOS, CHAR)
    par.parent = e; ch.parent = e
    return {"e": e, "head": h, "par": par, "char": ch}

def half_head(a, b, c, color, inner, parent=None):
    """cabeza de cerilla gigante cortada por el plano y=0 (queda la mitad y>0, la cara del corte más clara)"""
    me = bpy.data.meshes.new("hh"); bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=40, v_segments=24, radius=1.0)
    for v in bm.verts: v.co = Vector((v.co.x * a, v.co.y * b, v.co.z * c))
    geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
    r = bmesh.ops.bisect_plane(bm, geom=geom, plane_co=(0, 0, 0), plane_no=(0, 1, 0), clear_inner=True)
    edges = [g for g in r["geom_cut"] if isinstance(g, bmesh.types.BMEdge)]
    f = bmesh.ops.holes_fill(bm, edges=edges, sides=0)
    for fc in f["faces"]: fc.material_index = 1
    bm.normal_update(); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("hh", me); bpy.context.collection.objects.link(o)
    o.data.materials.append(mat(color)); o.data.materials.append(mat(inner))
    for p in o.data.polygons: p.use_smooth = p.material_index == 0
    if parent: o.parent = parent
    return o

def build():
    sc, cam = scene_setup(world=BG, shadow=0.3); cam.data.clip_start = 0.05
    S = {"cam": cam}; dyn = [cam]
    rnd = random.Random(7)
    # ---------- A: caja de cerillas sobre la mesa ----------
    box((60, 40, 1), LA + Vector((0, 4, -0.5)), TABLE)
    box((5.4, 3.6, 1.5), LA + Vector((0, 0, 0.75)), SLEEVE)
    box((5.42, 3.62, 0.35), LA + Vector((0, 0, 1.2)), SLEEVE2)
    box((5.2, 0.05, 1.15), LA + Vector((0, -1.82, 0.75)), STRIP)
    box((5.2, 0.05, 1.15), LA + Vector((0, 1.82, 0.75)), STRIP)
    for i in range(70):                       # grano de la tira
        sph(0.035, LA + Vector((rnd.uniform(-2.5, 2.5), -1.85, rnd.uniform(0.25, 1.25))), (0.3, 0.17, 0.1))
    # cajón medio abierto con cerillas
    box((4.9, 3.3, 1.2), LA + Vector((2.0, 0, 0.62)), DRAWER)
    box((4.6, 3.0, 0.2), LA + Vector((2.0, 0, 1.2)), (0.75, 0.7, 0.62))
    for k in range(7):
        y = -1.1 + 0.36 * k
        box((STICK, 0.22, 0.22), LA + Vector((2.2 + 0.15, y, 1.36)), WOOD)
        sph(0.24, LA + Vector((2.2 - STICK / 2, y, 1.36)), HEADR, scale=(1.45, 1.12, 1.12))
    S["mA"] = make_match(HEADR)
    S["fA"] = flame()
    S["sparks"] = [sph(0.045, LEJOS, YELLOW if k % 2 else ORANGE) for k in range(16)]
    S["smoke"] = [sph(0.4, LEJOS, SMOKE) for _ in range(8)]
    dyn += [S["mA"]["e"], S["fA"], S["sparks"], S["smoke"]]
    # ---------- B: frotar un palo ----------
    box((60, 40, 1), LB + Vector((0, 4, -0.5)), (0.2, 0.18, 0.17))
    box((14, 4, 1.2), LB + Vector((0, 0, 0.6)), WOOD_D)
    cyl(0.45, 0.3, LB + Vector((0, 0, 1.12)), (0.25, 0.15, 0.08))
    box((0.6, 0.6, 0.6), LB + Vector((0, -1.9, 0.85)), (0.25, 0.15, 0.08))
    S["spin"] = sp = empty(LB + Vector((0, 0, 1.2)))
    cyl(0.32, 11, (0, 0, 5.5), WOOD, sp)
    for k in range(4):
        a = k * math.pi / 2
        box((0.1, 0.1, 10.6), (0.31 * math.cos(a), 0.31 * math.sin(a), 5.5), WOOD_D, sp, rot=(0, 0, a))
    S["palms"] = []
    for s in (-1, 1):
        p = empty(LEJOS)
        sph(1, (0, 0, 0), SKIN, p, scale=(0.45, 1.5, 2.0))
        cyl(1.0, 7, (s * 3.6, 0, -1.5), SKIN, p, rot=(0, math.pi / 2 - s * 0.35, 0))
        sph(1, (s * 0.05, 0, 2.6), SKIN, p, scale=(0.38, 1.3, 1.5))
        sph(1, (s * 0.1, -1.45, 0.6), SKIN, p, scale=(0.35, 0.4, 0.9))
        S["palms"].append(p)
    S["ember"] = sph(0.35, LEJOS, ORANGE, unique=True)
    S["smokeB"] = [sph(0.6, LEJOS, SMOKE) for _ in range(8)]
    dyn += [sp, S["palms"], S["ember"], S["smokeB"]]
    # ---------- C: fósforo blanco y termómetro ----------
    box((60, 40, 1), LC + Vector((0, 4, -0.5)), (0.18, 0.19, 0.22))
    S["lump"] = lp = empty(LC)
    for p, r in (((0, 0, 0.7), 0.9), ((0.7, 0.3, 0.5), 0.65), ((-0.6, 0.2, 0.45), 0.6), ((0.1, -0.4, 1.2), 0.55)):
        sph(r, p, PALE, lp, scale=(1.1, 1, 0.85))
    TH = LC + Vector((3.2, 0, 0))
    box((1.6, 1.2, 10), TH + Vector((0, 0.7, 5.2)), (0.92, 0.92, 0.95))
    box((0.42, 0.1, 8.2), TH + Vector((0, 0.05, 5.2)), (0.25, 0.27, 0.32))
    sph(0.6, TH + Vector((0, 0, 0.9)), RED)
    for k in range(9):
        z = 1.8 + 0.8 * k
        box((0.5 if k % 2 == 0 else 0.3, 0.05, 0.06), TH + Vector((-0.55, -0.2, z)), GREY)
    box((0.9, 0.06, 0.1), TH + Vector((0, -0.31, 1.8 + 0.8 * 6)), (1.0, 0.82, 0.16))
    S["col"] = cyl(0.16, 1, LEJOS, RED)
    S["TH"] = TH
    S["fC"] = flame()
    S["smokeC"] = [sph(0.5, LEJOS, WHITE) for _ in range(6)]
    S["mC"] = make_match(PALE, fingers=False)
    dyn += [lp, S["col"], S["fC"], S["smokeC"], S["mC"]["e"]]
    # bolsillo vaquero
    box((30, 0.6, 28), LC2 + Vector((0, 1.0, 6)), DENIM)
    S["pocket"] = box((8, 0.4, 6.5), LC2 + Vector((0, 0.5, 4.2)), DENIM_D)
    box((8, 0.1, 0.12), LC2 + Vector((0, 0.27, 7.2)), STITCH)
    box((0.12, 0.1, 6.2), LC2 + Vector((-3.85, 0.27, 4.2)), STITCH); box((0.12, 0.1, 6.2), LC2 + Vector((3.85, 0.27, 4.2)), STITCH)
    box((8, 0.1, 0.12), LC2 + Vector((0, 0.27, 1.2)), STITCH)
    for x in (-3.85, 3.85): cyl(0.22, 0.2, LC2 + Vector((x, 0.22, 7.2)), (0.85, 0.55, 0.3), rot=(math.pi / 2, 0, 0))
    MP = ((-1.3, 0.12), (0.2, -0.05), (1.5, -0.18))
    for x, rz in MP:
        o = empty(LC2 + Vector((x, 0.5, 7.6)), None); o.rotation_euler = (0, rz, 0)
        box((0.22, 0.22, STICK), (0, 0, -STICK / 2 + 0.4), WOOD, o)
        sph(0.24, (0, 0, 0.6), PALE, o, scale=(1.12, 1.12, 1.45))
    S["pocket_heads"] = [LC2 + Vector((x + 0.6 * math.sin(rz), 0.5, 7.6 + 0.6 * math.cos(rz))) for x, rz in MP]
    S["fP"] = [flame() for _ in range(3)]
    S["fume"] = [sph(0.55, LEJOS, GREENF) for _ in range(10)]
    dyn += [S["fP"], S["fume"]]
    # ---------- D: corte gigante: tira + cabeza ----------
    box((80, 40, 1), LD + Vector((0, 10, -2.6)), (0.12, 0.12, 0.15))
    box((16, 6, 1.6), LD + Vector((0, 3.0, -1.3)), SLEEVE)
    box((14, 4, 1.6), LD + Vector((0, 2.0, 0)), STRIP)            # cara del corte en y=0, arriba z=0.8
    S["red"] = []; S["redpos"] = []
    for i in range(46):
        if i < 26: p = Vector((rnd.uniform(-6.6, 6.6), -0.02, rnd.uniform(-0.65, 0.65)))
        else: p = Vector((rnd.uniform(-6.6, 6.6), rnd.uniform(0.2, 3.8), 0.78))
        o = sph(0.24, LD + p, RED, unique=True); S["red"].append(o); S["redpos"].append(p)
    for i in range(30):
        if i < 16: p = Vector((rnd.uniform(-6.6, 6.6), -0.02, rnd.uniform(-0.6, 0.6)))
        else: p = Vector((rnd.uniform(-6.6, 6.6), rnd.uniform(0.2, 3.8), 0.8))
        box((0.34, 0.34, 0.2), LD + p, GLASS, rot=(rnd.uniform(0, 3), rnd.uniform(0, 3), rnd.uniform(0, 3)))
    S["mD"] = md = empty(LEJOS)
    half_head(2.6, 1.9, 1.9, HEADR, HEAD_IN, md)
    cyl(1.0, 0.02, (0, -0.01, 0), HEAD_IN, md, rot=(math.pi / 2, 0, 0)).scale = (2.3, 1.68, 1)
    box((12, 1.5, 1.5), (2.0 + 6, 0.75, 0), WOOD, md)
    box((12, 0.02, 1.5), (2.0 + 6, -0.0, 0), (0.98, 0.85, 0.62), md)
    S["clor"] = []; S["sulf"] = []; S["cpos"] = []; S["spos"] = []
    for i in range(34):
        while True:
            x, z = rnd.uniform(-2.4, 2.4), rnd.uniform(-1.75, 1.75)
            if (x / 2.4) ** 2 + (z / 1.75) ** 2 < 0.85: break
        p = Vector((x, -0.05, z))
        if i % 2 == 0:
            o = box((0.42, 0.2, 0.42), p, WHITE, md, rot=(0, rnd.uniform(0, 1.5), 0), unique=True); S["clor"].append(o); S["cpos"].append(p)
        else:
            o = sph(0.27, p, SULF, md, unique=True); S["sulf"].append(o); S["spos"].append(p)
    S["fD"] = flame()
    S["sparksD"] = [sph(0.14, LEJOS, YELLOW if k % 2 else HOT) for k in range(18)]
    S["o2"] = [arrow(CYAN, 0.07) for _ in range(5)]
    S["bub"] = [sph(0.13, LEJOS, CYAN) for _ in range(10)]
    dyn += [S["red"], md, S["fD"], S["sparksD"], S["o2"], S["bub"]]
    # ---------- E: pared ----------
    box((40, 30, 1), LE + Vector((0, -4, -0.5)), TABLE)
    box((24, 1, 16), LE + Vector((0, 0.5, 8)), PLASTER)
    for i in range(60):
        sph(0.08, LE + Vector((rnd.uniform(-11, 11), -0.02, rnd.uniform(0.5, 15))), (0.74, 0.7, 0.62))
    S["mE"] = make_match(HEADR)
    dyn += [S["mE"]["e"]]
    join_static(dyn)
    return sc, S

# ---------- utilidades de tiempo ----------
STRIKE0, STRIKE1 = 0.05, 0.85      # primer rascado

def headA(t):
    """posición (head), rotación de la cerilla A"""
    rot0 = Euler((0, -0.28, -0.4))
    if t < T("necesitas"):
        u = seg(t, STRIKE0, STRIKE1)
        x = mix(2.0, -1.6, u); p = LA + Vector((x, -2.03, 0.78))
        lift = seg(t, STRIKE1 + 0.05, 2.2)
        p += Vector((0.8 * lift, -0.6 * lift, 2.0 * lift))
        return p, rot0
    # segunda parte (llama que se apaga, parafina, final)
    return LA + Vector((-1.2, -5.5, 4.0)), Euler((0, 0, 0))

def flameA(t):
    if t < T("necesitas"):
        return 0.9 * seg(t, 0.6, 1.0) * (1 + 0.5 * math.exp(-((t - 0.95) / 0.25) ** 2)) * (1 - seg(t, T("vamos a") + 0.6, T("necesitas")))
    a = T("pero la llama"); b = T("así que mojas")
    if a - 0.5 <= t < b:
        return 1.3 * seg(t, a - 0.5, a - 0.2) * (1 - seg(t, T("suspiro") - 0.4, T("suspiro", fin=True) + 0.1))
    if t >= T("que arde despacio") - 0.3: return 0.85 * seg(t, T("que arde despacio") - 0.3, T("que arde despacio") + 0.2)
    return 0.0

def burnA(t):
    """longitud quemada del palo (0..)"""
    if t < T("que arde despacio"): return 0.0
    return 1.9 * seg(t, T("que arde despacio"), T("madera", 2, fin=True) + 0.4) + 0.12 * max(0.0, t - T("madera", 2, fin=True) - 0.4)

def parA(t):
    if t < T("así que mojas"): return 0.0
    return seg(t, T("parafina") - 0.2, T("parafina", fin=True) + 0.2)

def temp_C(t):
    return keyed(t, [(T("el fósforo blanco"), 20.0), (T("treinta"), 24.0), (T("grados", fin=True), 30.0)])

def drill_on(t): return T("frotar") <= t < T("así que buscas")

def scrape_u(t):
    a, b = T("al rascar"), T("calienta", fin=True)
    return seg(t, a, b)

def pose(t, S):
    # ---------- A ----------
    m = S["mA"]; p, r = headA(t)
    m["e"].location = p; m["e"].rotation_euler = r
    ph = m["e"].matrix_world
    bl = burnA(t); pa = parA(t)
    if pa > 0.01:
        L = (STICK - 0.4) * 0.6 * pa
        m["par"].location = (0.2 + L / 2, 0, 0); m["par"].scale = (max(L, 0.01), 0.27, 0.27)
    else: m["par"].location = LEJOS
    if bl > 0.01:
        m["char"].location = (0.2 + bl / 2, 0, 0); m["char"].scale = (bl, 0.29, 0.29)
    else: m["char"].location = LEJOS
    BURNT = (0.3, 0.07, 0.05)
    head_col = HEADR if t < STRIKE1 - 0.1 else BURNT
    if T("necesitas") <= t: head_col = HEADR if t < T("pero la llama") - 0.5 else BURNT
    set_color(m["head"], head_col)
    bpy.context.view_layer.update()
    fs = flameA(t)
    fpos = m["e"].matrix_world @ Vector((max(0.0, bl - 0.1), 0, 0.12))
    put_flame(S["fA"], fpos, fs, t)
    # chispas del primer rascado
    for k, s in enumerate(S["sparks"]):
        t0 = 0.55 + 0.03 * k
        u = t - t0
        if 0 <= u < 0.6:
            rr = random.Random(k)
            v = Vector((rr.uniform(-3, 2), rr.uniform(-3.5, -1), rr.uniform(1, 4)))
            s.location = LA + Vector((mix(2.0, -1.6, seg(t0, STRIKE0, STRIKE1)), -2.1, 0.8)) + v * u + Vector((0, 0, -6 * u * u))
            s.scale = (1 - u / 0.6,) * 3
        else: s.location = LEJOS
    # humo cuando se apaga la llama de la cabeza
    for k, s in enumerate(S["smoke"]):
        a = T("suspiro", fin=True) - 0.1
        u = (t - a - 0.12 * k)
        if 0 <= u < 1.6 and t < T("que arde despacio"):
            hp = m["e"].matrix_world @ Vector((0, 0, 0))
            s.location = hp + Vector((0.3 * math.sin(3 * u + k), 0, 0.3 + 1.6 * u)); s.scale = (0.3 + 0.5 * u,) * 3
        else: s.location = LEJOS
    # ---------- B ----------
    on = drill_on(t)
    w = 2 * math.pi * 2.2
    amp = 1.1 if on else 0.25
    yy = amp * math.sin(w * t)
    S["spin"].rotation_euler = (0, 0, 2.6 * math.sin(w * t) * (1 if on else 0.3))
    for s, pm in zip((-1, 1), S["palms"]):
        pm.location = LB + Vector((s * 0.78, s * yy, 8.6 - (1.2 * seg(t, T("frotar"), T("tardas")) if on else 0)))
    eg = seg(t, T("frotar") + 0.5, T("minutos", fin=True))
    S["ember"].location = LB + Vector((0, -0.45, 1.25)) if t < T("así que buscas") + 1 else LEJOS
    S["ember"].scale = (0.2 + 0.9 * eg,) * 3
    set_color(S["ember"], (0.35 + 0.65 * eg, 0.18 + 0.32 * eg, 0.08))
    for k, s in enumerate(S["smokeB"]):
        u = (t * 0.6 + k / 8) % 1.0
        if on:
            s.location = LB + Vector((0.6 * math.sin(4 * u + k), -0.6 - 0.8 * u, 1.3 + 4.0 * u)); s.scale = ((0.3 + 0.8 * u) * (0.3 + 0.7 * eg),) * 3
        else: s.location = LEJOS
    # ---------- C ----------
    TH = S["TH"]; tc = temp_C(t); ztop = 1.0 + (tc / 40.0) * 7.0
    bar = S["col"]; bar.location = TH + Vector((0, -0.12, (1.0 + ztop) / 2)); bar.scale = (1, 1, ztop - 1.0)
    lit = t >= T("grados", fin=True) - 0.1
    on_lump = lit and t < T("lo pones") + 0.3
    S["lump"].scale = (1, 1, 1) if t < T("lo pones") else (max(0.001, 1 - seg(t, T("lo pones"), T("lo pones") + 0.5)),) * 3
    put_flame(S["fC"], LC + Vector((0, 0, 1.4)), 2.6 * seg(t, T("grados", fin=True) - 0.1, T("grados", fin=True) + 0.3) if on_lump else 0.0, t)
    for k, s in enumerate(S["smokeC"]):
        u = (t * 0.5 + k / 6) % 1.0
        if on_lump: s.location = LC + Vector((0.8 * math.sin(3 * u + k), 0.3, 3.0 + 5 * u)); s.scale = (0.4 + 1.2 * u,) * 3
        else: s.location = LEJOS
    mc = S["mC"]
    if T("lo pones") <= t < T("pero es tan"):
        u = seg(t, T("lo pones"), T("lo pones") + 0.7)
        mc["e"].location = LC + Vector((-3.2, -1.5, mix(6.0, 1.6, u))); mc["e"].rotation_euler = (0.3 * math.sin(t * 1.6), 0.0, 0.06 * math.sin(t * 1.1))
        set_color(mc["head"], PALE)
    else: mc["e"].location = LEJOS
    for f, hp, k in zip(S["fP"], S["pocket_heads"], range(3)):
        tt = T("bolsillo") - 0.1 + 0.18 * k
        put_flame(f, hp, 1.5 * seg(t, tt, tt + 0.25) if T("pero es tan") <= t < T("así que separas") else 0.0, t, k)
    for k, s in enumerate(S["fume"]):
        u = (t * 0.45 + k / 10) % 1.0
        if T("y es venenoso") - 0.2 <= t < T("así que separas"):
            g = seg(t, T("y es venenoso") - 0.2, T("y es venenoso") + 0.4)
            s.location = LC2 + Vector((-2 + 4 * ((k * 0.37) % 1) + 0.8 * math.sin(2 * u + k), -0.6, 8.5 + 6 * u)); s.scale = ((0.5 + 1.4 * u) * g,) * 3
        else: s.location = LEJOS
    # ---------- D ----------
    md = S["mD"]
    show_d = T("así que separas") <= t < T("si la rascas")
    if show_d:
        hx = 4.5; hz = 6.0
        if t < T("en la caja"):            # la cerilla entera se separa del corte
            hz = mix(3.2, 6.0, seg(t, T("así que separas"), T("en dos", fin=True)))
        elif t < T("en la cabeza") + 0.4:
            hz = mix(6.0, 10.0, seg(t, T("en la caja"), T("la tira"))) if t < T("en la cabeza") - 0.4 else mix(10.0, 6.0, seg(t, T("en la cabeza") - 0.4, T("en la cabeza") + 0.4))
        if T("al rascar") - 0.6 <= t < T("pero la llama"):
            u = scrape_u(t); hz = mix(6.0, 2.7, seg(t, T("al rascar") - 0.6, T("al rascar")))
            hx = mix(4.5, -3.5, u)
        if T("pero la llama") <= t: hz = 6.0; hx = mix(-3.5, 1.0, seg(t, T("pero la llama"), T("pero la llama") + 0.8))
        if T("por eso solo") <= t:
            hx = 0.0; hz = mix(6.0, 7.6, seg(t, T("cada mitad"), T("sola", fin=True)))
        md.location = LD + Vector((hx, 0, hz))
    else: md.location = LEJOS
    # partículas rojas: las del recorrido en la superficie se vuelven blancas y prenden
    for o, pp in zip(S["red"], S["redpos"]):
        on_path = (pp.z > 0.7 and pp.y < 2.0) or (pp.y < 0.1 and pp.z > 0.35)
        col = RED
        if on_path and t >= T("una pizca"):
            # avanza de derecha a izquierda como el rascado
            k = seg(t, T("una pizca") + 0.4 * (4.5 - pp.x) / 8.0, T("una pizca") + 0.4 + 0.4 * (4.5 - pp.x) / 8.0)
            col = tuple(mix(a, b, k) for a, b in zip(RED, PALE))
            if T("y prende") <= t < T("esa chispa") + 1.0:
                fl = math.sin(t * 40 + pp.x * 3) * 0.5 + 0.5
                col = tuple(mix(a, b, fl) for a, b in zip(YELLOW, HOT))
            elif t >= T("esa chispa") + 1.0:
                col = (0.35, 0.3, 0.28)
        set_color(o, col)
    # chispa
    for k, s in enumerate(S["sparksD"]):
        t0 = T("y prende") + 0.05 * (k % 6)
        u = t - t0
        if show_d and 0 <= u < 0.7 and t < T("pero la llama"):
            rr = random.Random(k + 50)
            v = Vector((rr.uniform(-6, 6), rr.uniform(-3, -0.5), rr.uniform(1, 7)))
            s.location = md.location + Vector((rr.uniform(-1.5, 1.5), -0.3, -1.6)) + v * u + Vector((0, 0, -9 * u * u))
            s.scale = (1.4 - 1.8 * u,) * 3
        else: s.location = LEJOS
    # clorato que brilla, azufre que se enciende
    ca = T("esa chispa"); oa = T("que da oxígeno"); fu = T("fuuu")
    for o, pp in zip(S["clor"], S["cpos"]):
        g = seg(t, ca + 0.2 + 0.3 * (pp.z + 1.75) / 3.5, ca + 0.6 + 0.3 * (pp.z + 1.75) / 3.5) if ca <= t < T("pero la llama") else 0.0
        if t < ca and T("que suelta") <= t < T("y azufre"): g = 0.3 + 0.3 * math.sin(t * 9)
        set_color(o, tuple(mix(a, b, g) for a, b in zip(WHITE, (1.0, 0.65, 0.3))))
    for o, pp in zip(S["sulf"], S["spos"]):
        g = seg(t, fu - 0.3, fu + 0.1) if fu - 0.3 <= t < T("pero la llama") else 0.0
        set_color(o, tuple(mix(a, b, g) for a, b in zip(SULF, ORANGE)))
    # flechas de oxígeno (clorato → azufre)
    for k, a in enumerate(S["o2"]):
        if show_d and oa - 0.2 <= t < fu:
            c = md.matrix_world @ (S["cpos"][k * 3 % len(S["cpos"])] + Vector((0, -0.3, 0)))
            d = md.matrix_world @ (S["spos"][(k * 3 + 1) % len(S["spos"])] + Vector((0, -0.3, 0)))
            u = seg(t, oa - 0.2 + 0.1 * k, oa + 0.5 + 0.1 * k)
            put_arrow(a, c, c + (d - c) * max(u, 0.01))
        else: hide_arrow(a)
    for k, b in enumerate(S["bub"]):
        if show_d and T("que suelta") <= t < T("y azufre"):
            u = (t * 0.9 + k / 10) % 1.0; base = md.matrix_world @ (S["cpos"][k % len(S["cpos"])] + Vector((0, -0.25, 0)))
            b.location = base + Vector((0.2 * math.sin(6 * u + k), -0.3 - 0.6 * u, 1.2 * u)); b.scale = (1 - 0.5 * u,) * 3
        else: b.location = LEJOS
    fd = 0.0
    if show_d and fu - 0.2 <= t < T("pero la llama"): fd = 7.0 * seg(t, fu - 0.2, fu + 0.3)
    put_flame(S["fD"], md.location + Vector((0, -0.4, 1.0)), fd, t)
    # ---------- E: pared ----------
    me = S["mE"]
    if T("si la rascas") <= t < T("la inventó"):
        u = (t - T("si la rascas")) * 1.4
        x = 2.0 - 3.2 * abs(((u % 2.0) - 1.0)) if t < T("no pasa nada", fin=True) else 0.4
        me["e"].location = LE + Vector((x, -0.27, 7.0)); me["e"].rotation_euler = (0, -0.28, -0.12)
    else: me["e"].location = LEJOS
    apply_cam(S["cam"], *camera(t))

def CAMS():
    A, B, C, C2, D, E = LA, LB, LC, LC2, LD, LE
    return [
        (0.0, [(0, (A.x + 2.4, A.y - 7.0, 2.3), (A.x + 1.4, A.y - 2.0, 0.6), 35), (STRIKE1, (A.x - 0.6, A.y - 7.6, 2.4), (A.x - 1.2, A.y - 2.2, 0.9), 35),
               (2.3, (A.x + 0.6, A.y - 11.5, 4.2), (A.x + 0.2, A.y - 2.8, 2.0), 35), (T("necesitas"), (A.x + 2, A.y - 17, 8), (A.x + 0.5, A.y - 2, 1.6), 35)]),
        (T("necesitas"), [(0, (B.x + 6, B.y - 20, 9), (B.x, B.y, 4.5), 35), (T("frotar"), (B.x + 3, B.y - 17, 6), (B.x, B.y, 4.0), 35),
                          (T("tardas"), (B.x + 2.5, B.y - 14, 4.5), (B.x, B.y, 2.6), 35), (T("así que buscas"), (B.x + 2.0, B.y - 13, 4.0), (B.x, B.y, 2.4), 35)]),
        (T("así que buscas"), [(0, (C.x + 7, C.y - 15, 8), (C.x + 1.5, C.y, 3.8), 35), (T("el fósforo blanco"), (C.x + 3.5, C.y - 13, 6), (C.x + 1.6, C.y, 3.8), 35),
                               (T("grados"), (C.x + 2.5, C.y - 12.5, 5.5), (C.x + 1.6, C.y, 3.9), 35), (T("lo pones") + 0.3, (C.x - 1.6, C.y - 11, 3.6), (C.x - 1.4, C.y - 1.5, 1.8), 35),
                               (T("pero es tan") - 0.01, (C.x - 2.2, C.y - 10.5, 3.4), (C.x - 1.4, C.y - 1.5, 1.8), 35)]),
        (T("pero es tan"), [(0, (C2.x + 3, C2.y - 19, 9), (C2.x, C2.y, 6.5), 35), (T("y es venenoso"), (C2.x + 1, C2.y - 21, 10), (C2.x, C2.y, 8.0), 35),
                            (T("así que separas"), (C2.x - 2, C2.y - 21, 10), (C2.x, C2.y, 8.0), 35)]),
        (T("así que separas"), [(0, (D.x + 6, D.y - 30, 12), (D.x + 1, D.y, 3.0), 35), (T("en la caja"), (D.x + 2, D.y - 22, 5), (D.x, D.y, 1.0), 35),
                                (T("la tira"), (D.x - 3, D.y - 13, 2.6), (D.x - 1.5, D.y, 0.3), 35), (T("es mucho más"), (D.x + 2.5, D.y - 13, 2.4), (D.x + 1.5, D.y, 0.3), 35),
                                (T("en la cabeza"), (D.x + 5, D.y - 15, 7.5), (D.x + 4.5, D.y, 5.5), 35), (T("y azufre"), (D.x + 4, D.y - 13, 7.0), (D.x + 4.5, D.y, 5.8), 35),
                                (T("al rascar") - 0.3, (D.x + 3, D.y - 24, 6.0), (D.x + 1, D.y, 2.8), 35), (T("una pizca"), (D.x - 1, D.y - 20, 4.5), (D.x - 2.5, D.y, 1.8), 35),
                                (T("esa chispa"), (D.x - 2.5, D.y - 15, 4.5), (D.x - 3.5, D.y, 2.6), 35), (T("fuuu"), (D.x - 3, D.y - 24, 7.5), (D.x - 3.5, D.y, 4.5), 35),
                                (T("pero la llama") - 0.01, (D.x - 3, D.y - 24, 7.5), (D.x - 3.5, D.y, 4.5), 35)]),
        (T("pero la llama"), [(0, (A.x + 1.0, A.y - 17.0, 5.6), (A.x + 0.6, A.y - 5.5, 3.6), 35), (T("así que mojas"), (A.x + 1.5, A.y - 17.5, 5.0), (A.x + 0.7, A.y - 5.5, 3.6), 35),
                              (T("por eso solo") - 0.01, (A.x + 1.0, A.y - 17.5, 5.2), (A.x + 0.7, A.y - 5.5, 3.6), 35)]),
        (T("por eso solo"), [(0, (D.x + 5, D.y - 32, 10), (D.x + 3, D.y, 3.0), 35), (T("cada mitad"), (D.x + 4, D.y - 34, 9), (D.x + 3, D.y, 3.6), 35)]),
        (T("si la rascas"), [(0, (E.x + 2, E.y - 15, 9.5), (E.x + 1.8, E.y - 0.5, 6.4), 35), (T("no pasa nada"), (E.x + 1.5, E.y - 14, 9.0), (E.x + 1.8, E.y - 0.5, 6.6), 35)]),
        (T("la inventó"), [(0, (A.x + 1.5, A.y - 17, 6.0), (A.x + 1.1, A.y - 5.0, 3.2), 35), (T("sígueme"), (A.x + 3, A.y - 20, 8), (A.x + 1.0, A.y - 3.5, 2.6), 35),
                           (DUR + 1, (A.x + 4, A.y - 23, 9), (A.x + 1.0, A.y - 3, 2.4), 35)]),
    ]

def camera(t):
    segs = CAMS(); k = 0
    for i, (st, _) in enumerate(segs):
        if t >= st: k = i
    st, ks = segs[k]
    ks = [(st if a == 0 else a, p, q, l) for a, p, q, l in ks]
    if ks[-1][0] <= t: ks = ks + [(t + 1, ks[-1][1], ks[-1][2], ks[-1][3])]
    pos, tgt, lens = cam_state(t, ks, drift=0.01)
    tgt = tgt + Vector((0, 0, 0.17 * (tgt - pos).length))     # el objeto queda algo más abajo (subtítulo y marcadores arriba)
    return pos, tgt, lens

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v)
    mw = S["mA"]["e"].matrix_world; md = S["mD"]
    return {"headA": Pj(mw @ Vector((0, 0, 0))), "parA": Pj(mw @ Vector((2.0, 0, 0))), "woodA": Pj(mw @ Vector((3.0, 0, 0))),
            "board": Pj(LB + Vector((-4.5, -2, 1.2))), "spin": Pj(LB + Vector((0, 0, 7))), "ember": Pj(LB + Vector((0, -0.45, 1.3))),
            "lump": Pj(LC + Vector((0, 0, 1.2))), "thermo": Pj(S["TH"] + Vector((0, 0, 9.5))), "matchC": Pj(S["mC"]["e"].location),
            "pocket": Pj(LC2 + Vector((0, 0, 4))),
            "red": Pj(LD + Vector((-4.5, -0.1, 0.0))), "glass": Pj(LD + Vector((4.0, -0.1, 0.0))), "strip": Pj(LD + Vector((0, 0, 0))),
            "clor": Pj(md.location + Vector((-1.2, 0, 0.8))), "sulf": Pj(md.location + Vector((1.2, 0, -0.6))), "headD": Pj(md.location + Vector((0, 0, 1.9))),
            "wallM": Pj(S["mE"]["e"].location), "wall": Pj(LE + Vector((-5, 0, 3.5)))}

if __name__ == "__main__":
    run("cerilla", build, pose, anchors)
