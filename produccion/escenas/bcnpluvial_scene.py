# «¿Cuánta agua de tormenta cabe bajo Barcelona?» (Lo que esconde tu ciudad, parte 3). Maqueta de Barcelona sobre una isla
# de terreno cortada por delante: la montaña a la izquierda, el mar a la derecha, una calle que baja hacia el mar junto al
# corte, la alcantarilla en corte bajo la calle y, bajo el parque, el depósito de hormigón con pilares que se llena.
# Después llegan dos depósitos más unidos por un túnel con compuertas, los sensores, la depuradora, las 15 chinchetas de
# depósitos, la ciudad convertida en 190 piscinas olímpicas y el depósito nuevo de 2028.
# Planos (fotografía → motion; esquina libre arriba-izquierda salvo que se diga):
# 0 calle con lluvia y agua corriendo (primer plano, coche) · 2,4 seguimos el agua calle abajo · 4 ciudad bajo la lluvia ·
# 6,1 alejamos · 8 maqueta entera: montaña y mar · 10,3 desde la montaña · 11,8 calle en cuesta · 13,6 alcantarilla en corte ·
# 16,3 tapas que saltan · 18 parque y depósito que aparece · 19,6 · 20,9 depósito vacío por dentro · 23,5 tubo de entrada ·
# 24,8 agua que cae · 26,2 depósito Joan Miró · 28,4 · 31,2 ciudad entera · 33,6 tres depósitos · 35,1 túnel · 36,5 sensores ·
# 38 · 39,4 compuertas · 41 · 42,8 sale el sol · 44,2 depuradora · 46,6 · 48,2 chinchetas desde arriba · 50,3 · 53,7 piscinas ·
# 55,5 · 56,5 depósito de 2028 · 58,5 · 59,4 · 60,5 · 62,7 · 64,2 · 65,5 · 67,7 vuelta al primer plano.
import bpy, bmesh, math, sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from modelos import *
from maqueta import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("bcnpluvial")
AGUA = PAL["agua"]; HORM = PAL["hormigon"]; HORM2 = (0.66, 0.66, 0.64); CREMA = PAL["corte"]
YF, YB = -4.0, -1.4                       # cara del corte (delante) y fondo de los depósitos
DEP = {"A": (-1.8, 1.8, -2.1, -0.75), "B": (-4.2, -2.4, -1.95, -0.9), "C": (2.4, 4.2, -1.95, -0.9), "D": (4.7, 6.1, -2.1, -1.0)}
ZS, RS = -0.38, 0.15                      # alcantarilla
ZT, RT = -1.75, 0.14                      # túnel que une los depósitos
XDROP = -1.3
TAPAS = [-3.0, 0.8, 3.0]
SENS = [-3.0, 0.5, 3.0]
CIELO_T = (0.62, 0.69, 0.78)

def setbox(o, x0, x1, y0, y1, z0, z1):
    if x1 - x0 < 1e-3 or y1 - y0 < 1e-3 or z1 - z0 < 1e-3: o.location = LEJOS; return
    o.location = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2); o.scale = (x1 - x0, y1 - y0, z1 - z0)

def fbox(size, loc, color, parent=None, unique=False):
    """caja rápida (sin bpy.ops: con miles de objetos en escena, los operadores van muy lentos)"""
    me = bpy.data.meshes.new("fb"); bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("fb", me); bpy.context.collection.objects.link(o); o.location = loc; o.scale = size
    return setup(o, color, parent, unique=unique)

def fbar(color, r):
    me = bpy.data.meshes.new("fr"); bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=1, radius2=1, depth=1)
    for v in bm.verts: v.co.z += 0.5
    bm.to_mesh(me); bm.free(); o = bpy.data.objects.new("fr", me); bpy.context.collection.objects.link(o); setup(o, color); o["r"] = r
    return o

def unit(color, unique=False): return fbox((1, 1, 1), LEJOS, color, unique=unique)

def nube_gris(loc, s=1.0, seed=0, col=(0.72, 0.75, 0.80)):
    r = random.Random(seed); out = []
    for i in range(5):
        dx = (i - 2) * 0.55 * s + r.uniform(-0.1, 0.1) * s; rad = s * (0.55 + 0.35 * (1 - abs(i - 2) / 2))
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=rad, location=(loc[0] + dx, loc[1] + r.uniform(-0.2, 0.2) * s, loc[2] + r.uniform(-0.1, 0.25) * s))
        o = bpy.context.object; setup(o, col); o.scale.z = 0.75; out.append(o)
    return out

