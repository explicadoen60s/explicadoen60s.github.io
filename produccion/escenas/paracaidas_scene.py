# «Si tuvieras que inventar un paracaídas»: cielo de maqueta con nubes low-poly. El paracaidista sale del avión y cae
# boca abajo (las nubes suben a toda velocidad). Flechas de aire que empujan, una tela que crece, la cúpula atada a la
# espalda, el tirón si se abre de golpe, la mochila, el extractor pequeñito, el deslizador con anillas, la cúpula que se
# convierte en ala con celdas que se hinchan, los mandos para girar y, al final, la isla de césped que sube: flare y aterrizaje.
# Planos (fotografía → motion): 0 caída + avión (libre: arriba) · 4,5 flechas · 8,5 tela · 11,6 cúpula · 15,7 tirón ·
# 19,7 mochila · 21,9 extractor · 25,5 saca la grande · 30,4 deslizador · 36 plano general · 37,7 ala · 41 celdas ·
# 47 giro · 50,7 velocidad · 54,7 suelo · 59 mandos · 61 flare · 63 aterrizaje · 64,5 vuelta al primer plano.
import bpy, bmesh, math, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from maqueta import *
from marcas import cargar
from mathutils import Vector, Matrix, Euler

T0, DUR = cargar("paracaidas")
_CT = {}
def T(*a, **k):
    key = (a, tuple(sorted(k.items())))
    if key not in _CT: _CT[key] = T0(*a, **k)
    return _CT[key]
SUIT = (1.0, 0.5, 0.15); SKIN = (0.93, 0.72, 0.6); HELM = (0.97, 0.97, 0.98); PACK = (0.2, 0.3, 0.6); LINE = (0.35, 0.35, 0.4)
C1 = PAL["rojo"]; C2 = PAL["amarillo"]; DARK = (0.15, 0.15, 0.2); PLANE = (0.92, 0.93, 0.96)
CANH = 3.4          # altura de la cúpula sobre el arnés

def domo(r, colores, n=16):
    """media esfera (cúpula) con gajos de colores alternos; base en z=0"""
    me = bpy.data.meshes.new("domo"); bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=n, v_segments=10, radius=r)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < -1e-4], context='VERTS')
    for f in bm.faces:
        c = f.calc_center_median(); a = math.atan2(c.y, c.x)
        f.material_index = int(((a + math.pi) / (2 * math.pi)) * n) % 2
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("domo", me); bpy.context.collection.objects.link(o)
    for c in colores: o.data.materials.append(mat(c))
    m = o.modifiers.new("s", "SOLIDIFY"); m.thickness = 0.03
    for p in me.polygons: p.use_smooth = True
    return o

