# «Valencia movió un río entero» (Lo que esconde tu ciudad, parte 2): maqueta de Valencia sobre una isla de terreno cortada.
# El parque del antiguo cauce se inunda y vuelve a ser río; riada de 1957 (3.700 m³/s, calles con 5 m de agua); muros que no
# bastan; se excava el cauce nuevo por el sur (12 km, 175 m de ancho); un muro de tierra desvía el agua; carreteras y tren
# cortados y puentes que se levantan uno tras otro; el cauce nuevo traga 5.000 m³/s y casi siempre está seco; el viejo, vacío,
# casi autopista y al final jardín con campos, carril bici y árboles.
# Planos (fotografía → motion): 0 parque+agua (libre: arriba) · 2,8 río · 4 maqueta · 6,7 ciudad · 10,7 lluvia río arriba ·
# 14,6 crecida · 19 ciudad inundada · 20,5 calle (5 m) · 22,8 muros · 27 flecha sur · 30 excavadora · 32 12 km · 33,6 ancho ·
# 38 desvío · 39,8 muro · 42 gira · 43,7 carreteras · 46 puentes · 50 5.000 m³/s · 55 seco · 57,8 cauce viejo · 61 autopista ·
# 64 jardín · 66 campos · 69 paseante · 72,4 vuelta al primer plano.
import bpy, math, sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from modelos import *
from maqueta import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("turia")
BED = (0.86, 0.78, 0.58); BANK = (0.8, 0.8, 0.78); WATER = PAL["agua"]; PLAZA = (0.86, 0.86, 0.84); GRASS = PAL["cesped"]
RIO = [(-6.5, 0.6), (-4.0, 0.6), (-3.5, 0.51), (-2.0, 0.25), (0.0, 0.5), (2.0, 0.15), (4.0, 0.4), (5.7, 0.4)]
NUEVO = [(-4.2, 0.55), (-3.4, -1.2), (-2.2, -2.9), (-0.5, -3.3), (2.0, -3.3), (4.0, -3.0), (5.7, -2.6)]
WR, WN, HB = 0.7, 1.15, 0.15
ROADS = [(-0.9, "road"), (1.2, "road"), (3.0, "tren")]

def yr(x):
    for (x0, y0), (x1, y1) in zip(RIO, RIO[1:]):
        if x0 <= x <= x1: return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return RIO[-1][1]

def dseg(p, a, b):
    p, a, b = Vector(p), Vector(a), Vector(b); d = b - a; u = max(0, min(1, (p - a).dot(d) / d.length_squared))
    return (p - (a + d * u)).length

def strip(o, a, b, w, h, z0=0.0, frac=1.0, off=0.0):
    """coloca una caja unitaria como tira de a a b (ancho w, alto h, base z0), dibujada hasta frac y desplazada off a un lado"""
    a, b = Vector((a[0], a[1], 0)), Vector((b[0], b[1], 0)); d = b - a; L = d.length; n = Vector((-d.y, d.x, 0)) / L
    f = max(0.0, min(1.0, frac))
    if f < 1e-3 or h < 1e-4: o.hide_render = True; return
    o.hide_render = False; Lv = L * f + w * 0.5
    o.location = a + d.normalized() * (Lv / 2 - w * 0.25) + n * off + Vector((0, 0, z0 + h / 2))
    o.rotation_euler = (0, 0, math.atan2(d.y, d.x)); o.scale = (Lv, w, h)

def unit(color, unique=False): return box((1, 1, 1), LEJOS, color, unique=unique)

def cumul(pts):
    L = [0.0]
    for a, b in zip(pts, pts[1:]): L.append(L[-1] + (Vector(b) - Vector(a)).length)
    return L
LN = cumul(NUEVO)
RIO3 = poly([(x, y, 0.06) for x, y in RIO]); NUE3 = poly([(x, y, 0.06) for x, y in NUEVO])

