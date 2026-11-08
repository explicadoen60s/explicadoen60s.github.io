# «¿Qué hay dentro de tu móvil cuando vibra?»: un móvil con una llamada entrante tiembla sobre la mesa (ondas en la
# mesa); la pantalla se levanta y dentro gira el motor. Motor gigante junto a una lenteja (8 mm); una rueda centrada no
# sirve, la pesa de media luna sí: vista desde la punta del eje, la flecha de fuerza gira (arriba, a un lado, abajo) y
# arrastra el motor. Contador hasta 12.000 vueltas/min y 200 sacudidas/s. Gráfica: el motor tarda en arrancar y frenar.
# Motor lineal: pesa con muelles, imán y bobina; la corriente la empuja a un lado y al otro; altavoz; resonancia (poco
# empuje, mucho movimiento); gráfica con un toque cortísimo; dedo pulsando una tecla; la pesa rebota dentro del móvil.
import bpy, bmesh, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector

T0, DUR = cargar("vibracion")
_TC = {}
def T(k, n=1, fin=False):
    key = (k, n, fin)
    if key not in _TC: _TC[key] = T0(k, n, fin)
    return _TC[key]

BG = (0.06, 0.07, 0.1); TABLE = (0.3, 0.31, 0.36); FRAME = (0.14, 0.15, 0.18); GLASS = (0.05, 0.05, 0.07); CALL = (0.16, 0.22, 0.38)
GREEN = (0.25, 0.85, 0.45); FLOOR = (0.22, 0.23, 0.26); BATT = (0.55, 0.57, 0.62); PCB = (0.12, 0.45, 0.28); CHIPC = (0.1, 0.1, 0.12)
METAL = (0.74, 0.76, 0.8); BRASS = (0.9, 0.7, 0.3); BRASS_L = (0.95, 0.85, 0.6); COPPER = (0.85, 0.45, 0.2); LENTIL = (0.62, 0.5, 0.28)
YL = (1.0, 0.82, 0.16); RED = (0.92, 0.22, 0.2); BLUE = (0.25, 0.5, 0.95); CYAN = (0.25, 0.85, 1.0); ORANGE = (1.0, 0.55, 0.15)
SKIN = (0.93, 0.72, 0.58); WHITE = (0.94, 0.95, 0.97); RING = (0.45, 0.5, 0.62); GREY = (0.35, 0.36, 0.4)
LEJOS = Vector((0, 300, -300))
LA = Vector((0, 0, 0)); LB = Vector((60, 120, 0)); LC = Vector((120, 0, 0)); LD = Vector((180, 0, 0)); LE = Vector((240, 0, 0))
ERM_P = Vector((-2.2, -6.2, 0.75)); LRA_P = Vector((1.9, -6.2, 0.75))
NB = 48

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

def half_disc(r, th, color, parent=None, seg=24):
    """media luna (semicírculo extruido) en el plano YZ, hacia +Z local, eje X"""
    me = bpy.data.meshes.new("hd"); bm = bmesh.new()
    pts = [(r * math.cos(math.pi * k / seg), r * math.sin(math.pi * k / seg)) for k in range(seg + 1)]
    a = [bm.verts.new((-th / 2, y, z)) for y, z in pts]; b = [bm.verts.new((th / 2, y, z)) for y, z in pts]
    bm.faces.new(a); bm.faces.new(list(reversed(b)))
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n; bm.faces.new((a[i], b[i], b[j], a[j]))
    bm.normal_update(); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("hd", me); bpy.context.collection.objects.link(o)
    return setup(o, color, parent)

def finger():
    e = empty(LEJOS)
    sph(0.85, (0, 0, 0.85), SKIN, e, scale=(1, 1.05, 1))
    cyl(0.85, 9, (0, 0, 5.3), SKIN, e)
    sph(0.62, (0, 0.55, 1.4), (0.96, 0.86, 0.82), e, scale=(1, 0.35, 1.25))
    return e

