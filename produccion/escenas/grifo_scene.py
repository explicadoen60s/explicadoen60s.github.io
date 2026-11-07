# «Si tuvieras que inventar el grifo monomando…»: una mano sube y gira la palanca y el chorro pasa de azul a rojo. Dos
# tuberías (fría y caliente, a más de 50 °C); con dos llaves cuesta acertar. Dos discos de cerámica: el de abajo quieto con
# tres agujeros (fría, caliente, salida) y el de arriba con una ranura que mueve la palanca; si no coinciden, no pasa agua.
# El agua empuja con 5 bar pero la cerámica, lisa, no la deja pasar: sin goma. Subir la palanca agranda el hueco (más
# caudal); girarla cambia fría por caliente. En la punta, un aireador mete aire y baja de 12 a 6 litros por minuto.
import bpy, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector

T0, DUR = cargar("grifo")
_TC = {}
def T(k, n=1, fin=False):
    key = (k, n, fin)
    if key not in _TC: _TC[key] = T0(k, n, fin)
    return _TC[key]

BG = (0.08, 0.09, 0.12); WALL = (0.15, 0.17, 0.21); TILE = (0.18, 0.2, 0.25); COUNTER = (0.22, 0.23, 0.27); SINK = (0.6, 0.63, 0.68)
SINK_IN = (0.45, 0.48, 0.53); CHROME = (0.82, 0.85, 0.9); DARK = (0.12, 0.12, 0.14); COLD = (0.25, 0.55, 1.0); HOT = (0.95, 0.28, 0.22)
CER = (0.94, 0.93, 0.88); CER2 = (0.86, 0.84, 0.78); HOLE_O = (0.3, 0.32, 0.36); RUBBER = (0.1, 0.1, 0.1); SKIN = (0.93, 0.72, 0.58)
RED = (0.92, 0.22, 0.2); AIRB = (0.95, 0.97, 1.0)
LEJOS = Vector((0, 300, -300))
NOZ = Vector((0, 0, 0.42))            # boca del grifo
LD = Vector((20, 0, 1.0))             # centro del disco de abajo (escena de los discos)
HC = Vector((-0.45, 0.3, 0)); HH = Vector((0.45, 0.3, 0)); HO = Vector((0, -0.42, 0)); HR = 0.22
rng = random.Random(9)
PART = [(rng.uniform(-0.3, 0.3), rng.uniform(0, 1)) for _ in range(30)]
STREAM = [rng.uniform(0, 1) for _ in range(16)]

def lever(t):
    """(subida 0…1, giro -1 frío … +1 caliente)"""
    up = 0.0; rot = 0.0
    if t < T("vamos a inventarlo"):
        up = seg(t, 0.0, 0.5) * 0.9 + 0.1 * seg(t, 0.5, 1)
        rot = keyed(t, [(0, -0.9), (1.0, -0.9), (2.6, 0.9), (4.2, 0.0), (5.5, 0.1)])
    elif t >= T("el de arriba se mueve"):
        if t < T("si los agujeros"): up = 0.5 * seg(t, T("el de arriba se mueve"), T("con la palanca", fin=True)); rot = 0.0
        elif t < T("ahora", 3): up = 0.5 * (1 - seg(t, T("si los agujeros"), T("no coinciden", fin=True)))
        elif t < T("si la giras"): up = seg(t, T("si la subes"), T("el hueco crece", fin=True))
        elif t < T("pero el chorro"):
            up = 1.0; rot = keyed(t, [(T("si la giras"), 0.0), (T("tapas un poco"), 0.0), (T("la caliente", 2, fin=True), -0.5), (T("destapas"), -0.5), (T("la fría", 2, fin=True), -0.9), (T("solo la"), -0.9), (T("temperatura", fin=True), 0.1)])
        else: up = 1.0; rot = 0.1
    return up, rot

def temp_of(rot): return 15 + 37 * (rot + 1) / 2

