# «¿Y si construyes una pista de hielo?»: un patín corta el hielo y salta la viruta; bajamos a un bloque de la pista en
# sección. Suelo plano y nivelado, tubos en zigzag con anticongelante a −10 °C; si echas toda el agua de golpe salen
# burbujas y grietas, así que se echa en capas finas (contador hasta 20); el hielo es transparente y se ven los tubos: se
# pinta de blanco, se pintan las líneas y se sella. 3 cm cubierta, a −5 °C. El frío baja a la tierra, el agua del suelo se
# congela, se hincha y levanta la pista: debajo del aislante, tubos de calefacción. Una máquina rasca el hielo y echa
# agua caliente (400–800 L) y en media hora está lista.
import bpy, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector

T0, DUR = cargar("pistahielo")
_TC = {}
def T(k, n=1, fin=False):
    key = (k, n, fin)
    if key not in _TC: _TC[key] = T0(k, n, fin)
    return _TC[key]

BG = (0.06, 0.08, 0.12); EARTH = (0.42, 0.3, 0.2); EARTH_C = (0.55, 0.62, 0.72); SAND = (0.78, 0.68, 0.48); INS = (0.95, 0.75, 0.82)
CONC = (0.6, 0.61, 0.63); PIPE = (0.3, 0.55, 0.95); HEAT = (0.95, 0.5, 0.2); ICE = (0.72, 0.88, 0.98); ICE_TOP = (0.85, 0.94, 1.0)
WATER = (0.3, 0.6, 0.95); WHITE = (0.96, 0.97, 0.98); RED = (0.9, 0.2, 0.2); BLUE = (0.2, 0.35, 0.85); BOOT = (0.92, 0.92, 0.95)
BLADE = (0.82, 0.85, 0.9); MACH = (0.9, 0.75, 0.15); PLAZA = (0.25, 0.24, 0.26)
LEJOS = Vector((0, 300, -300))
XW = 2.2; YD = 1.4                     # medio ancho y medio fondo del bloque
ZI = 0.0                               # base del hielo (encima del hormigón)
HMAX = 0.24                            # grosor visual del hielo (≈3 cm)
PX = [-2.0 + 0.2 * k for k in range(21)]
rng = random.Random(8)
SHAV = [(rng.uniform(-1, 1), rng.uniform(0, 1), rng.uniform(0.5, 1)) for _ in range(18)]
LENS = [(rng.uniform(-2.0, 2.0), rng.uniform(-1.2, -0.75), rng.uniform(0.6, 1.0)) for _ in range(14)]

def nlayers(t):
    a, b = T("una se congela"), T("hasta doce")
    if t < T("así que la echas"): return 0
    if t < a: return 1 if t >= T("de apenas") else 0
    if t < b: return 1 + int(5 * seg(t, a, b))
    n = 6 + int(14 * seg(t, b, T("veinte capas", fin=True)))
    if t >= T("y otra vez"): n = 20 + int(4 * seg(t, T("y otra vez"), T("dentro", fin=True)))
    return min(n, 24)

