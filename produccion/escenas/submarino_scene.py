# «Si tuvieras que inventar un submarino»: maqueta de mar en corte (bloque de agua transparente sobre un fondo de arena)
# con el submarino abierto por la mitad: casco exterior, casco resistente con la tripulación, tanques de lastre a proa y popa,
# compuertas abajo y válvulas arriba, tanques de trimado, aletas, hélice y botellas de aire comprimido.
# Planos (fotografía → motion): 0 inmersión cerca (libre: arriba) · 5 superficie · 6,5 flechas peso/empuje · 12 tanques ·
# 13,6 compuertas · 16 válvulas · 19,7 baja · 22 presión · 27 profundo · 29,6 casco resistente · 33 flechas radiales ·
# 38 trimado · 46 aletas · 50 hélice · 53 botellas · 55 tanques vaciándose · 58 sube · 62 soplido · 65 vuelta al principio.
import bpy, bmesh, math, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from maqueta import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("submarino")
HULL = (0.32, 0.36, 0.42); PRES = (0.55, 0.58, 0.64); SAIL = (0.28, 0.31, 0.37); WATER = PAL["agua"]; AIR = (1.0, 1.0, 1.0)
BOT = (0.3, 0.75, 0.45); SAND = (0.93, 0.82, 0.55); SAND2 = (0.82, 0.68, 0.42); SKIN = (0.95, 0.75, 0.6); SHIRT = (0.95, 0.5, 0.2)
ZS = -0.12   # submarino en superficie
ZD = -3.3    # submarino profundo

def media_rev(prof, g, color, ns=16, corte=None):
    """Mitad trasera (y ≥ 0) de un sólido de revolución alrededor del eje X, hueco, con las caras cortadas en crema."""
    me = bpy.data.meshes.new("rev"); bm = bmesh.new(); an = []
    for x, r in prof:
        ri = max(r - g, 0.002); o, i = [], []
        for k in range(ns + 1):
            a = math.pi * k / ns; c, s = math.cos(a), math.sin(a)
            o.append(bm.verts.new((x, r * s, r * c))); i.append(bm.verts.new((x, ri * s, ri * c)))
        an.append((o, i))
    cc = []
    for j in range(len(an) - 1):
        (o0, i0), (o1, i1) = an[j], an[j + 1]
        for k in range(ns):
            bm.faces.new((o0[k], o1[k], o1[k + 1], o0[k + 1])); bm.faces.new((i0[k], i0[k + 1], i1[k + 1], i1[k]))
        for k in (0, ns): cc.append(bm.faces.new((o0[k], o1[k], i1[k], i0[k])))
    for f in cc: f.material_index = 1
    bm.normal_update(); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new("rev", me); bpy.context.collection.objects.link(ob)
    ob.data.materials.append(mat(color)); ob.data.materials.append(mat(corte or PAL["corte"]))
    for p in ob.data.polygons: p.use_smooth = True
    return ob

def transp(o, a):
    m = o.active_material; m.diffuse_color = (*m.diffuse_color[:3], a)
    try: m.surface_render_method = 'BLENDED'
    except Exception: pass

# ---------------- movimiento del submarino ----------------
def subz(t):
    if t < T("vamos a"): return mix(-0.7, -1.7, seg(t, 0, T("vamos a")))
    z = ZS + 0.02 * math.sin(t * 1.6)
    z = mix(z, -1.5, seg(t, T("y baja") - 0.2, T("más aprieta", fin=True)))
    z = mix(z, ZD, seg(t, T("más aprieta", fin=True), T("son treinta", fin=True)))
    z = mix(z, ZS + 0.02 * math.sin(t * 1.6), seg(t, T("y sube solo") - 0.4, T("como un corcho", fin=True)))
    return z

def subx(t):
    x = 0.0
    x = mix(x, 0.7, seg(t, T("para inclinarlo"), T("y aquí viene")))
    x = mix(x, 0.0, seg(t, T("y aquí viene"), T("para subir")))
    return x

def lastre(t):
    if t < T("vamos a"): return mix(0.35, 1.0, seg(t, 0, 3.0))
    v = seg(t, T("abres unas"), T("y el aire sale", fin=True))
    return v * (1 - 0.92 * seg(t, T("el aire empuja"), T("hacia fuera", fin=True)))

