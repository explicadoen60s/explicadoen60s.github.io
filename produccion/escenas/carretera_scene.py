# «¿Y si construyes una carretera?»: la rueda de un camión de 44 t pasa en primer plano y bajamos a la carretera en
# sección. Se quita la tierra blanda; la de debajo se aplasta con el peso, así que se compacta con un rodillo que vibra;
# el asfalto sobre tierra se agrieta, así que van dos capas de zahorra de 25 cm; tres capas de asfalto (base, intermedia y
# rodadura de 3 cm, unos 30 cm en total); si es plana el agua se queda, así que lleva bombeo del 2 % a cada lado, cunetas y
# tubos. El agua entra por una grieta, se congela, crece un 9 %, rompe y un camión arranca el trozo: un bache.
import bpy, bmesh, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector

T0, DUR = cargar("carretera")
_TC = {}
def T(k, n=1, fin=False):
    key = (k, n, fin)
    if key not in _TC: _TC[key] = T0(k, n, fin)
    return _TC[key]

BG = (0.07, 0.09, 0.13); SUB = (0.38, 0.27, 0.18); SUB_C = (0.28, 0.2, 0.14); SOFT = (0.6, 0.45, 0.3); GRASS = (0.25, 0.45, 0.25)
ZAH1 = (0.62, 0.6, 0.55); ZAH2 = (0.7, 0.68, 0.62); STONE = (0.5, 0.49, 0.46); AB = (0.2, 0.2, 0.22); AI = (0.26, 0.26, 0.28); AR = (0.14, 0.14, 0.16)
LINE = (0.92, 0.92, 0.88); WATER = (0.3, 0.6, 0.95); ICE = (0.85, 0.95, 1.0); PIPE = (0.55, 0.57, 0.6); TRUCK = (0.85, 0.3, 0.25)
TYRE = (0.08, 0.08, 0.09); RIM = (0.65, 0.67, 0.7); ROLL = (0.95, 0.75, 0.15); RED = (0.92, 0.22, 0.2); DARK = (0.05, 0.05, 0.06)
LEJOS = Vector((0, 300, -300))
WR = 4.6; L = 6.0                       # medio ancho de la calzada y medio largo del tramo
ZS = -1.56                              # techo de la explanada
ZZ1, ZZ2 = ZS + 0.5, ZS + 1.0           # techos de las dos capas de zahorra
HB, HI, HR = 0.3, 0.2, 0.06             # capas de asfalto (escala vertical ×2)
SLOPE = 0.045
CX = 1.6                                # posición de la grieta
rng = random.Random(6)
STONES = [(rng.uniform(-WR + 0.1, WR - 0.1), rng.uniform(0.05, 0.45), rng.uniform(0.03, 0.08), rng.randint(0, 1)) for _ in range(70)]
DROPS = [(rng.uniform(-3.5, 3.5), rng.uniform(-L + 0.3, 1.0), rng.uniform(0, 1)) for _ in range(22)]

def prism(color, unique=True):
    me = bpy.data.meshes.new("pr"); bm = bmesh.new()
    vs = [bm.verts.new((0, 0, 0)) for _ in range(12)]
    # índices: extremo e (0 delante, 1 detrás) * 6 + [b(-W), b(0), b(W), t(W), t(0), t(-W)]
    f = bm.faces.new([vs[i] for i in range(6)]); g = bm.faces.new([vs[6 + i] for i in reversed(range(6))])
    for i in range(6):
        j = (i + 1) % 6; bm.faces.new((vs[j], vs[i], vs[6 + i], vs[6 + j]))
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("pr", me); bpy.context.collection.objects.link(o); return setup(o, color, unique=unique)

def set_prism(o, xs, zb, zt, y0=-L, y1=L):
    me = o.data
    for e, y in enumerate((y0, y1)):
        pts = [(xs[0], zb[0]), (xs[1], zb[1]), (xs[2], zb[2]), (xs[2], zt[2]), (xs[1], zt[1]), (xs[0], zt[0])]
        for i, (x, z) in enumerate(pts): me.vertices[e * 6 + i].co = (x, y, z)
    me.update()