def deposito(k):
    """caja de hormigón abierta por delante (el corte): suelo, techo, paredes, pilares y cantos en crema"""
    x0, x1, z0, z1 = DEP[k]; w, h, th = x1 - x0, z1 - z0, 0.08; yc = (YF + YB) / 2; dpt = YB - YF
    e = empty(((x0 + x1) / 2, 0, z0))
    fbox((w, dpt, th), (0, yc, th / 2), HORM, e); fbox((w, dpt, th), (0, yc, h - th / 2), HORM, e)
    fbox((w, th, h), (0, YB - th / 2, h / 2), HORM2, e)
    for sx in (-1, 1): fbox((th, dpt, h), (sx * (w / 2 - th / 2), yc, h / 2), HORM, e)
    n = max(2, int(w / 0.8))
    for i in range(n):
        for yy in (YF + 0.75, YB - 0.7):
            cilindro(0.055, h - 2 * th, (-w / 2 + (i + 0.5) * w / n, yy, h / 2), HORM2, e, v=16, r=0)
    for zz in (th / 2, h - th / 2): fbox((w, 0.012, th), (0, YF - 0.004, zz), CREMA, e)
    for sx in (-1, 1): fbox((th, 0.012, h), (sx * (w / 2 - th / 2), YF - 0.004, h / 2), CREMA, e)
    return e

