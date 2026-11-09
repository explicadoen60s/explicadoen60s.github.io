# «Si tuvieras que inventar el velcro…»: macro de una tira de ganchos despegándose de la de bucles (el contador baja);
# zapatilla; 1941: ingeniero y perro llenos de cardos; cardo al microscopio (cada púa acaba en gancho); tira de ganchos que
# no tiene dónde engancharse; tira de bucles; al apretar se enganchan; el algodón se aplasta; nailon: bucles cortados por
# un lado = ganchos que vuelven a su forma; un gancho solo suelta una anilla; cuadrado de 2,5 cm con 300; tirón de golpe
# (aguanta) frente a despegar desde el borde (se sueltan de pocos en pocos); 1941 → 1955 y la zapatilla se cierra.
import bpy, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector, Quaternion

T, DUR = cargar("velcro")
BG = (0.08, 0.09, 0.12)
HOOK_N = (0.35, 0.72, 1.0); TAPE_H = (0.14, 0.32, 0.62)          # nailon: ganchos azules
LOOP_N = (0.93, 0.94, 0.97); TAPE_L = (0.42, 0.44, 0.5)           # nailon: bucles blancos
COT = (0.9, 0.8, 0.58); COT_D = (0.7, 0.6, 0.42)                  # algodón
BURR = (0.45, 0.5, 0.22); SPINE = (0.72, 0.68, 0.3); FUR = (0.85, 0.62, 0.35); SKIN = (0.93, 0.72, 0.58)
STEEL = (0.78, 0.8, 0.85); RED = (0.9, 0.25, 0.3); WHITE = (0.95, 0.95, 0.97)
LEJOS = (0, 0, -500)
NC = 25; XS = [-6 + 0.5 * i for i in range(NC)]; ROWS = [-0.75, -0.25, 0.25, 0.75]
ZH0 = 0.75
DOG = Vector((80, 0, 0)); MIC = Vector((160, 0, 0)); CUT = Vector((-80, 0, 0))

def K():
    return dict(zap=T("tus zapatillas"), vamos=T("vamos a inventar"), ano=T("en mil novecientos cuarenta"), ing=T("un ingeniero"),
                cardos=T("los dos van"), micro=T("los mira"), pin=T("y cada pinchito"), copiar=T("así que quieres"),
                tira=T("una tira cubierta"), pero=T("pero los ganchos"), otra=T("así que la otra"), hilos=T("hilos en forma"),
                apretar=T("al apretar"), cada=T("cada gancho se mete"), algodon=T("pero el algodón"), nailon=T("así que usas"),
                tejes=T("tejes bucles"), cortas=T("y luego cortas"), duros=T("así salen"), vuelven=T("que vuelven"),
                curioso=T("y aquí viene"), solo=T("un solo gancho"), hay=T("pero hay unos"), cuadrado=T("un cuadrado"),
                golpe=T("si tiras de golpe"), aguanta=T("y aguanta"), borde=T("pero si lo despegas"), sueltas=T("sueltas los"),
                facil=T("por eso se abre"), suena=T("y por eso suena"), tardo=T("tardó"), patento=T("lo patentó"), sig=T("sígueme"))
KK = None

