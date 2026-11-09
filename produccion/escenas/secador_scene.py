# «Si tuvieras que inventar el secador de pelo…»: secador en corte (sin la mitad delantera de la carcasa). Arranca con el chorro
# caliente moviendo un mechón mojado y el alambre al rojo dentro. Luego el pelo solo (gotas que tardan en irse; calor y aire),
# el ventilador con su motor detrás, la rejilla por la que entra el aire (bolitas azules), el alambre de nicrom que se enrolla
# en la cruz de mica, la corriente que lo pone al rojo y el aire que sale naranja; una mano tapa la rejilla, el aire se para y
# todo se recalienta; la lámina bimetálica se dobla y se separa del contacto (el alambre se apaga), al enfriarse vuelve; el
# fusible del mango se funde; la boquilla estrecha concentra el chorro sobre el pelo. Al final, el secador entero.
import bpy, bmesh, math, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("secador")
BG = (0.07, 0.08, 0.11); WALLC = (0.11, 0.12, 0.16)
SHELL = (0.35, 0.55, 0.85); SHELLIN = (0.72, 0.8, 0.92); DARK = (0.12, 0.12, 0.14); GRILL = (0.22, 0.23, 0.27)
METAL = (0.7, 0.72, 0.76); COPPER = (0.9, 0.5, 0.25); MICA = (0.86, 0.78, 0.58); NICR = (0.6, 0.6, 0.58)
GLOW = (1.0, 0.3, 0.07); HOT = (1.0, 0.8, 0.35); COLD = (0.45, 0.75, 1.0); WARM = (1.0, 0.55, 0.2); CUR = (1.0, 0.92, 0.3)
BRASS = (0.92, 0.7, 0.3); STEEL = (0.55, 0.57, 0.62); SKIN = (0.93, 0.72, 0.6); HAIR = (0.33, 0.2, 0.12); DROP = (0.55, 0.8, 1.0)
GLASS = (0.75, 0.88, 0.95); WHITE = (0.93, 0.94, 0.96)
LEJOS = (0, 0, -300)
X0, X1, RB = -2.3, 2.2, 1.0          # cuerpo: de atrás (rejilla) a delante, radio
HX0, HX1, HR, NT = -0.5, 1.4, 0.57, 10  # hélice del alambre
BX0, BX1, BZ, BY = 1.5, 2.05, 0.6, -0.32   # lámina bimetálica
HAIRX = 3.9
HROT = 0.2                           # inclinación del mango
HP = Vector((-0.45, 0, -0.85))       # arranque del mango

def cmix(a, b, u): u = max(0.0, min(1.0, u)); return tuple(mix(x, y, u) for x, y in zip(a, b))
def hsh(k, s=1.0): return (math.sin(k * 12.9898 + s * 78.233) * 43758.5453) % 1.0

def hw(lx, ly, lz):
    """punto del mango (coordenadas locales, z hacia abajo negativo) en el mundo"""
    c, s = math.cos(HROT), math.sin(HROT)
    return HP + Vector((lx * c + lz * s, ly, -lx * s + lz * c))

def tube(r, x0, x1, color, v=56):
    me = bpy.data.meshes.new("tubo"); bm = bmesh.new()
    a = [bm.verts.new((x0, r * math.cos(0.01 + math.tau * k / v), r * math.sin(0.01 + math.tau * k / v))) for k in range(v)]
    b = [bm.verts.new((x1, r * math.cos(0.01 + math.tau * k / v), r * math.sin(0.01 + math.tau * k / v))) for k in range(v)]
    for k in range(v): j = (k + 1) % v; bm.faces.new((a[k], a[j], b[j], b[k]))
    bm.normal_update(); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("tubo", me); bpy.context.collection.objects.link(o)
    setup(o, color, unique=True)
    for p in o.data.polygons: p.use_smooth = True
    return o

def cut(o, cutter, th, inner):
    o.data.materials.append(mat(inner, unique=True))
    m = o.modifiers.new("sol", "SOLIDIFY"); m.thickness = th; m.offset = -1; m.material_offset = 1; m.material_offset_rim = 1
    b = o.modifiers.new("cut", "BOOLEAN"); b.operation = 'DIFFERENCE'; b.object = cutter
    return o

