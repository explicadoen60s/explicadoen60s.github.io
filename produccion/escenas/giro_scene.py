# «Giras el móvil y la pantalla gira»: una mano gira el móvil en primer plano y la foto de la pantalla se endereza.
# La pantalla se desliza a un lado: dentro, el acelerómetro (más pequeño que un grano de arroz). Corte al chip gigante:
# se levanta la tapa y aparece el mecanismo visto desde arriba: masa de silicio colgada de muelles, peines de dedos
# móviles entre dedos fijos anclados. La gravedad tira, la masa baja, los huecos de un lado se cierran (franjas de
# color), regla del desplazamiento frente a un virus, carga en los huecos. Vuelta al móvil: tres ejes; se tumba, los
# medidores Y/X cambian, la foto gira. Al final el móvil «camina» y cuenta pasos.
import bpy, bmesh, math, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector, Matrix

T0, DUR = cargar("giro")
_TC = {}
def T(k, n=1, fin=False):
    key = (k, n, fin)
    if key not in _TC: _TC[key] = T0(k, n, fin)
    return _TC[key]

BG = (0.1, 0.07, 0.16); FRAME = (0.2, 0.2, 0.24); GLASS = (0.04, 0.04, 0.06); UIBG = (0.1, 0.11, 0.16)
SKY = (0.45, 0.72, 0.98); GROUND = (0.35, 0.72, 0.35); SUN = (1.0, 0.85, 0.3); TREE = (0.15, 0.45, 0.22); TRUNK = (0.45, 0.3, 0.2)
SKIN = (0.93, 0.72, 0.58); NAIL = (0.97, 0.86, 0.82); PCB = (0.12, 0.42, 0.3); BATT = (0.5, 0.52, 0.58); CHIPC = (0.08, 0.08, 0.1)
RICE = (0.97, 0.95, 0.88); FLOOR = (0.24, 0.25, 0.3)
PKG = (0.13, 0.13, 0.16); SUBS = (0.12, 0.2, 0.26); SI = (0.6, 0.66, 0.78); FIXED = (0.95, 0.55, 0.2); ANCH = (0.3, 0.32, 0.38)
SPRING = (0.92, 0.94, 0.98); YL = (1.0, 0.82, 0.16); RED = (0.95, 0.3, 0.28); GREENA = (0.3, 0.88, 0.45); BLUEA = (0.3, 0.6, 1.0)
GAPN = (0.22, 0.27, 0.36); CLOSE = (1.0, 0.4, 0.3); FAR = (0.3, 0.55, 0.95); VIR = (0.4, 0.8, 0.4); VIRS = (0.85, 0.3, 0.45)
LEJOS = Vector((0, 300, -300))
LA = Vector((0, 0, 0)); LB = Vector((200, 0, 0)); M = LB + Vector((0, 0, 1.6))
CHIP_L = Vector((1.6, 3.4, 0.95)); RICE_L = Vector((2.35, 3.35, 0.68))
MOV_Y = (-2.25, -0.75, 0.75, 2.25); FIX_Y = (-3.0, -1.5, 0.0, 1.5, 3.0); FT = 0.22

def hide_bar(o): bar_set(o, LEJOS, LEJOS + Vector((0, 0, 0.01)))

def cone(r, h, color, unique=False):
    bpy.ops.mesh.primitive_cone_add(radius1=r, radius2=0, depth=h, location=(0, 0, 0), vertices=16); o = bpy.context.object
    for vv in o.data.vertices: vv.co.z += h / 2
    return setup(o, color, None, True, unique)

def arrow(color, r, unique=False):
    return [bar_obj(color, r=r, unique=unique), cone(r * 2.6, r * 6, color, unique=unique)]

def put_arrow(a, p0, p1):
    p0, p1 = Vector(p0), Vector(p1); d = p1 - p0; L = d.length
    if L < 1e-3: hide_arrow(a); return
    hl = min(a[0]["r"] * 6, L * 0.6); q = p1 - d.normalized() * hl
    bar_set(a[0], p0, q); a[1].location = q; a[1].rotation_mode = 'QUATERNION'
    a[1].rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())

def hide_arrow(a):
    hide_bar(a[0]); a[1].location = LEJOS