def build():
    sc, cam = scene_setup(world=PAL["cielo"], shadow=0.22); entorno_claro(sc)
    S = {"cam": cam}
    # nubes que suben (sensación de caída)
    import random; rnd = random.Random(4)
    S["nubes"] = []
    for i in range(18):
        x = rnd.uniform(-9, 9); y = rnd.uniform(2, 14) if i % 3 else rnd.uniform(-9, -5)
        e = empty((x, y, 0)); e["z0"] = rnd.uniform(0, 44); e["x"] = x; e["y"] = y
        for o in nube((0, 0, 0), rnd.uniform(0.8, 1.6), seed=i): o.parent = e
        S["nubes"].append(e)
    # avión
    S["avion"] = empty((0, 0, 0))
    cyl(0.55, 5.0, (0, 0, 0), PLANE, S["avion"], rot=(0, math.pi / 2, 0))
    sph(0.55, (2.5, 0, 0), PLANE, S["avion"], scale=(1.6, 1, 1)); box((1.4, 7.5, 0.12), (0.2, 0, -0.1), PLANE, S["avion"])
    box((0.8, 2.6, 0.1), (-2.3, 0, 0.3), PLANE, S["avion"]); box((0.8, 0.1, 1.2), (-2.3, 0, 0.8), C1, S["avion"])
    box((0.9, 0.05, 1.0), (-0.6, -0.55, 0.05), DARK, S["avion"])
    for k in range(4): cyl(0.14, 0.05, (0.8 + 0.5 * k, -0.53, 0.25), (0.5, 0.7, 0.9), S["avion"], rot=(math.pi / 2, 0, 0))
    # isla de aterrizaje: césped, casa, árboles
    S["suelo"] = empty((0, 0, -300))
    for col, g, z in ((PAL["cesped"], 0.25, -0.125), (PAL["tierra"], 0.8, -0.65), (PAL["tierra2"], 1.0, -1.55)):
        box((10, 10, g), (0, 3, z), col, S["suelo"])
    box((1.6, 1.4, 1.2), (-2.6, 6.0, 0.6), PAL["pared"], S["suelo"]); box((1.8, 1.6, 0.15), (-2.6, 6.0, 1.3), C1, S["suelo"])
    box((0.35, 0.05, 0.6), (-2.6, 5.28, 0.3), PAL["madera"], S["suelo"])
    for x, y in ((2.6, 5.5), (3.4, 2.2), (-3.6, 1.5), (1.0, 7.0)):
        cyl(0.1, 0.8, (x, y, 0.4), PAL["madera"], S["suelo"]); sph(0.55, (x, y, 1.1), PAL["planta"], S["suelo"], seg=10)
    box((0.9, 0.9, 0.02), (0.8, -0.2, 0.01), (1.0, 1.0, 1.0), S["suelo"])   # diana blanca
    box((0.5, 0.5, 0.025), (0.8, -0.2, 0.01), C1, S["suelo"])
    # todo el equipo cuelga del «rig»
    S["rig"] = empty((0, 0, 0))
    S["diver"] = empty((0, 0, 0), S["rig"])
    d = S["diver"]
    box((0.4, 0.26, 0.6), (0, 0, 0), SUIT, d)
    sph(0.13, (0, -0.02, 0.45), SKIN, d); sph(0.145, (0, 0.02, 0.48), HELM, d, scale=(1, 1, 0.85))
    box((0.2, 0.03, 0.06), (0, -0.14, 0.47), DARK, d)
    S["pack"] = box((0.36, 0.16, 0.48), (0, 0.2, 0.02), PACK, d)
    S["piernas"] = [bar_obj(SUIT, 0.075) for _ in range(2)]
    S["brazos"] = [bar_obj(SUIT, 0.06) for _ in range(2)]
    for o in S["piernas"] + S["brazos"]: o.parent = d
    for sx in (-1, 1):
        box((0.04, 0.27, 0.62), (sx * 0.12, 0, 0), (0.15, 0.15, 0.18), d)   # arnés
    # tela de prueba (superficie que crece)
    S["tela"] = box((1, 1, 0.03), (0, 0, 0), (0.95, 0.95, 0.98), S["rig"], unique=True)
    # cúpula redonda, extractor y bolsa
    S["domo"] = domo(2.2, (C1, C2)); S["domo"].parent = S["rig"]
    S["piloto"] = domo(0.45, (C2, (1, 1, 1))); S["piloto"].parent = S["rig"]
    S["bolsa"] = box((0.3, 0.14, 0.4), (0, 0, 0), PACK, S["rig"])
    S["brida"] = bar_obj(LINE, 0.012)
    # deslizador con anillas
    S["slider"] = empty((0, 0, 0), S["rig"])
    box((1.4, 1.4, 0.03), (0, 0, 0), (0.3, 0.6, 1.0), S["slider"])
    for sx in (-1, 1):
        for sy in (-1, 1): torus(0.07, 0.018, (sx * 0.55, sy * 0.55, 0), (0.75, 0.76, 0.8), S["slider"])
    # ala con celdas
    S["ala"] = empty((0, 0, 0), S["rig"]); S["celdas"] = []; S["bocas"] = []
    for i in range(7):
        x = -1.62 + 0.54 * i; z = CANH + 0.25 - 0.12 * ((x / 1.62) ** 2)
        c = sph(1.0, (x, 0, z), C1 if i % 2 else C2, S["ala"], seg=16); c.scale = (0.31, 0.8, 0.06); S["celdas"].append(c)
        b = sph(1.0, (x, -0.7, z - 0.02), DARK, S["ala"], seg=12); b.scale = (0.2, 0.08, 0.04); S["bocas"].append(b)
    # cuerdas (a la cúpula y al ala) y mandos
    S["cuerdas"] = [bar_obj(LINE, 0.008) for _ in range(8)]
    S["mandos"] = [torus(0.05, 0.014, (0, 0, 0), C1, S["rig"], rot=(math.pi / 2, 0, 0)) for _ in range(2)]
    S["frenos"] = [bar_obj(LINE, 0.009) for _ in range(2)]
    # flechas
    S["f_aire"] = [flecha3d((0, 0, 0), (0, 0, 1), 0.9, 0.06, parent=S["rig"]) for _ in range(3)]
    S["f_tiron"] = flecha3d((0, 0, 0), (0, 0, 1), 1.4, 0.11, parent=S["rig"])
    S["f_celda"] = [flecha3d((0, 0, 0), (0, 1, 0), 0.7, 0.05, color=(0.35, 0.65, 1.0), parent=S["rig"]) for _ in range(3)]
    S["f_vel"] = flecha3d((0, 0, 0), (0, 0, -1), 1.0, 0.07, color=(0.35, 0.65, 1.0), parent=S["rig"])
    dyn = [cam, S["nubes"], S["avion"], S["suelo"], S["rig"], S["brida"], S["cuerdas"], S["frenos"]]
    join_static(dyn)
    return sc, S

