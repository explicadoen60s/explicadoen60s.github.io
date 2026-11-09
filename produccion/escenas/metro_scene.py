# «¿Y si construyes el metro bajo tu ciudad?»: corte de una ciudad con el túnel a 20 m; la rueda de corte araña la tierra;
# rebobinado; calles, casas y tráfico (la zanja no vale); la tuneladora baja por el pozo; regla de 100 m; la rueda con
# cuchillas; el agujero se derrumba; el escudo sujeta; el erector coloca 7 dovelas por anillo (vista desde dentro);
# los gatos empujan contra el último anillo; la cinta lleva la tierra al pozo y a los camiones; 18 m al día, 147 días,
# 189.000 m³ (montaña de tierra); el edificio no puede hundirse: estación topográfica midiendo milímetros; vías, cables,
# estación y tren.
import bpy, bmesh, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("metro")
BG = (0.09, 0.1, 0.13)
L1, L2, L3 = (0.58, 0.45, 0.32), (0.5, 0.38, 0.27), (0.43, 0.32, 0.23)
CONC, CONC2 = (0.78, 0.78, 0.8), (0.66, 0.67, 0.7)
YEL = (0.98, 0.74, 0.12); STEEL = (0.55, 0.58, 0.63); DARK = (0.16, 0.17, 0.2); CUT = (0.85, 0.87, 0.9)
ROCK = (0.33, 0.26, 0.2); ASPH = (0.24, 0.25, 0.28); WALK = (0.62, 0.62, 0.6); BLUE = (0.35, 0.7, 1.0); RED = (0.93, 0.25, 0.25)
GREEN = (0.3, 0.85, 0.45); WHITE = (0.95, 0.95, 0.96); TRAIN = (0.92, 0.93, 0.95); TRAIN2 = (0.85, 0.2, 0.25)
LEJOS = Vector((0, -400, -400))

ZT, RO, RI, RS = -20.0, 4.7, 4.3, 4.95      # eje del túnel, radio exterior/interior de las dovelas, radio del escudo
X0, RING = -24.0, 1.6                       # boca del túnel (pared del pozo) y ancho de anillo
NR = 35
SH0, SH1, SHZ = -38.0, -24.0, -26.0         # pozo
LS = 10.0                                   # largo del escudo
XFIN = 42.0

def arc_mesh(r_out, r_in, x0, x1, a0, a1, color, n=8, loc=(0, 0, 0), unique=True, name="arc"):
    """sector de corona (ángulos en el plano y-z: y = r cos a, z = r sin a) extruido en x"""
    me = bpy.data.meshes.new(name); bm = bmesh.new(); vs = []
    for x in (x0, x1):
        fila = []
        for k in range(n + 1):
            a = mix(a0, a1, k / n); c, s_ = math.cos(a), math.sin(a)
            fila.append((bm.verts.new((x, r_out * c, r_out * s_)), bm.verts.new((x, r_in * c, r_in * s_))))
        vs.append(fila)
    for k in range(n):
        o0, i0 = vs[0][k]; o1, i1 = vs[0][k + 1]; O0, I0 = vs[1][k]; O1, I1 = vs[1][k + 1]
        bm.faces.new((o0, o1, O1, O0)); bm.faces.new((i0, I0, I1, i1)); bm.faces.new((o0, i0, i1, o1)); bm.faces.new((O0, O1, I1, I0))
    for k in (0, n):
        o, i = vs[0][k]; O, I = vs[1][k]; bm.faces.new((o, O, I, i))
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(ob); ob.location = loc
    return setup(ob, color, unique=unique)

def halves(r_out, r_in, x0, x1, color, loc, n=24):
    """corona completa partida en mitad de atrás (y>0, siempre visible) y mitad de delante (solo en la vista interior)"""
    b = arc_mesh(r_out, r_in, x0, x1, -math.pi / 2, math.pi / 2, color, n, loc)
    f = arc_mesh(r_out, r_in, x0, x1, math.pi / 2, 1.5 * math.pi, color, n, loc)
    return b, f

def cone(r, d, color):
    bpy.ops.mesh.primitive_cone_add(radius1=r, radius2=0, depth=d, location=tuple(LEJOS), vertices=16); o = bpy.context.object
    return setup(o, color, unique=True)

