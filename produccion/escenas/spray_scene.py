# «Si tuvieras que inventar el spray…»: un dedo aprieta el pulsador y sale una nube hacia la cámara. Bote en corte: el
# líquido abajo; con aire a presión cada pulsación empuja menos (las partículas de gas se van y el manómetro baja); con
# butano apretado y líquido, al salir un chorro hierve un poco y la presión vuelve a 3 atm. Tubo hasta el fondo y válvula
# con muelle; al apretar sube el líquido y el gas hierve en la boquilla rompiéndolo en gotas. Al hervir roba calor: el bote
# se enfría. Al sol, a 50 °C, la presión sube y el bote aguanta 12 bar. 1926.
import bpy, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector

T0, DUR = cargar("spray")
_TC = {}
def T(k, n=1, fin=False):
    key = (k, n, fin)
    if key not in _TC: _TC[key] = T0(k, n, fin)
    return _TC[key]

BG = (0.07, 0.08, 0.12); FLOOR = (0.13, 0.14, 0.18); CAN = (0.72, 0.75, 0.8); CAN_IN = (0.86, 0.88, 0.92); BAND = (0.15, 0.6, 0.6)
ICE = (0.65, 0.85, 1.0); LIQ = (0.7, 0.45, 0.85); BUT = (0.95, 0.75, 0.35); GAS = (0.85, 0.9, 1.0); CAP = (0.95, 0.95, 0.97)
MIST = (0.92, 0.94, 0.98); SPRING = (0.95, 0.78, 0.25); SKIN = (0.93, 0.72, 0.58); SUN = (1.0, 0.85, 0.2); RED = (0.92, 0.22, 0.2)
LEJOS = Vector((0, 300, -300))
R = 0.35; HB = 1.35; NOZ = Vector((0, -0.13, 1.63))
rng = random.Random(4)
GP = [(rng.uniform(-0.3, 0.3), rng.uniform(0, 1), rng.uniform(0, 6.28)) for _ in range(26)]
MP = [(rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(0, 1)) for _ in range(30)]