def trim(t):
    """nivel de los tanques de trimado (delante, detrás)"""
    f = 0.5
    f = mix(f, 0.85, seg(t, T("y mueves"), T("delante", fin=True)))
    f = mix(f, 0.2, seg(t, T("detrás") - 0.2, T("detrás", fin=True) + 0.1))
    f = mix(f, 0.5, seg(t, T("hasta que"), T("ni baja", fin=True)))
    return f, 1 - f

def cabeceo(t):
    if t < T("vamos a"): return 0.16 * seg(t, 0, 1.5)
    f, b = trim(t)
    p = 0.35 * (f - b)
    p += -0.14 * seg(t, T("para inclinarlo") - 0.3, T("para inclinarlo") + 0.5) * (1 - seg(t, T("y aquí viene"), T("y aquí viene") + 0.6))
    p += -0.1 * seg(t, T("y sube solo") - 0.6, T("y sube solo")) * (1 - seg(t, T("como un corcho"), T("por eso")))
    return p

def subp(t): return Vector((subx(t), 0, subz(t)))

def build():
    sc, cam = scene_setup(world=PAL["cielo"], shadow=0.22); entorno_claro(sc)
    S = {"cam": cam}
    nubes(9, (0, 9, 3.2), 9, 1.2, 1.0, s=1.1, seed=5)
    # fondo de arena y bloque de mar transparente
    isla(11, 4.4, (0, 0.8, -5.0), capas=[(SAND, 0.15), (SAND2, 0.4), (PAL["tierra"], 0.5)])
    for k, (x, y) in enumerate(((-3.5, 1.8), (3.8, 2.2), (-1.5, 2.6), (2.0, 1.4))):
        sph(0.25 + 0.08 * k, (x, y, -4.95), (0.6, 0.6, 0.62), scale=(1.3, 1, 0.7), seg=8)
        for j in range(3):
            o = bar_obj(PAL["planta"], 0.03); bar_set(o, (x + 0.3 + 0.1 * j, y, -4.9), (x + 0.35 + 0.15 * j, y, -4.2 - 0.15 * j))
    S["mar"] = box((11, 4.4, 5.0), (0, 0.8, -2.5), WATER, unique=True)
    S["sup"] = box((11, 4.4, 0.03), (0, 0.8, -0.015), (0.3, 0.58, 0.9), unique=True)
    # submarino (padre que se mueve)
    S["sub"] = empty((0, 0, ZS)); sub = S["sub"]
    prof = [(1.32, 0.02), (1.3, 0.1), (1.24, 0.18), (1.12, 0.25), (0.95, 0.29), (0.75, 0.3), (-0.6, 0.3), (-0.85, 0.27),
            (-1.05, 0.2), (-1.2, 0.12), (-1.28, 0.05)]
    media_rev(prof, 0.025, HULL).parent = sub
    pres = [(0.64, 0.002), (0.62, 0.09), (0.57, 0.16), (0.5, 0.2), (-0.5, 0.2), (-0.57, 0.16), (-0.62, 0.09), (-0.64, 0.002)]
    S["pres"] = media_rev(pres, 0.05, PRES); S["pres"].parent = sub
    S["pres"].data.materials[0] = mat(PRES, unique=True)
    # mamparos de los tanques de lastre
    for x in (1.02, -0.92): box((0.025, 0.5, 0.5), (x, 0.13, 0), PAL["corte"], parent=sub)
    # agua dentro de los tanques de lastre (proa y popa)
    S["tq"] = [box((0.34, 0.2, 1.0), (0.83, 0.11, 0), WATER, parent=sub, unique=True),
               box((0.26, 0.2, 1.0), (-0.77, 0.11, 0), WATER, parent=sub, unique=True)]
    # compuertas (abajo) y válvulas (arriba)
    S["comp"] = []
    for x in (0.83, -0.77):
        e = empty((x, 0.0, -0.29), sub); box((0.14, 0.12, 0.015), (0.07, 0, 0), (0.9, 0.3, 0.25), parent=e); S["comp"].append(e)
        cyl(0.03, 0.06, (x, 0.04, 0.3), (0.9, 0.3, 0.25), parent=sub)
    # vela, aletas y hélice
    box((0.42, 0.12, 0.3), (0.35, 0.06, 0.42), SAIL, parent=sub)
    box((0.3, 0.06, 0.05), (0.35, 0.06, 0.62), SAIL, parent=sub)
    cyl(0.015, 0.25, (0.4, 0.04, 0.68), (0.7, 0.7, 0.72), parent=sub)
    S["aletas"] = []
    for x, w in ((0.35, 0.5), (-1.05, 0.62)):
        e = empty((x, 0.0, 0.42 if x > 0 else 0.0), sub); box((0.16, w, 0.02), (0, 0, 0), SAIL, parent=e); S["aletas"].append(e)
    box((0.18, 0.02, 0.4), (-1.08, 0.0, 0.0), SAIL, parent=sub)
    S["helice"] = empty((-1.33, 0.0, 0.0), sub)
    cyl(0.04, 0.08, (0, 0, 0), (0.85, 0.7, 0.3), parent=S["helice"], rot=(0, math.pi / 2, 0))
    for k in range(3):
        b = box((0.02, 0.05, 0.16), (0, 0, 0.08), (0.95, 0.78, 0.3), parent=S["helice"])
        b.location = (0, 0.08 * math.sin(k * 2.094), 0.08 * math.cos(k * 2.094)); b.rotation_euler = (-k * 2.094, 0, 0)
    # tripulación
    for x in (-0.25, 0.15):
        cyl(0.04, 0.12, (x, 0.08, -0.08), SHIRT, parent=sub); sph(0.035, (x, 0.08, 0.02), SKIN, parent=sub)
    box((1.0, 0.25, 0.02), (0, 0.12, -0.15), (0.75, 0.6, 0.4), parent=sub)
    # tanques de trimado y tubo entre ellos
    S["trim"] = []
    for x in (0.4, -0.4):
        box((0.16, 0.14, 0.012), (x, 0.08, -0.08), PAL["corte"], parent=sub)
        S["trim"].append(box((0.14, 0.12, 1.0), (x, 0.08, -0.13), WATER, parent=sub, unique=True))
    S["trimcaja"] = [box((0.16, 0.02, 0.12), (x, 0.15, -0.12), (0.7, 0.72, 0.76), parent=sub) for x in (0.4, -0.4)]
    o = bar_obj((0.7, 0.72, 0.76), 0.012); o.parent = sub; bar_set(o, (-0.4, 0.1, -0.18), (0.4, 0.1, -0.18))
    # botellas de aire comprimido
    S["bot"] = empty(LEJOS, sub)
    for k in range(3):
        cyl(0.03, 0.34, (0, 0.06 * k, 0.0), BOT, parent=S["bot"], rot=(0, math.pi / 2, 0))
        sph(0.03, (0.17, 0.06 * k, 0), BOT, parent=S["bot"])
    # partículas (en coordenadas del mundo)
    S["pw"] = [sph(0.025, LEJOS, WATER, seg=8) for _ in range(16)]
    S["pa"] = [sph(0.03, LEJOS, AIR, seg=8) for _ in range(18)]
    S["pt"] = [sph(0.016, LEJOS, WATER, seg=8) for _ in range(6)]
    S["spray"] = [sph(0.06, LEJOS, AIR, seg=8) for _ in range(16)]
    # flechas: peso, empuje y presión
    S["peso"] = flecha3d(LEJOS, (0, 0, -1), 0.7, 0.05)
    S["empuje"] = flecha3d(LEJOS, (0, 0, 1), 0.7, 0.05, color=(0.2, 0.55, 0.95))
    S["pres_fl"] = []
    for k in range(8):
        a = k / 8 * math.tau; d = Vector((math.cos(a), 0, math.sin(a)))
        S["pres_fl"].append((flecha3d(LEJOS, -d, 0.35, 0.03), d))
    dyn = [cam, S["mar"], S["sup"], sub, S["pw"], S["pa"], S["pt"], S["spray"], S["peso"], S["empuje"]] + [f for f, _ in S["pres_fl"]]
    join_static(dyn)
    transp(S["mar"], 0.22); transp(S["sup"], 0.45)
    return sc, S