# ---------------- estado ----------------
def postura(t):
    """0 = boca abajo (caída libre), 1 = colgado de pie"""
    u = seg(t, T("así que coges") - 0.2, T("así que coges") + 0.8)
    u *= 1 - seg(t, T("así que la doblas"), T("así que la doblas") + 0.8)
    u = max(u, seg(t, T("ese pequeño"), T("ese pequeño") + 1.2))
    return u

def vel(t):
    """velocidad de caída (m/s visuales para las nubes)"""
    v = mix(4, 14, seg(t, 0, 3.5))
    v = mix(v, 3.0, seg(t, T("ese pequeño") + 0.5, T("se queda arriba", fin=True) + 1.5))
    v = mix(v, 1.6, seg(t, T("la velocidad baja"), T("kilómetros por", 2, fin=True)))
    v = mix(v, 0.0, seg(t, T("el ala se"), T("aterrizas") + 0.2))
    return v

def caida(t, dt=1 / 30):
    s, x = 0.0, 0.0
    while x < t: s += vel(x) * dt; x += dt
    return s

def suelo_z(t):
    return keyed(t, [(T("pero para tocar") - 0.6, -60.0), (T("a unos tres"), -9.0), (T("el ala se"), -2.4), (T("aterrizas"), -1.12), (DUR + 2, -1.12)])

def apertura(t):
    """tamaño de la cúpula redonda (0-1)"""
    a = seg(t, T("así que coges") + 0.3, T("enorme", fin=True) + 0.3)
    if T("pero si se abre") <= t < T("así que la doblas"):
        a = 0.15 if t < T("a esa velocidad") + 0.3 else seg(t, T("a esa velocidad") + 0.3, T("a esa velocidad") + 0.5)
    a *= 1 - seg(t, T("así que la doblas"), T("mochila", fin=True))
    if t > T("ese pequeño"):
        a = 0.25 * seg(t, T("ese pequeño"), T("despacio", fin=True))
        a = mix(a, 1.0, seg(t, T("se queda arriba"), T("unos segundos", fin=True) + 0.4))
    return a * (1 - seg(t, T("es un ala") - 0.3, T("es un ala") + 0.4))

def hinchado(t):
    return mix(0.25, 1.0, seg(t, T("el aire entra"), T("las hincha", fin=True) + 0.3))

def ala(t): return seg(t, T("es un ala") - 0.3, T("es un ala") + 0.5)

def freno(t):
    return max(seg(t, T("tiras de las dos") , T("a la vez", fin=True)) * (1 - seg(t, T("aterrizas") + 0.5, T("sígueme"))),
               0.6 * seg(t, T("y giras"), T("y giras") + 0.4) * (1 - seg(t, T("dos asas") + 0.4, T("dos asas") + 0.9)))

def M(S): return S["rig"].matrix_world.copy()