def curve(splines, bevel, color, unique=False, parent=None, loc=(0, 0, 0)):
    cu = bpy.data.curves.new("c", 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = bevel; cu.bevel_resolution = 2
    for pts in splines:
        sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
        for i, p in enumerate(pts): sp.points[i].co = (*p, 1)
    o = bpy.data.objects.new("c", cu); bpy.context.collection.objects.link(o); o.location = loc
    o.data.materials.append(mat(color, unique))
    if parent: o.parent = parent
    return o

def hook_pts(y, s=1.0):
    """gancho colgando hacia abajo desde z=0, en el plano xz"""
    p = [(0, y, 0), (0, y, -0.42 * s)]
    for k in range(9):
        a = math.pi + math.pi * k / 8; p.append((0.11 * s + 0.11 * s * math.cos(a), y, -0.42 * s + 0.11 * s * math.sin(a)))
    p.append((0.22 * s, y, -0.31 * s)); return p

def loop_pts(x, y, hw=0.15, h=0.5):
    p = [(x, y + hw, 0)]
    for k in range(11):
        a = math.pi * k / 10; p.append((x, y + hw * math.cos(a), h - hw + hw * math.sin(a)))
    p.append((x, y - hw, 0)); return p

def spiky_burr(r, n, parent, rng, spine_len=0.6, hooks=False, col=BURR):
    sph(r, (0, 0, 0), col, parent=parent, seg=12)
    out = []
    for i in range(n):
        z = 1 - 2 * (i + 0.5) / n; th = i * 2.399963
        d = Vector((math.sqrt(1 - z * z) * math.cos(th), math.sqrt(1 - z * z) * math.sin(th), z))
        o = bar_obj(SPINE, r * 0.07, parent=parent); bar_set(o, d * r * 0.8, d * (r + spine_len))
        out.append(d)
    return out

def build():
    global KK
    KK = K()
    sc, cam = scene_setup(world=BG, shadow=0.35)
    S = {"cam": cam}; rng = random.Random(7)
    # ---------- tira de bucles (abajo) y de ganchos (arriba) ----------
    S["ltape"] = box((13.2, 2.3, 0.18), (0, 0, -0.09), TAPE_L, unique=True)
    S["loops"] = curve([loop_pts(x + 0.11, y) for x in XS for y in ROWS], 0.035, LOOP_N, unique=True)
    S["cols"] = []
    S["hmat"] = None
    for i, x in enumerate(XS):
        e = empty((x, 0, ZH0))
        tp = box((0.5, 2.3, 0.16), (0.11, 0, 0.08), TAPE_H, parent=e)
        hk = curve([hook_pts(y) for y in ROWS], 0.035, HOOK_N, parent=e)
        S["cols"].append((e, hk, tp))
    S["htmat"] = S["cols"][0][2].active_material; S["hkmat"] = S["cols"][0][1].active_material
    # ---------- zapatilla debajo de la tira ----------
    sh = empty((0, 0, 0)); S["shoe"] = sh
    SHC = (0.85, 0.3, 0.32)
    rounded_slab(13.4, 32, 5.5, 2.6, (0, -2, -12.2), WHITE, parent=sh)
    rounded_slab(12.4, 21, 5.0, 9.3, (0, 2.5, -9.6), SHC, parent=sh)
    sph(1, (0, -7.5, -6.6), SHC, parent=sh, scale=(6.2, 9.5, 4.2), seg=32)
    box((12.6, 0.6, 1.2), (0, -15.6, -9.0), (0.9, 0.9, 0.92), parent=sh)
    cyl(3.6, 0.4, (0, 8.6, -0.25), (0.1, 0.1, 0.12), parent=sh)
    torus(3.8, 0.55, (0, 8.6, -0.2), (0.25, 0.25, 0.3), parent=sh)
    for s_ in (-1, 1): box((0.2, 9, 1.0), (s_ * 6.25, 2, -7.5), (0.95, 0.95, 0.97), parent=sh, rot=(0.25, 0, 0))
    box((60, 60, 0.4), (0, 0, -12.9), (0.16, 0.17, 0.21))
    # ---------- 1941: ingeniero y perro con cardos ----------
    box((70, 30, 0.4), DOG + Vector((0, 4, -0.2)), (0.2, 0.28, 0.2))
    for k in range(10):
        sph(rng.uniform(1.2, 2.2), DOG + Vector((rng.uniform(-30, 30), rng.uniform(10, 16), 0.5)), (0.25, 0.38, 0.24), scale=(1, 1, 1.4), seg=12)
    dg = empty(DOG); S["dog"] = dg
    sph(1, (0, 0, 2.2), FUR, parent=dg, scale=(2.4, 1.1, 1.0))
    hd = sph(0.9, (2.4, 0, 3.3), FUR, parent=dg)
    sph(0.45, (3.2, 0, 3.05), (0.92, 0.72, 0.48), parent=dg, scale=(1.2, 0.9, 0.8))
    sph(0.15, (3.75, 0, 3.15), (0.1, 0.1, 0.1), parent=dg)
    for s in (-1, 1):
        sph(0.12, (3.0, s * 0.42, 3.6), (0.1, 0.1, 0.1), parent=dg)
        sph(0.4, (2.1, s * 0.75, 3.7), (0.6, 0.38, 0.2), parent=dg, scale=(0.6, 0.4, 1.2))
    S["legs"] = []
    for lx in (-1.6, 1.5):
        for s in (-1, 1):
            le = empty((lx, s * 0.6, 2.0), dg); cyl(0.3, 1.9, (0, 0, -0.95), FUR, parent=le)
            S["legs"].append(le)
    S["tail"] = tl = empty((-2.3, 0, 2.6), dg); cyl(0.18, 1.6, (0, 0, 0.8), FUR, parent=tl)
    man = empty(DOG + Vector((-4.5, 1.5, 0))); S["man"] = man
    S["mlegs"] = []
    for s in (-1, 1):
        le = empty((0, s * 0.55, 5.2), man); cyl(0.5, 5.2, (0, 0, -2.6), (0.3, 0.33, 0.45), parent=le)
        box((1.4, 0.8, 0.5), (0.35, 0, -5.0), (0.25, 0.18, 0.12), parent=le); S["mlegs"].append(le)
    box((1.4, 2.2, 3.6), (0, 0, 7.0), (0.55, 0.42, 0.3), parent=man)
    sph(0.9, (0, 0, 9.6), SKIN, parent=man)
    cyl(1.1, 0.5, (0, 0, 10.3), (0.3, 0.25, 0.2), parent=man); cyl(1.6, 0.12, (0, 0, 10.05), (0.3, 0.25, 0.2), parent=man)
    for s in (-1, 1): cyl(0.35, 3.4, (0, s * 1.4, 7.0), (0.55, 0.42, 0.3), parent=man)
    S["burrs"] = []
    spots = [(dg, (0.3, -1.05, 2.6)), (dg, (-1.2, -0.95, 2.1)), (dg, (1.2, -0.9, 1.8)), (dg, (-0.4, -1.0, 1.6)), (dg, (2.3, -0.8, 3.4)),
             (dg, (-1.9, -0.8, 2.7)), (man, (0.2, -1.0, 3.2)), (man, (0.3, -0.9, 1.8)), (man, (0.1, -1.3, 6.2)), (man, (0.4, -0.9, 4.2))]
    for par, p in spots:
        be = empty(p, par); spiky_burr(0.32, 14, be, rng, 0.22); S["burrs"].append(be)
    # ---------- cardo al microscopio ----------
    mb = empty(MIC); S["mic"] = mb
    sph(2.0, (0, 0, 0), BURR, parent=mb, seg=24)
    S["sp_hooks"] = []
    n = 46
    for i in range(n):
        z = 1 - 2 * (i + 0.5) / n; th = i * 2.399963
        d = Vector((math.sqrt(1 - z * z) * math.cos(th), math.sqrt(1 - z * z) * math.sin(th), z))
        se = empty((0, 0, 0), mb); se.rotation_mode = 'QUATERNION'; se.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d)
        cyl(0.07, 2.0, (0, 0, 2.6), SPINE, parent=se, v=10)
        hk = curve([[(0, 0, 3.55), (0, 0, 3.75)] + [(0.13 - 0.13 * math.cos(math.pi * k / 8), 0, 3.75 + 0.13 * math.sin(math.pi * k / 8)) for k in range(1, 9)]
                    + [(0.26, 0, 3.6)]], 0.055, (1.0, 0.85, 0.3), parent=se)
        S["sp_hooks"].append(hk)
    S["mic_tip"] = Vector((0, 0, 1))
    # ---------- taller de corte (bucles grandes → ganchos) ----------
    box((14, 3.0, 0.5), CUT + Vector((0, 0, -0.25)), TAPE_L)
    S["bloops"] = []; S["bhooks"] = []; S["bstubs"] = []
    for j, x in enumerate((-3.5, 0, 3.5)):
        pts = [(0.6, 0, 0), (0.6, 0, 1.9)] + [(0.6 * math.cos(math.pi * k / 12), 0, 1.9 + 0.6 * math.sin(math.pi * k / 12)) for k in range(1, 12)] + [(-0.6, 0, 1.9), (-0.6, 0, 0)]
        lp = curve([pts], 0.11, LOOP_N, unique=True, loc=CUT + Vector((x, 0, 0)))
        S["bloops"].append(lp)
        # gancho resultante (pierna derecha + arco + un poco de la izquierda), origen en su base
        hp = [(0, 0, 0), (0, 0, 1.9)] + [(-0.6 + 0.6 * math.cos(math.pi * k / 12), 0, 1.9 + 0.6 * math.sin(math.pi * k / 12)) for k in range(1, 12)] + [(-1.2, 0, 1.9), (-1.2, 0, 1.35)]
        hk = curve([hp], 0.11, HOOK_N, unique=True, loc=LEJOS); S["bhooks"].append(hk)
        st = curve([[(0, 0, 0), (0, 0, 0.95)]], 0.11, HOOK_N, unique=True, loc=LEJOS); S["bstubs"].append(st)
    S["blade"] = bl = empty(LEJOS)
    box((0.9, 2.2, 0.07), (0, 0, 0), STEEL, parent=bl); box((0.5, 1.8, 0.35), (0, -2.0, 0), (0.9, 0.3, 0.3), parent=bl)
    S["ring"] = torus(0.55, 0.09, LEJOS, (0.95, 0.75, 0.3), rot=(0, 0, 0), unique=True)
    S["weight"] = box((0.7, 0.7, 0.7), LEJOS, (0.5, 0.5, 0.55), unique=True)
    S["finger"] = fg = empty(LEJOS)
    sph(0.55, (0, 0, 0), SKIN, parent=fg, scale=(1, 1, 1.1)); cyl(0.55, 4, (0, 0, 2.0), SKIN, parent=fg)
    dyn = [cam, S["ltape"], S["loops"], [c[0] for c in S["cols"]], sh, dg, man, mb, S["bloops"], S["bhooks"], S["bstubs"], bl,
           S["ring"], S["weight"], fg]
    join_static(dyn)
    return sc, S