def build():
    sc, cam = scene_setup(world=BG, shadow=0.3); cam.data.clip_start = 0.02
    S = {"cam": cam}; dyn = [cam]
    # ---------- A: móvil en la mano ----------
    S["roll"] = roll = empty(LA)
    S["ph"] = ph = empty((0, 0.45, 0), roll); ph.rotation_euler = (math.pi / 2, 0, 0)
    rounded_slab(7.4, 15.4, 1.0, 0.8, (0, 0, -0.4), FRAME, ph)
    rounded_slab(7.0, 15.0, 0.8, 0.01, (0, 0, 0.4), FLOOR, ph)
    for s in (-1, 1):
        box((0.25, 15.0, 0.38), (s * 3.58, 0, 0.58), FRAME, ph); box((7.0, 0.25, 0.38), (0, s * 7.58, 0.58), FRAME, ph)
    box((6.4, 5.4, 0.1), (0, 4.4, 0.45), PCB, ph)
    box((1.3, 1.3, 0.2), (-1.6, 5.0, 0.55), CHIPC, ph); box((0.9, 0.6, 0.16), (-1.6, 3.4, 0.53), CHIPC, ph)
    cyl(0.6, 0.25, (1.8, 6.0, 0.6), CHIPC, ph); box((0.5, 0.25, 0.12), (0.2, 2.6, 0.52), (0.7, 0.6, 0.3), ph)
    box((CHIP_L.x * 0 + 0.3, 0.3, 0.1), (CHIP_L.x, CHIP_L.y, 0.55), CHIPC, ph)
    sph(0.035, (CHIP_L.x - 0.1, CHIP_L.y + 0.1, 0.6), (0.85, 0.85, 0.85), ph)
    for k in range(4):
        box((0.04, 0.06, 0.03), (CHIP_L.x - 0.18, CHIP_L.y - 0.1 + 0.07 * k, 0.51), (0.85, 0.75, 0.4), ph)
        box((0.04, 0.06, 0.03), (CHIP_L.x + 0.18, CHIP_L.y - 0.1 + 0.07 * k, 0.51), (0.85, 0.75, 0.4), ph)
    box((6.0, 8.2, 0.16), (0, -3.3, 0.5), BATT, ph)
    S["rice"] = sph(0.37, LEJOS, RICE, scale=(1, 0.42, 0.42)); S["rice"].parent = ph
    # pantalla (se desliza a un lado)
    S["scr"] = scr = empty((0, 0, 0), ph)
    rounded_slab(7.2, 15.2, 0.9, 0.1, (0, 0, 0.75), GLASS, scr)
    rounded_slab(6.8, 14.6, 0.7, 0.006, (0, 0, 0.85), UIBG, scr)
    S["ui"] = ui = empty((0, 0, 0.86), scr)
    box((6.4, 3.0, 0.01), (0, 0.8, 0), SKY, ui); box((6.4, 1.6, 0.01), (0, -1.5, 0), GROUND, ui)
    cyl(0.55, 0.02, (1.8, 1.5, 0.01), SUN, ui)
    cyl(0.08 * 3, 0.02, (-1.6, -0.2, 0.012), TREE, ui); box((0.2, 0.9, 0.01), (-1.6, -0.9, 0.012), TRUNK, ui)
    cyl(0.75, 0.02, (-1.6, 0.0, 0.014), TREE, ui)
    box((1.6, 0.2, 0.01), (0, 3.4, 0), (0.75, 0.78, 0.85), ui); box((2.4, 0.16, 0.01), (0, 2.95, 0), (0.45, 0.48, 0.56), ui)
    # mano: palma detrás, dedos por el borde derecho, pulgar por delante a la izquierda
    hand = empty((0, 0, 0), ph)
    sph(1, (0.4, -5.0, -1.3), SKIN, hand, scale=(3.4, 3.1, 1.1))
    for y in (-2.6, -3.8, -5.0, -6.2):
        cyl(0.55, 3.4, (2.2, y, -0.55), SKIN, hand, rot=(0, math.pi / 2, 0))
        sph(0.55, (3.95, y, 0.15), SKIN, hand); sph(0.32, (4.15, y, 0.45), NAIL, hand, scale=(0.6, 1, 0.9))
    th = bar_obj(SKIN, r=0.62); th.parent = hand; bar_set(th, (-3.3, -7.6, -0.9), (-3.55, -4.9, 0.9))
    sph(0.62, (-3.55, -4.9, 0.9), SKIN, hand); sph(0.36, (-3.5, -4.75, 1.3), NAIL, hand, scale=(1, 1.2, 0.5))
    S["grav"] = arrow(YL, 0.32)
    S["axes"] = [arrow(GREENA, 0.2, True), arrow(RED, 0.2, True), arrow(BLUEA, 0.2, True)]
    S["axes2"] = [cone(0.52, 1.2, GREENA, True), cone(0.52, 1.2, RED, True)]
    dyn += [roll, S["grav"], S["axes"], S["axes2"]]
    # ---------- B: el chip gigante y el mecanismo (visto desde arriba) ----------
    box((34, 34, 1.0), LB + Vector((0, 0, -0.5)), (0.1, 0.32, 0.24))            # placa
    box((28, 28, 1.0), M + Vector((0, 0, -1.6)), PKG)
    for s in (-1, 1):
        box((1.2, 28, 2.4), M + Vector((s * 13.4, 0, -0.4)), PKG); box((28, 1.2, 2.4), M + Vector((0, s * 13.4, -0.4)), PKG)
    for k in range(8):
        for s in (-1, 1):
            box((0.6, 1.8, 0.3), M + Vector((s * 14.4, -10.5 + 3 * k, -1.85)), (0.8, 0.8, 0.82))
    box((25.6, 25.6, 0.2), M + Vector((0, 0, -0.62)), SUBS)
    S["lid"] = lid = empty(M + Vector((0, 0, 1.1)))
    box((28, 28, 0.6), (0, 0, 0), PKG, lid); cyl(0.6, 0.05, (-11, 11, 0.32), (0.4, 0.4, 0.45), lid)
    # partes fijas (ancladas)
    for s in (-1, 1):
        box((1.0, 7.6, 0.8), M + Vector((s * 10.5, 0, 0)), FIXED)
        for x in (-2.6, 2.6): box((1.6, 1.0, 0.8), M + Vector((x, s * 9.0, 0)), ANCH)
    S["fix"] = []
    for s in (-1, 1):
        for y in FIX_Y:
            o = box((1, FT, 0.4), M + Vector((s * 7.5, y, 0)), FIXED); S["fix"].append((o, s, y))
    # masa
    S["mass"] = ms = empty(M)
    S["massb"] = box((8, 6, 0.8), (0, 0, 0), SI, ms, unique=True)
    for x in (-2.5, 0, 2.5):
        for y in (-1.5, 1.5): box((0.5, 0.5, 0.82), (x, y, 0), (0.48, 0.53, 0.64), ms)
    S["movf"] = []
    for s in (-1, 1):
        for y in MOV_Y:
            o = box((1, FT, 0.4), (s * 6.5, y, 0), SI, ms); S["movf"].append((o, s, y))
    S["springs"] = [bar_obj(SPRING, r=0.12, unique=True) for _ in range(40)]
    S["gaps"] = [box((1, 1, 0.04), LEJOS, GAPN, unique=True) for _ in range(16)]
    S["garrow"] = arrow(YL, 0.42)
    S["dimb"] = bar_obj(YL, r=0.06); S["rest"] = [bar_obj(SPRING, r=0.025) for _ in range(6)]
    S["virus"] = vir = empty(LEJOS)
    sph(1.5, (0, 0, 0), VIR, vir)
    for i in range(26):
        ph_ = math.acos(1 - 2 * (i + 0.5) / 26); th_ = math.pi * (1 + 5 ** 0.5) * i
        d = Vector((math.sin(ph_) * math.cos(th_), math.sin(ph_) * math.sin(th_), math.cos(ph_)))
        sph(0.24, tuple(d * 1.72), VIRS, vir)
    dyn += [lid, ms, S["fix"][0][0], [o for o, _, _ in S["fix"]], S["springs"], S["gaps"], S["garrow"], S["dimb"], S["rest"], vir]
    join_static(dyn)
    return sc, S

