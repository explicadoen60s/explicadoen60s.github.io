# «¿Hasta dónde llega tu wifi de 5 GHz?» (Wifi, parte 3). Piso de maqueta en corte (medidas reales, en metros) sobre una
# isla de césped: salón con el router y el móvil en la mesita, tabique de PLADUR, cocina con la NEVERA, pared de LADRILLO
# macizo y dormitorio al fondo; fachada de HORMIGÓN. Ondas de 2,4 GHz (amarillas, separadas) y de 5 GHz (azules, más juntas)
# que salen del router y pierden fuerza en cada pared. Ondas sinusoidales que vibran (5 GHz más del doble) con paquetes de
# datos encima; anillos de alcance de 45 m y 15 m sobre el barrio; el móvil cambia de red según la habitación.
# Planos (fotografía → motion), esquina libre arriba-izquierda salvo que se diga:
# 0 router emitiendo, primer plano (libre: arriba) · 1,9 router otro lado · 3,7 salón · 6 piso entero · 9 móvil en la mesita ·
# 11 pantalla con dos redes · 13,3 red de 5 GHz · 15,7 onda de 2,4 · 18 la sigue · 20,2 onda de 5 · 22 paquetes · 24,8 las dos ·
# 27,1 piso desde arriba · 28,5 ondas hacia el tabique · 31,9 pladur · 32,6 ladrillo · 33,3 hormigón · 34,2 nevera ·
# 35 piso · 37,7 pladur de cerca · 39,9 ladrillo · 41,5 dormitorio · 43,6 5 GHz casi nada · 45,6 sube · 47,3 barrio 45 m ·
# 50,6 15 m · 52,7 baja · 54,4 móvil junto al router · 57,1 móvil en el dormitorio · 59,9 piso · 62,3 router · 65 = plano 0.
import bpy, math, sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from modelos import *
from maqueta import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("wifi5ghz")
YEL = (1.0, 0.80, 0.15); CYAN = (0.20, 0.72, 1.0); WHITE = (0.97, 0.97, 0.98); DARK = (0.14, 0.15, 0.19)
PLADUR = (0.92, 0.92, 0.95); BRICK = (0.90, 0.52, 0.38); HORM = (0.74, 0.74, 0.73); SUELO = (0.88, 0.70, 0.48)
X0, X1, Y0, Y1 = -3.5, 3.5, -5.5, 5.5          # piso; el lado x=-3,5 está cortado (la cámara mira desde ahí)
YP, YB = -1.5, 1.8                              # tabique de pladur y pared de ladrillo
HW = 2.6
ROUTER = Vector((0.5, -4.2, 0.0))               # router sobre la mesita (z la pone build)
MESA_Z = 0.55
C0 = Vector((ROUTER.x, ROUTER.y, MESA_Z + 0.08))
Z24, Z5 = 0.74, 0.90                            # altura de los frentes de onda de cada banda
PH_SALON = Vector((0.95, -4.15, MESA_Z + 0.012)); PH_CUARTO = Vector((-0.6, 4.95, 0.5 + 0.012))
SINE_X, SINE_Y0, SINE_Y1 = -1.6, -5.2, -2.0     # ondas sinusoidales (primeros planos)

def alpha_mat(m, a):
    m.diffuse_color = (*m.diffuse_color[:3], a)
    try: m.surface_render_method = 'BLENDED' if a < 0.999 else 'DITHERED'
    except Exception: pass
    try: m.blend_method = 'BLEND'
    except Exception: pass
    m.use_backface_culling = False

def tapa(size, loc, col):
    box(size, loc, col); box((size[0] + 0.01, size[1] + 0.01, 0.04), (loc[0], loc[1], loc[2] + size[2] / 2 - 0.018), PAL["corte"])

def zona(y): return 0 if y < YP else (1 if y < YB else 2)

