# «Así funciona tu ratón»: primer plano de una mano deslizando el ratón con su luz roja; el ratón se da la vuelta y
# enseña el led. Corte lateral gigante: el led ilumina la mesa casi rozando, cada pelusa, fibra y arañazo hace sombra,
# la luz sube por la lente hasta la cámara. Rejilla de 18×18 píxeles con el mapa de manchas; la foto nueva se compara
# con la anterior y las manchas se van 3 puntos a la izquierda; el ratón va a la derecha; la flecha del monitor se mueve
# lo mismo. Ratón rápido (1.500 → 17.000 fotos/s) y, al final, sobre un cristal: no hay manchas y la flecha no se mueve.
import bpy, bmesh, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector

T0, DUR = cargar("raton")
_TC = {}
def T(k, n=1, fin=False):
    key = (k, n, fin)
    if key not in _TC: _TC[key] = T0(k, n, fin)
    return _TC[key]

BG = (0.07, 0.07, 0.1); WOOD = (0.66, 0.45, 0.28); WOOD_D = (0.5, 0.33, 0.2); MOUSE = (0.84, 0.89, 0.97); BASE = (0.18, 0.18, 0.2)
GAMER = (0.14, 0.15, 0.18); RED = (1.0, 0.18, 0.15); GLOW = (0.85, 0.12, 0.1); SKIN = (0.93, 0.72, 0.58); WHEEL = (0.25, 0.26, 0.3)
LENS = (0.55, 0.8, 0.95); CHIP = (0.1, 0.1, 0.12); PIN = (0.85, 0.7, 0.3); PCB = (0.15, 0.5, 0.3); SHADOW = (0.16, 0.1, 0.06)
GLASS = (0.62, 0.8, 0.88); FLUFF = (0.8, 0.78, 0.74); YL = (1.0, 0.82, 0.16); GREEN = (0.3, 0.9, 0.45); CYAN = (0.2, 0.9, 1.0)
PX_D = (0.18, 0.04, 0.04); PX_L = (0.98, 0.55, 0.48); SCREEN = (0.2, 0.42, 0.75); WIN = (0.85, 0.88, 0.94)
LEJOS = Vector((0, 300, -300))
LA = Vector((0, 0, 0)); LB = Vector((30, 0, 0)); LC = Vector((60, 0, 0)); LD = Vector((90, 0, 0))
GX = 2.6                         # posición del cristal en A
NG = 18; CS = 0.2                # rejilla 18 × 18

def half_ell(rx, ry, rz, loc, color, unique=False, seg=40):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, segments=seg, ring_count=seg // 2, location=loc); o = bpy.context.object
    bm = bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < -1e-4], context='VERTS')
    for v in bm.verts: v.co.x *= rx; v.co.y *= ry; v.co.z *= rz
    bm.to_mesh(o.data); bm.free()
    return setup(o, color, None, True, unique)

def cone(r, h, color, unique=False):
    bpy.ops.mesh.primitive_cone_add(radius1=r, radius2=0, depth=h, location=(0, 0, 0), vertices=16); o = bpy.context.object
    for vv in o.data.vertices: vv.co.z += h / 2
    return setup(o, color, None, True, unique)

def arrow(color, r):
    """flecha 3D: barra + punta (se coloca con put_arrow)"""
    return [bar_obj(color, r=r), cone(r * 2.6, r * 6, color)]

def put_arrow(a, p0, p1):
    p0, p1 = Vector(p0), Vector(p1); d = p1 - p0; L = d.length
    if L < 1e-3: hide_arrow(a); return
    hl = min(a[0]["r"] * 6, L * 0.6); q = p1 - d.normalized() * hl
    bar_set(a[0], p0, q); a[1].location = q; a[1].rotation_mode = 'QUATERNION'
    a[1].rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())

def hide_arrow(a):
    bar_set(a[0], LEJOS, LEJOS + Vector((0, 0, 0.01))); a[1].location = LEJOS

def hide_bar(o): bar_set(o, LEJOS, LEJOS + Vector((0, 0, 0.01)))

