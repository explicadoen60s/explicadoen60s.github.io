# «Así funciona la baliza V16»: de noche, una mano pega la baliza en el techo del coche y empieza a destellar; los
# triángulos caen; despiece (imán, SIM); coche parado en el arcén de una autovía, una persona andando a colocar los
# triángulos mientras pasan coches; el brazo saca la baliza por la ventanilla; anillo de luz de 1 km en 360°; curva con
# un monte que tapa la luz; despiece (GPS + SIM), ondas que salen; el aviso viaja a la DGT 3.0 (no al móvil ni a la grúa),
# de ahí a un panel y a los coches conectados que frenan; repetición cada 100 s; 12 años de conexión; batería 30 min.
import bpy, math, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector

T0, DUR = cargar("v16")
_TC = {}
def T(k, n=1, fin=False):
    key = (k, n, fin)
    if key not in _TC: _TC[key] = T0(k, n, fin)
    return _TC[key]

BG = (0.04, 0.05, 0.09); GROUND = (0.07, 0.09, 0.08); ASPH = (0.17, 0.18, 0.21); LINE = (0.82, 0.82, 0.76)
CARC = (0.82, 0.84, 0.88); GLASS = (0.12, 0.16, 0.22); TYRE = (0.08, 0.08, 0.09); RIM = (0.6, 0.62, 0.66)
AMB = (1.0, 0.72, 0.08); AMB_D = (0.55, 0.38, 0.08); BLACK = (0.08, 0.08, 0.1); SKIN = (0.93, 0.72, 0.58)
SLEEVE = (0.25, 0.35, 0.6); RED = (0.92, 0.2, 0.2); BRAKE_OFF = (0.35, 0.08, 0.08); HILL = (0.1, 0.16, 0.11)
PCB = (0.15, 0.5, 0.3); SIMC = (0.95, 0.8, 0.35); CHIP = (0.12, 0.12, 0.14); PATCH = (0.82, 0.72, 0.55); BATT = (0.3, 0.55, 0.95)
SIG = (0.35, 0.85, 1.0); DGTC = (0.32, 0.42, 0.62); VEST = (1.0, 0.85, 0.15)
LEJOS = Vector((0, 3000, -3000))
RC = 60.0; Y0 = -30.0; CX = -2.0          # curva de radio 60 detrás del tramo recto; eje de la carretera en x = -2
CEN = Vector((CX - RC, Y0, 0))
S_CAR = 30.0; O_CAR = 3.5                 # coche parado en el arcén
B = Vector((1.25, 0.15, 1.525))             # baliza en el techo
DGT = Vector((62, 55, 0))
S_GANTRY = -58.0

def road(s, o=0.0):
    """punto (z=0) y rumbo en la carretera: s a lo largo, o desplazamiento lateral (+ = derecha)"""
    if s >= 0: return Vector((CX + o, Y0 + s, 0)), math.pi / 2
    a = s / RC
    return CEN + Vector(((RC + o) * math.cos(a), (RC + o) * math.sin(a), 0)), a + math.pi / 2

def place(o, s, off, z=0.0):
    p, h = road(s, off); o.location = p + Vector((0, 0, z)); o.rotation_euler = (0, 0, h - math.pi / 2)

def car(color):
    e = empty(LEJOS); ch = {}
    box((1.8, 4.4, 0.72), (0, 0, 0.68), color, e)
    box((1.6, 2.3, 0.46), (0, -0.25, 1.27), GLASS, e)
    box((1.62, 2.0, 0.05), (0, -0.25, 1.5), color, e)
    for sx in (-0.9, 0.9):
        for sy in (-1.4, 1.4):
            cyl(0.34, 0.24, (sx, sy, 0.34), TYRE, e, rot=(0, math.pi / 2, 0))
            cyl(0.18, 0.26, (sx, sy, 0.34), RIM, e, rot=(0, math.pi / 2, 0))
    for sx in (-0.6, 0.6): box((0.42, 0.06, 0.16), (sx, 2.21, 0.82), (1.0, 0.96, 0.75), e)
    ch["brake"] = [box((0.42, 0.06, 0.16), (sx, -2.21, 0.85), BRAKE_OFF, e, unique=True) for sx in (-0.6, 0.6)]
    ch["haz"] = [box((0.14, 0.08, 0.1), (sx, sy * 2.2, 0.66), AMB_D, e, unique=True) for sx in (-0.82, 0.82) for sy in (-1, 1)]
    e["n"] = len(ch); return e, ch

