# «Así lee tu móvil la huella»: un dedo gigante baja sobre el sensor y el móvil se desbloquea. Corte microscópico: crestas
# que tocan el sensor, valles con aire, placas-condensador con su carga (barras) que baja mucho bajo las crestas y casi
# nada bajo los valles; cada placa se vuelve un píxel oscuro o claro. Rejilla de 88×88 píxeles que se va llenando con la
# huella; puntos donde una cresta termina o se divide; el mapa se queda solo; un segundo mapa (dedo girado) se compara;
# desbloqueo; cinco intentos fallidos y el teclado del código; huella bajo la pantalla con luz o ultrasonido.
import bpy, bmesh, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector

T0, DUR = cargar("huella")
_TC = {}
def T(k, n=1, fin=False):
    key = (k, n, fin)
    if key not in _TC: _TC[key] = T0(k, n, fin)
    return _TC[key]

BG = (0.06, 0.07, 0.1); DESK = (0.13, 0.14, 0.18); PHONE = (0.16, 0.17, 0.2); SCR_OFF = (0.03, 0.03, 0.05); SCR_LOCK = (0.1, 0.14, 0.28)
SCR_OK = (0.2, 0.55, 0.9); SCR_BAD = (0.75, 0.15, 0.15); RING = (0.7, 0.72, 0.78); RING_ON = (0.35, 0.85, 1.0)
SKIN = (0.93, 0.72, 0.58); SKIN_D = (0.82, 0.58, 0.45); SKIN2 = (0.62, 0.42, 0.3); GLASS = (0.55, 0.7, 0.8); AIR = (0.75, 0.9, 1.0)
PLATE = (0.75, 0.62, 0.3); CHG = (1.0, 0.82, 0.16); DARKPX = (0.08, 0.09, 0.12); LIGHTPX = (0.85, 0.88, 0.92); RED = (0.95, 0.25, 0.25)
BLUE = (0.3, 0.65, 1.0); WHITE = (0.95, 0.96, 0.98); OLED = (0.12, 0.1, 0.2); CHIP = (0.2, 0.55, 0.35); RAY = (1.0, 0.9, 0.4)
LEJOS = Vector((0, 300, -300))
LA = Vector((0, 0, 0)); LB = Vector((30, 0, 3)); LC = Vector((60, 0, 0)); LD = Vector((-30, 0, 0))
SEN = Vector((0, -0.62, 0.09))     # centro del sensor
NG = 88; CS = 0.1                  # rejilla de píxeles
RX = [-1.5 + 0.5 * k for k in range(7)]                 # crestas (corte)
PX = [-1.5 + 0.25 * k for k in range(13)]              # placas (corte)

def ridge(u, v):
    if u * u / 0.62 + (v + 0.02) ** 2 / 0.95 > 1: return False
    r = math.sqrt(u * u + (1.35 * (v + 0.12)) ** 2); th = math.atan2(v + 0.12, u)
    return math.sin(2 * math.pi * (r * 7.5 + 0.22 * math.sin(2 * th) + 0.05 * u)) > 0.05

def cells_mesh(cells, color, z=0.0):
    me = bpy.data.meshes.new("px"); bm = bmesh.new(); h = CS * 0.44
    for i, j in cells:
        x = (i - NG / 2 + 0.5) * CS; y = (j - NG / 2 + 0.5) * CS
        vs = [bm.verts.new((x + dx, y + dy, z)) for dx, dy in ((-h, -h), (h, -h), (h, h), (-h, h))]
        bm.faces.new(vs)
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("px", me); bpy.context.collection.objects.link(o); return setup(o, color)

def cone(r, h, color, unique=False):
    bpy.ops.mesh.primitive_cone_add(radius1=r, radius2=0, depth=h, location=(0, 0, 0), vertices=16); o = bpy.context.object
    for vv in o.data.vertices: vv.co.z += h / 2
    return setup(o, color, None, True, unique)

rng = random.Random(5)
MIN = []
while len(MIN) < 14:
    u, v = rng.uniform(-0.65, 0.65), rng.uniform(-0.85, 0.85)
    if ridge(u, v) and u * u / 0.5 + v * v / 0.8 < 1 and all((u - a) ** 2 + (v - b) ** 2 > 0.06 for a, b in MIN): MIN.append((u, v))