def mouse(loc):
    e = empty(loc)
    shell = half_ell(0.3, 0.55, 0.32, (0, 0, 0.05), MOUSE, unique=True); shell.parent = e
    rounded_slab(0.6, 1.1, 0.26, 0.05, (0, 0, 0.0), BASE, e)
    cyl(0.045, 0.035, (0, 0.27, 0.32), WHEEL, e, rot=(0, math.pi / 2, 0))
    box((0.012, 0.22, 0.03), (0, 0.44, 0.25), WHEEL, e, rot=(-0.6, 0, 0))
    # parte de abajo (z < 0 local)
    for x, y in ((-0.17, 0.38), (0.17, 0.38), (-0.17, -0.38), (0.17, -0.38)):
        box((0.12, 0.1, 0.012), (x, y, -0.006), (0.92, 0.92, 0.94), e)
    cyl(0.1, 0.004, (0, 0.05, -0.002), (0.05, 0.05, 0.06), e)
    cyl(0.045, 0.01, (0, 0.06, -0.005), LENS, e)
    torus(0.1, 0.012, (0, 0.05, -0.004), RED, e)
    led = sph(0.05, (0, -0.12, -0.008), RED, e, scale=(1, 1, 0.5), unique=True)
    strip = box((0.62, 0.03, 0.015), (0, -0.5, 0.06), MOUSE, e, unique=True)
    return e, shell, led, strip

def hand():
    e = empty(LEJOS)
    sph(1, (0, -0.2, 0.42), SKIN, e, scale=(0.29, 0.33, 0.12))
    for x, l in ((-0.1, 0.46), (0.03, 0.48), (0.15, 0.44)):
        cyl(0.045, l, (x, 0.14, 0.37), SKIN, e, rot=(math.pi / 2 - 0.22, 0, 0))
        sph(0.045, (x, 0.14 + l / 2 * 0.976, 0.37 - l / 2 * 0.218), SKIN, e)
    cyl(0.045, 0.3, (-0.3, -0.05, 0.17), SKIN, e, rot=(math.pi / 2, 0, -0.25))
    cyl(0.16, 0.7, (0, -0.75, 0.46), SKIN, e, rot=(math.pi / 2 - 0.12, 0, 0))
    return e

