# «¿Y si tuvieras que fabricar la nieve?»: primer plano de un cañón disparando nieve hacia la cámara; la ladera sin nevar y la
# pista que se pone blanca. Luego, en corte: balsa arriba que se llena en verano (lluvia y río), tubería enterrada que baja por
# la pista y sube por cada hidrante hasta su cañón, agua a chorro que cae como lluvia y hace hielo, gotas finísimas, la boquilla
# por dentro (agua + aire a presión, manómetro), el aire que se expande y se enfría, núcleos de hielo y gotas que se congelan
# al caer, el chorro según el aire esté húmedo o seco, la noche de madrugada, decenas de cañones y la pisapistas que aplana.
import bpy, bmesh, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("nieve")
SKY = (0.13, 0.17, 0.27); SKY_DAY = (0.42, 0.6, 0.78); SKY_NIGHT = (0.03, 0.04, 0.09)
SOIL = (0.36, 0.28, 0.22); SOIL2 = (0.29, 0.22, 0.18); TURF = (0.42, 0.45, 0.28); ROCK = (0.42, 0.4, 0.4); PEAK = (0.36, 0.35, 0.37)
SNOW = (0.96, 0.97, 1.0); WATER = (0.2, 0.5, 0.9); ICE = (0.65, 0.85, 0.98); YEL = (1.0, 0.78, 0.12); PIPE = (0.25, 0.45, 0.75)
AIRC = (0.92, 0.93, 0.96); DARK = (0.18, 0.19, 0.22); PINE = (0.12, 0.3, 0.2); RED = (0.85, 0.22, 0.2)
LEJOS = (0, 0, -500)
YF = -6.0                       # plano del corte
HX = (-22.0, 0.0, 22.0)         # hidrantes / cañones de la pista
YC = YF + 1.6                   # y de los cañones
DN = Vector((13.0, -17.0, 33.0))  # boquilla ampliada
EL = math.radians(24)
RNG = random.Random(3)

def surf(x):
    if x < -36: return 40.0
    if x > 60: return 0.0
    s = (x + 36) / 96
    return 40 * (1 - s) - 3.5 * math.sin(math.pi * s) + 0.5 * math.sin(x * 0.3)

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

def hide_bar(o): bar_set(o, LEJOS, Vector(LEJOS) + Vector((0, 0, 0.01)))

LX = [float(x) for x in range(-36, 61, 2)]
def layer_obj(color):
    """capa de nieve sobre la pista: tira que sigue la ladera (vértices que se mueven cada fotograma)"""
    me = bpy.data.meshes.new("ly"); bm = bmesh.new(); V = []
    for x in LX:
        z = surf(x); V.append([bm.verts.new((x, y, z + dz)) for y, dz in ((YF, 0), (6, 0), (6, 0.1), (YF, 0.1))])
    for a, b in zip(V, V[1:]):
        for i in range(4):
            j = (i + 1) % 4; bm.faces.new((a[i], b[i], b[j], a[j]))
    bm.faces.new(V[0]); bm.faces.new(list(reversed(V[-1])))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("ly", me); bpy.context.collection.objects.link(o)
    return setup(o, color, unique=True)

def layer_set(o, hfun, y1):
    vs = o.data.vertices
    for i, x in enumerate(LX):
        z = surf(x) - 0.05; h = max(0.0, hfun(x))
        for k, (y, top) in enumerate(((YF - 0.02, 0), (y1, 0), (y1, 1), (YF - 0.02, 1))):
            vs[4 * i + k].co = (x, y, z + (h if top else 0))
    o.data.update()

def cannon(loc, scale=1.0, parent=None):
    e = empty(loc, parent=parent); e.scale = (scale,) * 3
    box((1.8, 1.4, 0.25), (0, 0, 0.15), DARK, parent=e)
    for dy in (-0.6, 0.6): cyl(0.3, 0.2, (-0.6, dy, 0.3), (0.1, 0.1, 0.1), parent=e, rot=(math.pi / 2, 0, 0), v=12)
    cyl(0.12, 1.6, (0, 0, 1.0), (0.6, 0.62, 0.66), parent=e, v=12)
    b = empty((0, 0, 1.8), parent=e); b.rotation_euler = (0, -EL, 0)
    cyl(0.95, 2.4, (0, 0, 0), YEL, parent=b, rot=(0, math.pi / 2, 0))
    torus(0.95, 0.12, (1.2, 0, 0), DARK, parent=b, rot=(0, math.pi / 2, 0))
    torus(0.95, 0.1, (-1.2, 0, 0), DARK, parent=b, rot=(0, math.pi / 2, 0))
    for k in range(10):
        a = k * math.tau / 10; cyl(0.07, 0.25, (1.28, 0.95 * math.cos(a), 0.95 * math.sin(a)), (0.75, 0.77, 0.8), parent=b, rot=(0, math.pi / 2, 0), v=8)
    asp = empty((-1.0, 0, 0), parent=b)
    for k in range(3): box((0.06, 1.6, 0.35), (0, 0, 0), (0.3, 0.32, 0.36), parent=asp, rot=(k * math.pi / 3, 0, 0))
    return e, asp