EDGES = []
for k, (u, v) in enumerate(MIN):
    d = sorted(range(len(MIN)), key=lambda j: (MIN[j][0] - u) ** 2 + (MIN[j][1] - v) ** 2)
    for j in d[1:3]:
        if (min(k, j), max(k, j)) not in EDGES: EDGES.append((min(k, j), max(k, j)))
HALF = NG * CS / 2

def mpos(u, v, rot=0.0, off=(0, 0)):
    x, y = u * HALF, v * HALF
    c, s = math.cos(rot), math.sin(rot)
    return LC + Vector((c * x - s * y + off[0], s * x + c * y + off[1], 0.08))

def phone(loc):
    e = empty(loc)
    rounded_slab(0.78, 1.6, 0.1, 0.08, (0, 0, 0.01), PHONE, e)
    scr = rounded_slab(0.7, 1.2, 0.05, 0.005, (0, 0.1, 0.09), SCR_OFF, e, unique=True)
    torus(0.09, 0.012, (SEN.x, SEN.y, 0.09), RING, e)
    ring = torus(0.09, 0.012, (SEN.x, SEN.y, 0.092), RING, e, unique=True)
    cyl(0.08, 0.006, (SEN.x, SEN.y, 0.088), (0.1, 0.1, 0.12), e)
    return e, scr, ring

def finger(color):
    e = empty(LEJOS)
    cyl(0.13, 1.4, (0, 0.7, 0), color, e, rot=(math.pi / 2, 0, 0))
    sph(0.13, (0, 0, 0), color, e, scale=(1, 1.1, 0.9))
    sph(0.1, (0, 0.18, 0.09), (0.95, 0.85, 0.8), e, scale=(0.9, 1.2, 0.3))     # uña
    return e

def build():
    sc, cam = scene_setup(world=BG, shadow=0.3); cam.data.clip_start = 0.01
    S = {"cam": cam}
    box((200, 60, 0.2), (0, 0, -0.1), DESK)
    # ---- A: móvil
    S["ph"], S["scr"], S["ring"] = phone(LA)
    lock = empty(LA + Vector((0, 0.25, 0.1))); S["lock"] = lock
    box((0.16, 0.03, 0.13), (0, 0, 0.0), WHITE, lock, rot=(0, 0, 0))
    S["shackle"] = torus(0.055, 0.014, (0, 0, 0.07), WHITE, lock, rot=(0, 0, 0))
    lock.rotation_euler = (0, 0, 0)
    S["keys"] = [cyl(0.055, 0.004, LEJOS, WHITE) for _ in range(12)]
    S["fing"] = finger(SKIN); S["fing2"] = finger(SKIN2)
    # ---- B: corte microscópico
    box((4.4, 2.0, 0.1), LB + Vector((0, 0.4, 0.15)), GLASS)                   # cristal del sensor (z 0.1-0.2)
    S["plates"] = []
    for row in range(3):
        for k, x in enumerate(PX):
            p = box((0.2, 0.36, 0.07), LB + Vector((x, row * 0.45, 0.045)), PLATE, unique=(row == 0))
            if row == 0: S["plates"].append(p)
    S["chg"] = [bar_obj(CHG, r=0.05, unique=True) for _ in PX]
    skin = empty(LB); S["skin"] = skin
    box((4.2, 1.6, 1.0), (0, 0.4, 0.88), SKIN, skin)
    for x in RX: cyl(0.2, 1.6, (x, 0.4, 0.4), SKIN_D, skin, rot=(math.pi / 2, 0, 0))
    S["air"] = [sph(0.07, LEJOS, AIR) for _ in range(6)]
    # ---- C: rejilla de 88 × 88 píxeles y mapas
    dark = [(i, j) for i in range(NG) for j in range(NG) if ridge((i - NG / 2 + 0.5) / (NG / 2), (j - NG / 2 + 0.5) / (NG / 2))]
    light = [(i, j) for i in range(NG) for j in range(NG) if (i, j) not in set(dark)]
    S["pxd"] = cells_mesh(dark, DARKPX); S["pxl"] = cells_mesh(light, LIGHTPX)
    for o in (S["pxd"], S["pxl"]): o.location = LC + Vector((0, 0, 0.02))
    box((NG * CS + 0.3, NG * CS + 0.3, 0.02), LC + Vector((0, 0, 0.0)), (0.22, 0.24, 0.3))
    S["cover"] = box((1, 1, 0.05), LEJOS, (0.22, 0.24, 0.3))
    S["mdots"] = [sph(0.13, LEJOS, RED, unique=True) for _ in MIN]
    S["mring"] = [torus(0.26, 0.04, LEJOS, RED) for _ in MIN]
    S["medges"] = [bar_obj(RED, r=0.035) for _ in EDGES]
    S["ndots"] = [sph(0.11, LEJOS, BLUE) for _ in MIN]
    S["nedges"] = [bar_obj(BLUE, r=0.03) for _ in EDGES]
    # ---- D: huella bajo la pantalla (corte de capas)
    box((3.0, 1.2, 0.16), LD + Vector((0, 0, 0.6)), (0.7, 0.85, 0.95))          # cristal
    box((3.0, 1.2, 0.14), LD + Vector((0, 0, 0.45)), OLED)                      # pantalla
    S["pix"] = [box((0.12, 1.24, 0.04), LD + Vector((-1.35 + 0.15 * k, 0, 0.5)), (0.3, 0.3, 0.45), unique=True) for k in range(19)]
    box((3.0, 1.2, 0.3), LD + Vector((0, 0, 0.22)), PHONE)
    box((0.9, 1.26, 0.08), LD + Vector((0, 0, 0.33)), CHIP)
    S["rays"] = [bar_obj(RAY, r=0.03) for _ in range(7)]
    S["us"] = [torus(1.0, 0.02, LEJOS, RING_ON) for _ in range(3)]
    S["fingD"] = empty(LEJOS)
    box((2.4, 1.0, 0.8), (0, 0, 0.55), SKIN, S["fingD"])
    for k in range(8): cyl(0.1, 1.0, (-0.875 + 0.25 * k, 0, 0.15), SKIN_D, S["fingD"], rot=(math.pi / 2, 0, 0))
    join_static([cam, S["ph"], lock, S["keys"], S["fing"], S["fing2"], S["plates"], S["chg"], skin, S["air"], S["cover"], S["pxd"], S["pxl"],
                 S["mdots"], S["mring"], S["medges"], S["ndots"], S["nedges"], S["pix"], S["rays"], S["us"], S["fingD"]])
    return sc, S