def curve(pts, r, color):
    cu = bpy.data.curves.new("c", 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = r; cu.bevel_resolution = 2; cu.use_fill_caps = True
    sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts): sp.points[i].co = (p[0], p[1], p[2], 1)
    o = bpy.data.objects.new("c", cu); bpy.context.collection.objects.link(o)
    return setup(o, color, unique=True)

def curve_set(o, pts):
    sp = o.data.splines[0]
    for i, p in enumerate(pts): sp.points[i].co = (p[0], p[1], p[2], 1)

def helix(u):
    a = u * NT * math.tau
    return Vector((mix(HX0, HX1, u), HR * math.cos(a), HR * math.sin(a)))

def arrow(col, r=0.07, L=0.9):
    e = empty(LEJOS)
    cyl(r, L, (L / 2, 0, 0), col, parent=e, rot=(0, math.pi / 2, 0), v=12)
    bpy.ops.mesh.primitive_cone_add(radius1=r * 2.6, radius2=0, depth=r * 5, location=(L + r * 2.5, 0, 0), rotation=(0, math.pi / 2, 0), vertices=16)
    setup(bpy.context.object, col, parent=e)
    return e

def strand_pts(i, t, g):
    x0 = HAIRX + 0.75 * hsh(i, 1); y0 = -0.5 + 1.0 * hsh(i, 2); top = 3.0 + 0.3 * hsh(i, 3); ph = 6 * hsh(i, 4)
    pts = []
    for k in range(12):
        s = k / 11; z = top - 5.6 * s
        jet = g * 2.0 * math.exp(-(z / 1.4) ** 2) * (0.8 + 0.3 * math.sin(9 * t + ph + 3 * s)) * s ** 0.6
        sway = (0.12 + 0.35 * g) * s * math.sin(1.7 * t + ph + 2.5 * s)
        pts.append((x0 + jet + sway * 0.5, y0 + sway * 0.6 * g, z + 0.25 * jet * s))
    return pts