def build():
    sc, cam = scene_setup(world=BG, shadow=0.32); cam.data.clip_start = 0.01
    S = {"cam": cam}
    box((20, 20, 0.2), (0, 0, -0.1), FLOOR)
    bpy.ops.mesh.primitive_cube_add(size=1, location=LEJOS); ct = bpy.context.object; ct.scale = (2, 1, 4); ct.hide_render = True; S["ct"] = ct
    def cutm(o):
        m = o.modifiers.new("cut", "BOOLEAN"); m.operation = 'DIFFERENCE'; m.object = ct; return o
    # cuerpo del bote (tubo con fondo) + hombro + cuello
    bpy.ops.mesh.primitive_cylinder_add(radius=R, depth=HB, location=(0, 0, HB / 2), vertices=64, end_fill_type='NOTHING'); body = bpy.context.object
    setup(body, CAN, None, True, unique=True); m = body.modifiers.new("sol", "SOLIDIFY"); m.thickness = 0.015; m.offset = -1
    body.data.materials.append(mat(CAN_IN)); m.material_offset = 1; m.material_offset_rim = 1; cutm(body); S["body"] = body
    bpy.ops.mesh.primitive_uv_sphere_add(radius=R, location=(0, 0, HB), segments=48, ring_count=24); sh = bpy.context.object
    for v in sh.data.vertices:
        if v.co.z < 0: v.co.z = 0
    sh.scale = (1, 1, 0.35); setup(sh, CAN, None, True, unique=True)
    m = sh.modifiers.new("sol", "SOLIDIFY"); m.thickness = 0.015; m.offset = -1; sh.data.materials.append(mat(CAN_IN)); m.material_offset = 1; m.material_offset_rim = 1
    cutm(sh); S["shoulder"] = sh
    S["base"] = cutm(cyl(R, 0.02, (0, 0, 0.01), CAN, unique=True))
    S["cup"] = cutm(cyl(0.09, 0.08, (0, 0, HB + 0.14), CAN, unique=True))
    # válvula: muelle y vástago (dentro), pulsador con boquilla
    S["spring"] = empty((0, 0, HB + 0.04))
    for k in range(7): torus(0.03, 0.006, (0, 0, k / 6), SPRING, S["spring"])
    S["stem"] = cyl(0.015, 0.2, (0, 0, HB + 0.2), (0.5, 0.52, 0.56))
    act = empty((0, 0, 0)); S["act"] = act
    cyl(0.12, 0.12, (0, 0, HB + 0.29), CAP, act); cyl(0.02, 0.05, (0, -0.11, HB + 0.28), (0.3, 0.3, 0.32), act, rot=(math.pi / 2, 0, 0))
    S["tube"] = cyl(0.012, 1.3, (0, 0.02, 0.72), (0.9, 0.92, 0.95))
    # líquidos (cortados)
    S["liq"] = cutm(cyl(R - 0.02, 1.0, (0, 0, 0.5), LIQ, unique=True))
    S["but"] = cutm(cyl(R - 0.02, 1.0, (0, 0, 0.5), BUT, unique=True))
    S["gas"] = [sph(0.025, LEJOS, GAS) for _ in GP]
    S["rise"] = [sph(0.02, LEJOS, LIQ) for _ in range(10)]
    S["mist"] = [sph(0.03, LEJOS, MIST) for _ in MP]
    S["arr"] = [(bar_obj(RED, r=0.012), sph(0.03, LEJOS, RED)) for _ in range(3)]
    S["thumb"] = sph(0.08, LEJOS, SKIN, scale=(1, 1.2, 0.7)); S["tarm"] = bar_obj(SKIN, r=0.07)
    S["sun"] = sph(0.5, LEJOS, SUN); S["rays"] = [bar_obj(SUN, r=0.03) for _ in range(10)]
    join_static([cam, ct, body, sh, S["base"], S["cup"], S["spring"], S["stem"], act, S["tube"], S["liq"], S["but"], S["gas"],
                 S["rise"], S["mist"], S["arr"], S["thumb"], S["tarm"], S["sun"], S["rays"]])
    return sc, S

def hide_bar(o): bar_set(o, LEJOS, LEJOS + Vector((0, 0, 0.001)))

def presses(t):
    """instantes de las pulsaciones (para aire, para butano, para el gancho)"""
    P = [0.5]
    P += [T("cada vez") + 0.3, T("empuja menos") - 0.1, T("y al final") + 0.3]
    P += [T("cuando sale")]
    P += [T("al apretar")]
    return P

