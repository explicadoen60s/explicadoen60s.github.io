# «Tu repetidor wifi puede cortarte la velocidad a la mitad» (Wifi, parte 2). Casa de maqueta en corte sobre una isla de
# césped: salón con el router (delante), pasillo con el repetidor enchufado y la habitación del fondo con el móvil.
# Anillos de ondas que pierden fuerza en cada pared, el repetidor que recoge y relanza, su única radio que escucha o habla
# por turnos (paquetes que van y vienen), 100 → 50 megas, el repetidor mal puesto, el punto intermedio, la doble banda y
# el cable hasta un segundo punto de acceso.
# Planos (fotografía → motion): 0 repetidor emitiendo (libre: arriba) · 2,6 casa entera · 6,9 router · 9 ondas y paredes ·
# 11 móvil · 14 repetidor nuevo · 19,5 radio por dentro · 26,5 turnos · 36 megas · 40,7 mal sitio · 48 punto intermedio ·
# 53 doble banda · 62 cable · 70 vuelta al primer plano.
import bpy, math, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from modelos import *
from maqueta import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("repetidor")
YEL = (1.0, 0.82, 0.2); CYAN = (0.25, 0.75, 1.0); ORANGE = (1.0, 0.5, 0.15); WHITE = (0.97, 0.97, 0.98); DARK = (0.15, 0.16, 0.2)
WOOD = (0.86, 0.66, 0.42); WALL = PAL["pared"]; GREEN = (0.3, 0.85, 0.4); OFF = (0.6, 0.62, 0.66); CABLE = (0.2, 0.45, 0.95)
ROUTER = Vector((-0.8, -3.4, 0.62)); PHONE = Vector((0.55, 3.25, 0.72)); AP = Vector((-1.47, 1.1, 0.4))
REP_IN, REP_LEJOS = Vector((-1.47, 0.0, 0.38)), Vector((-1.47, 2.3, 0.38))
HWALL = 1.0

def alpha_mat(o, a):
    m = o.active_material; m.diffuse_color = (*m.diffuse_color[:3], a)
    try: m.surface_render_method = 'BLENDED'
    except Exception: pass
    m.use_backface_culling = False

def pared(size, loc):
    """muro de maqueta con el canto de arriba en color crema (corte)"""
    box(size, loc, WALL); box((size[0] + 0.004, size[1] + 0.004, 0.03), (loc[0], loc[1], loc[2] + size[2] / 2 - 0.014), PAL["corte"])

def anillos(n, paso, col, dz=0.0):
    out = []
    for i in range(1, n + 1):
        r = torus(paso * i, 0.022, LEJOS, col, unique=True); alpha_mat(r, 0.0); r["r"] = paso * i; r["dz"] = dz; out.append(r)
    return out

def ondas(rings, centro, t, on, rmax, fuerza=1.0, att=None, v=1.2, lam=1.1):
    """frentes de onda que salen del centro: cada anillo se enciende cuando pasa un frente"""
    for r in rings:
        R = r["r"]
        if not on or R > rmax: r.location = LEJOS; continue
        ph = ((R - v * t) / lam) % 1.0
        a = max(0.0, math.cos(ph * math.tau)) ** 6 * (1 - R / (rmax + 0.3)) * fuerza * (att(R) if att else 1.0)
        if a < 0.02: r.location = LEJOS; continue
        r.location = Vector(centro) + Vector((0, 0, 0.05 + r["dz"])); alpha_mat(r, min(0.95, a))