def build():
    sc, cam = scene_setup(world=BG, shadow=0.3); cam.data.clip_start = 0.05
    S = {"cam": cam}; dyn = [cam]
    # ---------- A: móvil sobre la mesa ----------
    box((50, 50, 1), LA + Vector((0, 0, -0.5)), TABLE)
    ph = empty(LA); S["ph"] = ph
    rounded_slab(7.4, 15.4, 1.0, 0.75, (0, 0, 0), FRAME, ph)
    rounded_slab(7.0, 15.0, 0.8, 0.01, (0, 0, 0.75), FLOOR, ph)
    S["inner"] = inner = empty((0, 0, 0), ph)
    box((6.0, 8.2, 0.14), (0, 1.0, 0.83), BATT, inner)
    box((6.4, 2.6, 0.1), (0, 6.0, 0.81), PCB, inner); box((1.4, 1.2, 0.2), (-1.5, 6.0, 0.9), CHIPC, inner)
    cyl(0.7, 0.3, (1.8, 6.2, 0.9), CHIPC, inner); cyl(0.4, 0.32, (1.8, 6.2, 0.95), (0.25, 0.3, 0.45), inner)
    box((6.4, 2.2, 0.1), (0, -4.9, 0.81), PCB, inner); box((1.0, 0.8, 0.16), (0.2, -4.9, 0.9), CHIPC, inner)
    # motor que gira (ERM) en la esquina
    S["ermA"] = erm = empty(ERM_P + Vector((0, 0, 0.32)), ph)
    cyl(0.3, 1.2, (0, 0, 0), METAL, erm, rot=(0, math.pi / 2, 0))
    cyl(0.06, 0.5, (0.75, 0, 0), METAL, erm, rot=(0, math.pi / 2, 0))
    S["ermAw"] = we = empty((0.85, 0, 0), erm); half_disc(0.36, 0.22, BRASS, we)
    # motor lineal (LRA) en la otra esquina, con la tapa abierta
    S["lraA"] = lra = empty(LRA_P + Vector((0, 0, 0.06)), ph)
    box((2.2, 1.1, 0.06), (0, 0, 0), GREY, lra)
    for x in (-1.08, 1.08): box((0.06, 1.1, 0.4), (x, 0, 0.2), GREY, lra)
    for y in (-0.53, 0.53): box((2.2, 0.06, 0.4), (0, y, 0.2), GREY, lra)
    S["lraAm"] = box((0.7, 0.7, 0.3), (0, 0, 0.2), METAL); S["lraAm"].parent = lra
    S["lraAs"] = [bar_obj(WHITE, r=0.025) for _ in range(12)]
    dyn += [S["lraAs"]]
    # pantalla (se levanta)
    S["scr"] = scr = empty(LA)
    rounded_slab(7.2, 15.2, 0.9, 0.12, (0, 0, 0.75), GLASS, scr)
    S["disp"] = rounded_slab(6.8, 14.6, 0.7, 0.006, (0, 0, 0.87), CALL, scr, unique=True)
    S["callui"] = cu = empty((0, 0, 0), scr)
    S["callbtn"] = cyl(0.75, 0.02, (0, -4.6, 0.88), GREEN, cu, unique=True)
    cyl(1.1, 0.02, (0, 3.6, 0.88), (0.5, 0.55, 0.7), cu); box((3.0, 0.3, 0.02), (0, 1.8, 0.88), WHITE, cu)
    S["kbd"] = kb = empty(LEJOS, scr); S["keys"] = []
    box((6.8, 4.6, 0.02), (0, -4.2, 0.88), (0.2, 0.21, 0.25), kb)
    for r_, n in ((0, 10), (1, 9), (2, 7)):
        for c in range(n):
            k = box((0.56, 0.9, 0.04), ((c - (n - 1) / 2) * 0.66, -2.6 - 1.15 * r_, 0.9), WHITE, kb, unique=True); S["keys"].append(k)
    S["ripples"] = [torus(1, 0.05, LEJOS, RING) for _ in range(4)]
    S["fing"] = finger()
    dyn += [ph, scr, S["ripples"], S["fing"]]
    # ---------- B: motor gigante (mm) ----------
    S["mot"] = mot = empty(LB)
    cyl(2.0, 8.0, (0, 0, 0), METAL, mot, rot=(0, math.pi / 2, 0))
    cyl(2.02, 0.5, (-3.9, 0, 0), BRASS, mot, rot=(0, math.pi / 2, 0)); cyl(0.7, 0.4, (4.1, 0, 0), METAL, mot, rot=(0, math.pi / 2, 0))
    cyl(0.35, 1.8, (4.9, 0, 0), METAL, mot, rot=(0, math.pi / 2, 0))
    box((1.2, 0.25, 0.25), (-4.6, 0.6, 0), RED, mot); box((1.2, 0.25, 0.25), (-4.6, -0.6, 0), (0.1, 0.1, 0.1), mot)
    S["wB"] = wb = empty((5.1, 0, 0), mot); half_disc(2.4, 1.3, BRASS, wb)
    S["discB"] = cyl(2.4, 1.3, LEJOS, (0.62, 0.64, 0.68), rot=(0, math.pi / 2, 0))
    S["blurB"] = cyl(2.38, 1.1, LEJOS, BRASS_L, rot=(0, math.pi / 2, 0))
    S["lentil"] = sph(3.0, LEJOS, LENTIL, scale=(1, 1, 0.38))
    S["dim"] = [bar_obj(YL, r=0.12) for _ in range(3)]
    S["force"] = arrow(YL, 0.3)
    S["trail"] = [sph(0.25, LEJOS, YL) for _ in range(10)]
    dyn += [mot, S["discB"], S["blurB"], S["lentil"], S["dim"], S["force"], S["trail"]]
    # ---------- C: gráfica ----------
    box((17, 0.3, 9.5), LC + Vector((0, 0.6, 0.6)), (0.12, 0.13, 0.17))
    box((16, 0.1, 0.12), LC + Vector((0, 0.3, -3.5)), WHITE)
    box((0.12, 0.1, 8), LC + Vector((-8, 0.3, 0.5)), WHITE)
    S["cmd"] = box((1, 0.1, 7.5), LEJOS, (0.2, 0.3, 0.55))
    S["bars"] = [bar_obj(ORANGE, r=0.13, unique=True) for _ in range(NB)]
    dyn += [S["cmd"], S["bars"]]
    # ---------- D: motor lineal gigante ----------
    box((13.4, 0.4, 7.4), LD + Vector((0, 1.3, 0)), (0.2, 0.21, 0.25))
    for z in (-3.5, 3.5): box((13.4, 2.4, 0.4), LD + Vector((0, 0.2, z)), GREY)
    for x in (-6.5, 6.5): box((0.4, 2.4, 7.4), LD + Vector((x, 0.2, 0)), GREY)
    S["mass"] = ms = empty(LD + Vector((0, 0.2, 0)))
    box((3.4, 1.6, 2.4), (0, 0, 0), METAL, ms)
    box((1.55, 0.1, 2.0), (-0.85, -0.82, 0), RED, ms); box((1.55, 0.1, 2.0), (0.85, -0.82, 0), BLUE, ms)
    S["coil"] = [torus(1.75, 0.16, LD + Vector((-0.8 + 0.4 * k, 0.2, 0)), COPPER, rot=(0, math.pi / 2, 0), unique=True) for k in range(5)]
    S["springs"] = [bar_obj(WHITE, r=0.1) for _ in range(20)]
    S["elec"] = [sph(0.16, LEJOS, YL) for _ in range(8)]
    S["push"] = arrow(YL, 0.22)
    dyn += [ms, S["coil"], S["springs"], S["elec"], S["push"]]
    # ---------- E: altavoz ----------
    box((10, 0.4, 10), LE + Vector((0, 1.6, 0)), (0.15, 0.16, 0.2))
    cyl(1.3, 1.0, LE + Vector((0, 1.0, 0)), GREY, rot=(math.pi / 2, 0, 0))
    torus(3.1, 0.2, LE + Vector((0, -0.3, 0)), (0.1, 0.1, 0.12), rot=(math.pi / 2, 0, 0))
    S["spk"] = spk = empty(LE)
    bpy.ops.mesh.primitive_cone_add(radius1=3.0, radius2=0.9, depth=1.3, location=(0, 0, 0), rotation=(-math.pi / 2, 0, 0), vertices=40, end_fill_type='NOTHING')
    o = bpy.context.object; setup(o, (0.18, 0.18, 0.2), spk, True)
    sph(0.95, (0, -0.1, 0), (0.12, 0.12, 0.14), spk, scale=(1, 0.5, 1))
    S["sound"] = [torus(1, 0.08, LEJOS, CYAN) for _ in range(3)]
    dyn += [spk, S["sound"]]
    join_static(dyn)
    return sc, S