def pose(t, S):
    D = caida(t)
    for e in S["nubes"]:
        e.location = (e["x"], e["y"], ((e["z0"] + D * 1.0) % 44.0) - 22.0)
        if t > T("pero para tocar"): e.location.z += 30 * seg(t, T("pero para tocar"), T("a unos tres"))
    # avión que se aleja
    if t < 7:
        S["avion"].location = (-1.6 + 9.0 * t, 3.4, 2.6 + 0.9 * D); S["avion"].rotation_euler = (0, -0.06, 0)
    else: S["avion"].location = LEJOS
    # rig: al final avanza y gira; aterriza andando
    giro = 0.6 * math.sin(math.pi * seg(t, T("y giras"), T("dos asas", fin=True) + 1.5))
    S["rig"].rotation_euler = (0, 0, giro)
    S["rig"].location = (0, -0.6 * seg(t, T("aterrizas"), T("sígueme") + 1.0), 0)
    S["suelo"].location = (0, 0, suelo_z(t))
    # postura del cuerpo
    p = postura(t); bob = 0.05 * math.sin(t * 3)
    tiron = 0.0
    if T("a esa velocidad") + 0.3 < t < T("de verdad", fin=True):
        tiron = 0.5 * math.exp(-(t - T("a esa velocidad") - 0.3) * 3) * abs(math.sin((t - T("a esa velocidad")) * 18))
    S["diver"].rotation_euler = (mix(math.pi / 2, 0, p) + 0.1 * math.sin(t * 1.3) * (1 - p), 0, 0)
    S["diver"].location = (0, 0, bob * (1 - p) + tiron)
    # brazos y piernas (en caída: abiertos en arco; colgado: brazos arriba a los mandos)
    walk = seg(t, T("aterrizas"), T("aterrizas") + 0.3)
    for k, sx in enumerate((-1, 1)):
        sw = 0.25 * math.sin(t * 9 + k * math.pi) * walk
        hip = Vector((sx * 0.1, 0, -0.3)); foot = hip + Vector((sx * mix(0.25, 0.05, p), mix(0.15, 0.0, p) + sw, -0.75))
        bar_set(S["piernas"][k], hip, foot)
        sh = Vector((sx * 0.22, 0, 0.25))
        hand_free = sh + Vector((sx * 0.45, -0.1, 0.25))
        hand_up = sh + Vector((sx * 0.08, -0.05, mix(0.45, 0.05, freno(t))))
        hold = seg(t, T("también avanzas") - 0.5, T("también avanzas")) * (1 - walk)
        bar_set(S["brazos"][k], sh, hand_free.lerp(hand_up, hold))
    # tela de prueba
    if T("cuanto más") - 0.2 < t < T("así que coges") + 0.4:
        u = mix(1.0, 3.6, seg(t, T("cuanto más"), T("superficie", fin=True)))
        S["tela"].location = (0, 0, 1.1); S["tela"].scale = (u, u, 0.03)
        S["tela"].rotation_euler = (0, 0, 0)
    else: S["tela"].location = LEJOS; S["tela"].scale = (1, 1, 0.03)
    # flechas de aire bajo el cuerpo / bajo la tela
    fa = win01(t, T("necesitas que") - 0.1, T("así que coges") + 0.3, 0.3, 0.3)
    grande = 1 + 1.4 * seg(t, T("cuanto más"), T("más aire", fin=True))
    for k, f in enumerate(S["f_aire"]):
        if fa > 0:
            x = (k - 1) * (0.45 * grande)
            f.location = (x, 0, (-1.4 if t < T("cuanto más") else 0.0) + 0.08 * math.sin(t * 8 + k))
            f.scale = (fa * grande ** 0.5,) * 2 + (fa * grande,)
        else: f.location = LEJOS
    ft = win01(t, T("a esa velocidad") + 0.25, T("de verdad", fin=True), 0.1, 0.3)
    S["f_tiron"].location = (0, 0.3, 0.5) if ft > 0 else LEJOS; S["f_tiron"].scale = (ft,) * 3
    # cúpula redonda
    a = apertura(t); pM = M(S)
    S["domo"].location = (0, 0, CANH * mix(0.4, 1.0, a) + 0.25)
    S["domo"].scale = (max(a, 0.001), max(a, 0.001), max(a, 0.001) * mix(1.2, 0.6, a))
    S["domo"].hide_render = a < 0.01
    # extractor y bolsa
    tp = T("y la sacas")
    up = seg(t, tp, tp + 0.6) * (1 - seg(t, T("es un ala") - 0.5, T("es un ala")))
    hp = mix(0.3, 2.0, up) + (CANH - 0.4) * seg(t, T("ese pequeño") - 0.3, T("ese pequeño") + 0.6) + mix(0, 0.8, seg(t, T("ese pequeño"), T("despacio", fin=True)))
    S["piloto"].location = (0, 0.15 * (1 - p), hp); S["piloto"].scale = (max(up, 0.001),) * 3; S["piloto"].hide_render = up < 0.01
    ub = seg(t, T("ese pequeño"), T("despacio", fin=True))
    S["bolsa"].location = (0, 0.1, mix(0.1, CANH, ub)) if 0.02 < ub and t < T("pero aún") + 0.5 else LEJOS
    pk = (pM @ (S["diver"].matrix_basis @ Vector((0, 0.28, 0.2)))) if t > tp else Vector(LEJOS)
    bar_set(S["brida"], pk, pM @ Vector((0, 0.15 * (1 - p), hp)) if up > 0.01 else pk + Vector((0, 0, 0.01)))
    # deslizador
    us = seg(t, T("así que pones") , T("así que pones") + 0.6) * (1 - ala(t))
    zs = mix(CANH * mix(0.4, 1.0, a) + 0.1, 1.0, seg(t, T("se queda arriba"), T("unos segundos", fin=True) + 0.4))
    S["slider"].location = (0, 0, zs) if us > 0.01 else LEJOS; S["slider"].scale = (max(us, 0.01) * mix(0.6, 1.0, a),) * 3
    # ala
    w = ala(t); h = hinchado(t); fr = freno(t)
    S["ala"].scale = (max(w, 0.001),) * 3
    S["ala"].location = (0, 0, 0) if w > 0.01 else LEJOS
    S["ala"].rotation_euler = (-0.35 * seg(t, T("el ala se"), T("frena", fin=True)) * (1 - seg(t, T("aterrizas") + 0.4, T("sígueme"))) + 0.15 * fr, 0, -0.3 * giro)
    for c in S["celdas"]: c.scale = (0.31, 0.8, mix(0.05, 0.26, h))
    for b in S["bocas"]: b.scale = (0.2, 0.08, mix(0.02, 0.17, h))
    # cuerdas: a la cúpula o al ala
    sh = [Vector((sx * 0.18, 0.05, 0.28)) for sx in (-1, 1)]
    if p > 0.5 and (a > 0.05 or w > 0.05):
        for k, L in enumerate(S["cuerdas"]):
            side = -1 if k < 4 else 1; j = k % 4
            if w > 0.5:
                top = Vector((side * (0.3 + 0.42 * j), (-0.5 if j % 2 else 0.4), CANH + 0.2 - 0.1 * j * j / 9))
                top = S["ala"].matrix_basis @ top
            else:
                ang = math.radians(side * (20 + 22 * j)); r = 2.2 * a
                top = Vector((r * math.sin(ang), r * 0.3 * math.cos(ang * 2), S["domo"].location.z))
            base = sh[0 if side < 0 else 1]
            if zs < CANH and us > 0.01 and w < 0.5: base = base
            bar_set(L, pM @ base, pM @ top)
    else:
        for L in S["cuerdas"]: bar_set(L, LEJOS, Vector(LEJOS) + Vector((0, 0, 0.01)))
    # mandos y líneas de freno
    for k, sx in enumerate((-1, 1)):
        mz = mix(0.75, 0.15, fr)
        on = w > 0.5 and p > 0.5
        S["mandos"][k].location = (sx * 0.3, -0.12, mz) if on else LEJOS
        if on:
            tail = S["ala"].matrix_basis @ Vector((sx * 1.5, 0.75, CANH + 0.1 - 0.05 * fr))
            bar_set(S["frenos"][k], pM @ Vector((sx * 0.3, -0.12, mz)), pM @ tail)
        else: bar_set(S["frenos"][k], LEJOS, Vector(LEJOS) + Vector((0, 0, 0.01)))
    # aire entrando en las celdas
    fc = win01(t, T("tiene celdas") - 0.1, T("como un colchón", fin=True), 0.3, 0.3)
    for k, f in enumerate(S["f_celda"]):
        if fc > 0:
            f.location = (-1.0 + 1.0 * k, -1.6 - 0.25 * ((t * 1.5 + k * 0.3) % 1.0), CANH + 0.15)
            f.scale = (fc,) * 3
        else: f.location = LEJOS
    fv = win01(t, T("la velocidad baja") - 0.2, T("kilómetros por", 2, fin=True) + 0.4, 0.3, 0.3)
    S["f_vel"].location = (0.8, -0.3, -0.2) if fv > 0 else LEJOS
    S["f_vel"].scale = (fv, fv, fv * mix(1.6, 0.4, seg(t, T("la velocidad baja"), T("kilómetros por", 2, fin=True))))
    apply_cam(S["cam"], *cam_lin(t, CAM()))