def build():
    sc, cam = scene_setup(world=PAL["cielo"], shadow=0.25, light_rot=-60); entorno_claro(sc)
    S = {"cam": cam}
    nubes(10, (0, 12, 3.0), 10, 2.0, 1.0, s=1.6, seed=5)
    isla(4.6, 10.6, (0, 0, 0), capas=[(PAL["cesped"], 0.15), (PAL["tierra"], 0.45), (PAL["tierra2"], 0.5)])
    for k in range(6): arbusto((1.95, -4.6 + 1.8 * k, 0.12), 1.6, seed=k)   # setos
    # casa en corte: suelo, muros (sin el frente) y tabiques con hueco de puerta
    box((3.3, 9.2, 0.06), (0, 0, 0.03), WOOD)
    pared((0.12, 9.2, HWALL), (-1.6, 0, HWALL / 2)); pared((3.3, 0.12, HWALL), (0, 4.6, HWALL / 2))
    pared((0.12, 9.2, 0.3), (1.6, 0, 0.15))
    for y in (-1.5, 1.5):
        pared((2.3, 0.12, HWALL), (-0.45, y, HWALL / 2)); pared((0.25, 0.12, HWALL), (1.48, y, HWALL / 2))
        box((0.9, 0.13, 0.15), (0.92, y, HWALL - 0.075), WALL)
    # salón: mesita con el router, sofá y tele
    mesita((-0.8, -3.4, 0.06), 1.0, ancho=0.6, alto=0.44)
    sofa((0.6, -2.35, 0.06), 1.0, ancho=1.4)
    tele((0.55, -4.35, 0.06), 1.0, rot=math.pi)
    planta((-1.3, -2.0, 0.06), 1.5)
    # router
    S["router"] = empty(ROUTER)
    rounded_slab(0.42, 0.26, 0.05, 0.07, (0, 0, 0), WHITE, parent=S["router"])
    for sx in (-1, 1): cyl(0.018, 0.32, (sx * 0.16, 0.1, 0.2), DARK, parent=S["router"])
    S["rled"] = [sph(0.015, (-0.1 + 0.05 * i, -0.131, 0.04), GREEN, parent=S["router"], unique=True) for i in range(4)]
    # pasillo: alfombra, enchufe
    box((0.8, 2.0, 0.02), (0.3, 0, 0.07), PAL["turquesa"])
    for p in (REP_IN, REP_LEJOS): box((0.02, 0.1, 0.12), (p.x - 0.06, p.y, p.z), WHITE)
    # repetidor: cuerpo abierto por delante (+x), tapa que se quita, placa, radio y luz
    S["rep"] = empty(LEJOS)
    for dy in (-1, 1): box((0.14, 0.02, 0.26), (0.07, dy * 0.09, 0), WHITE, parent=S["rep"])
    for dz in (-1, 1): box((0.14, 0.2, 0.02), (0.07, 0, dz * 0.13), WHITE, parent=S["rep"])
    box((0.02, 0.2, 0.26), (0.0, 0, 0), WHITE, parent=S["rep"])
    box((0.01, 0.16, 0.22), (0.02, 0, 0), (0.2, 0.6, 0.3), parent=S["rep"])
    box((0.03, 0.07, 0.07), (0.04, 0, 0.03), DARK, parent=S["rep"])
    torus(0.025, 0.008, (0.045, 0, -0.06), (0.9, 0.55, 0.25), parent=S["rep"], rot=(0, math.pi / 2, 0))
    for dy in (-1, 1): cyl(0.008, 0.18, (0.08, dy * 0.06, 0.2), DARK, parent=S["rep"])
    S["tapa"] = box((0.015, 0.2, 0.26), (0.145, 0, 0), WHITE, parent=S["rep"], unique=True)
    S["led"] = sph(0.022, (0.1, 0, 0.145), GREEN, parent=S["rep"], unique=True)
    # punto de acceso del final y su cable
    S["ap"] = empty(LEJOS)
    box((0.1, 0.24, 0.24), (0.04, 0, 0), WHITE, parent=S["ap"]); S["apled"] = sph(0.02, (0.1, 0, 0.08), CYAN, parent=S["ap"])
    CAB = [ROUTER + Vector((-0.2, 0.1, -0.05)), Vector((-1.45, -3.3, 0.08)), Vector((-1.45, AP.y, 0.08)), AP + Vector((0, 0, -0.12))]
    S["cablepath"] = poly(CAB)
    S["cable"] = tubo(CAB, 0.02, CABLE)
    S["pcable"] = [sph(0.03, LEJOS, YEL, seg=10) for _ in range(8)]
    # habitación del fondo: cama, mesilla y el móvil con sus barras
    cama((0.6, 3.5, 0.06), 1.0)
    mesita((-1.1, 4.2, 0.06), 1.0, ancho=0.4, alto=0.4)
    S["phone"] = empty(PHONE)
    rounded_slab(0.13, 0.26, 0.02, 0.018, (0, 0, 0), DARK, parent=S["phone"]).rotation_euler = (math.pi / 2, 0, 0)
    box((0.11, 0.003, 0.22), (0, -0.02, 0.13), (0.35, 0.6, 0.95), parent=S["phone"])
    S["bars"] = [box((0.04, 0.03, 0.06 + 0.05 * i), (0.14 + 0.055 * i, 0, 0.03 + 0.025 * i), OFF, parent=S["phone"], unique=True) for i in range(4)]
    # anillos de ondas fijos (radios 0,25 … R); la onda que avanza se dibuja encendiendo unos u otros
    S["rr"] = anillos(30, 0.25, YEL); S["rp"] = anillos(17, 0.25, CYAN); S["rp2"] = anillos(17, 0.25, YEL, 0.03)
    S["ra"] = anillos(17, 0.25, CYAN)
    # paquetes de datos
    S["pk"] = [box((0.11, 0.11, 0.11), LEJOS, ORANGE) for _ in range(4)]
    S["pk2"] = [box((0.11, 0.11, 0.11), LEJOS, CYAN) for _ in range(4)]
    S["fl"] = flecha3d(LEJOS, (0, 1, 0), 0.5, 0.04)
    dyn = [cam, S["router"], S["rep"], S["ap"], S["cable"], S["pcable"], S["phone"], S["rr"], S["rp"], S["ra"], S["rp2"], S["pk"], S["pk2"], S["fl"]]
    join_static(dyn)
    return sc, S