# ---------- utilidades de tiempo ----------
def theta(t):
    """ángulo (rad) de la pesa del motor que gira"""
    a = T("cuando el motor"); b1 = T("arriba"); b2 = T("lado", 2); b3 = T("abajo"); b4 = T("una y otra")
    if t < a: return 2 * math.pi * 3 * t
    if t < b3 + 0.2:
        return math.radians(keyed(t, [(a, -90.0), (b1, 90.0), (b2, 180.0), (b3, 270.0), (b3 + 0.2, 280.0)]))
    w = 2 * math.pi * (1.2 + 3 * seg(t, b4, b4 + 1.0))
    return math.radians(280.0) + w * (t - b3 - 0.2)

def spinning(t):
    """¿el motor que gira está en marcha (el móvil vibra)?"""
    return t < T("dentro hay") + 99 and (t < T("pero un motor") or T("por eso suena") <= t < T("pero un motor"))

def phone_buzz(t):
    if t < T("pero un motor") and (t < T("cuánto") or t >= T("por eso suena")): return 1.0
    if T("y el móvil entero") <= t < T("cuánto"): return 1.0
    if T("pero que en") <= t < T("y si la"): return 0.7
    return 0.0

def lra_x(t):
    """posición de la pesa del motor lineal (−1…1)"""
    a = T("la corriente"); b = T("luego hacia el")
    if a <= t < T("como un altavoz"):
        return keyed(t, [(a, 0.0), (a + 0.8, -1.0), (b, -1.0), (b + 0.5, 1.0), (T("como un altavoz") - 0.1, 0.0)])
    if T("y si la") <= t < T("así puede"):
        amp = 0.1 + 0.9 * seg(t, T("y si la") + 0.5, T("muchísimo", fin=True))
        return amp * math.sin(2 * math.pi * 2.2 * (t - T("y si la")))
    if T("así puede") <= t < T("esa sensación"):
        return 0.6 * math.sin(2 * math.pi * 2.5 * t) * math.exp(-4 * ((t - T("cortísimo")) % 1.2))
    if t >= T("es una pesa"):
        return 0.8 * math.sin(2 * math.pi * 3 * t) * math.exp(-2.5 * ((t - T("es una pesa")) % 1.0))
    return 0.0