def build():
    sc, cam = scene_setup(world=PAL["cielo"], shadow=0.25); entorno_claro(sc)
    S = {"cam": cam}
    nubes(10, (0, 9, 3.5), 9, 1.5, 1.0, s=1.4, seed=5)
    S["lluvia_nube"] = nube((-5.2, 0.6, 3.2), 1.0, seed=11)
    isla(13.0, 10.0, (0, 0, 0), capas=[(PAL["cesped"], 0.12), (PAL["tierra"], 0.6), (PAL["tierra2"], 0.8)])
    box((0.8, 10.0, 0.05), (6.1, 0, 0.02), WATER)                                   # el mar
    box((7.8, 5.6, 0.01), (0.5, 0.6, 0.005), PLAZA)                                 # suelo de la ciudad
    # edificios (sin pisar el río ni el cauce nuevo)
    rnd = random.Random(7); cols = [PAL["pared"], PAL["rosa"], (0.98, 0.85, 0.55), (0.75, 0.85, 0.95), (0.95, 0.7, 0.5), (0.85, 0.92, 0.8)]
    x = -3.2
    while x < 4.3:
        y = -1.9
        while y < 3.3:
            if abs(y - yr(x)) > 0.8 and all(dseg((x, y), a, b) > 0.95 for a, b in zip(NUEVO, NUEVO[1:])):
                h = rnd.uniform(0.14, 0.42); c = rnd.choice(cols); giro = rnd.choice((0, math.pi / 2, math.pi, -math.pi / 2))
                if h < 0.2: casa((x, y, 0), 0.25, pared=c, rot=giro, plantas=1)
                else: edificio((x, y, 0), pisos=max(2, round(h / 0.105)), s=0.25, color=c, rot=giro, ancho=1.6, fondo=1.6)
            y += 0.55
        x += 0.55
    # cauce viejo: lecho, orillas y agua
    S["rbed"], S["rw"], S["rpark"] = [], [], []
    for a, b in zip(RIO, RIO[1:]):
        o = unit(BED); strip(o, a, b, WR, 0.02, 0.01); S["rbed"].append(o)
        for sd in (-1, 1):
            o = unit(BANK); strip(o, a, b, 0.08, HB, 0.0, off=sd * (WR / 2 + 0.04))
        S["rw"].append(unit(WATER)); S["rpark"].append(unit(GRASS))
    S["muros"] = [unit((0.7, 0.7, 0.72)) for _ in range(2 * (len(RIO) - 3))]
    # parque / jardín: árboles, campo de fútbol y carril bici
    S["arboles"] = []
    for k in range(16):
        xx = -2.9 + k * 0.42; e = empty((xx, yr(xx) + (0.2 if k % 2 else -0.2), 0.03))
        arbol((0, 0, 0), 0.28, parent=e, seed=k)
        S["arboles"].append(e)
    S["campo"] = empty((1.0, yr(1.0), 0.03))
    box((0.55, 0.34, 0.012), (0, 0, 0), (0.35, 0.72, 0.3), parent=S["campo"])
    for xx in (-0.27, 0, 0.27): box((0.012, 0.34, 0.016), (xx, 0, 0), (1, 1, 1), parent=S["campo"])
    for yy in (-0.17, 0.17): box((0.55, 0.012, 0.016), (0, yy, 0), (1, 1, 1), parent=S["campo"])
    S["bici"] = [unit(PAL["rojo"]) for _ in range(len(RIO) - 3)]
    S["autopista"] = [unit(PAL["asfalto"]) for _ in range(len(RIO) - 3)]
    S["rayas"] = [box((0.12, 0.025, 0.012), LEJOS, (1, 1, 1)) for _ in range(18)]
    S["paseante"] = empty(LEJOS)
    persona((0, 0, 0), 0.16, parent=S["paseante"])
    # cauce nuevo (se excava): lecho, orillas, agua
    S["nbed"], S["nbk"], S["nw"] = [], [], []
    for a, b in zip(NUEVO, NUEVO[1:]):
        S["nbed"].append(unit((0.82, 0.8, 0.74))); S["nbk"].append((unit(BANK), unit(BANK))); S["nw"].append(unit(WATER))
    S["muro_tierra"] = unit(PAL["tierra"])
    # excavadora
    S["exc"] = empty(LEJOS)
    box((0.28, 0.18, 0.1), (0, 0, 0.07), PAL["amarillo"], parent=S["exc"]); box((0.12, 0.14, 0.12), (-0.05, 0, 0.18), (0.3, 0.32, 0.36), parent=S["exc"])
    for sy in (-1, 1): box((0.32, 0.05, 0.05), (0, sy * 0.1, 0.02), (0.2, 0.2, 0.22), parent=S["exc"])
    S["brazo"] = empty((0.1, 0, 0.14)); S["brazo"].parent = S["exc"]
    box((0.3, 0.04, 0.04), (0.15, 0, 0), PAL["amarillo"], parent=S["brazo"]); box((0.07, 0.08, 0.07), (0.3, 0, -0.04), (0.3, 0.32, 0.36), parent=S["brazo"])
    # carreteras y vía del tren que cruzan el cauce nuevo
    S["vias_mid"], S["puentes"] = [], []
    for x, tipo in ROADS:
        col = (0.55, 0.42, 0.32) if tipo == "tren" else PAL["asfalto"]
        box((0.26, 1.5, 0.02), (x, -4.25, 0.02), col)
        box((0.26, 1.2, 0.02), (x, -1.95, 0.02), col)
        S["vias_mid"].append(box((0.26, 1.6, 0.02), (x, -3.25, 0.02), col, unique=True))
        pe = empty((x, -3.25, 0)); S["puentes"].append(pe)
        box((0.36, 1.6, 0.06), (0, 0, 0.21), (0.92, 0.92, 0.9), parent=pe)
        for yy in (-0.45, 0.0, 0.45): box((0.1, 0.1, 0.2), (0, yy, 0.09), (0.75, 0.75, 0.75), parent=pe)
        box((0.26, 1.6, 0.012), (0, 0, 0.245), col, parent=pe)
    S["coches"] = [coche(LEJOS, 0.1, color=c, rot=math.pi / 2) for c in (PAL["rojo"], (0.2, 0.45, 0.85), PAL["amarillo"], (0.95, 0.95, 0.95))]
    S["tren"] = [box((0.12, 0.3, 0.1), LEJOS, (0.85, 0.2, 0.2)) for _ in range(3)]
    # riada: agua que cubre la ciudad
    S["inund"] = box((7.6, 5.4, 1.0), LEJOS, WATER, unique=True)
    # lluvia río arriba
    S["lluvia"] = [bar_obj((0.45, 0.65, 0.95), 0.012) for _ in range(24)]
    # flechas de corriente y partículas sobre el agua
    S["fr"] = [flecha3d(LEJOS, (1, 0, 0), 0.5, 0.05) for _ in range(3)]
    S["fn"] = [flecha3d(LEJOS, (1, 0, 0), 0.6, 0.06) for _ in range(3)]
    S["fs"] = flecha3d(LEJOS, (0, -1, 0), 1.6, 0.12)
    S["pr"] = [sph(0.03, LEJOS, (0.85, 0.93, 1.0), seg=8) for _ in range(18)]
    dyn = [cam, S["rbed"], S["rw"], S["rpark"], S["muros"], S["arboles"], S["campo"], S["bici"], S["autopista"], S["rayas"], S["paseante"],
           S["nbed"], [x for p in S["nbk"] for x in p], S["nw"], S["muro_tierra"], S["exc"], S["brazo"], S["vias_mid"], S["puentes"],
           S["coches"], S["tren"], S["inund"], S["lluvia"], S["fr"], S["fn"], S["fs"], S["pr"], S["lluvia_nube"]]
    join_static(dyn)
    return sc, S