def build():
    sc, cam = scene_setup(world=BG, shadow=0.32); cam.data.clip_start = 0.01
    S = {"cam": cam}
    dyn = [cam]
    # ---------- A: mesa, cristal, ratón y mano ----------
    box((24, 24, 0.4), LA + Vector((0, 0, -0.2)), WOOD)
    rng = random.Random(3)
    for k in range(14):
        box((5, rng.uniform(0.012, 0.025), 0.006), LA + Vector((0, -2.5 + 5 * k / 14 + rng.uniform(0, 0.2), 0.0)), WOOD_D)
    box((1.8, 2.6, 0.03), LA + Vector((GX, 0, 0.015)), GLASS)
    S["ms"], S["shell"], S["led"], S["strip"] = mouse(LA); dyn.append(S["ms"])
    S["glow"] = sph(1, LEJOS, GLOW, scale=(0.36, 0.32, 0.004)); dyn.append(S["glow"])
    S["hand"] = hand(); dyn.append(S["hand"])
    S["arrA"] = arrow(GREEN, 0.03); dyn.append(S["arrA"])
    # ---------- B: corte lateral gigante ----------
    S["deskB"] = box((40, 10, 2), LB + Vector((0, 4.4, -1)), WOOD, unique=True); dyn.append(S["deskB"])
    S["glassB"] = box((40, 10, 0.3), LEJOS, GLASS); dyn.append(S["glassB"])
    bpy.ops.mesh.primitive_cube_add(size=1, location=LB + Vector((0, -5, 3))); cutter = bpy.context.object; cutter.scale = (20, 10, 20); cutter.hide_render = True
    dyn.append(cutter)
    def cortar(o, th=None, inner=(0.97, 0.97, 0.98)):
        if th:
            o.data.materials.append(mat(inner, unique=True))
            m = o.modifiers.new("sol", "SOLIDIFY"); m.thickness = th; m.offset = -1; m.material_offset = 1; m.material_offset_rim = 1
        b = o.modifiers.new("cut", "BOOLEAN"); b.operation = 'DIFFERENCE'; b.object = cutter
        dyn.append(o); return o
    cortar(half_ell(4.4, 2.6, 2.6, LB + Vector((0, 0, 0.4)), MOUSE, unique=True), 0.15)
    for x0, x1 in ((-4.2, -1.6), (0.7, 4.2)):
        box((x1 - x0, 2.4, 0.2), LB + Vector(((x0 + x1) / 2, 1.2, 0.3)), BASE)
    for x in (-3.4, 3.4): box((0.9, 2.2, 0.2), LB + Vector((x, 1.2, 0.1)), (0.92, 0.92, 0.94))
    box((6.4, 2.2, 0.12), LB + Vector((0, 1.3, 1.75)), PCB)
    box((1.3, 1.0, 0.45), LB + Vector((0.0, 0.7, 1.45)), CHIP)
    for k in range(5):
        box((0.06, 0.5, 0.12), LB + Vector((-0.5 + 0.25 * k, 0.45, 1.65)), PIN)
    sph(1, LB + Vector((0, 0.6, 0.85)), LENS, scale=(0.55, 0.55, 0.16))
    box((1.4, 0.8, 0.08), LB + Vector((0, 0.8, 0.85)), (0.3, 0.3, 0.34))
    box((0.5, 0.6, 0.4), LB + Vector((-2.25, 0.7, 0.62)), (0.3, 0.3, 0.34))
    box((0.08, 0.3, 1.0), LB + Vector((-2.2, 0.7, 1.2)), PIN)
    S["ledB"] = sph(0.17, LB + Vector((-2.0, 0.5, 0.58)), RED, unique=True); dyn.append(S["ledB"])
    S["rays"] = [bar_obj(RED, r=0.028, unique=True) for _ in range(7)]; dyn.append(S["rays"])
    S["rays2"] = [bar_obj(RED, r=0.028) for _ in range(7)]; dyn.append(S["rays2"])
    S["up"] = [bar_obj((1.0, 0.55, 0.45), r=0.03) for _ in range(5)]; dyn.append(S["up"])
    # relieve de la mesa: pelusa, fibra, arañazo (y sus sombras)
    bumps = []
    pel = empty(LB + Vector((-0.55, 0.45, 0)))
    for dx, dz, r in ((0, 0.06, 0.09), (0.09, 0.05, 0.07), (-0.07, 0.04, 0.06), (0.03, 0.13, 0.06)):
        sph(r, (dx, 0, dz), FLUFF, pel)
    fib = cyl(0.055, 1.6, LB + Vector((0.15, 0.6, 0.02)), WOOD_D, rot=(math.pi / 2, 0, 0))
    scr = box((0.14, 1.6, 0.012), LB + Vector((0.8, 0.6, 0.004)), (0.22, 0.14, 0.08))
    lip = box((0.05, 1.6, 0.06), LB + Vector((0.71, 0.6, 0.03)), WOOD)
    bmp = [sph(0.045, LB + Vector((x, 0.35, 0.0)), WOOD_D) for x in (-0.25, 0.45, 1.05)]
    S["relief"] = [pel, fib, scr, lip] + bmp; dyn.append(S["relief"])
    S["shad"] = []
    for x, h in ((-0.45, 0.16), (0.21, 0.08), (0.74, 0.06), (-0.21, 0.045), (0.49, 0.045), (1.09, 0.045)):
        o = box((1, 0.4, 0.004), LEJOS, SHADOW); o["x"] = x; o["h"] = h; S["shad"].append(o)
    dyn.append(S["shad"])
    # ---------- C: rejillas de 18 × 18 ----------
    S["gridN"] = []; S["gridO"] = []
    S["frameN"] = box((NG * CS + 0.25, 0.05, NG * CS + 0.25), LEJOS, (0.22, 0.23, 0.28))
    S["frameO"] = box((NG * CS + 0.25, 0.05, NG * CS + 0.25), LEJOS, (0.22, 0.23, 0.28))
    for i in range(NG):
        for j in range(NG):
            S["gridN"].append(box((CS * 0.86, 0.05, CS * 0.86), LEJOS, PX_L, unique=True))
            S["gridO"].append(box((CS * 0.86, 0.05, CS * 0.86), LEJOS, PX_L, unique=True))
    dyn += [S["gridN"], S["gridO"], S["frameN"], S["frameO"]]
    S["arrC"] = arrow(YL, 0.07); S["arrC2"] = arrow(GREEN, 0.07); dyn += [S["arrC"], S["arrC2"]]
    # ---------- D: monitor ----------
    box((30, 10, 0.4), LD + Vector((0, 2, -0.2)), WOOD)
    box((0.6, 0.4, 1.2), LD + Vector((0, 0.5, 0.6)), (0.2, 0.2, 0.23))
    box((1.6, 1.0, 0.06), LD + Vector((0, 0.4, 0.03)), (0.2, 0.2, 0.23))
    o = rounded_slab(5.0, 3.0, 0.12, 0.2, LD + Vector((0, 0.3, 2.6)), (0.12, 0.12, 0.14)); o.rotation_euler = (math.pi / 2, 0, 0)
    o = rounded_slab(4.7, 2.7, 0.06, 0.02, LD + Vector((0, 0.105, 2.6)), SCREEN); o.rotation_euler = (math.pi / 2, 0, 0)
    for x, z, w, h in ((-1.3, 2.9, 1.5, 1.2), (0.6, 2.4, 1.8, 1.3)):
        box((w, 0.02, h), LD + Vector((x, 0.07, z)), WIN)
        box((w, 0.025, 0.16), LD + Vector((x, 0.065, z + h / 2 - 0.08)), (0.35, 0.38, 0.45))
    S["ticks"] = [box((0.04, 0.02, 0.18), LEJOS, YL) for _ in range(4)]; dyn.append(S["ticks"])
    me = bpy.data.meshes.new("cur"); bm = bmesh.new()
    pts = [(0, 0), (0, -0.42), (0.1, -0.32), (0.17, -0.47), (0.23, -0.44), (0.16, -0.3), (0.3, -0.3)]
    vb = [bm.verts.new((x, 0, z)) for x, z in pts]; bm.faces.new(vb); bm.to_mesh(me); bm.free()
    cur = bpy.data.objects.new("cur", me); bpy.context.collection.objects.link(cur); setup(cur, (0.98, 0.98, 1.0))
    me2 = me.copy(); out = bpy.data.objects.new("curo", me2); bpy.context.collection.objects.link(out); setup(out, (0.02, 0.02, 0.03))
    out.parent = cur; out.scale = (1.25, 1, 1.18); out.location = (-0.03, 0.01, 0.035)
    S["cur"] = cur; dyn.append(cur)
    join_static(dyn)
    return sc, S