# ---------------- estado ----------------
def rep_pos(t):
    if t < T("vamos a ver") or (T("así que pones") < t):
        u1 = seg(t, T("si lo pones"), T("si lo pones") + 1.0); u2 = seg(t, T("en un punto"), T("en un punto") + 1.0)
        p = REP_IN.lerp(REP_LEJOS, u1).lerp(REP_IN + Vector((0, 0.3, 0)), u2)
        p.z += 0.85 * (math.sin(math.pi * u1) + math.sin(math.pi * u2))     # salta por encima del tabique
        return p
    return None

def rep_activo(t): return rep_pos(t) is not None and t < T("llevar la") - 0.2

def senal_movil(t):
    """barras del móvil (0-4)"""
    if t < T("vamos a ver"): return 2
    if t < T("pero cada"): return 4
    if t < T("y la vuelve"): return mix(4, 1, seg(t, T("pero cada") + 0.4, T("apenas") + 0.5))
    if t < T("si lo pones"): return 3
    if t < T("en un punto"): return 1
    if t < T("llevar la"): return 3
    return 4

def arco_pts(a, b, t, h=0.6):
    p = Vector(a).lerp(Vector(b), t); p.z += h * 4 * t * (1 - t); return p

def turnos(t):
    """('in', u) móvil→repetidor, ('out', u) repetidor→router o None"""
    a, b = T("primero recibe"), T("primero recibe", fin=True) + 0.6
    if a <= t < T("luego se calla"): return ("in", seg(t, a, b))
    a = T("y se los"); b = T("y se los") + 1.2
    if a <= t < T("por el mismo"): return ("out", seg(t, a, b))
    if T("por el mismo") <= t < T("si tenías"):
        ph = ((t - T("por el mismo")) / 1.1) % 2.0
        return ("in", ph) if ph < 1 else ("out", ph - 1)
    return None

