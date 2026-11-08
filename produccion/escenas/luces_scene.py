# «Así funcionan las luces de Navidad»: primer plano de una guirnalda encendida en la que una bombilla se funde con un
# chispazo y las demás siguen; la guirnalda en serie con flechas de corriente desde el enchufe; si se corta una, se apagan
# todas; dentro de la bombilla (cristal transparente): filamento y, debajo, la derivación con su capa aislante; el
# filamento se rompe, el aislante se quema, la derivación se suelda y la corriente pasa por ella; las demás reciben más
# tensión, brillan más y se funden; diez guirnaldas para enseñar la probabilidad (6 de 10 con 50 bombillas, 2 de 10 con
# 150); al final se cambia la fundida y todo vuelve a la normalidad.
import bpy, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("luces")
BG = (0.09, 0.05, 0.1); WIRE = (0.08, 0.3, 0.14); SOCK = (0.1, 0.38, 0.17); POST = (0.75, 0.68, 0.55); CUR = (1.0, 0.9, 0.2)
COLD = (0.35, 0.35, 0.38); HOT = (1.0, 0.88, 0.5); COAT = (0.55, 0.62, 0.75); BURNT = (0.08, 0.07, 0.07); COPPER = (0.95, 0.55, 0.25)
COLS = [(1.0, 0.25, 0.25), (0.3, 0.95, 0.4), (0.3, 0.6, 1.0), (1.0, 0.82, 0.3), (1.0, 0.55, 0.15), (0.95, 0.35, 0.85), (0.3, 0.95, 0.95), (1.0, 0.92, 0.7)]
LEJOS = (0, 0, -900)
N = 8; SP = 6.0; HERO = 3; WZ = -1.2; RZ = -2.6; FZ = 1.55; SZ = 1.05; PX = 0.22
GX = -140.0                                     # guirnaldas de la probabilidad
FAIL50 = {1: 4, 4: 7, 6: 2, 8: 5}               # fila: bombilla fundida (de 10)
FAIL150 = {0: 12, 3: 25, 5: 8, 9: 17}           # filas que fallan además con 150
RNG = random.Random(5)
def X(i): return SP * i

def set_rgba(o, rgb, a):
    o.active_material.diffuse_color = (*lin(rgb), a)
def blended(o, a):
    m = o.active_material; m.diffuse_color = (*m.diffuse_color[:3], a); m.surface_render_method = 'BLENDED'
def show(o, on):
    o.hide_render = not on
    for c in o.children: show(c, on)
def poly(pts, u):
    P = [Vector(p) for p in pts]; L = [(b - a).length for a, b in zip(P, P[1:])]; s = u * sum(L)
    for a, b, l in zip(P, P[1:], L):
        if s <= l: return a.lerp(b, s / max(l, 1e-6)), (b - a).normalized()
        s -= l
    return P[-1], (P[-1] - P[-2]).normalized()

