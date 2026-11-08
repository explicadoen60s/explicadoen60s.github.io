# «Así funciona la TDT»: primer plano de un mando cambiando de canal hasta que la tele se queda sin señal; la antena del
# tejado (casa en corte) y la señal bajando por el cable; torre en un monte que lanza ondas en línea recta hasta la antena;
# paquete (múltiple) con cinco canales que se convierten en ceros y unos sobre una sola frecuencia; en la pantalla de la
# tele, barrido de 470 a 694 MHz con una aguja que va descubriendo los múltiples y una lista de canales; el mando salta al
# canal 1; cinco cadenas cambian de múltiple y la tele va al hueco vacío (sin señal); múltiple nuevo en DVB-T2 con más
# datos en el mismo ancho; menú, búsqueda automática y la tele vuelve a encontrarlo todo con la misma antena.
import bpy, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector, Matrix

T, DUR = cargar("tdt")
BG = (0.11, 0.08, 0.2); GROUND = (0.16, 0.2, 0.17); MOUNT = (0.22, 0.2, 0.3); WALL = (0.86, 0.78, 0.66); WALL_OUT = (0.93, 0.9, 0.85)
ROOF = (0.72, 0.3, 0.22); FLOOR = (0.55, 0.38, 0.25); WOOD = (0.42, 0.28, 0.18); TVBODY = (0.09, 0.09, 0.11); SCREEN = (0.03, 0.04, 0.06)
ALU = (0.78, 0.8, 0.84); WAVE = (0.3, 0.95, 0.85); BEAM = (1.0, 0.9, 0.4); SKIN = (0.93, 0.72, 0.58); REMOTE = (0.16, 0.17, 0.2)
NEEDLE = (1.0, 0.85, 0.15); GLASS = (0.75, 0.95, 1.0); GRAY = (0.45, 0.47, 0.52)
CHC = [(0.95, 0.3, 0.3), (1.0, 0.6, 0.15), (0.35, 0.8, 0.35), (0.85, 0.35, 0.85), (0.3, 0.6, 1.0), (0.2, 0.85, 0.85)]
LEJOS = (0, 0, -900)
TVZ = 38.0; SY = -2.85                         # centro de la pantalla y plano del contenido
TT = Vector((-150, 900, 392))                  # punta de la torre
ANT = Vector((30, -38, 180))                   # antena del tejado
D = (ANT - TT).normalized()                    # dirección de la señal
SIDE = D.cross(Vector((0, 0, 1))).normalized()  # lado (hacia -x)
REM = Vector((-4, -44, 23))                    # mando
PEAKS = [498, 530, 562, 594, 626, 650]
T2F = 682
CABLE = [(30, -38, 160), (30, -38, 152), (30, 2, 119), (30, 4, 110), (30, 4, 44), (8, 2.5, 40)]
# cinco cadenas que cambian de múltiple: (pico, hueco) → (pico, hueco)
MOVES = [((0, 0), (3, 4)), ((1, 1), (4, 4)), ((2, 2), (5, 4)), ((3, 2), (1, 4)), ((4, 3), (2, 4))]
RNG = random.Random(11)

def FX(f): return -21 + (f - 470) * 24 / 224
def alpha(o, a):
    m = o.active_material; m.diffuse_color = (*m.diffuse_color[:3], a); m.surface_render_method = 'BLENDED'
def show(o, on):
    o.hide_render = not on
    for c in o.children: show(c, on)
def hide_bar(o): bar_set(o, LEJOS, Vector(LEJOS) + Vector((0, 0, 0.01)))
def poly(pts, u):
    P = [Vector(p) for p in pts]; L = [(b - a).length for a, b in zip(P, P[1:])]; s = u * sum(L)
    for a, b, l in zip(P, P[1:], L):
        if s <= l: return a.lerp(b, s / max(l, 1e-6))
        s -= l
    return P[-1]
def sbox(w, h, x, z, col, parent, dy=0.0, unique=False):
    """rectángulo plano sobre la pantalla"""
    return box((w, 0.12, h), (x, SY - dy, z), col, parent=parent, unique=unique)
def stext(s, x, z, size, col, parent, align="CENTER", dy=0.25):
    return text3d(s, (x, SY - 0.1 - dy, z), size, col, parent=parent, rot=(math.pi / 2, 0, 0), align=align, unique=True, extrude=0.01)

def pkt_basis():
    dh = Vector((D.x, D.y, 0)).normalized(); y = -SIDE
    return Matrix((dh, y, Vector((0, 0, 1)))).transposed()