# ---------- movimiento del ratón en A ----------
def mouse_xy(t):
    """posición del ratón (x, y, yaw) en la mesa"""
    if t < T("mira por dentro"):
        return 0.28 * math.sin(t * 2.4), 0.06 * math.sin(t * 1.7), 0.12 * math.sin(t * 2.4 + 0.5)
    if T("es que tú") - 0.3 <= t < T("un chip"):
        u = seg(t, T("es que tú"), T("derecha", fin=True)); return -0.4 + 0.8 * u, 0, 0
    if T("así que") - 0.2 <= t < T("por eso falla"):
        f = 2.0 + 3.5 * seg(t, T("así que"), T("más rápido", fin=True)) + 3.0 * seg(t, T("los de videojuegos"), T("diecisiete", fin=True))
        ph = 2.4 * (t - T("así que")) + 0.5 * f * (t - T("así que")) ** 1.0
        return 0.4 * math.sin(ph * 1.6), 0.08 * math.sin(ph), 0.15 * math.sin(ph * 1.6 + 0.4)
    if T("por eso falla") <= t < T("es tan liso"):
        u = seg(t, T("por eso falla"), T("cristal", fin=True)); return mix(0.0, GX, u), 0, 0
    if T("la cámara ve") <= t:
        return GX + 0.35 * math.sin((t - T("la cámara ve")) * 4), 0.05 * math.sin(t * 3), 0.1 * math.sin(t * 4)
    return 0.15 * math.sin(t * 1.5), 0, 0