def flow_on(t):
    return t < T("vamos a inventarlo") or T("con dos llaves") <= t < T("así que pones") or t >= T("ahora", 3)

def build():
    sc, cam = scene_setup(world=BG, shadow=0.3); cam.data.clip_start = 0.01
    S = {"cam": cam}
    # ---- cocina: encimera, fregadero, azulejos
    box((6, 3, 0.1), (0, 0.9, -0.05), COUNTER)
    box((1.6, 1.2, 0.5), (0, -0.2, -0.3), SINK)
    box((1.4, 1.0, 0.5), (0, -0.2, -0.24), SINK_IN)
    box((6, 0.1, 4), (0, 1.6, 1.9), WALL)
    for i in range(-6, 7):
        for j in range(0, 8): box((0.42, 0.02, 0.42), (i * 0.46, 1.54, 0.25 + j * 0.46), TILE)
    # ---- grifo
    fau = empty((0, 0, 0)); S["fau"] = fau
    cyl(0.17, 0.08, (0, 0.62, 0.04), CHROME, fau)
    cyl(0.13, 0.55, (0, 0.62, 0.32), CHROME, fau)
    bar = bar_obj(CHROME, r=0.06); bar_set(bar, (0, 0.62, 0.55), (0, 0.0, 0.55)); bar.parent = fau
    sph(0.06, (0, 0.0, 0.55), CHROME, fau)
    cyl(0.065, 0.12, (0, 0, 0.49), CHROME, fau)
    S["aer"] = empty(LEJOS)
    cyl(0.058, 0.02, (0, 0, 0), (0.55, 0.58, 0.62), S["aer"])
    for k in range(-2, 3):
        b = box((0.005, 0.11, 0.022), (k * 0.02, 0, -0.012), DARK, S["aer"]); b2 = box((0.11, 0.005, 0.022), (0, k * 0.02, -0.012), DARK, S["aer"])
    S["lev"] = empty((0, 0.62, 0.6))
    cyl(0.07, 0.06, (0, 0, 0.03), CHROME, S["lev"])
    lb = bar_obj(CHROME, r=0.03); bar_set(lb, (0, 0, 0.05), (0, -0.4, 0.05)); lb.parent = S["lev"]
    sph(0.04, (0, -0.4, 0.05), CHROME, S["lev"])
    S["knobs"] = []
    for sx, col in ((-0.42, COLD), (0.42, HOT)):
        e = empty(LEJOS)
        cyl(0.05, 0.12, (0, 0, 0.06), CHROME, e)
        for a in (0, math.pi / 2): box((0.24, 0.035, 0.03), (0, 0, 0.13), CHROME, e, rot=(0, 0, a))
        cyl(0.03, 0.01, (0, 0, 0.15), col, e)
        S["knobs"].append((sx, e))
    # chorro, gotas y salpicaduras
    S["jet"] = cyl(1.0, 1.0, LEJOS, COLD, unique=True)
    S["jets"] = [sph(0.03, LEJOS, COLD, unique=True) for _ in STREAM]
    S["air"] = [sph(0.012, LEJOS, AIRB) for _ in range(14)]
    S["spl"] = [sph(0.02, LEJOS, COLD) for _ in range(12)]
    S["drip"] = sph(0.025, LEJOS, COLD, scale=(1, 1, 1.3))
    S["hand"] = sph(0.07, LEJOS, SKIN, scale=(1.2, 1.4, 0.8)); S["arm"] = bar_obj(SKIN, r=0.06)
    # ---- discos (escena aparte, grande)
    S["pipes"] = []
    for h, col in ((HC, COLD), (HH, HOT)):
        p = cyl(HR, 2.4, LD + h + Vector((0, 0, -1.3)), col); S["pipes"].append(p)
    cyl(HR, 1.6, LD + HO + Vector((0, 0, -0.9)), (0.55, 0.45, 0.75))
    S["low"] = empty(LD)
    cyl(1.0, 0.15, (0, 0, 0), CER2, S["low"], v=64)
    for h, col in ((HC, COLD), (HH, HOT), (HO, HOLE_O)): cyl(HR, 0.01, h + Vector((0, 0, 0.076)), col, S["low"], v=32)
    S["hl"] = [cyl(HR + 0.04, 0.012, LEJOS, c, unique=True) for c in (COLD, HOT, HOLE_O)]
    up = empty(LEJOS); S["up"] = up
    disc = cyl(0.95, 0.15, (0, 0, 0.075), CER, up, v=64, unique=True)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -0.25, 0.075)); sl = bpy.context.object; sl.scale = (0.72, 0.95, 0.4); sl.hide_render = True; sl.parent = up
    m = disc.modifiers.new("slot", "BOOLEAN"); m.operation = 'DIFFERENCE'; m.object = sl; S["slot"] = sl; S["disc"] = disc
    st = empty((0, 0, 0.15), up); S["stem"] = st
    cyl(0.12, 0.6, (0, 0.55, 0.3), (0.7, 0.72, 0.76), st)
    S["dlev"] = bar_obj(CHROME, r=0.06)
    S["part"] = [sph(0.05, LEJOS, COLD, unique=True) for _ in PART]
    S["parr"] = [(bar_obj(RED, r=0.04), sph(0.09, LEJOS, RED)) for _ in range(2)]
    S["ring"] = torus(1.02, 0.06, LEJOS, RUBBER)
    S["leak"] = [sph(0.045, LEJOS, COLD) for _ in range(10)]
    join_static([cam, fau, S["aer"], S["lev"], [e for _, e in S["knobs"]], S["jet"], S["jets"], S["air"], S["spl"], S["drip"], S["hand"], S["arm"],
                 S["pipes"], S["low"], S["hl"], up, sl, S["dlev"], S["part"], S["parr"], S["ring"], S["leak"]])
    return sc, S