def build():
    sc, cam = scene_setup(world=BG, shadow=0.3)
    S = {"cam": cam}
    box((40, 0.3, 30), (0, 7, 0), WALLC)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -5.0, 0)); cb = bpy.context.object; cb.scale = (30, 10, 30); cb.hide_render = True
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 5.0, 0)); cf = bpy.context.object; cf.scale = (30, 10, 30); cf.hide_render = True
    S["cutters"] = [cb, cf]
    # carcasa: mitad trasera (siempre) y mitad delantera (solo al final)
    S["shellB"] = cut(tube(RB, X0, X1, SHELL), cb, 0.08, SHELLIN)
    S["shellF"] = cut(tube(RB, X0, X1, SHELL), cf, 0.08, SHELLIN)
    S["rimB"] = torus(RB - 0.02, 0.06, (X1, 0, 0), SHELL, rot=(0, math.pi / 2, 0), unique=True)
    # rejilla de atrás
    S["grill"] = gr = empty((X0, 0, 0))
    for r in (0.94, 0.68, 0.42): torus(r, 0.035, (0, 0, 0), GRILL, parent=gr, rot=(0, math.pi / 2, 0))
    for k in range(6):
        a = k * math.pi / 6; o = box((0.05, 1.9, 0.05), (0, 0, 0), GRILL, parent=gr); o.rotation_euler = (a, 0, 0)
    cyl(0.18, 0.08, (0, 0, 0), GRILL, parent=gr, rot=(0, math.pi / 2, 0))
    # motor y ventilador
    S["motor"] = mo = empty((-1.75, 0, 0))
    cyl(0.33, 0.6, (0, 0, 0), STEEL, parent=mo, rot=(0, math.pi / 2, 0))
    for k in range(3): torus(0.31, 0.05, (-0.18 + 0.18 * k, 0, 0), COPPER, parent=mo, rot=(0, math.pi / 2, 0))
    for a in (0.0, math.pi / 2, -math.pi / 2):
        o = box((0.06, 0.06, 0.62), (0, 0.62 * math.cos(a), 0.62 * math.sin(a)), DARK, parent=mo); o.rotation_euler = (a - math.pi / 2, 0, 0)
    cyl(0.045, 0.6, (0.4, 0, 0), METAL, parent=mo, rot=(0, math.pi / 2, 0))
    S["fan"] = fn = empty((-1.12, 0, 0))
    cyl(0.17, 0.25, (0, 0, 0), DARK, parent=fn, rot=(0, math.pi / 2, 0))
    for k in range(6):
        arm = empty((0, 0, 0), parent=fn); arm.rotation_euler = (k * math.tau / 6, 0, 0)
        b = box((0.05, 0.3, 0.7), (0, 0, 0.5), (0.85, 0.86, 0.9), parent=arm); b.rotation_euler = (0, 0, 0.55)
    # cruz de mica y alambre
    S["mica"] = mi = empty((mix(HX0, HX1, 0.5), 0, 0))
    box((HX1 - HX0 + 0.15, 0.03, 1.08), (0, 0, 0), MICA, parent=mi); box((HX1 - HX0 + 0.15, 1.08, 0.03), (0, 0, 0), MICA, parent=mi)
    S["coil"] = curve([helix(k / 239) for k in range(240)], 0.032, NICR)
    S["cdots"] = [sph(0.05, LEJOS, CUR, seg=8) for _ in range(22)]
    # lámina bimetálica y contacto
    S["bim_a"] = [box((0.075, 0.18, 0.045), LEJOS, BRASS, unique=True) for _ in range(8)]
    S["bim_b"] = [box((0.075, 0.18, 0.045), LEJOS, STEEL, unique=True) for _ in range(8)]
    S["bim_base"] = box((0.12, 0.24, 0.22), LEJOS, DARK)
    S["contacto"] = cyl(0.045, 0.1, LEJOS, (0.95, 0.75, 0.3))
    S["cpost"] = box((0.06, 0.06, 0.28), LEJOS, DARK)
    S["chispa"] = [sph(0.025, LEJOS, CUR, seg=8) for _ in range(8)]
    # mango abierto por delante, cables y fusible
    S["handle"] = hd = empty(HP); hd.rotation_euler = (0, HROT, 0)
    box((0.95, 0.06, 2.8), (0, 0.4, -1.4), SHELL, parent=hd)
    for sx in (-1, 1): box((0.06, 0.86, 2.8), (sx * 0.475, 0, -1.4), SHELL, parent=hd)
    box((0.95, 0.86, 0.06), (0, 0, -2.8), SHELL, parent=hd)
    box((0.85, 0.02, 2.7), (0, 0.36, -1.4), SHELLIN, parent=hd)
    box((0.2, 0.25, 0.45), (0.0, -0.36, -0.55), DARK, parent=hd)                 # interruptor
    for dx in (-0.18, 0.18): box((0.04, 0.04, 2.3), (dx, 0.15, -1.6), (0.8, 0.2, 0.2) if dx < 0 else (0.2, 0.3, 0.8), parent=hd)
    S["fuse"] = fu = empty((0.18, 0.0, -1.35), parent=hd)
    S["fglass"] = cyl(0.11, 0.5, (0, 0, 0), GLASS, parent=fu, v=20, unique=True)
    for dz in (-0.27, 0.27): cyl(0.12, 0.08, (0, 0, dz), METAL, parent=fu, v=20)
    S["fwire"] = box((0.025, 0.025, 0.46), (0, -0.12, 0), (0.95, 0.95, 0.85), parent=fu, unique=True)
    S["fspark"] = [sph(0.03, LEJOS, CUR, seg=8) for _ in range(10)]
    S["cord"] = curve([hw(0, 0.1, -2.8), hw(0, 0.1, -3.3), hw(-0.3, 0.1, -4.2), hw(-1.0, 0.3, -5.5)], 0.07, DARK)
    # boquilla concentradora
    S["noz"] = nz = empty(LEJOS)
    o = tube(RB - 0.04, 0, 0.25, DARK, v=48); o.parent = nz
    for sz in (-1, 1):
        b = box((0.9, 1.7, 0.06), (0.6, 0, sz * 0.55), DARK, parent=nz); b.rotation_euler = (0, sz * 0.5, 0)
    for sy in (-1, 1): box((0.9, 0.06, 1.05), (0.6, sy * 0.85, 0), DARK, parent=nz)
    # aire, pelo, gotas, vapor, flechas, mano
    S["air"] = [sph(0.065, LEJOS, COLD, seg=8, unique=True) for _ in range(46)]
    S["hair"] = [curve(strand_pts(i, 0, 0), 0.035, HAIR) for i in range(14)]
    S["drops"] = [sph(0.07, LEJOS, DROP, seg=10) for _ in range(16)]
    S["vapor"] = [sph(0.09, LEJOS, (0.85, 0.88, 0.92), seg=8) for _ in range(14)]
    S["heat"] = [arrow(GLOW) for _ in range(3)]; S["wind"] = [arrow(COLD) for _ in range(3)]
    S["hand"] = hn = empty(LEJOS)
    sph(0.95, (0, 0, 0), SKIN, parent=hn, scale=(0.22, 0.85, 1.0))
    for k in range(4): cyl(0.15, 1.0, (0, -0.48 + 0.32 * k, 1.25 - 0.08 * abs(k - 1.5)), SKIN, parent=hn, v=16)
    for k in range(4): sph(0.15, (0, -0.48 + 0.32 * k, 1.75 - 0.08 * abs(k - 1.5)), SKIN, parent=hn)
    o = cyl(0.16, 0.9, (0, 0.95, 0.2), SKIN, parent=hn, v=16); o.rotation_euler = (-0.9, 0, 0)
    cyl(0.4, 2.4, (-1.2, 0, -0.6), SKIN, parent=hn, rot=(0, -1.2, 0))
    dyn = [cam, S["cutters"], S["shellB"], S["shellF"], S["rimB"], gr, mo, fn, mi, S["coil"], S["cdots"], S["bim_a"], S["bim_b"],
           S["bim_base"], S["contacto"], S["cpost"], S["chispa"], hd, S["fspark"], S["cord"], nz, S["air"], S["hair"], S["drops"],
           S["vapor"], S["heat"], S["wind"], hn]
    join_static(dyn)
    return sc, S

