# «Así funciona el vaho de la ventana»: primer plano de un dedo dibujando en el cristal empañado (las gotitas se borran
# a su paso y otras gotas resbalan); la ventana en corte, de noche: el cristal está seco por fuera; un metro cúbico de
# aire de la habitación con su vapor (puntos azules) que llega al respirar, ducharse y cocinar; al enfriarse de 20 a 10 °C
# el cubo ya no aguanta todo y el sobrante cae en gotas; el cristal se enfría como la calle, una burbuja de aire lo toca,
# se enfría de golpe y deja sus gotitas: el vaho; cristal más gordo (sigue empañado), doble acristalamiento con cámara de
# gas: flechas de calor que casi no pasan, el cristal de dentro se calienta y el vaho desaparece; al final se abre la
# ventana: sale el aire húmedo y entra aire seco.
import bpy, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("ventana")
BG = (0.04, 0.07, 0.13); WALL = (0.86, 0.83, 0.77); CUT = (0.62, 0.55, 0.5); FRAME = (0.95, 0.95, 0.93); FCUT = (0.7, 0.72, 0.75)
GLASS = (0.62, 0.82, 0.88); COLDG = (0.35, 0.6, 1.0); WARMG = (1.0, 0.82, 0.62); VAP = (0.3, 0.65, 1.0); FOG = (0.9, 0.95, 1.0)
DROP = (0.7, 0.88, 1.0); SKIN = (0.93, 0.72, 0.58); HEAT = (1.0, 0.35, 0.2); GAS = (0.75, 0.6, 1.0); SNOW = (0.95, 0.97, 1.0)
LEJOS = (0, 0, -900)
HINGE = Vector((-3.5, 40, 0))
CUBE = Vector((-50, 25, 58)); CS = 26.0
HEAD, SHOWER, POT = Vector((-64, 24, 28)), Vector((-50, 24, 38)), Vector((-36, 24, 24))
RNG = random.Random(4)

def alpha(o, a):
    m = o.active_material; m.diffuse_color = (*m.diffuse_color[:3], a); m.surface_render_method = 'BLENDED'
def show(o, on):
    o.hide_render = not on
    for c in o.children: show(c, on)
def grow(o, u, base=1.0):
    u = max(u, 0.001); o.scale = (base * u, base * u, base * u)
def hide_bar(o): bar_set(o, LEJOS, Vector(LEJOS) + Vector((0, 0, 0.01)))
def arrow(col, r=0.5):
    e = empty(LEJOS)
    cyl(r, 1.0, (0, 0, 0.5), col, parent=e, v=12)
    bpy.ops.mesh.primitive_cone_add(radius1=r * 2.4, radius2=0, depth=r * 4, location=(0, 0, 1.0 + r * 2), vertices=16); setup(bpy.context.object, col, parent=e)
    return e
def put_arrow(e, p0, p1, r=1.0):
    """flecha de p0 a p1: el palo se estira, la punta mantiene su tamaño (r = escala del grosor)"""
    p0, p1 = Vector(p0), Vector(p1); d = p1 - p0; L = d.length
    e.location = p0; e.rotation_mode = 'QUATERNION'; e.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())
    e.scale = (r, r, 1); st, tip = e.children[0], e.children[1]
    st.scale = (1, 1, max(L - 2.4 * r, 0.01)); tip.location = (0, 0, max(L - 2.4 * r, 0.01) + 1.2 * r); tip.scale = (1, 1, r)

# gotitas del vaho (en la cara interior del cristal), dedo, gotas que resbalan
FY = [1.2 + 1.6 * i for i in range(21)]; FZ = [20 + 1.6 * j for j in range(44)]
DOTS = [(y + RNG.uniform(-0.4, 0.4), z + RNG.uniform(-0.4, 0.4), RNG.random(), RNG.uniform(0.45, 0.75)) for y in FY for z in FZ]
def heart(s):
    a = 2 * math.pi * s
    return Vector((0, 18 + 0.42 * 16 * math.sin(a) ** 3, 56 + 0.42 * (13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))))
F0, F1 = 0.15, 3.2
def finger_tip(t):
    s = max(0, min(1, (t - F0) / (F1 - F0))); return heart(s)