def ring(color, r=0.02):
    return torus(1.0, r, LEJOS, color, rot=(0, 0, 0))

def build():
    sc, cam = scene_setup(world=BG, shadow=0.3); cam.data.clip_start = 0.02
    S = {"cam": cam}
    box((900, 900, 0.1), (0, 0, -0.1), GROUND)
    # carretera: tramo recto + curva
    s = -170.0
    while s < 330:
        p, h = road(s + 2); bx = box((10.6, 4.1, 0.06), p + Vector((0, 0, -0.01)), ASPH); bx.rotation_euler = (0, 0, h - math.pi / 2)
        for o, w in ((-5.0, 0.14), (2.0, 0.14)):
            q, _ = road(s + 2, o); ln = box((w, 4.1, 0.02), q + Vector((0, 0, 0.025)), LINE); ln.rotation_euler = (0, 0, h - math.pi / 2)
        if int(s) % 12 == 0:
            q, _ = road(s + 2, -1.5); ln = box((0.14, 4.0, 0.02), q + Vector((0, 0, 0.025)), LINE); ln.rotation_euler = (0, 0, h - math.pi / 2)
        if s >= 0 and int(s) % 4 == 0:
            q, _ = road(s, 6.0); cyl(0.06, 0.8, q + Vector((0, 0, 0.4)), (0.5, 0.52, 0.55), v=8)
            g = box((0.05, 4.0, 0.3), q + Vector((-0.08, 2, 0.7)), (0.7, 0.72, 0.76))
        s += 4
    # monte en el interior de la curva
    sph(1.0, CEN + Vector((33 * math.cos(-0.8), 33 * math.sin(-0.8), 0)), HILL, scale=(21, 21, 15))
    sph(1.0, CEN + Vector((30 * math.cos(-1.25), 30 * math.sin(-1.25), 0)), HILL, scale=(16, 16, 10))
    # edificio de la DGT y antena
    box((22, 18, 26), DGT + Vector((0, 0, 13)), DGTC)
    for k in range(5):
        for j in range(4): box((2.6, 0.2, 2.6), DGT + Vector((-7.5 + j * 5, -9.05, 5 + k * 4.4)), (0.6, 0.75, 0.95))
    text3d("DGT 3.0", DGT + Vector((0, -9.2, 26.5)), 4.2, (0.95, 0.97, 1.0), rot=(math.pi / 2, 0, 0), extrude=0.3)
    cyl(0.3, 14, DGT + Vector((6, 0, 33)), (0.7, 0.72, 0.76), v=8)
    # pórtico con panel
    p, h = road(S_GANTRY); hd = h - math.pi / 2
    for o in (-6.5, 6.5):
        q, _ = road(S_GANTRY, o); cyl(0.25, 7.2, q + Vector((0, 0, 3.6)), (0.55, 0.57, 0.6), v=10)
    bm = box((13.4, 0.5, 0.5), p + Vector((0, 0, 7.0)), (0.55, 0.57, 0.6)); bm.rotation_euler = (0, 0, hd)
    pn = box((7.2, 0.3, 2.4), p + Vector((0, 0, 5.6)), (0.03, 0.03, 0.04)); pn.rotation_euler = (0, 0, hd)
    dirv = Vector((math.cos(h), math.sin(h), 0))
    S["ptext"] = text3d("COCHE PARADO", p - dirv * 0.2 + Vector((0, 0, 5.6)), 0.85, (0.06, 0.05, 0.03), rot=(math.pi / 2, 0, hd), unique=True)
    # coche protagonista
    S["car"], S["carch"] = car(CARC)
    # otros coches
    S["traffic"] = [car(c) for c in ((0.85, 0.25, 0.25), (0.25, 0.45, 0.85), (0.9, 0.9, 0.92))]
    S["conn"] = [car(c) for c in ((0.3, 0.7, 0.45), (0.95, 0.6, 0.2))]
    S["icons"] = [sph(0.45, LEJOS, AMB, unique=True) for _ in S["conn"]]
    S["approach"] = car((0.6, 0.3, 0.75))
    # baliza
    bea = empty(B); S["bea"] = bea
    S["mag"] = cyl(0.04, 0.012, (0, 0, 0.006), (0.55, 0.57, 0.62), bea)
    S["base"] = cyl(0.046, 0.022, (0, 0, 0.023), BLACK, bea)
    S["board"] = cyl(0.04, 0.004, (0, 0, 0.036), PCB, bea)
    S["sim"] = box((0.022, 0.016, 0.003), (-0.015, 0.012, 0.04), SIMC, bea)
    S["gps"] = box((0.02, 0.02, 0.006), (0.016, 0.01, 0.041), PATCH, bea)
    box((0.012, 0.012, 0.004), (0.012, -0.018, 0.04), CHIP, bea)
    S["batt"] = cyl(0.008, 0.05, (0, -0.026, 0.047), BATT, bea, rot=(0, math.pi / 2, 0))
    dome = empty((0, 0, 0.034), bea); S["dome"] = dome
    S["domem"] = cyl(0.042, 0.045, (0, 0, 0.0225), AMB_D, dome, unique=True)
    sph(0.042, (0, 0, 0.045), BLACK, dome, scale=(1, 1, 0.25))
    # brazo
    S["arm"] = [bar_obj(SLEEVE, r=0.04), bar_obj(SKIN, r=0.03)]; S["hand"] = sph(0.04, LEJOS, SKIN, scale=(0.8, 1, 1.1))
    # persona con triángulo
    per = empty(LEJOS); S["per"] = per
    cyl(0.2, 0.9, (0, 0, 0.95), VEST, per); sph(0.15, (0, 0, 1.6), SKIN, per)
    for x in (-0.1, 0.1): cyl(0.08, 0.6, (x, 0, 0.3), (0.2, 0.22, 0.3), per)
    tri = empty(LEJOS); S["tri"] = tri
    S["trim"] = []
    for k in range(3):
        a = math.radians(90 + 120 * k); b2 = math.radians(90 + 120 * (k + 1))
        p0 = Vector((0.3 * math.cos(a), 0, 0.3 * math.sin(a) + 0.18)); p1 = Vector((0.3 * math.cos(b2), 0, 0.3 * math.sin(b2) + 0.18))
        bb = bar_obj(RED, r=0.03, unique=True); bar_set(bb, p0, p1); bb.parent = tri; S["trim"].append(bb)
    S["tri2"] = empty(LEJOS)
    for k in range(3):
        a = math.radians(90 + 120 * k); b2 = math.radians(90 + 120 * (k + 1))
        bb = bar_obj(RED, r=0.03); bar_set(bb, (0.3 * math.cos(a), 0, 0.3 * math.sin(a) + 0.18), (0.3 * math.cos(b2), 0, 0.3 * math.sin(b2) + 0.18)); bb.parent = S["tri2"]
    # luz, ondas y pulsos
    S["lring"] = ring(AMB, 0.012)
    S["waves"] = [ring(SIG, 0.02) for _ in range(3)]
    S["pulse"] = [sph(2.4, LEJOS, SIG) for _ in range(3)]
    S["sat"] = empty(LEJOS)
    box((0.6, 0.6, 0.6), (0, 0, 0), (0.8, 0.8, 0.85), S["sat"]); box((2.4, 0.05, 0.7), (0, 0, 0), (0.3, 0.45, 0.85), S["sat"])
    S["satbeam"] = bar_obj(SIG, r=0.04)
    dyn = [cam, S["car"], [c for c, _ in S["traffic"]], [c for c, _ in S["conn"]], S["approach"][0], S["icons"], bea, S["arm"], S["hand"],
           per, tri, S["tri2"], S["lring"], S["waves"], S["pulse"], S["sat"], S["satbeam"], S["ptext"]]
    join_static(dyn)
    return sc, S