def pose(t, S):
    # ---------- A ----------
    x, y, yaw = mouse_xy(t)
    onglass = abs(x - GX) < 0.9
    z0 = 0.012 + (0.03 if onglass else 0)
    flip = T("le das") - 0.1 <= t < T("ilumina")
    ms = S["ms"]
    if flip:
        u = seg(t, T("le das"), T("vuelta", fin=True) + 0.2)
        ms.location = LA + Vector((0, 0, z0 + 0.5 * u)); ms.rotation_euler = (0, math.pi * u, 0.3 * u)
    else:
        ms.location = LA + Vector((x, y, z0)); ms.rotation_euler = (0, 0, yaw)
    gamer = t >= T("los de videojuegos") and t < T("por eso falla")
    set_color(S["shell"], GAMER if gamer else MOUSE)
    hue = (t * 0.8) % 1.0
    rgb = tuple(0.5 + 0.5 * math.cos(2 * math.pi * (hue + k / 3)) for k in range(3))
    set_color(S["strip"], rgb if gamer else MOUSE)
    blink = 0.75 + 0.25 * math.sin(t * 40) if flip else 1.0
    set_color(S["led"], tuple(c * blink for c in RED))
    if not flip and not onglass:
        S["glow"].location = LA + Vector((x, y + 0.03, 0.004)); S["glow"].rotation_euler = (0, 0, yaw)
    else: S["glow"].location = LEJOS
    hand_on = (not flip) and (t < T("le das") or T("es que tú") - 0.3 <= t < T("un chip") or t >= T("así que") - 0.3)
    if hand_on:
        lift = 0.0
        if t < T("le das"): lift = seg(t, T("mira por dentro"), T("mira por dentro") + 0.4) * 1.5
        S["hand"].location = ms.location + Vector((0, 0, lift)); S["hand"].rotation_euler = (0, 0, yaw)
    else: S["hand"].location = LEJOS
    if T("es que tú") <= t < T("un chip"):
        u = seg(t, T("es que tú"), T("derecha", fin=True))
        put_arrow(S["arrA"], LA + Vector((x + 0.35, 0, 0.3)), LA + Vector((x + 0.45 + 0.5 * u, 0, 0.3)))
    else: hide_arrow(S["arrA"])
    # ---------- B ----------
    glassB = t >= T("es tan liso") - 0.2
    S["deskB"].location = LEJOS if glassB else LB + Vector((0, 4.4, -1))
    S["glassB"].location = LB + Vector((0, 4.4, -0.15)) if glassB else LEJOS
    for o in S["relief"]:
        if "home" not in o: o["home"] = list(o.location)
        o.location = LEJOS if glassB else Vector(o["home"])
    led = LB + Vector((-2.0, 0.5, 0.58))
    on = seg(t, T("ilumina"), T("ilumina") + 0.5)
    hits = [-1.0 + 0.32 * k for k in range(7)]
    for k, (r, r2) in enumerate(zip(S["rays"], S["rays2"])):
        flick = 0.75 + 0.25 * math.sin(t * 9 + k)
        if on > 0.01 and t >= T("ilumina") - 0.1:
            hx = hits[k]; hit = LB + Vector((hx, 0.5, 0.0))
            bar_set(r, led, led.lerp(hit, on))
            set_color(r, tuple(c * flick for c in RED))
            if glassB:
                d = (hit - led).normalized(); a = hit + d * (0.3 / -d.z); bar_set(r2, a, a + d * (1.6 / -d.z))
            else: hide_bar(r2)
        else: hide_bar(r); hide_bar(r2)
    # sombras: crecen con «hacen una sombra»
    sh = seg(t, T("así cada"), T("sombra", fin=True))
    ang = math.tan(math.radians(16))
    for o in S["shad"]:
        if glassB or t < T("así cada") - 0.1: o.location = LEJOS; continue
        L = max(0.01, o["h"] / ang * sh); o.scale = (L, 0.16 if o["h"] < 0.05 else 0.48, 0.004)
        o.location = LB + Vector((o["x"] + L / 2, 0.45 if o["h"] < 0.05 else 0.6, 0.003))
    # luz que sube a la lente y a la cámara
    u = seg(t, T("encima hay"), T("lente", fin=True)); u2 = seg(t, T("detrás"), T("diminuta", fin=True))
    for k, b in enumerate(S["up"]):
        if T("encima hay") - 0.1 <= t < T("tiene solo") and not glassB:
            p0 = LB + Vector((-0.4 + 0.2 * k, 0.5, 0.02)); p1 = LB + Vector((-0.2 + 0.1 * k, 0.5, 0.75))
            p2 = LB + Vector((-0.1 + 0.05 * k, 0.5, 1.22))
            if u2 <= 0.01: bar_set(b, p0, p0.lerp(p1, u))
            else: bar_set(b, p0, p1.lerp(p2, u2))
        else: hide_bar(b)
    # ---------- C ----------
    pose_grids(t, S)
    # ---------- D ----------
    a0 = T("y se lo manda")
    if t < T("la cámara ve"):
        steps = int(4 * seg(t, T("que mueve"), T("lo mismo", fin=True)) + 1e-6)
        steps = min(3, steps)
        cx = -1.0 + 0.35 * steps
    else:
        cx = -1.0 + 0.35 * 3
    S["cur"].location = LD + Vector((cx, 0.0, 2.75))
    for k, o in enumerate(S["ticks"]):
        if t >= T("que mueve") and k <= steps if t < T("la cámara ve") else False:
            o.location = LD + Vector((-1.0 + 0.35 * k + 0.02, 0.0, 2.15))
        else: o.location = LEJOS
    apply_cam(S["cam"], *camera(t))