def arcos(R, z):
    """trozos de la circunferencia de radio R (centro router) dentro del piso, separados por zona"""
    runs = []; cur = []; zc = None
    for k in range(0, 361, 3):
        a = math.radians(k); x = C0.x + R * math.cos(a); y = C0.y + R * math.sin(a)
        dentro = X0 + 0.05 < x < X1 - 0.08 and Y0 + 0.08 < y < Y1 - 0.08
        zz = zona(y) if dentro else None
        if zz != zc:
            if len(cur) > 1 and zc is not None: runs.append((zc, cur))
            cur = []; zc = zz
        if zz is not None: cur.append((x, y, z))
    if len(cur) > 1 and zc is not None: runs.append((zc, cur))
    return runs

def ondas_band(col, z):
    out = []
    for i in range(1, 31):
        R = 0.4 * i; mats = {}
        for zz, pts in arcos(R, z):
            o = tubo(pts, 0.03, col, unique=True)
            if zz not in mats: mats[zz] = o.active_material; alpha_mat(mats[zz], 0.0)
            else: o.data.materials[0] = mats[zz]
            o["R"] = R; o["z"] = zz; out.append(o)
    return out

def nevera(loc, s=1.0):
    e = empty(loc)
    caja((0.7 * s, 0.68 * s, 1.85 * s), (0, 0, 0.925 * s), (0.95, 0.96, 0.97), e, r=0.06 * s)
    caja((0.68 * s, 0.02 * s, 0.012 * s), (0, -0.345 * s, 1.25 * s), (0.75, 0.77, 0.8), e, r=0.004)
    for z in (1.0, 1.55):
        caja((0.04 * s, 0.05 * s, 0.32 * s), (-0.26 * s, -0.37 * s, z * s), (0.75, 0.77, 0.8), e, r=0.015 * s)
    caja((0.12 * s, 0.01 * s, 0.08 * s), (0.15 * s, -0.346 * s, 1.5 * s), PAL["rojo"], e, r=0.01)   # imán
    return e

def router_model(loc):
    e = empty(loc)
    caja((0.34, 0.22, 0.06), (0, 0, 0.03), WHITE, e, r=0.025)
    caja((0.3, 0.18, 0.012), (0, 0, 0.065), (0.88, 0.89, 0.92), e, r=0.005)
    ants = []
    for sx in (-0.13, -0.045, 0.045, 0.13):
        a = empty((sx, 0.1, 0.05), e); cilindro(0.012, 0.24, (0, 0, 0.12), DARK, a, r=0.006); ants.append(a)
    leds = [bola(0.011, (-0.09 + 0.045 * i, -0.112, 0.035), (0.3, 0.9, 0.45), e, unique=True) for i in range(5)]
    return e, ants, leds

def movil(loc):
    e = empty(loc)
    rounded_slab(0.075, 0.155, 0.012, 0.009, (0, 0, 0), DARK, parent=e)
    box((0.066, 0.142, 0.002), (0, 0, 0.0095), (0.94, 0.95, 0.97), parent=e)
    filas = []
    for i, (col, txt) in enumerate(((YEL, "CASA"), (CYAN, "CASA_5G"), ((0.8, 0.8, 0.82), "VECINO"))):
        y = 0.04 - i * 0.03
        f = box((0.058, 0.024, 0.002), (0, y, 0.0115), (0.86, 0.87, 0.9), parent=e, unique=True)
        bola(0.006, (-0.021, y, 0.0125), col, e)
        try: text3d(txt, (0.006, y, 0.0125), 0.008, DARK, parent=e, extrude=0.0005)
        except Exception: pass
        filas.append(f)
    return e, filas