def pose(t, S):
    rp = rep_pos(t); act = rep_activo(t)
    S["rep"].location = rp if rp is not None else LEJOS
    # aparece con un pequeño salto al enchufarlo
    pop = seg(t, T("así que pones") + 0.1, T("así que pones") + 0.4) if T("vamos a ver") < t < T("recoge") else 1.0
    S["rep"].scale = (max(pop, 0.01),) * 3
    S["tapa"].location.x = 0.145 + 0.6 * seg(t, T("muchos"), T("muchos") + 0.6) * (1 - seg(t, T("si tenías"), T("si tenías") + 0.4))
    S["tapa"].hide_render = S["tapa"].location.x > 0.6
    tr = turnos(t)
    if tr: set_color(S["led"], CYAN if tr[0] == "in" else ORANGE)
    elif T("y una radio") < t < T("primero recibe"):
        set_color(S["led"], CYAN if math.sin(t * 6) > 0 else ORANGE)
    else: set_color(S["led"], GREEN)
    for i, l in enumerate(S["rled"]): set_color(l, GREEN if math.sin(t * 9 + i * 1.7) > -0.3 else (0.1, 0.4, 0.15))
    # anillos del router: más débiles al pasar cada pared
    on_r = t > T("tu router") - 0.2 or t < T("vamos a ver")
    on_r = on_r and not (T("pero aquí") < t < T("si tenías")) and not (T("llevar la") - 0.1 < t)
    debil = t > T("pero cada")
    att = lambda R: 1.0 if (R < 1.9 or not debil) else (0.4 if R < 4.9 else 0.12)
    ondas(S["rr"], ROUTER, t, on_r, 7.5, 1.0, att)
    lejos = T("si lo pones") < t < T("en un punto")
    emite = act and (t < T("vamos a ver") or (T("y la vuelve") - 0.1 < t < T("pero aquí")) or (T("es todavía") < t < T("entonces")) or
                     (T("donde el wifi") < t < T("llevar la")))
    doble = T("un repetidor que") < t < T("llevar la")
    c = (rp + Vector((0.1, 0, 0.05))) if rp is not None else LEJOS
    ondas(S["rp"], c, t, emite, 2.0 if lejos else 4.2, 0.35 if lejos else 1.0)
    ondas(S["rp2"], c, t + 0.45, doble, 4.2)
    # punto de acceso por cable
    uc = seg(t, T("llevar la"), T("llevar la") + 1.2)
    S["ap"].location = AP if uc > 0.01 else LEJOS
    S["cable"].hide_render = uc < 0.5
    for k, p in enumerate(S["pcable"]):
        p.location = at(S["cablepath"], ((k / 8 + t * 0.5) % 1.0) * largo(S["cablepath"])) if uc > 0.9 else LEJOS
    ondas(S["ra"], AP + Vector((0.1, 0, 0)), t, uc > 0.9, 4.2)
    # móvil y barras
    S["phone"].rotation_euler.z = 0.25 * math.sin(t * 0.8)
    n = senal_movil(t)
    for i, b in enumerate(S["bars"]): set_color(b, GREEN if i < round(n) else OFF)
    # paquetes por turnos (naranja: tus datos)
    rr = rp if rp is not None else REP_IN
    a_in, b_in = PHONE + Vector((0, 0, 0.1)), rr + Vector((0.12, 0, 0.1))
    a_out, b_out = rr + Vector((0.12, 0, 0.1)), ROUTER + Vector((0, 0, 0.1))
    for k, p in enumerate(S["pk"]):
        p.location = LEJOS
        if tr:
            uu = tr[1] - 0.08 * k
            if 0 <= uu <= 1:
                p.location = arco_pts(a_in, b_in, uu) if tr[0] == "in" else arco_pts(a_out, b_out, uu)
                p.rotation_euler = (t * 3, t * 2, 0)
        if T("así que cada") <= t < T("si tenías"):
            uu = ((t - T("así que cada")) * 0.5 - 0.1 * k) % 1.0
            p.location = arco_pts(a_in, b_in, uu * 2) if uu < 0.5 else arco_pts(a_out, b_out, uu * 2 - 1)
    # doble banda: los dos tramos a la vez
    for k, p in enumerate(S["pk2"]):
        if doble and t > T("y contigo"):
            uu = (t * 0.6 - 0.25 * k) % 1.0
            p.location = arco_pts(a_in, b_in, uu) if k % 2 == 0 else arco_pts(a_out, b_out, uu)
        else: p.location = LEJOS
    # flecha: la señal que se pierde en cada pared
    if T("pero cada") < t < T("en la habitación"):
        u = seg(t, T("pero cada"), T("se come", fin=True) + 0.6)
        S["fl"].location = (0.2, mix(-2.6, -1.75, u), 0.6); S["fl"].scale = (1, 1, mix(1.0, 0.45, u))
    else: S["fl"].location = LEJOS
    apply_cam(S["cam"], *cam_lin(t, CAM()))