def car_truck():
    e = empty(LEJOS); wheels = []
    box((2.5, 2.2, 2.6), (0, 3.2, 2.2), TRUCK, e); box((2.3, 0.1, 1.0), (0, 4.31, 2.8), (0.15, 0.2, 0.28), e)
    box((2.5, 7.5, 2.9), (0, -2.2, 2.45), (0.85, 0.86, 0.9), e)
    for y in (3.3, -0.5, -1.8, -4.6, -5.6):
        for x in (-1.1, 1.1):
            w = empty((x, y, 0.55), e)
            cyl(0.55, 0.4, (0, 0, 0), TYRE, w, rot=(0, math.pi / 2, 0)); cyl(0.3, 0.42, (0, 0, 0), RIM, w, rot=(0, math.pi / 2, 0))
            for k in range(5): box((0.44, 0.06, 0.12), (0, 0.18 * math.cos(k * 1.26), 0.18 * math.sin(k * 1.26)), (0.4, 0.42, 0.45), w)
            wheels.append(w)
    return e, wheels

def build():
    sc, cam = scene_setup(world=BG, shadow=0.3); cam.data.clip_start = 0.02
    S = {"cam": cam}
    # explanada y arcenes (estático)
    S["sub"] = box((16, 2 * L, 3.0), (0, 0, ZS - 1.5), SUB, unique=True)
    for sx in (-1, 1):
        sh = prism(SOFT, unique=False)
        set_prism(sh, (sx * WR, sx * 5.2, sx * 8.0), (ZS, ZS, ZS), (0.0, -0.75, 0.05) if True else None)
        if sx < 0:
            set_prism(sh, (-8.0, -5.2, -WR), (ZS, ZS, ZS), (0.05, -0.75, 0.0))
        box((3.0, 2 * L, 0.04), (sx * 6.8, 0, 0.06), GRASS)
    S["pipes"] = [cyl(0.18, 2 * L, (sx * 5.2, 0, -1.05), PIPE, rot=(math.pi / 2, 0, 0)) for sx in (-1, 1)]
    for sx in (-1, 1): cyl(0.12, 2 * L + 0.02, (sx * 5.2, 0, -1.05), DARK, rot=(math.pi / 2, 0, 0))
    # tierra blanda (se quita), capas
    S["soft"] = box((2 * WR, 2 * L, -ZS), (0, 0, ZS / 2), SOFT, unique=True)
    S["z1"] = box((2 * WR, 2 * L, 0.5), LEJOS, ZAH1); S["z2"] = box((2 * WR, 2 * L, 0.5), LEJOS, ZAH2)
    S["st1"] = []; S["st2"] = []
    for x, z, r, k in STONES:
        S["st1" if k == 0 else "st2"].append(sph(r, LEJOS, STONE))
    S["ab"] = prism(AB); S["ai"] = prism(AI); S["ar"] = prism(AR)
    S["bad"] = box((2 * WR, 2 * L, 0.12), LEJOS, AR)
    S["bcr"] = [bar_obj((0.5, 0.5, 0.55), r=0.025) for _ in range(8)]
    S["lines"] = [box((0.15, 2 * L, 0.01), LEJOS, LINE) for _ in range(3)]
    # peso, rodillo, camión
    S["weight"] = box((2.0, 2.0, 1.0), LEJOS, (0.55, 0.57, 0.62))
    rol = empty(LEJOS); S["rol"] = rol
    S["drum"] = cyl(0.75, 2.0, (0, 0, 0.75), (0.6, 0.62, 0.66), rol, rot=(0, math.pi / 2, 0))
    box((2.4, 2.0, 1.2), (0, 1.8, 1.4), ROLL, rol); box((1.3, 1.2, 1.0), (0, 2.0, 2.5), (0.2, 0.3, 0.4), rol)
    S["truck"], S["wheels"] = car_truck()
    # agua, grieta, hielo, bache
    S["puddle"] = box((1, 1, 1), LEJOS, WATER)
    S["drops"] = [sph(0.09, LEJOS, WATER) for _ in DROPS]
    S["crack"] = prism(DARK); S["cw"] = prism(WATER)
    S["chunk"] = box((0.7, 0.9, HR + HI * 0.5), LEJOS, AR)
    S["hole"] = box((0.7, 0.9, 0.02), LEJOS, (0.45, 0.4, 0.33))
    S["holes"] = [sph(0.4, LEJOS, (0.45, 0.4, 0.33), scale=(1.2, 1.0, 0.03)) for _ in range(6)]
    S["arr"] = [(bar_obj(RED, r=0.04), sph(0.08, LEJOS, RED)) for _ in range(2)]
    join_static([cam, S["sub"], S["soft"], S["z1"], S["z2"], S["st1"], S["st2"], S["ab"], S["ai"], S["ar"], S["bad"], S["bcr"], S["lines"],
                 S["weight"], rol, S["truck"], S["puddle"], S["drops"], S["crack"], S["cw"], S["chunk"], S["hole"], S["holes"], S["arr"]])
    return sc, S

