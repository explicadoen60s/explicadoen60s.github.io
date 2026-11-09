# «¿Y si construyes un molino de viento gigante?»: una pala pasa rozando la cámara; el campo vacío y el viento frenado
# por árboles y casas; la torre sube de 80 a 160 m; el viento la tumbaría → zapata de hormigón y acero en corte bajo tierra;
# góndola y tres palas de 85 m; el rotor gira lento (15 rpm) y el generador pide 1.500 → multiplicadora en corte;
# la punta a 300 km/h; el viento cambia y la góndola gira hasta mirarlo; anemómetro: arranca a 3 m/s; a 90 km/h las palas
# se ponen de canto y el rotor frena; borrasca con molinos quietos.
import bpy, bmesh, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector, Matrix

T, DUR = cargar("aerogenerador")
SKY = (0.6, 0.74, 0.88); STORM = (0.3, 0.34, 0.4)
GRASS = (0.45, 0.66, 0.36); SOIL = (0.5, 0.37, 0.26); SOIL2 = (0.42, 0.3, 0.21); SOIL3 = (0.36, 0.26, 0.19)
WHITE = (0.94, 0.95, 0.96); WHITE2 = (0.84, 0.86, 0.88); CONC = (0.72, 0.72, 0.74); STEEL = (0.55, 0.58, 0.63)
REBAR = (0.92, 0.45, 0.15); GEN = (0.25, 0.7, 0.45); GEAR = (0.95, 0.72, 0.2); GEAR2 = (0.85, 0.55, 0.15)
WIND = (0.35, 0.7, 1.0); REDC = (0.93, 0.25, 0.22); INSIDE = (0.25, 0.27, 0.32); DARK = (0.12, 0.12, 0.14)
HUB = 16.0           # altura del buje (1 unidad = 10 m)
BL = 8.5             # pala de 85 m
HX = -0.95           # buje delante de la torre (el rotor mira hacia -X, de donde viene el viento)
LEJOS = (0, 0, -200)
YAW_F = math.radians(35)

def T_(k, n=1, fin=False): return T(k, n, fin)
K = dict(luz=T_("esa electricidad"), cons=T_("y si tuvieras"), lev=T_("vamos a levantarlo"), viento=T_("primero"), suelo=T_("cerca del suelo"),
         arb=T_("los árboles"), sube=T_("así que subes"), ochenta=T_("ochenta"), sesenta=T_("sesenta", fin=True), pero=T_("pero una torre"),
         emp=T_("con el viento"), vuelca=T_("volcaría"), bajo=T_("así que bajo"), zap=T_("zapata"), horm=T_("hormigón"), suj=T_("que la sujeta"),
         arriba=T_("arriba colocas"), palas=T_("tres palas"), hasta=T_("de hasta"), despacio=T_("pero giran"), diez=T_("entre diez"),
         elec=T_("y para hacer"), gen=T_("el generador"), mil=T_("mil quinientas"), caja=T_("en la caja"), mult=T_("pones una multiplicadora"),
         eng=T_("engranajes"), lenta=T_("cada vuelta lenta"), cur=T_("y aquí viene"), aunque=T_("aunque las palas"), punta=T_("la punta va"),
         tres00=T_("trescientos"), cambia=T_("pero el viento cambia"), gira=T_("así que la caja"), frente=T_("hasta mirar"),
         tres=T_("con unos tres"), arranca=T_("el molino arranca"), sopla=T_("pero si sopla"), noventa=T_("a unos noventa"),
         romper=T_("podría romperse"), canto=T_("pone las palas"), frena=T_("frena y"), poreso=T_("por eso"), borrasca=T_("en plena borrasca"),
         quietos=T_("ves molinos"), sig=T_("sígueme"))

# ---------------- geometría ----------------
def mesh_obj(name, verts, faces, color, smooth=False, unique=False, parent=None):
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.update()
    o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o)
    return setup(o, color, parent, smooth, unique)

def blade_mesh(L, color, parent=None, n=14):
    """pala a lo largo de +Z local; cuerda en Y (plano del rotor), grosor en X (dirección del viento)"""
    secs = [(0.0, 0.13, 0.13, 0), (0.07, 0.14, 0.13, 0), (0.17, 0.46, 0.13, 0.08), (0.35, 0.40, 0.08, 0.06), (0.6, 0.27, 0.05, 0.03),
            (0.85, 0.15, 0.03, 0.01), (1.0, 0.05, 0.012, 0)]
    vs, fs = [], []
    for r, c, th, off in secs:
        for k in range(n):
            a = math.tau * k / n
            vs.append((th / 2 * math.sin(a), c / 2 * math.cos(a) + off, r * L))
    for i in range(len(secs) - 1):
        for k in range(n):
            a, b = i * n + k, i * n + (k + 1) % n
            fs.append((a, b, b + n, a + n))
    fs.append(tuple(reversed(range(n)))); fs.append(tuple(range((len(secs) - 1) * n, len(secs) * n)))
    return mesh_obj("pala", vs, fs, color, smooth=True, parent=parent)