def CAM():
    k = Claves(); add = k.add
    ini = V((0, 0, 0.3), (1.6, -3.0, -0.9), 30)
    add(0.0, ini)
    add(1.2, V((0, 0, 0.0), (-1.4, -2.7, 0.7), 32))
    add(T("doscientos") - 0.3, V((0, 0, 0.0), (2.2, -3.4, 0.2), 30))
    add(T("vamos a"), V((0, 0, 0.0), (-0.8, -3.2, 1.6), 32))
    add(T("necesitas que"), V((0, 0, -0.6), (0.2, -3.4, -0.6), 30), 1.2)
    add(T("cuanto más"), V((0, 0, 0.5), (1.6, -5.6, 0.4), 28), 1.2)
    add(T("así que coges"), V((0, 0, 1.5), (2.4, -7.2, 0.4), 28), 1.2)
    add(T("y la atas"), V((0, 0, 0.5), (1.0, -3.2, 0.5), 30))
    add(T("pero si se abre"), V((0, 0, 1.5), (-2.4, -7.0, 0.6), 28), 1.2)
    add(T("el tirón"), V((0, 0, 0.4), (1.12, -3.25, 0.25), 40), 0.8)
    add(T("así que la doblas"), V((0, 0.1, 0.1), (1.0, -1.8, 1.4), 32), 1.0)
    add(T("y la sacas"), V((0, 0, 1.4), (1.6, -4.4, 1.0), 30), 0.6)
    add(T("del tamaño"), V((0, 0, 2.6), (-1.2, -3.6, 0.4), 32))
    add(T("ese pequeño"), V((0, 0, 2.0), (2.2, -7.4, 0.0), 28), 1.2)
    add(T("pero aún"), V((0, 0, 1.6), (-1.6, -5.6, 0.8), 28))
    add(T("así que pones"), V((0, 0, 2.6), (1.0, -3.6, 0.2), 32), 1.0)
    add(T("se queda arriba"), V((0, 0, 1.8), (1.8, -6.0, 0.2), 28), 1.2)
    add(T("y aquí viene"), V((0, 0, 1.6), (4.0, -8.0, 1.4), 28))
    add(T("el paracaídas moderno"), V((0, 0, 1.8), (-2.2, -7.0, 0.6), 28), 1.0)
    add(T("es un ala"), V((0, 0, 2.0), (2.6, -6.6, 1.0), 28))
    add(T("tiene celdas"), V((0, -0.7, CANH - 0.3), (0.9, -2.8, 0.2), 30), 0.6)
    add(T("el aire entra"), V((0, -0.5, CANH - 0.3), (-0.8, -3.0, 0.4), 30), 0.6)
    add(T("y la tela"), V((0, 0, 2.2), (1.6, -6.2, 1.6), 28))
    add(T("así no solo"), V((0, 0, 1.8), (3.6, -6.4, -0.6), 28), 0.6)
    add(T("y giras"), V((0, 0, 0.6), (1.25, -3.0, 0.5), 40), 0.8)
    add(T("la velocidad baja"), V((0, 0, 1.6), (-2.6, -7.0, 0.3), 28), 0.8)
    add(T("a unos veintidós"), V((0, 0, 0.5), (1.2, -3.0, 0.2), 30))
    add(T("pero para tocar"), V((0, 0, -2.0), (3.0, -7.5, 4.2), 28), 0.6)
    add(T("a unos tres"), V((0, 0, -0.5), (2.4, -5.6, 0.6), 28))
    add(T("tiras de las dos"), V((0, 0, 0.6), (1.12, -3.0, 0.38), 40), 0.6)
    add(T("el ala se"), V((0, 0, 1.4), (6.0, -1.5, 0.6), 28), 0.6)
    add(T("aterrizas"), V((0, -0.3, 0.6), (2.2, -5.0, 1.2), 28), 0.6)
    add(T("sígueme"), V((0, -0.6, 0.6), (-1.6, -4.0, 1.0), 30))
    add(DUR + 1, ini)
    return k.k

def anchors(sc, S, t):
    cam = S["cam"]; P = lambda v: proj(sc, cam, v); pM = M(S)
    return {"cuerpo": P(pM @ Vector((0, 0, 0.6))), "pies": P(pM @ Vector((0, 0, -1.1))), "tela": P(pM @ Vector((0, 0, 1.3))),
            "domo": P(pM @ Vector((0, 0, S["domo"].location.z + 1.2))), "pack": P(pM @ Vector((0, 0.3, 0.4))),
            "piloto": P(pM @ Vector((0, 0, S["piloto"].location.z + 0.5))), "slider": P(pM @ Vector((0.6, 0, S["slider"].location.z))),
            "ala": P(pM @ Vector((0, 0, CANH + 0.8))), "boca": P(pM @ Vector((0, -0.7, CANH + 0.2))), "mando": P(pM @ Vector((0.3, -0.12, 0.6)))}

if __name__ == "__main__":
    run("paracaidas", build, pose, anchors)
