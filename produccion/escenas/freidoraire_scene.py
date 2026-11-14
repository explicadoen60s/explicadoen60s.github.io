# «¿A cuántos grados sopla tu freidora de aire?» Cocina de maqueta sobre una isla cortada (baldosas, hormigón, tierra):
# pared de azulejos, bancada con placa y horno empotrado (con reloj), reloj de pared y la freidora de aire en la encimera.
# La freidora es una carcasa hueca (SOLIDIFY) con el frente cortado por una booleana (cantos crema): arriba la resistencia
# en espiral que se pone al rojo y el ventilador que gira; abajo el cesto con agujeros y las patatas. El aire (bolitas que
# pasan de amarillo a rojo) baja por los lados y sube a través del cesto; flechas rojas. Gotitas de agua en las patatas
# que el aire se lleva; con el cesto lleno hasta arriba el aire se queda atascado y sale vapor. Mando que baja 20 grados,
# una sola capa y el cesto que se sacude.
# Cámara por cortes (lección de nevera, 14-nov): cada plano empuja un 8 % y cambia de golpe; nunca viaja a través de nada.
# Planos (fotografía → motion; esquina libre arriba-izquierda salvo el mini del juego):
#  0 cesto con aire subiendo a 0,5 m · 1,4 interior · 2,6 cocina · 4,9 cesto lleno · 6,1 patatas blandas · 7,1 freidora ·
#  8,8 freidora y horno · 10,6 resistencia · 13,2 resistencia (otro lado) · 14,8 ventilador · 16,2 interior con flechas ·
#  17 patatas con gotas · 19,7 patatas doradas · 22 agujeros del cesto · 24 cesto lleno · 25,8 una patata · 28,2 atasco ·
#  30,4 atasco (otro lado) · 33,1 patatas · 34,5 vapor · 36,3 cocina · 37,8 interior (revelación) · 40,3 horno y reloj ·
#  43,9 display de la freidora · 45,9 cocina · 47,9 mando · 49,9 freidora · 50,8 una sola capa · 52,5 cesto que se sacude ·
#  54,8 cocina · 55,8 interior · 58,8 freidora y horno · 60,6 cocina · 61,7 resistencia · 64,4 vuelta al primer plano.
import bpy, math, sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from modelos import *
from maqueta import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("freidoraire")
SUELO = (0.90, 0.86, 0.80); NEGRO = (0.20, 0.21, 0.24); PALIDA = (0.99, 0.92, 0.60); DORADA = (0.95, 0.62, 0.18)
AIRE_F = (1.0, 0.85, 0.35); AIRE_C = (0.98, 0.30, 0.15); GOTA = (0.45, 0.72, 1.0); VAPOR = (0.97, 0.98, 1.0)
F = Vector((-0.25, 0.5, 0.9))                       # base de la freidora (encima de la encimera)
HORNO = Vector((0.65, 0.29, 0.48))                  # puerta del horno
KNOB = F + Vector((0.0, -0.06, 0.392))
RELOJ = Vector((0.65, 0.73, 1.75))
NP, NA, NG, NV = 28, 30, 18, 12

def modo(t):
    """'lleno' (hasta arriba), 'capa' (una sola capa) o 'normal'"""
    if T("la llenas") - 0.2 <= t < T("tu freidora no") - 0.2: return "lleno"
    if T("pero llenas") - 0.2 <= t < T("y aquí viene") - 0.2: return "lleno"
    if T("pon una sola") - 0.1 <= t < T("te has acercado") - 0.2: return "capa"
    return "normal"

def atasco(t):
    return win01(t, T("las patatas se tapan") - 0.1, T("y aquí viene") - 0.2, 0.4, 0.3)