def revolve_half(profile, color, a0=0.0, a1=math.pi, n=24, loc=(0, 0, 0), unique=False):
    """revoluciona un perfil (r, z) entre a0 y a1 (media pieza y>=0) y cierra las dos caras del corte"""
    vs, fs = [], []; m = len(profile)
    for j in range(n + 1):
        a = mix(a0, a1, j / n)
        for r, z in profile: vs.append((r * math.cos(a), r * math.sin(a), z))
    for j in range(n):
        for i in range(m - 1):
            p = j * m + i; fs.append((p, p + 1, p + 1 + m, p + m))
    fs.append(tuple(range(m))); fs.append(tuple(reversed(range(n * m, n * m + m))))
    o = mesh_obj("rev", vs, fs, color, unique=unique); o.location = loc; return o

def cone(r1, r2, depth, loc, color, rot=(0, 0, 0), parent=None, unique=False, v=24):
    bpy.ops.mesh.primitive_cone_add(radius1=r1, radius2=r2, depth=depth, location=loc, rotation=rot, vertices=v)
    return setup(bpy.context.object, color, parent, True, unique)

def tower_obj(color):
    bpy.ops.mesh.primitive_cone_add(radius1=0.26, radius2=0.16, depth=1, location=(0, 0, 0), vertices=32); o = bpy.context.object
    for vv in o.data.vertices: vv.co.z += 0.5
    return setup(o, color, smooth=True)

def arrow3d(col, r=0.07, head=0.22):
    e = empty(LEJOS)
    sh = bar_obj(col, r, parent=e, unique=False)
    hd = cone(head, 0, head * 2.0, (0, 0, 0), col, parent=e)
    return {"e": e, "sh": sh, "hd": hd}

def arrow_set(a, p0, p1):
    p0, p1 = Vector(p0), Vector(p1); d = p1 - p0; L = d.length
    if L < 0.05: a["e"].location = LEJOS; return
    a["e"].location = (0, 0, 0); hl = a["hd"].dimensions.z
    bar_set(a["sh"], p0, p1 - d.normalized() * hl * 0.9)
    a["hd"].location = p1 - d.normalized() * hl * 0.5
    a["hd"].rotation_mode = 'QUATERNION'; a["hd"].rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())

def gear(R, depth, teeth, color, parent, loc):
    """engranaje con el eje a lo largo de X local"""
    e = empty(loc, parent=parent)
    cyl(R, depth, (0, 0, 0), color, parent=e, rot=(0, math.pi / 2, 0), v=max(16, teeth * 2))
    tw = 2 * math.pi * R / teeth * 0.5
    for k in range(teeth):
        a = math.tau * k / teeth
        box((depth, tw, R * 0.22), (0, (R + R * 0.08) * math.cos(a), (R + R * 0.08) * math.sin(a)), color, parent=e, rot=(a - math.pi / 2, 0, 0))
    box((depth * 1.05, R * 0.35, R * 0.08), (0, 0, R * 0.55), DARK, parent=e)     # marca para que se vea girar
    return e

def small_turbine(loc, s=1.0):
    """molino del fondo: torre fija; cabeza (yaw) y rotor (giro) dinámicos"""
    x, y = loc
    t = tower_obj(WHITE); t.location = (x, y, 0); t.scale = (s, s, HUB * s)
    yaw = empty((x, y, HUB * s)); yaw.scale = (s, s, s)
    box((1.4, 0.42, 0.45), (0.1, 0, 0.1), WHITE, parent=yaw)
    rot = empty((HX, 0, 0.1), parent=yaw)
    sph(0.26, (-0.15, 0, 0), WHITE, parent=rot, scale=(1.4, 1, 1))
    pit = []
    for k in range(3):
        p = empty((0, 0, 0), parent=rot); p.rotation_euler = (math.tau * k / 3, 0, 0)
        pp = empty((0, 0, 0), parent=p); blade_mesh(BL, WHITE, parent=pp); pit.append(pp)
    return {"yaw": yaw, "rot": rot, "pit": pit}