# ---------------- estado ----------------
def nivel_viejo(t, aguas_arriba):
    """altura del agua en el cauce viejo"""
    if t < T("que antes"): return mix(0.0, 0.05, seg(t, 0.0, 1.2))
    h = 0.04
    h = mix(h, 0.16, seg(t, T("llegaron"), T("el cauce no", fin=True)))
    h = mix(h, 0.04, seg(t, T("podrías hacer"), T("podrías hacer") + 1.5))
    h = mix(h, 0.08, seg(t, T("pero el agua siempre"), T("pero el agua siempre") + 1.0))
    if not aguas_arriba: h = mix(h, 0.0, seg(t, T("y el agua gira"), T("hacia el nuevo", fin=True)))
    else: h = mix(h, 0.06, seg(t, T("y el agua gira"), T("hacia el nuevo", fin=True)))
    return h

def nivel_nuevo(t):
    h = mix(0.0, 0.07, seg(t, T("y el agua gira"), T("hacia el nuevo", fin=True)))
    h = mix(h, 0.14, seg(t, T("el cauce nuevo traga") - 0.3, T("por segundo", 2, fin=True)))
    h = mix(h, 0.0, seg(t, T("y casi todo"), T("está seco", fin=True)))
    return h

def inundacion(t):
    return mix(0.0, 0.24, seg(t, T("y el agua se metió"), T("más de cinco", fin=True) + 0.4)) * (1 - seg(t, T("podrías hacer"), T("podrías hacer") + 1.2))