def mundo(t, local):
    """punto local del submarino → mundo"""
    p = cabeceo(t); x, y, z = local
    return subp(t) + Vector((x * math.cos(p) + z * math.sin(p), y, -x * math.sin(p) + z * math.cos(p)))

def pose(t, S):
    sub = S["sub"]; sub.location = subp(t); sub.rotation_euler = (0, cabeceo(t), 0)
    lv = lastre(t)
    for tq, (x, h) in zip(S["tq"], ((0.83, 0.5), (-0.77, 0.5))):
        hh = max(lv * h, 0.002); tq.scale.z = hh; tq.location.z = -0.25 + hh / 2
    llenando = t < T("vamos a") or T("abres unas") < t < T("el submarino pesa")
    vaciando = T("el aire empuja") - 0.2 < t < T("el submarino pesa menos")
    for e in S["comp"]: e.rotation_euler.y = 1.1 if (llenando or vaciando) else 0.0
    # trimado
    vis_trim = t > T("tanques pequeños") - 0.3
    for o, n, c in zip(S["trim"], trim(t), S["trimcaja"]):
        h = max(0.1 * n, 0.002) if vis_trim else 0.002; o.scale.z = h; o.location.z = -0.18 + h / 2
    set_color(S["pres"], (0.95, 0.62, 0.2) if T("así que el casco") < t < T("un tubo redondo") + 1.0 else PRES)
    # aletas y hélice
    fa = 0.0
    if T("y aletas") < t < T("y aquí viene"): fa = 0.35 * math.sin((t - T("y aletas")) * 3)
    for e in S["aletas"]: e.rotation_euler.y = fa
    S["helice"].rotation_euler.x = t * (14 if T("y aletas") < t < T("y aquí viene") + 0.5 else 4)
    # botellas
    S["bot"].location = (-0.17, 0.05, 0.08) if t > T("abres botellas") - 0.2 else LEJOS
    S["bot"].scale = (seg(t, T("abres botellas") - 0.2, T("abres botellas") + 0.2) + 0.001,) * 3
    # agua que entra / sale por las compuertas
    for k, p in enumerate(S["pw"]):
        u = (k / len(S["pw"]) + t * 1.3) % 1.0; x = 0.83 if k % 2 == 0 else -0.77
        if llenando: p.location = mundo(t, (x + 0.05 * math.sin(k), -0.05, -0.75 + 0.6 * u))
        elif vaciando: p.location = mundo(t, (x + 0.05 * math.sin(k), -0.05, -0.3 - 0.6 * u))
        else: p.location = LEJOS
    # aire que sale por arriba al llenar / burbujas que suben
    for k, p in enumerate(S["pa"]):
        u = (k / len(S["pa"]) + t * 0.8) % 1.0; x = 0.83 if k % 2 == 0 else -0.77
        if llenando and (t < T("vamos a") or t > T("y el aire") - 0.3):
            q = mundo(t, (x, -0.05, 0.32)); p.location = q + Vector((0.05 * math.sin(t * 5 + k), 0, u * max(0.8, -q.z + 0.1)))
        elif vaciando:
            # de las botellas a los tanques
            dst = (x, -0.04, 0.15); src = (-0.0, -0.04, 0.08)
            p.location = mundo(t, tuple(Vector(src).lerp(Vector(dst), u)))
        else: p.location = LEJOS
    for k, p in enumerate(S["pt"]):
        if T("y mueves") < t < T("hasta que"):
            u = (k / 6 + t * 1.2) % 1.0; d = 1 if t < T("detrás") - 0.2 else -1
            p.location = mundo(t, (-0.4 * d + 0.8 * d * u, 0.05, -0.18))
        else: p.location = LEJOS
    # soplido al salir
    for k, p in enumerate(S["spray"]):
        ts = T("suena ese")
        if ts - 0.3 < t < ts + 2.2:
            u = ((t - ts) * 0.9 + k / len(S["spray"])) % 1.0; x = 0.83 if k % 2 == 0 else -0.77
            q = mundo(t, (x, -0.02, 0.32)); p.location = q + Vector((0.25 * math.sin(k * 2.3) * u, -0.1 * math.cos(k), 1.1 * u))
            p.scale = ((1.2 - u) * 1.5,) * 3
        else: p.location = LEJOS
    # flechas de peso y empuje
    c = subp(t)
    fu = (T("un barco flota") - 0.2 < t < T("tienes que hacerlo", fin=True) + 0.1) or (T("el submarino pesa más") - 0.2 < t < T("y baja", fin=True) + 0.5) \
         or (T("el submarino pesa menos") - 0.2 < t < T("como un corcho", fin=True))
    if fu:
        pesado = T("el submarino pesa más") - 0.2 < t < T("y baja", fin=True) + 0.5 or (T("tienes que") < t < T("tienes que hacerlo", fin=True) + 0.1)
        lig = T("el submarino pesa menos") - 0.2 < t
        S["peso"].location = c + Vector((0.1, -0.45, -0.32)); S["peso"].scale = ((1.5 if pesado else 1.0),) * 3
        S["empuje"].location = c + Vector((-0.1, -0.45, 0.35)); S["empuje"].scale = ((1.5 if lig else (0.8 if pesado else 1.15)),) * 3
    else:
        S["peso"].location = LEJOS; S["empuje"].location = LEJOS
    # presión del agua (crece con la profundidad)
    pv = (T("pero cuanto") - 0.2 < t < T("así que el casco")) or (T("un tubo redondo") - 0.1 < t < T("ahora") + 0.3)
    prof = max(0.0, (-subz(t) - 0.1) / (-ZD - 0.1))
    for k, (f, d) in enumerate(S["pres_fl"]):
        if pv:
            s = 0.6 + 1.0 * prof + 0.1 * math.sin(t * 8 + k)
            R = 1.0 / math.sqrt((d.x / 1.34) ** 2 + (d.z / 0.34) ** 2)
            f.location = c + d * (R + 0.35 * s + 0.03) + Vector((0, -0.42, 0))
            f.scale = (s,) * 3
        else: f.location = LEJOS
    apply_cam(S["cam"], *cam_lin(t, CAM()))