# ---------- rejillas ----------
rb = random.Random(11)
BLOBS = [(9.5, 8.5, 1.6, 1.0)] + [(rb.uniform(-8, 28), rb.uniform(-2, 20), rb.uniform(1.0, 2.4), rb.uniform(0.6, 1.0)) for _ in range(34)]
def hsh(i, j): return (math.sin(i * 12.9898 + j * 78.233) * 43758.5453) % 1.0
def field(u, v, glass=False):
    if glass: return 0.62
    s = 0.0
    for cx, cy, r, a in BLOBS: s += a * math.exp(-((u - cx) ** 2 + (v - cy) ** 2) / (r * r))
    return max(0.0, min(1.0, 0.85 - 0.75 * s + 0.12 * (hsh(math.floor(u), math.floor(v)) - 0.5)))
def tracked(u, v):
    cx, cy, r, a = BLOBS[0]; return math.exp(-((u - cx) ** 2 + (v - cy) ** 2) / (r * r)) > 0.45

def cellpos(base, i, j): return base + Vector(((i - NG / 2 + 0.5) * CS, 0, (j - NG / 2 + 0.5) * CS))

def paint(cells, base, t, ox, oy, appear=1.0, mode="map", glass=False, hl=False):
    for idx, o in enumerate(cells):
        i, j = divmod(idx, NG)
        a = seg(appear * (NG + 6) - (NG - 1 - j), 0, 1) if appear < 1 else 1.0
        if a <= 0.01: o.location = LEJOS; continue
        o.location = cellpos(base, i, j); o.scale = (a, 1, a)
        if mode == "blank": col = (0.42, 0.4, 0.42)
        else:
            u, v = i + ox, j + oy; f = field(u, v, glass)
            col = tuple(mix(PX_D[k], PX_L[k], f) for k in range(3))
            if glass: col = tuple(c * (0.97 + 0.03 * math.sin(t * 20 + idx)) for c in col)
            if hl and tracked(u, v): col = YL
        set_color(o, col)

def hide_cells(cells):
    for o in cells: o.location = LEJOS