def build():
    sc, cam = scene_setup(world=PAL["cielo"], shadow=0.25, light_rot=145); entorno_claro(sc)
    S = {"cam": cam}
    nubes(9, (0, 70, 30), 60, 8, 6, s=7, seed=3)
    nubes(5, (6, 16, 6), 8, 1.5, 1.5, s=1.4, seed=9)
    isla(110, 110, (0, 0, 0), capas=[(PAL["cesped"], 0.5), (PAL["tierra"], 3.0), (PAL["tierra2"], 4.0)])
    # barrio alrededor (escala del alcance: 15 y 45 m)
    rnd = random.Random(4)
    for k in range(16):
        a = k * math.tau / 16 + rnd.uniform(-0.15, 0.15); d = rnd.uniform(20, 48)
        x, y = d * math.cos(a), d * math.sin(a)
        if abs(x) < 9 and abs(y) < 11: continue
        if k % 3 == 0: edificio((x, y, 0), pisos=4, s=2.6, rot=rnd.uniform(0, 3), ancho=1.6, fondo=1.4)
        else: casa((x, y, 0), 4.0, rot=rnd.uniform(0, 3), pared=rnd.choice([PAL["pared"], (0.98, 0.85, 0.6), (0.85, 0.92, 0.98)]))
    for k in range(22):
        a = rnd.uniform(0, math.tau); d = rnd.uniform(14, 50); arbol((d * math.cos(a), d * math.sin(a), 0), 3.0, seed=k)
    calle(110, (0, -9.5, 0), ancho=5, aceras=True)
    for k in range(4): coche((-30 + 18 * k, -9.0 + (1.2 if k % 2 else -1.2), 0.04), 2.6, color=[PAL["rojo"], (0.25, 0.5, 0.9), PAL["amarillo"], (0.95, 0.95, 0.95)][k], rot=0 if k % 2 else math.pi)
    # el piso: suelo, fachada de hormigón y tabiques
    box((X1 - X0 + 0.3, Y1 - Y0 + 0.3, 0.12), (0, 0, 0.06), HORM)
    box((X1 - X0, Y1 - Y0, 0.02), (0, 0, 0.13), SUELO)
    tapa((0.25, Y1 - Y0 + 0.25, HW), (X1 + 0.12, 0, HW / 2 + 0.12), HORM)
    tapa((X1 - X0 + 0.25, 0.25, HW), (0, Y1 + 0.12, HW / 2 + 0.12), HORM)
    tapa((X1 - X0 + 0.25, 0.25, 0.35), (0, Y0 - 0.12, 0.3), HORM)        # murete del frente cortado
    tapa((0.25, Y1 - Y0 + 0.25, 0.35), (X0 - 0.12, 0, 0.3), HORM)        # murete del lado cortado
    # tabique de pladur con puerta (hueco x -3,0 … -2,1)
    tapa((X1 - (-2.1), 0.1, HW), ((X1 + -2.1) / 2, YP, HW / 2 + 0.12), PLADUR)
    tapa((0.45, 0.1, HW), (-3.27, YP, HW / 2 + 0.12), PLADUR); box((0.9, 0.1, 0.5), (-2.55, YP, HW - 0.13), PLADUR)
    # pared de ladrillo macizo con llagas
    tapa((X1 - (-2.1), 0.26, HW), ((X1 - 2.1) / 2, YB, HW / 2 + 0.12), BRICK)
    tapa((0.45, 0.26, HW), (-3.27, YB, HW / 2 + 0.12), BRICK); box((0.9, 0.26, 0.5), (-2.55, YB, HW - 0.13), BRICK)
    for j in range(1, 10):
        z = 0.12 + j * 0.26
        for sd in (-1, 1):
            box((X1 + 2.1, 0.01, 0.022), ((X1 - 2.1) / 2, YB + sd * 0.132, z), (0.93, 0.88, 0.8))
        for i in range(12):
            x = -2.0 + i * 0.5 + (0.25 if j % 2 else 0)
            if x < X1 - 0.05:
                for sd in (-1, 1): box((0.022, 0.01, 0.26), (x, YB + sd * 0.132, z - 0.13), (0.93, 0.88, 0.8))
    # salón
    alfombrilla((0.6, -3.3, 0.14), 2.2, 1.6, color=PAL["rosa"])
    mesita((ROUTER.x + 0.15, ROUTER.y, 0.13), 1.0, ancho=0.8, alto=MESA_Z - 0.13, color=(0.55, 0.75, 0.9))
    sofa((0.7, -2.35, 0.13), 1.2, color=PAL["turquesa"], ancho=1.6)
    tele((0.7, -5.15, 0.13), 1.2, rot=math.pi)
    planta((2.8, -5.0, 0.13), 1.6); planta((-2.7, -4.9, 0.13), 1.3, maceta=PAL["rosa"])
    # cocina con nevera
    cocina((0.6, 1.3, 0.13), 1.0, ancho=2.4)
    S_nev = nevera((2.75, 1.25, 0.13))
    olla((0.4, 1.3, 1.03), 0.8)
    # dormitorio
    cama((1.6, 4.4, 0.13), 1.25)
    mesita((-0.6, 4.95, 0.13), 1.0, ancho=0.5, alto=0.5 - 0.13)
    planta((-2.8, 5.0, 0.13), 1.4); alfombrilla((0.2, 3.3, 0.14), 1.0, 0.7, color=PAL["amarillo"])
    # router, móvil
    S["router"], S["ants"], S["leds"] = router_model(Vector((ROUTER.x, ROUTER.y, MESA_Z)))
    S["phone"], S["filas"] = movil(PH_SALON)
    S["pled"] = bola(0.13, LEJOS, CYAN, unique=True)
    # frentes de onda por bandas y zonas
    S["w24"] = ondas_band(YEL, Z24); S["w5"] = ondas_band(CYAN, Z5)
    # ondas sinusoidales (bolitas) y paquetes de datos
    S["s24"] = [sph(0.035, LEJOS, YEL, seg=10) for _ in range(70)]
    S["s5"] = [sph(0.035, LEJOS, CYAN, seg=10) for _ in range(70)]
    S["pk24"] = [caja((0.14, 0.14, 0.14), LEJOS, (1.0, 0.55, 0.15)) for _ in range(3)]
    S["pk5"] = [caja((0.14, 0.14, 0.14), LEJOS, (0.15, 0.45, 0.95)) for _ in range(7)]
    # flechas de señal que chocan con las paredes
    S["fP"] = flecha3d(LEJOS, (0, 1, 0), 1.0, 0.07); S["fB"] = flecha3d(LEJOS, (0, 1, 0), 1.0, 0.07)
    # anillos de alcance (45 m y 15 m)
    S["r45"] = torus(45, 0.7, LEJOS, YEL, unique=True); S["r15"] = torus(15, 0.55, LEJOS, CYAN, unique=True)
    dyn = [cam, S["router"], S["phone"], S["pled"], S["w24"], S["w5"], S["s24"], S["s5"], S["pk24"], S["pk5"], S["fP"], S["fB"],
           S["r45"], S["r15"]]
    join_static(dyn)
    return sc, S