DRIPS = [(30.5, 72, 0.9, 7.0), (6.0, 80, 2.0, 6.0), (27.0, 46, 1.4, 8.0)]   # y, z0, t0, velocidad
def drip_pos(k, t):
    y, z0, t0, v = DRIPS[k]; return Vector((0, y, z0 - max(0, t - t0) * v))
CLEAR = []
for (y, z, th, r) in DOTS:
    tc = 99.0
    for i in range(121):
        tt = F0 + (F1 - F0) * i / 120; p = finger_tip(tt)
        if (p.y - y) ** 2 + (p.z - z) ** 2 < 1.5 ** 2: tc = tt; break
    for k in range(3):
        for i in range(80):
            tt = DRIPS[k][2] + i * 0.08; p = drip_pos(k, tt)
            if p.z < 18: break
            if (p.y - y) ** 2 + (p.z - z) ** 2 < 1.1 ** 2 and z <= DRIPS[k][1] + 0.5: tc = min(tc, tt); break
    CLEAR.append(tc)
NV = 32
VDOT = [(RNG.uniform(0, 6.28), RNG.uniform(0.5, 1.3), RNG.uniform(0.5, 1.3), RNG.uniform(0.5, 1.3)) for _ in range(NV)]
SNOWP = [(RNG.uniform(6, 90), RNG.uniform(-10, 90), RNG.uniform(0, 140), RNG.uniform(5, 9)) for _ in range(70)]
PARC = [Vector((RNG.uniform(-1, 1), RNG.uniform(-1, 1), RNG.uniform(-1, 1))).normalized() * RNG.uniform(1.0, 3.6) for _ in range(14)]
OUTP = [(RNG.uniform(0, 1), RNG.uniform(5, 30), RNG.uniform(15, 85)) for _ in range(26)]

def fogs(t):
    f = keyed(t, [(0, 1.0), (T("mira") + 0.4, 1.0), (T("el aire de") + 0.2, 0.0), (T("gotitas") - 0.2, 0.0), (T("eso es") + 0.8, 1.0),
                  (T("así que el de dentro") + 0.6, 1.0), (T("por eso", 1), 0.08), (T("y si aun") - 0.2, 0.08), (T("se empaña", 2) + 0.4, 0.75),
                  (T("abre") + 0.8, 0.75), (T("seco") + 0.3, 0.0)])
    return f

def tglass(t):
    """temperatura del cristal (el de dentro, con doble acristalamiento)"""
    return keyed(t, [(0, 20.0), (T("el cristal se") - 0.1, 20.0), (T("calle") + 0.3, 10.0), (T("así que el de dentro") + 0.3, 10.0), (T("cuarto", fin=True), 16.0)])

def inner_x(t):
    """cara interior del cristal: simple → gordo → doble"""
    g = seg(t, T("gordo") - 0.6, T("gordo") + 0.3) * (1 - seg(t, T("es meter"), T("es meter") + 0.8))
    d = seg(t, T("es meter"), T("es meter") + 0.8)
    return -0.5 - 1.5 * g - 1.1 * d