# ---------------- estado de las tiras ----------------
def xfront(t):
    k = KK
    if t < k["vamos"] + 0.3: return mix(-4.8, 8.0, seg(t, 0.0, k["vamos"] + 0.2) ** 0.8)
    if t < k["borde"]: return -9.0 if t > k["copiar"] - 1 else 8.0
    if t < k["tardo"]: return mix(-7.0, 7.0, seg(t, k["borde"] + 0.2, k["suena"] + 1.2))
    return mix(7.0, -7.0, seg(t, k["tardo"] + 0.1, k["patento"] + 0.8))

def tape_state(t):
    """(zh, escala ganchos, escala bucles, ganchos visibles, bucles visibles, algodón 0..1)"""
    k = KK
    zh = ZH0; hs = 1.0; ls = 1.0; cot = 0.0
    if k["copiar"] - 0.5 < t < k["nailon"] + 0.6:
        cot = 1.0 - seg(t, k["nailon"], k["nailon"] + 0.5)
        zh = 2.2
        if t < k["apretar"] + 0.2:
            zh = 2.2 - 1.5 * (seg(t, k["pero"] + 0.6, k["pero"] + 1.1) - seg(t, k["pero"] + 1.5, k["pero"] + 2.1))
        else:
            zh = mix(2.2, ZH0, seg(t, k["apretar"] + 0.1, k["cada"] + 0.2))
        crush = seg(t, k["algodon"] + 0.5, k["algodon"] + 1.6) * (1 - seg(t, k["nailon"], k["nailon"] + 0.6))
        ls = 1 - 0.55 * crush; hs = 1 - 0.3 * crush; zh -= 0.35 * crush
        if t < k["tira"] + 1.5: hs = max(1e-3, seg(t, k["tira"] - 0.2, k["tira"] + 1.0))
        ls *= max(1e-3, seg(t, k["hilos"] - 0.3, k["hilos"] + 0.8)) if t < k["hilos"] + 1 else 1
    if k["golpe"] < t < k["borde"]:
        u = seg(t, k["golpe"] + 0.1, k["golpe"] + 0.6) * (1 - seg(t, k["aguanta"] + 0.4, k["borde"] - 0.05))
        zh = ZH0 + 0.28 * u + 0.03 * math.sin(t * 40) * u; ls = 1 + 0.55 * u
    showL = not (k["copiar"] - 0.5 < t < k["otra"])
    return zh, hs, ls, showL, cot