def flash(t, on_from):
    return t >= on_from and (t - on_from) * 1.6 % 1.0 < 0.6

def bezier(a, b, h, u):
    m = (a + b) / 2 + Vector((0, 0, h)); return (1 - u) ** 2 * a + 2 * (1 - u) * u * m + u * u * b

def hide_bar(o): bar_set(o, LEJOS, LEJOS + Vector((0, 0, 0.01)))

def pose(t, S):
    # ---------- baliza: dónde está y si destella ----------
    on1 = 0.35                              # gancho: la pega y destella
    place_a, place_b = T("así que ahora"), T("el imán")
    exp = max(seg(t, T("ahora llevas"), T("ahora llevas") + 0.6) * (1 - seg(t, T("por qué"), T("mira qué"))),
              seg(t, T("así que dentro"), T("así que dentro") + 0.6) * (1 - seg(t, T("y lo envía"), T("y lo envía") + 0.4)),
              seg(t, T("y la batería"), T("y la batería") + 0.6) * (1 - seg(t, T("sígueme"), T("sígueme") + 0.5)))
    bea_on = not (T("se te para") <= t < place_a)
    hand_on = None
    if t < 0.4:
        u = seg(t, 0.0, 0.35); hand_on = B + Vector((0, 0, 0.07 * (1 - u)))
    elif place_a <= t < place_b:
        u = seg(t, T("pegas"), T("techo", fin=True)); u0 = seg(t, place_a, T("ventanilla", fin=True))
        out = Vector((0.35, 0.1, 1.15)); hi = Vector((0.6, 0.15, 1.75))
        hand_on = out.lerp(hi, u0) if u < 0.01 else hi.lerp(B, u)
    if not bea_on: S["bea"].location = LEJOS
    else:
        S["bea"].location = (hand_on + Vector((0, 0, 0.0))) if hand_on is not None else B + Vector((0, 0, 0.09 * exp))
    S["dome"].location = Vector((0, 0, 0.034 + 0.07 * exp))
    S["mag"].location = Vector((0, 0, 0.006 - 0.035 * exp))
    act = on1 if t < T("se te para") else T("y empieza")
    lit = bea_on and hand_on is None and flash(t, act)
    set_color(S["domem"], AMB if lit else AMB_D)
    # brazo (hasta la mano)
    if hand_on is not None:
        hp = hand_on + Vector((-0.075, -0.01, 0.03))
        sh = Vector((0.55, 0.1, 1.1)) if t > 1 else hp + Vector((-0.7, -0.05, 0.25))
        el = sh.lerp(hp, 0.5) + Vector((-0.1, 0, 0.12))
        bar_set(S["arm"][0], sh, el); bar_set(S["arm"][1], el, hp); S["hand"].location = hp
    else:
        for a in S["arm"]: hide_bar(a)
        S["hand"].location = LEJOS
    # intermitentes de emergencia
    hz = flash(t, 0.35) and t >= T("se te para") - 0.3 or flash(t, 0.35) and t < 9
    for o in S["carch"]["haz"]: set_color(o, AMB if hz else AMB_D)
    if T("se te para") <= t < T("antes tenías"):
        place(S["car"], mix(-10, S_CAR, seg(t, T("se te para"), T("autovía", fin=True))), mix(0.25, O_CAR, seg(t, T("el coche"), T("autovía", fin=True))))
    else: place(S["car"], S_CAR, O_CAR)
    # ---------- triángulos ----------
    a0 = T("desde este"); a1 = T("ahora llevas")
    if a0 - 0.6 <= t < a1:
        place(S["tri"], S_CAR - 4.0, O_CAR - 0.1)
        fall = seg(t, T("ya no"), T("valen", fin=True))
        S["tri"].rotation_euler = (-fall * math.pi / 2 * 0.98, 0, 0)
        for o in S["trim"]: set_color(o, tuple(mix(c, 0.35, fall) for c in RED))
    else: S["tri"].location = LEJOS
    # persona que sale y anda por el arcén
    p0, p1 = T("antes tenías"), T("así que ahora")
    if p0 <= t < p1:
        u = seg(t, T("andar"), T("colocar"))
        s = mix(S_CAR - 1.0, 4.0, u); place(S["per"], s, 5.1); S["per"].rotation_euler = (0, 0, math.pi + 0.15 * math.sin(t * 9) * (0 < u < 1))
        S["per"].location.z = 0.06 * abs(math.sin(t * 9)) * (0 < u < 1)
        if t >= T("triángulos", 2, fin=True) - 0.3: place(S["tri2"], 3.2, 4.6)
        else:
            S["tri2"].location = S["per"].location + Vector((0, 0, 0.5)); S["tri2"].rotation_euler = (0, 0, 0)
            q, h = road(s, 5.1); S["tri2"].location = q + Vector((0.35, -0.3, 0.55)); S["tri2"].rotation_euler = (0, 0, h - math.pi / 2)
    else:
        S["per"].location = LEJOS; S["tri2"].location = LEJOS
    # tráfico rápido (120 km/h = 33 m/s)
    for k, (c, ch) in enumerate(S["traffic"]):
        a, b = T("se te para"), T("así que ahora")
        if a <= t < b:
            s = -160 + 33 * (t - a - 1.6 * k) + 40 * (k == 2)
            s = ((s + 170) % 470) - 170
            place(c, s, 0.25 if k != 1 else -3.25)
        else: c.location = LEJOS
    # coche que viene por la curva
    a, b = T("si estás"), T("así que dentro")
    c, ch = S["approach"]
    if a <= t < b: place(c, -150 + 22 * (t - a), 0.25)
    else: c.location = LEJOS
    # anillo de luz: 1 km en todas direcciones
    a, b = T("su luz"), T("pero una luz")
    if a <= t < b + 0.3:
        r = 3 + 150 * seg(t, a + 0.2, T("kilómetro", fin=True))
        p, _ = road(S_CAR, O_CAR); S["lring"].location = p + Vector((0, 0, 0.3)); S["lring"].scale = (r, r, 30 + 0 * r)
        S["lring"].scale = (r, r, r * 0.4)
    else: S["lring"].location = LEJOS
    # satélite y ondas de la SIM
    a, b = T("calcula"), T("y lo envía")
    if a - 0.2 <= t < b:
        sp = B + Vector((-0.9, 0.6, 1.2)); S["sat"].location = sp; S["sat"].scale = (0.15,) * 3; S["sat"].rotation_euler = (0, 0, t * 0.5)
        u = seg(t, a, a + 0.5); bar_set(S["satbeam"], sp, sp.lerp(B + Vector((0.016, 0.01, 0.13)), u)); S["satbeam"]["r"] = 0.006
    else:
        S["sat"].location = LEJOS; hide_bar(S["satbeam"])
    waves_t = [(T("y lo envía"), 1.6, 0.6)]
    for tt in (T("repite"), T("repite") + 1.6): waves_t.append((tt, 1.4, 2.5))
    for k, w in enumerate(S["waves"]):
        w.location = LEJOS
        for st, ln, mx in waves_t:
            u = (t - st - 0.25 * k) / ln
            if 0 <= u < 1:
                w.location = S["bea"].location + Vector((0, 0, 0.1 + 0.3 * u * mx)); r = 0.05 + mx * u; w.scale = (r, r, r)
    # pulsos: baliza → DGT → panel y coches
    car_p = road(S_CAR, O_CAR)[0] + Vector((0, 0, 2))
    gant = road(S_GANTRY)[0] + Vector((0, 0, 7.5))
    conn_s = [keyed(t, [(T("desde ahí"), -165), (T("así se"), -95), (T("antes de ver"), -78), (DUR, -78)]),
              keyed(t, [(T("desde ahí"), -195), (T("así se"), -118), (T("antes de ver"), -95), (DUR, -95)])]
    routes = [(T("esa posición"), T("plataforma"), car_p, DGT + Vector((0, 0, 30)), 40)]
    a = T("el aviso"); routes += [(a, T("paneles", fin=True), DGT + Vector((0, 0, 30)), gant, 30),
                                  (T("conectados") - 0.7, T("conectados") + 0.5, DGT + Vector((0, 0, 30)), road(conn_s[0], 0.25)[0] + Vector((0, 0, 3)), 35)]
    for k, pl in enumerate(S["pulse"]):
        st, en, pa, pb, h = routes[k]
        if st <= t < en: pl.location = bezier(pa, pb, h, seg(t, st, en)); pl.scale = (0.35,) * 3 if k == 2 else (1, 1, 1)
        else: pl.location = LEJOS
    lit_panel = t >= T("paneles", fin=True)
    set_color(S["ptext"], AMB if lit_panel and (t * 2) % 1 < 0.7 else (0.06, 0.05, 0.03))
    # coches conectados que frenan
    for k, (c, ch) in enumerate(S["conn"]):
        if T("desde ahí") <= t < T("y mientras"):
            place(c, conn_s[k], 0.25 if k == 0 else -3.25)
            got = t >= T("conectados") + 0.3 * k
            S["icons"][k].location = c.location + Vector((0, 0, 2.6 + 0.15 * math.sin(t * 6))) if got else LEJOS
            brk = t >= T("así se")
            for o in ch["brake"]: set_color(o, RED if brk else BRAKE_OFF)
        else: c.location = LEJOS; S["icons"][k].location = LEJOS
    apply_cam(S["cam"], *camera(t))