def excavado(t): return LN[-1] * seg(t, T("excavas"), T("ancho", fin=True) - 0.3)

def jardin(t): return max(1 - seg(t, T("que antes") - 0.1, T("que antes") + 0.5), seg(t, T("así que hoy"), T("así que hoy") + 1.2))

def pose(t, S):
    up = nivel_viejo(t, True); dn = nivel_viejo(t, False)
    seco_viejo = t > T("hacia el nuevo", fin=True)
    for i, (a, b) in enumerate(zip(RIO, RIO[1:])):
        h = up if i < 2 else dn
        strip(S["rw"][i], a, b, WR, h, 0.02)
    # muros más altos (y luego se quitan)
    hm = 0.22 * seg(t, T("podrías hacer"), T("más altos", fin=True)) * (1 - seg(t, T("así que decides"), T("así que decides") + 0.6))
    for j, (a, b) in enumerate(list(zip(RIO, RIO[1:]))[2:]):
        for sd, o in zip((-1, 1), S["muros"][2 * j:2 * j + 2]): strip(o, a, b, 0.06, hm, HB, off=sd * (WR / 2 + 0.04))
    # parque / jardín en el cauce viejo
    g = jardin(t)
    for i, (a, b) in enumerate(zip(RIO, RIO[1:])):
        strip(S["rpark"][i], a, b, WR - 0.02, 0.025 * g if i >= 2 else 0, 0.02)
    for k, e in enumerate(S["arboles"]):
        gk = g if t < 10 else seg(t, T("así que hoy") + 0.12 * k, T("así que hoy") + 0.12 * k + 0.4)
        e.scale = (max(gk, 0.001),) * 3; e.hide_render = gk < 0.01
        for c in e.children: c.hide_render = gk < 0.01
    gc = seg(t, T("con campos") - 0.2, T("con campos") + 0.3) if t > 10 else g
    S["campo"].location.z = 0.03 if gc > 0.01 else -5
    S["campo"].scale = (max(gc, 0.01),) * 3
    gb = seg(t, T("carriles bici") - 0.2, T("carriles bici") + 0.4) if t > 10 else g
    for j, (a, b) in enumerate(list(zip(RIO, RIO[1:]))[2:]): strip(S["bici"][j], a, b, 0.07, 0.03 * gb, 0.03, off=-0.22)
    ga = seg(t, T("querían"), T("querían") + 0.5) * (1 - seg(t, T("pero los vecinos"), T("pero los vecinos") + 0.5))
    for j, (a, b) in enumerate(list(zip(RIO, RIO[1:]))[2:]): strip(S["autopista"][j], a, b, WR - 0.06, 0.03 * ga, 0.02)
    for k, r in enumerate(S["rayas"]):
        if ga > 0.05:
            xx = -3.2 + k * 0.48; r.location = (xx, yr(xx), 0.06); r.rotation_euler.z = math.atan2(yr(xx + 0.1) - yr(xx), 0.1)
        else: r.location = LEJOS
    # paseante
    if t < T("que antes") or t > T("si has paseado") - 0.2:
        u = (t * 0.25) % 1.0; xx = mix(-1.5, 2.5, u)
        S["paseante"].location = (xx, yr(xx) + 0.1, 0.05 + 0.01 * abs(math.sin(t * 9)))
    else: S["paseante"].location = LEJOS
    # riada en la ciudad
    fl = inundacion(t)
    if fl > 0.005: S["inund"].location = (0.5, 0.6, fl - 0.5)
    else: S["inund"].location = LEJOS
    # lluvia río arriba
    llueve = T("pero en mil") - 0.2 < t < T("llegaron") + 1.0
    S_n = S["lluvia_nube"]
    for o in S_n: o.hide_render = not llueve
    rnd = random.Random(3)
    for k, b in enumerate(S["lluvia"]):
        if llueve:
            x0 = rnd.uniform(-6.2, -4.2); y0 = rnd.uniform(-0.6, 1.8); z = 3.0 - ((t * 2.5 + k / 24) % 1.0) * 2.8
            bar_set(b, (x0, y0, z), (x0, y0, z - 0.3))
        else: bar_set(b, LEJOS, Vector(LEJOS) + Vector((0, 0, 0.01)))
    # flecha hacia el sur («sacarlo de la ciudad»)
    if T("así que decides") < t < T("excavas") + 0.6:
        S["fs"].location = (-1.0, -0.6 - 0.4 * seg(t, T("sacarlo"), T("sacarlo") + 0.8), 0.6); S["fs"].scale = (1, 1, 0.6 + 0.4 * seg(t, T("así que decides"), T("sacarlo")))
    else: S["fs"].location = LEJOS
    # excavación del cauce nuevo
    P = excavado(t)
    for i, (a, b) in enumerate(zip(NUEVO, NUEVO[1:])):
        f = (P - LN[i]) / (LN[i + 1] - LN[i])
        strip(S["nbed"][i], a, b, WN, 0.02, 0.005, frac=f)
        for sd, o in zip((-1, 1), S["nbk"][i]): strip(o, a, b, 0.08, HB, 0.0, frac=f, off=sd * (WN / 2 + 0.04))
        strip(S["nw"][i], a, b, WN, nivel_nuevo(t), 0.02, frac=f)
    if T("excavas") - 0.3 < t < T("pero el agua siempre") + 0.3:
        p = at(NUE3, min(P, largo(NUE3) - 0.01)); q = at(NUE3, min(P + 0.05, largo(NUE3)))
        S["exc"].location = (p.x, p.y, 0.03); S["exc"].rotation_euler.z = math.atan2(q.y - p.y, q.x - p.x)
        S["brazo"].rotation_euler.y = 0.4 * math.sin(t * 8)
    else: S["exc"].location = LEJOS
    # muro de tierra que cierra el cauce viejo
    hmt = 0.3 * seg(t, T("cierras"), T("de tierra", fin=True))
    strip(S["muro_tierra"], (-3.62, 0.53), (-3.38, 0.49), WR + 0.25, hmt, 0.0)
    # carreteras cortadas y puentes
    for k, (x, tipo) in enumerate(ROADS):
        corta = P > LN[3] + (x + 0.5) and t > T("excavas")
        S["vias_mid"][k].hide_render = corta
        tb = T("levantas puentes") + 0.7 * k
        u = seg(t, tb, tb + 0.35)
        S["puentes"][k].location = (x, -3.25, -0.3 * (1 - u)) if u > 0.01 else LEJOS
    for k, c in enumerate(S["coches"]):
        x = ROADS[k % 2][0]
        if t > T("levantas puentes") + 0.7 * (k % 2) + 0.4:
            yy = -4.8 + ((t * 0.5 + k * 0.37) % 1.0) * 3.3; zz = 0.06 + (0.21 if -4.05 < yy < -2.45 else 0.0)
            c.location = (x + (0.06 if k < 2 else -0.06), yy, zz - 0.035)
        else: c.location = LEJOS
    for k, c in enumerate(S["tren"]):
        if t > T("uno tras") + 0.2:
            yy = -4.9 + ((t * 0.45) % 1.0) * 3.6 + k * 0.32; zz = 0.07 + (0.21 if -4.05 < yy < -2.45 else 0.0)
            c.location = (3.0, yy, zz)
        else: c.location = LEJOS
    # flechas de corriente
    cv = (t < T("hacia el nuevo", fin=True))
    for k, f in enumerate(S["fr"]):
        if cv and up > 0.02:
            s = ((k / 3 + t * 0.12) % 1.0) * largo(RIO3); p = at(RIO3, s); q = at(RIO3, s + 0.1)
            if not (t > T("y el agua gira") and p.x > -3.5):
                f.location = (p.x, p.y, 0.12 + up); f.rotation_quaternion = Vector((0, 0, 1)).rotation_difference((q - p).normalized())
                sc = 1.0 + 0.8 * seg(t, T("llegaron"), T("por segundo", fin=True)) * (1 - seg(t, T("podrías"), T("podrías") + 1))
                f.scale = (sc,) * 3; continue
        f.location = LEJOS
    hn = nivel_nuevo(t)
    for k, f in enumerate(S["fn"]):
        if hn > 0.02:
            s = ((k / 3 + t * 0.12) % 1.0) * largo(NUE3); p = at(NUE3, s); q = at(NUE3, s + 0.1)
            f.location = (p.x, p.y, 0.12 + hn); f.rotation_quaternion = Vector((0, 0, 1)).rotation_difference((q - p).normalized())
            f.scale = (1 + 4 * max(0, hn - 0.07),) * 3
        else: f.location = LEJOS
    for k, p in enumerate(S["pr"]):
        if cv and k < 12 and up > 0.02:
            s = ((k / 12 + t * 0.09) % 1.0) * largo(RIO3); q = at(RIO3, s)
            p.location = (q.x, q.y + 0.18 * math.sin(k * 2.3), up + 0.03) if not (t > T("y el agua gira") and q.x > -3.5) else LEJOS
        elif k >= 12 and hn > 0.02:
            s = (((k - 12) / 6 + t * 0.1) % 1.0) * largo(NUE3); q = at(NUE3, s); p.location = (q.x, q.y + 0.3 * math.sin(k), hn + 0.03)
        else: p.location = LEJOS
    apply_cam(S["cam"], *cam_lin(t, CAM(), drift=0.03))

