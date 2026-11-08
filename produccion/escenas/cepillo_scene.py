# «Si tuvieras que inventar el cepillo eléctrico…»: primer plano del cabezal vibrando sobre unas muelas con la pasta
# salpicando; el cepillo de mano frotando despacio; luego se construye pieza a pieza en corte: mango, batería, motor que
# gira (no sirve), bobina e imán que lleva el cabezal a derecha e izquierda según la corriente, vibración rápida; la pasta
# y la saliva que se meten entre las muelas; la presión que frena la vibración y el anillo que se pone rojo; las dos
# arcadas vistas desde arriba con un reloj de 2 minutos y 4 zonas; el enchufe mojado (no) y la base de carga con dos
# bobinas, campo magnético, corriente hacia la batería y el mango ya cerrado.
import bpy, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("cepillo")
BG = (0.06, 0.11, 0.125); WHITE = (0.95, 0.96, 0.96); INNER = (0.72, 0.84, 0.86); CORAL = (1.0, 0.45, 0.38); TEAL = (0.2, 0.75, 0.72)
BR1 = (0.97, 0.97, 0.97); BR2 = (0.45, 0.8, 1.0); TOOTH = (0.97, 0.95, 0.88); GUM = (0.93, 0.5, 0.55); COPPER = (0.9, 0.52, 0.28)
STEEL = (0.72, 0.75, 0.8); RED = (0.95, 0.22, 0.2); BLUE = (0.2, 0.45, 0.95); CUR = (1.0, 0.88, 0.2); FIELD = (0.35, 0.8, 1.0)
GREEN = (0.3, 0.95, 0.5); MANUAL = (0.3, 0.55, 0.95); FOAM = (0.98, 0.98, 1.0); SALIVA = (0.6, 0.85, 1.0); LEJOS = (0, 0, -900)
RNG = random.Random(5)
PIV = 11.8                       # pivote del cabezal (brazo A)
TX = 60.0                        # muelas
DX = 150.0                       # arcadas vistas desde arriba
PX = -60.0                       # enchufe
HEAD2 = Vector((TX, 1.4, 6.2))
GAPS = (-1.4, 1.4, 4.2)

def alpha(o, a):
    m = o.active_material; m.diffuse_color = (*m.diffuse_color[:3], a); m.surface_render_method = 'BLENDED'
def poly(pts, u):
    P = [Vector(p) for p in pts]; L = [(b - a).length for a, b in zip(P, P[1:])]; s = u * sum(L)
    for a, b, l in zip(P, P[1:], L):
        if s <= l: return a.lerp(b, s / max(l, 1e-6))
        s -= l
    return P[-1]
def show(o, on):
    o.hide_render = not on
    for c in o.children: show(c, on)
def place(o, on, loc):
    o.location = loc if on else LEJOS; show(o, on)
def arrow(col, r=0.3, L=3.0):
    e = empty(LEJOS)
    cyl(r, L, (0, 0, L / 2), col, parent=e, v=12)
    bpy.ops.mesh.primitive_cone_add(radius1=r * 2.4, radius2=0, depth=r * 4.5, location=(0, 0, L + r * 2.2), vertices=16); setup(bpy.context.object, col, parent=e)
    return e
def aim(o, p, d, s=1.0):
    o.location = p; o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(Vector(d).normalized())
    s = max(s, 0.001); o.scale = (s, s, s)

def brush_head_down(parent, handle_col, manual=False):
    """cabezal con las cerdas hacia abajo y mango hacia +y (para las muelas)"""
    box((1.15, 2.9, 0.6), (0, 0, 0), WHITE if not manual else handle_col, parent=parent)
    for i in range(6):
        for x in (-0.3, 0.3):
            cyl(0.17, 1.15, (x, -1.2 + 0.48 * i, -0.875), BR1 if (i + (x > 0)) % 2 else BR2, parent=parent, v=10)
    o = bar_obj(WHITE if not manual else handle_col, 0.42, parent=parent); bar_set(o, (0, 1.3, 0.05), (0, 6, 1.2))
    if manual:
        o = box((1.0, 14, 0.7), (0, 13, 2.9), handle_col, parent=parent, rot=(0.24, 0, 0))
        return None
    o = bar_obj(WHITE, 1.35, parent=parent); bar_set(o, (0, 6, 1.2), (0, 20, 4.6))
    led = torus(1.38, 0.13, (0, 7.2, 1.48), GREEN, parent=parent, rot=(math.pi / 2 - 0.24, 0, 0), unique=True)
    cyl(0.35, 0.3, (0, 9.5, 2.4), CORAL, parent=parent, rot=(0.24 - math.pi / 2, 0, 0))
    return led