def build():
    sc, cam = scene_setup(world=BG, shadow=0.3)
    S = {"cam": cam}
    rng = random.Random(7)
    # ---------- terreno en corte (y >= 0) con el pozo y el túnel ----------
    cutters = []
    c1 = box((SH1 - SH0, 14, 30), ((SH0 + SH1) / 2, 7, SHZ + 15), DARK); cutters.append(c1)
    c2 = cyl(RS + 0.15, 200, (X0 + 100 - 0.01, 0, ZT), DARK, rot=(0, math.pi / 2, 0), v=64); cutters.append(c2)
    for (z0, z1, col) in ((0, -5, L1), (-5, -13, L2), (-13, -60, L3)):
        g = box((300, 60, z0 - z1), (0, 30, (z0 + z1) / 2), col)
        for c in cutters:
            m = g.modifiers.new("b", "BOOLEAN"); m.operation = "DIFFERENCE"; m.object = c; m.solver = "EXACT"
        bpy.context.view_layer.objects.active = g
        for m in list(g.modifiers): bpy.ops.object.modifier_apply(modifier=m.name)
    for c in cutters: bpy.data.objects.remove(c)
    for k in range(90):       # piedras en el corte
        x, z = rng.uniform(-120, 120), rng.uniform(-45, -1.5)
        if abs(z - ZT) < RS + 1.2 or (SH0 - 1 < x < SH1 + 1 and z > SHZ - 1): continue
        sph(rng.uniform(0.25, 0.7), (x, -0.02, z), (0.36, 0.28, 0.2) if z < -13 else (0.45, 0.35, 0.26), scale=(1.4, 0.15, 1))
    # pozo: muro de fondo, suelo
    box((SH1 - SH0, 0.3, -SHZ), ((SH0 + SH1) / 2, 14.0, SHZ / 2), (0.6, 0.61, 0.63))
    box((SH1 - SH0, 14, 0.4), ((SH0 + SH1) / 2, 7, SHZ - 0.2), (0.5, 0.51, 0.53))
    # tapa del frente: tierra delante de la rueda (cubre el hueco aún sin excavar)
    S["tapa"] = box((1, 0.1, 2 * RS + 1.0), (0, -0.06, ZT), L3, unique=True)
    # ---------- superficie: plaza, calle, edificios ----------
    box((300, 9, 0.25), (0, 4.5, 0.12), WALK)
    box((300, 9, 0.25), (0, 13.5, 0.1), ASPH)
    for x in range(-140, 150, 6): box((2.6, 0.3, 0.02), (x, 13.5, 0.24), (0.9, 0.9, 0.85))
    box((300, 4, 0.3), (0, 20, 0.15), WALK)
    pal = [(0.86, 0.72, 0.55), (0.75, 0.55, 0.45), (0.9, 0.85, 0.75), (0.6, 0.66, 0.75), (0.85, 0.6, 0.5), (0.7, 0.75, 0.65)]
    x = -110
    while x < 120:
        w = rng.uniform(8, 13); h = rng.uniform(12, 30); col = rng.choice(pal)
        box((w - 0.6, 12, h), (x + w / 2, 28, h / 2), col)
        for fx in range(int((w - 2) / 2.2)):
            for fz in range(int((h - 3) / 3.2)):
                box((1.1, 0.2, 1.5), (x + 1.6 + fx * 2.2, 21.95, 2.6 + fz * 3.2), (0.25, 0.32, 0.42))
        x += w
    # edificio delante, justo encima del túnel (el que no se puede hundir)
    S["casa"] = casa = empty((11, 5.0, 0.25))
    box((9, 7, 14), (0, 0, 7), (0.88, 0.66, 0.5), parent=casa)
    for fx in range(3):
        for fz in range(4): box((1.4, 0.2, 1.8), (-2.8 + 2.8 * fx, -3.55, 2.8 + fz * 3.0), (0.25, 0.32, 0.42), parent=casa)
    box((9.6, 7.6, 0.6), (0, 0, 14.2), (0.7, 0.5, 0.4), parent=casa)
    S["prisma"] = sph(0.35, (4.3, -3.6, 9.5), (1.0, 0.85, 0.2), parent=casa, unique=True)
    # obra del pozo: valla y grúa
    for xx in (SH0 - 1, SH1 + 1): box((0.2, 9, 2.2), (xx, 4.5, 1.1), (0.95, 0.55, 0.15))
    for k in range(4): box((0.3, 0.3, 34), (-46 + (k % 2) * 1.6, 9 + (k // 2) * 1.6, 17), YEL)
    box((34, 1.2, 1.2), (-33, 9.8, 34.5), YEL); box((1.6, 1.6, 2.5), (-47, 9.8, 36), (0.3, 0.3, 0.33))
    S["carro"] = box((1.6, 1.8, 0.8), (-31, 9.8, 33.6), DARK, unique=True)
    S["cable"] = bar_obj((0.15, 0.15, 0.15), 0.08, unique=True)
    # coches
    S["coches"] = []
    for k in range(9):
        e = empty(tuple(LEJOS)); col = rng.choice([(0.9, 0.25, 0.25), (0.25, 0.5, 0.9), (0.95, 0.85, 0.3), (0.9, 0.9, 0.92), (0.3, 0.7, 0.45)])
        rounded_slab(4.2, 1.9, 0.4, 0.9, (0, 0, 0.45), col, parent=e)
        rounded_slab(2.4, 1.7, 0.35, 0.75, (-0.2, 0, 1.3), (0.3, 0.38, 0.48), parent=e)
        for wx in (-1.3, 1.3): cyl(0.42, 2.0, (wx, 0, 0.42), (0.1, 0.1, 0.1), rot=(math.pi / 2, 0, 0), parent=e)
        S["coches"].append((e, rng.uniform(0, 1), 11.4 if k % 2 else 15.6, 1 if k % 2 else -1))
    # zanja (lo que NO se puede hacer)
    S["zanja"] = box((1, 7.6, 1), tuple(LEJOS), (0.12, 0.09, 0.07), unique=True)
    # ---------- tuneladora ----------
    S["tbm"] = tbm = empty(tuple(LEJOS))
    S["rueda"] = rueda = empty((0, 0, 0), parent=tbm)
    cyl(RS - 0.05, 0.7, (-0.35, 0, 0), (0.58, 0.6, 0.65), rot=(0, math.pi / 2, 0), parent=rueda, v=48)
    for k in range(6):
        a = k * math.pi / 3
        rad = box((0.4, 0.7, RS - 0.3), (0.05, 0.5 * (RS - 0.3) * math.cos(a), 0.5 * (RS - 0.3) * math.sin(a)), YEL, parent=rueda, rot=(a - math.pi / 2, 0, 0))
        for j in range(4):
            r = 1.2 + j * 0.95
            cyl(0.28, 0.25, (0.35, r * math.cos(a + 0.12), r * math.sin(a + 0.12)), CUT, rot=(0, math.pi / 2, 0), parent=rueda, v=12)
    torus(RS - 0.25, 0.22, (0.05, 0, 0), YEL, parent=rueda, rot=(0, math.pi / 2, 0))
    bpy.ops.mesh.primitive_cone_add(radius1=0.9, radius2=0.1, depth=1.0, location=(0.5, 0, 0), rotation=(0, math.pi / 2, 0), vertices=16)
    setup(bpy.context.object, CUT, parent=rueda)
    cyl(2.5, 6.0, (-3.8, 0, 0), YEL, rot=(0, math.pi / 2, 0), parent=tbm, v=32)          # motor
    for k in range(5): cyl(2.6, 0.25, (-1.6 - k * 1.1, 0, 0), (0.85, 0.6, 0.1), rot=(0, math.pi / 2, 0), parent=tbm, v=32)
    S["esc_e"] = esc = empty((-0.75, 0, 0), parent=tbm)      # escudo (crece hacia atrás)
    S["esc_b"], S["esc_f"] = halves(RS, RS - 0.25, -LS + 0.75, 0, STEEL, (0, 0, 0))
    S["esc_b"].parent = esc; S["esc_f"].parent = esc
    S["mamparo"] = halves(RS - 0.25, 2.5, -7.2, -6.9, (0.42, 0.44, 0.48), (0, 0, 0))
    for o in S["mamparo"]: o.parent = tbm
    S["gatos"] = [bar_obj((0.95, 0.75, 0.2), 0.22, unique=True) for _ in range(3)]
    S["gpos"] = [(RI + 0.15) * Vector((0, math.cos(a), math.sin(a))) for a in (-0.9, 0.0, 0.9)]
    S["fl_gato"] = [cone(0.55, 1.4, BLUE) for _ in range(3)]
    # piedras que salta la rueda
    S["piedras"] = [box((1, 1, 1), tuple(LEJOS), ROCK, unique=True) for _ in range(22)]
    S["ppar"] = [(rng.uniform(0, math.tau), rng.uniform(1.5, RS - 0.4), rng.uniform(0, 1), rng.uniform(4, 9), rng.uniform(0.15, 0.4)) for _ in range(22)]
    # derrumbe
    S["trozos"] = [box((rng.uniform(1.0, 1.8), 1.5, rng.uniform(0.8, 1.4)), tuple(LEJOS), L2, rot=(0, rng.uniform(-0.4, 0.4), 0), unique=True) for _ in range(12)]
    # flechas de empuje del terreno sobre el escudo
    S["fl_ter"] = [cone(0.5, 1.3, (0.95, 0.55, 0.2)) for _ in range(6)]
    # ---------- anillos de dovelas (7 piezas) ----------
    S["anillos"] = []
    da = math.tau / 7
    for i in range(NR):
        x = X0 + i * RING; piezas = []
        for j in range(7):
            a0 = -math.pi / 2 + j * da + 0.025; a1 = -math.pi / 2 + (j + 1) * da - 0.025
            col = CONC if (i + j) % 2 else CONC2
            partes = []
            for (b0, b1, front) in ((a0, min(a1, math.pi / 2), False), (max(a0, math.pi / 2), a1, True)):
                if b1 - b0 > 0.01: partes.append((arc_mesh(RO, RI, 0, RING - 0.07, b0, b1, col, 6, (x, 0, ZT)), front))
            piezas.append({"partes": partes, "ac": (a0 + a1) / 2})
        S["anillos"].append(piezas)
    S["brazo"] = bar_obj((0.95, 0.5, 0.15), 0.35, unique=True)
    # ---------- cinta, elevador, camión, montaña ----------
    S["cinta"] = box((1, 1.4, 0.35), tuple(LEJOS), (0.3, 0.32, 0.36), unique=True)
    S["elev"] = box((1.4, 1.4, 1), tuple(LEJOS), (0.3, 0.32, 0.36), unique=True)
    S["bolas"] = [sph(0.6, tuple(LEJOS), (0.48, 0.36, 0.25), seg=10, unique=True) for _ in range(34)]
    S["camion"] = cam_ = empty(tuple(LEJOS))
    box((3, 2.6, 2.6), (3.4, 0, 1.8), (0.95, 0.65, 0.15), parent=cam_); box((0.2, 2.2, 1.0), (4.95, 0, 2.3), (0.3, 0.38, 0.48), parent=cam_)
    box((6, 2.8, 0.3), (-1.2, 0, 1.0), (0.3, 0.3, 0.33), parent=cam_)
    for xx in (-3.8, 1.4): box((0.2, 2.8, 2.0), (xx, 0, 2.0), (0.75, 0.3, 0.2), parent=cam_)
    for yy in (-1.35, 1.35): box((5.4, 0.2, 2.0), (-1.2, yy, 2.0), (0.75, 0.3, 0.2), parent=cam_)
    for wx in (-3, -1.4, 3.2): cyl(0.65, 3.0, (wx, 0, 0.65), (0.1, 0.1, 0.1), rot=(math.pi / 2, 0, 0), parent=cam_)
    S["carga"] = box((5.2, 2.4, 1), (-1.2, 0, 1.2), (0.48, 0.36, 0.25), parent=cam_, unique=True)
    bpy.ops.mesh.primitive_cone_add(radius1=1, radius2=0, depth=1, location=tuple(LEJOS), vertices=24)
    S["monte"] = setup(bpy.context.object, (0.5, 0.38, 0.27), unique=True)
    # ---------- estación topográfica ----------
    S["topo"] = topo = empty(tuple(LEJOS))
    for a in (0, 2.1, 4.2): bar_set(bar_obj((0.85, 0.75, 0.2), 0.06, parent=topo), (0, 0, 1.6), (0.7 * math.cos(a), 0.7 * math.sin(a), 0))
    box((0.6, 0.5, 0.6), (0, 0, 1.95), (0.9, 0.9, 0.92), parent=topo); cyl(0.15, 0.6, (0.3, 0, 2.0), DARK, rot=(0, math.pi / 2, 0), parent=topo)
    S["laser"] = bar_obj(RED, 0.05, unique=True)
    # ---------- vías, cables, estación, tren ----------
    S["rail"] = [box((1, 0.18, 0.25), tuple(LEJOS), (0.7, 0.72, 0.76), unique=True) for _ in range(2)]
    S["losa"] = box((1, 3.6, 0.5), tuple(LEJOS), (0.55, 0.55, 0.57), unique=True)
    S["cables"] = [bar_obj(c, 0.09, unique=True) for c in ((0.95, 0.3, 0.25), (0.2, 0.2, 0.22), (0.3, 0.6, 0.95))]
    S["est"] = est = empty(tuple(LEJOS))
    box((SH1 - SH0, 5.5, 1.6), (0, 3.5, 0.8), (0.82, 0.8, 0.76), parent=est)
    box((SH1 - SH0, 0.3, 0.2), (0, 0.8, 1.65), (0.95, 0.8, 0.2), parent=est)
    for k in range(4): box((2.4, 0.2, 0.5), (-5 + k * 3.4, 6.0, 7.5), (1.0, 0.95, 0.75), parent=est)
    for k in range(12): box((1.0, 3.0, 0.55), (-6 + k * 1.0, 10.5, 1.6 + k * 0.55 + 0.27), (0.7, 0.7, 0.72), parent=est)
    S["tren"] = tren = empty(tuple(LEJOS))
    for c in range(3):
        xc = -c * 15.4
        box((15, 2.8, 3.0), (xc, 0, 1.9), TRAIN, parent=tren)
        box((15.02, 2.82, 0.35), (xc, 0, 0.7), TRAIN2, parent=tren)
        for wk in range(5): box((1.8, 2.84, 1.0), (xc - 6 + wk * 3, 0, 2.4), (0.2, 0.26, 0.35), parent=tren)
    box((0.2, 2.6, 1.3), (7.55, 0, 2.3), (0.2, 0.26, 0.35), parent=tren)
    dyn = [cam, S["tapa"], casa, S["carro"], S["cable"], [c[0] for c in S["coches"]], S["zanja"], tbm, S["esc_b"], S["esc_f"],
           S["gatos"], S["fl_gato"], S["piedras"], S["trozos"], S["fl_ter"], S["brazo"], S["cinta"], S["elev"], S["bolas"], cam_,
           S["monte"], topo, S["laser"], S["rail"], S["losa"], S["cables"], est, tren]
    for piezas in S["anillos"]:
        for p in piezas: dyn += [o for o, _ in p["partes"]]
    join_static(dyn)
    return sc, S

# ---------------- tiempos ----------------
def K():
    return dict(pies=T("bajo tus pies"), tren=T("puede haber"), y_si=T("y si tuvieras"), vamos=T("vamos a excavarlo"),
                prim=T("primero"), calles=T("arriba hay"), casas=T("casas y"), zanja=T("no puedes"), pozo=T("así que bajas"),
                tunel=T("la tuneladora"), mide=T("mide casi"), pesa=T("y pesa"), rueda=T("delante tiene"), derr=T("pero un agujero"),
                asi=T("así que justo"), escudo=T("un escudo"), paso=T("y a cada paso"), brazos=T("unos brazos"), dovelas=T("llamadas dovelas"),
                siete=T("siete piezas"), otro=T("luego otro"), otro2=T("y otro"), avanza=T("la tuneladora avanza"), tierra=T("pero la tierra"),
                cinta=T("así que una cinta"), camiones=T("y de ahí"), curioso=T("y aquí viene"), madrid=T("en la última"),
                avanzo=T("avanzó"), dias=T("en ciento"), casi3=T("casi tres"), saco=T("y sacó"), hundir=T("pero no puede"),
                mide2=T("así que se mide"), mm=T("aunque sea"), termina=T("cuando termina"), vias=T("llegan las vías"),
                cables=T("los cables"), estac=T("y las estaciones"), sig=T("sígueme"))

def xf_of(t, k):
    return keyed(t, [(0, XFIN), (k["y_si"] + 0.4, XFIN), (k["vamos"] - 0.1, -25.0), (k["rueda"] - 0.1, -25.0), (k["derr"] - 0.3, -19.0),
                     (k["asi"], -19.0), (k["paso"] - 0.2, -14.0), (k["otro"] - 0.3, -14.0), (k["otro"] - 0.05, -14 + RING),
                     (k["otro2"] - 0.3, -14 + RING), (k["otro2"] - 0.05, -14 + 2 * RING), (k["avanza"] + 0.4, -14 + 2 * RING),
                     (k["avanza"] + 2.6, -14 + 3 * RING), (k["avanzo"], -14 + 3 * RING), (k["avanzo"] + 2.2, -14 + 3 * RING + 18),
                     (k["dias"], -14 + 3 * RING + 18), (k["casi3"] + 0.8, XFIN)])

def tbm_z(t, k):
    if t < k["vamos"] + 0.2: return ZT
    if t < k["pozo"]: return ZT + mix(0, 60, seg(t, k["vamos"] + 0.2, k["vamos"] + 1.0))
    return mix(ZT + 45, ZT, seg(t, k["pozo"], k["tunel"] + 0.2))

def ring_pieces(i, t, k, tail):
    """nº de piezas puestas (float) del anillo i"""
    if k["vamos"] < t < k["paso"] - 0.4: return 0.0
    if t < k["paso"] - 0.4 or t > k["avanza"]:
        return max(0.0, min(7.0, (tail - (X0 + (i - 0.5) * RING)) / (0.5 * RING) * 7))
    if i == 0: return 7 * seg(t, k["brazos"] - 0.2, k["siete"] + 1.4) if t > k["brazos"] - 0.2 else 0.0
    if i == 1: return 7 * seg(t, k["otro"], k["otro"] + 0.6)
    if i == 2: return 7 * seg(t, k["otro2"], k["otro2"] + 0.5)
    return 0.0

def hide(o): o.location = LEJOS

def pose(t, S):
    k = K()
    xf = xf_of(t, k); zt = tbm_z(t, k)
    vis_tbm = zt < ZT + 40
    S["tbm"].location = (xf, 0, zt) if vis_tbm else LEJOS
    cavando = (t < k["y_si"]) or (k["rueda"] - 0.3 < t < k["paso"]) or (k["avanzo"] - 0.2 < t < k["saco"])
    rot_v = 2.2 if cavando or (k["avanza"] < t < k["avanza"] + 2.8) or (k["tierra"] < t < k["curioso"]) else 0.5
    S["rueda"].rotation_euler = (t * rot_v if t < 6 else 6 * 2.2 + (t - 6) * 1.6, 0, 0)
    interior = k["paso"] - 0.2 < t < k["avanza"] - 0.2
    # escudo: está desde el principio (vídeo terminado) y vuelve a aparecer al decirlo
    g = 1.0 if t < k["vamos"] + 0.5 else seg(t, k["escudo"] - 0.3, k["escudo"] + 0.9)
    S["esc_e"].scale = (max(g, 0.001), 1, 1)
    S["esc_f"].hide_render = not interior
    S["mamparo"][1].hide_render = not interior
    for o in S["mamparo"]: o.hide_render = o.hide_render or g < 0.9
    tail = xf - LS if g > 0.9 else X0 - 10
    tapa_on = not (t < 1.5 or (k["rueda"] - 0.2 < t < k["derr"] - 0.1))
    if tapa_on:
        S["tapa"].scale.x = 150; S["tapa"].location = (xf + 75 + 0.05, -0.06, ZT)
    else: hide(S["tapa"])
    # piedras que saltan de la rueda
    for o, (a, r, ph, sp, sz) in zip(S["piedras"], S["ppar"]):
        if cavando and vis_tbm and zt <= ZT + 0.1:
            u = (t * 1.3 + ph) % 1.0; aa = a + t * 2.2
            p = Vector((xf + 0.4 + 0.5 * sp * u, -r * abs(math.cos(aa)) - 0.3 - 1.2 * u, ZT + r * math.sin(aa) + 2.5 * u - 7 * u * u))
            o.location = p; o.rotation_euler = (t * 3 + a, t * 2, 0); o.scale = (sz * (1 - 0.5 * u),) * 3
        else: hide(o)
    # derrumbe detrás de la rueda (antes del escudo)
    for j, o in enumerate(S["trozos"]):
        if k["derr"] - 0.1 < t < k["asi"] + 0.6:
            u = seg(t, k["derr"] + 0.25 + 0.06 * j, k["derr"] + 1.0 + 0.06 * j)
            x = -23.6 + 0.38 * j
            o.location = (x, 1.5, mix(ZT + RS + 0.3, ZT + 2.7 + 0.25 * (j % 3), u)); o.rotation_euler = (0, 0.4 * u * (1 if j % 2 else -1), 0)
        else: hide(o)
    # flechas del terreno empujando el escudo
    for j, o in enumerate(S["fl_ter"]):
        if k["escudo"] < t < k["paso"] - 0.2:
            u = seg(t, k["escudo"] + 0.3, k["escudo"] + 1.0); x = xf - 2.0 - 2.5 * (j % 3); top = j < 3
            zz = ZT + (RS + 1.2 + 0.25 * math.sin(t * 7 + j)) * (1 if top else -1)
            o.location = (x, 0.3, zz); o.rotation_euler = (math.pi if top else 0, 0, 0); o.scale = (u + 0.001,) * 3
        else: hide(o)
    # anillos
    nlast = -1
    for i, piezas in enumerate(S["anillos"]):
        n = ring_pieces(i, t, k, tail)
        if n >= 6.99: nlast = i
        for j, p in enumerate(piezas):
            u = max(0.0, min(1.0, n - j))
            ac = p["ac"]; off = Vector((0, math.cos(ac), math.sin(ac))) * (-2.6 * (1 - u))
            for o, front in p["partes"]:
                if u <= 0.0: hide(o); continue
                o.location = Vector((X0 + i * RING, 0, ZT)) + off
                o.hide_render = front and not interior
    # brazo erector: lleva la pieza que se está colocando
    br = None
    if interior:
        for i in range(3):
            n = ring_pieces(i, t, k, tail)
            if 0 < n < 7:
                j = int(n); ac = S["anillos"][i][j]["ac"]; u = n - j
                br = (Vector((X0 + i * RING + 0.8, 0, ZT)), Vector((X0 + i * RING + 0.8, 0, ZT)) + Vector((0, math.cos(ac), math.sin(ac))) * (RI - 2.6 * (1 - u) - 0.3))
    if br: bar_set(S["brazo"], br[0], br[1])
    else: hide(S["brazo"])
    # gatos: del mamparo al último anillo
    xlast = X0 + (nlast + 1) * RING
    push = (k["avanza"] - 0.2 < t < k["avanza"] + 3.0) or (k["otro"] - 0.4 < t < k["otro"]) or (k["otro2"] - 0.4 < t < k["otro2"])
    for gk, (o, gp, fl) in enumerate(zip(S["gatos"], S["gpos"], S["fl_gato"])):
        if nlast >= 0 and g > 0.9 and vis_tbm and xf - 6.9 > xlast:
            bar_set(o, Vector((xlast, 0, ZT)) + gp, Vector((xf - 6.9, 0, ZT)) + gp)
            o["r"] = 0.22
        else: hide(o)
        if push and nlast >= 0 and k["avanza"] - 0.2 < t:
            fl.location = Vector((xlast + 0.9 + 0.3 * math.sin(t * 8 + gk), 0, ZT)) + gp * 0.8
            fl.rotation_euler = (0, -math.pi / 2, 0)
        else: hide(fl)
    # coches
    for e, ph, y, d in S["coches"]:
        stop = seg(t, k["zanja"] - 0.2, k["zanja"] + 0.6) * (1 - seg(t, k["pozo"], k["pozo"] + 0.4))
        sp = 0.025 * (1 - 0.0 * stop)
        u = (ph + d * t * sp) % 1.0
        x = -100 + 200 * u
        if stop > 0.01 and -26 < x < 60:          # se paran ante la zanja
            x = min(x, 2) if d > 0 else max(x, 2)
        e.location = (x, y, 0.2); e.rotation_euler = (0, 0, 0 if d > 0 else math.pi)
    # zanja abierta por la calle
    z = seg(t, k["zanja"] + 0.2, k["zanja"] + 1.0) * (1 - seg(t, k["pozo"] - 0.3, k["pozo"] + 0.2))
    if z > 0.01:
        S["zanja"].scale = (70 * z, 18.3, 9 * z); S["zanja"].location = (-5 + 35 * z, 9.1, 0.4 - 4.5 * z)
    else: hide(S["zanja"])
    # grúa: carro y cable hasta la tuneladora mientras baja
    S["carro"].location = (-31, 9.8, 33.6)
    if k["vamos"] + 0.2 < t < k["tunel"] + 1.0 and vis_tbm:
        bar_set(S["cable"], (-31, 9.8, 33.2), (xf - 5, 0, zt + RS)); S["cable"]["r"] = 0.08
    else: hide(S["cable"])
    # cinta, elevador y bolas de tierra
    cinta_on = t > k["tierra"] - 0.3 or t < k["vamos"]
    if cinta_on and vis_tbm:
        x0c, x1c = -36.0, xf - 5.0
        S["cinta"].scale = (x1c - x0c, 1.4, 0.35); S["cinta"].location = ((x0c + x1c) / 2, 1.6, ZT - RI + 0.75)
        S["elev"].scale = (1.4, 1.4, 0 - (ZT - RI + 0.6) + 3.0); S["elev"].location = (-36.7, 1.6, (ZT - RI + 0.6 + 3.0) / 2)
    else: hide(S["cinta"]); hide(S["elev"])
    pts = [Vector((xf - 5.0, 1.6, ZT - RI + 1.25)), Vector((-36.0, 1.6, ZT - RI + 1.25)), Vector((-36.0, 1.6, 3.4)), Vector((-43.0, 1.6, 4.2))]
    segl = [(b - a).length for a, b in zip(pts, pts[1:])]; L = sum(segl)
    flow = cinta_on and vis_tbm and (t < k["vamos"] or k["tierra"] < t < k["hundir"])
    for j, o in enumerate(S["bolas"]):
        if not flow: hide(o); continue
        d = ((j / len(S["bolas"])) * L + t * 9.0) % L
        if t > k["tierra"] and t < k["cinta"] + 0.5: d = min(d, (t - k["tierra"]) * 9.0)
        for a, b, l in zip(pts, pts[1:], segl):
            if d <= l: o.location = a.lerp(b, d / l); break
            d -= l
    # camión que se lleva la tierra
    cm = S["camion"]
    drive = seg(t, k["camiones"] + 0.4, k["curioso"] + 0.3)
    back = seg(t, k["curioso"] + 1.5, k["madrid"] + 1.5)
    xcam = -47.5 - 40 * drive + 40 * back
    cm.location = (xcam, 4.5, 0.25); cm.rotation_euler = (0, 0, math.pi)
    fill = seg(t, k["cinta"] + 1.5, k["camiones"] + 0.4) * (1 - back) if t < k["madrid"] + 2 else 0.5 + 0.5 * math.sin(t * 2) ** 2
    S["carga"].scale = (5.2, 2.4, max(0.02, 2.2 * fill)); S["carga"].location.z = 1.1 + 1.1 * fill
    # montaña de tierra sacada
    m = seg(t, k["saco"], k["saco"] + 3.0)
    if m > 0.01:
        S["monte"].location = (-66, 9, 0); S["monte"].scale = (13 * m, 9 * m, 10 * m); S["monte"].location.z = 5 * m
    else: hide(S["monte"])
    # edificio que se hunde (lo que no puede pasar) y vuelve
    hz = seg(t, k["hundir"] + 0.3, k["hundir"] + 1.2) * (1 - seg(t, k["mide2"] - 0.1, k["mide2"] + 0.4))
    S["casa"].location = (11, 5.0, 0.25 - 1.6 * hz); S["casa"].rotation_euler = (0, -0.07 * hz, 0)
    # estación topográfica con láser al prisma
    if k["mide2"] - 0.3 < t < k["termina"]:
        S["topo"].location = (-6, 2.5, 0.25)
        pr = S["casa"].matrix_world @ Vector((4.3, -3.6, 9.5))
        if t > k["mide2"] + 0.4: bar_set(S["laser"], (-5.7, 2.5, 2.25), pr)
        else: hide(S["laser"])
        set_color(S["prisma"], (1.0, 0.25, 0.2) if int(t * 4) % 2 else (1.0, 0.85, 0.2))
    else: hide(S["topo"]); hide(S["laser"])
    # vías, cables y estación
    fin = t > k["termina"] or t < k["vamos"]
    if fin:
        u = 1.0 if t < k["vamos"] else seg(t, k["vias"] - 0.1, k["vias"] + 0.9)
        x0r, x1r = SH0, XFIN - LS - 0.5; xr = mix(x0r, x1r, u)
        S["losa"].scale = (xr - x0r, 3.6, 0.5); S["losa"].location = ((x0r + xr) / 2, 0.0, ZT - RI + 0.55)
        for o, yy in zip(S["rail"], (-0.75, 0.75)):
            o.scale = (xr - x0r, 0.18, 0.25); o.location = ((x0r + xr) / 2, yy, ZT - RI + 0.92)
        uc = 1.0 if t < k["vamos"] else seg(t, k["cables"] - 0.1, k["cables"] + 0.8)
        for j, o in enumerate(S["cables"]):
            p0 = Vector((X0 + 0.3, 3.0, ZT + 2.0 + 0.35 * j)); bar_set(o, p0, p0 + Vector(((x1r - X0) * uc + 0.01, 0, 0)))
        ue = 1.0 if t < k["vamos"] else seg(t, k["estac"] - 0.1, k["estac"] + 0.6)
        if ue > 0.01: S["est"].location = ((SH0 + SH1) / 2, 0, SHZ + 2.0 - 8 * (1 - ue)); S["est"].scale = (1, 1, max(ue, 0.01))
        else: hide(S["est"])
    else:
        hide(S["losa"]); hide(S["est"]); [hide(o) for o in S["rail"] + S["cables"]]
    # tren
    tr = S["tren"]
    if t < k["vamos"]:
        x = mix(24, -16, seg(t, 0.8, k["vamos"])); tr.location = (x, 0, ZT - RI + 0.65); tr.scale = (1, 1, 1)
    elif t > k["estac"] - 0.6:
        x = mix(62, -23, seg(t, k["estac"] - 0.6, DUR + 0.3)); tr.location = (x, 0, ZT - RI + 0.65)
    else: hide(tr)
    apply_cam(S["cam"], *cam_state(t, CAM(k), drift=0.08))

def V(at, off, lens=30):
    return (tuple(Vector(at) + Vector(off)), tuple(at), lens)

def CAM(k):
    c = []
    def add(t, v): c.append((t,) + v)
    xi = XFIN
    add(0.0, V((xi - 0.3, -0.5, ZT + 0.2), (7.0, -8.0, 1.3), 28))
    add(0.9, V((xi - 1.0, -0.5, ZT + 0.3), (7.5, -10.5, 1.6), 28))
    add(k["tren"], V((xi - 6, 0, ZT + 2), (4, -24, 4), 28))
    add(k["y_si"], V((6, 0, -9), (0, -62, 6), 28))
    add(k["vamos"] + 0.6, V((-12, 0, -8), (0, -64, 6), 28))
    add(k["calles"], V((2, 12, 6), (0, -36, 9), 30))
    add(k["zanja"] + 0.3, V((14, 9, -2), (-2, -46, 10), 30))
    add(k["pozo"] - 0.3, V((10, 9, -2), (-2, -46, 10), 30))
    add(k["pozo"] + 0.3, V((-31, 4, -3), (8, -48, 8), 30))
    add(k["tunel"] + 0.2, V((-28, 0, ZT + 1), (7, -32, 5), 30))
    add(k["mide"] + 0.4, V((15, 0, -14), (0, -112, 6), 22))
    add(k["pesa"] + 1.6, V((15, 0, -14), (0, -108, 5), 22))
    add(k["rueda"] + 0.3, V((-22.0, -0.5, ZT + 0.2), (9.5, -11.0, 1.8), 28))
    add(k["derr"] - 0.2, V((-19.5, -0.5, ZT + 0.5), (8.5, -12.0, 2.0), 28))
    add(k["derr"] + 0.8, V((-21.0, 0, ZT + 1.5), (1.0, -21, 2.5), 30))
    add(k["escudo"] + 0.6, V((-19.5, 0, ZT + 0.5), (1.5, -23, 2.5), 30))
    add(k["paso"] + 0.5, V((-23.0, 0, ZT + 0.2), (-11, -6.0, 1.2), 28))
    add(k["siete"], V((-23.0, 0, ZT + 0.2), (-12, -5.0, 1.0), 28))
    add(k["otro2"] + 0.5, V((-21.0, 0, ZT + 0.2), (-12, -6.0, 1.0), 28))
    add(k["avanza"] + 0.5, V((-15.5, 0, ZT + 0.5), (1.5, -22, 2.5), 30))
    add(k["tierra"] + 0.4, V((-14, 0, ZT - 1), (1, -30, 3), 30))
    add(k["cinta"] + 1.0, V((-30, 0, ZT + 2), (2, -34, 3), 30))
    add(k["camiones"] - 0.3, V((-38, 0, -6), (2, -38, 4), 30))
    add(k["camiones"] + 0.2, V((-45, 3, 3), (4, -30, 6), 30))
    add(k["curioso"] + 0.4, V((-8, 0, -12), (0, -62, 3), 28))
    add(k["avanzo"] + 1.0, V((-4, 0, -13), (0, -60, 3), 28))
    add(k["casi3"] + 0.6, V((22, 0, -13), (0, -66, 3), 28))
    add(k["saco"] + 1.5, V((-60, 6, 3), (6, -40, 6), 30))
    add(k["hundir"] + 0.3, V((8, 3, -5), (-3, -44, 6), 30))
    add(k["mide2"] + 0.5, V((3, 3, 4), (-3, -28, 6), 30))
    add(k["mm"] + 0.9, V((4, 3, 4), (-2, -29, 6), 30))
    add(k["termina"] + 0.6, V((-8, 0, ZT - 1), (2, -30, 3), 30))
    add(k["estac"] + 0.5, V((-24, 0, ZT - 2), (3, -32, 3), 30))
    add(DUR + 2, V((-26, 0, ZT - 2), (2, -36, 4), 30))
    return c

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v); k = K(); xf = xf_of(t, k)
    return {"surf": Pj((xf - 14, 0, 0.3)), "axis": Pj((xf - 14, 0, ZT)), "pozo": Pj(((SH0 + SH1) / 2, 0, 2)),
            "tbm": Pj(S["tbm"].location + Vector((-3, 0, RS + 1))), "rA": Pj((xf - LS, 0, ZT - RS - 1)), "rB": Pj((xf - LS + 100, 0, ZT - RS - 1)),
            "rueda": Pj((xf, 0, ZT + RS)), "derr": Pj((-22, 0, ZT + RS)), "anillo": Pj((X0 + RING, 0, ZT + RO)),
            "cinta": Pj((xf - 20, 0, ZT - RI)), "camion": Pj(S["camion"].location + Vector((0, 0, 5))),
            "monte": Pj((-66, 9, 10)), "casa": Pj((11, 5, 16)), "zanja": Pj((25, 13.5, 0.5)), "topo": Pj((-6, 2.5, 2.5)),
            "vias": Pj((0, 0, ZT - RI + 1)), "cables": Pj((10, 3, ZT + 2.5)), "est": Pj(((SH0 + SH1) / 2, 0, SHZ + 6)),
            "face": Pj((xf + 0.5, 0, ZT))}

if __name__ == "__main__":
    run("metro", build, pose, anchors)