def pose_grids(t, S):
    a0 = T("tiene solo"); split = T("compara cada"); end = T("y se lo manda")
    glass = T("la cámara ve") - 0.3 <= t < T("y la flecha")
    vis = (a0 - 0.2 <= t < end) or glass
    if not vis:
        hide_cells(S["gridN"]); hide_cells(S["gridO"]); S["frameN"].location = LEJOS; S["frameO"].location = LEJOS
        hide_arrow(S["arrC"]); hide_arrow(S["arrC2"]); return
    sp = seg(t, split, split + 0.6) if not glass else 0.0
    baseN = LC + Vector((2.0 * sp, 0, 0)); baseO = LC + Vector((-2.0, 0, 0))
    S["frameN"].location = baseN + Vector((0, 0.06, 0))
    appear = seg(t, a0, T("píxeles", fin=True)) if t < T("trescientos") else 1.0
    mode = "blank" if t < T("con eso") else "map"
    ox, oy = 0.0, 0.0
    if T("el ratón no guarda") <= t < split:
        k = int((t - T("el ratón no guarda")) * 12); ox = 0.5 * k; oy = 0.3 * math.sin(k)
    elif t >= split:
        ox = 6.0 + 3.0 * seg(t, T("si las manchas"), T("izquierda", fin=True))
    else:
        ox = 6.0 * seg(t, T("y aquí viene"), T("el ratón no guarda")) if t >= T("y aquí viene") else 0.0
    if glass: ox = 0
    hl = t >= T("si las manchas") - 0.3 and not glass
    if t >= split and t < T("compara cada") + 0.0: pass
    paint(S["gridN"], baseN, t, ox, oy, appear, mode, glass, hl)
    if t >= split and not glass:
        pa = seg(t, split, split + 0.6)
        paint(S["gridO"], baseO, t, 6.0, 0.0, 1.0, "map", False, hl)
        for o in S["gridO"]:
            if o.location.y < 100: o.scale = (pa, 1, pa)
        S["frameO"].location = baseO + Vector((0, 0.06, 0))
    else: hide_cells(S["gridO"]); S["frameO"].location = LEJOS
    zt = NG * CS / 2 + 0.45
    if T("si las manchas") <= t < end:
        u = seg(t, T("si las manchas"), T("izquierda", fin=True))
        put_arrow(S["arrC"], baseN + Vector((0.6, -0.15, zt)), baseN + Vector((0.6 - 1.4 * u - 0.01, -0.15, zt)))
    else: hide_arrow(S["arrC"])
    if T("y en qué") <= t < end:
        u = seg(t, T("y en qué"), T("dirección", fin=True))
        put_arrow(S["arrC2"], LC + Vector((-0.8, -0.15, -zt)), LC + Vector((-0.8 + 1.6 * u + 0.01, -0.15, -zt)))
    else: hide_arrow(S["arrC2"])

# ---------- cámara ----------
def CAMS():
    B, C, D = LB, LC, LD
    return [
        (0.0, [(0, (0.75, 1.15, 0.32), (0.0, 0.0, 0.15), 30), (T("mira por dentro"), (0.85, 1.35, 0.55), (0.0, 0.0, 0.2), 30),
               (T("le das"), (0.6, 1.4, 1.2), (0, 0, 0.4), 30), (T("es un led"), (0.25, 0.75, 1.55), (0, 0, 0.5), 32), (T("ilumina"), (0.2, 0.7, 1.6), (0, -0.02, 0.5), 34)]),
        (T("ilumina"), [(0, (B.x - 0.5, B.y - 13.0, 2.6), (B.x - 0.3, 0.5, 1.1), 35), (T("casi rozando"), (B.x - 0.8, B.y - 8.5, 1.4), (B.x - 0.8, 0.5, 0.45), 35),
                        (T("así cada"), (B.x + 0.1, B.y - 4.2, 0.9), (B.x + 0.15, 0.5, 0.1), 35), (T("sombra"), (B.x + 0.3, B.y - 4.0, 0.75), (B.x + 0.3, 0.5, 0.12), 35),
                        (T("encima hay"), (B.x + 0.1, B.y - 7.0, 1.4), (B.x, 0.5, 0.75), 35), (T("diminuta"), (B.x + 0.1, B.y - 6.0, 1.7), (B.x, 0.5, 1.15), 35),
                        (T("pero no es"), (B.x - 0.3, B.y - 5.0, 1.9), (B.x, 0.6, 1.4), 35)]),
        (T("tiene solo"), [(0, (C.x, C.y - 9.5, 0.2), (C.x, 0, -0.2), 35), (T("con eso"), (C.x + 0.3, C.y - 8.8, 0.1), (C.x, 0, -0.2), 35),
                           (T("y aquí viene"), (C.x - 0.3, C.y - 9.0, 0.3), (C.x, 0, -0.2), 35), (T("compara cada"), (C.x, C.y - 17.0, 0.2), (C.x, 0, -0.3), 35),
                           (T("es que tú") - 0.01, (C.x + 0.2, C.y - 16.8, 0.2), (C.x, 0, -0.3), 35)]),
        (T("es que tú") - 0.3, [(0, (0.0, -0.7, 2.7), (0.0, 0.15, 0.0), 30), (T("derecha"), (0.3, -0.65, 2.6), (0.3, 0.15, 0.0), 30)]),
        (T("un chip"), [(0, (C.x + 0.3, C.y - 17.0, 0.2), (C.x, 0, -0.3), 35), (T("y se lo manda"), (C.x - 0.2, C.y - 16.8, 0.3), (C.x, 0, -0.3), 35)]),
        (T("y se lo manda"), [(0, (D.x + 0.5, D.y - 9.0, 2.8), (D.x, 0, 2.4), 35), (T("que mueve"), (D.x - 0.3, D.y - 6.0, 2.8), (D.x - 0.4, 0, 2.5), 35)]),
        (T("así que") - 0.2, [(0, (0.9, 1.6, 0.6), (0, 0, 0.15), 32), (T("un ratón sencillo"), (1.2, 2.2, 0.9), (0, 0, 0.15), 32),
                              (T("los de videojuegos"), (0.9, 1.6, 0.55), (0, 0, 0.18), 32)]),
        (T("por eso falla"), [(0, (-0.5, 1.9, 1.0), (0.3, 0.0, 0.1), 32), (T("cristal", fin=True), (-0.6, 1.8, 0.9), (0.3, 0.0, 0.1), 32)]),
        (T("es tan liso") - 0.2, [(0, (B.x + 0.2, B.y - 9.5, 0.9), (B.x - 0.3, 0.5, 0.0), 35), (T("la cámara ve"), (B.x - 0.2, B.y - 9.0, 0.6), (B.x - 0.3, 0.5, -0.2), 35)]),
        (T("la cámara ve") - 0.3, [(0, (C.x, C.y - 9.5, 0.2), (C.x, 0, -0.2), 35)]),
        (T("y la flecha"), [(0, (D.x - 0.4, D.y - 6.0, 2.8), (D.x - 0.4, 0, 2.5), 35)]),
        (T("sígueme"), [(0, (GX + 0.9, 1.4, 0.6), (GX, 0, 0.15), 32), (DUR + 1, (GX + 1.3, 2.0, 0.9), (GX, 0, 0.15), 32)]),
    ]