def tooth(x, y, parent=None, s=1.0, col=TOOTH, unique=False):
    o = rounded_slab(2.4 * s, 2.45 * s, 0.7 * s, 2.3 * s, (x, y, 1.9), col, parent=parent, unique=unique)
    for dx in (-0.55, 0.55):
        for dy in (-0.55, 0.55): sph(0.6 * s, (x + dx * s, y + dy * s, 1.9 + 2.15 * s), col, parent=parent, seg=12)
    return o

FOAMP = [(RNG.uniform(-0.9, 0.9), RNG.uniform(-1.4, 1.4), RNG.uniform(4.4, 5.3), RNG.uniform(0.18, 0.36), RNG.random() < 0.6, RNG.uniform(0, 6.28)) for _ in range(40)]
LIQ = [(RNG.choice(GAPS), RNG.uniform(-0.9, 0.9), RNG.random()) for _ in range(30)]

def arch_pos(i, upper):
    """8 dientes por media arcada; i 0..15 (0-7 derecha, 8-15 izquierda)"""
    side = 1 if i < 8 else -1; k = i % 8
    th = math.radians(8 + k * 11.5) * side
    x = DX + 7.4 * math.sin(th); y = 6.0 * math.cos(th)
    return (x, (4.0 + y) if upper else -(4.0 + y)), th