def VV(at_, off, lens=35):
    """vista de maqueta desde arriba: el cauce se ve por encima de los edificios"""
    h = math.hypot(off[0], off[1]); return V(at_, (off[0] * 0.85, off[1] * 0.85, max(off[2], 1.15 * h)), lens)

def CAM():
    k = Claves(); add = k.add
    ini = VV((-0.5, 0.4, 0.1), (1.3, -2.8, 1.7), 36)
    ancho = VV((0.3, -0.5, 0.0), (0.5, -11.0, 8.0), 30)
    add(0.0, VV((-1.0, 0.35, 0.1), (1.0, -2.6, 1.6), 36)); add(1.4, ini)
    add(T("que antes"), VV((0.0, 0.4, 0.1), (-1.2, -3.2, 2.0), 34))
    add(T("cómo se mueve"), ancho, 1.2)
    add(T("el turia"), VV((-1.0, 0.4, 0.0), (0.5, -5.5, 3.5), 32))
    add(T("casi siempre"), VV((1.5, 0.2, 0.1), (-0.8, -3.2, 1.8), 36))
    add(T("pero en mil"), VV((-5.0, 0.6, 0.4), (1.5, -4.2, 2.6), 32), 1.6)
    add(T("llegaron"), VV((-2.0, 0.4, 0.2), (1.0, -3.0, 1.6), 36), 1.2)
    add(T("el cauce no"), VV((0.5, 0.3, 0.3), (1.2, -3.4, 2.2), 36))
    add(T("y el agua se metió"), VV((1.0, 0.5, 0.2), (0.5, -5.0, 3.2), 32))
    add(T("en algunas"), VV((0.8, 1.3, 0.3), (0.6, -2.6, 1.2), 38), 1.0)
    add(T("podrías hacer"), VV((-0.5, 0.4, 0.3), (1.2, -3.2, 2.0), 36))
    add(T("pero el río seguiría"), VV((0.0, 0.2, 0.0), (0.0, -8.0, 6.5), 30), 1.0)
    add(T("así que decides"), VV((-1.0, -1.2, 0.0), (0.5, -9.0, 7.0), 30), 1.2)
    add(T("excavas"), VV((-2.0, -2.5, 0.0), (1.5, -4.5, 3.2), 34))
    add(T("doce"), VV((1.0, -3.2, 0.0), (1.0, -4.5, 3.0), 34))
    add(T("ciento"), VV((2.5, -3.2, 0.0), (-1.0, -2.6, 1.6), 38), 1.0)
    add(T("pero el agua siempre"), ancho, 1.2)
    add(T("así que", 2), VV((-4.0, 0.4, 0.1), (1.0, -3.0, 2.0), 36))
    add(T("cierras"), VV((-3.6, 0.5, 0.2), (0.8, -2.2, 1.3), 40), 1.0)
    add(T("y el agua gira"), VV((-3.2, -1.2, 0.1), (1.4, -3.2, 2.2), 34))
    add(T("pero por encima"), VV((0.5, -3.2, 0.1), (1.5, -3.5, 2.2), 34), 1.0)
    add(T("levantas puentes"), VV((2.0, -3.2, 0.1), (-1.5, -3.4, 2.0), 34), 1.2)
    add(T("y aquí viene"), VV((0.5, -1.0, 0.0), (-1.0, -12.0, 8.5), 30))
    add(T("el cauce nuevo traga"), VV((1.0, -3.2, 0.1), (1.2, -3.0, 1.6), 38), 1.0)
    add(T("cúbicos", 2), VV((3.5, -3.0, 0.1), (-1.2, -3.0, 1.6), 38))
    add(T("más que aquella"), VV((0.0, -1.0, 0.0), (0.5, -9.0, 6.0), 30))
    add(T("y casi todo"), VV((0.5, -3.2, 0.1), (1.2, -2.6, 1.4), 40), 1.0)
    add(T("y el cauce viejo"), VV((0.0, 0.4, 0.1), (0.5, -4.0, 2.6), 34))
    add(T("cruzando"), VV((2.5, 0.3, 0.1), (-1.5, -3.6, 2.2), 34))
    add(T("querían"), VV((0.0, 0.4, 0.1), (1.0, -3.0, 1.6), 36))
    add(T("pero los vecinos"), VV((-1.5, 0.5, 0.1), (-0.5, -3.0, 1.8), 36))
    add(T("así que hoy"), VV((0.0, 0.4, 0.1), (0.6, -5.0, 3.2), 32))
    add(T("con campos"), VV((1.2, 0.2, 0.1), (0.8, -2.6, 1.4), 38), 0.8)
    add(T("si has paseado"), VV((0.0, 0.4, 0.1), (1.0, -2.4, 0.9), 38), 1.4)
    add(T("sígueme"), VV((-1.0, 0.35, 0.1), (1.0, -2.6, 1.6), 36))
    add(DUR + 1, ini)
    return k.k

def anchors(sc, S, t):
    cam = S["cam"]; P = lambda v: proj(sc, cam, v)
    return {"parque": P((0.0, yr(0.0), 0.35)), "rio": P((-2.0, yr(-2.0), 0.4)), "calle": P((0.85, 1.3, 0.5)), "nuevo": P((1.0, -3.25, 0.35)),
            "ancho": P((2.5, -3.3, 0.35)), "muro": P((-3.5, 0.5, 0.45)), "puentes": P((1.2, -3.25, 0.45)), "viejo": P((0.5, yr(0.5), 0.3)),
            "arriba": P((-5.0, 0.6, 0.5)), "mar": P((5.7, -2.6, 0.3))}

if __name__ == "__main__":
    run("turia", build, pose, anchors)