def hide_bar(o): bar_set(o, LEJOS, LEJOS + Vector((0, 0, 0.01)))

def put_finger(o, press, tilt=0.0, yaw=0.0, lift=0.7):
    """dedo sobre el sensor: press 0 (arriba) … 1 (apoyado)"""
    o.location = LA + SEN + Vector((0, 0.02, 0.12 + lift * (1 - press)))
    o.rotation_euler = (math.radians(28) + tilt, 0, yaw)

def pose(t, S):
    # ---------- A: dedo y pantalla ----------
    scr = SCR_OFF; ring = RING; locked = True
    fp = None
    if t < T("cómo lee"):
        fp = seg(t, 0.0, 0.55); ring = RING_ON if t > 0.5 else RING
        scr = SCR_LOCK if t > 0.5 else SCR_OFF
        if t > T("sabe que"): scr = SCR_OK; locked = False
        fp *= 1 - seg(t, T("sabe que") + 0.4, T("cómo lee"))
        put_finger(S["fing"], fp)
    elif T("cuando vuelves") <= t < T("compara"):
        fp = seg(t, T("cuando vuelves"), T("tocar", fin=True)); put_finger(S["fing"], fp, yaw=0.25); ring = RING_ON if fp > 0.9 else RING; scr = SCR_LOCK
    elif T("se desbloquea") - 0.15 <= t < T("y aquí viene"):
        put_finger(S["fing"], 1 - seg(t, T("se desbloquea") + 0.3, T("y aquí viene")), yaw=0.25); scr = SCR_OK; locked = False; ring = RING_ON
    elif T("y para que") <= t < T("en los móviles"):
        a = T("tras cinco"); k = max(0, min(4, int((t - a) / 0.42)))
        ph = ((t - a) / 0.42) % 1.0 if t >= a else 0.0
        put_finger(S["fing2"], math.sin(math.pi * ph) if T("tras cinco") <= t < T("el código") else 0.0, yaw=0.4)
        scr = SCR_BAD if (t >= a and ph > 0.4 and t < T("el código")) else SCR_LOCK
        S["fing"].location = LEJOS
    else: S["fing"].location = LEJOS
    if not (T("y para que") <= t < T("en los móviles")): S["fing2"].location = LEJOS
    if fp is None and not (T("y para que") <= t < T("en los móviles")): S["fing"].location = LEJOS
    set_color(S["scr"], scr); set_color(S["ring"], ring)
    S["lock"].location = LA + Vector((0, 0.3, 0.1)) if t < T("cómo lee") or t >= T("cuando vuelves") else LEJOS
    S["shackle"].location = Vector((0, 0, 0.07 + (0.04 if not locked else 0)))
    S["shackle"].rotation_euler = (0, 0, 0.0); S["shackle"].rotation_euler = (math.pi / 2, (0 if locked else 0.5), 0)
    showk = T("el código") <= t < T("en los móviles")
    for k, o in enumerate(S["keys"]):
        if showk:
            r, c = divmod(k, 3); o.location = LA + Vector((-0.2 + 0.2 * c, 0.15 - 0.17 * r, 0.096))
            o.scale = (seg(t, T("el código") + 0.05 * k, T("el código") + 0.05 * k + 0.25),) * 3
        else: o.location = LEJOS
    # ---------- B: corte ----------
    dz = 1.5 * (1 - seg(t, T("tu huella"), T("tiene crestas")))
    S["skin"].location = LB + Vector((0, 0, dz))
    for k, a in enumerate(S["air"]):
        if T("y valles") <= t < T("así que cada") + 2.5:
            x = (RX[k] + RX[k + 1]) / 2; a.location = LB + Vector((x + 0.03 * math.sin(t * 3 + k), -0.42, 0.33 + 0.03 * math.sin(t * 4 + k)))
            a.scale = (seg(t, T("un poquito"), T("aire", fin=True)),) * 3
        else: a.location = LEJOS
    # carga de cada placa
    def charge(x, t):
        d = min(abs(x - r) for r in RX); under = math.exp(-(d / 0.13) ** 2)
        c = 1.0 - (0.7 * under + 0.05 * (1 - under)) * seg(t, T("donde toca"), T("casi nada", fin=True))
        return c
    for k, (x, b, p) in enumerate(zip(PX, S["chg"], S["plates"])):
        on = seg(t, T("guarda una"), T("eléctrica", fin=True))
        if on > 0.01 and t < T("un sensor"):
            c = charge(x, t); b0 = LB + Vector((x, -0.25, -0.06)); bar_set(b, b0, b0 - Vector((0, 0, 0.9 * c * on)))
        else: hide_bar(b)
        px = seg(t, T("así que cada"), T("es un píxel", fin=True))
        c = charge(x, t + 100); col = DARKPX if c < 0.6 else LIGHTPX
        set_color(p, tuple(mix(PLATE[i], col[i], px) for i in range(3))); set_color(b, tuple(mix(CHG[i], col[i], px) for i in range(3)))
    # ---------- C: rejilla y mapas ----------
    rev = seg(t, T("un sensor"), T("píxeles", fin=True))
    grid_on = T("un sensor") <= t < T("con esos puntos") + 0.8 or T("y aquí viene") <= t < T("y para que")
    fade = seg(t, T("con esos puntos"), T("con esos puntos") + 0.8)
    for o in (S["pxd"], S["pxl"]):
        o.location = LC + Vector((0, 0, 0.02 - 0.2 * fade)) if grid_on else LEJOS
    if t < T("pero tu móvil") and rev < 1:
        h = (NG * CS + 0.4) * (1 - rev) + 0.01; S["cover"].scale = (NG * CS + 0.4, h, 1)
        S["cover"].location = LC + Vector((0, -NG * CS / 2 - 0.2 + (NG * CS + 0.2) - h / 2 + 0.2, 0.06))
    else: S["cover"].location = LEJOS
    # puntos guardados (rojo)
    a0 = T("busca dónde")
    show_m = a0 <= t < T("y para que")
    for k, ((u, v), d, rg) in enumerate(zip(MIN, S["mdots"], S["mring"])):
        app = seg(t, a0 + 0.18 * k, a0 + 0.18 * k + 0.3)
        if show_m and app > 0:
            p = mpos(u, v); d.location = p + Vector((0, 0, 0.1)); d.scale = (app,) * 3
            if t < T("con esos puntos"): rg.location = p + Vector((0, 0, 0.05)); rg.scale = (app,) * 3
            else: rg.location = LEJOS
            set_color(d, RED)
        else: d.location = LEJOS; rg.location = LEJOS
    for (i, j), e in zip(EDGES, S["medges"]):
        u = seg(t, T("dibuja un mapa") - 0.3, T("dibuja un mapa") + 0.6)
        if show_m and u > 0 and t >= T("con esos"):
            p0 = mpos(*MIN[i]) + Vector((0, 0, 0.1)); p1 = mpos(*MIN[j]) + Vector((0, 0, 0.1)); bar_set(e, p0, p0.lerp(p1, u))
        else: hide_bar(e)
    # mapa nuevo (azul): llega girado y se encaja
    a0 = T("compara")
    newm = (a0 <= t < T("se desbloquea")) or (T("el sensor no") <= t < T("y para que"))
    if a0 <= t < T("se desbloquea"):
        rot = 0.35 * (1 - seg(t, a0 + 0.3, T("dos mapas", fin=True) + 0.3)); off = (2.0 * (1 - seg(t, a0, a0 + 0.6)), 0)
        jit = 0.06
    else:
        rot = 0.12 + 0.04 * math.sin(t * 2); off = (0.15, 0.1); jit = 0.1
        if t >= T("otra persona"): rot = 0.5; off = (0.4, -0.3); jit = 0.5
    for k, ((u, v), d) in enumerate(zip(MIN, S["ndots"])):
        if newm:
            j = Vector((jit * math.sin(k * 2.3), jit * math.cos(k * 1.7), 0))
            d.location = mpos(u, v, rot, off) + j + Vector((0, 0, 0.18))
        else: d.location = LEJOS
    for (i, j), e in zip(EDGES, S["nedges"]):
        if newm:
            bar_set(e, S["ndots"][i].location, S["ndots"][j].location)
        else: hide_bar(e)
    # coincidencias: los puntos rojos se ponen verdes
    if T("si coinciden") <= t < T("y aquí viene"):
        nm = int(len(MIN) * seg(t, T("si coinciden"), T("puntos", 3, fin=True)))
        for k, d in enumerate(S["mdots"]):
            if k < nm: set_color(d, (0.3, 0.9, 0.45))
    # ---------- D: bajo la pantalla ----------
    a0 = T("en los móviles")
    if t >= a0:
        S["fingD"].location = LD + Vector((0, 0, 0.68 + 0.6 * (1 - seg(t, a0, a0 + 0.6))))
        lt = t < T("o un ultrasonido")
        for k, r in enumerate(S["rays"]):
            x = -0.3 + 0.1 * k; b0 = LD + Vector((x, -0.64, 0.37))
            u = seg(t, T("una luz"), T("una luz") + 0.4)
            if lt and u > 0: bar_set(r, b0, b0 + Vector((0.08 * (k - 3), 0, 0.31 * u)))
            else: hide_bar(r)
        for k, w in enumerate(S["us"]):
            u = ((t - T("o un ultrasonido")) * 1.2 + k / 3) % 1.0
            if not lt and t < T("sígueme") + 0.3:
                w.location = LD + Vector((0, -0.64, 0.37)); r = 0.05 + 0.35 * u; w.scale = (r, r, r); w.rotation_euler = (math.pi / 2, 0, 0)
            else: w.location = LEJOS
        for k, p in enumerate(S["pix"]):
            on = (t * 3 + k * 0.37) % 1.0 < 0.5
            set_color(p, (0.95, 0.4, 0.55) if on else (0.25, 0.5, 0.95))
    else:
        S["fingD"].location = LEJOS
        for r in S["rays"]: hide_bar(r)
        for w in S["us"]: w.location = LEJOS
    apply_cam(S["cam"], *camera(t))