def build():
    sc, cam = scene_setup(world=SKY, shadow=0.3)
    S = {"cam": cam, "world": sc.world}
    rng = random.Random(4)
    # terreno en corte: todo en y>=0, la cara frontal (y=0) es el corte
    box((120, 60, 0.08), (0, 30, -0.04), GRASS)
    box((120, 60, 0.5), (0, 30, -0.33), SOIL)
    box((120, 60, 1.0), (0, 30, -1.08), SOIL2)
    box((120, 60, 2.5), (0, 30, -2.83), SOIL3)
    for k in range(70):
        x, z = rng.uniform(-40, 40), rng.uniform(-3.8, -0.4)
        if abs(x) < 2.2: continue
        sph(rng.uniform(0.05, 0.16), (x, 0.0, z), (0.6, 0.5, 0.4), scale=(1.5, 0.2, 1))
    # árboles y casas
    for k in range(70):
        x, y = rng.uniform(-45, 45), rng.uniform(1.2, 40)
        if abs(x) < 3 and y < 5: continue
        h = rng.uniform(0.6, 1.3)
        cyl(0.07, h * 0.5, (x, y, h * 0.25), (0.42, 0.3, 0.2), v=8)
        sph(h * 0.42, (x, y, h * 0.65), rng.choice([(0.3, 0.55, 0.28), (0.36, 0.6, 0.3), (0.26, 0.48, 0.26)]), seg=12)
    for k in range(18):
        x, y = rng.uniform(-30, 30), rng.uniform(2, 30)
        if abs(x) < 4 and y < 6: continue
        rz = rng.uniform(0, math.pi)
        box((1.0, 0.8, 0.6), (x, y, 0.3), (0.95, 0.9, 0.82), rot=(0, 0, rz))
        r = box((1.1, 0.62, 0.62), (x, y, 0.62), (0.8, 0.35, 0.25), rot=(math.pi / 4, 0, rz)); r.scale = (1.1, 0.62, 0.62)
    # molinos del fondo
    S["bg"] = [small_turbine(p, s) for p, s in (((-22, 26), 0.9), ((16, 32), 0.9), ((34, 22), 0.85), ((-40, 40), 0.8))]
    # zapata en corte (media pieza delante de la cara del terreno) y el hoyo excavado
    S["hoyo"] = box((2.9, 0.02, 0.85), (0, -0.006, -0.38), (0.18, 0.13, 0.1), unique=True)
    prof = [(0, -0.78), (1.35, -0.78), (1.35, -0.5), (0.48, -0.2), (0.48, 0.03), (0, 0.03)]
    S["zap"] = revolve_half(prof, CONC, a0=math.pi, a1=2 * math.pi, loc=(0, 0.02, 0), unique=True)
    S["zap"].scale = (1, 0.02, 1)             # solo se ve la cara del corte
    S["rebar"] = []
    for z in (-0.7, -0.58):
        S["rebar"].append(bar_obj(REBAR, 0.018, unique=True)); S["rebar"][-1]["seg"] = (-1.27, z, 1.27, z)
    for xx in (-1.15, -0.9, -0.65, -0.4, -0.15, 0.15, 0.4, 0.65, 0.9, 1.15):
        S["rebar"].append(bar_obj(REBAR, 0.015, unique=True)); S["rebar"][-1]["seg"] = (xx, -0.74, xx, -0.54)
    for xx in (-0.38, -0.2, 0.2, 0.38):
        S["rebar"].append(bar_obj(REBAR, 0.015, unique=True)); S["rebar"][-1]["seg"] = (xx, -0.72, xx, 0.0)
    S["pernos"] = [cyl(0.02, 0.5, (0, 0, 0), STEEL, unique=True) for _ in range(6)]
    # torre
    S["torre"] = tower_obj(WHITE)
    S["regla"] = box((0.12, 0.12, 1), (1.5, -0.4, 0.5), (1.0, 0.82, 0.16), unique=True)
    S["ticks"] = [box((0.35, 0.08, 0.06), LEJOS, (1.0, 0.82, 0.16), unique=True) for _ in range(17)]
    # cabeza: góndola + rotor + multiplicadora + generador + anemómetro
    yaw = empty((0, 0, HUB)); S["yaw"] = yaw
    S["shell"] = sh = empty((0, 0, 0), parent=yaw)
    rounded = box((1.6, 0.48, 0.66), (0.15, 0, 0.17), WHITE, parent=sh)
    box((0.3, 0.3, 0.5), (0, 0, -0.15), WHITE2, parent=sh)            # unión con la torre
    # góndola en corte (sin la pared delantera): suelo, techo, pared de atrás, laterales
    S["shellc"] = shc = empty(LEJOS, parent=yaw)
    box((1.6, 0.48, 0.03), (0.15, 0, -0.15), WHITE2, parent=shc)
    box((1.6, 0.03, 0.66), (0.15, 0.225, 0.17), INSIDE, parent=shc)
    box((1.6, 0.48, 0.03), (0.15, 0, 0.49), WHITE2, parent=shc)
    box((0.03, 0.48, 0.66), (0.94, 0, 0.17), WHITE2, parent=shc)
    box((0.03, 0.48, 0.66), (-0.64, 0, 0.17), WHITE2, parent=shc)
    box((0.3, 0.3, 0.5), (0, 0, -0.15), WHITE2, parent=shc)
    # tren de potencia (dentro)
    S["eje_lento"] = el = empty((HX, 0, 0.1), parent=yaw)
    cyl(0.06, 0.95, (0.5, 0, 0), STEEL, parent=el, rot=(0, math.pi / 2, 0))
    S["g1"] = gear(0.16, 0.08, 22, GEAR, el, (0.85, 0, 0))
    S["eje_med"] = em = empty((HX + 0.85, 0, 0.1 + 0.205), parent=yaw)
    cyl(0.03, 0.42, (0.15, 0, 0), STEEL, parent=em, rot=(0, math.pi / 2, 0))
    gear(0.045, 0.08, 7, GEAR2, em, (0.0, 0, 0))
    gear(0.13, 0.07, 18, GEAR, em, (0.3, 0, 0))
    S["eje_rap"] = er = empty((HX + 1.15, 0, 0.1 + 0.205 - 0.175), parent=yaw)
    cyl(0.025, 0.55, (0.3, 0, 0), STEEL, parent=er, rot=(0, math.pi / 2, 0))
    gear(0.04, 0.07, 7, GEAR2, er, (0.0, 0, 0))
    cyl(0.08, 0.015, (0.22, 0, 0), (0.7, 0.7, 0.72), parent=er, rot=(0, math.pi / 2, 0))          # disco de freno
    S["rotgen"] = er
    S["gen"] = cyl(0.13, 0.32, (HX + 1.15 + 0.5, 0, 0.13), GEN, parent=yaw, rot=(0, math.pi / 2, 0), unique=True)
    for k in range(6):
        a = math.tau * k / 6
        box((0.06, 0.012, 0.11), (0.48, 0.1 * math.cos(a), 0.1 * math.sin(a)), (0.95, 0.95, 0.95), parent=er, rot=(a, 0, 0))
    S["pinza"] = box((0.04, 0.05, 0.06), (HX + 1.15 + 0.22, 0, 0.13 - 0.09), (0.3, 0.3, 0.32), parent=yaw, unique=True)
    # anemómetro y veleta en el techo
    S["anem"] = an = empty((0.75, 0.0, 0.57), parent=yaw)
    cyl(0.012, 0.1, (0, 0, -0.06), STEEL, parent=an)
    for k in range(3):
        a = math.tau * k / 3
        bar = box((0.12, 0.012, 0.012), (0.06 * math.cos(a), 0.06 * math.sin(a), 0), STEEL, parent=an, rot=(0, 0, a))
        sph(0.03, (0.12 * math.cos(a), 0.12 * math.sin(a), 0), (0.95, 0.3, 0.25), parent=an, scale=(1, 0.6, 1))
    # rotor
    S["rot"] = rot = empty((HX, 0, 0.1), parent=yaw)
    sph(0.3, (-0.18, 0, 0), WHITE, parent=rot, scale=(1.5, 1, 1))
    cyl(0.29, 0.3, (0.05, 0, 0), WHITE2, parent=rot, rot=(0, math.pi / 2, 0))
    S["pit"] = []; S["pal"] = []
    for k in range(3):
        p = empty((0, 0, 0), parent=rot); p.rotation_euler = (math.tau * k / 3, 0, 0)
        pp = empty((0, 0, 0.0), parent=p)
        S["pal"].append(blade_mesh(BL, WHITE, parent=pp)); S["pit"].append(pp)
    S["estela"] = [sph(0.13, LEJOS, (1.0, 0.82, 0.16), seg=8, unique=True) for _ in range(24)]
    S["regla_pala"] = bar_obj((1.0, 0.82, 0.16), 0.05, unique=True)
    # viento: flechas por alturas, estelas que cruzan, flecha de empuje
    S["fl"] = [arrow3d(WIND, 0.08 + 0.02 * k, 0.25 + 0.05 * k) for k in range(5)]
    S["empuje"] = arrow3d(REDC, 0.18, 0.5)
    S["sujeta"] = [arrow3d((0.3, 0.85, 0.45), 0.06, 0.16) for _ in range(2)]
    S["str"] = [bar_obj((0.97, 0.98, 1.0), 0.03, unique=True) for _ in range(46)]
    S["strp"] = [(rng.uniform(0, 1), rng.uniform(-4, 8), rng.uniform(0.3, 22)) for _ in range(46)]
    S["lluvia"] = [bar_obj((0.75, 0.82, 0.92), 0.02, unique=True) for _ in range(40)]
    S["lluvp"] = [(rng.uniform(-14, 10), rng.uniform(-14, 4), rng.uniform(0, 1)) for _ in range(40)]
    S["nubes"] = [sph(rng.uniform(3, 5), LEJOS, (0.56, 0.59, 0.64), scale=(1.8, 1, 0.55), unique=True) for _ in range(6)]
    S["nubp"] = [(rng.uniform(-30, 30), rng.uniform(10, 40), rng.uniform(26, 32)) for _ in range(6)]
    dyn = [cam, S["hoyo"], S["zap"], S["rebar"], S["pernos"], S["torre"], S["regla"], S["ticks"], yaw, S["estela"], S["regla_pala"],
           [a["e"] for a in S["fl"]], S["empuje"]["e"], [a["e"] for a in S["sujeta"]], S["str"], S["lluvia"], S["nubes"]]
    for b in S["bg"]: dyn.append(b["yaw"])
    join_static(dyn)
    return sc, S