def build():
    sc, cam = scene_setup(world=BG, shadow=0.32, light_rot=60)
    S = {"cam": cam}
    # ---------------- paisaje ----------------
    box((5000, 5000, 1), (0, 1200, -0.6), GROUND)
    bpy.ops.mesh.primitive_cone_add(radius1=480, radius2=26, depth=310, location=(TT.x, TT.y, 155), vertices=9); setup(bpy.context.object, MOUNT)
    bpy.ops.mesh.primitive_cone_add(radius1=380, radius2=40, depth=200, location=(TT.x + 520, TT.y + 260, 100), vertices=8); setup(bpy.context.object, (0.2, 0.18, 0.27))
    bpy.ops.mesh.primitive_cone_add(radius1=420, radius2=40, depth=170, location=(TT.x - 600, TT.y + 150, 85), vertices=7); setup(bpy.context.object, (0.19, 0.17, 0.26))
    # torre de celosía
    base = 310
    for sx in (-1, 1):
        for sy in (-1, 1):
            o = bar_obj((0.92, 0.92, 0.92), 1.4); bar_set(o, (TT.x + sx * 13, TT.y + sy * 13, base), (TT.x + sx * 3, TT.y + sy * 3, TT.z - 6))
    for k in range(6):
        z = base + 12 + 12 * k; w = 13 - 10 * (z - base) / (TT.z - 6 - base)
        col = (0.95, 0.25, 0.2) if k % 2 else (0.92, 0.92, 0.92)
        for a, b in (((-w, -w), (w, w)), ((w, -w), (-w, w))):
            o = bar_obj(col, 0.8); bar_set(o, (TT.x + a[0], TT.y + a[1], z), (TT.x + b[0], TT.y + b[1], z + 12))
        for a, b in (((-w, -w), (w, -w)), ((w, -w), (w, w)), ((w, w), (-w, w)), ((-w, w), (-w, -w))):
            o = bar_obj(col, 0.7); bar_set(o, (TT.x + a[0], TT.y + a[1], z), (TT.x + b[0], TT.y + b[1], z))
    for k, a in enumerate((0.3, 2.4, 4.5)):
        box((5, 2, 9), (TT.x + 5 * math.cos(a), TT.y + 5 * math.sin(a), TT.z - 14 + 3 * k), (0.85, 0.85, 0.88), rot=(0, 0, a))
    sph(1.6, tuple(TT + Vector((0, 0, 2))), (1, 0.2, 0.2))
    # casas vecinas con su antena
    for k in range(16):
        x = RNG.choice((-1, 1)) * RNG.uniform(140, 520); y = RNG.uniform(-120, 650)
        w, dpt, h = RNG.uniform(50, 90), RNG.uniform(50, 80), RNG.uniform(40, 80)
        box((w, dpt, h), (x, y, h / 2), WALL_OUT)
        bpy.ops.mesh.primitive_cone_add(radius1=w * 0.75, radius2=0, depth=h * 0.45, location=(x, y, h + h * 0.22), vertices=4, rotation=(0, 0, math.pi / 4))
        o = bpy.context.object; o.scale = (1, dpt / w, 1); setup(o, ROOF)
        cyl(0.8, 22, (x, y, h + h * 0.45 + 8), ALU, v=8); box((1, 18, 1), (x, y, h + h * 0.45 + 16), ALU)
    for k in range(26):
        x = RNG.uniform(-700, 700); y = RNG.uniform(-60, 800)
        if abs(x) < 110 and y < 60: continue
        bpy.ops.mesh.primitive_cone_add(radius1=RNG.uniform(10, 16), radius2=0, depth=RNG.uniform(30, 48), location=(x, y, 22), vertices=8)
        setup(bpy.context.object, (0.15, 0.36, 0.25))
    # ---------------- casa en corte ----------------
    box((140, 92, 2), (0, -38, -1), FLOOR)
    box((144, 2, 113), (0, 8, 56), WALL); box((144, 2.4, 113), (0, 9.5, 56), WALL_OUT)
    for sx in (-1, 1):
        box((2, 92, 113), (sx * 71, -38, 56), WALL); box((2.4, 92, 113), (sx * 72.5, -38, 56), WALL_OUT)
    box((146, 94, 3), (0, -38, 113.5), (0.95, 0.93, 0.9))
    ang = math.atan2(37, 48)
    for sy in (-1, 1):
        box((154, 62, 3), (0, -38 + sy * 24, 133), ROOF, rot=(-sy * ang, 0, 0))
    for sx in (-1, 1):   # hastiales laterales
        bpy.ops.mesh.primitive_cone_add(radius1=48, radius2=0, depth=2, vertices=3, location=(sx * 72, -38, 115), rotation=(0, math.pi / 2, math.pi / 2))
        o = bpy.context.object; o.scale = (1, 37 / 24, 1); setup(o, WALL_OUT)
    box((156, 4, 4), (0, -38, 151), (0.6, 0.25, 0.18))
    # salón
    box((112, 36, 20), (0, -12, 10), WOOD); box((108, 0.4, 16), (0, -30.2, 10), (0.5, 0.35, 0.24))
    for x in (-27, 27): box((0.4, 0.5, 15), (x, -30.4, 10), (0.32, 0.2, 0.13))
    box((16, 9, 1.4), (0, -2, 20.7), TVBODY); box((4, 2, 5), (0, 0.5, 23), TVBODY)
    S["tv"] = tv = box((52, 2.4, 31), (0, -1.2, TVZ), TVBODY)
    box((48, 0.2, 27), (0, -2.5, TVZ), SCREEN)
    cyl(0.5, 0.3, (21, -2.5, TVZ - 14.6), (0.2, 0.9, 0.3), rot=(math.pi / 2, 0, 0))
    # sofá al fondo no: lámpara y planta
    cyl(9, 2, (-52, -20, 1), (0.7, 0.45, 0.3)); cyl(1, 60, (-52, -20, 31), (0.25, 0.25, 0.28))
    bpy.ops.mesh.primitive_cone_add(radius1=10, radius2=6, depth=12, location=(-52, -20, 64)); setup(bpy.context.object, (1.0, 0.92, 0.7))
    cyl(6, 14, (55, -20, 27), (0.85, 0.85, 0.82)); sph(11, (55, -20, 42), (0.2, 0.55, 0.3), scale=(1, 1, 1.4))
    box((40, 1, 26), (-30, 7, 80), (0.35, 0.55, 0.75)); box((44, 0.8, 30), (-30, 7.2, 80), (0.95, 0.95, 0.95))
    # cable coaxial
    for a, b in zip(CABLE, CABLE[1:]):
        o = bar_obj((0.15, 0.15, 0.17), 0.7); bar_set(o, a, b)
    S["pulsos"] = [sph(1.3, LEJOS, WAVE, seg=10) for _ in range(10)]
    # antena (Yagi) apuntando a la torre
    S["antena"] = a = empty(ANT); a.rotation_euler = (0, 0, math.atan2(-D.x, -D.y) * -1)
    cyl(1.0, 32, (0, 0, -14), ALU, parent=a, v=12)
    box((1.2, 46, 1.2), (0, 0, 0), ALU, parent=a)
    S["elem"] = []
    for k in range(9):
        L = 26 - 1.6 * k if k else 30
        S["elem"].append(cyl(0.45, L, (0, -20 + 5 * k, 0), ALU, parent=a, rot=(0, math.pi / 2, 0), v=8, unique=True))
    box((5, 3, 4), (0, -23, 0), (0.25, 0.25, 0.28), parent=a)
    # ---------------- señal ----------------
    S["anillos"] = [torus(1, 0.035, LEJOS, WAVE, unique=True) for _ in range(7)]
    S["haz"] = bar_obj(BEAM, 0.9, unique=True); S["luz"] = sph(3.2, LEJOS, (1, 1, 0.85), seg=16)
    S["portadora"] = [sph(0.9, LEJOS, WAVE, seg=8) for _ in range(70)]
    # paquete (múltiple)
    S["pkt"] = p = empty(LEJOS)
    o = box((14, 14, 22), (0, 0, 0), GLASS, parent=p, unique=True); alpha(o, 0.22)
    for x in (-7, 7):
        for z in (-11, 11):
            o = bar_obj(WAVE, 0.35, parent=p); bar_set(o, (x, -7, z), (x, 7, z)); o.location = Vector((x, -7, z))
    for x in (-7, 7):
        for y in (-7, 7):
            o = bar_obj(WAVE, 0.35, parent=p); bar_set(o, (x, y, -11), (x, y, 11))
    for y in (-7, 7):
        for z in (-11, 11):
            o = bar_obj(WAVE, 0.35, parent=p); bar_set(o, (-7, y, z), (7, y, z))
    S["canales"] = []; S["bits"] = []
    for k in range(5):
        c = empty(LEJOS)
        box((10, 1.0, 3.4), (0, 0, 0), CHC[k], parent=c); box((10.6, 0.8, 4.0), (0, 0.3, 0), (0.12, 0.12, 0.14), parent=c)
        text3d(str(k + 1), (-3.4, -0.6, 0), 2.6, (1, 1, 1), parent=c, rot=(math.pi / 2, 0, 0), unique=True)
        S["canales"].append(c)
        bs = []
        for j in range(8):
            bs.append(box((1.5, 1.2, 1.5), LEJOS, (1, 1, 1), unique=True))
        S["bits"].append(bs)
    # ---------------- mando y mano ----------------
    S["mando"] = m = empty(REM); m.rotation_euler = (0.32, 0, -0.12)
    rounded_slab(5.6, 18, 1.8, 1.8, (0, 0, -0.9), REMOTE, parent=m)
    cyl(0.75, 0.5, (1.5, 7, 1.0), (0.9, 0.2, 0.2), parent=m)
    for i in range(3):
        for j in range(4):
            cyl(0.55, 0.45, (-1.6 + 1.6 * i, 3.6 - 1.6 * j, 1.0), (0.6, 0.62, 0.66), parent=m)
    for j in range(2): box((3.6, 1.1, 0.5), (0, -3.5 - 1.6 * j, 1.0), (0.35, 0.37, 0.42), parent=m)
    cyl(0.6, 0.6, (0, 9.1, 0), (0.5, 0.1, 0.1), parent=m, rot=(math.pi / 2, 0, 0))
    sph(4.2, (0, -5, -2.2), SKIN, parent=m, scale=(1.05, 1.5, 0.85))
    for k in range(4): sph(1.2, (3.4, -1.5 - 2.3 * k, -0.6), SKIN, parent=m, scale=(0.8, 1, 1.6))
    S["pulgar"] = th = empty((-3.0, -6.5, 1.6), parent=m)
    cyl(1.15, 6, (0, 3, 0), SKIN, parent=th, rot=(math.pi / 2, 0, 0)); sph(1.15, (0, 6, 0), SKIN, parent=th)
    sph(1.4, (0, 0, -0.2), SKIN, parent=th)
    th.rotation_euler = (0, 0, -0.45)
    S["ir"] = [sph(0.7, LEJOS, (1.0, 0.35, 0.35), seg=8) for _ in range(5)]
    # ---------------- pantalla ----------------
    # imagen de un canal
    S["pic"] = pc = empty((0, 0, 0))
    S["cielo"] = sbox(47.6, 26.6, 0, TVZ, (0.4, 0.7, 1.0), pc, unique=True)
    S["sol"] = sph(3.2, (0, SY - 0.3, 0), (1, 0.9, 0.4), parent=pc, scale=(1, 0.2, 1), unique=True)
    S["colinas"] = []
    for x, sz in ((-14, 10), (2, 8), (14, 9)):
        S["colinas"].append(box((sz, 0.12, sz), (x, SY - 0.3, TVZ - 5.3), (0.3, 0.7, 0.35), parent=pc, rot=(0, math.pi / 4, 0), unique=True))
    S["colinas"].append(sbox(47.6, 8, 0, TVZ - 9.3, (0.3, 0.7, 0.35), pc, dy=0.6, unique=True))
    S["nube"] = nb = empty((0, SY - 0.4, TVZ + 7), parent=pc)
    for dx, r in ((-2.4, 1.8), (0, 2.4), (2.4, 1.7)): sph(r, (dx, 0, 0), (1, 1, 1), parent=nb, scale=(1, 0.2, 0.8))
    # nieve
    S["noise"] = nz = empty((0, 0, 0)); S["celdas"] = []
    for i in range(16):
        for j in range(9):
            S["celdas"].append(box((3.0, 0.12, 3.0), (-22.5 + 3 * i, SY - 0.2, TVZ - 12 + 3 * j), (0.5, 0.5, 0.5), parent=nz, unique=True))
    # espectro
    S["spec"] = sp = empty((0, 0, 0))
    sbox(25, 0.35, -9, 27.4, (0.8, 0.82, 0.9), sp)
    for f in (470, 526, 582, 638, 694): sbox(0.25, 0.9, FX(f), 27.0, (0.8, 0.82, 0.9), sp)
    stext("470", FX(470), 25.4, 1.5, (0.8, 0.82, 0.9), sp); stext("694", FX(694), 25.4, 1.5, (0.8, 0.82, 0.9), sp)
    stext("MHz", -9, 25.4, 1.3, (0.6, 0.62, 0.7), sp)
    sbox(0.2, 25, 5.0, TVZ, (0.25, 0.27, 0.33), sp)
    S["bloques"] = {}; S["huecos"] = []
    for i, f in enumerate(PEAKS):
        for j in range(4):
            S["bloques"][(i, j)] = sbox(2.0, 1.5, FX(f), 29.0 + 1.8 * j, CHC[(i + j) % 6], sp, dy=0.15, unique=True)
            S["huecos"].append(sbox(2.0, 1.5, FX(f), 29.0 + 1.8 * j, (0.2, 0.22, 0.28), sp, dy=0.05))
    S["t2"] = [sbox(2.0, 1.5, FX(T2F), 29.0 + 1.8 * j, (1.0, 0.8, 0.2), sp, dy=0.15, unique=True) for j in range(7)]
    S["aguja"] = ag = empty((FX(470), 0, 0), parent=sp)
    sbox(0.4, 21, 0, 38.3, NEEDLE, ag, dy=0.4); sph(0.9, (0, SY - 0.5, 49.2), NEEDLE, parent=ag, scale=(1, 0.3, 1))
    S["filas"] = []
    for k in range(7):
        r = empty((0, 0, 0), parent=sp); z = 48.5 - 3.2 * k
        hl = sbox(12.6, 2.8, 11.6, z, (0.2, 0.22, 0.28), r, dy=0.02, unique=True)
        chip = sbox(1.7, 1.7, 6.9, z, (1, 1, 1), r, dy=0.1, unique=True)
        num = stext(str(k + 1), 9.2, z, 2.4, (1, 1, 1), r)
        fr = stext("000", 14.2, z, 2.4, (0.75, 0.95, 1.0), r)
        S["filas"].append((r, hl, chip, num, fr))
    S["progreso"] = sbox(1, 1.2, 0, 51.0, WAVE, sp, dy=0.2, unique=True)
    # menú
    S["menu"] = mn = empty((0, 0, 0))
    sbox(24, 16, 0, TVZ, (0.12, 0.14, 0.2), mn, dy=0.4)
    for k in range(3):
        sbox(20, 3.2, 0, TVZ + 4.5 - 4.5 * k, (0.3, 0.6, 1.0) if k == 1 else (0.25, 0.27, 0.34), mn, dy=0.6)
        sbox(10 if k != 1 else 14, 0.8, -2 if k != 1 else 0, TVZ + 4.5 - 4.5 * k, (0.85, 0.87, 0.92), mn, dy=0.8)
    dyn = [cam, S["pulsos"], S["antena"], S["anillos"], S["haz"], S["luz"], S["portadora"], S["pkt"], S["canales"], S["bits"],
           S["mando"], S["ir"], S["pic"], S["noise"], S["spec"], S["menu"]]
    join_static(dyn)
    return sc, S