def mouth(c):
    return Vector(c) + Vector((1.25 * math.cos(EL), 0, 1.8 + 1.25 * math.sin(EL)))

DIR = Vector((math.cos(EL), 0, math.sin(EL)))
def plume(M, k, N, t, speed=9.0, life=1.6, spread=0.18, g=6.0, rate=0.9, seed=0, d=DIR):
    rr = random.Random(k * 7 + seed)
    sv = Vector((rr.uniform(-1, 1), rr.uniform(-1, 1), rr.uniform(-1, 1))) * spread * speed
    u = (t * rate + k / N + rr.random() * 0.03) % 1; s = u * life
    p = M + (d * speed + sv) * s + Vector((0, 0, -0.5 * g * s * s))
    return p, u

GRID = [(x, y) for x in (-30, -12, 8, 28, 46) for y in (14, 28, 42) ] + [(x, y) for x in (-28, -6, 16, 38) for y in (56,)]
MOUNDS = [(x + 9, 0.0) for x in HX]

def build():
    sc, cam = scene_setup(world=SKY, shadow=0.35, light_rot=-30)
    S = {"cam": cam}
    prof = [(x, surf(x)) for x in [-90.0] + [float(v) for v in range(-80, 91, 2)]]
    prism([(-90, -40)] + [(x, z - 0.6) for x, z in prof] + [(90, -40)], YF, 90, SOIL)
    prism([(x, z - 0.6) for x, z in prof] + [(x, z) for x, z in reversed(prof)], YF, 90, TURF)
    for k in range(70):
        x = RNG.uniform(-88, 88); z = RNG.uniform(-38, surf(x) - 2.5)
        box((RNG.uniform(1.2, 3), 0.05, RNG.uniform(0.3, 0.6)), (x, YF - 0.02, z), SOIL2, rot=(0, RNG.uniform(-0.4, 0.4), 0))
    for k in range(18): sph(RNG.uniform(0.6, 1.6), (RNG.uniform(-88, 88), YF - 0.05, RNG.uniform(-38, -4)), ROCK, scale=(1.4, 0.1, 1), seg=10)
    for x, y, r, h in ((-70, 120, 60, 95), (10, 150, 70, 80), (80, 110, 50, 60), (-20, 95, 35, 70), (60, 160, 60, 100)):
        bpy.ops.mesh.primitive_cone_add(radius1=r, radius2=0, depth=h, location=(x, y, h / 2 - 5), vertices=7); setup(bpy.context.object, PEAK)
    for k in range(40):
        x = RNG.uniform(-60, 80); y = RNG.choice([RNG.uniform(8, 12), RNG.uniform(20, 26), RNG.uniform(34, 40), RNG.uniform(48, 85)])
        z = surf(x); h = RNG.uniform(3, 5.5)
        bpy.ops.mesh.primitive_cone_add(radius1=h * 0.3, radius2=0, depth=h, location=(x, y, z + h / 2 + 0.6), vertices=8); setup(bpy.context.object, PINE)
    # balsa: diques, lámina y agua
    for x0, x1 in ((-64, -60), (-42, -38)):
        prism([(x0, 39.9), (x1, 39.9), ((x0 + x1) / 2 + 0.6, 44.2), ((x0 + x1) / 2 - 0.6, 44.2)], YF, 16, (0.5, 0.47, 0.42))
    box((24, 3, 4.3), (-51, 15.5, 42), (0.5, 0.47, 0.42))
    box((21, 21.4, 0.2), (-51, 4.7, 40.05), (0.15, 0.15, 0.17))
    S["balsa"] = box((1, 1, 1), LEJOS, WATER, unique=True); alpha(S["balsa"], 0.82)
    S["lluvia"] = [bar_obj((0.55, 0.75, 1.0), 0.08) for _ in range(40)]
    S["nubes"] = empty(LEJOS)
    for k in range(6): sph(RNG.uniform(4, 6), (RNG.uniform(-10, 10), RNG.uniform(-3, 6), RNG.uniform(-1, 1)), (0.55, 0.58, 0.64), parent=S["nubes"], scale=(1.4, 1, 0.6), seg=16)
    S["rio"] = bar_obj(WATER, 0.9, unique=True)
    S["rio_p"] = [sph(0.35, LEJOS, (0.7, 0.85, 1.0), seg=8) for _ in range(14)]
    S["sol"] = sph(9, (-20, 200, 95), (1.0, 0.85, 0.35), unique=True)
    S["luna"] = sph(5, (40, 200, 90), (0.92, 0.94, 1.0), unique=True)
    S["estrellas"] = [sph(0.5, (RNG.uniform(-150, 150), 240, RNG.uniform(60, 190)), (1, 1, 1), seg=6) for _ in range(40)]
    # tubería enterrada (en el corte) y hidrantes
    PP = [(-48, 39.0)] + [(float(x), surf(x) - 2.2) for x in range(-36, 41, 4)]
    S["tubo_pts"] = [Vector((x, YF, z)) for x, z in PP]
    S["tubo"] = []
    for (xa, za), (xb, zb) in zip(PP, PP[1:]):
        o = bar_obj(PIPE, 0.45, unique=False); bar_set(o, (xa, YF, za), (xb, YF, zb)); S["tubo"].append(o)
    S["risers"] = []
    for x in HX:
        o = bar_obj(PIPE, 0.35); bar_set(o, (x, YF, surf(x) - 2.2), (x, YF, surf(x) + 0.8)); S["risers"].append(o)
        o2 = bar_obj(DARK, 0.15); bar_set(o2, (x, YF, surf(x) + 0.8), (x, YC, surf(x) + 0.5)); S["risers"].append(o2)
    S["flujo"] = [sph(0.28, LEJOS, (0.6, 0.85, 1.0), seg=8) for _ in range(40)]
    # cañones de la pista
    S["can"] = []; S["aspas"] = []
    for x in HX:
        e, a = cannon((x, YC, surf(x))); S["can"].append(e); S["aspas"].append(a)
    S["snowp"] = [sph(0.12, LEJOS, SNOW, seg=8) for _ in range(150)]
    S["drop"] = [sph(0.28, LEJOS, WATER, seg=10) for _ in range(40)]
    S["mist"] = [sph(0.1, LEJOS, (0.75, 0.88, 1.0), seg=6) for _ in range(120)]
    S["vapor"] = [sph(0.25, LEJOS, (0.85, 0.9, 0.95), seg=8) for _ in range(24)]
    for o in S["vapor"]: o.active_material = S["vapor"][0].active_material
    alpha(S["vapor"][0], 0.45)
    S["hielo"] = box((1, 1, 1), LEJOS, ICE, unique=True)
    S["capa"] = layer_obj(SNOW)
    S["mont"] = [sph(1, LEJOS, SNOW, seg=16, unique=False) for _ in MOUNDS]
    # muchos cañones (centenar)
    S["grid"] = []; S["gridp"] = []
    for x, y in GRID:
        e, a = cannon((x, y, surf(x)), 1.2); S["grid"].append(e)
    S["gridp"] = [sph(0.2, LEJOS, SNOW, seg=6) for _ in range(len(GRID) * 6)]
    # pisapistas
    S["pisa"] = empty(LEJOS); p = S["pisa"]
    box((4.2, 3.0, 1.4), (0, 0, 1.4), RED, parent=p); box((2.0, 2.6, 1.4), (0.4, 0, 2.6), (0.25, 0.3, 0.4), parent=p)
    box((1.9, 2.5, 0.15), (0.4, 0, 3.35), RED, parent=p)
    for dy in (-1.3, 1.3):
        box((5.0, 0.9, 1.0), (0, dy, 0.5), (0.12, 0.12, 0.13), parent=p)
        for k in range(6): cyl(0.35, 0.95, (-2.0 + 0.8 * k, dy, 0.5), (0.4, 0.4, 0.42), parent=p, rot=(math.pi / 2, 0, 0), v=12)
    box((0.3, 4.2, 1.2), (3.1, 0, 0.6), (0.85, 0.85, 0.88), parent=p)
    box((1.4, 3.6, 0.7), (-3.0, 0, 0.5), (0.3, 0.32, 0.36), parent=p)
    box((0.2, 0.25, 0.25), (2.0, -1.0, 2.1), (1.0, 0.95, 0.6), parent=p); box((0.2, 0.25, 0.25), (2.0, 1.0, 2.1), (1.0, 0.95, 0.6), parent=p)
    S["pana"] = [box((1.95, 0.12, 0.06), LEJOS, (0.82, 0.85, 0.92)) for _ in range(2 * 20)]
    S["monton"] = sph(1, LEJOS, SNOW, seg=16, unique=False)
    # boquilla ampliada
    S["det"] = empty(DN); d = S["det"]
    box((9.5, 0.4, 5.6), (0, 0.6, 0), (0.22, 0.24, 0.28), parent=d)
    o = bar_obj(PIPE, 0.42, parent=d); bar_set(o, (-4.6, 0, -1.4), (0.4, 0, -0.35))
    o = bar_obj((0.75, 0.77, 0.82), 0.42, parent=d); bar_set(o, (-4.6, 0, 1.4), (0.4, 0, 0.35))
    sph(0.85, (0.8, 0, 0), (0.55, 0.57, 0.62), parent=d, seg=20)
    bpy.ops.mesh.primitive_cone_add(radius1=0.75, radius2=0.25, depth=1.4, location=(2.1, 0, 0), rotation=(0, math.pi / 2, 0), vertices=24)
    setup(bpy.context.object, (0.55, 0.57, 0.62), parent=d)
    o = bar_obj((0.4, 0.42, 0.46), 0.1, parent=d); bar_set(o, (-2.8, 0, 1.4), (-2.8, 0, 2.0))
    cyl(0.75, 0.25, (-2.8, -0.2, 2.6), (0.95, 0.95, 0.95), parent=d, rot=(math.pi / 2, 0, 0))
    torus(0.75, 0.08, (-2.8, -0.3, 2.6), DARK, parent=d, rot=(math.pi / 2, 0, 0))
    S["aguja"] = empty((-2.8, -0.38, 2.6), parent=d)
    box((0.08, 0.05, 0.6), (0, 0, 0.27), RED, parent=S["aguja"])
    S["dagua"] = [sph(0.17, LEJOS, (0.45, 0.75, 1.0), seg=8) for _ in range(14)]
    S["daire"] = [sph(0.14, LEJOS, (1, 1, 1), seg=8) for _ in range(14)]
    S["dspray"] = [sph(0.09, LEJOS, (0.5, 0.78, 1.0), seg=6) for _ in range(40)]
    S["puff"] = [sph(1.0, LEJOS, (0.9, 0.93, 0.97), seg=12) for _ in range(10)]
    for o in S["puff"]: o.active_material = S["puff"][0].active_material
    alpha(S["puff"][0], 0.3)
    S["nucleo"] = []
    for _ in range(18):
        bpy.ops.mesh.primitive_ico_sphere_add(radius=0.11, subdivisions=1, location=LEJOS); S["nucleo"].append(setup(bpy.context.object, (1, 1, 1)))
    S["gcae"] = [sph(0.2, LEJOS, WATER, seg=10, unique=True) for _ in range(10)]
    S["gota"] = sph(0.42, LEJOS, WATER, seg=16, unique=True)
    dyn = [cam, S["balsa"], S["lluvia"], S["nubes"], S["rio"], S["rio_p"], S["sol"], S["luna"], S["estrellas"], S["tubo"], S["risers"],
           S["flujo"], S["can"], S["snowp"], S["drop"], S["mist"], S["vapor"], S["hielo"], S["capa"], S["mont"], S["grid"], S["gridp"],
           S["pisa"], S["pana"], S["monton"], S["det"], S["dagua"], S["daire"], S["dspray"], S["puff"], S["nucleo"], S["gcae"], S["gota"]]
    join_static(dyn)
    return sc, S