def build():
    sc, cam = scene_setup(world=BG, shadow=0.32, light_rot=150)
    S = {"cam": cam}; sc.display.shading.use_world_space_lighting = False
    # pared en corte (todo empieza en y=0)
    box((25, 80, 40), (0.5, 40, -20), WALL); box((25, 80, 30), (0.5, 40, 115), WALL); box((25, 40, 100), (0.5, 60, 50), (0.42, 0.4, 0.45))
    box((25, 0.4, 40), (0.5, -0.2, -20), CUT); box((25, 0.4, 30), (0.5, -0.2, 115), CUT)
    box((10, 82, 3), (-17, 40, -1.5), (0.95, 0.94, 0.9))      # alféizar interior
    box((8, 82, 2), (16, 40, -1), (0.6, 0.6, 0.62))            # vierteaguas exterior
    # calle de noche: edificios con ventanas, luna
    for k in range(7):
        x = 160 + RNG.uniform(0, 60); y = -120 + k * 45; h = RNG.uniform(60, 160)
        box((30, 34, h), (x, y, h / 2 - 60), (0.08, 0.1, 0.17))
        for j in range(8):
            if RNG.random() < 0.45:
                box((0.5, 5, 6), (x - 15.3, y + RNG.uniform(-12, 12), RNG.uniform(-50, h - 70)), (1.0, 0.82, 0.45))
    sph(14, (320, 120, 170), (0.95, 0.95, 0.85))
    # hoja de la ventana (gira sobre la bisagra al final)
    S["hoja"] = empty(HINGE); h = S["hoja"]
    L = lambda x, y, z: (x - HINGE.x, y - HINGE.y, z - HINGE.z)
    box((7, 40, 6), L(0, 20, 3), FRAME, parent=h); box((7, 40, 6), L(0, 20, 97), FRAME, parent=h); box((7, 6, 100), L(0, 37, 50), FRAME, parent=h)
    box((7.02, 0.3, 6), L(0, 0.15, 3), FCUT, parent=h); box((7.02, 0.3, 6), L(0, 0.15, 97), FCUT, parent=h)
    S["vidrio"] = box((1, 34, 88), L(0, 17, 50), GLASS, parent=h, unique=True); alpha(S["vidrio"], 0.35)
    S["vin"] = box((0.6, 34, 88), L(-1.3, 17, 50), GLASS, parent=h, unique=True); alpha(S["vin"], 0.4)
    S["vout"] = box((0.6, 34, 88), L(1.3, 17, 50), GLASS, parent=h, unique=True); alpha(S["vout"], 0.4)
    S["gas"] = box((1.9, 34, 88), L(0, 17, 50), GAS, parent=h, unique=True); alpha(S["gas"], 0.13)
    S["borde"] = [box((0.2, 34, 0.2), L(0, 17, 6.1), (0.15, 0.15, 0.18), parent=h), box((0.2, 34, 0.2), L(0, 17, 93.9), (0.15, 0.15, 0.18), parent=h)]
    S["vaho"] = [sph(r, L(-0.85, y, z), FOG, parent=h, scale=(0.35, 1, 1), seg=8) for (y, z, th, r) in DOTS]
    S["drips"] = [sph(1.0, LEJOS, DROP, parent=h, scale=(0.5, 0.9, 1.25), seg=12) for _ in DRIPS]
    # dedo
    S["dedo"] = empty(LEJOS); d = S["dedo"]
    sph(1.05, (0, 0, 0), SKIN, parent=d, scale=(0.8, 1, 1.1))
    cyl(1.05, 9, (-4.5, 0, 0), SKIN, parent=d, rot=(0, math.pi / 2, 0)); cyl(1.1, 7, (-11, 0, 0), SKIN, parent=d, rot=(0, math.pi / 2, 0))
    box((0.3, 1.3, 1.5), (-0.4, 0, 0.55), (0.98, 0.85, 0.8), parent=d)
    # cubo de aire con vapor
    S["cubo"] = empty(CUBE); c = S["cubo"]
    S["aristas"] = []
    h2 = CS / 2
    for a, b in [((-1, -1, -1), (1, -1, -1)), ((-1, 1, -1), (1, 1, -1)), ((-1, -1, 1), (1, -1, 1)), ((-1, 1, 1), (1, 1, 1)),
                 ((-1, -1, -1), (-1, 1, -1)), ((1, -1, -1), (1, 1, -1)), ((-1, -1, 1), (-1, 1, 1)), ((1, -1, 1), (1, 1, 1)),
                 ((-1, -1, -1), (-1, -1, 1)), ((1, -1, -1), (1, -1, 1)), ((-1, 1, -1), (-1, 1, 1)), ((1, 1, -1), (1, 1, 1))]:
        o = bar_obj((1.0, 0.7, 0.3), 0.45, parent=c, unique=True); bar_set(o, Vector(a) * h2, Vector(b) * h2); o.location = Vector(a) * h2
        S["aristas"].append(o)
    S["aire"] = box((CS, CS, CS), (0, 0, 0), (1.0, 0.8, 0.55), parent=c, unique=True); alpha(S["aire"], 0.12)
    S["vap"] = [sph(1.1, LEJOS, VAP, seg=10, unique=True) for _ in range(NV)]
    # fuentes de vapor: cabeza, ducha y olla
    S["cabeza"] = empty(HEAD); hd = S["cabeza"]
    sph(5, (0, 0, 0), SKIN, parent=hd); sph(5.2, (-0.6, 0.4, 1.4), (0.3, 0.2, 0.12), parent=hd, scale=(1, 1, 0.75))
    sph(0.9, (4.9, -0.2, -0.6), SKIN, parent=hd); sph(0.55, (2.8, -4.3, 0.8), (0.1, 0.1, 0.1), parent=hd)
    S["ducha"] = empty(SHOWER); du = S["ducha"]
    cyl(3.5, 1.0, (0, 0, 0), (0.8, 0.82, 0.86), parent=du); o = bar_obj((0.8, 0.82, 0.86), 0.5, parent=du); bar_set(o, (0, 0, 0.5), (0, 8, 8)); o.location = (0, 0, 0.5)
    S["chorros"] = [bar_obj((0.6, 0.85, 1.0), 0.18) for _ in range(7)]
    S["olla"] = empty(POT); ol = S["olla"]
    cyl(6, 7, (0, 0, 0), (0.35, 0.37, 0.42), parent=ol); cyl(6.6, 0.5, (0, 0, 3.6), (0.3, 0.32, 0.36), parent=ol)
    cyl(8, 1.5, (0, 0, -4.3), (0.15, 0.15, 0.17), parent=ol); torus(4.5, 0.4, (0, 0, -3.4), (1.0, 0.4, 0.1), parent=ol)
    # gotas sobrantes del cubo
    S["sobra"] = [sph(1.2, LEJOS, DROP, seg=10) for _ in range(8)]
    # nieve
    S["nieve"] = [sph(0.5, LEJOS, SNOW, seg=6) for _ in SNOWP]
    # burbuja de aire que toca el cristal
    S["burb"] = sph(5, LEJOS, (1.0, 0.8, 0.55), seg=24, unique=True); alpha(S["burb"], 0.25)
    S["bvap"] = [sph(0.55, LEJOS, VAP, seg=8, unique=True) for _ in PARC]
    # flechas de calor
    S["calor_in"] = [arrow(HEAT) for _ in range(3)]
    S["calor_out"] = [arrow(HEAT) for _ in range(3)]
    # ventilación
    S["sale"] = [sph(0.9, LEJOS, VAP, seg=8) for _ in OUTP]
    S["entra"] = [arrow((0.85, 0.95, 1.0), 0.35) for _ in range(4)]
    dyn = [cam, S["hoja"], S["dedo"], S["cubo"], S["vap"], S["cabeza"], S["ducha"], S["chorros"], S["olla"], S["sobra"], S["nieve"],
           S["burb"], S["bvap"], S["calor_in"], S["calor_out"], S["sale"], S["entra"]]
    join_static(dyn)
    return sc, S