def hide_bar(o): bar_set(o, LEJOS, LEJOS + Vector((0, 0, 0.001)))

def crown(t):
    if t < T("vamos a construir"): return 1.0
    return seg(t, T("así que le das"), T("de tejado", fin=True))

def surf(x, c, zbase):
    return zbase + c * SLOPE * (WR - abs(x))

def pose(t, S):
    built = t < T("vamos a construir")
    c = crown(t)
    # tierra blanda
    if built: S["soft"].location = LEJOS
    else:
        up = seg(t, T("primero quitas"), T("tierra blanda", fin=True))
        S["soft"].location = Vector((0, 0, ZS / 2 + 4 * up)) if up < 0.99 else LEJOS
    # explanada: se aplasta y se compacta
    dent = seg(t, T("se aplasta"), T("el peso", fin=True)) * (1 - seg(t, T("así que la compactas"), T("así que la compactas") + 0.6))
    comp = seg(t, T("con rodillos"), T("como una piedra", fin=True)) if not built else 1.0
    set_color(S["sub"], tuple(mix(SUB[i], SUB_C[i], comp) for i in range(3)))
    if T("pero la tierra") <= t < T("así que la compactas") + 0.6:
        S["weight"].location = Vector((-1.5, -L + 1.2, ZS + 0.5 - 0.35 * dent - 3.0 * (1 - seg(t, T("pero la tierra"), T("se aplasta")))))
    else: S["weight"].location = LEJOS
    S["sub"].location = Vector((0, 0, ZS - 1.5))
    # rodillo que vibra
    if T("así que la compactas") <= t < T("pero si echas"):
        u = seg(t, T("así que la compactas"), T("como una piedra", fin=True)); x = -3.6 + 7.2 * u
        vib = 0.03 * math.sin(t * 60)
        S["rol"].location = Vector((x, -L + 1.3, ZS + vib)); S["rol"].rotation_euler = (0, 0, math.pi / 2)
        S["drum"].rotation_euler = (x * 1.3, math.pi / 2, 0)
    else: S["rol"].location = LEJOS
    # asfalto malo (sin zahorra) que se agrieta
    if T("pero si echas") <= t < T("así que pones"):
        S["bad"].location = Vector((0, 0, ZS + 0.06))
        for k, b in enumerate(S["bcr"]):
            u = seg(t, T("se agrieta") - 0.1 + 0.04 * k, T("se agrieta", fin=True) + 0.1)
            if u > 0.01:
                p0 = Vector((-3.5 + k, -L - 0.01, ZS + 0.12)); bar_set(b, p0, p0 + Vector((0.3 * math.sin(k * 2), 0, -0.12 * u)))
            else: hide_bar(b)
    else:
        S["bad"].location = LEJOS
        for b in S["bcr"]: hide_bar(b)
    # zahorra
    z1 = 1.0 if built else seg(t, T("piedra machacada") - 0.5, T("una capa de") + 0.8)
    z2 = 1.0 if built else seg(t, T("y otra más") - 0.3, T("y otra más") + 0.5)
    S["z1"].location = Vector((0, 0, ZS + 0.25 + 3 * (1 - z1))) if z1 > 0.01 else LEJOS
    S["z2"].location = Vector((0, 0, ZZ1 + 0.25 + 3 * (1 - z2))) if z2 > 0.01 else LEJOS
    for lst, base, on in ((S["st1"], ZS, z1), (S["st2"], ZZ1, z2)):
        st = [s for s in STONES if s[3] == (0 if lst is S["st1"] else 1)]
        for o, (x, z, r, k) in zip(lst, st):
            o.location = Vector((x, -L - 0.01, base + z + 3 * (1 - on))) if on > 0.01 else LEJOS
    # asfalto (tres capas, con bombeo)
    xs = (-WR, 0.0, WR)
    def lay(o, on, zb0, h, crown_bottom):
        if on < 0.01: o.location = LEJOS; return
        o.location = Vector((0, 0, 3 * (1 - on)))
        zb = [surf(x, c, zb0) if crown_bottom else zb0 for x in xs]; zt = [surf(x, c, zb0 + h) for x in xs]
        set_prism(o, xs, zb, zt)
    ab = 1.0 if built else seg(t, T("una gruesa") - 0.2, T("de base", fin=True))
    ai = 1.0 if built else seg(t, T("una intermedia") - 0.2, T("intermedia", fin=True))
    ar = 1.0 if built else seg(t, T("la de rodadura") - 0.2, T("rodadura", fin=True))
    lay(S["ab"], ab, ZZ2, HB, False); lay(S["ai"], ai, ZZ2 + HB, HI, True); lay(S["ar"], ar, ZZ2 + HB + HI, HR, True)
    ztop = ZZ2 + HB + HI + HR
    for k, ln in enumerate(S["lines"]):
        x = (0.0, -WR + 0.35, WR - 0.35)[k]
        if ar > 0.99: ln.location = Vector((x, 0, surf(x, c, ztop) + 0.004)); ln.rotation_euler = (0, (0 if k == 0 else (1 if k == 1 else -1)) * -c * SLOPE, 0)
        else: ln.location = LEJOS
        if k == 0 and ar > 0.99: ln.scale = (0.15, 2 * L, 0.01)
    # agua en la calzada plana / que escurre
    a0, a1 = T("si la carretera"), T("y aquí viene")
    if a0 <= t < T("así que le das") + 0.6:
        f = seg(t, T("el agua se queda") - 0.3, T("encima", 2, fin=True)) * (1 - seg(t, T("así que le das"), T("así que le das") + 0.6))
        S["puddle"].location = Vector((0, -L / 2, ztop + 0.01)); S["puddle"].scale = (6.5 * f + 0.01, 0.6 * L * f + 0.01, 0.015)
    else: S["puddle"].location = LEJOS
    for k, (d, (x0, y, ph)) in enumerate(zip(S["drops"], DROPS)):
        if T("así que le das") <= t < a1:
            u = ((t - T("así que le das")) * 0.45 + ph) % 1.0; sx = 1 if x0 >= 0 else -1
            if u < 0.6:
                x = x0 + (sx * WR - x0) * (u / 0.6) * c; z = surf(x, c, ztop) + 0.07
            else:
                w = (u - 0.6) / 0.4; x = sx * (WR + 0.6 * w); z = surf(sx * WR, c, ztop) + 0.07 - 0.8 * w
            d.location = Vector((x, y, z))
        else: d.location = LEJOS
    # grieta, agua, hielo, bache
    a0 = T("se cuela")
    zc = surf(CX, c, ztop)
    if a0 <= t < T("y arranca") + 0.3:
        grow = 1 + 1.5 * seg(t, T("empuja"), T("la grieta crece", fin=True))
        w = 0.06 * grow; d = (HR + HI * 0.6) * min(1.0, 0.7 + 0.3 * grow / 2.5)
        set_prism(S["crack"], (CX - w, CX, CX + w), (zc - 0.001, zc - d, zc - 0.001), (zc + 0.002, zc + 0.002, zc + 0.002), -L - 0.003, -L + 0.9)
        S["crack"].location = Vector((0, 0, 0))
        fill = seg(t, a0, T("diminuta", fin=True))
        if fill > 0.01:
            dd = d * fill
            set_prism(S["cw"], (CX - w * 0.8, CX, CX + w * 0.8), (zc - dd * 0.2, zc - d * 0.95, zc - dd * 0.2), (zc, zc, zc), -L - 0.006, -L + 0.85)
            S["cw"].location = Vector((0, 0, 0))
            frz = seg(t, T("se congela"), T("se congela", fin=True) + 0.3)
            set_color(S["cw"], tuple(mix(WATER[i], ICE[i], frz) for i in range(3)))
        else: S["cw"].location = LEJOS
    else: S["crack"].location = LEJOS; S["cw"].location = LEJOS
    for k, (b, tip) in enumerate(S["arr"]):
        if T("empuja") <= t < T("luego pasa"):
            sx = -1 if k == 0 else 1; p0 = Vector((CX, -L - 0.05, zc - 0.06)); p1 = p0 + Vector((sx * (0.1 + 0.25 * seg(t, T("empuja"), T("rompe", fin=True))), 0, 0))
            bar_set(b, p0, p1); tip.location = p1
        else: hide_bar(b); tip.location = LEJOS
    arr = seg(t, T("y arranca"), T("el trozo", fin=True))
    if T("luego pasa") <= t:
        S["hole"].location = Vector((CX, -L + 0.45, zc - 0.005)) if arr > 0.05 else LEJOS
        if arr < 0.999 and t < T("así nace") + 0.6:
            S["chunk"].location = Vector((CX, -L + 0.45, zc - (HR + HI * 0.5) / 2 + 1.2 * arr)) + Vector((0, -2.0 * arr, 0)); S["chunk"].rotation_euler = (2.5 * arr, 0.6 * arr, 0)
        else: S["chunk"].location = LEJOS
    else: S["hole"].location = LEJOS; S["chunk"].location = LEJOS
    for k, ho in enumerate(S["holes"]):
        if t >= T("por eso hay"):
            ap = seg(t, T("por eso hay") + 0.2 * k, T("por eso hay") + 0.2 * k + 0.3)
            x = (-3.0, -1.2, 2.8, -2.2, 0.8, 3.4)[k]; y = (-3.5, 1.5, 2.5, -0.5, 4.0, -1.0)[k]
            ho.location = Vector((x, y, surf(x, c, ztop) + 0.002)); ho.scale = (1.2 * ap + 0.001, ap + 0.001, 0.03)
        else: ho.location = LEJOS
    # camión
    tr = None
    if t < T("vamos a construir"): tr = (-14 + 16 * t / T("vamos a construir"), 2.0)
    elif T("luego pasa") - 0.4 <= t < T("así nace") + 1.0: tr = (-16 + 11 * seg(t, T("luego pasa") - 0.4, T("el trozo", fin=True) + 0.4) * 1.0 + 0.0, CX)
    if tr:
        y, x = tr; S["truck"].location = Vector((x, y, surf(x, c, ztop)))
        for w in S["wheels"]: w.rotation_euler = (-y / 0.55, 0, 0)
    else: S["truck"].location = LEJOS
    apply_cam(S["cam"], *camera(t))