# ---------- tiempos ----------
def roll_ang(t):
    """giro del móvil (grados) alrededor del eje de la pantalla"""
    ks = [(0.0, 25.0), (1.45, 90.0), (T("cómo sabe") - 0.2, 90.0), (T("cómo sabe") + 0.9, 0.0)]
    if t < T("si tumbas"): return keyed(t, ks)
    if t < T("con ese mismo"): return keyed(t, [(T("si tumbas"), 0.0), (T("si tumbas") + 1.4, 90.0)])
    return keyed(t, [(T("con ese mismo"), 90.0), (T("con ese mismo") + 0.7, 0.0)])

def ui_ang(t):
    """giro de la foto respecto al móvil (grados) y escala"""
    r = roll_ang(t)
    if t < 1.9: return 0.0, 1.0
    if t < T("cómo sabe") - 0.2:
        u = seg(t, 1.9, 2.5); return -90.0 * u, mix(1.0, 1.45, u)
    if t < T("si tumbas"):
        u = seg(t, T("cómo sabe") + 0.9, T("cómo sabe") + 1.4); return mix(-90.0, 0.0, u), mix(1.45, 1.0, u)
    if t < T("gira la pantalla"): return 0.0, 1.0
    if t < T("con ese mismo"):
        u = seg(t, T("gira la pantalla"), T("gira la pantalla") + 0.5); return -90.0 * u, mix(1.0, 1.45, u)
    return -r, mix(1.0, 1.45, r / 90.0)