# ---------------- estado ----------------
def bandas(t):
    """(intensidad 2,4, intensidad 5)"""
    a, b = 1.0, 1.0
    if T("la de dos coma") - 0.2 < t < T("la de cinco", 2) - 0.1: b = 0.0
    if T("la de dos coma", 2) - 0.2 < t < T("la de cinco solo") - 0.1: b = 0.0
    if T("la de cinco solo") - 0.1 < t < T("entonces"): a = 0.0
    if T("en la misma") < t < T("con dos"): a = 0.25
    if T("con dos") < t < T("te has"): b = 0.25
    return a, b

def atenua(t, band, z):
    if z == 0: return 1.0
    k1 = seg(t, T("un tabique") + 0.6, T("la mitad", fin=True))
    k2 = seg(t, T("deja pasar"), T("quinta", fin=True))
    k3 = seg(t, T("y en cinco"), T("todavía", fin=True))
    if band == 24: return mix(0.8, 0.5, k1) if z == 1 else mix(0.6, 0.5, k1) * mix(1.0, 0.36, k2)
    v = mix(0.75, 0.5, k1) if z == 1 else mix(0.5, 0.5, k1) * mix(1.0, 0.36, k2)
    return v * mix(1.0, 0.45 if z == 1 else 0.25, k3)