# ---------------------------------------------------------------------------------------------------
def presses():
    return [0.08, 0.74, 1.42, T("el uno") - 0.1, T("tu tele va") + 0.3, T("menú") - 0.05, T("búsqueda") + 0.1]

def channel_pic(t):
    """qué canal se ve (índice de color) o None"""
    if t < 0.74: return 2
    if t < 1.42: return 4
    return None

def mode(t):
    if t < 1.5: return "pic"
    if t < T("tu tele no") - 0.2: return "noise"
    if t < T("salta") + 0.2: return "spec"
    if t < T("y aquí"): return "pic1"
    if t < T("y no encuentra") + 0.05: return "spec"
    if t < T("además") - 0.1: return "noise"
    if t < T("menú") + 0.1: return "spec"
    if t < T("búsqueda") + 0.1: return "menu"
    if t < T("no hace") - 0.2: return "spec"
    return "pic1"

def needle_f(t):
    t0, t1 = T("escucha"), T("megahercios", fin=True)
    if t < T("y aquí"):
        f = 470 + 224 * seg(t, t0, t1) if t < T("el uno") else 694
        if t >= T("el uno") - 0.1: f = mix(694, PEAKS[0], seg(t, T("el uno"), T("el uno") + 0.5))
        return f
    if t < T("menú"):
        f = mix(PEAKS[0], 470, seg(t, T("y aquí"), T("y aquí") + 0.6))
        return mix(f, PEAKS[0], seg(t, T("tu tele va") + 0.3, T("tu tele va") + 0.8))
    r0, r1 = T("búsqueda") + 0.3, T("frecuencias", fin=True)
    f = 470 + 224 * seg(t, r0, r1) if t < r1 + 0.2 else 694
    return mix(f, PEAKS[3], seg(t, r1 + 0.2, r1 + 0.6))