# ---------------- tiempo ----------------
def omega(t):
    return keyed(t, [(0, 2.4), (1.2, 2.4), (2.4, 1.7), (K["cons"], 1.7), (K["lev"], 0.0), (K["despacio"] - 0.4, 0.0), (K["diez"], 1.57), (K["cambia"], 1.57),
                     (K["gira"] + 0.3, 0.0), (K["tres"] + 1.0, 0.0), (K["arranca"] + 0.6, 1.3), (K["noventa"] + 1.0, 2.2),
                     (K["canto"] + 0.2, 2.2), (K["frena"] + 0.5, 0.0)])
_TH = {}
def theta(t):
    f = int(round(t * 30))
    if f in _TH: return _TH[f]
    th = 2.356 - 2.4 * 0.12; dt = 1 / 30
    for i in range(f): th += omega(i * dt) * dt
    _TH[f] = th; return th

def wind_ms(t):
    return keyed(t, [(0, 9), (K["cambia"], 9), (K["gira"], 2.0), (K["tres"], 1.5), (K["arranca"], 3.0), (K["sopla"], 4), (K["romper"], 25), (DUR, 25)])

def wind_dir(t):
    a = keyed(t, [(0, 0.0), (K["cambia"], 0.0), (K["cambia"] + 1.2, YAW_F), (DUR, YAW_F)])
    return Vector((math.cos(a), math.sin(a), 0))