def CAMS():
    P = road(S_CAR, O_CAR)[0]; Bc = B
    close = lambda dx, dy, dz: (Bc.x + dx, Bc.y + dy, Bc.z + dz)
    tb = (Bc.x, Bc.y, Bc.z + 0.06); tx = (Bc.x, Bc.y, Bc.z + 0.12)
    def chase(sfun, off, back=9, up=2.6, ahead=25):
        def f(t):
            s = sfun(t); return road(s - back, off)[0] + Vector((0, 0, up)), road(s + ahead, off + 0.6)[0] + Vector((0, 0, 1.0)), 30
        return f
    conn0 = lambda t: keyed(t, [(T("desde ahí"), -165), (T("así se"), -95), (T("antes de ver"), -78), (DUR, -78)])
    return [
        (0.0, [(0.0, close(-0.3, -0.4, 0.12), tb, 50), (T("desde este"), close(-0.42, -0.55, 0.2), tb, 50)]),
        (T("desde este") - 0.1, [(0, (P.x - 3.2, P.y - 9.5, 1.6), (P.x - 0.2, P.y - 3.0, 0.5), 32), (T("ahora llevas"), (P.x - 2.4, P.y - 8.8, 2.2), (P.x, P.y - 2.5, 0.6), 32)]),
        (T("ahora llevas"), [(0, close(-0.3, -0.38, 0.2), tx, 50), (T("mira qué"), close(-0.2, -0.44, 0.24), tx, 50)]),
        (T("mira qué"), [(0, close(-0.4, -0.6, 0.25), tb, 50), (T("se te para"), close(-1.1, -1.9, 0.8), tb, 45)]),
        (T("se te para"), [(0, (P.x - 9, P.y + 12, 6), (P.x, P.y - 14, 0.5), 30), (T("antes tenías"), (P.x - 8, P.y + 10, 5), (P.x, P.y, 0.6), 30)]),
        (T("antes tenías"), [(0, (P.x + 2.5, P.y - 12, 3.8), (P.x + 2.5, P.y - 2, 0.9), 30), (T("andar"), (P.x - 1.2, P.y - 17, 4.4), (P.x + 2.5, P.y - 6, 0.9), 30),
                              (T("justo donde"), (P.x - 1.0, P.y - 37, 3.4), (P.x + 3.0, P.y - 24, 0.9), 30)]),
        (T("justo donde"), [(0, (P.x + 5.6, P.y - 32, 1.5), (P.x - 1.5, P.y - 20, 0.8), 28), (T("así que ahora"), (P.x + 5.6, P.y - 29, 1.7), (P.x - 1.5, P.y - 18, 0.8), 28)]),
        (T("así que ahora"), [(0, (P.x - 2.4, P.y - 2.6, 1.7), (P.x - 0.7, P.y + 0.1, 1.3), 32), (T("pegas"), (Bc.x - 1.4, Bc.y - 1.6, 1.9), (Bc.x - 0.3, Bc.y, 1.55), 35),
                               (T("el imán"), (Bc.x - 0.9, Bc.y - 1.1, 1.85), tb, 40)]),
        (T("el imán"), [(0, close(-0.35, -0.45, 0.12), tb, 50), (T("su luz"), close(-0.55, -0.75, 0.25), tb, 50)]),
        (T("su luz"), [(0, (P.x - 6, P.y - 12, 8), (P.x, P.y, 1), 30), (T("kilómetro", fin=True), (P.x - 60, P.y - 230, 260), (P.x, P.y - 15, 0), 30),
                        (T("si estás"), (P.x - 62, P.y - 225, 255), (P.x, P.y - 15, 0), 30)]),
        (T("si estás"), chase(lambda t: -150 + 22 * (t - T("si estás")), 0.25)),
        (T("así que dentro"), [(0, close(-0.3, -0.4, 0.25), (Bc.x, Bc.y, Bc.z + 0.14), 50), (T("calcula"), close(-0.28, -0.46, 0.3), (Bc.x, Bc.y, Bc.z + 0.14), 50),
                                (T("dónde estás"), close(-0.8, -0.9, 0.6), (Bc.x - 0.3, Bc.y + 0.2, Bc.z + 0.4), 45), (T("y aquí"), close(-1.2, -1.6, 0.8), (Bc.x, Bc.y, Bc.z + 0.5), 40)]),
        (T("y aquí"), [(0, (P.x - 12, P.y - 30, 18), (P.x + 15, P.y + 15, 8), 30), (T("la dgt"), (P.x - 20, P.y - 70, 45), (DGT.x - 10, DGT.y - 10, 12), 30),
                        (T("desde ahí"), (P.x - 22, P.y - 74, 47), (DGT.x - 10, DGT.y - 10, 12), 30)]),
        (T("desde ahí"), [(0, tuple(road(S_GANTRY - 30, 0.5)[0] + Vector((0, 0, 3.0))), tuple(road(S_GANTRY, 0)[0] + Vector((0, 0, 5.5))), 32),
                           (T("conectados") - 0.8, tuple(road(S_GANTRY - 22, 0.5)[0] + Vector((0, 0, 3.4))), tuple(road(S_GANTRY, 0)[0] + Vector((0, 0, 5.6))), 32)]),
        (T("conectados") - 0.8, chase(conn0, 0.25, back=11, up=3.4, ahead=15)),
        (T("y mientras"), [(0, (P.x - 3.4, P.y - 4.2, 3.0), (Bc.x, Bc.y, 1.7), 32), (T("y la batería"), (P.x - 2.8, P.y - 4.6, 2.6), (Bc.x, Bc.y, 1.6), 32)]),
        (T("y la batería"), [(0, close(-0.32, -0.4, 0.26), (Bc.x, Bc.y, Bc.z + 0.16), 50), (T("sígueme"), close(-0.28, -0.45, 0.3), (Bc.x, Bc.y, Bc.z + 0.16), 50),
                              (T("sígueme") + 0.6, close(-0.4, -0.55, 0.16), tb, 50), (DUR + 1, close(-0.3, -0.65, 0.2), tb, 50)]),
    ]