def CAMS():
    zt = ZZ2 + HB + HI + HR
    def hook(t):
        y = -14 + 16 * t / T("vamos a construir"); wy = y + 3.3
        u = seg(t, T("y por qué"), T("vamos a construir"))
        p0 = Vector((4.6, wy - 2.6, 0.9)); t0 = Vector((2.4, wy + 0.3, 0.6))
        p1 = Vector((9.0, -L - 9.0, 4.2)); t1 = Vector((0.5, -L + 2, -0.8))
        return p0.lerp(p1, u), t0.lerp(t1, u), mix(30, 30, u)
    return [
        (0.0, hook),
        (T("vamos a construir"), [(0, (9.0, -L - 9.0, 4.2), (0.5, -L + 2, -0.8), 30), (T("primero quitas"), (7.0, -L - 8.0, 3.0), (0, -L + 2, -1.0), 30),
                                  (T("pero la tierra"), (3.5, -L - 5.5, 1.2), (-1.2, -L + 1.5, ZS), 30), (T("así que la compactas"), (5.5, -L - 7.0, 2.0), (0, -L + 2, ZS), 30),
                                  (T("hasta dejarla"), (4.0, -L - 6.0, 1.0), (0, -L + 1.5, ZS), 30)]),
        (T("pero si echas"), [(0, (4.6, -L - 5.6, 0.5), (0, -L, ZS + 0.1), 30), (T("así que pones"), (5.0, -L - 6.0, 0.8), (0, -L, ZS + 0.4), 30),
                              (T("que encajan"), (1.8, -L - 3.2, ZS + 0.6), (0.4, -L, ZS + 0.25), 32), (T("una capa de"), (4.5, -L - 6.0, 0.6), (0, -L, ZS + 0.6), 30),
                              (T("ahora sí"), (4.5, -L - 6.2, 0.6), (0, -L, ZZ2), 30)]),
        (T("ahora sí"), [(0, (4.0, -L - 5.5, 0.7), (0, -L, ZZ2), 30), (T("primero", 2), (2.6, -L - 3.6, zt + 0.1), (0.5, -L, ZZ2 + 0.2), 32),
                          (T("y arriba"), (2.4, -L - 3.2, zt + 0.25), (0.6, -L, zt - 0.1), 32), (T("en las carreteras"), (5.0, -L - 6.5, 1.5), (0, -L + 1, ZZ1), 30)]),
        (T("si la carretera"), [(0, (6.5, -L - 7.0, 3.6), (0, -L + 2, -0.2), 30), (T("y en los bordes"), (8.5, -L - 6.5, 2.4), (4.0, -L + 2, -0.7), 30),
                                (T("y aquí viene"), (7.0, -L - 7.5, 3.0), (0.5, -L + 2, -0.3), 30)]),
        (T("se cuela"), [(0, (CX + 0.9, -L - 1.6, zt + 0.5), (CX, -L + 0.2, zt - 0.15), 34), (T("y al hacerse"), (CX + 0.7, -L - 1.3, zt + 0.4), (CX, -L + 0.2, zt - 0.15), 36), (T("la grieta crece", fin=True), (CX + 0.6, -L - 1.2, zt + 0.35), (CX, -L + 0.2, zt - 0.15), 36),
                         (T("luego pasa"), (CX + 5.0, -L - 4.5, 2.2), (CX, -L + 1, 0.3), 30), (T("así nace"), (CX + 2.0, -L - 2.5, 1.4), (CX, -L + 0.5, zt), 32)]),
        (T("por eso hay"), [(0, (6.0, -L - 6.5, 4.5), (0, 0, -0.3), 30), (DUR + 1, (5.0, -L - 7.5, 5.5), (0, 0, -0.3), 30)]),
    ]