def tower_h(t):
    if t < K["lev"]: return HUB
    if t < K["sube"]: return HUB * (1 - seg(t, K["lev"], K["lev"] + 0.9))
    return 8.0 * seg(t, K["ochenta"] - 0.4, K["ochenta"] + 0.9) + 8.0 * seg(t, K["sesenta"] - 1.3, K["sesenta"])

def pose(t, S):
    k = K
    # cielo
    storm = seg(t, k["romper"] - 1.0, k["poreso"] + 0.5)
    S["world"].color = lin(tuple(mix(a, b, storm) for a, b in zip(SKY, STORM)))
    # ---- construcción ----
    gone = seg(t, k["lev"], k["lev"] + 0.9) * (1 - seg(t, k["sube"] - 0.3, k["sube"]))
    th = tower_h(t)
    S["torre"].scale = (1, 1, max(0.001, th - 0.3))
    tilt = math.radians(7) * seg(t, k["emp"] + 0.3, k["vuelca"] + 0.6) * (1 - seg(t, k["bajo"] + 0.2, k["bajo"] + 0.9))
    tilt += math.radians(0.6) * math.sin(t * 5) * seg(t, k["emp"], k["vuelca"]) * (1 - seg(t, k["bajo"], k["bajo"] + 0.5))
    S["torre"].rotation_euler = (0, tilt, 0)
    # regla de altura 80 → 160 m
    rp = win01(t, k["sube"], k["pero"], 0.4, 0.4)
    if rp > 0:
        S["regla"].location = (1.3, -0.5, th / 2); S["regla"].scale = (0.12 * rp, 0.12 * rp, max(0.01, th))
        for i, o in enumerate(S["ticks"]):
            z = i * 1.0
            o.location = (1.3 + 0.12, -0.5, z) if z <= th + 0.01 else LEJOS; o.scale = (0.35 * rp * (1.6 if i % 4 == 0 else 1), 0.08 * rp, 0.06 * rp)
    else:
        S["regla"].location = LEJOS
        for o in S["ticks"]: o.location = LEJOS
    # zapata: hoyo → ferralla → hormigón
    zap_on = t < k["lev"] + 0.5 or t > k["bajo"] + 0.3
    hoyo = seg(t, k["bajo"] + 0.3, k["bajo"] + 1.0) * (1 - seg(t, k["suj"] + 0.2, k["suj"] + 0.6)) if t > k["sube"] else 0.0
    S["hoyo"].scale = (2.9, 0.02, max(0.001, 0.85 * hoyo))
    reb = 1.0 if t < k["lev"] + 0.5 else seg(t, k["zap"] - 0.2, k["zap"] + 0.8)
    for o in S["rebar"]:
        x0, z0, x1, z1 = o["seg"]
        if reb > 0.01 and zap_on: bar_set(o, (x0, -0.05, z0), (mix(x0, x1, reb), -0.05, mix(z0, z1, reb)))
        else: o.location = LEJOS
    con = 1.0 if t < k["lev"] + 0.5 else seg(t, k["horm"] + 0.2, k["suj"])
    if zap_on and con > 0.01:
        S["zap"].location = (0, -0.01, -0.78 * (1 - con)); S["zap"].scale = (1, 0.02, max(0.01, con))
    else: S["zap"].location = LEJOS
    for i, o in enumerate(S["pernos"]):
        x = (-0.36, -0.24, -0.12, 0.12, 0.24, 0.36)[i]
        o.location = (x, -0.04, -0.2) if zap_on and reb > 0.5 else LEJOS
    # cabeza
    head = 1.0 if t < k["lev"] else (0.0 if t < k["arriba"] else 1.0)
    drop = seg(t, k["arriba"] - 0.1, k["arriba"] + 0.8) if t > k["arriba"] - 0.2 else 1.0
    if t < k["lev"] + 0.6:
        drop = 1.0 - seg(t, k["lev"], k["lev"] + 0.6); head = 1.0
    yaw_a = keyed(t, [(0, 0.0), (k["gira"], 0.0), (k["frente"] + 0.6, YAW_F), (DUR, YAW_F)])
    if head > 0 and drop > 0.001:
        S["yaw"].location = (0, 0, th + 4.0 * (1 - drop)); S["yaw"].scale = (drop, drop, drop) if t < k["lev"] + 0.6 else (1, 1, 1)
        S["yaw"].rotation_euler = (0, 0, yaw_a)
    else: S["yaw"].location = LEJOS
    cut = win01(t, k["caja"] - 0.3, k["cur"] + 0.2, 0.2, 0.2) > 0.5
    S["shell"].location = LEJOS if cut else (0, 0, 0); S["shellc"].location = (0, 0, 0) if cut else LEJOS
    # palas: aparecen una a una
    th_r = theta(t)
    S["rot"].rotation_euler = (th_r, 0, 0)
    pitch = math.radians(88) * seg(t, k["canto"] + 0.1, k["canto"] + 1.2)
    for i, pp in enumerate(S["pit"]):
        if t < k["lev"] + 0.6: s = 1.0
        else: s = seg(t, k["palas"] - 0.3 + 0.45 * i, k["palas"] + 0.2 + 0.45 * i)
        pp.scale = (1, 1, max(0.001, s)) if s > 0 else (0.001, 0.001, 0.001)
        pp.rotation_euler = (0, 0, pitch)
    # tren de potencia: rápido de verdad (el lento a la vez que el rotor)
    S["eje_lento"].rotation_euler = (th_r, 0, 0)
    S["eje_med"].rotation_euler = (-th_r * 3.5, 0, 0)
    S["eje_rap"].rotation_euler = (th_r * 3.5 * 3.25, 0, 0)
    brake = win01(t, k["frena"] - 0.2, k["poreso"] + 0.6, 0.2, 0.4)
    set_color(S["pinza"], tuple(mix(a, b, brake) for a, b in zip((0.3, 0.3, 0.32), (1.0, 0.25, 0.1))))
    gl = win01(t, k["mil"] + 0.2, k["cur"], 0.3, 0.3)
    set_color(S["gen"], tuple(mix(a, b, gl * (0.5 + 0.5 * math.sin(t * 10))) for a, b in zip(GEN, (0.5, 1.0, 0.6))))
    # anemómetro: gira según el viento
    S["anem"].rotation_euler = (0, 0, sum_wind(t))
    # estela de la punta
    tip_on = win01(t, k["punta"] - 0.4, k["cambia"] - 0.1, 0.2, 0.2) > 0.5
    for j, o in enumerate(S["estela"]):
        if tip_on:
            b, i = divmod(j, 8)
            a = th_r + b * math.tau / 3 - 0.05 * (i + 1)
            p = S["yaw"].matrix_world @ Vector((HX, -BL * math.sin(a) * 0.985, 0.1 + BL * math.cos(a) * 0.985))
            o.location = p; s = 1 - i / 8; o.scale = (s, s, s)
        else: o.location = LEJOS
    # regla de la pala de 85 m (sobre la pala 0)
    if win01(t, k["hasta"] - 0.1, k["despacio"] + 0.2) > 0 and t > k["palas"]:
        M = S["pal"][0].matrix_world
        bar_set(S["regla_pala"], M @ Vector((-0.25, 0, 0.15)), M @ Vector((-0.25, 0, 0.15 + (BL - 0.15) * seg(t, k["hasta"] - 0.1, k["hasta"] + 0.8))))
    else: S["regla_pala"].location = LEJOS
    # flechas del viento por alturas (cerca del suelo, cortas)
    fp = win01(t, k["viento"], k["sube"] + 0.3, 0.4, 0.4)
    for i, a in enumerate(S["fl"]):
        z = (0.6, 2.0, 4.0, 7.0, 10.5)[i]; L = (1.0, 2.3, 3.6, 4.6, 5.2)[i]
        if fp > 0.01:
            wob = 0.25 * math.sin(t * 7 + i) if i == 0 else 0.1 * math.sin(t * 3 + i)
            x0 = -9.5 + 0.3 * math.sin(t * 2 + i)
            g = seg(t, k["viento"] + 0.2 * i, k["viento"] + 0.6 + 0.2 * i) * fp
            arrow_set(a, (x0, -1.0, z), (x0 + L * g + wob, -1.0, z))
        else: a["e"].location = LEJOS
    # empuje del viento arriba y anclaje
    ep = win01(t, k["emp"], k["bajo"] + 0.4, 0.3, 0.3)
    if ep > 0.01: arrow_set(S["empuje"], (-6.5, -0.8, th - 0.6), (-6.5 + 5.6 * ep, -0.8, th - 0.6))
    else: S["empuje"]["e"].location = LEJOS
    sp = win01(t, k["suj"] - 0.2, k["arriba"] - 0.1, 0.3, 0.3)
    for i, a in enumerate(S["sujeta"]):
        x = (-1.0, 1.0)[i]
        if sp > 0.01: arrow_set(a, (x, -0.12, -0.15), (x, -0.12, -0.15 - 0.55 * sp))
        else: a["e"].location = LEJOS
    # estelas de viento
    wd = wind_dir(t); perp = Vector((-wd.y, wd.x, 0)); ws_ = wind_ms(t)
    vis_w = 1.0 if (t < k["lev"] or t > k["viento"] - 0.3) else 0.0
    if k["bajo"] < t < k["arriba"]: vis_w = 0.0
    ph = sum_wind(t) * 0.06
    apply_cam(S["cam"], *cam_state(t, CAM(), drift=0.05))
    for i, (o, (u0, y0, z0)) in enumerate(zip(S["str"], S["strp"])):
        if vis_w and (i < 22 or ws_ > 6):
            slow = 0.35 + 0.65 * min(1, z0 / 10)
            u = (u0 + ph * slow * 0.6) % 1.0
            c = Vector((0, 0, z0)) + wd * (-22 + 44 * u) + perp * y0
            L = 0.5 + 0.08 * ws_ * slow
            if (c - S["cam"].location).length < 4.0: o.location = LEJOS; continue
            bar_set(o, c, c + wd * L)
        else: o.location = LEJOS
    # lluvia y nubes
    for i, (o, (x, y, u0)) in enumerate(zip(S["lluvia"], S["lluvp"])):
        if storm > 0.3:
            cp = S["cam"].location
            u = (u0 + t * 1.6) % 1.0; z = 14 - 14 * u
            p = Vector((cp.x + x * 0.6, cp.y + 8 + (y + 14) * 0.6, cp.z - 7 + z))
            bar_set(o, p, p + Vector((0.25, 0.1, -1.2)))
        else: o.location = LEJOS
    for o, (x, y, z) in zip(S["nubes"], S["nubp"]):
        o.location = (x + 2 * t * 0.1, y, z + 20 * (1 - storm)) if storm > 0.02 else LEJOS
    # molinos del fondo
    for j, b in enumerate(S["bg"]):
        b["yaw"].rotation_euler = (0, 0, yaw_a)
        b["rot"].rotation_euler = (theta_bg(t) * (0.9 + 0.07 * j) + j * 1.3, 0, 0)
        for pp in b["pit"]: pp.rotation_euler = (0, 0, pitch)
    apply_cam(S["cam"], *cam_state(t, CAM(), drift=0.05))