def build():
    sc, cam = scene_setup(world=BG, shadow=0.3, light_rot=-30)
    S = {"cam": cam}
    # ---------------- cepillo A (vertical, en corte) ----------------
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -6, 6)); cut = bpy.context.object; cut.scale = (8, 12, 22); cut.hide_render = True
    S["cut"] = cut
    def cutobj(o, th=0.14, inner=INNER):
        m = o.modifiers.new("sol", "SOLIDIFY"); m.thickness = th; m.offset = -1
        o.data.materials.append(mat(inner)); m.material_offset = 1; m.material_offset_rim = 1
        b = o.modifiers.new("cut", "BOOLEAN"); b.operation = 'DIFFERENCE'; b.object = cut
        return b
    S["mango"] = cyl(1.4, 15, (0, 0, 7.5), WHITE, v=48); S["bool"] = cutobj(S["mango"])
    S["ledA"] = torus(1.42, 0.13, (0, 0, 14.4), TEAL, unique=True)
    # cabezal + cuello + eje (pivota en PIV)
    S["cab"] = empty((0, 0, PIV)); cb = S["cab"]
    cyl(0.16, 3.4, (0, 0, 1.7), STEEL, parent=cb)
    o = cyl(0.55, 4.6, (0, 0, 5.5), WHITE, parent=cb)
    box((1.15, 0.65, 2.9), (0, 0, 9.2), WHITE, parent=cb)
    for i in range(6):
        for x in (-0.3, 0.3):
            cyl(0.17, 1.15, (x, -0.85, 8.0 + 0.48 * i), BR1 if (i + (x > 0)) % 2 else BR2, parent=cb, rot=(math.pi / 2, 0, 0), v=10)
    S["iman"] = empty((0, 0, 0.55), parent=cb)
    box((0.75, 0.62, 0.6), (0.37, 0, 0), RED, parent=S["iman"]); box((0.75, 0.62, 0.6), (-0.37, 0, 0), BLUE, parent=S["iman"])
    S["fant"] = []
    for sx in (-1, 1):
        e = empty((0, 0, PIV)); box((1.15, 0.65, 2.9), (0, 0, 9.2), (0.8, 0.9, 0.95), parent=e, unique=True); alpha(e.children[0], 0.35)
        S["fant"].append(e)
    cyl(0.32, 0.9, (0, 0, PIV), (0.4, 0.42, 0.46), rot=(math.pi / 2, 0, 0))
    # batería
    S["bat"] = empty((0, 0, 0)); bt = S["bat"]
    cyl(0.75, 5, (0, 0, 5.5), (0.22, 0.24, 0.28), parent=bt); cyl(0.35, 0.3, (0, 0, 8.1), STEEL, parent=bt)
    S["carga"] = box((0.5, 0.12, 1), (0, -0.78, 3.1), GREEN, parent=bt, unique=True)
    # cables y corriente
    S["cables"] = [bar_obj((0.85, 0.3, 0.25), 0.07), bar_obj((0.2, 0.2, 0.22), 0.07)]
    S["corr"] = [sph(0.13, LEJOS, CUR, seg=8) for _ in range(10)]
    # motor
    S["motor"] = empty(LEJOS); mt = S["motor"]
    cyl(0.75, 2.5, (0, 0, 9.65), STEEL, parent=mt); cyl(0.12, 0.9, (0, 0, 11.3), STEEL, parent=mt)
    box((0.3, 0.1, 2.3), (0, -0.76, 9.65), CORAL, parent=mt)
    # bobina que mueve el imán
    S["bobina"] = empty(LEJOS); bb = S["bobina"]
    cyl(0.5, 1.7, (0, 0, 10.4), COPPER, parent=bb, rot=(0, math.pi / 2, 0))
    for k in range(7): torus(0.52, 0.07, (-0.75 + 0.25 * k, 0, 10.4), (0.7, 0.35, 0.18), parent=bb, rot=(0, math.pi / 2, 0))
    # bobina de carga del mango y base
    S["bob_m"] = empty(LEJOS)
    for k in range(5): torus(0.95, 0.12, (0, 0, 0.55 + 0.22 * k), COPPER, parent=S["bob_m"])
    S["base"] = empty(LEJOS); bs = S["base"]
    o = cyl(2.7, 2.4, (0, 0, -1.25), WHITE, parent=bs, v=48); cutobj(o, 0.16); S["baseo"] = o
    cyl(0.45, 0.5, (0, 0, 0.1), WHITE, parent=bs)
    for k in range(5): torus(1.7, 0.14, (0, 0, -1.9 + 0.25 * k), COPPER, parent=bs)
    o = bar_obj((0.85, 0.85, 0.87), 0.2, parent=bs); bar_set(o, (0, 2.6, -2.1), (0, 12, -2.1))
    S["campo"] = []
    for R in (1.0, 1.6, 2.3):
        for sx in (-1, 1):
            S["campo"].append(torus(R, 0.06, LEJOS, FIELD, rot=(math.pi / 2, 0, 0), unique=True)); S["campo"][-1]["R"] = R * sx
    S["corr2"] = [sph(0.12, LEJOS, CUR, seg=8) for _ in range(8)]
    # ---------------- muelas ----------------
    rounded_slab(3.6, 13, 1.4, 2.6, (TX, 1.4, 0), GUM)
    for y in (-2.8, 0, 2.8, 5.6): tooth(TX, y)
    S["b2"] = empty(HEAD2); S["led2"] = brush_head_down(S["b2"], WHITE)
    S["b3"] = empty(LEJOS); brush_head_down(S["b3"], MANUAL, manual=True)
    S["espuma"] = [sph(r, LEJOS, FOAM if f else SALIVA, seg=8) for (_, _, _, r, f, _) in FOAMP]
    S["liq"] = [sph(0.28, LEJOS, (0.3, 0.65, 1.0), seg=8) for _ in LIQ]
    S["fuerza"] = arrow(RED, 0.4, 3.0)
    # ---------------- arcadas desde arriba ----------------
    S["dientes"] = {}
    for up in (True, False):
        for i in range(16):
            (x, y), th = arch_pos(i, up)
            o = rounded_slab(1.5, 1.35 if i % 8 > 2 else 1.0, 0.45, 1.2, (x, y, 0), TOOTH, unique=True); o.rotation_euler = (0, 0, -th if up else th)
            S["dientes"][(up, i)] = o
            g = rounded_slab(2.2, 2.0, 0.7, 0.7, (x, y, -0.5), GUM); g.rotation_euler = (0, 0, -th if up else th)
    rounded_slab(22, 30, 4, 0.6, (DX, 0, -1.2), (0.16, 0.24, 0.26))
    S["mini"] = empty(LEJOS); mn = S["mini"]
    box((1.0, 2.4, 0.5), (0, 0, 1.6), WHITE, parent=mn); o = bar_obj(WHITE, 0.4, parent=mn); bar_set(o, (0, 1.2, 1.6), (0, 4.5, 1.8))
    o = bar_obj(WHITE, 1.0, parent=mn); bar_set(o, (0, 4.5, 1.8), (0, 13, 2.2)); torus(1.02, 0.1, (0, 5.2, 1.85), TEAL, parent=mn, rot=(math.pi / 2, 0, 0))
    for i in range(5):
        for x in (-0.25, 0.25): cyl(0.15, 0.8, (x, -0.95 + 0.48 * i, 1.0), BR2, parent=mn, v=8)
    # ---------------- enchufe ----------------
    rounded_slab(6, 0.8, 0.6, 7.5, (PX, 1.2, -3.75), WHITE).rotation_euler = (0, 0, 0)
    box((40, 1, 30), (PX, 2.2, 0), (0.2, 0.3, 0.32))
    cyl(1.9, 0.4, (PX, 0.6, 0), (0.85, 0.85, 0.86), rot=(math.pi / 2, 0, 0))
    S["clavija"] = empty((PX, -0.9, 0)); cl = S["clavija"]
    cyl(1.6, 2.2, (0, -0.9, 0), (0.95, 0.95, 0.95), parent=cl, rot=(math.pi / 2, 0, 0))
    o = bar_obj((0.95, 0.95, 0.95), 0.4, parent=cl); bar_set(o, (0, -2.0, 0), (0, -2.6, -1.2)); o = bar_obj((0.95, 0.95, 0.95), 0.4, parent=cl); bar_set(o, (0, -2.6, -1.2), (0, -2.6, -14))
    S["gotasP"] = [sph(0.35, LEJOS, SALIVA, seg=10) for _ in range(6)]
    S["chispa"] = [sph(0.25, LEJOS, CUR, seg=8) for _ in range(8)]
    dyn = [cam, cut, S["mango"], S["ledA"], S["cab"], S["fant"], S["bat"], S["cables"], S["corr"], S["motor"], S["bobina"], S["bob_m"],
           S["base"], S["campo"], S["corr2"], S["b2"], S["b3"], S["espuma"], S["liq"], S["fuerza"], list(S["dientes"].values()),
           S["mini"], S["clavija"], S["gotasP"], S["chispa"]]
    join_static(dyn)
    return sc, S