def pose(t, S):
    full = t < T("vamos a inventarlo") or t >= T("así que pones")
    xray = t >= T("pero,") - 0.1 or False
    S["ct"].location = Vector((0, -0.5, 1.0)) if t >= T("qué hay") - 0.3 else LEJOS
    # válvula, tubo, pulsador
    valve_on = t < T("vamos a inventarlo") or t >= T("y una válvula")
    tube_on = t < T("vamos a inventarlo") or t >= T("así que pones un tubo")
    press = 0.0
    if t < T("pero,"): press = seg(t, 0.2, 0.5) * (1 - seg(t, T("finísima", fin=True) - 0.2, T("finísima", fin=True) + 0.2))
    elif T("al apretar") - 0.3 <= t < T("y aquí viene"): press = seg(t, T("al apretar") - 0.3, T("al apretar") + 0.2)
    S["act"].location = Vector((0, 0, -0.035 * press)) if valve_on else LEJOS
    S["stem"].location = Vector((0, 0, HB + 0.2 - 0.035 * press)) if valve_on else LEJOS
    S["spring"].location = Vector((0, 0, HB + 0.04)) if valve_on else LEJOS
    S["spring"].scale = (1, 1, 0.1 - 0.035 * press)
    dt = seg(t, T("así que pones un tubo"), T("hasta el fondo", fin=True)) if t >= T("así que pones un tubo") else 1.0
    S["tube"].location = Vector((0, 0.02, 0.72 + 1.5 * (1 - dt))) if tube_on else LEJOS
    for o in (S["cup"],): o.location = Vector((0, 0, HB + 0.14)) if valve_on else LEJOS
    # niveles
    mode = "full"
    if T("vamos a inventarlo") <= t < T("así que usas"): mode = "air"
    lvl_liq = 0.45
    if mode == "air": lvl_liq = 0.45 * seg(t, T("quieres repartir"), T("diminutas", fin=True)) - 0.04 * sum(1 for p in presses(t)[1:4] if t > p)
    but_lvl = 0.0
    if t >= T("así que usas"):
        but_lvl = 0.35 * seg(t, T("se vuelve"), T("butano o propano", fin=True))
        if t >= T("cuando sale"): but_lvl -= 0.06 * seg(t, T("cuando sale"), T("rellena el hueco", fin=True))
        if t >= T("al apretar"): but_lvl -= 0.05 * seg(t, T("el líquido sube"), T("en gotas", fin=True))
        if t >= T("si pulverizas"): but_lvl -= 0.06 * seg(t, T("si pulverizas"), T("helado", fin=True))
    if t < T("vamos a inventarlo"): but_lvl = 0.3; lvl_liq = 0.4
    if lvl_liq > 0.01:
        S["liq"].location = Vector((0, 0, 0.02 + lvl_liq / 2)); S["liq"].scale = (1, 1, lvl_liq)
    else: S["liq"].location = LEJOS
    if but_lvl > 0.01:
        S["but"].location = Vector((0, 0, 0.02 + lvl_liq + but_lvl / 2)); S["but"].scale = (1, 1, but_lvl)
    else: S["but"].location = LEJOS
    surf = 0.02 + lvl_liq + but_lvl
    # gas: partículas en la cámara de arriba
    n_gas = len(GP)
    if mode == "air":
        n_gas = 0 if t < T("un gas") else int(len(GP) * (1 - 0.25 * sum(1 for p in presses(t)[1:4] if t > p)))
    hot = seg(t, T("a cincuenta"), T("sube mucho", fin=True)) * (1 - seg(t, T("lo patentó"), T("lo patentó") + 0.8))
    spd = 1.0 + 2.5 * hot
    boil = T("un poco de líquido") <= t < T("y la presión vuelve") or T("y el gas hierve") <= t < T("rompiendo") + 1.0 or T("para hervir") <= t < T("pero el calor")
    if T("vamos a inventarlo") <= t < T("así que necesitas") + 1.0 and mode == "air" and t < T("un gas"): n_gas = 0
    for k, (g, (x, ph, a)) in enumerate(zip(S["gas"], GP)):
        if k >= n_gas or not (t >= T("un gas") or t < T("vamos a inventarlo")): g.location = LEJOS; continue
        top = HB + 0.08
        if boil and k % 3 == 0:
            u = (t * 0.9 + ph) % 1.0; z = surf + (top - surf) * u
        else:
            z = surf + 0.04 + (top - surf - 0.08) * (0.5 + 0.5 * math.sin(t * 2.1 * spd + a))
        g.location = Vector((x + 0.03 * math.sin(t * 3 * spd + a), -0.03, z))
    # flechas de empuje del gas sobre el líquido
    push = T("así que necesitas") <= t < T("pero si metes") or T("está a unas") <= t < T("cuando sale") or T("a cincuenta") <= t < T("por eso nunca")
    for k, (b, tip) in enumerate(S["arr"]):
        if push:
            x = -0.2 + 0.2 * k; L = 0.12 + 0.12 * hot
            b0 = Vector((x, -0.04, surf + 0.06 + L)); b1 = Vector((x, -0.04, surf + 0.04)); bar_set(b, b0, b1); tip.location = b1
        else: hide_bar(b); tip.location = LEJOS
    # líquido subiendo por el tubo
    up_on = T("el líquido sube") <= t < T("y aquí viene") or t < T("pero,") and press > 0.5
    for k, r in enumerate(S["rise"]):
        if up_on:
            u = (t * 1.5 + k / 10) % 1.0; z = 0.06 + (HB + 0.25 - 0.06) * u
            r.location = Vector((0, 0.0, z)) if z < HB + 0.22 else NOZ + Vector((0, -0.03, 0))
        else: r.location = LEJOS
    # nube
    jets = []
    for p in presses(t):
        jets.append((p, 1.4 if p > 1 else 2.8))
    jets.append((T("al apretar") + 0.8, 7.5)); jets.append((T("si pulverizas"), 2.0))
    weak = 1.0
    for k, (m, (dx, dz, ph)) in enumerate(zip(S["mist"], MP)):
        m.location = LEJOS
        for i, (st, ln) in enumerate(jets):
            if st <= t < st + ln:
                w = 1.0
                if mode == "air" and 1 <= i <= 3: w = 1 - 0.3 * (i - 1)
                if k >= int(len(MP) * w): continue
                u = ((t - st) * 1.2 + ph) % 1.0
                spread = 0.05 + 0.5 * u
                m.location = NOZ + Vector((dx * spread - 0.9 * u * w, -0.05 - 0.9 * u * w, dz * spread * 0.8)); m.scale = ((0.5 + 2.0 * u) * w,) * 3
                break
    # bote helado / caliente
    cold = seg(t, T("el bote se queda helado") - 0.6, T("helado", fin=True)) * (1 - seg(t, T("pero el calor"), T("pero el calor") + 0.6))
    hotc = hot
    c = tuple(mix(mix(CAN[i], ICE[i], cold), (0.95, 0.55, 0.35)[i], hotc * 0.6) for i in range(3))
    for o in (S["body"], S["shoulder"], S["base"]): set_color(o, c)
    wob = 1 + 0.015 * hot * math.sin(t * 25)
    for o in (S["body"],): o.scale = (wob, wob, 1)
    # dedo
    if t < T("pero,") or T("al apretar") - 0.4 <= t < T("y aquí viene") or (T("cada vez") - 0.2 <= t < T("así que usas")) or (T("cuando sale") - 0.3 <= t < T("un poco de líquido")):
        pr = press
        if T("cada vez") - 0.2 <= t < T("así que usas") or T("cuando sale") - 0.3 <= t < T("un poco de líquido"):
            pr = max([max(0.0, 1 - abs(t - p - 0.2) / 0.35) for p in presses(t)])
        hp = Vector((0, 0.02, HB + 0.38 - 0.035 * pr + 0.04 * (1 - min(1, pr * 3))))
        S["thumb"].location = hp; bar_set(S["tarm"], hp + Vector((0, 0.03, 0.02)), hp + Vector((0.25, 0.6, 0.45)))
        if pr > 0.3 and t >= T("cada vez") - 0.2 and t < T("y aquí viene") and not T("al apretar") - 0.4 <= t: S["act"].location = Vector((0, 0, -0.035 * pr))
    else: S["thumb"].location = LEJOS; hide_bar(S["tarm"])
    # sol
    if T("pero el calor") <= t < T("lo patentó"):
        sp = Vector((-1.2, 0.8, 2.6)); S["sun"].location = sp
        for k, r in enumerate(S["rays"]):
            a = k / 10 * math.tau + t * 0.6; d = Vector((math.cos(a), 0, math.sin(a)))
            bar_set(r, sp + d * 0.6, sp + d * (0.85 + 0.08 * math.sin(t * 6 + k)))
    else:
        S["sun"].location = LEJOS
        for r in S["rays"]: hide_bar(r)
    apply_cam(S["cam"], *camera(t))