def build():
    sc, cam = scene_setup(world=PAL["cielo"], shadow=0.25, light_rot=-40); entorno_claro(sc)
    S = {"cam": cam, "sc": sc}
    nubes(9, (0, 10, 4.0), 9, 1.2, 1.0, s=1.5, seed=3)
    S["grises"] = []
    rg = random.Random(4)
    for i in range(6): S["grises"] += nube_gris((rg.uniform(-5, 5), rg.uniform(-1, 3), 3.4 + rg.uniform(-0.2, 0.4)), 1.1, seed=20 + i)
    # terreno: césped arriba, playa y mar a la derecha, tierra cortada por delante (con huecos para depósitos y tubos)
    fbox((12.05, 8.0, 0.12), (-0.475, 0, -0.06), PAL["cesped"])
    fbox((0.3, 8.0, 0.12), (5.7, 0, -0.06), (0.95, 0.87, 0.62))
    fbox((0.65, 8.0, 0.1), (6.175, 0, -0.07), AGUA)
    fbox((13.0, 5.0, 2.28), (0, 1.5, -1.26), PAL["tierra"])
    fbox((13.0, 8.0, 0.6), (0, 0, -2.7), PAL["tierra2"])
    S["tierra"] = fbox((13.0, 3.0, 2.28), (0, -2.5, -1.26), PAL["tierra"], unique=True)
    S["cut"] = {}
    for k in DEP: S["cut"][k] = cortador((1, 1, 1), LEJOS)
    S["cut"]["s"] = cortador((13.2, 0.32, 0.36), (0, YF + 0.06, ZS))
    S["cut"]["t"] = cortador((1, 1, 1), LEJOS)
    S["cut"]["d"] = cortador((1, 1, 1), LEJOS)
    for c in S["cut"].values(): cortar(S["tierra"], c)
    # montaña (izquierda, al fondo)
    for (x, y, r, h) in ((-5.4, 1.6, 2.2, 1.8), (-4.5, 3.2, 1.7, 1.3)):
        bpy.ops.mesh.primitive_cone_add(vertices=9, radius1=r, radius2=0.55, depth=h, location=(x, y, h / 2))
        setup(bpy.context.object, PAL["cesped2"])
    for i, (x, y) in enumerate(((-4.6, 0.6), (-5.9, 0.4), (-4.2, 2.0), (-6.1, 2.6), (-3.9, 3.6))):
        arbol((x, y, 0.0), 0.5, seed=i)
    # calle que baja hacia el mar, junto al corte, con acera de atrás
    calle(10.4, (0.0, -3.4, 0.0), ancho=0.9, aceras=False)
    fbox((10.4, 0.2, 0.08), (0.0, -2.85, 0.04), (0.82, 0.82, 0.8))
    S["tapas"] = [cilindro(0.12, 0.03, (x, -3.62, 0.05), (0.25, 0.26, 0.28), unique=False) for x in TAPAS]
    S["chorros"] = [cilindro(0.07, 1.0, LEJOS, AGUA, v=16, r=0) for _ in TAPAS]
    # parque sobre el depósito
    fbox((3.6, 1.5, 0.02), (0, -2.0, 0.01), (0.42, 0.76, 0.33))
    fbox((3.4, 0.22, 0.025), (0, -2.0, 0.02), (0.92, 0.84, 0.66))
    for i, x in enumerate((-1.5, -0.8, 0.0, 0.8, 1.5)):
        arbol((x, -1.55 if i % 2 else -2.45, 0.0), 0.5, seed=10 + i)
    for x in (-1.15, 0.45):
        caja((0.34, 0.1, 0.05), (x, -2.2, 0.17), PAL["madera"]); caja((0.34, 0.03, 0.12), (x, -2.25, 0.25), PAL["madera"])
    persona((-0.3, -2.1, 0.02), 0.32, ropa=PAL["amarillo"]); persona((1.1, -1.85, 0.02), 0.3, ropa=PAL["rosa"])
    # ciudad (bajo un empty: se aplasta cuando salen las piscinas)
    S["ciudad"] = empty((0, 0, 0))
    rnd = random.Random(7); cols = [PAL["pared"], (0.98, 0.85, 0.55), (0.93, 0.74, 0.62), (0.86, 0.90, 0.93), (0.98, 0.95, 0.88), PAL["rosa"]]
    y = -0.8
    while y < 3.7:
        x = -3.9 + (0.3 if int(y * 10) % 2 else 0)
        while x < 5.2:
            if not (x < -3.6 and y > 1.2):
                pis = rnd.randint(3, 8)
                if rnd.random() < 0.18: casa((x, y, 0), 0.3, parent=S["ciudad"], pared=rnd.choice(cols), rot=rnd.choice((0, math.pi)))
                else: edificio((x, y, 0), pisos=pis, s=0.3, parent=S["ciudad"], color=rnd.choice(cols), ancho=1.7, fondo=1.7)
            x += 0.85
        y += 0.8
    for x in (-3.6, -2.7, 2.6, 3.5, 4.4):
        edificio((x, -1.9, 0), pisos=rnd.randint(3, 6), s=0.3, parent=S["ciudad"], color=rnd.choice(cols), ancho=1.7, fondo=1.7)
    for x in (-2.2, 2.2, 5.1): arbol((x, -2.5, 0), 0.4, parent=S["ciudad"], seed=int(x * 10))
    # coches por la calle (hacia el mar)
    S["coches"] = [coche(LEJOS, 0.28, color=c) for c in (PAL["rojo"], (0.2, 0.45, 0.85), PAL["amarillo"])]
    # agua en la calle
    S["calle_agua"] = unit(AGUA)
    S["fcalle"] = [flecha3d(LEJOS, (1, 0, 0), 0.5, 0.045) for _ in range(3)]
    # alcantarilla en corte y su agua
    medio_tubo([(-6.5, YF, ZS), (6.5, YF, ZS)], RS, 0.03, (0.6, 0.6, 0.62))
    S["alc_agua"] = unit(AGUA)
    S["falc"] = [flecha3d(LEJOS, (1, 0, 0), 0.35, 0.035) for _ in range(3)]
    # sensores dentro del tubo
    S["sens"] = []
    for x in SENS:
        caja((0.16, 0.08, 0.09), (x, YF + 0.1, ZS + 0.1), PAL["amarillo"])
        S["sens"].append(sph(0.04, (x, YF + 0.05, ZS + 0.08), (0.4, 0.4, 0.4), unique=True))
    # depósitos
    S["dep"] = {k: deposito(k) for k in DEP}
    S["dagua"] = {k: unit(AGUA) for k in DEP}
    S["bajada"] = medio_tubo([(XDROP, YF, -0.4), (XDROP, YF, -0.8)], 0.1, 0.025, (0.6, 0.6, 0.62))
    S["chorro"] = unit(AGUA); S["fdrop"] = flecha3d(LEJOS, (0, 0, -1), 0.35, 0.04)
    # túnel que une los depósitos y compuertas
    S["tunel"] = medio_tubo([(-3.3, YF, ZT), (3.3, YF, ZT)], RT, 0.03, (0.6, 0.6, 0.62))
    S["tun_agua"] = unit(AGUA)
    S["comp"] = [caja((0.05, 0.3, 0.32), LEJOS, PAL["rojo"]) for _ in range(2)]
    S["ftun"] = [flecha3d(LEJOS, (1, 0, 0), 0.4, 0.04) for _ in range(2)]
    # depuradora junto al mar
    S["depura"] = empty((5.2, -2.0, 0))
    for dx in (-0.25, 0.3):
        cilindro(0.26, 0.3, (dx, 0, 0.15), (0.85, 0.86, 0.88), S["depura"])
        cilindro(0.21, 0.02, (dx, 0, 0.3), (0.45, 0.72, 0.85), S["depura"], r=0.005)
    caja((0.3, 0.26, 0.26), (0.0, 0.42, 0.13), (0.95, 0.95, 0.95), S["depura"])
    S["fdep"] = [flecha3d(LEJOS, (1, 0, 0), 0.4, 0.04) for _ in range(2)]
    # chinchetas de depósitos (15)
    S["pins"] = []
    rp = random.Random(11); P = [(0, -3.0)]
    while len(P) < 15:
        q = (rp.uniform(-4.0, 5.0), rp.uniform(-2.6, 3.4))
        if all(math.dist(q, p) > 1.1 for p in P): P.append(q)
    for x, yy in P:
        e = empty(LEJOS); e["p"] = (x, yy)
        cilindro(0.025, 1.1, (0, 0, 0.55), (0.95, 0.95, 0.97), e, v=8, r=0); bola(0.22, (0, 0, 1.2), (0.2, 0.55, 0.95), e)
        S["pins"].append(e)
    # 190 piscinas olímpicas (19 x 10)
    S["pis"] = []
    for j in range(10):
        for i in range(19):
            o = fbox((0.44, 0.27, 0.05), LEJOS, (0.97, 0.97, 0.98)); w = fbox((0.38 / 0.44, 0.2 / 0.27, 0.4), (0, 0, 0.32), AGUA, o)
            o["p"] = (-4.3 + i * 0.5, -2.65 + j * 0.62); o["i"] = i + j * 0.9; S["pis"].append(o)
    # lluvia
    S["lluvia"] = [fbar((0.55, 0.72, 0.98), 0.012) for _ in range(70)]
    dyn = [cam, S["grises"], S["tierra"], list(S["cut"].values()), S["chorros"], S["ciudad"], S["coches"], S["calle_agua"], S["fcalle"],
           S["alc_agua"], S["falc"], S["sens"], list(S["dep"].values()), list(S["dagua"].values()), S["bajada"], S["chorro"], S["fdrop"],
           S["tunel"], S["tun_agua"], S["comp"], S["ftun"], S["depura"], S["fdep"], S["pins"], S["pis"], S["lluvia"], S["tapas"]]
    join_static(dyn)
    return sc, S