def hide_bar(o): bar_set(o, LEJOS, LEJOS + Vector((0, 0, 0.001)))

def mixc(a, b, u): return tuple(mix(a[i], b[i], u) for i in range(3))

def pose(t, S):
    up, rot = lever(t)
    h = (rot + 1) / 2
    col = mixc(COLD, HOT, h)
    # ---- grifo: palanca o dos llaves
    two = T("con dos llaves") <= t < T("así que pones")
    S["lev"].rotation_euler = (math.radians(-35) * up, 0, -rot * 0.7)
    S["lev"].location = Vector((0, 0.62, 0.6)) if not two else LEJOS
    for k, (sx, e) in enumerate(S["knobs"]):
        e.location = Vector((sx, 0.62, 0.0)) if two else LEJOS
        e.rotation_euler = (0, 0, 2.5 * math.sin(t * 3.0 + k * 1.7))
    if two:
        h = 0.5 + 0.48 * math.sin(t * 3.4); col = mixc(COLD, HOT, h); fl = 0.8
    else: fl = up
    # chorro
    aer = t >= T("así que en la punta")
    S["aer"].location = NOZ + Vector((0, 0, 0.005)) if aer else LEJOS
    fr = fl if flow_on(t) else 0.0
    if T("si los agujeros") <= t < T("ahora", 3): fr = 0.0
    if fr > 0.02 and t < T("así que pones") or (t >= T("ahora", 3) and fr > 0.02):
        r = 0.012 + 0.028 * fr * (0.8 if aer else 1.0)
        S["jet"].location = NOZ + Vector((0, 0, -0.43)); S["jet"].scale = (r, r, 0.86)
        jc = col if not aer else mixc(col, (0.85, 0.9, 1.0), 0.35)
        set_color(S["jet"], jc)
        for k, (j, ph) in enumerate(zip(S["jets"], STREAM)):
            u = (t * 1.8 + ph) % 1.0; j.location = NOZ + Vector((0.004 * math.sin(k * 3), 0, -0.86 * u)); j.scale = (r / 0.03 * 1.15,) * 3; set_color(j, jc)
        bruto = T("pero el chorro") <= t < T("así que en la punta") + 0.5
        for k, s in enumerate(S["spl"]):
            u = (t * 1.6 + k / 12) % 1.0; a = k * 2.4
            rr = (0.05 + 0.35 * u) * (1.0 if bruto else 0.35)
            s.location = Vector((rr * math.cos(a), rr * math.sin(a), -0.44 + (0.3 if bruto else 0.08) * math.sin(math.pi * u)))
        for k, a in enumerate(S["air"]):
            if aer:
                u = (t * 1.8 + k / 14) % 1.0; a.location = NOZ + Vector((r * 0.9 * math.cos(k * 2.2), -r * 0.9 * abs(math.sin(k * 2.2)) - 0.005, -0.86 * u))
            else: a.location = LEJOS
    else:
        S["jet"].location = LEJOS
        for o in S["jets"] + S["spl"] + S["air"]: o.location = LEJOS
    # gota que deja de caer
    if T("por eso los grifos") <= t < T("ahora", 3):
        u = ((t - T("por eso los grifos")) * 0.9) % 1.0
        S["drip"].location = NOZ + Vector((0, 0, -0.03 - 0.8 * u * u)) if t < T("casi no gotean") else LEJOS
    else: S["drip"].location = LEJOS
    # mano en la palanca
    hand_on = t < T("vamos a inventarlo") or T("si la subes") - 0.4 <= t < T("pero el chorro") or two or T("y tú casi") <= t
    if hand_on and not two and t < T("y tú casi"):
        a = -rot * 0.7; ph = math.radians(35) * up
        tipw = Vector((0, 0.62, 0.65)) + Vector((0.4 * math.cos(ph) * math.sin(a), -0.4 * math.cos(ph) * math.cos(a), 0.4 * math.sin(ph)))
        S["hand"].location = tipw + Vector((0, -0.02, 0.03)); bar_set(S["arm"], tipw + Vector((0.03, -0.04, 0.02)), tipw + Vector((0.5, -0.55, 0.25)))
    elif t >= T("y tú casi"):
        hp = NOZ + Vector((0, 0, -0.35)); S["hand"].location = hp; bar_set(S["arm"], hp, hp + Vector((0.7, -0.4, -0.1)))
    else: S["hand"].location = LEJOS; hide_bar(S["arm"])
    # ---- discos
    dz = 0.9 * (1 - seg(t, T("uno encima"), T("del otro", fin=True)))
    disc_scene = T("pero tienes") <= t < T("con dos llaves") or T("así que pones") <= t < T("por eso los grifos") or T("ahora", 3) <= t < T("pero el chorro")
    S["up"].location = LD + Vector((0, 0, 0.075 + dz)) if t >= T("así que pones") - 0.2 else LEJOS
    S["up"].rotation_euler = (0, 0, -rot * 0.55)
    S["slot"].location = Vector((0, -0.55 + 0.5 * (up if t >= T("el de arriba") else 0.0), 0.075))
    lev_on = t >= T("el de arriba se mueve")
    if lev_on:
        ang = -rot * 0.55; base = LD + Vector((0, 0, 0.6)) + Vector((0, 0, 0.075 + dz))
        s0 = S["up"].matrix_world @ Vector((0, 0.55, 0.6))
        bar_set(S["dlev"], s0, s0 + Vector((-math.sin(ang) * 1.2, math.cos(ang) * 1.2, 0.5 + 0.6 * up)))
    else: hide_bar(S["dlev"])
    S["stem"].scale = (1, 1, 1) if lev_on else (1e-3,) * 3
    # agujeros resaltados
    for k, (o, hc, key) in enumerate(zip(S["hl"], (HC, HH, HO), ("entra la fría", "entra la caliente", "y sale"))):
        if T(key) <= t < T("el de arriba se mueve") and t >= T("tiene tres"):
            pul = 1 + 0.1 * math.sin(t * 8); o.location = LD + hc + Vector((0, 0, 0.07)); o.scale = (pul, pul, 1)
        else: o.location = LEJOS
    # partículas de agua por la ranura
    open_amt = up if t >= T("el de arriba se mueve") else 0.0
    if T("si los agujeros") <= t < T("ahora", 3): open_amt = 0.0
    for k, (p, (x, ph)) in enumerate(zip(S["part"], PART)):
        pipes_flow = T("pero tienes") <= t < T("con dos llaves")
        if pipes_flow:
            hc = HC if k % 2 == 0 else HH; u = (t * 0.8 + ph) % 1.0
            p.location = LD + hc + Vector((0.1 * math.sin(k), -0.25, -2.2 + 2.0 * u)); set_color(p, COLD if k % 2 == 0 else HOT)
            if T("una fría") > t or (k % 2 == 0 and t < T("una fría")) or (k % 2 == 1 and t < T("y otra caliente")): p.location = LEJOS
        elif disc_scene and open_amt > 0.05 and k < int(len(PART) * open_amt):
            u = (t * 0.9 + ph) % 1.0
            loc = Vector((x, 0.25 - 0.67 * u, 0.12)); src_hot = (k % 10) < 10 * h
            w = S["up"].matrix_world @ (loc - Vector((0, 0, 0.0)))
            p.location = Vector((w.x, w.y, LD.z + 0.16)); set_color(p, HOT if src_hot else COLD)
        else: p.location = LEJOS
    # flechas de presión (5 bar)
    for k, (b, tip) in enumerate(S["parr"]):
        if T("pero el agua empuja") <= t < T("y aquí viene"):
            hc = (HC, HH)[k]; L = 0.2 + 0.6 * seg(t, T("pero el agua empuja"), T("bares", fin=True))
            b0 = LD + hc + Vector((0, -0.25, -1.3)); b1 = b0 + Vector((0, 0, L)); bar_set(b, b0, b1); tip.location = b1
        else: hide_bar(b); tip.location = LEJOS
    # goma que sobra
    a0 = T("no hace falta")
    if a0 - 0.4 <= t < T("por eso los grifos"):
        fall = seg(t, T("ninguna goma"), T("ninguna goma") + 0.8)
        S["ring"].location = LD + Vector((1.6 * fall, -0.3 * fall, 0.08 - 1.5 * fall * fall)); S["ring"].scale = (1, 1, 1)
    else: S["ring"].location = LEJOS
    # el agua intenta colarse entre los discos y no puede
    for k, d in enumerate(S["leak"]):
        if T("no se escapa") <= t < T("no hace falta"):
            a = k / 10 * math.tau; u = abs(math.sin((t * 1.4 + k * 0.3) * math.pi))
            d.location = LD + Vector((0.6 * math.cos(a) * (0.55 + 0.4 * u), 0.6 * math.sin(a) * (0.55 + 0.4 * u), 0.075))
            d.location = LD + Vector((math.cos(a) * (0.55 + 0.38 * u), math.sin(a) * (0.55 + 0.38 * u), 0.08)) if False else d.location
        else: d.location = LEJOS
    apply_cam(S["cam"], *camera(t))