def found(t, f):
    """momento en que el barrido encuentra la frecuencia f"""
    t0, t1 = T("escucha"), T("megahercios", fin=True)
    # inversa aproximada del seg suavizado
    lo, hi = t0, t1
    for _ in range(30):
        m = (lo + hi) / 2
        if 470 + 224 * seg(m, t0, t1) < f: lo = m
        else: hi = m
    return lo

def found2(f):
    r0, r1 = T("búsqueda") + 0.3, T("frecuencias", fin=True); lo, hi = r0, r1
    for _ in range(30):
        m = (lo + hi) / 2
        if 470 + 224 * seg(m, r0, r1) < f: lo = m
        else: hi = m
    return lo

def slot_pos(i, j): return Vector((FX(PEAKS[i]), SY - 0.15, 29.0 + 1.8 * j))

def pkt_pos(t):
    s = keyed(t, [(0, 190), (T("cada canal"), 190), (T("a ese paquete"), 95), (T("tu tele no") - 0.9, 40), (T("tu tele no") - 0.3, 0)])
    return ANT - D * s + Vector((0, 0, 4))

def pose(t, S):
    md = mode(t)
    # -------- mando --------
    P = presses()
    vis_m = t < T("la antena") + 0.4 or (T("cuando pulsas") - 0.4 < t < T("y aquí")) or (T("tu tele va") - 0.3 < t < T("además")) \
        or (T("la solución") < t < T("y la tele vuelve"))
    if vis_m:
        ins = [T("cuando pulsas") - 0.4, T("tu tele va") - 0.3, T("la solución")]
        off = [T("y aquí"), T("además"), T("y la tele vuelve")]
        u = 1.0
        for a, b in zip(ins, off):
            if a < t < b: u = seg(t, a, a + 0.5) * (1 - seg(t, b - 0.5, b))
        if t < 3: u = 1 - seg(t, T("la antena") - 0.2, T("la antena") + 0.4)
        S["mando"].location = REM + Vector((0, -6, -22)) * (1 - u)
    else: S["mando"].location = LEJOS
    show(S["mando"], vis_m)
    bpy.context.view_layer.update()
    pr = 0.0
    for p in P:
        if p - 0.12 < t < p + 0.3: pr = max(pr, seg(t, p - 0.12, p) * (1 - seg(t, p + 0.1, p + 0.3)))
    S["pulgar"].rotation_euler = (-0.28 * pr, 0, -0.45)
    tip = S["mando"].matrix_world @ Vector((0, 9.6, 0)) if vis_m else Vector(LEJOS)
    for k, o in enumerate(S["ir"]):
        o.location = LEJOS
        for p in P:
            u = (t - p - 0.04 * k) / 0.35
            if 0 <= u <= 1 and vis_m: o.location = tip.lerp(Vector((0, -3, TVZ)), u)
    # -------- pantalla --------
    show(S["pic"], md in ("pic", "pic1")); show(S["noise"], md == "noise"); show(S["spec"], md == "spec"); show(S["menu"], md == "menu")
    if md in ("pic", "pic1"):
        c = channel_pic(t) if md == "pic" else 0
        sky = [(0.45, 0.75, 1.0), (0.55, 0.85, 1.0), (1.0, 0.65, 0.45), (0.5, 0.8, 1.0), (0.95, 0.55, 0.7)][c if c is not None else 0]
        set_color(S["cielo"], sky)
        for k, o in enumerate(S["colinas"]): set_color(o, [(0.35, 0.5, 0.75), (0.3, 0.45, 0.7), (0.4, 0.55, 0.8), (0.3, 0.7, 0.35)][k] if c != 2 else [(0.85, 0.5, 0.3), (0.7, 0.4, 0.25), (0.9, 0.6, 0.35), (0.95, 0.8, 0.45)][k])
        S["sol"].location = (14 - 3 * math.sin(t * 0.8), SY - 0.3, TVZ + 6 + 1.5 * math.sin(t * 1.3))
        S["nube"].location = (-24 + ((t * 6) % 48), SY - 0.4, TVZ + 7)
    if md == "noise":
        r = random.Random(int(t * 30))
        for o in S["celdas"]:
            v = r.random() ** 1.5; set_color(o, (v, v, v))
    if md == "spec": pose_spec(t, S)
    # -------- antena y cable --------
    hit = win01(t, T("hasta la antena"), T("cada canal") + 0.4, 0.2, 0.4) + win01(t, T("la antena") - 0.1, T("qué ha") + 0.2, 0.2, 0.3)
    for k, o in enumerate(S["elem"]):
        fl = 0.5 + 0.5 * math.sin(t * 14 - k * 0.9)
        u = hit * fl if t > 6 else 0.75 * hit
        set_color(o, tuple(mix(c, d, u) for c, d in zip(ALU, (0.3, 1.0, 0.6) if t < 6 else WAVE)))
    cab = (T("mira cómo") - 0.1 < t < T("desde una") + 0.2) or (T("tu tele no") - 0.4 < t < T("tu tele no") + 1.4)
    for k, o in enumerate(S["pulsos"]):
        o.location = poly(CABLE, (t * 0.7 + k / 10) % 1) if cab else LEJOS
    # -------- ondas desde la torre --------
    rg = T("desde una") + 0.6 < t < T("cada canal") + 0.6
    for k, o in enumerate(S["anillos"]):
        if not rg: o.location = LEJOS; continue
        u = (t * 0.32 + k / 7) % 1
        o.location = TT.lerp(ANT, u); R = 4 + 150 * u
        o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(D)
        fade = min(1, u * 8) * (1 - seg(t, T("cada canal"), T("cada canal") + 0.6)) * seg(t, T("desde una") + 0.6, T("desde una") + 1.4)
        o.scale = (R * fade + 0.01,) * 3
    b0, b1 = T("viajan en"), T("hasta la antena") + 0.6
    if b0 - 0.1 < t < b1 + 0.3:
        u = seg(t, b0 - 0.1, T("velocidad")); bar_set(S["haz"], TT, TT.lerp(ANT, max(u, 0.001)))
        v = seg(t, T("velocidad") - 0.2, T("hasta la antena") + 0.4); S["luz"].location = TT.lerp(ANT, v) if t < b1 else LEJOS
    else: hide_bar(S["haz"]); S["luz"].location = LEJOS
    # -------- paquete --------
    c0, c1 = T("cada canal"), T("tu tele no") - 0.2
    on = c0 - 0.3 < t < c1
    pp = pkt_pos(t); M = pkt_basis()
    S["pkt"].location = pp if (on and t > T("van empaquetados") - 0.3) else LEJOS
    S["pkt"].rotation_euler = M.to_euler()
    gk = seg(t, T("van empaquetados") - 0.3, T("van empaquetados") + 0.3) * (1 - seg(t, c1 - 0.5, c1))
    S["pkt"].scale = (max(gk, 0.01),) * 3
    show(S["pkt"], on and t > T("van empaquetados") - 0.3)
    bitu = seg(t, T("comprimidos"), T("ceros") + 0.2)
    for k, c in enumerate(S["canales"]):
        if not on: c.location = LEJOS; show(c, False); [setattr(b, "location", Vector(LEJOS)) for b in S["bits"][k]]; continue
        loose = pp + M @ Vector(((k - 2) * 4.0, 0, (k - 2) * 5.0 + 1.2 * math.sin(t * 2.2 + k)))
        inside = pp + M @ Vector((0, -2.0, -8.0 + 4.0 * k))
        u = seg(t, T("van empaquetados") - 0.2 + 0.12 * k, T("van empaquetados") + 0.5 + 0.12 * k)
        pos = loose.lerp(inside, u)
        c.location = pos; c.rotation_euler = M.to_euler()
        sc_ = (1 - bitu) + 0.0001; c.scale = (sc_, sc_, sc_)
        show(c, bitu < 0.98)
        for j, b in enumerate(S["bits"][k]):
            if bitu > 0.02:
                b.location = inside + M @ Vector(((j % 4 - 1.5) * 2.2, 0, (j // 4 - 0.5) * 1.8))
                b.rotation_euler = M.to_euler(); s = bitu; b.scale = (s, s, s)
                on1 = (hash((k, j, int(t * 6))) % 2) == 0
                set_color(b, (1, 1, 1) if on1 else (0.15, 0.17, 0.25))
            else: b.location = LEJOS
    # portadora (onda senoidal) por la que viaja el paquete
    pc0 = T("en una sola")
    car = pc0 - 0.2 < t < c1
    up = Vector((0, 0, 1))
    for k, o in enumerate(S["portadora"]):
        if not car: o.location = LEJOS; continue
        s = k * 5.0
        g = seg(t, pc0 - 0.2, pc0 + 0.8)
        if s > 345 * g: o.location = LEJOS; continue
        base = ANT - D * s
        o.location = base + up * (7 * math.sin(s * 0.16 + t * 7))
    apply_cam(S["cam"], *cam_state(t, CAM(), drift=0.35))

def pose_spec(t, S):
    first = t < T("y aquí")
    # aguja
    f = needle_f(t)
    S["aguja"].location = (FX(f) - FX(470) + 0 if False else FX(f), 0, 0)
    S["aguja"].location = (FX(f), 0, 0)
    # bloques de canales
    mv = T("cinco cadenas") + 0.2
    movers = {a: (b, k) for k, (a, b) in enumerate(MOVES)}
    for (i, j), o in S["bloques"].items():
        tf = found(t, PEAKS[i]) + 0.05 * j
        g = seg(t, tf - 0.05, tf + 0.25) if first else 1.0
        base = slot_pos(i, j)
        if (i, j) in movers and t > mv:
            (i2, j2), k = movers[(i, j)]
            u = seg(t, mv + 0.3 * k, mv + 0.3 * k + 0.9)
            tgt = slot_pos(*(i2, j2))
            p = base.lerp(tgt, u) + Vector((0, -0.6, 7 * math.sin(math.pi * u)))
            o.location = p
            set_color(o, tuple(mix(c, 1.0, 0.5 * math.sin(math.pi * u)) for c in CHC[(i + j) % 6]))
        else:
            o.location = base; set_color(o, CHC[(i + j) % 6])
        # el canal 1 brilla cuando lo eliges
        if (i, j) == (0, 0):
            hl = win01(t, T("el uno"), T("y aquí"), 0.2, 0.2) + win01(t, found2(PEAKS[3]) - 0.1, DUR + 2, 0.2, 0.1) * 0
            if hl: set_color(o, tuple(mix(c, 1.0, 0.5 * hl * (0.5 + 0.5 * math.sin(t * 12))) for c in CHC[0]))
        # el segundo barrido hace parpadear lo que encuentra
        if not first and t > T("búsqueda"):
            ff = PEAKS[i]
            if (i, j) in movers and t > mv: ff = PEAKS[movers[(i, j)][0][0]]
            fl = win01(t, found2(ff), found2(ff) + 0.5, 0.05, 0.4)
            if fl: set_color(o, tuple(mix(c, 1.0, 0.6 * fl) for c in CHC[(i + j) % 6]))
        s = max(g, 0.001); o.scale = (2.0 * s, 0.12, 1.5 * s)
    for k, o in enumerate(S["huecos"]):
        i, j = k // 4, k % 4
        o.scale = (2.0, 0.12, 1.5) if (not first or t > found(t, PEAKS[i])) else (0.001, 0.12, 0.001)
    # múltiple nuevo (DVB-T2)
    a0 = T("además")
    for j, o in enumerate(S["t2"]):
        g = seg(t, a0 + 0.2 + 0.08 * j, a0 + 0.5 + 0.08 * j) if j < 4 else seg(t, T("mete") + 0.1 * (j - 4), T("mete") + 0.4 + 0.1 * (j - 4))
        dense = seg(t, T("mete") - 0.2, T("mete") + 0.6)
        h = mix(1.5, 1.0, dense); pitch = mix(1.8, 1.2, dense)
        o.location = Vector((FX(T2F), SY - 0.15, 29.0 - 0.25 * dense + pitch * j))
        s = max(g, 0.001) if (t > a0) else 0.001
        o.scale = (2.0 * s, 0.12, h * s)
        old = seg(t, T("si tu tele es") - 0.1, T("si tu tele es") + 0.4)
        if old > 0:
            v = 0.3 + 0.4 * ((hash((j, int(t * 12))) % 100) / 100)
            set_color(o, tuple(mix(c, v, old) for c in (0.97, 0.97, 1.0)))
        else: set_color(o, (0.97, 0.97, 1.0) if j % 2 else (0.75, 0.9, 1.0))
    # lista de canales
    l0 = T("y apunta")
    for k, (r, hl, chip, num, fr) in enumerate(S["filas"]):
        g = seg(t, l0 + 0.3 * k, l0 + 0.3 * k + 0.3) if first else 1.0
        r.location = (0, 0, 0) if g > 0.01 else LEJOS
        r.scale = (1, 1, max(g, 0.01)); r.location = Vector((0, 0, (48.5 - 3.2 * k) * (1 - max(g, 0.01))))
        i, j = divmod(k, 4)
        freq = PEAKS[i]
        if (i, j) in dict(MOVES) and t > found2(PEAKS[dict(MOVES)[(i, j)][0]]): freq = PEAKS[dict(MOVES)[(i, j)][0]]
        txt = f"{freq}"
        if fr.data.body != txt: fr.data.body = txt
        set_color(chip, CHC[(i + j) % 6])
        sel = 0.0
        if k == 0: sel = win01(t, T("el uno") - 0.1, T("y aquí"), 0.15, 0.2) + win01(t, T("tu tele va") + 0.2, T("además"), 0.15, 0.2)
        upd = 0.0
        if not first and (i, j) in dict(MOVES): upd = win01(t, found2(PEAKS[dict(MOVES)[(i, j)][0]]), found2(PEAKS[dict(MOVES)[(i, j)][0]]) + 0.8, 0.05, 0.4)
        set_color(hl, tuple(mix(mix(c, d, min(1, sel)), e, upd) for c, d, e in zip((0.2, 0.22, 0.28), (0.85, 0.65, 0.1), (0.2, 0.75, 0.4))))
    # barra de progreso de la búsqueda
    r0, r1 = T("búsqueda") + 0.3, T("frecuencias", fin=True)
    pg = seg(t, r0, r1) if t > T("menú") else 0
    if pg > 0.001:
        S["progreso"].scale = (46 * pg, 0.12, 1.2); S["progreso"].location = (-23 + 23 * pg, SY - 0.2, 51.0)
    else: S["progreso"].location = LEJOS

# ---------------------------------------------------------------------------------------------------
def VD(at, dist, yaw, pitch, lens=32):
    at = Vector(at); y, p = math.radians(yaw), math.radians(pitch)
    return (tuple(at + dist * Vector((math.sin(y) * math.cos(p), -math.cos(y) * math.cos(p), math.sin(p)))), tuple(at), lens)

def CAM():
    k = []
    def add(t, v): k.append((t,) + v)
    def pk(t, off_side, off_back, dz, lens=32):
        pp = pkt_pos(t); pos = pp + SIDE * off_side - D * off_back + Vector((0, 0, dz)); add(t, (tuple(pos), tuple(pp + Vector((0, 0, 2))), lens))
    add(0.0, VD((-3, -22, 31), 74, -22, 9, 30))
    add(1.5, VD((0, -12, 34), 82, -12, 6, 30))
    add(T("la antena") + 0.2, VD((14, -30, 120), 230, -8, 14, 30))
    add(T("qué ha") + 0.1, VD(tuple(ANT + Vector((-2, 0, -6))), 95, -28, 12, 32))
    add(T("mira cómo") + 0.6, VD((10, -34, 95), 290, 6, 8, 30))
    add(T("desde una") + 0.2, VD((10, -34, 100), 300, -4, 9, 30))
    add(T("desde una") + 1.6, VD(tuple(TT + Vector((0, 0, -40))), 200, -30, 6, 30))
    add(T("salen ondas"), VD(tuple(TT + Vector((0, 0, -30))), 230, -20, 4, 30))
    add(T("viajan en") + 0.3, (tuple(TT.lerp(ANT, 0.3) + SIDE * 160 + Vector((0, 0, 30))), tuple(TT.lerp(ANT, 0.5)), 30))
    add(T("velocidad"), (tuple(TT.lerp(ANT, 0.55) + SIDE * 170 + Vector((0, 0, 30))), tuple(TT.lerp(ANT, 0.72)), 30))
    add(T("hasta la antena") + 0.4, VD(tuple(ANT + Vector((0, 0, -8))), 140, -55, 12, 32))
    pk(T("cada canal") + 0.6, 88, 0, 6)
    pk(T("van empaquetados"), 70, 6, 6)
    pk(T("en una sola") + 0.6, 70, -14, 8)
    pk(T("comprimidos") + 0.3, 56, -6, 6)
    pk(T("a ese paquete") + 0.5, 54, 8, 10)
    add(T("tu tele no") - 0.3, VD((12, -30, 108), 270, -6, 9, 30))
    add(T("tu tele no") + 1.0, VD((0, -3, 37), 74, 0, 0, 30))
    add(T("hace un barrido"), VD((-1, -3, 37), 72, 0, 0, 30))
    add(T("y apunta"), VD((0, -3, 37), 73, 2, 0, 30))
    add(T("cuando pulsas"), VD((0, -6, 32), 82, -6, 5, 30))
    add(T("salta") + 0.4, VD((0, -6, 32), 80, 4, 3, 30))
    add(T("y aquí") + 0.3, VD((0, -3, 37), 73, -3, 0, 30))
    add(T("cinco cadenas"), VD((-1, -3, 37), 71, 0, 0, 30))
    add(T("tu tele va"), VD((-1, -6, 32), 81, -5, 4, 30))
    add(T("además") + 0.4, VD((1, -3, 37), 73, 3, 0, 30))
    add(T("mete"), VD((0, -3, 36), 71, 0, 0, 30))
    add(T("la solución"), VD((0, -6, 32), 81, -4, 4, 30))
    add(T("búsqueda") + 0.5, VD((0, -3, 37), 73, 0, 0, 30))
    add(T("no hace") - 0.3, VD((0, -3, 37), 76, 3, 1, 30))
    add(T("no hace") + 0.9, VD((14, -32, 112), 250, -6, 10, 30))
    add(DUR, VD((14, -32, 108), 300, 6, 13, 30))
    add(DUR + 3, VD((14, -32, 108), 305, 8, 13, 30))
    return k

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v)
    return {"antena": Pj(tuple(ANT + Vector((0, 0, 6)))), "cable": Pj((30, 4, 80)), "torre": Pj(tuple(TT + Vector((0, 0, 10)))),
            "pkt": Pj(tuple(pkt_pos(t) + Vector((0, 0, 12)))), "aguja": Pj((FX(needle_f(t)), SY, 50.5)),
            "p0": Pj((FX(PEAKS[0]), SY, 34)), "p3": Pj((FX(PEAKS[3]), SY, 36)), "t2": Pj((FX(T2F), SY, 36)),
            "t2l": Pj((FX(T2F) - 1.0, SY, 27)), "t2r": Pj((FX(T2F) + 1.0, SY, 27)), "tele": Pj((0, -3, TVZ + 15)),
            "lista": Pj((15, SY, 51)), "mando": Pj(tuple(REM + Vector((0, 0, 4))))}

if __name__ == "__main__":
    run("tdt", build, pose, anchors)