def pose_ondas(t, S, fuerza):
    a24, a5 = bandas(t)
    for objs, band, lam, v, caida, amp in ((S["w24"], 24, 1.6, 1.6, 9.0, a24), (S["w5"], 5, 0.8, 1.6, 5.0, a5)):
        seen = set()
        for o in objs:
            R = o["R"]; ph = ((R - v * t) / lam) % 1.0
            a = max(0.0, math.cos(ph * math.tau)) ** 8 * math.exp(-R / caida) * atenua(t, band, o["z"]) * amp * fuerza
            o.hide_render = a < 0.03
            m = o.active_material
            if m.name not in seen: seen.add(m.name); aa = a * 1.5; alpha_mat(m, 1.0 if aa > 0.8 else aa)

def pose_sine(t, S):
    on = T("la de dos coma") - 0.4 < t < T("pero hay una") + 0.2
    for chain, z, lam, w, vis in ((S["s24"], 1.75, 1.0, 2.4, t > T("la de dos coma") - 0.4), (S["s5"], 1.05, 0.46, 5.0, t > T("la de cinco", 2) - 0.2)):
        for i, s in enumerate(chain):
            if not (on and vis): s.location = LEJOS; continue
            u = i / (len(chain) - 1); y = mix(SINE_Y0, SINE_Y1, u)
            grow = seg(t, (T("la de dos coma") if z > 1.5 else T("la de cinco", 2)) - 0.4 + u * 0.8, (T("la de dos coma") if z > 1.5 else T("la de cinco", 2)) + u * 0.8)
            s.location = (SINE_X, y, z + 0.2 * grow * math.sin(math.tau * (y / lam) - w * 1.6 * t))
            s.scale = (max(grow, 0.01),) * 3
    pk_on = T("y caben") - 0.3 < t < T("pero hay una") + 0.2
    for pks, lam, w, z in ((S["pk24"], 1.0, 2.4, 1.75), (S["pk5"], 0.46, 5.0, 1.05)):
        for k, p in enumerate(pks):
            if not pk_on: p.location = LEJOS; continue
            u = ((k / len(pks)) + (t - T("y caben")) * 0.18) % 1.0; y = mix(SINE_Y0, SINE_Y1, u)
            g = seg(t, T("y caben") - 0.3 + 0.1 * k, T("y caben") + 0.1 * k)
            p.location = (SINE_X, y, z + 0.2 * math.sin(math.tau * (y / lam) - w * 1.6 * t) + 0.16); p.scale = (max(g, 0.01),) * 3