def helix(x0, x1, r, turns, z, color, bevel=0.016):
    cu = bpy.data.curves.new("hx", 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = bevel; cu.bevel_resolution = 2
    sp = cu.splines.new('POLY'); n = int(turns * 14); sp.points.add(n)
    for k in range(n + 1):
        u = k / n; a = 2 * math.pi * turns * u
        sp.points[k].co = (mix(x0, x1, u), r * math.cos(a), z + r * math.sin(a), 1)
    o = bpy.data.objects.new("hx", cu); bpy.context.collection.objects.link(o)
    o.data.materials.append(mat(color, unique=True)); return o

def build():
    sc, cam = scene_setup(world=BG, shadow=0.3, light_rot=20)
    S = {"cam": cam}
    # fondo: luces desenfocadas
    S["bokeh"] = []
    for k in range(40):
        p = (RNG.uniform(-170, 70), RNG.uniform(30, 70), RNG.uniform(-25, 45))
        o = sph(RNG.uniform(1.2, 2.6), p, RNG.choice(COLS), seg=12, unique=True); blended(o, 0.3); S["bokeh"].append(o)
    # enchufe y cables
    box((2.4, 1.6, 2.8), (-7.2, 0, -1.9), (0.92, 0.92, 0.9))
    for z in (-1.3, -2.5): cyl(0.18, 1.6, (-9.0, 0, z), (0.8, 0.8, 0.82), rot=(0, math.pi / 2, 0), v=10)
    def wire(a, b, sag=0.0):
        a, b = Vector(a), Vector(b); m = (a + b) / 2 - Vector((0, 0, sag))
        for p, q in ((a, m), (m, b)):
            o = bar_obj(WIRE, 0.14); bar_set(o, p, q)
    wire((-6.0, 0, WZ), (X(0) - 0.7, 0, WZ), 0.3)
    for i in range(N - 1): wire((X(i) + 0.7, 0, WZ), (X(i + 1) - 0.7, 0, WZ), 0.5)
    wire((X(N - 1) + 0.7, 0, WZ), (X(N - 1) + 1.6, 0, RZ), 0); wire((X(N - 1) + 1.6, 0, RZ), (-6.0, 0, RZ), 0.6)
    # bombillas
    S["b"] = []
    for i in range(N):
        e = empty((X(i), 0, 0)); B = {"e": e}
        cyl(0.7, 1.8, (0, 0, -0.9), SOCK, parent=e); cyl(0.78, 0.3, (0, 0, -0.1), (0.08, 0.3, 0.13), parent=e)
        for sx in (-1, 1):
            o = bar_obj(POST, 0.035, parent=e); bar_set(o, (sx * PX, 0, -0.2), (sx * PX, 0, FZ)); o.location = (sx * PX, 0, -0.2)
        B["bead"] = sph(0.13, (0, 0, 0.45), (0.95, 0.95, 1.0), parent=e, scale=(1.5, 1, 1))
        if i == HERO:
            S["pivL"] = empty((-PX, 0, FZ), parent=e); S["pivR"] = empty((PX, 0, FZ), parent=e)
            hl = helix(-PX, 0, 0.045, 5, FZ, COLD, 0.012); hl.parent = S["pivL"]; hl.location = (PX, 0, -FZ)
            hr = helix(0, PX, 0.045, 5, FZ, COLD, 0.012); hr.parent = S["pivR"]; hr.location = (-PX, 0, -FZ)
            B["fil"] = [hl, hr]
            S["shunt"] = helix(-PX - 0.03, PX + 0.03, 0.05, 6, SZ, (0.6, 0.6, 0.62), 0.014); S["shunt"].parent = e
            S["coat"] = cyl(0.1, 2 * PX + 0.12, (0, 0, SZ), COAT, parent=e, rot=(0, math.pi / 2, 0), v=16, unique=True); blended(S["coat"], 0.75)
        else:
            o = bar_obj(COLD, 0.045, parent=e, unique=True); bar_set(o, (-PX, 0, FZ), (PX, 0, FZ)); o.location = (-PX, 0, FZ); B["fil"] = [o]
        B["core"] = sph(0.3, (0, 0, FZ), HOT, parent=e, seg=12, unique=True)
        g1 = cyl(0.56, 2.0, (0, 0, 1.0), COLS[i], parent=e, unique=True); blended(g1, 0.5)
        g2 = sph(0.56, (0, 0, 2.0), COLS[i], parent=e, scale=(1, 1, 1.35), unique=True); blended(g2, 0.5)
        B["glass"] = [g1, g2]
        B["halo"] = sph(1.0, (0, 0, 1.4), COLS[i], parent=e, seg=16, unique=True); blended(B["halo"], 0.14)
        S["b"].append(B)
    # flechas de corriente
    S["flechas"] = []
    for k in range(110):
        bpy.ops.mesh.primitive_cone_add(radius1=0.22, radius2=0, depth=0.55, location=LEJOS, vertices=10)
        S["flechas"].append(setup(bpy.context.object, CUR))
    # chispas
    S["chispas"] = [sph(0.09, LEJOS, (1, 0.95, 0.6), seg=8) for _ in range(16)]
    S["flash"] = sph(1, LEJOS, (1, 0.95, 0.75), seg=16, unique=True); blended(S["flash"], 0.55)
    # guirnaldas de la probabilidad
    S["filas"] = []
    for r in range(10):
        z = 3.6 * (9 - r)
        o = bar_obj(WIRE, 0.12); bar_set(o, (GX + 2.5, 0, z - 0.6), (GX + 34.5, 0, z - 0.6))
        bulbs = [sph(0.55, LEJOS, COLS[(j + r) % 8], seg=10, unique=True) for j in range(30)]
        mk = sph(0.9, (GX + 37.5, 0, z), (0.3, 0.9, 0.4), seg=14, unique=True)
        S["filas"].append((bulbs, mk))
    dyn = [cam, S["bokeh"], [B["e"] for B in S["b"]], S["flechas"], S["chispas"], S["flash"], [f[0] for f in S["filas"]], [f[1] for f in S["filas"]]]
    join_static(dyn)
    return sc, S

# ---------------------------------------------------------------------------------------------------
def TB(): return T("se rompe", 2) + 0.15           # se rompe el filamento de la bombilla protagonista
def pops():
    return [(0.55, HERO), (T("y se funden") + 0.1, 6), (T("una avería") + 0.1, 1)]
def replace_t(i):
    a = T("cambiar") - 0.1
    return {HERO: a, 6: a + 0.7, 1: a + 1.4}[i]

def dead(t, i):
    """la bombilla i está fundida (pero con la derivación soldada)"""
    if i == HERO:
        if 0.55 < t < T("mira por") + 0.3: return True
        if t > TB() and t < replace_t(HERO) + 0.5: return True
        return False
    for tp, k in pops()[1:]:
        if k == i and tp < t < replace_t(i) + 0.5: return True
    return False

def string_on(t):
    if T("y se apagan") - 0.05 < t < T("así que dentro") - 0.3: return False
    if TB() < t < T("se suelda") + 0.45: return False
    return True

def boost(t):
    n = sum(1 for i in range(N) if dead(t, i)) if t > T("cada bombilla que") else 0
    return 1 + 0.6 * seg(t, T("así que las demás"), T("y brillan", fin=True)) * min(n, 3) / 3

def path(t):
    pts = [(-6.0, 0, WZ)]
    for i in range(N):
        z = SZ if (dead(t, i) and t > T("la corriente pasa") - 0.5) else FZ
        pts += [(X(i) - 0.7, 0, WZ), (X(i) - PX, 0, -0.1), (X(i) - PX, 0, z), (X(i) + PX, 0, z), (X(i) + PX, 0, -0.1), (X(i) + 0.7, 0, WZ)]
    pts += [(X(N - 1) + 1.6, 0, RZ), (-6.0, 0, RZ)]
    return pts

def flow_on(t):
    return (T("la corriente entra") - 0.3 < t < T("y se apagan")) or (T("mientras") - 0.2 < t < TB()) or \
           (T("la corriente pasa") - 0.3 < t < T("noventa") - 0.5) or (T("cambiar") + 1.6 < t)

def flow_off(t):
    """avance acumulado de la corriente (se para cuando se corta el camino)"""
    tf = T("el camino") + 0.2
    if T("si se rompe") < t < T("así que dentro"): t = min(t, tf)
    return t * 0.045

def spark(S, t, t0, p, slot=0):
    u = (t - t0) / 0.45
    if not (0 <= u <= 1): return False
    for k, o in enumerate(S["chispas"]):
        a = k * 2.4 + slot; e = 0.35 + (k % 4) * 0.25
        d = Vector((math.cos(a) * 0.8, -0.5 + 0.3 * math.sin(a * 1.7), math.sin(a) * 0.8 + 0.4)).normalized()
        o.location = Vector(p) + d * e * 2.2 * u + Vector((0, 0, -1.2 * u * u)); s = 1.6 * (1 - u) + 0.01; o.scale = (s, s, s)
    S["flash"].location = p; f = 1.4 * math.sin(math.pi * min(1, u * 1.5)) + 0.01; S["flash"].scale = (f, f, f)
    return True

def pose(t, S):
    on = string_on(t); bo = boost(t); t_in = T("así que dentro") - 0.4; t_out = T("y aquí")
    close = t_in < t < t_out
    for i, B in enumerate(S["b"]):
        lit = on and not dead(t, i)
        if i == 5 and T("si se rompe") + 0.3 < t < T("así que dentro") - 0.3: lit = False
        e = B["e"]
        # cambio de la fundida: sale y entra otra nueva
        rt = replace_t(i) if i in (HERO, 6, 1) else None
        dz = 0.0
        if rt and rt - 0.1 < t < rt + 1.0: dz = 6 * math.sin(math.pi * seg(t, rt - 0.1, rt + 0.9))
        e.location = (X(i), 0, dz)
        c = COLS[i]
        tw = 0.9 + 0.1 * math.sin(t * 5 + i * 1.7)
        if lit:
            gc = tuple(min(1, v * (0.85 + 0.15 * bo)) for v in c)
            a = 0.5
            if i == HERO and close: gc = tuple(mix(v, 1, 0.5) for v in c); a = 0.12
            for g in B["glass"]: set_rgba(g, gc, a)
            set_rgba(B["core"], HOT, 1); s = 0.3 * bo * tw; B["core"].scale = (s / 0.3,) * 3
            B["core"].hide_render = (i == HERO and close)
            B["halo"].hide_render = (i == HERO and close); hs = 1.6 * bo * tw; B["halo"].scale = (hs, hs, hs)
            set_rgba(B["halo"], c, 0.13 + 0.05 * (bo - 1))
            for f in B["fil"]: set_color(f, HOT)
        else:
            dc = tuple(v * 0.3 for v in c); a = 0.55
            if i == HERO and close: dc = tuple(mix(v, 1, 0.5) for v in c); a = 0.12
            for g in B["glass"]: set_rgba(g, dc, a)
            B["core"].hide_render = True; B["halo"].hide_render = True
            for f in B["fil"]: set_color(f, COLD)
        if i == 5:   # filamento roto en la demostración «si se rompe una»
            br = T("si se rompe") + 0.3 < t < T("así que dentro") - 0.3
            B["fil"][0].hide_render = br
    # filamento protagonista: se rompe y cae
    tb = TB(); r = seg(t, tb, tb + 0.5) if (tb < t < replace_t(HERO) + 0.5) else 0.0
    if 0.55 < t < T("mira por") + 0.3: r = 1.0
    S["pivL"].rotation_euler = (0, 1.1 * r, 0); S["pivR"].rotation_euler = (0, -1.1 * r, 0)
    hfil = S["b"][HERO]["fil"]
    if close and on and not dead(t, HERO):
        for f in hfil: set_color(f, HOT)
    # aislante y soldadura
    t_q, t_s = T("el aislante"), T("se suelda")
    burnt = seg(t, t_q, t_q + 0.6)
    gone = seg(t, t_q + 0.7, t_s) if t < replace_t(HERO) + 0.4 else 0.0
    set_rgba(S["coat"], tuple(mix(a, b, burnt if t < replace_t(HERO) + 0.4 else 0) for a, b in zip(COAT, BURNT)), 0.75 * (1 - gone))
    S["coat"].hide_render = gone > 0.97
    sh = seg(t, t_s, t_s + 0.4) if t < replace_t(HERO) + 0.4 else 0.0
    glow = win01(t, t_s, t_s + 1.6, 0.2, 0.8)
    set_color(S["shunt"], tuple(mix(mix(0.6, b, sh), w, glow) for b, w in zip(COPPER, (1, 0.95, 0.6))))
    # chispas
    S["flash"].location = LEJOS
    for o in S["chispas"]: o.location = LEJOS
    hero_p = Vector((X(HERO), -0.2, FZ))
    for t0, p, sl in ((0.55, Vector((X(HERO), -0.2, 1.6)), 0), (tb, hero_p, 1), (t_q, Vector((X(HERO), -0.2, SZ)), 2), (t_s, Vector((X(HERO), -0.2, SZ)), 3),
                      (pops()[1][0], Vector((X(6), -0.2, 1.6)), 4), (pops()[2][0], Vector((X(1), -0.2, 1.6)), 5)):
        if spark(S, t, t0, p, sl): break
    if close:
        S["flash"].scale = tuple(v * 0.35 for v in S["flash"].scale)
        for o in S["chispas"]: o.scale = tuple(v * 0.4 for v in o.scale)
    # flechas de corriente
    fo = flow_on(t); P = path(t); off = flow_off(t)
    vis = T("si se rompe") < t < T("y se apagan")
    if close:
        H = X(HERO); zz = SZ if t > T("la corriente pasa") - 0.5 else FZ
        P = [(H - 1.8, 0, WZ), (H - 0.7, 0, WZ), (H - PX, 0, -0.1), (H - PX, 0, zz), (H + PX, 0, zz), (H + PX, 0, -0.1), (H + 0.7, 0, WZ), (H + 1.8, 0, WZ)]
    for k, o in enumerate(S["flechas"]):
        if not fo or (close and k >= 22): o.location = LEJOS; continue
        u = ((t * 0.22 + k / 22) % 1) if close else (off + k / len(S["flechas"])) % 1
        p, d = poly(P, u)
        o.location = p + Vector((0, -0.05, 0)); o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d)
        s = 0.24 if close else 1.0
        if T("el camino") + 0.2 < t < T("así que dentro"): s *= 1 - seg(t, T("el camino") + 0.4, T("y se apagan"))
        o.scale = (s, s, s)
    # fondo
    for k, o in enumerate(S["bokeh"]):
        s = 1 + 0.15 * math.sin(t * 0.9 + k); o.scale = (s, s, s)
    # guirnaldas de probabilidad
    g0, g1 = T("una guirnalda de"), T("con ciento")
    f50 = T("seis") - 0.2; f150 = T("dos de cada") - 0.3
    for r, (bulbs, mk) in enumerate(S["filas"]):
        z = 3.6 * (9 - r); gs = T("si cada") + 0.4; app = seg(t, gs + 0.25 * r, gs + 0.35 + 0.25 * r)
        n = 10 if t < g1 + 0.2 else 30
        cm = seg(t, g1 + 0.2, g1 + 0.9)
        for j, o in enumerate(bulbs):
            if j >= n and cm < 0.01: o.location = LEJOS; continue
            if n == 10: x = GX + 4 + 3.0 * j
            else:
                x0 = GX + 4 + 3.0 * (j // 3) if j % 3 == 0 else None
                x = mix(GX + 4 + 3.0 * (j // 3), GX + 4 + 0.95 * j, cm)
            o.location = (x, 0, z + 0.15 * math.sin(t * 2 + j * 0.5 + r))
            rr = mix(0.55, 0.42, cm) * max(app, 0.001); o.scale = (rr / 0.55,) * 3
            bad = False
            if r in FAIL50 and t > f50 + 0.1 * r and ((n == 10 and j == FAIL50[r]) or (n == 30 and j == FAIL50[r] * 3)): bad = True
            if r in FAIL150 and t > f150 + 0.1 * r and n == 30 and j == FAIL150[r]: bad = True
            c = COLS[(j + r) % 8]
            set_color(o, tuple(v * 0.22 for v in c) if bad else tuple(min(1, v * (0.9 + 0.1 * math.sin(t * 4 + j))) for v in c))
        fail = (r in FAIL50 and t > f50 + 0.1 * r) or (r in FAIL150 and t > f150 + 0.1 * r)
        ok_vis = t > f50 - 0.1
        mk.scale = (max(app * (1 if ok_vis else 0.001), 0.001),) * 3
        set_color(mk, (0.95, 0.25, 0.25) if fail else (0.3, 0.9, 0.4))
    apply_cam(S["cam"], *cam_state(t, CAM(), drift=0.12))

# ---------------------------------------------------------------------------------------------------
def VD(at, dist, yaw, pitch, lens=40):
    at = Vector(at); y, p = math.radians(yaw), math.radians(pitch)
    return (tuple(at + dist * Vector((math.sin(y) * math.cos(p), -math.cos(y) * math.cos(p), math.sin(p)))), tuple(at), lens)

def CAM():
    k = []
    def add(t, v): k.append((t,) + v)
    H = X(HERO); G = (GX + 23.5, 0, 22.5)
    add(0.0, VD((H + 3, 0, 1.0), 22, -52, 13, 40))
    add(T("alguna bombilla"), VD((H + 0.5, 0, 1.2), 16, -24, 11, 40))
    add(T("por qué"), VD((H + 2, 0, 1.0), 24, -32, 14, 40))
    add(T("mira por") + 0.2, VD((H, 0, 1.3), 12, -20, 8, 42))
    add(T("van en fila") + 0.3, VD((20, 0, 0.5), 38, -62, 15, 40))
    add(T("la corriente entra"), VD((19, 0, 0.5), 37, -55, 13, 40))
    add(T("sale por"), VD((22, 0, 0), 38, -60, 14, 40))
    add(T("si se rompe") + 0.4, VD((X(5), 0, 0.6), 24, -38, 12, 40))
    add(T("y se apagan") + 0.4, VD((21, 0, 0.5), 37, -50, 15, 40))
    add(T("así que dentro") + 0.6, VD((H, 0, 1.3), 10, -15, 6, 45))
    add(T("un alambre"), VD((H, 0, 1.25), 6.0, -10, 4, 50))
    add(T("derivación"), VD((H, 0, 1.15), 5.6, 10, 3, 50))
    add(T("mientras") + 0.4, VD((H, 0, 1.25), 6.6, 16, 5, 50))
    add(T("pero si el"), VD((H, 0, 1.3), 5.8, -6, 4, 50))
    add(T("toda la tensión") + 0.5, VD((H, 0, 1.2), 6.4, -14, 5, 50))
    add(T("el aislante"), VD((H, 0, 1.05), 4.8, 8, 3, 50))
    add(T("se suelda") + 0.4, VD((H, 0, 1.05), 5.0, -6, 3, 50))
    add(T("la corriente pasa") + 0.6, VD((H, 0, 0.9), 16, -28, 10, 40))
    add(T("y aquí") + 0.5, VD((20, 0, 0.5), 38, -62, 15, 40))
    add(T("así que las demás"), VD((21, 0, 0.5), 36, -54, 13, 40))
    add(T("una avería") + 0.4, VD((21, 0, 0.5), 38, -60, 15, 40))
    add(T("noventa") + 0.3, VD(G, 84, -8, 4, 40))
    add(T("con ciento"), VD(G, 82, 6, 4, 40))
    add(T("dos de cada") + 1.0, VD(G, 84, -2, 4, 40))
    add(T("por eso") + 0.6, VD((21, 0, 0), 40, -50, 14, 40))
    add(DUR, VD((21, 0, 0), 52, -44, 17, 40))
    add(DUR + 3, VD((21, 0, 0), 54, -42, 17, 40))
    return k

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v); H = X(HERO)
    return {"hero": Pj((H, 0, 2.6)), "fil": Pj((H, 0, FZ + 0.1)), "shunt": Pj((H + 0.05, 0, SZ - 0.05)),
            "postL": Pj((H - PX, 0, 0.2)), "postR": Pj((H + PX, 0, 0.2)), "enchufe": Pj((-7.2, 0, -0.2)),
            "b5": Pj((X(5), 0, 2.6)), "b0": Pj((X(0), 0, 2.8)), "b7": Pj((X(7), 0, 2.8)), "grid": Pj((GX + 19.5, 0, 34)),
            "b6": Pj((X(6), 0, 2.8)), "b1": Pj((X(1), 0, 2.8))}

if __name__ == "__main__":
    run("luces", build, pose, anchors)