# ---------------- tiempos ----------------
def llueve(t): return t < T("cuando pasa") + 0.4 or t > T("pídelo") - 0.3
def construido(t, k):
    a = {"A": T("así que cavas"), "B": T("así que construyes"), "C": T("así que construyes") + 0.5, "D": T("y en dos mil")}[k]
    return seg(t, a, a + 1.2)

def nivel(t, k):
    """fracción llena de cada depósito"""
    if k == "A":
        v = seg(t, T("el agua de la"), T("guarda cincuenta", fin=True) + 1.6) * 0.85
        v = mix(v, 0.12, seg(t, T("el agua sale poco"), T("así no se", fin=True)))
        return mix(v, 0.3, seg(t, T("pídelo"), DUR))
    if k == "B":
        v = seg(t, T("y unas compuertas"), T("se llena") + 0.6) * 0.85
        return mix(v, 0.1, seg(t, T("el agua sale poco"), T("así no se", fin=True)))
    if k == "C":
        v = seg(t, T("se llena") + 0.6, T("cuando pasa")) * 0.6
        return mix(v, 0.1, seg(t, T("el agua sale poco"), T("así no se", fin=True)))
    return 0.15 * seg(t, T("de sesenta"), T("de sesenta") + 1.5)

def pose(t, S):
    sc = S["sc"]
    tormenta = max(1 - seg(t, T("cuando pasa"), T("cuando pasa") + 1.2), seg(t, T("pídelo") - 0.5, T("pídelo") + 1.0))
    sc.world.color = lin(tuple(mix(a, b, tormenta) for a, b in zip(PAL["cielo"], CIELO_T)))
    for o in S["grises"]: o.hide_render = tormenta < 0.3
    # cortes en la tierra (huecos de los depósitos, el túnel y la bajada)
    for k in DEP:
        x0, x1, z0, z1 = DEP[k]
        if construido(t, k) > 0.02: setbox(S["cut"][k], x0, x1, YF - 0.1, YB, z0, z1)
        else: S["cut"][k].location = LEJOS
        e = S["dep"][k]; g = construido(t, k)
        if g < 0.02: e.location = LEJOS
        else: e.location = ((x0 + x1) / 2, 0, z0); e.scale = (1, 1, g)
        lv = nivel(t, k) * g
        o = S["dagua"][k]
        if lv > 0.01: setbox(o, x0 + 0.08, x1 - 0.08, YF + 0.002, YB - 0.08, z0 + 0.08, z0 + 0.08 + (z1 - z0 - 0.16) * lv)
        else: o.location = LEJOS
    if construido(t, "A") > 0.02: setbox(S["cut"]["d"], XDROP - 0.14, XDROP + 0.14, YF - 0.1, YF + 0.15, -0.8, -0.4); S["bajada"].location = (0, 0, 0)
    else: S["cut"]["d"].location = LEJOS; S["bajada"].location = LEJOS
    tun = seg(t, T("y los conectas"), T("y los conectas") + 0.8)
    if tun > 0.02:
        setbox(S["cut"]["t"], -3.3, 3.3, YF - 0.1, YF + 0.19, ZT - 0.18, ZT + 0.18); S["tunel"].location = (0, 0, 0); S["tunel"].scale = (tun, 1, 1)
    else: S["cut"]["t"].location = LEJOS; S["tunel"].location = LEJOS
    # compuertas: la de la izquierda se abre primero (se llena B), luego la de la derecha
    tc = T("y unas compuertas"); tl = T("se llena") + 0.6
    abre = [seg(t, tc, tc + 0.5) * (1 - seg(t, tl, tl + 0.4)), seg(t, tl, tl + 0.5) * (1 - seg(t, T("cuando pasa"), T("cuando pasa") + 0.5))]
    for k, (c, x) in enumerate(zip(S["comp"], (-2.1, 2.1))):
        c.location = (x, YF + 0.16, ZT + 0.33 * abre[k]) if tun > 0.5 else LEJOS
    # agua del túnel y flechas
    flujo = None
    if tc < t < tl: flujo = -1
    elif tl < t < T("cuando pasa"): flujo = 1
    if flujo: setbox(S["tun_agua"], -3.3, 3.3, YF + 0.002, YF + 0.12, ZT - RT + 0.02, ZT - 0.02)
    else: S["tun_agua"].location = LEJOS
    for k, f in enumerate(S["ftun"]):
        if flujo:
            u = (t * 0.7 + k * 0.5) % 1.0; x = flujo * (0.6 + 1.6 * u)
            f.location = (x, YF - 0.05, ZT); f.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(Vector((flujo, 0, 0)))
        else: f.location = LEJOS
    # agua de la calle
    lc = 0.012 + 0.03 * seg(t, T("cuando cae"), T("pero las alcantarillas", fin=True))
    lc = mix(lc, 0.01, seg(t, T("el agua de la"), T("el agua de la") + 2.0))
    lc = mix(lc, 0.0, seg(t, T("cuando pasa"), T("cuando pasa") + 1.0)) + 0.015 * seg(t, T("pídelo"), T("pídelo") + 1.5)
    if lc > 0.003: setbox(S["calle_agua"], -5.2, 5.2, -3.82, -2.98, 0.04, 0.045 + lc)
    else: S["calle_agua"].location = LEJOS
    for k, f in enumerate(S["fcalle"]):
        if lc > 0.008 and not (T("así que cavas") < t < T("cuando llueve")) and not (T("hoy barcelona") - 0.3 < t < T("y en dos mil")):
            u = (t * 0.22 + k / 3) % 1.0; f.location = (mix(-4.5, 4.8, u), -3.4, 0.12 + lc)
            f.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(Vector((1, 0, -0.05)))
            f.scale = (1 + 0.6 * seg(t, T("cuando cae"), T("el agua baja", fin=True)),) * 3
        else: f.location = LEJOS
    # alcantarilla: se llena con la tormenta y desborda por las tapas
    la = 0.06 + 0.24 * seg(t, T("cuando cae"), T("no dan abasto", fin=True))
    la = mix(la, 0.14, seg(t, T("el agua de la"), T("el agua de la") + 2.0))
    la = mix(la, 0.2, seg(t, T("el agua sale poco"), T("el agua sale poco") + 0.6))
    la = mix(la, 0.05, seg(t, T("así no se"), T("hoy barcelona")))
    setbox(S["alc_agua"], -6.5, 6.5, YF + 0.002, YF + 0.13, ZS - RS + 0.02, ZS - RS + 0.02 + la)
    for k, f in enumerate(S["falc"]):
        on = la > 0.1 and t < T("así no se", fin=True)
        if on:
            u = (t * 0.35 + k / 3) % 1.0; f.location = (mix(-5.5, 5.5, u), YF - 0.05, ZS); f.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(Vector((1, 0, 0)))
        else: f.location = LEJOS
    # tapas que saltan y chorros
    ts = T("y el agua sale"); te = T("así que cavas") + 0.3
    for k, (tp, ch, x) in enumerate(zip(S["tapas"], S["chorros"], TAPAS)):
        a = ts + 0.2 * k
        if a < t < te:
            hch = 0.5 * seg(t, a, a + 0.3) * (1 - seg(t, te - 0.5, te)) * (1 + 0.15 * math.sin(t * 17 + k))
            tp.location = (x, -3.62, 0.05 + hch + 0.03); tp.rotation_euler = (0.3 * math.sin(t * 9 + k), 0.3 * math.cos(t * 7 + k), 0)
            ch.location = (x, -3.62, 0.05 + hch / 2); ch.scale = (1, 1, max(hch, 0.001))
        else:
            tp.location = (x, -3.62, 0.05); tp.rotation_euler = (0, 0, 0); ch.location = LEJOS
    # chorro de la bajada al depósito A
    lv = nivel(t, "A"); z0A = DEP["A"][2] + 0.08 + (DEP["A"][3] - DEP["A"][2] - 0.16) * lv
    llenando = T("el agua de la") - 0.2 < t < T("pero uno solo") or T("pídelo") < t
    if llenando and construido(t, "A") > 0.9:
        setbox(S["chorro"], XDROP - 0.06, XDROP + 0.06, YF + 0.002, YF + 0.08, z0A, -0.42)
        S["fdrop"].location = (XDROP + 0.0, YF - 0.06, -0.6 - 0.25 * ((t * 1.2) % 1.0)); S["fdrop"].rotation_quaternion = Vector((0, 0, 1)).rotation_difference(Vector((0, 0, -1)))
    else: S["chorro"].location = LEJOS; S["fdrop"].location = LEJOS
    # sensores que parpadean
    for k, s in enumerate(S["sens"]):
        on = T("sensores") - 0.1 < t < T("cuando pasa")
        set_color(s, (0.2, 0.95, 0.35) if on and math.sin(t * 10 + k * 2) > -0.2 else ((1.0, 0.25, 0.2) if on else (0.4, 0.4, 0.4)))
    # depuradora: el agua sale hacia ella y luego al mar
    for k, f in enumerate(S["fdep"]):
        if T("el agua sale poco") < t < T("hoy barcelona"):
            u = (t * 0.6 + k * 0.5) % 1.0
            if k == 0: f.location = (mix(4.3, 5.6, u), YF - 0.05, ZS); f.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(Vector((1, 0, 0)))
            else: f.location = (mix(5.4, 6.3, u), -2.0, 0.35); f.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(Vector((1, 0, 0)))
        else: f.location = LEJOS
    # coches
    for k, c in enumerate(S["coches"]):
        if T("hoy barcelona") - 0.3 < t < T("y en dos mil"): c.location = LEJOS; continue
        u = (t * 0.07 + k * 0.37) % 1.0; c.location = (mix(-4.8, 5.0, u), -3.68 if k % 2 == 0 else -3.12, 0.05)
        c.rotation_euler.z = 0 if k % 2 == 0 else 0
    # chinchetas de los 15 depósitos
    th = T("hoy barcelona")
    for k, e in enumerate(S["pins"]):
        a = th + 0.12 * k; g = seg(t, a, a + 0.25) * (1 - seg(t, T("unas ciento") - 0.3, T("unas ciento")))
        if g < 0.02: e.location = LEJOS
        else: x, yy = e["p"]; e.location = (x, yy, 0.0 + 0.04 * math.sin(t * 4 + k)); e.scale = (g, g, g)
    # la ciudad se aplasta y salen 190 piscinas
    tp0 = T("unas ciento"); tp1 = T("y en dos mil") - 0.2
    aplasta = seg(t, tp0 - 0.3, tp0 + 0.3) * (1 - seg(t, tp1, tp1 + 0.5))
    S["ciudad"].scale = (1, 1, max(1 - aplasta, 0.001))
    for o in S["pis"]:
        a = tp0 + 0.12 * o["i"] * 0.18; g = seg(t, a, a + 0.25) * (1 - seg(t, tp1, tp1 + 0.4))
        if g < 0.02: o.location = LEJOS
        else: x, yy = o["p"]; o.location = (x, yy, 0.03); o.scale = (g * 0.44, g * 0.27, 0.05)
    # lluvia
    rnd = random.Random(3); on = llueve(t)
    camp = S["cam"].location
    for k, b in enumerate(S["lluvia"]):
        x0 = rnd.uniform(-5.5, 5.5); y0 = rnd.uniform(-4.0, 3.0)
        if k < 30: x0 = camp.x * 0.0 + rnd.uniform(-2.5, 2.5) + (S["cam_tgt"].x if "cam_tgt" in S else 0); y0 = rnd.uniform(-3.9, -1.5)
        if on:
            z = 3.2 - ((t * 1.6 + k / 70) % 1.0) * 3.2
            bar_set(b, (x0, y0, z + 0.25), (x0, y0, z))
        else: bar_set(b, LEJOS, Vector(LEJOS) + Vector((0, 0, 0.01)))
    pos, tgt, lens = cam_lin(t, CAM(), drift=0.02); S["cam_tgt"] = Vector(tgt)
    apply_cam(S["cam"], pos, tgt, lens)