def camera(t):
    segs = CAMS(); k = 0
    for i, (st, _) in enumerate(segs):
        if t >= st: k = i
    st, ks = segs[k]
    if callable(ks): return ks(t)
    ks = [(st if a == 0 else a, p, q, l) for a, p, q, l in ks]
    if ks[-1][0] <= t: ks = ks + [(t + 1, ks[-1][1], ks[-1][2], ks[-1][3])]
    return cam_state(t, ks, drift=0.01)

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v)
    zt = ZZ2 + HB + HI + HR
    return {"sub": Pj(Vector((-2.5, -L, ZS - 0.4))), "z1": Pj(Vector((2.6, -L, ZS + 0.25))), "z2": Pj(Vector((2.6, -L, ZZ1 + 0.25))),
            "ab": Pj(Vector((-2.4, -L, ZZ2 + HB / 2))), "ai": Pj(Vector((-2.4, -L, ZZ2 + HB + HI / 2))), "ar": Pj(Vector((-2.4, -L, zt))),
            "ditch": Pj(Vector((5.2, -L, -0.75))), "pipe": Pj(Vector((5.2, -L, -1.05))), "crack": Pj(Vector((CX, -L, zt - 0.1))),
            "truck": Pj(S["truck"].location + Vector((0, 3, 3.6))), "top": Pj(Vector((0, -L, zt + 0.2)))}

if __name__ == "__main__":
    run("carretera", build, pose, anchors)