def camera(t):
    segs = CAMS(); k = 0
    for i, (st, _) in enumerate(segs):
        if t >= st: k = i
    st, ks = segs[k]
    if callable(ks): return ks(t)
    ks = [(st if a == 0 else a, p, q, l) for a, p, q, l in ks]
    if ks[-1][0] <= t: ks = ks + [(t + 1, ks[-1][1], ks[-1][2], ks[-1][3])]
    return cam_state(t, ks, drift=0.0)

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v)
    b = S["bea"].location
    return {"bea": Pj(b + Vector((0, 0, 0.12))), "mag": Pj(S["mag"].matrix_world.translation), "sim": Pj(S["sim"].matrix_world.translation),
            "gps": Pj(S["gps"].matrix_world.translation), "batt": Pj(S["batt"].matrix_world.translation),
            "dgt": Pj(DGT + Vector((0, 0, 34))), "panel": Pj(road(S_GANTRY)[0] + Vector((0, 0, 9))),
            "car": Pj(road(S_CAR, O_CAR)[0] + Vector((0, 0, 2))), "hill": Pj(CEN + Vector((33 * math.cos(-0.8), 33 * math.sin(-0.8), 16))),
            "per": Pj(S["per"].location + Vector((0, 0, 2)))}

if __name__ == "__main__":
    run("v16", build, pose, anchors)