def omega_bg(t):
    return keyed(t, [(0, 1.5), (K["canto"] + 0.2, 1.5), (K["frena"] + 0.8, 0.0)])
_TB = {}
def theta_bg(t):
    f = int(round(t * 30))
    if f not in _TB:
        _TB[f] = sum(omega_bg(i / 30) for i in range(f)) / 30
    return _TB[f]

_SW = {}
def sum_wind(t):
    f = int(round(t * 30))
    if f in _SW: return _SW[f]
    s = 0.0
    for i in range(f): s += wind_ms(i / 30) * 1.2 / 30
    _SW[f] = s; return s

def V(at, off, lens=32):
    return (tuple(Vector(at) + Vector(off)), tuple(at), lens)

def CAM():
    k = K
    P = (HX - 0.1, -4.6, HUB - 4.6)                     # punto del barrido de la pala
    hubF = Vector((HX * math.cos(YAW_F), HX * math.sin(YAW_F), HUB + 0.1))
    anF = Vector((0.75 * math.cos(YAW_F), 0.75 * math.sin(YAW_F), HUB + 0.5))
    W = (-1.5, 0, 11.0)
    H0 = (HX, -1.2, HUB - 2.2)
    c = [(0.0,) + V(H0, (-6.0, -3.2, -2.2), 26), (1.0,) + V(H0, (-6.8, -4.2, -2.0), 26),
         (2.6,) + V(W, (-10, -25, -3.0), 34), (k["cons"],) + V(W, (-9, -26, -2.6), 34),
         (k["viento"],) + V((-5, 0, 6.0), (-2, -20, 0.5), 34), (k["arb"] + 1.0,) + V((-5.5, 0, 5.5), (-1, -19, 0.0), 34),
         (k["ochenta"],) + V((0.5, 0, 7.5), (-6, -28, 0.0), 34), (k["sesenta"],) + V((0.5, 0, 9.0), (-6, -31, -1.0), 34),
         (k["vuelca"],) + V((0.0, 0, 9.0), (-4, -31, -1.5), 34),
         (k["bajo"] + 0.7,) + V((0, 0, -0.3), (-0.4, -5.6, 0.7), 30), (k["bajo"] + 1.2,) + V((0, 0, -0.3), (-0.3, -5.6, 0.7), 30),
         (k["horm"],) + V((0, 0, -0.25), (0.1, -5.7, 0.75), 30), (k["suj"] + 0.2,) + V((0, 0, -0.2), (0.4, -5.8, 0.8), 30),
         (k["suj"] + 0.6,) + V((0, 0, 0.4), (0.4, -7.5, 1.2), 30),
         (k["arriba"] + 0.3,) + V((-0.6, 0, 13.5), (-6, -22, -2), 34), (k["hasta"] + 0.5,) + V((-0.8, 0, 12.0), (-7, -24, -2.2), 34),
         (k["diez"] + 0.5,) + V((-0.8, 0, 12.5), (-8, -24, -2.0), 34), (k["mil"],) + V((-0.6, 0, 13.0), (-7, -24, -1.0), 34),
         (k["caja"] - 0.2,) + V((0.0, 0, HUB), (-1.0, -6.0, 0.6), 32),
         (k["caja"] + 0.5,) + V((0.12, 0, HUB + 0.12), (-0.3, -2.9, 0.25), 32), (k["caja"] + 1.2,) + V((0.14, 0, HUB + 0.12), (-0.2, -2.9, 0.25), 32),
         (k["lenta"] + 0.5,) + V((0.18, 0, HUB + 0.12), (0.1, -3.0, 0.3), 32), (k["cur"] - 0.1,) + V((0.18, 0, HUB + 0.12), (0.2, -3.05, 0.3), 32),
         (k["cur"] + 0.4,) + V((0.0, 0, HUB), (-0.5, -7.0, 0.3), 32),
         (k["cur"] + 1.3,) + V((-1.0, 0, 12.0), (-9, -26, -2.0), 34), (k["aunque"] + 1.3,) + V((-1.0, 0, 12.0), (-10, -27, -2.0), 34),
         (k["punta"] + 0.2,) + V((HX, -1.5, 9.0), (-9.0, -6.5, -0.8), 28), (k["tres00"] + 1.0,) + V((HX, -1.5, 9.0), (-9.4, -5.8, -0.8), 28),
         (k["gira"],) + V((0, 0, 13.0), (-8, -24, 8), 34), (k["frente"] + 1.0,) + V((0, 0, 13.0), (-14, -21, 8), 34),
         (k["tres"] + 0.4,) + V(anF, (0.9, -2.2, 0.6), 30), (k["arranca"] + 0.4,) + V(anF + Vector((-0.4, 0, -0.1)), (1.4, -2.6, 0.8), 30), (k["sopla"],) + V(anF + Vector((-0.4, 0, -0.3)), (3.0, -6.0, 1.0), 32),
         (k["sopla"] + 0.6,) + V((-1, 0, 11.5), (-11, -27, -2.0), 34), (k["romper"] + 0.2,) + V((-1, 0, 11.5), (-12, -26, -2.5), 34),
         (k["canto"] + 0.3,) + V(hubF, (-3.6, -4.2, -0.6), 30), (k["frena"] + 0.3,) + V(hubF, (-3.9, -4.6, -0.6), 30),
         (k["borrasca"],) + V((3, 6, 9.5), (-10, -40, -1.5), 32), (DUR + 1.0,) + V((3, 6, 9.5), (-9, -36, -1.5), 32)]
    return c

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v)
    Y = S["yaw"].matrix_world
    tip0 = S["pal"][0].matrix_world @ Vector((0, 0, BL * 0.5))
    tips = [p.matrix_world @ Vector((0, 0, BL)) for p in S["pal"]]
    low = min(tips, key=lambda v: v.z)
    return {"top": Pj((0, 0, tower_h(t))), "regla": Pj((1.3, -0.5, tower_h(t))), "zap": Pj((0, 0, -0.45)), "torre": Pj((0, 0, 8)),
            "hub": Pj(Y @ Vector((HX - 0.3, 0, 0.1))), "pala": Pj(tip0), "tip": Pj(low), "g1": Pj(Y @ Vector((HX + 0.85, 0, 0.1))),
            "gen": Pj(Y @ Vector((HX + 1.65, 0, 0.13))), "anem": Pj(Y @ Vector((0.75, 0, 0.57))), "nac": Pj(Y @ Vector((0.15, 0, 0.4))),
            "freno": Pj(Y @ Vector((HX + 1.37, 0, 0.13))), "suelo": Pj((-6, -1, 0.6)), "alto": Pj((-6, -1, 10.5))}

if __name__ == "__main__":
    run("aerogenerador", build, pose, anchors)