def slide(t):
    a = T("dentro hay")
    if t < a or t > T("vamos a abrirlo") + 0.3: return 0.0
    return seg(t, a, a + 0.8)

def drop(t, t0, amp=-0.32):
    if t < t0: return 0.0
    u = t - t0; return amp * (1 - math.exp(-3.2 * u) * math.cos(8.5 * u))

def mass_d(t):
    g = T("la gravedad tira") + 0.5; n = T("el bloque se mueve")
    if t < g: return 0.02 * math.sin(t * 2.3)
    if t < n - 0.3: return drop(t, g)
    if t < n + 0.1: return mix(drop(t, g), 0.0, seg(t, n - 0.3, n))
    return drop(t, n + 0.1)

def finger_scale(t):
    return seg(t, T("y tiene dedos"), T("y tiene dedos") + 0.8), seg(t, T("entre sus dedos") + 0.2, T("entre sus dedos") + 1.1)

def gaps_on(t): return t >= T("sus dedos se") - 0.4

def walk(t):
    a = T("con ese mismo") + 0.6
    if t < a: return 0.0
    return 0.55 * abs(math.sin(math.pi * (t - a) / 0.55)) * seg(t, a, a + 0.3)

def pose(t, S):
    # ---------- A ----------
    S["roll"].rotation_euler = (0, math.radians(-roll_ang(t)), 0)
    S["roll"].location = LA + Vector((0, 0, walk(t)))
    S["scr"].location = (-9.5 * slide(t), 0, 1.2 * math.sin(math.pi * slide(t)) if slide(t) < 0.99 else 0)
    ua, us = ui_ang(t); S["ui"].rotation_euler = (0, 0, math.radians(ua)); S["ui"].scale = (us, us, 1)
    r0 = T("grano"); rs = seg(t, r0, r0 + 0.35) if T("dentro hay") < t < T("vamos a abrirlo") + 0.3 else 0.0
    S["rice"].location = RICE_L if rs > 0.01 else LEJOS; S["rice"].scale = (rs * 1.0, rs * 0.42, rs * 0.42)
    S["rice"].rotation_euler = (0, 0, 0.25)
    mw = S["ph"].matrix_world; R3 = mw.to_3x3().normalized(); C = mw @ Vector((0, 0, 0.6))
    grav_show = (T("cómo sabe") <= t < T("dentro hay")) or (T("si tumbas") <= t < T("el móvil lo lee"))
    if grav_show:
        a0 = T("cómo sabe") if t < T("dentro hay") else T("si tumbas")
        u = seg(t, a0, a0 + 0.4); top = LA + Vector((0, -3.2, 1.0 + walk(t)))
        put_arrow(S["grav"], top, top + Vector((0, 0, -0.01 - 7.5 * u)))
    else: hide_arrow(S["grav"])
    ax_on = T("y lo hace") <= t < T("el móvil lo lee") + 0.6
    if ax_on:
        L = 6.0; front = R3 @ Vector((0, 0, 1.3))
        u = seg(t, T("y lo hace"), T("y lo hace") + 0.5)
        dirs = [R3 @ Vector((0, 1, 0)), R3 @ Vector((1, 0, 0)), R3 @ Vector((0, 0, 1))]
        pulses = [T("arriba y"), T("a los lados"), T("y delante")]
        for k, (a, d) in enumerate(zip(S["axes"], dirs)):
            p = math.exp(-((t - pulses[k] - 0.4) / 0.35) ** 2)
            hot = (k == 1 and T("ahora tira") <= t) or (k == 0 and t < T("si tumbas") and t >= T("el chip mide"))
            col = tuple(min(1, c + 0.35 * max(p, 0.5 if (k == 1 and T("ahora tira") <= t) else 0)) for c in (GREENA, RED, BLUEA)[k])
            set_color(a[0], col); set_color(a[1], col)
            a[0]["r"] = 0.2 * (1 + 0.7 * p)
            ln = (L if k < 2 else 5.0) * u + 0.01
            if k == 2: put_arrow(a, C + front, C + front + d * ln)
            else: put_arrow(a, C + front - d * ln, C + front + d * ln)
            if k < 2:
                o = S["axes2"][k]
                if u > 0.05:
                    q = C + front - d * ln; o.location = q + d * 1.2; o.rotation_mode = 'QUATERNION'
                    o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(-d)
                    set_color(o, col)
                else: o.location = LEJOS
    else:
        for a in S["axes"]: hide_arrow(a)
        for o in S["axes2"]: o.location = LEJOS
    # ---------- B ----------
    lo = T("vamos a abrirlo") + 0.15
    u = seg(t, lo, lo + 0.9)
    S["lid"].location = M + Vector((0, 0, 1.1)) + Vector((34 * u, 6 * u, 6 * math.sin(math.pi * min(u, 1))))
    S["lid"].rotation_euler = (0, 0.5 * u, 0)
    d = mass_d(t); S["mass"].location = M + Vector((0, d, 0))
    hl = math.exp(-((t - T("dentro hay", 2) - 0.8) / 0.5) ** 2)
    set_color(S["massb"], tuple(min(1, c + 0.25 * hl) for c in SI))
    fm, ff = finger_scale(t)
    for o, s, y in S["movf"]:
        L = 5.0 * fm + 0.001; o.scale = (L, FT, 0.4); o.location = (s * (4 + L / 2), y, 0)
    for o, s, y in S["fix"]:
        L = 5.0 * ff + 0.001; o.scale = (L, FT, 0.4); o.location = M + Vector((s * (10 - L / 2), y, 0))
    # muelles en zigzag (4: dos arriba, dos abajo)
    sp = math.exp(-((t - T("está colgado") - 0.9) / 0.6) ** 2) + math.exp(-((t - T("los muelles ceden") - 0.5) / 0.5) ** 2)
    for j in range(4):
        x0 = -2.6 if j % 2 == 0 else 2.6; top = j < 2
        ya = M.y + (8.5 if top else -8.5); yb = M.y + d + (3.0 if top else -3.0)
        for i in range(10):
            b = S["springs"][j * 10 + i]
            p0 = Vector((M.x + x0 + (0 if i == 0 else (0.9 if i % 2 else -0.9)), ya + (yb - ya) * i / 10, M.z))
            p1 = Vector((M.x + x0 + (0 if i == 9 else (-0.9 if i % 2 else 0.9)), ya + (yb - ya) * (i + 1) / 10, M.z))
            bar_set(b, p0, p1)
            set_color(b, tuple(min(1, mix(c1, c2, min(1, sp))) for c1, c2 in zip(SPRING, (0.3, 0.9, 1.0))))
    # huecos entre dedos (franjas sobre el sustrato)
    if gaps_on(t):
        elec = seg(t, T("pero entre"), T("pero entre") + 0.5)
        k = 0
        for s in (-1, 1):
            for y in MOV_Y:
                for up in (0, 1):
                    g = S["gaps"][k]; k += 1
                    yf = y + d
                    if up: y0, y1 = yf + FT / 2, y + 0.75 - FT / 2
                    else: y0, y1 = y - 0.75 + FT / 2, yf - FT / 2
                    h = max(0.01, y1 - y0)
                    g.location = M + Vector((s * 6.5, (y0 + y1) / 2, -0.24)); g.scale = (4.0, h, 0.04)
                    closing = h < 0.5
                    pc = math.exp(-((t - T("sus dedos se") - 0.7) / 0.6) ** 2) if closing else math.exp(-((t - T("y se alejan") - 0.6) / 0.6) ** 2)
                    base = CLOSE if closing else FAR
                    col = tuple(mix(GAPN[i], base[i], min(1, 0.8 + 0.2 * pc) if T("sus dedos se") <= t else 0) for i in range(3))
                    if elec > 0:
                        q = min(1.0, 0.15 / max(h, 0.05)) * (0.75 + 0.25 * math.sin(t * 14 + k))
                        col = tuple(mix(col[i], mix(0.25, 1.0, q) * YL[i], elec) for i in range(3))
                    set_color(g, col)
    else:
        for g in S["gaps"]: g.location = LEJOS
    # flecha de gravedad sobre la masa
    ga = T("la gravedad tira")
    if ga <= t < T("y lo hace"):
        u = seg(t, ga, ga + 0.5); p0 = S["mass"].location + Vector((0, 2.2, 0.9)); put_arrow(S["garrow"], p0, p0 + Vector((0, -0.01 - 4.4 * u, 0)))
    else: hide_arrow(S["garrow"])
    # regla del desplazamiento y virus
    n = T("el bloque se mueve")
    yref = M.y - 0.75
    if n <= t < T("cuanto más"):
        x = M.x - 4.9
        bar_set(S["dimb"], Vector((x, yref, M.z + 0.5)), Vector((x, yref + min(-0.001, d), M.z + 0.5)))
        for i, r in enumerate(S["rest"]):
            xa = M.x - 9.0 + i * 0.85; bar_set(r, Vector((xa, yref, M.z + 0.42)), Vector((xa + 0.45, yref, M.z + 0.42)))
    else:
        hide_bar(S["dimb"])
        for r in S["rest"]: hide_bar(r)
    v0 = T("mucho menos")
    if v0 <= t < T("cuanto más"):
        vs = seg(t, v0, v0 + 0.35); S["virus"].location = Vector((M.x - 7.4, M.y - 0.9, M.z + 2.4)); S["virus"].scale = (vs,) * 3
        S["virus"].rotation_euler = (0.3 * t, 0.5 * t, 0)
    else: S["virus"].location = LEJOS
    apply_cam(S["cam"], *camera(t))