def CAM():
    k = Claves(); add = k.add
    def sv(t, off=(0, 0, 0), o=(0, -3, 0.5), lens=35):
        return V(tuple(subp(t) + Vector(off)), o, lens)
    add(0.0, sv(0.0, (0.2, 0, 0), (0.8, -3.0, 0.5), 35))
    add(1.8, sv(1.8, (0.1, 0, 0), (-0.6, -2.9, 0.3), 35))
    add(T("y vuelve") , sv(3.6, (0, 0, 0), (1.0, -4.3, 1.1), 32))
    add(T("vamos a") + 0.1, V((0, 0, 0.1), (1.4, -5.4, 1.6), 32), 1.0)
    add(T("un barco flota") + 0.2, V((0, 0, -0.2), (0.0, -5.2, 0.3), 32), 1.0)
    add(T("para hundirlo"), V((0, 0, -0.1), (-1.0, -3.6, 0.6), 34))
    add(T("así que le pones"), V((0.8, 0, 0.0), (0.3, -1.9, 0.3), 38), 0.6)
    add(T("abres unas"), V((0.8, 0, -0.3), (0.2, -1.7, -0.45), 38), 0.8)
    add(T("y el aire sale"), V((0.8, 0, 0.2), (0.1, -1.7, 0.45), 38), 0.6)
    add(T("el submarino pesa más"), V((0, 0, -0.1), (0.9, -5.0, 0.7), 33))
    add(T("y baja"), V((0, 0, -0.5), (-0.5, -3.8, 0.6), 33))
    add(T("pero cuanto") + 0.6, sv(T("más aprieta"), (0, 0, 0), (0.5, -3.6, 0.4), 33))
    add(T("cada diez"), sv(T("cada diez"), (0, 0, 0), (-0.8, -3.2, -0.2), 34))
    add(T("la presión sube"), sv(T("la presión sube"), (0, 0, 0), (0.6, -2.8, 0.6), 35))
    add(T("a trescientos"), sv(T("son treinta"), (0, 0, 0.4), (1.5, -5.6, 0.9), 30))
    add(T("así que el casco"), sv(T("así que el casco"), (0, 0, 0), (0.1, -1.9, 0.2), 40))
    add(T("es un tubo"), sv(T("es un tubo"), (0, 0, 0), (-0.4, -1.7, 0.3), 40))
    add(T("un tubo redondo"), sv(T("un tubo redondo"), (0, 0, 0), (0.0, -3.5, 0.0), 34), 1.0)
    add(T("cómo te quedas"), sv(T("cómo te quedas"), (0, 0, 0), (0.9, -3.4, 0.8), 33))
    add(T("tanques pequeños"), sv(T("tanques pequeños"), (0, 0, -0.1), (0.2, -1.6, 0.2), 40), 0.8)
    add(T("y mueves"), sv(T("y mueves"), (0, 0, -0.1), (0.0, -1.9, 0.3), 40))
    add(T("detrás"), sv(T("detrás"), (0, 0, 0), (0.5, -3.4, 0.3), 34))
    add(T("ni sube"), sv(T("ni sube"), (0, 0, 0), (-0.6, -3.2, 0.5), 34))
    add(T("y aletas"), sv(T("y aletas"), (-0.9, 0, 0), (-0.4, -1.7, 0.4), 38))
    add(T("para inclinarlo"), sv(T("para inclinarlo") + 0.8, (0, 0, 0), (1.0, -3.6, 0.6), 33))
    add(T("y aquí viene"), sv(T("y aquí viene"), (0, 0, 0.3), (-1.2, -4.8, 1.0), 30))
    add(T("ningún motor"), sv(T("ningún motor") + 0.5, (-1.0, 0, 0), (-0.4, -1.7, 0.2), 38))
    add(T("abres botellas"), sv(T("abres botellas"), (-0.1, 0, 0.05), (0.1, -1.6, 0.15), 40), 0.8)
    add(T("el aire empuja"), sv(T("el aire empuja"), (0.8, 0, -0.1), (0.3, -1.9, -0.2), 38))
    add(T("hacia fuera") - 0.2, sv(T("hacia fuera"), (-0.7, 0, -0.1), (-0.3, -1.9, 0.0), 38))
    add(T("el submarino pesa menos"), sv(T("el submarino pesa menos") + 0.6, (0, 0, 0.2), (0.8, -4.3, 0.4), 32))
    add(T("y sube solo"), sv(T("como un corcho"), (0, 0, 0.1), (-0.5, -3.8, 0.6), 33))
    add(T("por eso"), V((0.3, 0, 0.3), (0.8, -3.2, 0.8), 34))
    add(T("suena ese"), V((0.3, 0, 0.5), (0.3, -2.4, 0.6), 36), 0.8)
    add(T("sígueme"), V((0.0, 0, -0.1), (0.8, -3.0, 0.5), 35))
    add(DUR + 1, V((0.0, 0, -0.1), (0.8, -3.0, 0.5), 35))
    return k.k

def anchors(sc, S, t):
    cam = S["cam"]; P = lambda v: proj(sc, cam, tuple(v))
    return {"sub": P(mundo(t, (0, 0, 0.45))), "proa": P(mundo(t, (0.83, 0, 0.25))), "popa": P(mundo(t, (-0.77, 0, 0.25))),
            "compuerta": P(mundo(t, (0.83, 0, -0.32))), "casco": P(mundo(t, (0, 0, 0.2))), "vela": P(mundo(t, (0.35, 0, 0.75))),
            "trimd": P(mundo(t, (0.4, 0, -0.02))), "trimt": P(mundo(t, (-0.4, 0, -0.02))), "aleta": P(mundo(t, (-1.05, 0, 0.1))),
            "bot": P(mundo(t, (0.0, 0, 0.15))), "helice": P(mundo(t, (-1.33, 0, 0.15))), "abajo": P(mundo(t, (0, 0, -0.5)))}

if __name__ == "__main__":
    run("submarino", build, pose, anchors)