def build():
    sc, cam = scene_setup(world=BG, shadow=0.3); cam.data.clip_start = 0.01
    S = {"cam": cam}
    # plaza alrededor (lejos del bloque, para el gancho)
    box((40, 40, 0.2), (0, 6, -2.1), PLAZA)
    # capas del suelo
    S["earth"] = box((2 * XW, 2 * YD, 1.3), (0, 0, -1.35), EARTH, unique=True)
    S["sand"] = box((2 * XW, 2 * YD, 0.25), (0, 0, -0.575), SAND)
    S["ins"] = box((2 * XW, 2 * YD, 0.15), (0, 0, -0.375), INS)
    S["conc"] = box((2 * XW, 2 * YD, 0.3), (0, 0, -0.15), CONC)
    # tubos de frío (a lo largo de y) y de calor
    S["pipes"] = [cyl(0.045, 2 * YD - 0.05, (x, -0.025, 0.045), PIPE, rot=(math.pi / 2, 0, 0)) for x in PX]
    S["bends"] = [bar_obj(PIPE, r=0.045) for _ in range(len(PX) // 2)]
    S["heat"] = [cyl(0.035, 2 * YD - 0.05, (x + 0.1, -0.025, -0.58), HEAT, rot=(math.pi / 2, 0, 0)) for x in PX[::2]]
    S["flow"] = [sph(0.035, LEJOS, (0.55, 0.8, 1.0)) for _ in range(24)]
    # hielo (crece por capas), agua de golpe, burbujas, grietas
    S["ice"] = box((1, 1, 1), LEJOS, ICE, unique=True)
    S["film"] = box((1, 1, 1), LEJOS, WATER)
    S["slab"] = box((2 * XW, 2 * YD, 0.3), LEJOS, WATER, unique=True)
    S["bub"] = [sph(0.03, LEJOS, WHITE) for _ in range(16)]
    S["cracks"] = [bar_obj((0.2, 0.3, 0.45), r=0.012) for _ in range(9)]
    S["ghost"] = [box((0.07, 2 * YD - 0.1, 0.004), LEJOS, (0.45, 0.62, 0.85)) for _ in PX]
    S["paint"] = box((1, 1, 1), LEJOS, WHITE)
    S["lines"] = [box((0.08, 2 * YD, 0.006), LEJOS, c) for c in (RED, BLUE, BLUE)]
    S["noz"] = empty(LEJOS)
    box((0.12, 2 * YD + 0.2, 0.06), (0, 0, 0), (0.25, 0.27, 0.3), S["noz"])
    S["spray"] = [cyl(0.01, 0.2, (0, -YD + 0.2 + k * 0.35, -0.12), WATER, S["noz"]) for k in range(8)]
    # frío que baja, lentes de hielo, flechas de calor
    S["down"] = [(bar_obj(BLUE, r=0.03), sph(0.07, LEJOS, BLUE)) for _ in range(4)]
    S["upar"] = [(bar_obj(HEAT, r=0.03), sph(0.07, LEJOS, HEAT)) for _ in range(4)]
    S["lens"] = [sph(0.12, LEJOS, WHITE, scale=(1.6, 1, 0.5)) for _ in LENS]
    # rayas de patines y máquina
    S["scr"] = [bar_obj((0.6, 0.66, 0.72), r=0.008) for _ in range(10)]
    mach = empty(LEJOS); S["mach"] = mach
    box((1.0, 1.4, 0.55), (0, 0, 0.42), MACH, mach); box((0.6, 1.2, 0.35), (0.15, 0, 0.85), (0.2, 0.3, 0.4), mach)
    box((0.3, 1.5, 0.12), (-0.6, 0, 0.12), (0.3, 0.32, 0.36), mach)
    for sx in (-0.3, 0.35):
        for sy in (-0.6, 0.6): cyl(0.15, 0.12, (sx, sy, 0.15), (0.12, 0.12, 0.14), mach, rot=(math.pi / 2, 0, 0))
    S["wet"] = box((1, 1, 1), LEJOS, (0.55, 0.8, 1.0))
    # patín del gancho
    sk = empty(LEJOS); S["skate"] = sk
    box((0.5, 0.18, 0.28), (0, 0, 0.34), BOOT, sk); box((0.24, 0.16, 0.4), (-0.12, 0, 0.62), BOOT, sk)
    box((0.62, 0.02, 0.1), (0, 0, 0.05), BLADE, sk)
    for x in (-0.18, 0.18): box((0.03, 0.03, 0.12), (x, 0, 0.14), BLADE, sk)
    S["shav"] = [sph(0.02, LEJOS, WHITE) for _ in SHAV]
    S["trail"] = bar_obj((0.6, 0.68, 0.76), r=0.012)
    join_static([cam, S["earth"], S["sand"], S["ins"], S["conc"], S["pipes"], S["bends"], S["heat"], S["flow"], S["ice"], S["film"], S["slab"], S["bub"], S["cracks"], S["ghost"],
                 S["paint"], S["lines"], S["noz"], S["down"], S["upar"], S["lens"], S["scr"], mach, S["wet"], sk, S["shav"], S["trail"]])
    return sc, S

def hide_bar(o): bar_set(o, LEJOS, LEJOS + Vector((0, 0, 0.001)))

def ice_h(t):
    if t < T("vamos a congelar"): return HMAX
    return HMAX * nlayers(t) / 24

def pose(t, S):
    lift = 0.16 * seg(t, T("se hincha"), T("levanta la pista", fin=True)) * (1 - seg(t, T("pero de calefacción"), T("puesta", fin=True)))
    L = Vector((0, 0, lift))
    # el bloque de arriba (hormigón, tubos, hielo) sube si se hincha el suelo
    S["conc"].location = Vector((0, 0, -0.15)) + L; S["ins"].location = Vector((0, 0, -0.375)) + L; S["sand"].location = Vector((0, 0, -0.575)) + L
    show_pipes = t < T("vamos a congelar") or t >= T("tiendes")
    for k, p in enumerate(S["pipes"]):
        ap = seg(t, T("tiendes") + 0.06 * k, T("tiendes") + 0.06 * k + 0.25) if T("vamos a congelar") <= t < T("muy juntos") + 0.5 else 1.0
        p.location = Vector((PX[k], -0.025, 0.045 + 1.5 * (1 - ap))) + L if show_pipes else LEJOS
    for k, b in enumerate(S["bends"]):
        x0, x1 = PX[2 * k], PX[2 * k + 1]; yy = YD - 0.06 if k % 2 == 0 else YD - 0.06
        if show_pipes and t >= T("muy juntos"): bar_set(b, Vector((x0, yy, 0.045)) + L, Vector((x1, yy, 0.045)) + L)
        else: hide_bar(b)
    heat_on = t >= T("pones otros")
    for k, hh in enumerate(S["heat"]):
        ap = seg(t, T("pones otros") + 0.08 * k, T("pones otros") + 0.08 * k + 0.3) if heat_on else 0.0
        hh.location = Vector((PX[2 * k] + 0.1, -0.025, -0.58)) + L if ap > 0.01 else LEJOS
        hh.scale = (1, 1, ap + 0.001)
    # anticongelante que corre
    flow_on = T("por ellos") <= t < T("pero si echas") or T("y se mantiene") <= t < T("y aquí viene")
    for k, f in enumerate(S["flow"]):
        if flow_on:
            i = (k * 7) % len(PX); u = (t * 0.5 + k / 24) % 1.0; dirn = 1 if i % 2 == 0 else -1
            f.location = Vector((PX[i], -YD + 0.02 if dirn > 0 else YD - 0.1, 0.045)) + Vector((0, dirn * (2 * YD - 0.1) * u, 0)) + L
            f.location.y = max(-YD + 0.02, min(YD - 0.1, f.location.y))
            f.location.x = PX[i]; f.location.y = -YD + 0.03 + 0.0
            f.location = Vector((PX[i], -YD + 0.05 + (2 * YD - 0.15) * (u if dirn > 0 else 1 - u), 0.045)) + L
        else: f.location = LEJOS
    # agua de golpe → hielo con burbujas y grietas
    a0, a1 = T("pero si echas"), T("así que la echas")
    if a0 <= t < a1:
        fill = seg(t, a0, T("de golpe", fin=True)); frz = seg(t, T("se congela mal"), T("se congela mal") + 0.8)
        h = 0.3 * fill; S["slab"].location = Vector((0, 0, ZI + h / 2)) + L; S["slab"].scale = (1, 1, max(h, 0.001) / 0.3)
        set_color(S["slab"], tuple(mix(WATER[i], ICE[i], frz) for i in range(3)))
        for k, b in enumerate(S["bub"]):
            if t >= T("con burbujas") - 0.2: b.location = Vector((-2.0 + 0.26 * k, -YD - 0.005, 0.05 + 0.2 * ((k * 0.37) % 1)))
            else: b.location = LEJOS
        for k, c in enumerate(S["cracks"]):
            if t >= T("y grietas") - 0.1:
                x = -1.8 + 0.45 * k; p0 = Vector((x, -YD + 0.2 + 0.25 * (k % 3), 0.302)); u = seg(t, T("y grietas") - 0.1 + 0.05 * k, T("grietas", fin=True) + 0.2)
                bar_set(c, p0, p0 + Vector((0.25 * math.cos(k * 2.1), 0.9 * u, 0)))
            else: hide_bar(c)
    else:
        S["slab"].location = LEJOS
        for b in S["bub"]: b.location = LEJOS
        for c in S["cracks"]: hide_bar(c)
    # hielo por capas
    h = ice_h(t)
    resurf = T("una máquina") <= t
    if h > 0.002 and not (T("pero si echas") <= t < T("así que la echas")):
        S["ice"].location = Vector((0, 0, ZI + h / 2)) + L; S["ice"].scale = (2 * XW, 2 * YD, h)
    else: S["ice"].location = LEJOS
    # boquilla que echa cada capa
    a0 = T("así que la echas")
    if a0 <= t < T("pero el hielo") or T("y otra vez") <= t < T("al final"):
        sp = 0.7 if t < T("hasta doce") else 2.0
        u = (t * sp) % 1.0; x = -XW + 2 * XW * u
        S["noz"].location = Vector((x, 0, ZI + h + 0.22)) + L
        S["film"].location = Vector(((-XW + x) / 2, 0, ZI + h + 0.006)) + L; S["film"].scale = (max(0.01, x + XW), 2 * YD, 0.012)
    else: S["noz"].location = LEJOS; S["film"].location = LEJOS
    # tubos que se ven a través del hielo, pintura y líneas
    see = T("pero el hielo") <= t < T("lo pintas") + 0.6
    paint = seg(t, T("lo pintas"), T("de blanco", fin=True)) if t >= T("lo pintas") else 0.0
    for k, g in enumerate(S["ghost"]):
        g.location = Vector((PX[k], 0, ZI + h + 0.003)) + L if see and (PX[k] + XW) / (2 * XW) > paint else LEJOS
    if paint > 0.01:
        w = 2 * XW * paint; S["paint"].location = Vector((-XW + w / 2, 0, ZI + h + 0.004)) + L; S["paint"].scale = (w, 2 * YD, 0.006)
    else: S["paint"].location = LEJOS
    for k, ln in enumerate(S["lines"]):
        ap = seg(t, T("las líneas") - 0.2 + 0.25 * k, T("las líneas") + 0.3 + 0.25 * k) if t >= T("encima", 2) else 0.0
        if ap > 0.01:
            x = (0.0, -1.2, 1.2)[k]; ln.location = Vector((x, -YD + YD * ap, ZI + h + 0.008)) + L; ln.scale = (0.08, 2 * YD * ap, 0.006)
        else: ln.location = LEJOS
    # frío que baja y suelo que se congela
    a0, a1 = T("el frío baja"), T("así que debajo")
    for k, (b, tip) in enumerate(S["down"]):
        if a0 <= t < a1:
            x = -1.5 + k; u = seg(t, a0, a0 + 0.8); b0 = Vector((x, -YD - 0.02, -0.3)) + L; b1 = b0 + Vector((0, 0, -0.55 * u))
            bar_set(b, b0, b1); tip.location = b1
        else: hide_bar(b); tip.location = LEJOS
    for k, (b, tip) in enumerate(S["upar"]):
        if T("pero de calefacción") <= t < T("pero los patines"):
            x = -1.5 + k; u = seg(t, T("pero de calefacción"), T("pero de calefacción") + 0.6); b0 = Vector((x + 0.2, -YD - 0.02, -0.62)); b1 = b0 + Vector((0, 0, -0.5 * u))
            bar_set(b, b0, b1); tip.location = b1
        else: hide_bar(b); tip.location = LEJOS
    frz = seg(t, T("el agua del suelo"), T("se congela", 4, fin=True)) * (1 - seg(t, T("pero de calefacción"), T("puesta", fin=True)))
    set_color(S["earth"], tuple(mix(EARTH[i], EARTH_C[i], frz) for i in range(3)))
    for k, (le, (x, z, s)) in enumerate(zip(S["lens"], LENS)):
        g = seg(t, T("se hincha") - 0.3 + 0.05 * k, T("se hincha") + 0.4 + 0.05 * k) * (1 - seg(t, T("pero de calefacción"), T("puesta", fin=True)))
        if g > 0.01: le.location = Vector((x, -YD - 0.01, z)); le.scale = (1.6 * s * g, 0.4, 0.5 * s * g)
        else: le.location = LEJOS
    # rayas de patines
    a0 = T("pero los patines")
    mx = None
    if T("una máquina") <= t < T("sígueme"):
        u = seg(t, T("una máquina"), T("cada pasada", fin=True)); mx = -XW - 0.6 + (2 * XW + 1.2) * u
    for k, sc in enumerate(S["scr"]):
        if a0 <= t and t < T("y en media") + 0.5:
            ap = seg(t, a0 + 0.1 * k, a0 + 0.1 * k + 0.4)
            x0 = -2.0 + 0.4 * k; p0 = Vector((x0, -YD + 0.1 + 0.2 * (k % 4), ZI + h + 0.004)); p1 = p0 + Vector((0.5 * math.sin(k), 2.2 * ap, 0))
            if mx is not None and x0 < mx - 0.5: hide_bar(sc)
            else: bar_set(sc, p0, p1)
        else: hide_bar(sc)
    if mx is not None:
        S["mach"].location = Vector((mx, 0, ZI + h)); w = max(0.01, mx - 0.5 + XW)
        S["wet"].location = Vector((-XW + w / 2, 0, ZI + h + 0.004)); S["wet"].scale = (min(w, 2 * XW), 2 * YD - 0.1, 0.006)
        dry = seg(t, T("y en media"), T("estar lista", fin=True))
        set_color(S["wet"], tuple(mix((0.45, 0.72, 1.0)[i], ICE_TOP[i], dry) for i in range(3)))
    else: S["mach"].location = LEJOS; S["wet"].location = LEJOS
    # gancho: patín cortando el hielo
    if t < T("vamos a congelar"):
        u = t / T("vamos a congelar"); x = -0.2 + 1.6 * u
        S["skate"].location = Vector((x, -0.4 + 0.15 * math.sin(t * 2), h)); S["skate"].rotation_euler = (0.1 * math.sin(t * 3), 0, 0.12)
        bar_set(S["trail"], Vector((-1.6, -0.45, h + 0.002)), Vector((x - 0.3, S["skate"].location.y - 0.04, h + 0.002)))
        for k, (sv, (dx, ph, sp)) in enumerate(zip(S["shav"], SHAV)):
            uu = (t * 2.0 * sp + ph) % 1.0
            sv.location = Vector((x - 0.3 - 0.4 * uu, S["skate"].location.y - 0.05 + 0.3 * dx * uu, h + 0.02 + 0.35 * math.sin(math.pi * uu)))
    else:
        S["skate"].location = LEJOS; hide_bar(S["trail"])
        for sv in S["shav"]: sv.location = LEJOS
    apply_cam(S["cam"], *camera(t))

def CAMS():
    tg = lambda z=0.0: (0, 0, z)
    return [
        (0.0, [(0, (-1.0, -2.1, HMAX + 0.55), (0.0, -0.4, HMAX + 0.3), 34), (T("están montando"), (0.3, -2.5, HMAX + 0.8), (0.6, -0.4, HMAX + 0.3), 32),
               (T("aunque"), (1.5, -6.5, 2.5), (0, 0, -0.4), 30), (T("vamos a congelar"), (2.2, -7.0, 2.2), (0, 0, -0.5), 30)]),
        (T("vamos a congelar"), [(0, (2.2, -7.0, 2.2), (0, 0, -0.5), 30), (T("encima"), (1.6, -6.0, 2.6), (0, 0, -0.3), 30),
                                 (T("por ellos"), (0.9, -3.4, 1.0), (0.2, -0.4, 0.0), 30), (T("pero si echas"), (1.4, -5.2, 2.4), (0, 0, -0.2), 30)]),
        (T("pero si echas"), [(0, (1.4, -5.2, 2.4), (0, 0, -0.1), 30), (T("con burbujas"), (0.6, -3.2, 1.0), (0, -0.6, 0.1), 32), (T("así que la echas"), (1.0, -3.6, 1.2), (0, -0.4, 0.05), 32)]),
        (T("así que la echas"), [(0, (0.9, -3.0, 0.9), (0, -0.6, 0.05), 32), (T("una se congela"), (0.7, -2.6, 0.7), (0, -0.8, 0.05), 34), (T("hasta doce"), (1.2, -3.6, 1.2), (0, -0.4, 0.05), 32)]),
        (T("pero el hielo"), [(0, (0.8, -3.0, 2.6), (0, -0.2, 0.2), 32), (T("lo pintas"), (1.2, -3.4, 2.8), (0, 0, 0.2), 32), (T("las líneas"), (0.6, -3.6, 3.2), (0, 0, 0.2), 32)]),
        (T("y otra vez"), [(0, (0.9, -3.2, 1.0), (0, -0.5, 0.1), 32), (T("al final"), (0.8, -2.6, 0.6), (0, -0.9, 0.1), 34),
                           (T("y se mantiene"), (1.2, -4.2, 1.2), (0, -0.4, 0.0), 32)]),
        (T("y aquí viene"), [(0, (1.6, -5.6, 0.6), (0, 0, -0.6), 30), (T("el frío baja"), (1.2, -5.2, -0.2), (0, 0, -0.8), 30),
                             (T("y levanta"), (1.8, -6.2, 0.4), (0, 0, -0.6), 30), (T("así que debajo"), (1.0, -4.6, -0.2), (0, 0, -0.65), 30),
                             (T("una pista de hielo con"), (1.8, -6.4, 1.0), (0, 0, -0.5), 30)]),
        (T("pero los patines"), [(0, (0.6, -2.4, 1.2), (0, -0.3, 0.2), 32), (T("una máquina"), (1.6, -5.4, 2.6), (0, 0, 0.2), 30),
                                 (T("y en media"), (0.8, -5.0, 2.2), (0, 0, 0.1), 30), (DUR + 1, (1.2, -5.4, 2.6), (0, 0, 0.1), 30)]),
    ]

def camera(t):
    segs = CAMS(); k = 0
    for i, (st, _) in enumerate(segs):
        if t >= st: k = i
    st, ks = segs[k]
    ks = [(st if a == 0 else a, p, q, l) for a, p, q, l in ks]
    if ks[-1][0] <= t: ks = ks + [(t + 1, ks[-1][1], ks[-1][2], ks[-1][3])]
    return cam_state(t, ks, drift=0.006)

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v)
    h = ice_h(t)
    return {"pipe": Pj(Vector((PX[6], -YD, 0.05))), "ice": Pj(Vector((-1.0, -YD, h))), "conc": Pj(Vector((-1.2, -YD, -0.15))),
            "ins": Pj(Vector((1.2, -YD, -0.375))), "sand": Pj(Vector((1.2, -YD, -0.575))), "earth": Pj(Vector((0, -YD, -1.0))),
            "heat": Pj(Vector((PX[12] + 0.1, -YD, -0.58))), "mach": Pj(S["mach"].location + Vector((0, 0, 1.1))), "top": Pj(Vector((0, 0, h)))}

if __name__ == "__main__":
    run("pistahielo", build, pose, anchors)