def camera(t):
    segs = CAMS(); k = 0
    for i, (st, _) in enumerate(segs):
        if t >= st: k = i
    st, ks = segs[k]
    ks = [(st if a == 0 else a, p, q, l) for a, p, q, l in ks]
    if ks[-1][0] <= t: ks = ks + [(t + 1, ks[-1][1], ks[-1][2], ks[-1][3])]
    pos, tgt, lens = cam_state(t, ks, drift=0.004)
    # en A la cámara sigue un poco al ratón
    if (t < T("le das") - 0.1) or (T("así que") - 0.2 <= t < T("por eso falla")) or t >= T("sígueme"):
        x, y, _ = mouse_xy(t); off = Vector((x - (GX if t >= T("sígueme") else 0), y, 0)) * 0.55
        pos = pos + off; tgt = tgt + off
    if T("por eso falla") <= t < T("es tan liso") - 0.2:
        x, y, _ = mouse_xy(t); off = Vector((x, 0, 0)); pos = pos + off; tgt = tgt + off
    return pos, tgt, lens

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v)
    ms = S["ms"]
    return {"led": Pj(ms.matrix_world @ Vector((0, -0.12, -0.008))), "ledB": Pj(LB + Vector((-2.0, 0.5, 0.58))),
            "lens": Pj(LB + Vector((0, 0.6, 0.85))), "chip": Pj(LB + Vector((0, 0.7, 1.45))), "pel": Pj(LB + Vector((-0.55, 0.45, 0.1))),
            "fib": Pj(LB + Vector((0.15, 0.4, 0.05))), "scr": Pj(LB + Vector((0.8, 0.4, 0.0))),
            "gridN": Pj(LC + Vector((2.0, 0, NG * CS / 2))), "gridO": Pj(LC + Vector((-2.0, 0, NG * CS / 2))), "grid": Pj(LC + Vector((0, 0, -NG * CS / 2))),
            "glass": Pj(LA + Vector((GX, -0.6, 0.03))), "cur": Pj(S["cur"].matrix_world @ Vector((0.1, 0, -0.2))), "glassB": Pj(LB + Vector((1.5, 0, -0.15))),
            "mouse": Pj(ms.matrix_world @ Vector((0, 0, 0.3)))}

if __name__ == "__main__":
    run("raton", build, pose, anchors)