def sca(o, u):
    u = max(u, 0.001); o.scale = (u, u, u)
    for c in ([o] + list(o.children_recursive)):
        if c.type in ('MESH', 'CURVE'): c.hide_render = u < 0.01

def flow_at(t):
    covered = seg(t, T("pero si tapas") + 0.8, T("el aire deja") + 0.3) * (1 - seg(t, T("al enfriarse") - 0.2, T("al enfriarse") + 0.6))
    if t < T("vamos a"): return 1.0
    return seg(t, T("aspira el"), T("aspira el") + 0.8) * (1 - 0.97 * covered)

def phase(t):
    n = int(t * 15); s = 0.0
    for k in range(n): s += flow_at(k / 15) / 15
    return s + flow_at(t) * (t - n / 15)

def pose(t, S):
    t_inv, t_pelo, t_calor, t_aire, t_prim = T("vamos a"), T("el pelo mojado"), T("el agua necesita"), T("y aire que"), T("primero")
    t_vent, t_motor, t_asp, t_frio, t_alam = T("así que pones un"), T("con un motor"), T("aspira el"), T("pero el aire frío"), T("pones un alambre")
    t_30, t_mica, t_corr, t_rojo, t_sale = T("unos treinta"), T("enrollados"), T("cuando pasa la"), T("el alambre se pone"), T("el aire lo")
    t_cur, t_tapa, t_deja, t_sigue, t_todo = T("y aquí viene"), T("pero si tapas"), T("el aire deja"), T("el alambre sigue"), T("y todo se")
    t_lam, t_calt, t_dobla, t_60, t_corta = T("así que pones una"), T("al calentarse"), T("y la lámina"), T("cuando pasa de"), T("se separa")
    t_enfr, t_vuel, t_fus, t_funde, t_ult = T("al enfriarse"), T("vuelve"), T("y por si"), T("se funde"), T("por último")
    t_boq, t_sig = T("una boquilla"), T("sígueme")
    intro = t < t_inv
    gone = seg(t, t_inv - 0.05, t_inv + 0.45)
    def appear(a, d=0.45): return 1.0 if intro else seg(t, a, a + d)
    body = (1 - gone) if intro else seg(t, t_prim - 0.3, t_prim + 0.3)
    sca(S["shellB"], body); sca(S["rimB"], body); sca(S["handle"], body); sca(S["cord"], body)
    sca(S["shellF"], seg(t, t_sig - 0.2, t_sig + 0.5)); S["shellF"].scale = (1, 1, 1) if t > t_sig - 0.2 else (0.001,) * 3
    S["shellF"].hide_render = t < t_sig - 0.2
    sca(S["grill"], (1 - gone) if intro else seg(t, t_asp - 0.2, t_asp + 0.3))
    sca(S["motor"], (1 - gone) if intro else seg(t, t_motor - 0.1, t_motor + 0.4))
    sca(S["fan"], (1 - gone) if intro else seg(t, t_vent + 0.5, t_vent + 1.0))
    sca(S["mica"], (1 - gone) if intro else seg(t, t_mica + 0.3, t_mica + 0.8))
    # alambre: se enrolla poco a poco
    if intro: cu = 1 - gone
    else: cu = seg(t, t_alam, t_alam + 0.6) * 0.15 + 0.85 * seg(t, t_30, t_mica + 0.6)
    S["coil"].hide_render = cu < 0.01; S["coil"].data.bevel_factor_end = max(cu, 0.001)
    # ---------- calor del alambre ----------
    on = 1.0 if intro else 0.0
    if not intro:
        on = seg(t, t_corr + 0.2, t_rojo + 0.6) * (1 - seg(t, t_corta + 0.6, t_corta + 1.6))
        on = max(on, seg(t, t_vuel - 0.2, t_vuel + 0.6) * (1 - seg(t, t_funde + 0.3, t_funde + 0.8)))
        on = max(on, seg(t, t_ult, t_ult + 0.5))
    over = seg(t, t_sigue, t_todo + 0.8) * (1 - seg(t, t_corta + 0.4, t_corta + 1.6))
    col = cmix(NICR, GLOW, on / 0.8) if on < 0.8 else cmix(GLOW, (1.0, 0.45, 0.12), (on - 0.8) / 0.2)
    col = cmix(col, HOT, over * 0.85)
    if intro: col = cmix(GLOW, (1.0, 0.45, 0.12), 0.5) if gone < 0.5 else NICR
    set_color(S["coil"], col)
    set_color(S["shellB"], cmix(SHELL, (0.85, 0.35, 0.3), over * 0.8))
    # corriente por el alambre
    cur_on = (not intro) and (t_corr < t < t_cur or t_lam < t < t_corta + 0.5 or t_vuel < t < t_funde + 0.3)
    for k, d in enumerate(S["cdots"]):
        if not cur_on: d.location = LEJOS; continue
        d.location = helix(((t * 0.12 + k / 22) % 1.0)) * 1.04 if cu > 0.99 else LEJOS
    # ---------- ventilador y aire ----------
    fl = flow_at(t)
    spin = 30 * t if intro else 30 * max(0.0, t - t_vent - 0.6) * (1 if t > t_motor else 0)
    S["fan"].rotation_euler = (spin, 0, 0)
    ph = phase(t); airvis = 1.0 if intro else seg(t, t_asp, t_asp + 0.5)
    hairjet = intro or t > t_boq
    nozf = seg(t, t_boq, t_boq + 0.6)
    for k, d in enumerate(S["air"]):
        if airvis < 0.02 or (t_cur < t < t_tapa - 0.2 and False): d.location = LEJOS; continue
        L = 8.6; x = -3.6 + ((ph * 3.2 + k / 46 * L) % L)
        a = math.tau * hsh(k, 5); r = 0.15 + 0.68 * hsh(k, 6)
        if x < X0: r *= 1.0 + (X0 - x) * 0.6
        y = r * math.cos(a); z = r * math.sin(a)
        if x > X1:
            spread = 1 + (x - X1) * 0.35 * (1 - 0.6 * nozf)
            y *= spread * (1 - 0.3 * nozf); z *= spread * (1 - 0.65 * nozf)
        if not hairjet and x > X1 + 1.6: d.location = LEJOS; continue
        d.location = (x, y, z)
        hot = on * seg(x, HX0 + 0.4, HX1 + 0.3)
        set_color(d, cmix(COLD, WARM, hot)); s = airvis * (0.6 + 0.4 * fl) * (1 - 0.5 * (x > X1 + 1.0) * seg(x, X1 + 1, X1 + 2.6))
        d.scale = (s, s, s)
    # ---------- pelo ----------
    hair_on = t < t_prim + 0.6 or t > t_ult + 0.6
    g = 1.0 if intro else (seg(t, t_boq - 0.3, t_boq + 0.4) if t > t_ult else 0.0)
    for i, o in enumerate(S["hair"]):
        o.hide_render = not hair_on
        if hair_on: curve_set(o, strand_pts(i, t, g))
    wet = t < t_aire + 1.2
    for k, d in enumerate(S["drops"]):
        i = k % 14; pts = strand_pts(i, t, g); p = Vector(pts[3 + (k * 5) % 7])
        if not hair_on or (t > t_prim): d.location = LEJOS; continue
        if intro:
            u = (t * 0.9 + hsh(k, 9)) % 1.0; d.location = p + Vector((3.0 * u, 0.3 * (hsh(k, 2) - 0.5) * u, -0.6 * u * u)); d.scale = (1 - 0.6 * u,) * 3
        else:
            sh = 1.0 - 0.15 * seg(t, t_pelo, t_calor) - 0.7 * seg(t, t_calor + 0.5, t_aire + 1.0)
            fly = seg(t, t_aire + 0.1, t_aire + 1.1)
            d.location = p + Vector((-0.05 + 2.5 * fly * hsh(k, 7), -0.06, 0)); d.scale = (max(sh, 0.05),) * 3
    for k, d in enumerate(S["vapor"]):
        v = 0.0 if intro else win01(t, t_pelo + 0.3, t_prim + 0.4, 0.4, 0.4)
        if v < 0.03: d.location = LEJOS; continue
        rate = 0.25 + 0.8 * seg(t, t_calor, t_calor + 0.6)
        u = (t * rate + k / 14) % 1.0
        drift = 2.2 * seg(t, t_aire, t_aire + 0.8) * u
        d.location = (HAIRX + 0.7 * hsh(k, 3) + drift, -0.3 + 0.6 * hsh(k, 4), -1.5 + 2.8 * hsh(k, 5) + 2.2 * u)
        d.scale = (v * (0.5 + u) * (0.5 + 0.6 * seg(t, t_calor, t_calor + 0.6)),) * 3
    for k, e in enumerate(S["heat"]):
        v = win01(t, t_calor + 0.2, t_aire + 0.2, 0.3, 0.3)
        if v < 0.02: e.location = LEJOS; continue
        z = -0.8 + 0.8 * k; e.location = (HAIRX - 1.3 + 0.2 * math.sin(6 * t + k), -0.4, z); e.scale = (v,) * 3
    for k, e in enumerate(S["wind"]):
        v = win01(t, t_aire, t_prim + 0.3, 0.2, 0.3)
        if v < 0.02: e.location = LEJOS; continue
        u = (t * 1.2 + k / 3) % 1.0
        e.location = (HAIRX - 2.6 + 4.0 * u, -0.6, -0.6 + 0.8 * k); e.scale = (v,) * 3
    # ---------- mano que tapa la rejilla ----------
    hv = seg(t, t_tapa, t_tapa + 1.2) * (1 - seg(t, t_enfr - 0.3, t_enfr + 0.5))
    if hv > 0.001 and not intro:
        S["hand"].location = Vector((X0 - 0.32, 0.0, 0.0)) + Vector((-4.0, -1.0, 1.5)) * (1 - hv); S["hand"].rotation_euler = (0, 0, 0)
    else: S["hand"].location = LEJOS
    # ---------- lámina bimetálica ----------
    lv = 1.0 if intro else seg(t, t_lam + 0.3, t_lam + 0.8)
    if intro: lv = 1 - gone
    curv = keyed(t, [(0, 0.0), (t_calt, 0.0), (t_dobla + 0.6, 0.45), (t_60 + 1.0, 0.75), (t_corta + 0.3, 1.0), (t_enfr, 1.0), (t_vuel + 0.4, 0.0), (DUR + 2, 0.0)])
    heatb = seg(t, t_calt, t_calt + 1.2) * (1 - seg(t, t_enfr, t_vuel + 0.4))
    Lb = BX1 - BX0; ang_tot = math.radians(48) * curv
    for k in range(8):
        for lst, dz in ((S["bim_a"], -0.0225), (S["bim_b"], 0.0225)):
            o = lst[k]
            if lv < 0.02: o.location = LEJOS; continue
            s0 = (k + 0.5) / 8 * Lb; ang = ang_tot * (k + 0.5) / 8
            if ang_tot > 1e-4:
                R = Lb / ang_tot; x = BX0 + R * math.sin(s0 / R); z = BZ + R * (1 - math.cos(s0 / R))
            else: x, z = BX0 + s0, BZ
            o.location = (x - math.sin(ang) * dz, BY, z + math.cos(ang) * dz); o.rotation_euler = (0, -ang, 0)
            o.scale = (0.075 * lv * (1.0 + (0.07 * heatb if lst is S["bim_a"] else 0)), 0.18 * lv, 0.045 * lv)
            set_color(o, cmix(BRASS if lst is S["bim_a"] else STEEL, (1.0, 0.4, 0.2), 0.45 * heatb))
    S["bim_base"].location = (BX0 - 0.05, BY, BZ + 0.0) if lv > 0.02 else LEJOS
    S["contacto"].location = (BX1 - 0.04, BY, BZ - 0.075) if lv > 0.02 else LEJOS
    S["cpost"].location = (BX1 - 0.04, BY, BZ - 0.26) if lv > 0.02 else LEJOS
    for k, d in enumerate(S["chispa"]):
        u = (t - (t_corta - 0.05)) / 0.4; u2 = (t - (t_vuel + 0.3)) / 0.35
        uu = u if 0 < u < 1 else (u2 if 0 < u2 < 1 else -1)
        if uu > 0:
            a = k * math.tau / 8; d.location = (BX1 + 0.18 * uu * math.cos(a), BY - 0.1, BZ - 0.03 + 0.18 * uu * math.sin(a)); d.scale = (1 - uu,) * 3
        else: d.location = LEJOS
    # ---------- fusible ----------
    melt = seg(t, t_funde + 0.1, t_funde + 0.6) * (1 - seg(t, t_ult + 0.6, t_ult + 1.0))
    S["fwire"].scale = (0.025, 0.025, 0.46 * max(1 - melt, 0.02)); S["fwire"].hide_render = melt > 0.97
    set_color(S["fwire"], cmix((0.95, 0.95, 0.85), (1.0, 0.5, 0.15), seg(t, t_funde - 0.4, t_funde + 0.2) * (1 - melt)))
    set_color(S["fglass"], cmix(GLASS, (0.35, 0.33, 0.33), melt))
    fw = S["fuse"].matrix_world.translation
    for k, d in enumerate(S["fspark"]):
        u = (t - (t_funde + 0.1)) / 0.5
        if 0 < u < 1 and body > 0.5:
            a = k * math.tau / 10; d.location = fw + Vector((0.35 * u * math.cos(a), -0.25, 0.35 * u * math.sin(a))); d.scale = (1 - u,) * 3
        else: d.location = LEJOS
    # ---------- boquilla ----------
    S["noz"].location = (X1 - 0.05 + 2.5 * (1 - nozf), 0, 0) if nozf > 0.001 else LEJOS
    S["noz"].scale = (1, 1, 1)
    apply_cam(S["cam"], *cam_state(t, CAM(), drift=0.03))