def pose(t, S):
    # ---------- A ----------
    buzz = phone_buzz(t)
    j = Vector((0.12 * math.sin(t * 97), 0.12 * math.sin(t * 131 + 1), 0)) * buzz
    tap = 0.0
    for tt in (T("como cuando"), T("tecla"), T("esa sensación"), T("no es un")):
        tap = max(tap, math.exp(-((t - tt - 0.15) / 0.06) ** 2))
    j += Vector((0.08 * tap * math.sin(t * 150), 0, 0))
    S["ph"].location = LA + j; S["ph"].rotation_euler = (0, 0, 0.015 * buzz * math.sin(t * 83))
    # pantalla levantada
    lift = 0.0
    if T("dentro hay") <= t < T("y el móvil entero"): lift = seg(t, T("dentro hay"), T("vueltas", fin=True))
    if T("es una pesa") - 0.3 <= t: lift = seg(t, T("es una pesa") - 0.3, T("rebotando", fin=True))
    S["scr"].location = S["ph"].location + Vector((0, 9.0 * lift, 13.0 * lift)); S["scr"].rotation_euler = (-0.9 * lift, 0, S["ph"].rotation_euler.z)
    S["inner"].location = (0, 0, 0) if lift > 0.02 else LEJOS
    modern = t >= T("y aquí viene")
    S["ermA"].location = ERM_P + Vector((0, 0, 0.32)) if (lift > 0.02 and not modern) else LEJOS
    S["lraA"].location = LRA_P + Vector((0, 0, 0.06)) if (lift > 0.02 and modern) else LEJOS
    S["ermAw"].rotation_euler = (theta(t) - math.pi / 2, 0, 0)
    mx = 0.55 * lra_x(t)
    S["lraAm"].location = (mx, 0, 0.2)
    for k, b in enumerate(S["lraAs"]):
        if S["lraA"].location.y < 100:
            base = S["lraA"].matrix_world
            side = 0 if k < 6 else 1; i = k % 6
            x0, x1 = (-1.05, mx - 0.35) if side == 0 else (mx + 0.35, 1.05)
            p0 = base @ Vector((mix(x0, x1, i / 6), (0.2 if i % 2 else -0.2), 0.2)); p1 = base @ Vector((mix(x0, x1, (i + 1) / 6), (-0.2 if i % 2 else 0.2), 0.2))
            bar_set(b, p0, p1)
        else: hide_bar(b)
    keyb = t >= T("así puede") or (T("pero que en") <= t < T("y si la"))
    S["kbd"].location = (0, 0, 0) if keyb else LEJOS
    S["callui"].location = LEJOS if keyb else (0, 0, 0)
    set_color(S["callbtn"], GREEN if (t * 2.5) % 1 < 0.6 else (0.15, 0.6, 0.3))
    for k, o in enumerate(S["keys"]):
        hit = (k == 14 and tap > 0.3) or (k == 23 and T("tecla") <= t < T("tecla") + 0.3)
        set_color(o, (0.55, 0.75, 1.0) if hit else WHITE)
    # anillos en la mesa
    for k, r in enumerate(S["ripples"]):
        if buzz > 0 and lift < 0.02:
            u = ((t * 1.4) + k / 4) % 1.0; R = 8.5 + 6 * u
            r.location = LA + Vector((0, 0, 0.02)); r.scale = (R * 0.62, R, 1)
        else: r.location = LEJOS
    # dedo
    f = S["fing"]
    if T("pero que en") <= t < T("y si la"):
        f.location = S["ph"].location + Vector((1.0, -2.0, 0.9 + 3 * (1 - seg(t, T("pero que en"), T("pero que en") + 0.4))))
        f.rotation_euler = (-0.55, 0.3, 0)
    elif T("como cuando") - 0.4 <= t < T("es una pesa") - 0.3:
        press = max(0.0, tap); f.location = S["ph"].location + Vector((0.0, -3.75, 0.92 + 0.9 * (1 - press)))
        f.rotation_euler = (-0.55, 0.3, 0)
    else: f.location = LEJOS
    # ---------- B ----------
    th = theta(t)
    d = Vector((0, math.cos(th), math.sin(th)))
    shake = 0.0
    if T("cuando el motor") <= t < T("pero un motor"): shake = 0.35
    S["mot"].location = LB + d * shake
    S["wB"].rotation_euler = (th - math.pi / 2, 0, 0)
    wpos = S["mot"].location + Vector((5.1, 0, 0))
    centered = T("pero su eje") <= t < T("lleva una pesa")
    S["discB"].location = wpos if centered else LEJOS
    if centered: S["wB"].scale = (0.001, 0.001, 0.001)
    else: S["wB"].scale = (1, 1, 1) if t < T("lleva una pesa") + 0.01 else (seg(t, T("lleva una pesa"), T("pesa") + 0.4),) * 3
    if t < T("pero su eje"): S["wB"].scale = (1, 1, 1)
    fast = T("cuánto") <= t < T("por eso suena")
    S["blurB"].location = wpos + Vector((-0.02, 0, 0)) if fast and t > T("hasta doce") else LEJOS
    S["lentil"].location = LB + Vector((0.5, 0, -6.0)) if T("en muchos") <= t < T("pero su eje") else LEJOS
    if T("ocho") <= t < T("pero su eje"):
        u = seg(t, T("ocho"), T("milímetros", fin=True)); z = 3.0
        bar_set(S["dim"][0], LB + Vector((-4 * u, -2.2, z)), LB + Vector((4 * u + 0.001, -2.2, z)))
        bar_set(S["dim"][1], LB + Vector((-4, -2.2, z - 0.6)), LB + Vector((-4, -2.2, z + 0.6)))
        bar_set(S["dim"][2], LB + Vector((4, -2.2, z - 0.6)), LB + Vector((4, -2.2, z + 0.6)))
    else:
        for b in S["dim"]: hide_bar(b)
    if T("cuando el motor") <= t < T("cuánto"):
        c = LB + Vector((6.2, 0, 0)) + d * shake
        put_arrow(S["force"], c, c + d * 5.0)
        for k, s in enumerate(S["trail"]):
            th2 = th - 0.18 * (k + 1); s.location = LB + Vector((6.2, math.cos(th2) * 4.6, math.sin(th2) * 4.6)); s.scale = (1 - k / 11,) * 3
    else:
        hide_arrow(S["force"])
        for s in S["trail"]: s.location = LEJOS
    # ---------- C: gráfica ----------
    g1 = T("pero un motor") <= t < T("y aquí viene")
    g2 = T("así puede") <= t < T("como cuando")
    if g1 or g2:
        a0 = T("pero un motor") if g1 else T("así puede"); a1 = T("seco", fin=True) if g1 else T("cortísimo", fin=True)
        rev = seg(t, a0 + 0.2, a1)
        S["cmd"].location = LC + Vector((-8 + 16 * 0.2, 0.42, 0.25)); S["cmd"].scale = (16 * 0.2, 0.1, 7.5)
        for k, b in enumerate(S["bars"]):
            u = (k + 0.5) / NB
            if g1: h = seg(u, 0.1, 0.55) * (1 - seg(u, 0.55, 0.97))
            else: h = seg(u, 0.1, 0.14) * (1 - seg(u, 0.27, 0.32))
            x = LC.x - 8 + 16 * u
            if u <= rev and h > 0.01:
                bar_set(b, Vector((x, 0.2, -3.45)), Vector((x, 0.2, -3.45 + 7.0 * h)))
            else: hide_bar(b)
            set_color(b, ORANGE if g1 else CYAN)
    else:
        S["cmd"].location = LEJOS
        for b in S["bars"]: hide_bar(b)
    # ---------- D: motor lineal ----------
    xm = 1.3 * lra_x(t); S["mass"].location = LD + Vector((xm, 0.2, 0))
    for k, b in enumerate(S["springs"]):
        side = 0 if k < 10 else 1; i = k % 10
        x0, x1 = (-6.3, xm - 1.7) if side == 0 else (xm + 1.7, 6.3)
        p0 = LD + Vector((mix(x0, x1, i / 10), 0.2, 0.7 if i % 2 else -0.7)); p1 = LD + Vector((mix(x0, x1, (i + 1) / 10), 0.2, -0.7 if i % 2 else 0.7))
        if i == 0: p0.z = 0
        if i == 9: p1.z = 0
        bar_set(b, p0, p1)
    cur = 0.0
    if T("la corriente") <= t < T("como un altavoz"): cur = -1.0 if t < T("luego hacia el") else 1.0
    elif T("y si la") <= t < T("así puede"): cur = 1.0 if math.cos(2 * math.pi * 2.2 * (t - T("y si la"))) > 0 else -1.0
    show_coil = t >= T("y una bobina")
    for k, c in enumerate(S["coil"]):
        c.location = LD + Vector((-0.8 + 0.4 * k, 0.2, 0)) if show_coil else LEJOS
        set_color(c, ORANGE if cur > 0 else (BLUE if cur < 0 else COPPER))
    for k, e in enumerate(S["elec"]):
        if cur != 0:
            a = 2 * math.pi * k / 8 + cur * t * 5; e.location = LD + Vector((0.8, 0.2 + 1.75 * math.cos(a), 1.75 * math.sin(a)))
        else: e.location = LEJOS
    vel = 0.0
    if T("la corriente") <= t < T("como un altavoz"): vel = cur
    elif T("y si la") <= t < T("así puede"): vel = 0.35 * cur
    if vel != 0:
        c = LD + Vector((xm, -1.2, 2.2)); put_arrow(S["push"], c, c + Vector((2.6 * vel, 0, 0)))
    else: hide_arrow(S["push"])
    # ---------- E: altavoz ----------
    S["spk"].location = LE + Vector((0, 0.35 * math.sin(t * 40), 0))
    for k, r in enumerate(S["sound"]):
        if T("como un altavoz") <= t < T("pero que en"):
            u = (t * 1.6 + k / 3) % 1.0; r.location = LE + Vector((0, -1.0 - 4 * u, 0)); s = 3.2 + 2.5 * u; r.scale = (s, s, s); r.rotation_euler = (math.pi / 2, 0, 0)
        else: r.location = LEJOS
    apply_cam(S["cam"], *camera(t))