# --------------------------------------------------------------------------------------------------
def clock(t):
    """reloj simulado del cepillo (0-120 s) mientras la voz habla del tiempo"""
    return 120 * max(0, min(1, (t - T("pones un reloj") - 0.2) / (T("cuatro pausas", fin=True) - 0.3 - T("pones un reloj") - 0.2)))
def paused(t):
    c = clock(t)
    return any(abs(c - p) < 2.2 for p in (30, 60, 90)) or c >= 119.5

def pose(t, S):
    t_vam, t_prim, t_frota, t_pones, t_gira, t_ytu, t_usas = T("vamos"), T("primero"), T("frota"), T("así que pones"), T("pero un motor"), T("y tú"), T("así que usas")
    t_c1, t_der, t_c2, t_izq, t_otra, t_cons = T("cuando la"), T("el imán"), T("cuando cambia"), T("a la izquierda"), T("una y otra"), T("así consigues")
    t_cur, t_esa, t_cerd, t_liq, t_don, t_pero, t_fren, t_poreso = T("y aquí"), T("a esa"), T("las cerdas"), T("y el líquido"), T("donde"), T("pero si"), T("frenas"), T("por eso")
    t_ahora, t_falta, t_agua, t_base, t_otra_b, t_sin, t_carga = T("ahora"), T("falta"), T("pero el agua"), T("así que la base"), T("otra bobina"), T("sin ningún"), T("con una carga")
    # ---- cepillo eléctrico sobre las muelas ----
    b2_on = t < t_vam + 1.2 or t > t_cur - 0.3
    fly = seg(t, t_vam, t_vam + 1.1) if t < t_cur - 0.3 else 0
    amp = 0.32
    if t > t_pero: amp *= 1 - 0.7 * seg(t, t_pero + 0.5, t_fren + 0.6) * (1 - seg(t, t_poreso + 1.6, t_poreso + 2.4))
    vib = amp * math.sin(t * 2 * math.pi * 7.5 + 0.8)
    push = 0.0
    if t > t_pero: push = -0.25 * seg(t, t_pero, t_pero + 0.6) * (1 - seg(t, t_poreso + 1.6, t_poreso + 2.4))
    place(S["b2"], b2_on, HEAD2 + Vector((vib, 0, push + 14 * fly * fly)))
    S["b2"].rotation_euler = (0, 0, 0.03 * math.sin(t * 2 * math.pi * 7.5))
    alarm = seg(t, T("sensor") - 0.3, T("sensor")) * (1 - seg(t, t_poreso + 1.6, t_poreso + 2.4))
    set_color(S["led2"], RED if alarm > 0.5 and int(t * 6) % 2 == 0 else (tuple(g + (r - g) * alarm for g, r in zip(GREEN, RED))))
    fz = win01(t, t_pero, t_poreso + 2.0, 0.3, 0.4)
    if fz > 0.02: aim(S["fuerza"], HEAD2 + Vector((vib, 0.6, 5.4 - 0.6 * math.sin(t * 6) ** 2)), (0, 0, -1), fz * 0.6)
    else: S["fuerza"].location = LEJOS
    # cepillo manual
    man = t_vam + 0.5 < t < t_pones + 0.3
    come = seg(t, t_vam + 0.5, t_vam + 1.4)
    scrub = 0.9 * math.sin((t - t_frota) * 2 * math.pi * 3.0) if t > t_frota - 0.2 else 0.3 * math.sin(t * 5)
    place(S["b3"], man, HEAD2 + Vector((0, scrub, 12 * (1 - come) ** 2 - 0.05)))
    # espuma y líquido
    agit = 1.0 + 1.6 * seg(t, t_cerd, t_cerd + 0.8)
    for k, (o, (x, y, z, r, f, ph)) in enumerate(zip(S["espuma"], FOAMP)):
        on = (t < t_vam + 0.6) or (t > t_cur - 0.3 and t < T("ahora"))
        if not on: o.location = LEJOS; continue
        j = 0.25 * agit
        o.location = Vector((TX + x * 1.1 + vib * 0.6 + j * math.sin(t * 11 + ph), 1.4 + y + j * math.cos(t * 9 + ph * 2), z + 0.25 * agit * abs(math.sin(t * 7 + ph))))
    lq = t > t_liq - 0.2 and t < T("ahora")
    for k, (o, (gy, x, ph)) in enumerate(zip(S["liq"], LIQ)):
        if not lq: o.location = LEJOS; continue
        u = ((t - t_liq) * 0.55 + ph) % 1
        o.location = Vector((TX + x, gy + 0.06 * math.sin(t * 8 + k), 4.7 - 1.9 * u))
    # ---- cepillo A en corte ----
    S["bool"].show_render = t < t_sin + 0.3
    S["baseo"].modifiers["cut"].show_render = t < t_sin + 0.3
    mot_in = seg(t, t_pones + 0.2, t_pones + 1.0); mot_out = seg(t, t_usas - 0.1, t_usas + 0.6)
    mot_on = t_pones < t < t_usas + 0.6
    place(S["motor"], mot_on, (0, -9 * (1 - mot_in) - 9 * mot_out, 0))
    spin = 0.0
    if t_gira - 0.1 < t < t_usas: spin = (t - t_gira) * 14 * (1 - seg(t, t_ytu - 0.2, t_ytu + 0.3))
    S["motor"].rotation_euler = (0, 0, spin)
    bob = seg(t, t_usas + 0.2, t_usas + 1.0)
    place(S["bobina"], t > t_usas + 0.2, (0, -9 * (1 - bob), 0))
    show(S["iman"], t > t_usas + 0.2)
    S["iman"].scale = (max(bob, 0.001),) * 3
    # oscilación del cabezal
    tilt = 0.0; rotz = spin if t < t_ytu + 0.3 else 0.0
    if t_ytu - 0.1 < t < t_usas:
        tilt = 0.06 * math.sin((t - t_ytu) * 2 * math.pi * 1.6) * seg(t, t_ytu, t_ytu + 0.4)
    sgn = 0
    if t_c1 < t < t_c2: sgn = 1; tilt = 0.17 * seg(t, t_der - 0.4, t_der + 0.3)
    elif t_c2 <= t < t_otra: sgn = -1; tilt = mix(0.17, -0.17, seg(t, t_izq - 0.4, t_izq + 0.2))
    elif t_otra <= t < t_cur - 0.2:
        f = mix(1.5, 7.5, seg(t, t_otra, t_cons + 0.8)); tilt = 0.09 * math.sin((t - t_otra) * 2 * math.pi * f + math.pi / 2) * -1
        tilt = -0.17 * math.cos((t - t_otra) * 2 * math.pi * f) if t < t_cons + 0.8 else 0.09 * math.sin(t * 2 * math.pi * 7.5)
        sgn = 1 if tilt > 0 else -1
    elif t > t_carga - 0.2: tilt = 0.06 * math.sin(t * 2 * math.pi * 7.5)
    S["cab"].rotation_euler = (0, tilt, rotz)
    gh = win01(t, t_cons + 0.6, t_cur - 0.2, 0.4, 0.3)
    for e, sx in zip(S["fant"], (-1, 1)):
        place(e, gh > 0.05, (0, 0, PIV)); e.rotation_euler = (0, 0.09 * sx, 0)
    # cables y corriente
    wires = t > t_pones + 0.6
    tops = [(0.9, -0.3, 10.4), (-0.9, -0.3, 10.4)] if t > t_usas + 0.6 else [(0.5, -0.5, 8.6), (-0.5, -0.5, 8.6)]
    for o, x, tp in zip(S["cables"], (0.4, -0.4), tops):
        if wires and not (t_usas - 0.1 < t < t_usas + 0.6): bar_set(o, (x, -0.5, 8.0), tp)
        else: bar_set(o, LEJOS, Vector(LEJOS) + Vector((0, 0, 0.01)))
    curr_on = (t_c1 < t < t_cur - 0.2) or (t_pones + 1.0 < t < t_usas - 0.1)
    if t_pones < t < t_usas: sgn = 1
    for k, o in enumerate(S["corr"]):
        if not curr_on or sgn == 0: o.location = LEJOS; continue
        u = ((t * 0.9 * (1 if sgn > 0 else -1)) + k / 10) % 1
        p0, p1 = (Vector((0.4, -0.85, 8.0)), Vector((-0.4, -0.85, 8.0)))
        a, b = Vector(tops[0]) + Vector((0, -0.3, 0)), Vector(tops[1]) + Vector((0, -0.3, 0))
        o.location = poly([p0, a, b, p1], u)
    # batería
    lvl = 0.75
    if t > t_base: lvl = 0.15 + 0.85 * seg(t, t_otra_b + 0.4, t_sin)
    if t > t_carga: lvl = 1 - 0.85 * seg(t, t_carga + 0.4, DUR - 0.6)
    S["carga"].scale = (0.5, 0.12, max(4.6 * lvl, 0.01)); S["carga"].location = (0, -0.78, 3.2 + 2.3 * lvl)
    set_color(S["carga"], GREEN if lvl > 0.3 else CORAL)
    # base y carga
    bse = seg(t, t_base - 0.2, t_base + 0.8)
    place(S["base"], t > t_base - 0.2, (0, 0, -12 * (1 - bse)))
    place(S["bob_m"], t > t_otra_b - 0.3, (0, -6 * (1 - seg(t, t_otra_b - 0.3, t_otra_b + 0.4)), 0))
    fld = win01(t, T("campo") - 0.4, t_sin + 0.5, 0.4, 0.5)
    for k, o in enumerate(S["campo"]):
        if fld < 0.02: o.location = LEJOS; continue
        R = o["R"]; pul = 0.85 + 0.15 * math.sin(t * 6 - k)
        o.location = (R * pul, 0, -0.6); o.scale = (pul * fld, pul * fld, pul * fld)
        set_color(o, tuple(c * (0.7 + 0.3 * math.sin(t * 6 - k)) for c in FIELD))
    c2on = t_otra_b + 0.6 < t < t_sin + 0.3
    for k, o in enumerate(S["corr2"]):
        if not c2on: o.location = LEJOS; continue
        u = (t * 0.8 + k / 8) % 1; sx = 1 if k % 2 else -1
        o.location = poly([(0.95 * sx, -0.9, 1.5), (0.6 * sx, -0.9, 2.2), (0.3 * sx, -0.9, 3.0)], u)
    set_color(S["ledA"], GREEN if t > t_otra_b else TEAL)
    # ---- arcadas y reloj ----
    c = clock(t); zone = min(3, int(c // 30))
    ZONES = [(True, range(0, 8)), (True, range(8, 16)), (False, range(8, 16)), (False, range(0, 8))]
    for (up, i), o in S["dientes"].items():
        col = TOOTH
        for zi, (zu, rg) in enumerate(ZONES):
            if zu == up and i in rg:
                if c >= 30 * (zi + 1) - 0.1: col = (0.55, 0.95, 0.75)
                elif zi == zone and c > 0: col = (0.75, 0.9, 1.0)
        set_color(o, col)
    dz = T("ahora") - 0.3 < t < t_falta - 0.1
    if dz:
        up, rg = ZONES[zone]; k = (c % 30) / 30
        i = list(rg)[min(7, int(k * 8))]; (x, y), th = arch_pos(i, up)
        (x2, y2), _ = arch_pos(list(rg)[min(7, int(k * 8) + 1)], up)
        fr = (k * 8) % 1; x, y = mix(x, x2, fr), mix(y, y2, fr)
        w = 0 if paused(t) else 0.18 * math.sin(t * 2 * math.pi * 7.5)
        S["mini"].location = (x + w, y, 0.2); S["mini"].rotation_euler = (0, 0, (-th if up else th) + (0 if up else math.pi) + (0 if (i < 8) == up else 0))
        show(S["mini"], True)
    else: place(S["mini"], False, LEJOS)
    # ---- enchufe mojado ----
    pz = t_falta - 0.3 < t < t_base
    for k, o in enumerate(S["gotasP"]):
        if not pz or t < t_agua: o.location = LEJOS; continue
        u = ((t - t_agua) * 1.3 + k / 6) % 1
        o.location = (PX + (k % 3 - 1) * 0.7, -1.6, 9 - 8.4 * u); o.scale = (1, 1, 1.3)
    sp = pz and t > t_agua + 0.5 and int(t * 10) % 3 != 0
    for k, o in enumerate(S["chispa"]):
        if not sp: o.location = LEJOS; continue
        a = k * 0.785 + t * 3; r = 0.8 + 0.8 * RNG.random()
        o.location = (PX + r * math.cos(a), -1.6, 0.6 + r * math.sin(a))
    apply_cam(S["cam"], *camera(t))

def VD(at, dist, yaw, pitch, lens=40):
    at = Vector(at); y, p = math.radians(yaw), math.radians(pitch)
    return (tuple(at + dist * Vector((math.sin(y) * math.cos(p), -math.cos(y) * math.cos(p), math.sin(p)))), tuple(at), lens)

_SH = None
def shots():
    global _SH
    if _SH: return _SH
    H = Vector(HEAD2)
    sh = []
    def shot(t0, keys): sh.append((t0, [(a,) + b for a, b in keys]))
    hz = (TX, 1.4, 4.9)
    shot(0.0, [(0, VD(hz, 10.5, -30, 30)), (2.4, VD(hz, 12.5, -12, 34)), (T("vamos"), VD((TX, 2, 5.2), 16, 8, 32)),
               (T("frota"), VD(hz, 15, -22, 28)), (T("así que pones"), VD(hz, 16, -10, 30))])
    shot(T("así que pones") - 0.05, [(T("así que pones"), VD((0, 0, 9.5), 23, -14, 8)), (T("pero un motor"), VD((0, 0, 13), 25, 10, 8)),
               (T("y tú"), VD((0, 0, 17), 23, -6, 6)), (T("vibre") + 0.8, VD((0, 0, 17.5), 23, 4, 6)), (T("así que usas"), VD((0, 0, 11), 17, -12, 6)), (T("cuando la"), VD((0, 0, 11.6), 14, 8, 4)),
               (T("una y otra"), VD((0, 0, 13), 22, -6, 5)), (T("así consigues") + 0.5, VD((0, 0, 21.5), 14, 8, 5)), (T("y aquí"), VD((0, 0, 22), 12, -8, 5))])
    shot(T("y aquí") - 0.1, [(T("y aquí"), VD(hz, 13, -24, 34)), (T("las cerdas"), VD((TX, 1.0, 4.4), 9.5, -18, 24)),
               (T("y el líquido") + 0.3, VD((TX, 1.4, 3.8), 10, 72, 12)), (T("donde"), VD((TX, 1.4, 3.8), 10, 96, 14)),
               (T("pero si"), VD((TX, 2.4, 6.6), 19, -22, 22)), (T("por eso"), VD((TX, 5.5, 6.5), 17, 22, 22)),
               (T("ahora"), VD((TX, 6, 6.8), 17, 30, 24))])
    shot(T("ahora") - 0.05, [(T("ahora"), VD((DX, 0.3, 0), 44, 0, 74)), (T("cuatro zonas"), VD((DX, 0.3, 0), 40, 6, 76)),
               (T("falta"), VD((DX, 0.3, 0), 40, -4, 78))])
    shot(T("falta") - 0.05, [(T("falta"), VD((PX, 0, 1.5), 22, -18, 10)), (T("pero el agua"), VD((PX, 0, 1.5), 18, 10, 12)),
               (T("así que la base"), VD((PX, 0, 1), 17, 16, 10))])
    shot(T("así que la base") - 0.05, [(T("así que la base"), VD((0, 0, 1.5), 22, -14, 10)), (T("campo"), VD((0, 0, 1.0), 17, 12, 10)),
               (T("otra bobina") + 0.3, VD((0, 0, 3), 17, -10, 6)), (T("sin ningún") + 0.3, VD((0, 0, 18), 42, 8, 6)),
               (T("con una carga") + 0.3, VD((0, 0, 20.5), 24, -10, 8)), (DUR - 0.8, VD((0, 0, 19.5), 30, 6, 8)), (DUR + 3, VD((0, 0, 19), 36, 8, 8))])
    _SH = sh; return sh

def camera(t):
    sh = shots(); cur = sh[0]
    for s in sh:
        if t >= s[0]: cur = s
    ks = cur[1]
    if len(ks) == 1: ks = ks + [(ks[0][0] + 10,) + ks[0][1:]]
    return cam_state(t, ks, drift=0.08)

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v)
    c = Vector(S["cab"].location)
    return {"head2": Pj(HEAD2 + Vector((0, 0, 0.6))), "gap": Pj((TX + 1.3, 1.4, 3.2)), "gap2": Pj((TX + 1.3, 4.2, 3.2)), "led2": Pj((TX, 7.2, 3.0)),
            "motor": Pj((0.8, -0.8, 9.6)), "headA": Pj((0, -1, 21)), "iman": Pj((0.8, -0.4, PIV + 0.55)), "bobina": Pj((0.9, -0.6, 10.4)),
            "bat": Pj((0.8, -0.8, 5)), "bob_m": Pj((1.0, -0.9, 1.0)), "base": Pj((2.0, -1.8, -1.5)), "headAl": Pj((-1.6, -1, 21)),
            "headAr": Pj((1.6, -1, 21)), "plug": Pj((PX, -1.6, 1.8)), "arch": Pj((DX, 0, 0)), "brushA": Pj((0, -1.4, 8))}

if __name__ == "__main__":
    run("cepillo", build, pose, anchors)