# --------------------------------------------------------------------------------------------------
def GX(t): return mix(-24, 34, seg(t, T("y luego") + 0.2, T("invierno", fin=True) + 0.6))

def snow_mode(t):
    """qué sale del cañón principal: 'nieve', 'agua' (chorro), 'niebla' (gotas finas) o None"""
    if t < T("y si tuvieras") + 0.4: return "nieve"
    if T("pero si lanzas") + 0.2 < t < T("así que la rompes"): return "agua"
    if T("así que la rompes") <= t < T("en el cañón") + 0.3: return "niebla"
    if T("pero no vale") <= t < T("si el aire") + 0.2: return "nieve"
    if T("si el aire") + 0.2 <= t < T("si está muy seco"): return "agua" if t < T("bajo cero") else "nieve"
    if T("si está muy seco") <= t < T("una gran"): return "nieve"
    if T("una gran") <= t < DUR + 1: return "nieve"
    return None

def pose(t, S):
    world = bpy.context.scene.world
    t_res, t_prim, t_balsa, t_llen, t_lluv, t_rio, t_deb, t_tub, t_suben, t_canon = (T("vamos a hacerla"), T("primero"), T("así que haces"),
        T("y la llenas"), T("con agua de"), T("río"), T("debajo"), T("tuberías"), T("que suben"), T("cada cañón"))
    t_lanza, t_cong, t_romp, t_encan, t_aire, t_cur, t_sal, t_exp, t_enfr, t_crea, t_peg, t_cong2 = (T("pero si lanzas"), T("y se congela"),
        T("así que la rompes"), T("en el cañón"), T("aire a presión"), T("y aquí"), T("al salir"), T("se expande"), T("se enfría"),
        T("así crea"), T("las gotas se"), T("se congelan"))
    t_vale, t_hum, t_seco, t_evap, t_roba, t_cero, t_poreso, t_madr, t_gran, t_cent, t_luego, t_maq, t_aplas, t_inv = (T("pero no vale"),
        T("si el aire"), T("si está muy seco"), T("se evapora"), T("roba calor"), T("cero grados"), T("por eso"), T("madrugada"),
        T("una gran"), T("centenar"), T("y luego"), T("unas máquinas"), T("aplastan"), T("invierno"))
    # cielo: verano de día al llenar la balsa; madrugada de noche
    day = win01(t, t_llen - 0.3, t_deb + 0.2, 0.6, 0.6)
    night = win01(t, t_poreso, t_gran + 1.0, 0.8, 1.0)
    c = tuple(mix(mix(a, b, day), n, night) for a, b, n in zip(SKY, SKY_DAY, SKY_NIGHT))
    world.color = lin(c)
    S["sol"].hide_render = day < 0.3; S["luna"].hide_render = night < 0.3
    for o in S["estrellas"]: o.hide_render = night < 0.4
    # balsa
    built = t < t_res + 0.2
    lvl = (1.0 - seg(t, t_res - 0.6, t_res + 0.4)) if t < t_prim else seg(t, t_llen, t_rio + 0.7) * 0.92
    if lvl > 0.01:
        h = 3.6 * lvl; S["balsa"].location = (-51, 4.9, 40.15 + h / 2); S["balsa"].scale = (21.0 - 2 * 0, 21.4, h)
        if lvl < 0.99 or True: S["balsa"].scale = (mix(20, 22.5, lvl), 21.2, h)
    else: S["balsa"].location = LEJOS
    rain = t_lluv - 0.2 < t < t_deb + 0.3
    S["nubes"].location = (-51, 6, 56) if rain else LEJOS; show(S["nubes"], rain)
    for k, o in enumerate(S["lluvia"]):
        if rain:
            rr = random.Random(k); x = -51 + rr.uniform(-10, 10); y = rr.uniform(-4, 14); u = (t * 1.6 + k / 40) % 1; z = mix(54, 41, u)
            bar_set(o, (x, y, z), (x - 0.3, y, z - 1.5))
        else: hide_bar(o)
    riv = t_rio - 0.3 < t < t_deb + 0.6
    if riv: bar_set(S["rio"], (-80, 20, 52), (-80 + 18 * seg(t, t_rio - 0.3, t_rio + 0.5), 8, 52 - 9 * seg(t, t_rio - 0.3, t_rio + 0.5)))
    else: hide_bar(S["rio"])
    for k, o in enumerate(S["rio_p"]):
        if riv and t > t_rio + 0.4: u = (t * 1.2 + k / 14) % 1; o.location = Vector((-80, 20, 53)).lerp(Vector((-62, 8, 44)), u)
        else: o.location = LEJOS
    # tubería, flujo, hidrantes
    tub = built or t > t_deb + 0.3
    tu = 1.0 if built else seg(t, t_deb + 0.3, t_tub + 0.5)
    P = S["tubo_pts"]; n = len(P) - 1
    for i, o in enumerate(S["tubo"]):
        a, b = P[i], P[i + 1]; f = max(0.0, min(1.0, tu * n - i))
        if tub and f > 0.01: bar_set(o, a, a.lerp(b, f))
        else: hide_bar(o)
    ris = built or t > t_suben - 0.2
    for k, o in enumerate(S["risers"]):
        x = HX[k // 2]; u = 1.0 if built else seg(t, t_suben - 0.2 + 0.15 * (k // 2), t_suben + 0.4 + 0.15 * (k // 2))
        if ris and u > 0.01:
            if k % 2 == 0: bar_set(o, (x, YF, surf(x) - 2.2), (x, YF, surf(x) - 2.2 + 3.0 * u))
            else: bar_set(o, (x, YF, surf(x) + 0.8), Vector((x, YF, surf(x) + 0.8)).lerp(Vector((x, YC, surf(x) + 0.5)), u))
        else: hide_bar(o)
    fl = t_suben - 0.3 < t < t_lanza + 0.5
    for k, o in enumerate(S["flujo"]):
        if not fl: o.location = LEJOS; continue
        if k < 28:
            u = (t * 0.35 + k / 28) % 1; L = len(P) - 1; s = u * L; i = min(int(s), L - 1); p = P[i].lerp(P[i + 1], s - i)
            o.location = p + Vector((0, -0.45, 0))
        else:
            j = (k - 28) % 3; x = HX[j]; u = (t * 1.0 + (k - 28) / 12) % 1
            o.location = (x, YF - 0.35, surf(x) - 2.2 + 3.0 * u)
    # cañones
    for k, (e, a) in enumerate(zip(S["can"], S["aspas"])):
        x = HX[k]
        if built: u = 1 - seg(t, t_res - 0.6, t_res + 0.3)
        else: u = seg(t, t_canon - 0.6 + 0.2 * k, t_canon + 0.0 + 0.2 * k)
        e.location = (x, YC, surf(x)); e.scale = (max(u, 0.001),) * 3; show(e, u > 0.01)
        a.rotation_euler = (t * 25, 0, 0)
    # cañón principal (x=0): nieve, agua, niebla
    mode = snow_mode(t); M = mouth((0.0, YC, surf(0.0)))
    side = [(-22.0, YC, surf(-22.0)), (22.0, YC, surf(22.0))]
    for k, o in enumerate(S["snowp"]):
        if mode == "nieve" and (k < 90 or t < t_res or t > t_gran):
            if k < 90: p, u = plume(M, k, 90, t, speed=10, life=1.9, g=5.0, spread=0.16)
            else:
                c = side[k % 2]; p, u = plume(mouth(c), k, 60, t, speed=10, life=1.9, g=5.0, spread=0.16, seed=5)
            if p.z < surf(p.x) + 0.2: p.z = surf(p.x) + 0.2
            o.location = p
            if t_hum < t < t_seco + 2 and t_cong2 < t: o.location = p
        else: o.location = LEJOS
    for k, o in enumerate(S["drop"]):
        if mode == "agua":
            p, u = plume(M, k, 40, t, speed=9, life=1.7, g=9.0, spread=0.05, rate=1.1)
            if p.z < surf(p.x) + 0.3: o.location = LEJOS
            else: o.location = p
        else: o.location = LEJOS
    for k, o in enumerate(S["mist"]):
        if mode == "niebla":
            p, u = plume(M, k, 120, t, speed=10, life=1.9, g=4.0, spread=0.2)
            o.location = p if p.z > surf(p.x) + 0.2 else LEJOS
        else: o.location = LEJOS
    vap = t_evap - 0.2 < t < t_poreso
    for k, o in enumerate(S["vapor"]):
        if vap:
            rr = random.Random(k); p, u = plume(M, k % 12, 12, t, speed=10, life=1.9, g=5.0, spread=0.16, seed=0)
            u2 = (t * 0.7 + k / 24) % 1; o.location = p + Vector((rr.uniform(-1, 1), -0.6, 1.5 * u2 + 0.3))
            s_ = 0.5 + 1.2 * u2; o.scale = (s_, s_, s_)
        else: o.location = LEJOS
    # hielo en el suelo
    hi = seg(t, t_cong - 0.2, T("hielo duro") + 0.3) * (1 - seg(t, t_romp + 0.5, t_romp + 1.2))
    if hi > 0.01:
        x0 = 13.0; S["hielo"].location = (x0, YC + 0.4, surf(x0) + 0.1); S["hielo"].scale = (12 * hi, 5 * hi, 0.3)
        S["hielo"].rotation_euler = (0, math.atan2(surf(x0 + 1) - surf(x0 - 1), 2) * -1, 0)
    else: S["hielo"].location = LEJOS
    # capa de nieve de la pista
    if t < t_res + 0.5:
        H = 0.9 * seg(t, T("y las pistas"), T("blancas", fin=True)) * (1 - seg(t, t_res - 0.5, t_res + 0.4)); R = 70 * seg(t, T("y las pistas") - 0.3, T("blancas", fin=True))
        H0 = 0.15
    else:
        H = 0.9 * seg(t, t_vale, t_gran + 1.0) + 0.3 * seg(t, t_gran, t_cent + 1.0); R = 12 + 70 * seg(t, t_vale, t_cent)
        H0 = 0.0
    y1 = 6 + 50 * seg(t, t_gran, t_cent + 1.2)
    def hf(x):
        d = min(abs(x - (h + 10)) for h in HX)
        return (H + H0) * max(0.0, min(1.0, (R - d) / 6.0)) if H > 0.01 else 0.0
    layer_set(S["capa"], hf, y1); S["capa"].hide_render = H < 0.01
    # montones bajo cada cañón y pisapistas
    gx = GX(t)
    pisa = t > t_luego - 0.2
    for k, (o, (mx, my)) in enumerate(zip(S["mont"], MOUNDS)):
        grow = seg(t, t_poreso, t_gran + 1.5)
        flat = 1.0 - seg(gx, mx - 4, mx + 1) if pisa else 1.0
        h = 1.8 * grow * flat
        if h > 0.05: o.location = (mx, YF + 6.5, surf(mx) + 0.7); o.scale = (6, 5.5, h); o.hide_render = False
        else: o.location = LEJOS
    if pisa:
        zz = surf(gx) + H + H0; ang = math.atan2(surf(gx + 1) - surf(gx - 1), 2)
        S["pisa"].location = (gx, 2.5, zz - 0.1); S["pisa"].rotation_euler = (0, -ang, 0); show(S["pisa"], True)
        S["monton"].location = (gx + 4.3 * math.cos(ang), 2.5, zz - 4.3 * math.sin(ang) * 0 + surf(gx + 4.3) - surf(gx) + 0.4)
        s_ = 0.8 + 0.6 * seg(t, t_maq, t_aplas); S["monton"].scale = (1.2 * s_, 2.4, 0.9 * s_); S["monton"].hide_render = False
    else:
        S["pisa"].location = LEJOS; show(S["pisa"], False); S["monton"].location = LEJOS
    for k, o in enumerate(S["pana"]):
        xi = -34 + 2 * (k // 2) * 2; yy = 1.5 + (k % 2) * 2.0
        if pisa and gx - 3 > xi:
            z = surf(xi) + H + H0; o.location = (xi, yy, z + 0.02); o.rotation_euler = (0, -math.atan2(surf(xi + 1) - surf(xi - 1), 2), 0)
            o.hide_render = False
        else: o.location = LEJOS
    # muchos cañones
    gon = t > t_gran - 0.3
    for k, e in enumerate(S["grid"]):
        a = t_gran - 0.3 + 0.1 * k; u = seg(t, a, a + 0.4) if gon else 0.0
        x, y = GRID[k]; e.location = (x, y, surf(x)) if u > 0.01 else LEJOS; e.scale = (1.2 * max(u, 0.001),) * 3; show(e, u > 0.01)
    for k, o in enumerate(S["gridp"]):
        j = k // 6
        if gon and t > t_gran + 0.1 * j:
            x, y = GRID[j]; p, u = plume(mouth((x, y, surf(x))) + Vector((0.3, 0, 0.35)), k % 6, 6, t, speed=11, life=1.8, g=5.0, spread=0.15, seed=j)
            o.location = p if p.z > surf(p.x) else LEJOS
        else: o.location = LEJOS
    # boquilla ampliada
    dv = win01(t, t_encan - 0.3, t_vale + 0.2, 0.5, 0.5)
    S["det"].location = DN if dv > 0.01 else LEJOS; S["det"].scale = (max(dv, 0.001),) * 3; show(S["det"], dv > 0.01)
    S["aguja"].rotation_euler = (0, mix(-2.2, 1.2, seg(t, t_aire, t_aire + 0.8)) + 0.04 * math.sin(t * 30), 0)
    flow = dv > 0.5
    for k, o in enumerate(S["dagua"]):
        if flow and t > T("el agua sale") - 0.2:
            u = (t * 0.8 + k / 14) % 1; o.location = DN + Vector((-4.6, -0.45, -1.4)).lerp(Vector((0.6, -0.45, -0.3)), u)
        else: o.location = LEJOS
    for k, o in enumerate(S["daire"]):
        if flow and t > t_aire - 0.2:
            u = (t * 1.3 + k / 14) % 1; o.location = DN + Vector((-4.6, -0.45, 1.4)).lerp(Vector((0.6, -0.45, 0.3)), u)
        else: o.location = LEJOS
    sp_on = flow and t > T("pulveriza") - 0.3
    for k, o in enumerate(S["dspray"]):
        if sp_on:
            rr = random.Random(k); u = (t * 0.9 + k / 40) % 1; d = Vector((1, rr.uniform(-0.15, 0.15), rr.uniform(-0.45, 0.45))).normalized()
            o.location = DN + Vector((2.8, -0.4, 0)) + d * (u * 7) + Vector((0, 0, -1.2 * u * u))
        else: o.location = LEJOS
    pf = flow and t > t_exp - 0.3
    cold = seg(t, t_enfr - 0.2, t_enfr + 0.6)
    S["puff"][0].active_material.diffuse_color = (*lin(tuple(mix(a, b, cold) for a, b in zip((0.95, 0.95, 0.95), (0.55, 0.8, 1.0)))), 0.3)
    for k, o in enumerate(S["puff"]):
        if pf:
            u = (t * 0.6 + k / 10) % 1; o.location = DN + Vector((2.8 + 5 * u, -0.6, 0.6 * math.sin(k * 2.1) * u))
            s_ = 0.3 + 1.6 * u; o.scale = (s_, s_ * 0.5, s_)
        else: o.location = LEJOS
    nu = flow and t > t_crea
    for k, o in enumerate(S["nucleo"]):
        rr = random.Random(50 + k)
        if nu and t > t_crea + 0.06 * k:
            base = DN + Vector((rr.uniform(3.5, 7.5), -0.9, rr.uniform(-1.4, 1.2)))
            fall = max(0.0, t - t_peg - 0.3) * 0.9
            o.location = base + Vector((0.3 * math.sin(t * 2 + k), 0, -fall))
            o.rotation_euler = (t * 2 + k, t, 0)
        else: o.location = LEJOS
    for k, o in enumerate(S["gcae"]):
        rr = random.Random(50 + k)
        if nu and t > t_peg - 0.3:
            base = DN + Vector((rr.uniform(3.5, 7.5), -0.9, rr.uniform(-1.4, 1.2)))
            st = Vector((rr.uniform(-1.5, 1.5), 0, rr.uniform(-1.0, 1.0)))
            u = seg(t, t_peg - 0.2 + 0.08 * k, t_peg + 0.6 + 0.08 * k); fall = max(0.0, t - t_peg - 0.3) * 0.9
            o.location = base + st * (1 - u) + Vector((0.3 * math.sin(t * 2 + k), -0.05, -fall))
            fr = seg(t, t_cong2 + 0.05 * k, t_cong2 + 0.7 + 0.05 * k); set_color(o, tuple(mix(a, b, fr) for a, b in zip(WATER, SNOW)))
        else: o.location = LEJOS
    if nu and t > t_peg - 0.5:
        u = seg(t, t_peg - 0.4, t_peg + 0.4); fall = max(0.0, t - t_peg - 0.3) * 0.9
        S["gota"].location = DN + Vector((5.0, -1.0, 0.6 - fall)) + Vector((-1.6, 0, 0.8)) * (1 - u)
        fr = seg(t, t_cong2, T("caen", fin=True)); set_color(S["gota"], tuple(mix(a, b, fr) for a, b in zip(WATER, SNOW)))
    else: S["gota"].location = LEJOS
    apply_cam(S["cam"], *cam_state(t, CAM(), drift=0.35))

def VD(at, dist, yaw, pitch, lens=32):
    at = Vector(at); y, p = math.radians(yaw), math.radians(pitch)
    return (tuple(at + dist * Vector((math.sin(y) * math.cos(p), -math.cos(y) * math.cos(p), math.sin(p)))), tuple(at), lens)

_CAM = None
def CAM():
    global _CAM
    if _CAM: return _CAM
    k = []
    def add(t, v): k.append((t,) + v)
    M = mouth((0.0, YC, surf(0.0)))
    add(0.0, (tuple(M + Vector((5.5, -3.2, -0.4))), tuple(M + Vector((0.5, 0.3, 0.3))), 24))
    add(1.2, (tuple(M + Vector((6.5, -4.5, -0.2))), tuple(M + Vector((1.0, 0.3, 0.2))), 24))
    add(T("aún no"), VD((4, 0, 24), 42, 35, 10, 26))
    add(T("y las pistas") + 0.4, VD((4, 2, 20), 75, 25, 16, 26))
    add(T("blancas"), VD((6, 4, 18), 90, 18, 18, 26))
    add(T("vamos a hacerla"), VD((0, 4, 18), 110, 0, 14, 26))
    add(T("primero") + 0.3, VD((-40, 0, 38), 60, -10, 16, 28))
    add(T("así que haces") + 0.6, VD((-50, 4, 42), 50, -18, 22, 28))
    add(T("con agua de") + 0.2, VD((-52, 6, 45), 58, -6, 18, 28))
    add(T("río", fin=True), VD((-56, 8, 45), 62, -22, 16, 28))
    add(T("debajo") + 0.6, VD((-12, 0, 20), 75, -8, 12, 28))
    add(T("cada cañón"), VD((0, 0, 22), 66, 6, 12, 28))
    add(T("pero si lanzas") + 0.3, VD((8, YC, 25), 26, -10, 6, 28))
    add(T("y se congela") + 0.6, VD((10, YC, 23), 24, 12, 18, 28))
    add(T("así que la rompes") + 0.6, VD((3.2, YC, 27.5), 12, -10, 6, 28))
    add(T("finísimas", fin=True), VD((3.6, YC, 27.5), 11, 4, 6, 28))
    add(T("en el cañón") + 0.4, (tuple(DN + Vector((-0.5, -15.5, 1.0))), tuple(DN + Vector((-0.5, 0, 1.0))), 30))
    add(T("pulveriza"), (tuple(DN + Vector((0.5, -14.5, 0.8))), tuple(DN + Vector((0.3, 0, 1.0))), 30))
    add(T("al salir"), (tuple(DN + Vector((3.0, -13.5, 0.8))), tuple(DN + Vector((3.0, 0, 1.0))), 30))
    add(T("así crea"), (tuple(DN + Vector((4.5, -12.0, 0.8))), tuple(DN + Vector((4.8, 0, 0.9))), 30))
    add(T("las gotas se") + 0.3, (tuple(DN + Vector((4.5, -11.0, 0.0))), tuple(DN + Vector((4.8, 0, -1.0))), 30))
    add(T("caen", fin=True), (tuple(DN + Vector((4.5, -11.0, -1.4))), tuple(DN + Vector((4.8, 0, -2.4))), 30))
    add(T("pero no vale") + 0.8, VD((7, YC, 27), 30, -8, 8, 28))
    add(T("si está muy seco"), VD((7, YC, 27), 27, 10, 10, 28))
    add(T("cero grados", fin=True), VD((7, YC, 27), 29, -4, 12, 28))
    add(T("madrugada") + 0.3, VD((0, 10, 24), 70, 18, 16, 28))
    add(T("centenar") + 0.2, VD((4, 22, 18), 125, 10, 24, 28))
    add(T("a la vez"), VD((4, 22, 18), 130, -6, 24, 28))
    for q in range(9):
        tq = T("y luego") + 0.4 + 0.75 * q
        if tq > DUR - 0.8: break
        g = GX(tq); z = surf(g)
        add(tq, ((g - 7, YF - 12, z + 10.5), (g + 2, 2.5, z + 1.2), 28))
    add(DUR, VD((10, 6, 14), 90, 12, 18, 28))
    add(DUR + 3, VD((10, 6, 14), 95, 14, 18, 28))
    _CAM = k; return k

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v)
    M = mouth((0.0, YC, surf(0.0)))
    gx = GX(t)
    return {"canon": Pj(tuple(M + Vector((0, 0, 1.2)))), "pista": Pj((14, YF, surf(14) + 1)), "balsa": Pj((-51, YF, 44.5)),
            "rio": Pj((-70, 14, 50)), "tubo": Pj((-10, YF, surf(-10) - 2.2)), "hidr": Pj((22, YF, surf(22) + 3.2)),
            "hielo": Pj((13, YC, surf(13) + 0.6)), "lluvia": Pj((9, YC, 25)), "dagua": Pj(tuple(DN + Vector((-3.2, -0.5, -1.4)))),
            "daire": Pj(tuple(DN + Vector((-3.6, -0.5, 1.4)))), "mano": Pj(tuple(DN + Vector((-2.8, -0.5, 3.4)))),
            "boq": Pj(tuple(DN + Vector((2.6, -0.5, 0)))), "puff": Pj(tuple(DN + Vector((5.5, -0.6, 1.2)))),
            "nuc": Pj(tuple(DN + Vector((5.5, -0.9, 1.0)))), "gota": Pj(tuple(S["gota"].location)) if S["gota"].location.z > -100 else [0.5, 0.5, 1],
            "pisa": Pj((gx, 2.5, surf(gx) + 4.5)), "nieve": Pj((14, YF, surf(14)))}

if __name__ == "__main__":
    run("nieve", build, pose, anchors)