def CAMS():
    B, C, D, E = LB, LC, LD, LE
    E1, L1 = ERM_P, LRA_P
    return [
        (0.0, [(0, (6.0, -12.5, 6.0), (0, -1.0, 0.6), 35), (T("dentro hay"), (5.0, -13.0, 8.0), (0, -0.5, 0.5), 35),
               (T("mira por dentro"), (2.0, -10.0, 12.0), (0, -1.5, 0.5), 35), (T("en muchos") - 0.01, (E1.x + 1.2, E1.y - 3.6, 3.0), (E1.x, E1.y, 1.0), 35)]),
        (T("en muchos"), [(0, (B.x + 1.5, B.y - 31, -1.5), (B.x + 1.0, B.y, -2.2), 35), (T("ocho"), (B.x + 1.0, B.y - 29, -0.5), (B.x + 0.5, B.y, -1.0), 35)]),
        (T("pero su eje"), [(0, (B.x + 16, B.y - 15, 6), (B.x + 3.5, B.y, 0), 35), (T("toda hacia"), (B.x + 15, B.y - 12, 4), (B.x + 4.0, B.y, 0), 35)]),
        (T("cuando el motor"), [(0, (B.x + 27, B.y + 0.01, 0.4), (B.x + 5, B.y, 0), 35), (T("una y otra"), (B.x + 27, B.y + 0.01, 0.4), (B.x + 5, B.y, 0), 35)]),
        (T("y el móvil entero"), [(0, (6.5, -13.0, 6.5), (0, -1.0, 0.6), 35)]),
        (T("cuánto"), [(0, (B.x + 18, B.y - 16, 7), (B.x + 3.0, B.y, 0), 35), (T("doscientas"), (B.x + 14, B.y - 13, 4), (B.x + 3.5, B.y, 0), 35)]),
        (T("por eso suena"), [(0, (0.0, -15.0, 9.0), (0, -1.0, 0.0), 35)]),
        (T("pero un motor"), [(0, (C.x, C.y - 32, 0.6), (C.x, 0, 0.0), 35), (T("y aquí viene"), (C.x + 0.5, C.y - 31, 0.6), (C.x, 0, 0.0), 35)]),
        (T("y aquí viene"), [(0, (D.x + 6, D.y - 26, 7), (D.x, 0, 0), 35), (T("tienen una"), (D.x + 2, D.y - 24, 3), (D.x, 0, 0), 35),
                              (T("la corriente"), (D.x, D.y - 25, 1.0), (D.x, 0, -0.2), 35)]),
        (T("como un altavoz"), [(0, (E.x + 4, E.y - 17, 3), (E.x, 0, 0), 35)]),
        (T("pero que en"), [(0, (6.0, -13.0, 8.0), (0.3, -1.5, 0.8), 35)]),
        (T("y si la"), [(0, (D.x - 2, D.y - 25, 2.0), (D.x, 0, -0.2), 35), (T("muchísimo"), (D.x + 1, D.y - 24, 1.0), (D.x, 0, -0.2), 35)]),
        (T("así puede"), [(0, (C.x, C.y - 32, 0.6), (C.x, 0, 0.0), 35)]),
        (T("como cuando"), [(0, (3.0, -10.5, 10.0), (0, -3.0, 0.8), 35), (T("no es un"), (2.0, -11.0, 9.0), (0, -3.0, 0.8), 35)]),
        (T("es una pesa") - 0.3, [(0, (L1.x + 1.5, L1.y - 4.5, 4.5), (L1.x, L1.y, 1.0), 35), (T("sígueme"), (L1.x + 1.2, L1.y - 4.0, 4.0), (L1.x, L1.y, 0.9), 35),
                                   (DUR + 1, (4.0, -16.0, 10.0), (0, -2.0, 0.5), 35)]),
    ]