_CK = None
def CAM():
    global _CK
    if _CK: return _CK
    k = Claves(); add = k.add
    ini = V((-0.6, -3.4, 0.15), (1.5, -2.5, 0.85), 34)
    add(0.0, ini)
    add(1.4, V((0.2, -3.4, 0.12), (1.3, -2.4, 0.75), 35))
    add(T("y el agua corre"), V((1.8, -3.4, 0.1), (-1.2, -2.4, 0.8), 36))
    add(T("cuánta agua"), V((0.5, -2.0, 0.3), (0.6, -6.5, 3.4), 32))
    add(T("escribe"), V((0.0, -1.5, 0.3), (-1.5, -8.0, 4.5), 30))
    add(T("barcelona está"), V((0.0, 0.5, 0.3), (-1.5, -13.0, 9.5), 22))
    add(T("barcelona está") + 1.4, V((0.0, 0.5, 0.3), (1.5, -12.5, 9.0), 23))
    add(T("cuando cae"), V((-1.0, -1.6, 0.3), (-5.2, -4.6, 3.4), 32))
    add(T("el agua baja"), V((0.5, -3.4, 0.1), (-3.5, -3.0, 1.5), 34))
    add(T("pero las alcantarillas"), V((0.8, -3.95, -0.3), (0.3, -3.0, 0.7), 40))
    add(T("pero las alcantarillas") + 1.3, V((-0.4, -3.95, -0.3), (-0.4, -3.1, 0.8), 40))
    add(T("y el agua sale"), V((0.8, -3.6, 0.2), (0.6, -2.7, 1.1), 38))
    add(T("así que cavas"), V((0.0, -3.0, -0.9), (0.0, -7.5, 1.8), 32))
    add(T("así que cavas") + 1.6, V((0.0, -3.0, -0.9), (1.5, -6.5, 1.2), 33))
    add(T("enterrada"), V((0.0, -3.0, -1.4), (-0.8, -3.8, 0.3), 36))
    add(T("cuando llueve"), V((-1.0, -3.4, -0.4), (1.2, -4.5, 1.4), 36))
    add(T("el agua de la"), V((-0.8, -3.5, -1.2), (0.6, -3.5, 0.3), 40))
    add(T("el depósito joan"), V((0.0, -3.0, -1.0), (-1.2, -6.0, 1.2), 34))
    add(T("guarda cincuenta"), V((0.0, -3.0, -1.0), (1.4, -5.5, 0.6), 36))
    add(T("pero uno solo"), V((0.0, -2.0, -0.5), (0.0, -12.0, 4.5), 30))
    add(T("así que construyes"), V((0.0, -3.5, -1.3), (0.5, -10.0, 1.0), 30))
    add(T("y los conectas"), V((-2.4, -3.9, -1.6), (0.8, -3.2, 0.4), 40))
    add(T("sensores"), V((0.5, -3.95, -0.33), (-0.7, -2.2, 0.08), 42))
    add(T("sensores") + 1.5, V((0.6, -3.95, -0.33), (0.9, -2.4, 0.06), 38))
    add(T("y unas compuertas"), V((-2.1, -3.9, -1.7), (-0.6, -2.6, 0.4), 42))
    add(T("se llena") + 0.4, V((1.0, -3.6, -1.4), (0.5, -7.0, 0.8), 32))
    add(T("cuando pasa"), V((0.0, -1.0, 0.0), (1.0, -11.0, 6.0), 30))
    add(T("el agua sale poco"), V((4.6, -2.5, -0.3), (-1.6, -5.0, 2.2), 34))
    add(T("así no se"), V((0.0, -3.0, -1.0), (-1.0, -9.0, 2.0), 30))
    add(T("hoy barcelona"), V((0.5, 0.5, 0.0), (0.0, -10.0, 10.0), 30))
    add(T("juntos guardan"), V((0.5, 0.5, 0.0), (2.0, -9.0, 9.0), 32))
    add(T("cuatrocientos") + 1.0, V((0.5, 0.3, 0.0), (0.5, -9.5, 8.0), 31))
    add(T("unas ciento"), V((0.3, 0.4, 0.0), (-1.5, -9.0, 7.0), 32))
    add(T("unas ciento") + 1.8, V((0.3, 0.4, 0.0), (1.5, -8.0, 6.0), 34))
    add(T("y en dos mil"), V((5.4, -3.6, -1.4), (-1.5, -5.0, 1.0), 34))
    add(T("de sesenta"), V((5.0, -3.6, -1.4), (-0.5, -4.0, 0.6), 38))
    add(T("te has"), V((0.0, -2.0, -0.6), (0.0, -11.0, 4.0), 30))
    add(T("dime en"), V((0.0, 0.0, 0.0), (-2.0, -12.0, 7.0), 30))
    add(T("dime en") + 1.6, V((0.0, 0.0, 0.0), (1.5, -12.0, 6.0), 30))
    add(T("y si quieres"), V((0.0, -3.0, -1.0), (1.2, -7.0, 1.6), 32))
    add(T("pídelo"), V((-1.0, -1.5, 0.3), (-4.0, -5.0, 3.0), 32))
    add(T("lo más"), V((0.5, -3.2, 0.2), (-2.5, -3.5, 1.5), 34))
    add(T("sígueme"), ini)
    add(DUR + 1, ini)
    _CK = k.k
    return _CK

def anchors(sc, S, t):
    cam = S["cam"]; P = lambda v: proj(sc, cam, v)
    return {"calle": P((0.3, -3.4, 0.3)), "alc": P((0.0, YF, ZS + 0.1)), "tapa": P((0.8, -3.62, 0.4)), "depA": P((0.0, YF, -0.6)),
            "depB": P((-3.3, YF, -0.75)), "depC": P((3.3, YF, -0.75)), "depD": P((5.4, YF, -0.85)), "tunel": P((-2.1, YF, ZT + 0.2)),
            "sens": P((0.5, YF, -0.15)), "depura": P((5.2, -2.0, 0.6)), "ciudad": P((0.5, 0.4, 1.8)), "parque": P((0.0, -2.0, 0.6))}

if __name__ == "__main__":
    run("bcnpluvial", build, pose, anchors)