def CAMS():
    ph = lambda v: v
    a = T("dentro hay"); b = T("vamos a abrirlo")
    CH = Vector((CHIP_L.x, -1.6, CHIP_L.y))   # el chip en el mundo con el móvil de pie (y = hacia la cámara)
    Mx = M
    return [
        (0.0, [(0, (0.6, -21.0, 0.6), (0, 0, -0.6), 35), (1.45, (0.4, -27.0, 0.4), (0, 0, -0.3), 35),
               (T("cómo sabe"), (0.0, -27.5, 0.0), (0, 0, -0.8), 35), (a, (1.0, -23.0, 0.5), (0, 0, -0.6), 35)]),
        (a, [(0, (1.0, -23.0, 0.5), (0, 0, -0.6), 35), (a + 0.9, (2.0, -12.0, 2.5), (CH.x, 0, CH.z), 35),
             (T("grano") - 0.2, (CH.x + 0.4, -3.6, CH.z - 0.1), (CH.x + 0.38, 0, CH.z), 35),
             (b, (CH.x + 0.45, -3.1, CH.z), (CH.x + 0.42, 0, CH.z), 35)]),
        (b, [(0, (Mx.x + 2, Mx.y - 18, Mx.z + 70), (Mx.x + 0.5, Mx.y + 0.5, Mx.z), 35),
             (T("dentro hay", 2) + 0.3, (Mx.x + 0.6, Mx.y - 9.5, Mx.z + 45), (Mx.x + 0.6, Mx.y + 0.4, Mx.z), 35),
             (T("y tiene dedos"), (Mx.x + 0.4, Mx.y - 9.0, Mx.z + 44), (Mx.x + 0.6, Mx.y + 0.4, Mx.z), 35)]),
        (T("cuando sujetas"), [(0, (Mx.x + 0.6, Mx.y - 9.0, Mx.z + 44), (Mx.x + 0.6, Mx.y + 0.4, Mx.z), 35),
                                (T("los muelles ceden"), (Mx.x + 0.6, Mx.y - 9.5, Mx.z + 42), (Mx.x + 0.6, Mx.y + 0.4, Mx.z), 35),
                                (T("sus dedos se"), (Mx.x - 6.8, Mx.y - 1.2, Mx.z + 15), (Mx.x - 6.8, Mx.y - 0.2, Mx.z), 35),
                                (T("y aquí viene"), (Mx.x - 6.9, Mx.y - 1.1, Mx.z + 14), (Mx.x - 6.9, Mx.y - 0.2, Mx.z), 35)]),
        (T("y aquí viene"), [(0, (Mx.x - 6.9, Mx.y - 1.1, Mx.z + 14), (Mx.x - 6.9, Mx.y - 0.2, Mx.z), 35),
                              (T("el bloque se mueve"), (Mx.x - 6.6, Mx.y - 1.1, Mx.z + 10.5), (Mx.x - 6.6, Mx.y - 0.4, Mx.z), 35),
                              (T("mucho menos"), (Mx.x - 6.8, Mx.y - 1.2, Mx.z + 12.5), (Mx.x - 6.8, Mx.y - 0.4, Mx.z + 0.6), 35),
                              (T("pero entre"), (Mx.x - 6.8, Mx.y - 1.2, Mx.z + 13.5), (Mx.x - 6.8, Mx.y - 0.4, Mx.z + 0.4), 35),
                              (T("cuanto más"), (Mx.x - 4.0, Mx.y - 5.5, Mx.z + 24), (Mx.x - 4.0, Mx.y - 0.5, Mx.z), 35),
                              (T("más carga"), (Mx.x + 0.6, Mx.y - 13.5, Mx.z + 49), (Mx.x + 0.6, Mx.y - 3.8, Mx.z), 35),
                              (T("y lo hace") - 0.01, (Mx.x + 0.6, Mx.y - 13.5, Mx.z + 50), (Mx.x + 0.6, Mx.y - 3.8, Mx.z), 35)]),
        (T("y lo hace"), [(0, (10.0, -25.0, 6.0), (0.5, 0, -0.5), 35), (T("y delante"), (12.0, -24.0, 7.0), (0.5, 0, -0.5), 35),
                          (T("si tumbas"), (6.0, -29.0, 3.0), (0.3, 0, -0.8), 35), (T("ahora tira"), (3.0, -31.0, 1.5), (0.2, 0, -1.2), 35),
                          (T("el móvil lo lee"), (2.0, -31.0, 1.0), (0.2, 0, -1.0), 35), (T("con ese mismo"), (1.5, -30.0, 1.5), (0.0, 0, -0.4), 35),
                          (T("sígueme"), (1.0, -26.0, 2.0), (0.0, 0, 0.2), 35), (DUR + 1, (1.0, -29.0, 2.5), (0.0, 0, 0.2), 35)]),
    ]