def orb(tg, d, el, az, lens=35, up=0.0):
    tg = Vector(tg); el, az = math.radians(el), math.radians(az)
    pos = tg + d * Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
    return (tuple(pos), tuple(tg + Vector((0, 0, up * d))), lens)

FUSEW = None
def CAM():
    k = []
    def add(t, v): k.append((t,) + v)
    fz = hw(0.18, 0, -1.35)
    add(0.0, orb((3.4, 0, 0.6), 6.2, 6, 16))
    add(1.6, orb((2.8, 0, 0.4), 8.4, 8, 12))
    add(T("vamos a") - 0.2, orb((1.8, 0, -0.4), 10.5, 8, 10))
    add(T("vamos a") + 0.6, orb((HAIRX + 0.5, 0, 0.3), 8.0, 6, 4))
    add(T("y aire que"), orb((HAIRX + 0.9, 0, 0.2), 8.0, 6, -2))
    add(T("primero") + 0.4, orb((0, 0, -0.8), 11.0, 10, -14))
    add(T("así que pones un") + 0.6, orb((-1.3, 0, -0.3), 6.4, 12, -24))
    add(T("en la parte"), orb((-1.4, 0, -0.3), 6.2, 10, -34))
    add(T("aspira el") + 0.6, orb((-1.4, 0, -0.1), 7.0, 8, -58))
    add(T("pero el aire frío"), orb((0.6, 0, 0.0), 8.5, 8, -10))
    add(T("pones un alambre"), orb((0.45, 0, 0.0), 5.8, 10, -12))
    add(T("enrollados") + 0.6, orb((0.45, 0, 0.0), 5.2, 14, -18))
    add(T("cuando pasa la"), orb((0.5, 0, 0.0), 5.0, 10, -8))
    add(T("el aire lo"), orb((1.6, 0, 0.0), 8.5, 8, 14))
    add(T("y aquí viene"), orb((0.4, 0, 1.6), 10.5, 8, -6))
    add(T("por eso un"), orb((0.4, 0, 1.6), 11.0, 8, 4))
    add(T("pequeño", 2) + 0.2, orb((0.4, 0, 1.6), 11.2, 8, -4))
    add(T("pero si tapas"), orb((-1.4, 0, -0.2), 8.5, 8, -48))
    add(T("el aire deja") + 0.5, orb((-1.0, 0, -0.1), 8.5, 8, -40))
    add(T("el alambre sigue"), orb((0.6, 0, 0.0), 7.5, 8, -12))
    add(T("así que pones una") + 0.4, orb((1.78, BY, 0.72), 2.4, 8, -10))
    add(T("cuando pasa de"), orb((1.78, BY, 0.74), 2.2, 6, -6))
    add(T("vuelve") + 0.5, orb((1.78, BY, 0.72), 2.4, 8, -12))
    add(T("y por si") + 0.7, orb(tuple(fz + Vector((0, 0, 0.5))), 4.6, 6, -6))
    add(T("se funde") + 0.8, orb(tuple(fz + Vector((0, 0, 0.5))), 4.4, 6, -10))
    add(T("una boquilla"), orb((3.0, 0, 0.0), 7.5, 8, 18))
    add(T("sígueme"), orb((1.3, 0, -0.9), 14.0, 10, 12))
    add(DUR + 2, orb((1.3, 0, -0.9), 15.0, 10, 18))
    return k

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v)
    return {"fan": Pj((-1.12, -0.2, 0.6)), "motor": Pj((-1.75, -0.2, 0.3)), "grill": Pj((X0, 0, 0.9)), "coil": Pj(helix(0.75) + Vector((0, 0, 0))),
            "mica": Pj((0.45, -0.1, -0.5)), "bim": Pj(((BX0 + BX1) / 2, BY, BZ + 0.05)), "cont": Pj((BX1, BY, BZ - 0.1)),
            "fuse": Pj(S["fuse"].matrix_world.translation), "noz": Pj((X1 + 0.6, 0, 0.6)), "out": Pj((X1 + 0.6, 0, 0)),
            "hair": Pj((HAIRX + 0.4, 0, 2.0)), "hand": Pj((X0 - 0.4, 0, 1.4)), "body": Pj((0.0, 0, 1.0))}

if __name__ == "__main__":
    run("secador", build, pose, anchors)