def CAMS():
    return [
        (0.0, [(0, (0.35, -0.55, HB + 0.42), (0, -0.05, HB + 0.3), 36), (T("y sale"), (0.7, -1.4, HB + 0.4), (0, -0.4, HB + 0.25), 32),
               (T("pero,"), (0.9, -2.0, HB + 0.2), (0, -0.4, HB), 32)]),
        (T("pero,"), [(0, (0.6, -2.6, 1.3), (0, 0, 0.95), 32), (T("vamos a inventarlo"), (0.3, -3.2, 1.2), (0, 0, 0.85), 32)]),
        (T("vamos a inventarlo"), [(0, (0.3, -3.2, 1.1), (0, 0, 0.8), 32), (T("así que necesitas"), (0.5, -2.8, 1.0), (0, 0, 0.75), 32),
                                   (T("pero si metes"), (0.2, -3.0, 1.2), (0, 0, 0.85), 32), (T("cada vez"), (0.4, -3.2, 1.4), (0, -0.3, 1.0), 32),
                                   (T("así que usas"), (0.3, -3.2, 1.2), (0, 0, 0.85), 32)]),
        (T("así que usas"), [(0, (0.4, -2.6, 0.9), (0, 0, 0.6), 32), (T("el butano"), (0.3, -2.4, 0.95), (0, 0, 0.65), 32),
                             (T("dentro del", 2), (0.5, -2.9, 1.2), (0, 0, 0.85), 32), (T("cuando sale"), (0.6, -3.4, 1.5), (0, -0.3, 1.0), 32),
                             (T("pero el líquido"), (0.3, -3.2, 1.1), (0, 0, 0.85), 32)]),
        (T("así que pones un tubo"), [(0, (0.4, -3.0, 1.1), (0, 0, 0.8), 32), (T("y una válvula"), (0.2, -1.1, HB + 0.25), (0, 0, HB + 0.15), 36),
                                      (T("al apretar"), (0.25, -1.2, HB + 0.3), (0, 0, HB + 0.18), 36), (T("el líquido sube"), (0.5, -3.0, 1.0), (0, 0, 0.85), 32),
                                      (T("sale por"), (0.25, -0.9, HB + 0.3), (0, -0.2, HB + 0.25), 36), (T("y el gas"), (0.6, -1.5, HB + 0.35), (0, -0.5, HB + 0.2), 34),
                                      (T("y aquí viene"), (0.4, -3.0, 1.2), (0, 0, 0.85), 32)]),
        (T("para hervir"), [(0, (0.6, -2.8, 1.2), (0, 0, 0.85), 32), (T("por eso"), (0.4, -3.2, 1.3), (0, -0.2, 0.9), 32)]),
        (T("pero el calor"), [(0, (0.3, -3.8, 1.6), (-0.3, 0, 1.2), 32), (T("a cincuenta"), (0.4, -3.4, 1.3), (-0.2, 0, 1.0), 32),
                              (T("lo patentó"), (0.6, -3.0, 1.2), (0, 0, 0.9), 32)]),
        (T("lo patentó"), [(0, (0.5, -2.6, 1.6), (0, -0.3, 1.1), 32), (T("sígueme"), (0.4, -1.6, HB + 0.4), (0, -0.4, HB + 0.2), 34), (DUR + 1, (0.5, -1.8, HB + 0.4), (0, -0.4, HB + 0.2), 34)]),
    ]

def camera(t):
    segs = CAMS(); k = 0
    for i, (st, _) in enumerate(segs):
        if t >= st: k = i
    st, ks = segs[k]
    ks = [(st if a == 0 else a, p, q, l) for a, p, q, l in ks]
    if ks[-1][0] <= t: ks = ks + [(t + 1, ks[-1][1], ks[-1][2], ks[-1][3])]
    return cam_state(t, ks, drift=0.004)

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v)
    return {"liq": Pj(Vector((0.2, -0.05, 0.2))), "but": Pj(Vector((0.2, -0.05, S["but"].location.z if S["but"].location.z > -100 else 0.6))),
            "gas": Pj(Vector((0.2, -0.05, 1.15))), "tube": Pj(Vector((0, 0, 0.5))), "spring": Pj(Vector((0, -0.05, HB + 0.08))),
            "noz": Pj(NOZ), "can": Pj(Vector((0, -R, 0.9)))}

if __name__ == "__main__":
    run("spray", build, pose, anchors)