def camera(t):
    segs = CAMS(); k = 0
    for i, (st, _) in enumerate(segs):
        if t >= st: k = i
    st, ks = segs[k]
    ks = [(st if a == 0 else a, p, q, l) for a, p, q, l in ks]
    if ks[-1][0] <= t: ks = ks + [(t + 1, ks[-1][1], ks[-1][2], ks[-1][3])]
    return cam_state(t, ks, drift=0.008 if t < T("vamos a abrirlo") else 0.02)

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v)
    mw = S["ph"].matrix_world; R3 = mw.to_3x3().normalized(); C = mw @ Vector((0, 0, 0.6)); front = R3 @ Vector((0, 0, 1.3))
    return {"chip": Pj(mw @ Vector((CHIP_L.x, CHIP_L.y, 0.6))), "rice": Pj(mw @ RICE_L), "phone": Pj(C),
            "grav_tip": Pj(LA + Vector((0, -3.2, -6.5 + walk(t)))),
            "ax_y": Pj(C + front + R3 @ Vector((0, 6.6, 0))), "ax_x": Pj(C + front + R3 @ Vector((6.6, 0, 0))),
            "ax_z": Pj(C + front + R3 @ Vector((0, 0, 5.6))), "ax_y_dn": Pj(C + front + R3 @ Vector((0, -6.6, 0))),
            "mass": Pj(S["mass"].location + Vector((0, 0, 0.4))), "spring": Pj(M + Vector((2.6, 6.0, 0.4))),
            "wall": Pj(M + Vector((-10.5, 0, 0.4))), "virus": Pj(Vector((M.x - 7.4, M.y - 0.9, M.z + 2.4))),
            "dim": Pj(Vector((M.x - 4.9, M.y - 0.9, M.z + 0.5)))}

if __name__ == "__main__":
    run("giro", build, pose, anchors)