# --------------------------------------------------------------------------------------------------
def vap_pos(k, t):
    ph, a, b, c = VDOT[k]
    return CUBE + Vector((math.sin(t * a + ph) * 0.4, math.sin(t * b * 0.8 + ph * 2) * 0.4, math.sin(t * c * 0.7 + ph * 3) * 0.4)) * CS

def pose(t, S):
    t_aire, t_resp, t_duch, t_coc, t_pero = T("el aire de"), T("respirar"), T("ducharte"), T("cocinar"), T("pero el aire no")
    t_metro, t_diez, t_noche, t_crist, t_golpe, t_got = T("un metro"), T("a diez"), T("y de noche"), T("el cristal se"), T("así que el aire"), T("gotitas")
    t_gordo, t_meter, t_doble, t_camara, t_dentro, t_si, t_abre, t_fin = T("gordo"), T("es meter"), T("doble"), T("cámara"), T("así que el de dentro"), T("y si aun"), T("abre"), T("sígueme")
    h = S["hoja"]
    # apertura final de la ventana
    op = seg(t, t_abre - 0.1, t_abre + 1.4) * (1 - seg(t, t_fin + 0.2, t_fin + 0.9))
    h.rotation_euler = (0, 0, -math.radians(75) * op)
    # cristales
    g = seg(t, t_gordo - 0.6, t_gordo + 0.3) * (1 - seg(t, t_meter, t_meter + 0.3))
    dbl = t > t_meter
    S["vidrio"].hide_render = dbl; S["vidrio"].scale = (1 + 3 * g, 1, 1)
    for o in (S["vin"], S["vout"]): o.hide_render = not dbl
    sp = seg(t, t_meter, t_meter + 0.8)
    S["vin"].location = (-3.5 + HINGE.x * 0 + 3.5 - mix(0.3, 1.3, sp) - 0, -23, 50) if False else (3.5 - mix(0.3, 1.3, sp), -23, 50)
    S["vout"].location = (3.5 + mix(0.3, 1.3, sp), -23, 50)
    S["gas"].hide_render = not (t > t_camara - 0.3); S["gas"].scale = (max(seg(t, t_camara - 0.3, t_camara + 0.4), 0.01), 1, 1)
    cold = seg(t, t_crist, T("calle") + 0.3)
    if t < t_aire: cold = 1.0
    gcol = tuple(mix(a, b, cold) for a, b in zip(GLASS, COLDG))
    set_color(S["vidrio"], gcol); S["vidrio"].active_material.diffuse_color[3] = 0.35 + 0.15 * cold + 0.3 * seg(t, T("curioso") - 0.5, T("curioso"))
    set_color(S["vout"], COLDG); S["vout"].active_material.diffuse_color[3] = 0.4
    w = seg(t, t_dentro, T("cuarto", fin=True))
    set_color(S["vin"], tuple(mix(a, b, w) for a, b in zip(COLDG, WARMG))); S["vin"].active_material.diffuse_color[3] = 0.45 - 0.2 * w
    # vaho
    f = fogs(t); xi = inner_x(t) - 0.35 + 3.5
    early = t < T("el aire de")
    for (y, z, th, r), tc, o in zip(DOTS, CLEAR, S["vaho"]):
        vis = f > th * 0.98 + 0.01 and not (early and t > tc)
        o.hide_render = not vis
        if vis:
            s = min(1.0, (f - th) * 4 + 0.35); o.scale = (0.35 * s, s, s); o.location = (xi, y - 40, z)
    for k, o in enumerate(S["drips"]):
        if early and t > DRIPS[k][2] - 0.3:
            p = drip_pos(k, t); o.location = (xi - 0.2, p.y - 40, p.z); o.hide_render = p.z < 18
        else: o.location = LEJOS
    # dedo
    if t < F1 + 0.8:
        tip = finger_tip(t); back = seg(t, F1, F1 + 0.8)
        S["dedo"].location = Vector((-1.1 - 14 * back, tip.y, tip.z - 6 * back)); S["dedo"].rotation_euler = (0, math.radians(-25), math.radians(8))
        show(S["dedo"], True)
    else: S["dedo"].location = LEJOS; show(S["dedo"], False)
    # cubo de aire
    cu = t_aire - 0.3 < t < t_noche + 0.6
    show(S["cubo"], cu); grow(S["cubo"], seg(t, t_aire - 0.3, t_aire + 0.5) * (1 - seg(t, t_noche, t_noche + 0.6)))
    temp = keyed(t, [(0, 20), (t_diez - 0.2, 20), (T("grados", 2, fin=True), 10)])
    u = (20 - temp) / 10
    for o in S["aristas"]: set_color(o, tuple(mix(a, b, u) for a, b in zip((1.0, 0.65, 0.25), (0.35, 0.65, 1.0))))
    set_color(S["aire"], tuple(mix(a, b, u) for a, b in zip((1.0, 0.8, 0.55), (0.55, 0.75, 1.0)))); S["aire"].active_material.diffuse_color[3] = 0.12
    srcs = [(HEAD + Vector((5.5, 0, -0.6)), t_resp), (SHOWER + Vector((0, 0, -1)), t_duch), (POT + Vector((0, 0, 4)), t_coc)]
    vis_c = seg(t, t_aire - 0.3, t_aire + 0.5) * (1 - seg(t, t_noche, t_noche + 0.6))
    for k, o in enumerate(S["vap"]):
        if not cu: o.location = LEJOS; continue
        p = vap_pos(k, t)
        if k >= 16:
            src, ts = srcs[k % 3]; t0 = ts + 0.15 * (k // 3 - 5)
            if t < t0: o.location = LEJOS; continue
            p = Vector(src).lerp(p, seg(t, t0, t0 + 1.4)) + Vector((0, 0, 0))
        if k >= 24:
            dz = seg(t, t_diez + 0.5 + 0.1 * (k - 24), t_diez + 1.2 + 0.1 * (k - 24))
            if dz > 0: o.location = LEJOS; continue
        o.location = CUBE + (p - CUBE) * vis_c if k < 16 else p
    for j, o in enumerate(S["sobra"]):
        k = 24 + j; t1 = t_diez + 0.5 + 0.1 * j
        if cu and t > t1:
            p0 = vap_pos(k, t1); zf = CUBE.z - CS / 2 + 1.2
            o.location = Vector((p0.x, p0.y, max(zf, p0.z - 40 * (t - t1) ** 2))); grow(o, vis_c)
        else: o.location = LEJOS
    # fuentes
    for key, ts in (("cabeza", t_resp), ("ducha", t_duch), ("olla", t_coc)):
        on = ts - 0.4 < t < t_pero + 0.3
        show(S[key], on); grow(S[key], seg(t, ts - 0.4, ts + 0.1) * (1 - seg(t, t_pero - 0.2, t_pero + 0.3)))
    S["olla"].rotation_euler = (0.03 * math.sin(t * 30), 0, 0)
    for k, o in enumerate(S["chorros"]):
        if t_duch < t < t_pero:
            a = k / 7 * 6.28; p0 = SHOWER + Vector((2 * math.cos(a), 2 * math.sin(a), -0.6)); L = 8 + 1.5 * math.sin(t * 20 + k)
            bar_set(o, p0, p0 + Vector((0, 0, -L)))
        else: hide_bar(o)
    # nieve (fuera, de noche)
    sn = (t < T("mira") + 0.5) or (t > t_noche - 0.3)
    for (x, y, z, v), o in zip(SNOWP, S["nieve"]):
        o.location = (x + 1.5 * math.sin(t + y), y, (z - v * t) % 140 - 10) if sn else LEJOS
    # burbuja de aire que toca el cristal
    bu = t_golpe - 0.4 < t < T("eso es") + 0.3
    x0 = inner_x(t) - 5.2
    bp = Vector((-26, 10, 50)).lerp(Vector((x0, 10, 50)), seg(t, t_golpe - 0.4, T("toca") + 0.4))
    cb = seg(t, T("golpe") - 0.3, T("golpe") + 0.4)
    S["burb"].location = bp if bu else LEJOS
    grow(S["burb"], seg(t, t_golpe - 0.4, t_golpe + 0.1) * (1 - seg(t, T("eso es"), T("eso es") + 0.3)))
    set_color(S["burb"], tuple(mix(a, b, cb) for a, b in zip((1.0, 0.8, 0.55), (0.45, 0.7, 1.0)))); S["burb"].active_material.diffuse_color[3] = 0.25
    for k, o in enumerate(S["bvap"]):
        if not bu: o.location = LEJOS; continue
        q = bp + PARC[k] * (1 + 0.15 * math.sin(t * 3 + k))
        if k < 9:
            st = seg(t, t_got - 0.2 + 0.08 * k, t_got + 0.5 + 0.08 * k)
            q = q.lerp(Vector((inner_x(t) - 0.6, 10 + PARC[k].y * 2, 50 + PARC[k].z * 2)), st)
            set_color(o, tuple(mix(a, b, st) for a, b in zip(VAP, FOG)))
        o.location = q
    # flechas de calor (de dentro hacia fuera)
    hf = t_doble - 0.2 < t < t_dentro + 0.5
    for k in range(3):
        z = 34 + 16 * k; ei, eo = S["calor_in"][k], S["calor_out"][k]
        show(ei, hf); show(eo, hf)
        if hf:
            a = seg(t, t_doble - 0.2, t_doble + 0.5); r_out = mix(1.0, 0.25, seg(t, T("apenas") - 0.2, T("apenas") + 0.8))
            ph = (t * 1.5 + k * 0.3) % 1
            put_arrow(ei, (-24 + 2 * ph, 3, z), (-2.4, 3, z), 1.0 * a + 0.01)
            put_arrow(eo, (2.4, 3, z), (22 + 2 * ph, 3, z), r_out * a + 0.01)
        else: ei.location = LEJOS; eo.location = LEJOS
    # ventilar: sale aire húmedo, entra aire seco
    ve = t_abre + 0.6 < t < t_fin + 0.4
    for k, (ph, y, z) in enumerate(OUTP):
        if ve:
            u = (t * 0.45 + ph) % 1; o = S["sale"][k]; o.location = (mix(-30, 40, u), y - 4, z + 18 * u)
        else: S["sale"][k].location = LEJOS
    for k, e in enumerate(S["entra"]):
        show(e, ve)
        if ve:
            u = (t * 0.6 + k / 4) % 1; z = 12 + 6 * k
            put_arrow(e, (mix(40, -10, u), 4, z), (mix(40, -10, u) - 9, 4, z), 1.0)
        else: e.location = LEJOS
    apply_cam(S["cam"], *cam_state(t, CAM(), drift=0.25))

def VD(at, dist, yaw, pitch, lens=40):
    at = Vector(at); y, p = math.radians(yaw), math.radians(pitch)
    return (tuple(at + dist * Vector((math.sin(y) * math.cos(p), -math.cos(y) * math.cos(p), math.sin(p)))), tuple(at), lens)

def FACE(at, dist, yaw, pitch, lens=40):
    """mirando el cristal desde dentro (yaw 0 = de frente)"""
    at = Vector(at); y, p = math.radians(yaw), math.radians(pitch)
    return (tuple(at + dist * Vector((-math.cos(y) * math.cos(p), math.sin(y) * math.cos(p), math.sin(p)))), tuple(at), lens)

def CAM():
    k = []
    def add(t, v): k.append((t,) + v)
    add(0.0, FACE((0, 18, 56), 36, 12, 4))
    add(2.4, FACE((0, 18, 55), 42, -6, 2))
    add(T("pero ese") + 0.3, VD((-4, 18, 52), 95, -40, 8))
    add(T("mira") + 0.5, VD((-2, 14, 54), 115, -10, 6))
    add(T("el aire de") + 0.8, VD(CUBE + Vector((0, 0, -9)), 125, -8, 8))
    add(T("y lo vas") + 0.4, VD((-50, 24, 48), 128, 6, 10))
    add(T("pero el aire no") + 0.6, VD(CUBE + Vector((0, 0, -9)), 118, -6, 12))
    add(T("a diez"), VD(CUBE + Vector((0, 0, -9)), 112, 8, 14))
    add(T("y de noche") + 0.5, FACE((0, 18, 55), 115, -42, 6))
    add(T("el cristal se") + 0.6, FACE((0, 18, 55), 90, -34, 4))
    add(T("así que el aire") + 0.2, FACE((-4, 12, 52), 58, -40, 4))
    add(T("gotitas"), FACE((-1, 12, 52), 42, -34, 4))
    add(T("eso es") + 0.4, FACE((0, 18, 55), 60, -20, 6))
    add(T("si el cristal"), FACE((0, 18, 55), 72, -30, 6))
    add(T("curioso") + 0.2, VD((0, 4, 50), 30, -6, 14))
    add(T("es meter") + 0.4, VD((0, 4, 50), 26, -4, 12))
    add(T("doble") + 0.4, VD((0, 10, 50), 70, -6, 6))
    add(T("apenas"), VD((0, 10, 50), 64, -12, 6))
    add(T("así que el de dentro") + 0.4, VD((-2, 10, 52), 62, -16, 6))
    add(T("por eso") + 0.4, FACE((0, 18, 55), 64, -30, 6))
    add(T("abre"), VD((-8, 24, 50), 150, -22, 10))
    add(T("seco"), VD((-8, 24, 46), 150, -10, 10))
    add(DUR + 3, VD((-6, 22, 48), 140, -16, 8))
    return k

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v); xi = inner_x(t)
    return {"fuera": Pj((8, 6, 70)), "dentro": Pj((xi - 1, 6, 70)), "cubo": Pj(tuple(CUBE + Vector((0, -CS / 2, CS / 2)))), "cubo_c": Pj(tuple(CUBE)),
            "cabeza": Pj(tuple(HEAD + Vector((0, 0, 6)))), "ducha": Pj(tuple(SHOWER + Vector((0, 0, 3)))), "olla": Pj(tuple(POT + Vector((0, 0, 5)))),
            "cristal": Pj((xi, 4, 76)), "burb": Pj((-12, 10, 57)), "calle": Pj((40, 10, 90)), "gas": Pj((0, 2, 30)), "vout": Pj((1.3, 2, 82)),
            "vin": Pj((-1.3, 2, 82)), "abierta": Pj((-20, 10, 60)), "base": Pj((0, 10, 8))}

if __name__ == "__main__":
    run("ventana", build, pose, anchors)