def CAMS():
    L = LD; lvp = (0, 0.75, 0.68)
    return [
        (0.0, [(0, (0.55, -0.35, 0.75), (0, 0.35, 0.45), 32), (T("hay un grifo"), (0.7, -0.75, 0.75), (0, 0.25, 0.35), 32),
               (T("con una sola"), (0.45, -0.35, 1.05), lvp, 36), (T("vamos a inventarlo"), (0.9, -1.4, 1.0), (0, 0.3, 0.3), 32)]),
        (T("quieres agua"), [(0, (0.6, -1.3, 0.7), (0, 0, 0.1), 32), (T("pero tienes"), (0.4, -1.1, 0.6), (0, 0, 0.0), 32)]),
        (T("pero tienes"), [(0, (L.x + 1.6, L.y - 4.2, L.z + 0.2), (L.x, L.y, L.z - 0.9), 32), (T("que llega"), (L.x + 1.4, L.y - 3.6, L.z - 0.4), (L.x + 0.3, L.y, L.z - 0.9), 34)]),
        (T("con dos llaves"), [(0, (0.0, -1.3, 0.75), (0, 0.4, 0.1), 32), (T("así que pones"), (0.2, -1.4, 0.8), (0, 0.4, 0.1), 32)]),
        (T("así que pones"), [(0, (L.x + 1.2, L.y - 3.4, L.z + 2.0), (L.x, L.y, L.z + 0.3), 32), (T("el de abajo"), (L.x + 0.6, L.y - 2.8, L.z + 2.6), (L.x, L.y, L.z + 0.1), 32),
                              (T("tiene tres"), (L.x, L.y - 1.0, L.z + 4.0), (L.x, L.y - 0.05, L.z), 32), (T("el de arriba se mueve"), (L.x + 0.5, L.y - 3.0, L.z + 3.2), (L.x, L.y + 0.2, L.z + 0.3), 30),
                              (T("si los agujeros"), (L.x, L.y - 1.2, L.z + 4.2), (L.x, L.y, L.z), 32)]),
        (T("pero el agua empuja"), [(0, (L.x + 1.8, L.y - 4.0, L.z + 0.4), (L.x, L.y, L.z - 0.5), 32), (T("no se escapa"), (L.x + 0.4, L.y - 3.2, L.z + 0.5), (L.x, L.y, L.z + 0.1), 34),
                                    (T("y aquí viene"), (L.x + 0.2, L.y - 2.4, L.z + 0.35), (L.x, L.y, L.z + 0.08), 40), (T("no hace falta"), (L.x + 0.8, L.y - 3.6, L.z + 0.8), (L.x, L.y, L.z - 0.2), 32)]),
        (T("por eso los grifos"), [(0, (0.35, -0.9, 0.45), (0, 0, 0.25), 34), (T("ahora", 3), (0.3, -0.85, 0.45), (0, 0, 0.25), 34)]),
        (T("ahora", 3), [(0, (L.x + 0.6, L.y - 2.6, L.z + 3.6), (L.x, L.y, L.z + 0.2), 32), (T("si la giras"), (L.x, L.y - 1.3, L.z + 4.2), (L.x, L.y, L.z), 32),
                      (T("el caudal"), (L.x + 0.3, L.y - 1.6, L.z + 4.0), (L.x, L.y, L.z), 32)]),
        (T("pero el chorro"), [(0, (0.8, -1.3, 0.4), (0, 0, -0.1), 32), (T("así que en la punta"), (0.32, -0.5, 0.42), (0, 0, 0.36), 40),
                               (T("unas rejillas"), (0.22, -0.36, 0.3), (0, 0, 0.36), 42), (T("un grifo que", 2), (0.5, -1.0, 0.5), (0, 0, 0.1), 34)]),
        (T("y tú casi"), [(0, (0.6, -1.1, 0.5), (0, 0, 0.1), 34), (DUR + 1, (0.7, -1.3, 0.6), (0, 0, 0.15), 34)]),
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
    return {"cold": Pj(LD + HC + Vector((0, 0, 0.1))), "hot": Pj(LD + HH + Vector((0, 0, 0.1))), "out": Pj(LD + HO + Vector((0, 0, 0.1))),
            "pc": Pj(LD + HC + Vector((0, -0.2, -1.6))), "ph": Pj(LD + HH + Vector((0, -0.2, -1.6))), "up": Pj(LD + Vector((0.7, -0.5, 0.25))),
            "low": Pj(LD + Vector((0.8, -0.5, -0.05))), "ring": Pj(S["ring"].location), "aer": Pj(NOZ + Vector((0.06, 0, -0.02))),
            "jet": Pj(NOZ + Vector((0, 0, -0.4))), "lev": Pj(Vector((0, 0.95, 0.7)))}

if __name__ == "__main__":
    run("grifo", build, pose, anchors)