def pose(t, S):
    # router: luces que parpadean, antenas que vibran
    for i, l in enumerate(S["leds"]):
        on = math.sin(t * 9 + i * 1.7) > -0.2
        set_color(l, (0.3, 0.95, 0.45) if on else (0.2, 0.4, 0.25))
    for i, a in enumerate(S["ants"]): a.rotation_euler = (0.05 * math.sin(t * 20 + i), 0.06 * math.sin(t * 17 + i * 2), 0)
    pose_ondas(t, S, 1.0)
    pose_sine(t, S)
    # móvil: lista de redes; la de 5 GHz se ilumina; después cambia de red y de habitación
    f24, f5, fv = S["filas"]
    dos = T("muchas veces") < t < T("la de dos coma") - 0.3
    set_color(f24, (1.0, 0.92, 0.55) if dos and math.sin(t * 6) > 0 else (0.86, 0.87, 0.9))
    c5 = T("una acaba") < t < T("la de dos coma") - 0.3 or (dos and math.sin(t * 6) <= 0)
    set_color(f5, (0.6, 0.86, 1.0) if c5 else (0.86, 0.87, 0.9))
    u = seg(t, T("con dos"), T("con dos") + 1.0)
    p = PH_SALON.lerp(PH_CUARTO, u); p.z += 1.6 * math.sin(math.pi * u)
    S["phone"].location = p; S["phone"].rotation_euler.z = math.tau * u
    if T("en la misma") + 0.3 < t < T("te has"):
        S["pled"].location = p + Vector((0, 0, 0.35 + 0.05 * math.sin(t * 8)))
        set_color(S["pled"], CYAN if t < T("con dos") + 0.6 else YEL)
    else: S["pled"].location = LEJOS
    # flechas que empujan contra el tabique y la pared (se encogen al atravesar)
    for f, y, a, b, sc in ((S["fP"], YP, T("un tabique"), T("y una pared"), 0.5), (S["fB"], YB, T("y una pared"), T("y en cinco") + 1.0, 0.2)):
        if a - 0.2 < t < b:
            k = seg(t, a, a + 0.8); f.location = (0.5, y - 1.15 + 0.15 * k, Z24 + 0.6)
            f.scale = (1, 1, mix(1.0, 0.35, seg(t, a + 0.6, a + 1.4)))
        else: f.location = LEJOS
    # anillos de alcance
    g45 = seg(t, T("la de dos coma", 2), T("cuarenta y cinco", fin=True)) * (1 - seg(t, T("entonces"), T("entonces") + 0.6))
    g15 = seg(t, T("la de cinco solo"), T("quince", fin=True)) * (1 - seg(t, T("entonces"), T("entonces") + 0.6))
    for o, g, z in ((S["r45"], g45, 0.6), (S["r15"], g15, 0.75)):
        if g > 0.01:
            o.location = (C0.x, C0.y, z); o.scale = (g, g, 1)
        else: o.location = LEJOS
    apply_cam(S["cam"], *cam_lin(t, CAM(), drift=0.02))