def camera(t):
    segs = CAMS(); k = 0
    for i, (st, _) in enumerate(segs):
        if t >= st: k = i
    st, ks = segs[k]
    ks = [(st if a == 0 else a, p, q, l) for a, p, q, l in ks]
    if ks[-1][0] <= t: ks = ks + [(t + 1, ks[-1][1], ks[-1][2], ks[-1][3])]
    return cam_state(t, ks, drift=0.01)

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v)
    return {"erm": Pj(ERM_P + Vector((0, 0, 0.4))), "lra": Pj(LRA_P + Vector((0, 0, 0.3))), "motor": Pj(LB + Vector((0, 0, 2.2))),
            "lentil": Pj(LB + Vector((0.5, 0, -6.0))), "weight": Pj(S["mot"].location + Vector((5.1, 0, 2.5))), "spring": Pj(LD + Vector((-4.5, 0, 0))),
            "magnet": Pj(S["mass"].location + Vector((0, -0.9, -1.2))), "coil": Pj(LD + Vector((0, 0.2, 1.9))), "mass": Pj(S["mass"].location),
            "g_start": Pj(LC + Vector((-8 + 16 * 0.3, 0, 2.0))), "g_end": Pj(LC + Vector((-8 + 16 * 0.8, 0, 0.5))), "g_cmd": Pj(LC + Vector((-8 + 16 * 0.2, 0, 4.2))),
            "spk": Pj(LE + Vector((0, 0, 3.4))), "phone": Pj(S["ph"].location + Vector((0, 0, 1)))}

if __name__ == "__main__":
    run("vibracion", build, pose, anchors)