def CAM():
    k = Claves(); add = k.add
    rep0 = V(REP_IN + Vector((0, 0, 0.1)), (1.7, -1.6, 0.9), 34)
    ancho = V((0, 0.3, 0.0), (0.4, -7.2, 6.4), 30)
    ancho2 = V((0, 0.3, 0.0), (3.4, -5.6, 6.6), 30)
    repcl = V(REP_IN + Vector((0, 0, 0.02)), (1.1, -0.85, 0.7), 40)
    add(0.0, rep0); add(1.4, V(REP_IN + Vector((0, 0, 0.1)), (1.9, -1.2, 1.1), 34))
    add(T("puede estar"), ancho, 1.2)
    add(T("vamos a ver"), ancho2)
    add(T("tu router"), V(ROUTER, (1.3, -1.7, 1.0), 35), 0.6)
    add(T("pero cada"), V((0, -1.0, 0), (2.6, -5.5, 4.6), 30), 1.0)
    add(T("en la habitación"), V(PHONE, (0.9, -1.7, 0.9), 38), 1.0)
    add(T("apenas") + 0.5, V((0, 0.5, 0), (2.4, -4.6, 4.6), 30))
    add(T("así que pones"), V(REP_IN, (1.5, -1.2, 0.9), 36), 1.0)
    add(T("recoge"), V((-0.6, -1.2, 0), (2.8, -4.2, 4.2), 30))
    add(T("y la vuelve"), V((-0.4, 1.4, 0), (2.8, -3.8, 4.0), 30))
    add(T("pero aquí"), repcl, 0.6)
    add(T("muchos") + 0.6, V(REP_IN, (0.9, 0.75, 0.65), 42), 1.2)
    add(T("pero no las"), repcl)
    add(T("primero recibe"), V((-0.6, 1.2, 0.4), (3.2, -2.8, 3.2), 28), 1.4)
    add(T("luego se calla"), repcl, 0.6)
    add(T("y se los"), V((-1.0, -1.7, 0.4), (2.6, -3.0, 2.8), 32))
    add(T("por turnos"), ancho2, 1.0)
    add(T("así que cada") + 1.2, V((-0.5, 0, 0), (3.6, -3.0, 4.5), 30))
    add(T("si tenías"), V(PHONE, (1.0, -1.6, 0.8), 38), 1.4)
    add(T("y aquí viene"), ancho)
    add(T("si lo pones"), V(REP_LEJOS, (1.6, 0.6, 1.0), 36), 1.2)
    add(T("el repetidor recibe"), V((-0.6, 0.0, 0), (3.0, -4.0, 4.4), 30), 1.0)
    add(T("y solo puede"), V(REP_LEJOS, (1.2, 0.1, 0.7), 40), 1.0)
    add(T("entonces"), ancho2)
    add(T("en un punto"), V(REP_IN + Vector((0, 0.3, 0)), (1.4, -1.2, 0.9), 36), 0.9)
    add(T("donde el wifi"), V((-0.5, -1.0, 0), (2.8, -4.6, 4.2), 30))
    add(T("y si no"), ancho, 0.6)
    add(T("hay dos"), V(REP_IN + Vector((0, 0.3, 0)), (1.0, -0.85, 0.7), 40))
    add(T("un repetidor que") + 0.8, V((-0.5, 0, 0), (3.4, -3.4, 4.0), 30), 0.8)
    add(T("y contigo"), V((-0.2, 1.8, 0.3), (2.4, -2.8, 2.6), 32))
    add(T("así no hay"), V(PHONE, (0.9, -1.6, 0.9), 38))
    add(T("llevar la"), V((-1.2, -1.2, 0.1), (2.9, -3.2, 3.2), 30), 1.0)
    add(T("segundo punto"), V(AP, (1.2, -1.2, 0.7), 38), 0.6)
    add(T("por el cable"), V((-1.45, -0.5, 0.1), (1.4, -1.2, 1.1), 36), 0.8)
    add(T("y la velocidad"), V(PHONE, (1.0, -1.7, 0.9), 38), 0.8)
    add(T("sígueme"), rep0)
    add(DUR + 1, rep0)
    return k.k

def anchors(sc, S, t):
    cam = S["cam"]; P = lambda v: proj(sc, cam, v); rp = rep_pos(t) or REP_IN
    return {"rep": P(rp + Vector((0.05, 0, 0.35))), "router": P(ROUTER + Vector((0, 0, 0.45))), "phone": P(PHONE + Vector((0, 0, 0.45))),
            "ap": P(AP + Vector((0, 0, 0.3))), "radio": P(rp + Vector((0.05, 0, 0.03))), "pared": P((0.2, -1.5, 1.1))}

if __name__ == "__main__":
    run("repetidor", build, pose, anchors)