def CAMS():
    s = LA + SEN
    B, C, D = LB, LC, LD
    return [
        (0.0, [(0, (s.x + 0.55, s.y - 0.55, s.z + 0.35), (s.x, s.y + 0.15, s.z + 0.05), 35), (T("sabe que"), (s.x + 0.6, s.y - 1.2, s.z + 0.9), (s.x, s.y + 0.4, 0.05), 32),
               (T("cómo lee"), (s.x + 0.2, s.y - 0.5, s.z + 0.5), (s.x, s.y, s.z), 36), (T("vamos a mirar"), (s.x + 0.05, s.y - 0.12, s.z + 0.12), (s.x, s.y, s.z), 40)]),
        (T("tu huella"), [(0, (B.x + 0.3, B.y - 4.6, B.z + 0.9), (B.x, 0, B.z + 0.35), 35), (T("debajo"), (B.x + 0.2, B.y - 4.4, B.z + 0.6), (B.x, 0, B.z + 0.05), 35),
                          (T("cada una es"), (B.x - 0.3, B.y - 3.4, B.z + 0.3), (B.x - 0.2, 0, B.z - 0.12), 35), (T("donde toca"), (B.x + 0.2, B.y - 4.0, B.z + 0.15), (B.x + 0.1, 0, B.z - 0.3), 35),
                          (T("así que cada"), (B.x, B.y - 4.0, B.z + 1.8), (B.x, 0.3, B.z - 0.1), 35)]),
        (T("un sensor"), [(0, (C.x, C.y - 3.5, 7.5), (C.x, C.y + 0.3, 0), 35), (T("más de siete"), (C.x, C.y - 5.5, 12.5), (C.x, C.y + 0.4, 0), 35),
                          (T("pero tu móvil"), (C.x + 0.5, C.y - 4.2, 11.0), (C.x, C.y + 0.4, 0), 35), (T("con esos puntos"), (C.x, C.y - 4.0, 11.5), (C.x, C.y + 0.4, 0), 35)]),
        (T("cuando vuelves"), [(0, (s.x + 0.5, s.y - 0.7, s.z + 0.45), (s.x, s.y + 0.1, s.z + 0.05), 35)]),
        (T("compara"), [(0, (C.x, C.y - 4.0, 11.5), (C.x, C.y + 0.4, 0), 35), (T("se desbloquea"), (C.x + 0.4, C.y - 3.8, 11.2), (C.x, C.y + 0.4, 0), 35)]),
        (T("se desbloquea") - 0.15, [(0, (s.x + 0.3, s.y - 0.9, s.z + 1.4), (0, 0.0, 0.05), 32)]),
        (T("y aquí viene"), [(0, (C.x - 0.5, C.y - 4.8, 12.0), (C.x, C.y + 0.4, 0), 35), (T("y para que"), (C.x + 0.5, C.y - 4.2, 11.0), (C.x, C.y + 0.4, 0), 35)]),
        (T("y para que"), [(0, (0.5, -1.7, 1.7), (0, -0.1, 0.05), 32), (T("el código"), (0.2, -1.2, 1.9), (0, 0.05, 0.05), 32)]),
        (T("en los móviles"), [(0, (D.x + 0.4, D.y - 2.9, 1.2), (D.x, D.y, 0.7), 35), (DUR + 1, (D.x - 0.3, D.y - 2.6, 1.0), (D.x, D.y, 0.68), 35)]),
    ]