def CAM():
    k = Claves(); add = k.add
    R = C0 + Vector((0, 0, 0.1))
    ini = ((R.x - 1.15, R.y - 0.75, R.z + 0.72), (R.x + 0.05, R.y + 0.05, R.z + 0.33), 40)
    piso = ((-9.5, -9.0, 11.5), (0.2, -0.2, 0.3), 28)
    add(0.0, ((R.x - 1.0, R.y - 0.95, R.z + 0.6), (R.x, R.y, R.z + 0.32), 40)); add(1.0, ini)
    add(T("en dos"), ((R.x - 1.4, R.y + 0.9, R.z + 0.9), (R.x, R.y, R.z + 0.35), 38))
    add(T("hasta cuántos"), ((-4.6, -7.4, 3.4), (0.4, -3.6, 0.9), 32))
    add(T("escribe"), piso)
    add(T("mira la"), ((PH_SALON.x - 0.55, PH_SALON.y - 0.35, PH_SALON.z + 0.7), (PH_SALON.x, PH_SALON.y, PH_SALON.z + 0.05), 40))
    add(T("muchas veces"), ((PH_SALON.x - 0.32, PH_SALON.y - 0.05, PH_SALON.z + 0.45), (PH_SALON.x, PH_SALON.y, PH_SALON.z), 40))
    add(T("una acaba"), ((PH_SALON.x - 0.25, PH_SALON.y + 0.12, PH_SALON.z + 0.4), (PH_SALON.x, PH_SALON.y, PH_SALON.z), 40))
    sy = (SINE_Y0 + SINE_Y1) / 2
    add(T("la de dos coma"), ((-5.6, -4.6, 2.2), (SINE_X, -4.2, 1.6), 38))
    add(T("cuatrocientos"), ((-5.6, -3.0, 2.0), (SINE_X, -3.0, 1.55), 38))
    add(T("la de cinco", 2), ((-5.4, -4.0, 1.4), (SINE_X, -3.8, 1.1), 40))
    add(T("más vibraciones"), ((-6.6, -2.4, 2.0), (SINE_X, sy, 1.35), 34))
    add(T("y caben"), ((-6.0, -5.2, 1.9), (SINE_X, sy, 1.35), 36))
    add(T("por eso la"), ((-7.0, -1.5, 2.6), (SINE_X, sy, 1.3), 34))
    add(T("pero hay una"), ((-8.5, -10.5, 10.5), (0.4, -0.4, 0.4), 28))
    add(T("cuanto más"), ((-8.0, -6.5, 5.0), (0.4, -2.0, 1.0), 32))
    add(T("el pladur"), ((-5.0, -3.6, 2.6), (0.6, YP, 1.2), 34))
    add(T("el ladrillo"), ((-5.0, -0.4, 2.8), (0.6, YB, 1.2), 34))
    add(T("el hormigón"), ((-6.0, -1.0, 3.6), (X1, 0.0, 1.3), 30))
    add(T("tu nevera"), ((-2.8, -0.6, 2.2), (2.75, 1.0, 1.1), 36))
    add(T("cada obstáculo"), ((-10.5, -7.5, 11.0), (0.2, 0.0, 0.4), 28))
    add(T("un tabique"), ((-4.6, -4.4, 3.4), (0.6, YP, 1.0), 34))
    add(T("y una pared"), ((-4.8, -0.8, 3.6), (0.6, YB, 1.0), 34))
    add(T("deja pasar"), ((-5.4, 2.6, 3.4), (0.4, 3.6, 0.9), 34))
    add(T("y en cinco"), ((-6.5, -1.0, 5.2), (0.4, 1.5, 1.0), 32))
    add(T("por eso", 2), ((-14.0, -14.0, 16.0), (0.4, -1.0, 0.0), 30))
    add(T("la de dos coma", 2), ((-46.0, -66.0, 82.0), (0.0, -2.0, 0.0), 26))
    add(T("la de cinco solo"), ((-24.0, -38.0, 40.0), (0.0, -3.0, 0.0), 28))
    add(T("entonces"), ((-9.0, -10.0, 10.0), (0.3, -0.6, 0.4), 28))
    add(T("en la misma"), ((-3.6, -6.3, 2.2), (0.7, -4.2, 0.8), 34))
    add(T("con dos"), ((-7.5, -4.5, 6.5), (0.0, 0.5, 1.0), 28))
    add(T("la de dos coma", 3), ((-4.4, 3.2, 2.4), (-0.6, 4.9, 0.6), 36))
    add(T("te has"), piso)
    add(T("pídelo"), ((-4.8, -6.4, 2.8), (0.4, -3.8, 0.9), 32))
    add(T("lo más"), ((R.x - 1.4, R.y + 0.9, R.z + 0.9), (R.x, R.y, R.z + 0.35), 38))
    add(T("sígueme"), ((R.x - 1.0, R.y - 0.95, R.z + 0.6), (R.x, R.y, R.z + 0.32), 40))
    add(DUR + 0.4, ini)
    return k.k

def anchors(sc, S, t):
    cam = S["cam"]; P = lambda v: proj(sc, cam, v)
    sy = (SINE_Y0 + SINE_Y1) / 2
    return {"router": P(C0 + Vector((0, 0, 0.35))), "phone": P(S["phone"].location), "s24": P((SINE_X, sy, 2.05)), "s5": P((SINE_X, sy, 1.3)),
            "pladur": P((0.6, YP, HW)), "ladrillo": P((0.6, YB, HW)), "cuarto": P((0.4, 3.6, 1.2)), "nevera": P((2.75, 1.25, 2.1)),
            "horm": P((X1, 0.0, HW)), "r45": P((C0.x, C0.y + 45, 0.6)), "r15": P((C0.x, C0.y + 15, 0.75))}

if __name__ == "__main__":
    run("wifi5ghz", build, pose, anchors)