def col_pose(t, x, zh):
    xf = xfront(t); d = max(0.0, xf - x)
    lift = 3.2 * (1 - math.exp(-d * 0.8 / 3.2)); ang = math.atan(0.8 * math.exp(-d * 0.8 / 3.2)) if d > 0 else 0.0
    return lift, ang

def engaged(t):
    zh, hs, ls, showL, cot = tape_state(t)
    if not showL or zh > 1.2: return 0
    return sum(1 for x in XS if col_pose(t, x, zh)[0] < 0.18) * 12

def pose(t, S):
    k = KK
    zh, hs, ls, showL, cot = tape_state(t)
    hc = tuple(mix(a, b, cot) for a, b in zip(HOOK_N, COT)); tc = tuple(mix(a, b, cot) for a, b in zip(TAPE_H, COT_D))
    lc = tuple(mix(a, b, cot) for a, b in zip(LOOP_N, COT)); ltc = tuple(mix(a, b, cot) for a, b in zip(TAPE_L, COT_D))
    S["hkmat"].diffuse_color = (*lin(hc), 1); S["htmat"].diffuse_color = (*lin(tc), 1)
    set_color(S["loops"], lc); set_color(S["ltape"], ltc)
    on_main = not (k["ano"] - 0.1 < t < k["copiar"] - 0.6)
    # tira de ganchos aparece al «inventarla»
    born = seg(t, k["copiar"] - 0.4, k["tira"]) if k["copiar"] - 1 < t < k["tira"] + 1 else 1.0
    for i, (e, hk, tp) in enumerate(S["cols"]):
        lift, ang = col_pose(t, XS[i], zh)
        b = max(1e-3, seg(born * 1.6, i / NC * 0.6, i / NC * 0.6 + 0.4)) if born < 1 else 1.0
        e.location = (XS[i], 0, zh + lift) if on_main else LEJOS
        e.rotation_euler = (0, -ang, 0); e.scale = (1, b, b)
        hs_i = hs
        if lift > 0.18: hs_i = hs * (1 + 0.08 * math.sin(t * 30 + i) * math.exp(-(lift - 0.18) * 3))
        hk.scale = (1, 1, max(1e-3, hs_i))
    S["loops"].location = (0, 0, 0) if (showL and on_main) else LEJOS
    S["ltape"].location = (0, 0, -0.09) if (showL and on_main) else LEJOS
    if k["otra"] - 0.5 < t < k["otra"] + 1.0:
        S["ltape"].scale = (13.2 * max(1e-3, seg(t, k["otra"], k["otra"] + 0.7)), 2.3, 0.18)
    else: S["ltape"].scale = (13.2, 2.3, 0.18)
    S["loops"].scale = (1, 1, max(1e-3, ls))
    S["shoe"].location = (0, 0, 0) if on_main and (t < k["copiar"] - 1 or t > k["tardo"] - 0.3) else LEJOS
    # ---------- perro e ingeniero caminando ----------
    if k["ano"] - 0.6 < t < k["micro"] + 0.6:
        w = t - k["ano"]
        S["dog"].location = DOG + Vector((-3 + 1.1 * w, 0, 0.15 * abs(math.sin(w * 7))))
        S["man"].location = DOG + Vector((-8.5 + 1.1 * w, 2.0, 0.1 * abs(math.sin(w * 3.5))))
        for j, le in enumerate(S["legs"]): le.rotation_euler = (0, 0.5 * math.sin(w * 7 + (j % 2 + j // 2) * math.pi), 0)
        for j, le in enumerate(S["mlegs"]): le.rotation_euler = (0, 0.4 * math.sin(w * 3.5 + j * math.pi), 0)
        S["tail"].rotation_euler = (0.5 * math.sin(w * 9), -0.6, 0)
        for j, b in enumerate(S["burrs"]):
            s = seg(t, k["cardos"] - 0.2 + 0.12 * j, k["cardos"] + 0.15 + 0.12 * j)
            b.scale = (max(1e-3, s),) * 3; b.rotation_euler = (0, 0, j)
    else:
        S["dog"].location = LEJOS; S["man"].location = LEJOS
    # ---------- microscopio ----------
    if k["micro"] - 0.6 < t < k["copiar"] - 0.5:
        S["mic"].location = MIC; S["mic"].rotation_euler = (0.25, 0.15 * math.sin(t * 0.5), 0.25 * t)
        g = seg(t, k["pin"], k["pin"] + 0.8)
        for hk in S["sp_hooks"]: hk.scale = (1 + 0.6 * g * (0.5 + 0.5 * math.sin(t * 6)), 1, 1)
    else: S["mic"].location = LEJOS
    # ---------- taller de corte ----------
    cut_on = k["tejes"] - 0.6 < t < k["hay"] - 0.3
    for j, (lp, hk, st) in enumerate(zip(S["bloops"], S["bhooks"], S["bstubs"])):
        x = CUT.x - 3.5 + 3.5 * j
        tc = k["cortas"] + 0.55 + 0.65 * j
        if cut_on and t < tc:
            lp.location = (x, CUT.y, CUT.z); lp.scale = (1, 1, max(1e-3, seg(t, k["tejes"] + 0.15 * j, k["tejes"] + 0.7 + 0.15 * j)))
            hk.location = LEJOS; st.location = LEJOS
        elif cut_on:
            lp.location = LEJOS
            hk.location = (x + 0.6, CUT.y, CUT.z); st.location = (x - 0.6, CUT.y, CUT.z)
            rot = 0.0
            if j == 1 and k["vuelven"] - 0.2 < t < k["curioso"] + 0.3:
                pr = seg(t, k["vuelven"] - 0.1, k["vuelven"] + 0.35); rel = t - (k["vuelven"] + 0.5)
                rot = 0.55 * pr if rel < 0 else 0.55 * math.exp(-rel * 4) * math.cos(rel * 20)
            if j == 1 and t > k["solo"] + 0.6:
                rot = -0.5 * seg(t, k["solo"] + 0.6, k["solo"] + 1.3) * (1 - seg(t, k["solo"] + 1.6, k["solo"] + 1.9))
            hk.rotation_euler = (0, -rot, 0)
            hard = seg(t, k["duros"], k["duros"] + 0.5)
            col = tuple(mix(a, b, hard) for a, b in zip(LOOP_N, HOOK_N)); set_color(hk, col); set_color(st, col)
        else:
            lp.location = LEJOS; hk.location = LEJOS; st.location = LEJOS
    bl = S["blade"]
    if cut_on and k["cortas"] < t < k["duros"]:
        j = min(2, int((t - k["cortas"]) / 0.65)); u = ((t - k["cortas"]) - 0.65 * j) / 0.65
        bl.location = CUT + Vector((-3.5 + 3.5 * j - 0.6, mix(-2.4, 1.8, ss(min(1, u * 1.3))), 1.15))
    else: bl.location = LEJOS
    fg = S["finger"]
    if cut_on and k["vuelven"] - 0.4 < t < k["vuelven"] + 0.9:
        pr = seg(t, k["vuelven"] - 0.3, k["vuelven"] + 0.35) * (1 - seg(t, k["vuelven"] + 0.45, k["vuelven"] + 0.8))
        fg.location = CUT + Vector((0, 0, 3.15 + 3.0 * (1 - pr)))
    else: fg.location = LEJOS
    # anilla con pesa en un solo gancho
    rg, wt = S["ring"], S["weight"]
    if cut_on and k["curioso"] - 0.2 < t < k["hay"] - 0.3:
        hk = S["bhooks"][1]
        tip = CUT + Vector((0, 0.0, 2.45))
        fall = seg(t, k["solo"] + 1.35, k["solo"] + 2.0)
        drop = 9.0 * fall ** 2 + 0.9 * seg(t, k["solo"] + 0.6, k["solo"] + 1.3)
        ap = seg(t, k["curioso"] - 0.2, k["curioso"] + 0.4)
        rg.location = tip + Vector((0, 0, -0.5 - drop + 4 * (1 - ap))); rg.rotation_euler = (math.pi / 2, 0, math.pi / 2)
        wt.location = rg.location + Vector((0, 0, -0.95))
    else: rg.location = LEJOS; wt.location = LEJOS
    apply_cam(S["cam"], *cam_at(t, k))

def V(tgt, off, lens):
    return (tuple(Vector(tgt) + Vector(off)), tuple(tgt), lens)

def SHOTS(k):
    """planos: cada uno con sus claves; entre planos hay corte (sin interpolar)"""
    D = lambda a, b, h: (a, -b, h)                     # vista en diagonal: se ven ganchos y bucles a la vez
    return [
        (0.0, [(0.0,) + V((-4.0, 0, 0.9), D(2.6, 2.8, 0.9), 32), (1.6,) + V((-1.8, 0, 1.2), D(3.0, 3.4, 1.3), 32),
               (k["vamos"] - 0.4,) + V((1.0, 0, 1.4), D(3.6, 4.6, 2.0), 32), (k["vamos"] + 0.9,) + V((0, -2, -3.0), (44, -32, 22), 34),
               (k["ano"],) + V((0, -2, -3.0), (47, -34, 23), 34)]),
        (k["ano"] - 0.1, [(k["ano"] - 0.1,) + V(DOG + Vector((-2.0, 0, 4.5)), (2.5, -26, 4), 34), (k["cardos"],) + V(DOG + Vector((4.0, 0, 3.8)), (2, -22, 3), 34),
                          (k["micro"],) + V(DOG + Vector((6.8, 0, 2.6)), (1, -11, 1.5), 34)]),
        (k["micro"] + 0.1, [(k["micro"] + 0.1,) + V(MIC, (1.0, -15, 3.0), 34), (k["pin"],) + V(MIC + Vector((0, 0, 1.0)), (0.5, -10.5, 2.0), 34),
                            (k["copiar"],) + V(MIC + Vector((0, 0, 1.0)), (0.5, -9.5, 1.5), 34)]),
        (k["copiar"] - 0.5, [(k["copiar"] - 0.5,) + V((0, 0, 1.6), (5.0, -9.0, 3.2), 30), (k["tira"] + 0.5,) + V((-1, 0, 1.6), D(4.0, 6.0, 2.2), 30),
                             (k["otra"],) + V((0, 0, 1.0), (4.0, -9.0, 3.2), 30), (k["hilos"] + 0.4,) + V((-1.5, 0, 0.5), D(2.6, 3.4, 1.4), 30),
                             (k["apretar"] + 0.2,) + V((-1.0, 0, 0.7), D(2.8, 3.6, 1.0), 30), (k["algodon"] + 0.3,) + V((-0.5, 0, 0.5), D(2.4, 3.2, 0.8), 30),
                             (k["nailon"] + 0.6,) + V((0, 0, 0.7), D(2.8, 3.6, 1.0), 30), (k["tejes"],) + V((0.5, 0, 0.7), D(3.0, 3.8, 1.0), 30)]),
        (k["tejes"] - 0.3, [(k["tejes"] - 0.3,) + V(CUT + Vector((0, 0, 1.5)), (1.5, -13, 2.2), 32), (k["cortas"] + 1.8,) + V(CUT + Vector((0, 0, 1.5)), (1.0, -12, 1.8), 32),
                            (k["vuelven"] - 0.3,) + V(CUT + Vector((0, 0, 2.2)), (1.5, -7.5, 0.8), 32), (k["solo"],) + V(CUT + Vector((0, 0, 1.6)), (1.4, -7.5, 0.4), 32),
                            (k["hay"],) + V(CUT + Vector((0, 0, 1.4)), (1.0, -8.0, 0.6), 32)]),
        (k["hay"] - 0.25, [(k["hay"] - 0.25,) + V((0, 0, 0.8), (0.0, -4.6, 6.8), 32), (k["cuadrado"] + 1.5,) + V((0, 0, 0.8), (0.3, -4.0, 5.8), 32),
                           (k["golpe"] + 0.2,) + V((0, 0, 1.0), (4.5, -8.0, 2.4), 30), (k["borde"],) + V((-2.0, 0, 1.0), D(4.0, 5.5, 1.8), 30),
                           (k["sueltas"],) + V((-2.5, 0, 1.2), D(3.0, 4.0, 1.4), 30), (k["facil"],) + V((0.5, 0, 1.4), D(3.0, 4.2, 1.6), 30),
                           (k["suena"] + 1.0,) + V((3.0, 0, 1.6), D(3.2, 4.6, 2.0), 30), (k["tardo"] + 0.6,) + V((0, -2, -3.0), (42, -30, 21), 34),
                           (k["sig"],) + V((0, -2, -3.0), (46, -33, 23), 34), (DUR + 3,) + V((0, -2, -3.0), (49, -35, 24), 34)])]

def cam_at(t, k):
    sh = SHOTS(k); i = max(j for j, (t0, _) in enumerate(sh) if t >= t0 or j == 0)
    ks = sh[i][1]
    if t > ks[-1][0]: ks = ks + [(t + 1,) + ks[-1][1:]]
    if len(ks) < 2: ks = ks + [(ks[0][0] + 50,) + ks[0][1:]]
    return cam_state(max(t, ks[0][0]), ks, drift=0.02)

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v)
    zh = tape_state(t)[0]
    d = {"eng": [engaged(t) / 1000.0, 0, 0],
         "loops": Pj((-1.5, -1.2, 0.3)), "hooks": Pj((-1.5, -1.2, zh + 0.1)), "tape": Pj((0, 0, zh + 0.2)),
         "dog": Pj(S["dog"].location + Vector((0, 0, 4.5))), "burr": Pj(S["dog"].location + Vector((0.3, -1.1, 2.6))),
         "bloop": Pj(CUT + Vector((3.5, 0, 2.7))), "bhook": Pj(CUT + Vector((0, 0, 2.7))), "blade": Pj(S["blade"].location + Vector((0, 0, 0.8))),
         "ring": Pj(S["ring"].location), "shoe": Pj((0, -3, -3))}
    for i, (x, y) in enumerate(((-1.1, -1.15), (1.1, -1.15), (1.1, 1.15), (-1.1, 1.15))):
        d["sq%d" % i] = Pj((x, y, zh + 0.17))
    for i, (e, _, _) in enumerate(S["cols"]):
        d["c%d" % i] = Pj(e.matrix_world @ Vector((0.11, 0, 0.16))); d["l%d" % i] = [round(col_pose(t, XS[i], zh)[0], 3), 0, 0]
    return d

if __name__ == "__main__":
    run("velcro", build, pose, anchors)