def camera(t):
    segs = CAMS(); k = 0
    for i, (st, _) in enumerate(segs):
        if t >= st: k = i
    st, ks = segs[k]
    ks = [(st if a == 0 else a, p, q, l) for a, p, q, l in ks]
    if ks[-1][0] <= t: ks = ks + [(t + 1, ks[-1][1], ks[-1][2], ks[-1][3])]
    return cam_state(t, ks, drift=0.005)

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v)
    return {"ridge": Pj(LB + Vector((RX[2], -0.42, 0.35))), "valley": Pj(LB + Vector(((RX[3] + RX[4]) / 2, -0.42, 0.33))),
            "plate": Pj(LB + Vector((PX[6], -0.2, 0.05))), "chg_r": Pj(LB + Vector((PX[6], -0.25, -0.6))), "chg_v": Pj(LB + Vector((PX[7], -0.25, -0.6))),
            "grid": Pj(LC + Vector((0, HALF, 0))), "m0": Pj(mpos(*MIN[0])), "m1": Pj(mpos(*MIN[3])),
            "sensor": Pj(LA + SEN), "phone": Pj(LA + Vector((0, 0.3, 0.1))), "chip": Pj(LD + Vector((0, -0.63, 0.33))), "D": Pj(LD + Vector((0, -0.62, 0.5)))}

if __name__ == "__main__":
    run("huella", build, pose, anchors)