def build():
    sc, cam = scene_setup(world=PAL["cielo"], shadow=0.25, light_rot=50); entorno_claro(sc)
    S = {"cam": cam}
    nubes(8, (0.0, 6.0, 3.0), 6, 0.8, 1.0, s=1.1, seed=31)
    # ---------- cocina ----------
    isla(3.0, 2.0, (0.1, 0.15, 0), capas=[(SUELO, 0.08), (PAL["hormigon"], 0.16), (PAL["tierra"], 0.32), (PAL["tierra2"], 0.36)])
    for k in range(8): box((0.012, 2.0, 0.006), (-1.3 + k * 0.4, 0.15, 0.003), (0.80, 0.76, 0.70))
    for k in range(5): box((3.0, 0.012, 0.006), (0.1, -0.75 + k * 0.4, 0.003), (0.80, 0.76, 0.70))
    box((3.0, 0.1, 2.2), (0.1, 0.85, 1.1), PAL["pared"]); box((3.0, 0.102, 0.03), (0.1, 0.85, 2.185), PAL["corte"])
    azulejos(2.8, 0.6, (0.1, 0.79, 1.22), color=(0.98, 0.72, 0.55), paso=0.15)
    cocina((0.1, 0.6, 0), 1.0, ancho=1.8)
    olla((0.45, 0.6, 0.905), 0.55)
    planta((0.95, 0.65, 0.905), 0.7); planta((-1.25, 0.55, 0.0), 1.5)
    caja((0.4, 0.28, 0.03), (0.1, 0.62, 0.92), PAL["madera"], r=0.01)                            # tabla de cortar
    alfombrilla((0.1, -0.15, 0.01), 0.7, 0.4, color=PAL["rosa"])
    # horno empotrado con su reloj
    caja((0.58, 0.04, 0.52), tuple(HORNO), (0.25, 0.26, 0.29), r=0.02)
    caja((0.44, 0.012, 0.26), tuple(HORNO + Vector((0, -0.022, -0.04))), (0.12, 0.13, 0.16), r=0.01)
    caja((0.42, 0.03, 0.025), tuple(HORNO + Vector((0, -0.04, 0.17))), (0.78, 0.8, 0.84), r=0.01)
    caja((0.12, 0.01, 0.05), tuple(HORNO + Vector((0, -0.024, 0.22))), (0.10, 0.12, 0.15), r=0.005)
    # reloj de pared (la aguja corre mientras el horno se calienta)
    cilindro(0.16, 0.03, tuple(RELOJ), (0.99, 0.99, 0.97), rot=(math.pi / 2, 0, 0), r=0.01)
    torus(0.16, 0.015, tuple(RELOJ + Vector((0, -0.01, 0))), PAL["rojo"], rot=(math.pi / 2, 0, 0))
    for k in range(12): box((0.01, 0.01, 0.03), tuple(RELOJ + Vector((0.13 * math.sin(k * 0.5236), -0.02, 0.13 * math.cos(k * 0.5236)))), (0.2, 0.2, 0.25), rot=(0, k * 0.5236, 0))
    S["aguja"] = empty(tuple(RELOJ + Vector((0, -0.025, 0)))); S["aguja"].rotation_mode = 'XYZ'
    box((0.012, 0.008, 0.12), (0, 0, 0.05), (0.15, 0.15, 0.18), S["aguja"])
    # ---------- freidora de aire: carcasa hueca con el frente cortado ----------
    S["carcasa"] = caja((0.32, 0.34, 0.4), tuple(F + Vector((0, 0, 0.2))), NEGRO, r=0.06, unique=True)
    S["carcasa"].data.materials.append(mat(PAL["corte"]))
    m = S["carcasa"].modifiers.new("hueca", "SOLIDIFY"); m.thickness = 0.018; m.offset = -1; m.material_offset = 1
    S["cut"] = cortador((0.27, 0.2, 0.33), tuple(F + Vector((0, -0.105, 0.19))))
    cortar(S["carcasa"], S["cut"])                                                   # corte real: modificador BOOLEAN
    caja((0.2, 0.012, 0.05), tuple(F + Vector((0, -0.165, 0.375))), (0.12, 0.14, 0.18), r=0.01)   # display
    for k in range(4): cilindro(0.02, 0.01, tuple(F + Vector((-0.09 + 0.06 * k, 0.17, 0.4))), (0.3, 0.32, 0.36), r=0.004)     # rejilla de salida
    S["mando"] = empty(tuple(KNOB)); S["mando"].rotation_mode = 'XYZ'
    cilindro(0.035, 0.02, (0, 0, 0), (0.85, 0.86, 0.9), S["mando"], r=0.006)
    box((0.006, 0.03, 0.022), (0, -0.015, 0.008), PAL["rojo"], S["mando"])
    for k in range(4): caja((0.04, 0.04, 0.02), tuple(F + Vector((-0.12 + 0.24 * (k % 2), -0.12 + 0.24 * (k // 2), -0.005))), (0.1, 0.1, 0.12), r=0.008)
    # resistencia en espiral (se pone al rojo) y ventilador
    pts = []
    for i in range(60):
        a = i / 59 * 2.5 * 2 * math.pi; r = 0.03 + 0.085 * i / 59
        pts.append(F + Vector((r * math.cos(a), 0.02 + r * math.sin(a) * 0.5, 0.31)))
    S["res"] = tubo(pts, 0.007, (0.45, 0.45, 0.48), unique=True)
    S["vent"] = empty(tuple(F + Vector((0, 0.02, 0.345)))); S["vent"].rotation_mode = 'XYZ'
    cilindro(0.025, 0.02, (0, 0, 0), (0.6, 0.62, 0.66), S["vent"], r=0.006)
    for k in range(6):
        a = k * math.pi / 3
        caja((0.1, 0.03, 0.006), (0.06 * math.cos(a), 0.06 * math.sin(a), 0), (0.75, 0.77, 0.80), S["vent"], rot=(0.35, 0, a), r=0.003)
    # cesto con agujeros (se puede sacar y sacudir) y patatas
    S["cesto"] = empty(tuple(F + Vector((0, 0, 0.05))))
    caja((0.24, 0.24, 0.012), (0, 0, 0), (0.30, 0.32, 0.36), S["cesto"], r=0.004)
    for i in range(6):
        for j in range(6): cilindro(0.008, 0.014, (-0.1 + i * 0.04, -0.1 + j * 0.04, 0.0), (0.08, 0.08, 0.1), S["cesto"], v=10, r=0.002)
    caja((0.24, 0.012, 0.15), (0, 0.115, 0.075), (0.30, 0.32, 0.36), S["cesto"], r=0.004)
    for sx in (-1, 1): caja((0.012, 0.24, 0.15), (0.115 * sx, 0, 0.075), (0.30, 0.32, 0.36), S["cesto"], r=0.004)
    caja((0.06, 0.08, 0.03), (0, -0.2, 0.06), NEGRO, S["cesto"], r=0.01)                          # asa
    S["pat"] = [caja((0.016, 0.016, 0.075), LEJOS, PALIDA, r=0.004, unique=True) for _ in range(NP)]
    S["aire"] = [sph(0.009, LEJOS, AIRE_F, seg=8, unique=True) for _ in range(NA)]
    S["gotas"] = [sph(0.006, LEJOS, GOTA, seg=8) for _ in range(NG)]
    S["vapor"] = [sph(0.02, LEJOS, VAPOR, seg=10) for _ in range(NV)]
    S["fl_baja"] = [flecha3d(LEJOS, (0, 0, -1), 0.1, 0.008) for _ in range(2)]
    S["fl_sube"] = flecha3d(LEJOS, (0, 0, 1), 0.12, 0.01)
    S["fl_pat"] = [flecha3d(LEJOS, d, 0.05, 0.005) for d in ((1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1))]
    dyn = [cam, S["aguja"], S["carcasa"], S["cut"], S["mando"], S["res"], S["vent"], S["cesto"], S["pat"], S["aire"], S["gotas"],
           S["vapor"], S["fl_baja"], S["fl_sube"], S["fl_pat"]]
    join_static(dyn)
    return sc, S

def cesto_off(t):
    """el cesto sale hacia delante y se sacude en «sacude el cesto»"""
    a, b = T("y sacude") - 0.1, T("cocción", fin=True) + 0.4
    u = win01(t, a, b, 0.4, 0.4)
    return Vector((0.02 * math.sin(t * 30) * u, -0.12 * u, 0.025 * abs(math.sin(t * 22)) * u))

def pos_patatas(t):
    md = modo(t); rr = random.Random(2); out = []
    for k in range(NP):
        if md == "capa":
            if k >= 12: out.append(None); continue
            i, j = k % 4, k // 4
            out.append((Vector((-0.075 + i * 0.05, -0.06 + j * 0.06, 0.016)), (0, math.pi / 2, 0.2 * (k % 3))))
            continue
        x, y = rr.uniform(-0.09, 0.09), rr.uniform(-0.09, 0.09)
        capa = k / NP
        z = 0.02 + (0.08 if md == "normal" else 0.15) * capa + rr.uniform(0, 0.02)
        if md == "normal" and k >= 20: out.append(None); continue
        out.append((Vector((x, y, z)), (rr.uniform(0.6, 1.4), rr.uniform(-0.4, 0.4), rr.uniform(0, 3.1))))
    return out

def pose(t, S):
    st = atasco(t); bo = cesto_off(t)
    calor = keyed(t, [(0, 0.8), (T("arriba", 2) - 0.1, 0.3), (T("calienta"), 1.0), (T("tu horno") - 0.2, 1.0), (T("tu horno"), 0.8)])
    set_color(S["res"], (mix(0.45, 1.0, calor), mix(0.45, 0.28, calor), mix(0.48, 0.1, calor)))
    vel = 1.0 - 0.75 * st
    S["vent"].rotation_euler = (0, 0, t * (14 + 10 * seg(t, T("un ventilador"), T("un ventilador") + 0.5)))
    S["aguja"].rotation_euler = (0, t * 0.4 + 9 * seg(t, T("tu horno"), T("calentarse", fin=True)) + 3 * seg(t, T("tu freidora", 3), T("cinco", fin=True)), 0)
    S["mando"].rotation_euler = (0, 0, math.radians(-40 * seg(t, T("baja") - 0.1, T("veinte grados", fin=True))) if t < T("te has acercado") else 0.0)
    S["cesto"].location = F + Vector((0, 0, 0.05)) + bo
    # patatas: pálidas, se doran con el aire; blandas y pálidas cuando el cesto va lleno
    md = modo(t); dorado = seg(t, T("por eso se dora") - 0.2, T("crujiente", fin=True))
    if md == "lleno": dorado *= 0.15
    if md == "capa": dorado = 1.0
    if t > T("te has acercado"): dorado = 0.8
    col = tuple(mix(a, b, dorado) for a, b in zip(PALIDA, DORADA))
    for p, pr in zip(S["pat"], pos_patatas(t)):
        if pr is None: p.location = LEJOS; continue
        loc, rot = pr; salto = Vector((0, 0, 0.03 * abs(math.sin(t * 22 + loc.x * 40)))) * (1 if bo.length > 0.01 else 0)
        p.location = F + Vector((0, 0, 0.06)) + bo + loc + salto; p.rotation_euler = rot; set_color(p, col)
    # aire caliente: baja por los lados y sube a través del cesto; con el cesto lleno se queda atascado
    temp = seg(t, T("el aire sube") - 0.1, T("doscientos", fin=True))
    for k, b in enumerate(S["aire"]):
        sx = 1 if k % 2 else -1
        ruta = poly([F + Vector((0, 0.02, 0.33)), F + Vector((0.12 * sx, 0.02, 0.33)), F + Vector((0.135 * sx, 0.02, 0.05)),
                     F + Vector((0.03 * sx, 0.02, 0.035)), F + Vector((0.0, 0.02, 0.17)), F + Vector((0.0, 0.02, 0.3))])
        u = (t * 0.55 * vel + k / NA) % 1.0
        p = at(ruta, u * largo(ruta)) + Vector((0, -0.06 + 0.12 * ((k * 0.37) % 1.0), 0))
        if st > 0.05 and p.z < 0.2 + F.z and abs(p.x - F.x) < 0.1:          # atascado dentro del montón
            p = p + Vector((0.01 * math.sin(t * 9 + k), 0, -0.02 * st))
        b.location = p; set_color(b, tuple(mix(a, c, max(calor * 0.6, temp)) for a, c in zip(AIRE_F, AIRE_C)))
    w = win01(t, T("un ventilador") - 0.1, T("cada patata"), 0.3, 0.3) + win01(t, 0.0, T("escribe"), 0.01, 0.3)
    for k, f in enumerate(S["fl_baja"]):
        sx = 1 if k else -1
        f.location = F + Vector((0.15 * sx, -0.01, 0.27 - 0.04 * ((t * 1.5) % 1.0))) if w > 0.01 else LEJOS; f.scale = (max(w, 0.001),) * 3
    ws = max(w, 0) * (1 - st)
    S["fl_sube"].location = F + Vector((0, 0.0, 0.2 + 0.04 * ((t * 1.5) % 1.0))) + bo if ws > 0.01 else LEJOS
    S["fl_sube"].scale = (max(ws * (1 + 0.6 * seg(t, T("ese aire"), T("ese aire") + 0.5)), 0.001),) * 3
    # una patata con aire por todos lados
    wp = win01(t, T("cada patata") - 0.1, T("las patatas se tapan"), 0.3, 0.3)
    pr = pos_patatas(t)[3]
    for k, f in enumerate(S["fl_pat"]):
        if wp < 0.01 or pr is None: f.location = LEJOS; continue
        c = F + Vector((0, 0, 0.06)) + pr[0]; d = ((-0.05, 0, 0), (0.05, 0, 0), (0, 0, -0.07), (0, 0, 0.07))[k]
        f.location = c + Vector(d); f.scale = (wp,) * 3
    # gotitas de agua en las patatas: el aire se las lleva; con el atasco se quedan
    barre = seg(t, T("ese aire") + 0.3, T("de la superficie", fin=True))
    hay = t >= T("la llenas") - 0.2
    for k, g in enumerate(S["gotas"]):
        if not hay or pr is None: g.location = LEJOS; continue
        pp = pos_patatas(t)[k % NP] or pos_patatas(t)[0]
        base = F + Vector((0, 0, 0.06)) + bo + pp[0] + Vector((0.01, -0.01, 0.03))
        quita = barre * (1 - (1 if modo(t) == "lleno" else 0)) if t < T("pon una sola") else 1.0
        if t > T("las patatas se tapan"): quita = 0.0 if modo(t) == "lleno" else quita
        if t > T("te has acercado"): quita = 1.0
        if quita > 0.98: g.location = LEJOS; continue
        g.location = base + Vector((0.12 * quita * (1 if k % 2 else -1), 0, 0.15 * quita))
    # vapor: las patatas se cuecen en su propio vapor
    va = win01(t, T("y en vez") - 0.1, T("y aquí viene") + 0.2, 0.4, 0.4)
    for k, v in enumerate(S["vapor"]):
        if va < 0.01: v.location = LEJOS; continue
        u = (t * 0.3 + k / NV) % 1.0
        v.location = F + Vector((-0.08 + 0.016 * k, -0.04 + 0.03 * (k % 3), 0.2 + 0.13 * u)); v.scale = (va * (0.6 + u),) * 3
    apply_cam(S["cam"], *cam_cortes(t, CAM()))

def cam_cortes(t, ks, drift=0.002):
    """planos por corte: la cámara no viaja entre claves; cada plano empuja un 8 %; el último plano acaba en la clave del primero"""
    planos = []
    for k in ks:
        if planos and k[1] == planos[-1][1] and k[2] == planos[-1][2]: continue
        planos.append(k)
    i = 0
    while i + 1 < len(planos) and planos[i + 1][0] <= t: i += 1
    a = planos[i]; fin = planos[i + 1][0] if i + 1 < len(planos) else DUR + 0.4
    u = ss((t - a[0]) / max(fin - a[0], 0.3))
    if i + 1 >= len(planos) or planos[i + 1][0] > DUR: u = 1 - u
    tgt = Vector(a[2]); pos = tgt + (Vector(a[1]) - tgt) * (1 - 0.08 * u)
    pos += Vector((math.sin(t * 0.9), 0.7 * math.sin(t * 0.7), 0.8 * math.sin(t * 1.1))) * drift
    return pos, tgt, a[3]

def P(dx, dy, dz): return tuple(F + Vector((dx, dy, dz)))
COC = (0.1, 0.5, 0.9)
def CAM():
    k = Claves(); add = k.add
    ini = V(P(0, -0.02, 0.15), (0.22, -0.5, 0.1), 36)
    add(0.0, ini)
    add(1.4, V(P(0, 0, 0.2), (0.4, -0.75, 0.22), 34))
    add(T("escribe") - 0.2, V((-0.1, 0.5, 1.0), (-0.4, -1.5, 0.5), 30))
    add(T("la llenas") - 0.2, V(P(0, 0, 0.18), (0.08, -0.38, 0.32), 38))
    add(T("y sale blanda") - 0.2, V(P(0, -0.04, 0.16), (0.2, -0.32, 0.06), 40))
    add(T("tu freidora no") - 0.2, V(P(0, 0, 0.2), (0.5, -0.9, 0.3), 32))
    add(T("es un horno") - 0.2, V((0.25, 0.45, 0.75), (0.45, -1.8, 0.45), 30))
    add(T("arriba", 2) - 0.2, V(P(0, 0.02, 0.31), (0.18, -0.42, 0.02), 40))
    add(T("calienta") - 0.2, V(P(0, 0.02, 0.31), (-0.22, -0.4, 0.06), 40))
    add(T("un ventilador") - 0.2, V(P(0, 0.02, 0.34), (0.22, -0.42, -0.02), 40))
    add(T("contra la comida") - 0.2, V(P(0, 0, 0.18), (0.35, -0.62, 0.18), 34))
    add(T("ese aire") - 0.2, V(P(0, -0.03, 0.15), (0.15, -0.3, 0.08), 40))
    add(T("por eso se dora") - 0.2, V(P(0, -0.03, 0.15), (-0.2, -0.32, 0.1), 40))
    add(T("por eso el cesto") - 0.2, V(P(0, 0, 0.07), (-0.08, -0.3, 0.32), 38))
    add(T("pero llenas") - 0.2, V(P(0, 0, 0.18), (0.08, -0.38, 0.32), 38))
    add(T("cada patata") - 0.2, V(P(0, -0.03, 0.16), (0.1, -0.22, 0.05), 44))
    add(T("las patatas se tapan") - 0.2, V(P(0, 0, 0.16), (0.3, -0.5, 0.14), 36))
    add(T("así que el aire") - 0.2, V(P(0, 0, 0.16), (-0.3, -0.5, 0.14), 36))
    add(T("y en vez") - 0.2, V(P(0, -0.03, 0.16), (0.18, -0.3, 0.08), 40))
    add(T("se cuecen") - 0.2, V(P(0, 0, 0.24), (0.2, -0.42, 0.18), 38))
    add(T("y aquí viene") - 0.2, V(COC, (0.3, -2.4, 1.5), 30))
    add(T("el aire sube") - 0.2, V(P(0, 0, 0.28), (0.4, -0.75, 0.1), 34))
    add(T("tu horno") - 0.2, V((0.65, 0.5, 1.1), (-0.25, -1.9, 0.0), 30))
    add(T("tu freidora", 3) - 0.2, V(P(0, -0.1, 0.36), (0.2, -0.55, 0.15), 36))
    add(T("y si copias") - 0.2, V((0.25, 0.45, 0.8), (0.3, -1.5, 0.5), 32))
    add(T("baja") - 0.2, V(tuple(KNOB), (0.12, -0.28, 0.14), 40))
    add(T("qué haces") - 0.2, V(P(0, 0, 0.2), (0.5, -0.9, 0.3), 32))
    add(T("pon una sola") - 0.2, V(P(0, 0, 0.12), (0.08, -0.36, 0.3), 38))
    add(T("y sacude") - 0.2, V(P(0, -0.12, 0.14), (0.4, -0.6, 0.25), 34))
    add(T("te has acercado") - 0.2, V(COC, (-0.7, -2.6, 1.0), 30))
    add(T("y si quieres") - 0.2, V(P(0, 0, 0.2), (0.4, -0.75, 0.22), 34))
    add(T("lo más pedido") - 0.2, V((0.25, 0.45, 0.75), (0.45, -1.8, 0.45), 30))
    add(T("sígueme") - 0.2, V(COC, (0.3, -2.4, 1.3), 30))
    add(T("y ahora ya sabes") - 0.2, V(P(0, 0.02, 0.31), (0.18, -0.42, 0.02), 40))
    add(T("la freidora de tu") - 0.3, ini)
    add(DUR + 1, ini)
    return k.k

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, Vector(v))
    return {"res": Pj(F + Vector((0, 0.02, 0.42))), "cesto": Pj(F + Vector((0, 0, 0.3))), "horno": Pj(HORNO + Vector((0, 0, 0.34))),
            "display": Pj(F + Vector((0, -0.17, 0.47))), "mando": Pj(KNOB + Vector((0, 0, 0.08))), "reloj": Pj(RELOJ + Vector((0, 0, 0.25))),
            "vent": Pj(F + Vector((0, 0.02, 0.4)))}

if __name__ == "__main__":
    run("freidoraire", build, pose, anchors)
