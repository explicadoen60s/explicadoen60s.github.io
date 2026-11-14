# «¿Cuánta luz gasta tu lavadora solo calentando agua?» Lavadero de maqueta sobre una isla cortada (baldosas, hormigón,
# tierra): pared de azulejos, estante con detergentes, cesto de ropa, planta y contador de la luz en la pared. La lavadora
# (modelo «lavadora») tiene la pared izquierda cortada con una booleana (cantos crema): se ven el tambor abierto con la ropa
# que da vueltas, el agua con su superficie, la resistencia que se pone al rojo y echa burbujas, el motor con la correa y la
# polea. Una mano gira el mando (60 → 40). Termómetro grande de 15 a 60 °C, dos barras de kWh (20 °C: 0,33; 60 °C: 1,5),
# barra partida resistencia/motor (80-85 %), cuatro cestos (4 coladas por semana) y toallas con bacterias que desaparecen.
# Cámara por cortes (lección de nevera, 14-nov): cada plano empuja un 8 % y cambia de golpe; nunca viaja a través de nada.
# Planos (fotografía → motion; esquina libre arriba-izquierda salvo el mini del juego):
#  0 mando girando con la mano a 0,7 m · 1,6 tambor abierto con la resistencia · 3,3 lavadero · 5,4 mando · 7,7 tambor ·
#  9,2 resistencia al rojo · 11,4 motor · 14,3 lavadero · 16,2 termómetro · 20 tambor con ropa · 22,9 barras ·
#  27,5 contador · 31,3 lavadero alto · 32,9 barra partida · 38 resistencia · 40,3 mando a 40 · 42,8 contador ·
#  45,8 cuatro cestos · 47,5 toallas · 50,3 toallas y lavadora · 53,9 mando · 54,7 mano a 40 · 56,9 tambor · 57,9 contador ·
#  58,9 lavadero · 59,9 tambor · 63,2 lavadero · 64,9 lavadero · 66,1 resistencia · 68,1 vuelta al primer plano.
import bpy, math, sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from modelos import *
from maqueta import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("lavar30")
SUELO = (0.90, 0.86, 0.80); PIEL = (0.96, 0.78, 0.64); BACT = (0.45, 0.85, 0.30); BURB = (0.80, 0.92, 1.0)
L = Vector((0.0, 0.4, 0.0))                          # lavadora (frontal en y = 0.11)
KNOB = L + Vector((0.19, -0.302, 0.785))
DRUM = L + Vector((0.05, 0.02, 0.45))
RES = L + Vector((-0.06, 0.04, 0.18))
MOTOR = L + Vector((0.08, 0.18, 0.1))
TERMO = Vector((-0.8, 0.5, 0.0))
METER = Vector((0.85, 0.71, 1.25))
BARS = Vector((0.85, 0.25, 0.0))
SPLIT = Vector((1.3, 0.25, 0.0))
TOALLA = L + Vector((0.0, 0.05, 0.86))
CESTOS = [Vector((-1.05 + 0.33 * k, -0.55, 0.0)) for k in range(4)]
SALA = (0.1, 0.3, 0.55)
NB, NR = 14, 9

def ang_mando(t):
    """grados del mando (−90 = 20 °C, −45 = 30, 0 = 40, 45 = 60, 90 = 90)"""
    g, s6 = T("giras"), T("sesenta grados", fin=True); b, c1 = T("si bajas"), T("cuarenta", fin=True)
    q, c2 = T("qué haces"), T("cuarenta", 2, fin=True); f = T("tu lavadora calentando") - 0.3
    if t < g - 0.05: return mix(-45, 45, seg(t, 0.1, 1.4))
    if t < b - 0.05: return mix(-90, 45, seg(t, g + 0.3, s6))
    if t < q - 0.05: return mix(45, 0, seg(t, b + 0.4, c1))
    if t < f: return mix(45, 0, seg(t, q + 1.1, c2))
    return mix(0, -45, seg(t, f, f + 0.5)) if t < f + 0.6 else -45

def calor(t):
    """0..1: lo roja que está la resistencia"""
    return keyed(t, [(0, 0.85), (T("dentro") - 0.1, 0.1), (T("una resistencia") + 0.2, 0.1), (T("al rojo", fin=True), 1.0),
                     (T("si bajas"), 1.0), (T("cuarenta", fin=True), 0.55), (T("qué haces"), 1.0), (T("cuarenta", 2, fin=True), 0.55),
                     (T("tu lavadora calentando") - 0.3, 0.55), (T("tu lavadora calentando"), 0.85)])

def temp(t):
    return keyed(t, [(0, 15.0), (T("subir el agua"), 15.0), (T("cuesta", fin=True), 60.0), (T("si bajas"), 60.0), (T("cuarenta", fin=True), 40.0)])

def build():
    sc, cam = scene_setup(world=PAL["cielo"], shadow=0.25, light_rot=55); entorno_claro(sc)
    S = {"cam": cam}
    nubes(8, (0.0, 6.0, 3.0), 6, 0.8, 1.0, s=1.1, seed=12)
    # ---------- lavadero ----------
    isla(3.4, 2.2, (0.15, 0.1, 0), capas=[(SUELO, 0.08), (PAL["hormigon"], 0.16), (PAL["tierra"], 0.32), (PAL["tierra2"], 0.36)])
    for k in range(9): box((0.012, 2.2, 0.006), (-1.45 + k * 0.4, 0.1, 0.003), (0.80, 0.76, 0.70))
    for k in range(6): box((3.4, 0.012, 0.006), (0.15, -0.9 + k * 0.4, 0.003), (0.80, 0.76, 0.70))
    box((3.4, 0.1, 2.2), (0.15, 0.8, 1.1), PAL["pared"]); box((3.4, 0.102, 0.03), (0.15, 0.8, 2.185), PAL["corte"])
    azulejos(3.2, 0.9, (0.15, 0.74, 0.95), color=PAL["menta"], paso=0.15)
    caja((0.9, 0.22, 0.03), (0.0, 0.62, 1.55), PAL["madera"], r=0.01)                             # estante
    for k, c in enumerate(((0.35, 0.6, 0.95), (0.95, 0.5, 0.6), (0.55, 0.85, 0.5))):
        cilindro(0.05, 0.2, (-0.25 + 0.22 * k, 0.62, 1.67), c, r=0.02); cilindro(0.02, 0.04, (-0.25 + 0.22 * k, 0.62, 1.79), (0.96, 0.96, 0.96), r=0.008)
    planta((1.45, 0.45, 0.0), 1.3)
    alfombrilla((0.0, -0.3, 0.01), 0.6, 0.4, color=(0.55, 0.75, 0.95))
    cilindro(0.2, 0.32, (-1.2, -0.05, 0.16), (0.92, 0.80, 0.55), r=0.04)                         # cesto de mimbre
    for k in range(4): bola(0.08, (-1.26 + 0.05 * k, -0.08 + 0.03 * (k % 2), 0.34), ((0.95, 0.45, 0.5), (0.4, 0.6, 0.95), (0.98, 0.9, 0.4), (0.6, 0.85, 0.6))[k], escala=(1.2, 1, 0.6))
    # contador de la luz (con disco que gira según el gasto)
    caja((0.36, 0.1, 0.46), tuple(METER), (0.93, 0.93, 0.95), r=0.03)
    caja((0.26, 0.02, 0.1), tuple(METER + Vector((0, -0.055, 0.1))), (0.15, 0.2, 0.25), r=0.01)
    caja((0.28, 0.02, 0.16), tuple(METER + Vector((0, -0.052, -0.09))), (0.75, 0.88, 0.95), r=0.01)
    S["disco"] = empty(tuple(METER + Vector((0, -0.06, -0.09)))); S["disco"].rotation_mode = 'XYZ'
    cilindro(0.1, 0.01, (0, 0, 0), (0.70, 0.72, 0.76), S["disco"], rot=(math.pi / 2, 0, 0), r=0.003)
    box((0.03, 0.012, 0.012), (0.08, -0.008, 0), PAL["rojo"], S["disco"])
    tubo([METER + Vector((0.12, 0, -0.23)), METER + Vector((0.12, 0, -0.5)), Vector((0.3, 0.71, 0.75)), Vector((0.3, 0.71, 0.4))], 0.012, (0.3, 0.3, 0.32))
    # ---------- lavadora con la pared izquierda cortada ----------
    S["lav"] = lavadora(tuple(L))
    ch = {o.name.split(".")[0]: o for o in S["lav"].children_recursive}
    S["pared"] = ch["pared_izq"]; S["pared"].data.materials.append(mat(PAL["corte"]))
    S["cut"] = cortador((0.2, 0.5, 0.7), tuple(L + Vector((-0.3, 0.0, 0.41))))
    cortar(S["pared"], S["cut"])                                                     # corte real: modificador BOOLEAN
    S["mando"], S["tambor"], S["polea"] = ch["mando"], ch["tambor"], ch["polea"]
    # resistencia (en U bajo el tambor), agua con su superficie, burbujas
    S["res"] = tubo([RES + Vector((0, -0.22, 0)), RES + Vector((0, 0.04, 0)), RES + Vector((0.07, 0.04, 0)), RES + Vector((0.07, -0.22, 0))], 0.019, (0.45, 0.45, 0.48), unique=True)
    caja((0.13, 0.03, 0.06), tuple(RES + Vector((0.035, -0.24, 0))), (0.3, 0.3, 0.32), r=0.01)
    S["agua"] = box((0.24, 0.42, 0.006), tuple(L + Vector((0.11, 0.02, 0.31))), (0.45, 0.72, 1.0), unique=True)
    S["burb"] = [sph(0.012, LEJOS, BURB, seg=8) for _ in range(NB)]
    # ropa dentro del tambor (8 kg de algodón)
    S["ropa"] = [caja((0.07, 0.12, 0.05), LEJOS, c, r=0.02) for c in ((0.95, 0.45, 0.5), (0.4, 0.6, 0.95), (0.98, 0.9, 0.4), (0.6, 0.85, 0.6),
                                                                     (0.95, 0.65, 0.3), (0.75, 0.55, 0.9), (0.98, 0.98, 0.98), (0.4, 0.8, 0.85))]
    # motor y correa
    cilindro(0.07, 0.16, tuple(MOTOR), (0.35, 0.38, 0.42), rot=(math.pi / 2, 0, 0), r=0.02)
    for k in range(4): box((0.145, 0.01, 0.01), tuple(MOTOR + Vector((0, -0.05 + 0.03 * k, 0.07))), (0.25, 0.27, 0.3))
    S["polea_m"] = empty(tuple(MOTOR + Vector((0, 0.1, 0)))); S["polea_m"].rotation_mode = 'XYZ'
    cilindro(0.035, 0.02, (0, 0, 0), (0.6, 0.62, 0.66), S["polea_m"], rot=(math.pi / 2, 0, 0), r=0.004)
    box((0.06, 0.022, 0.008), (0, 0, 0), (0.3, 0.3, 0.32), S["polea_m"])
    pc = L + Vector((0, 0.24, 0.45)); pm = MOTOR + Vector((0, 0.1, 0))
    for sg in (-1, 1):
        a = pm + Vector((0.035 * sg, 0, 0)); b = pc + Vector((0.19 * sg, 0, 0)); o = bar_obj((0.12, 0.12, 0.13), r=0.007); bar_set(o, a, b)
    S["fl_motor"] = flecha3d(LEJOS, (1, 0, 0.3), 0.18, 0.018, color=PAL["rojo"])
    # mano (gira el mando)
    S["mano"] = empty(LEJOS); S["mano"].rotation_mode = 'XYZ'
    caja((0.09, 0.06, 0.07), (0, -0.05, 0), PIEL, S["mano"], r=0.025)
    for k in range(3): cilindro(0.011, 0.05, (-0.03 + 0.03 * k, -0.01, 0.045), PIEL, S["mano"], r=0.005)
    cilindro(0.012, 0.045, (0.055, -0.015, 0.0), PIEL, S["mano"], rot=(0, math.pi / 2, 0), r=0.005)
    cilindro(0.04, 0.3, (0, -0.22, -0.03), (0.95, 0.55, 0.3), S["mano"], rot=(math.pi / 2, 0, 0), r=0.015)
    # termómetro grande (15 → 60 °C)
    caja((0.16, 0.1, 0.95), tuple(TERMO + Vector((0, 0, 0.52))), (0.99, 0.99, 0.99), r=0.04)
    caja((0.3, 0.3, 0.05), tuple(TERMO + Vector((0, 0, 0.025))), (0.5, 0.52, 0.56), r=0.02)
    bola(0.055, tuple(TERMO + Vector((0, -0.04, 0.14))), PAL["rojo"])
    box((0.03, 0.01, 0.72), tuple(TERMO + Vector((0, -0.05, 0.55))), (0.88, 0.92, 0.96))
    for k in range(11): box((0.04 if k % 5 else 0.06, 0.01, 0.006), tuple(TERMO + Vector((0.045, -0.052, 0.2 + 0.07 * k))), (0.3, 0.3, 0.35))
    S["columna"] = box((1, 1, 1), LEJOS, PAL["rojo"], unique=True)
    # barras de kWh (20 °C y 60 °C) y barra partida resistencia / motor
    for k in range(2):
        caja((0.22, 0.22, 0.04), tuple(BARS + Vector((-0.13 + 0.26 * k, 0, 0.02))), (0.3, 0.32, 0.36), r=0.015)
        text3d(("20°", "60°")[k], tuple(BARS + Vector((-0.13 + 0.26 * k, -0.115, 0.045))), 0.07, (0.99, 0.99, 0.99), rot=(math.pi / 2, 0, 0), extrude=0.005)
    S["b20"] = box((1, 1, 1), LEJOS, (0.45, 0.70, 1.0), unique=True); S["b60"] = box((1, 1, 1), LEJOS, PAL["rojo"], unique=True)
    caja((0.26, 0.26, 0.04), tuple(SPLIT + Vector((0, 0, 0.02))), (0.3, 0.32, 0.36), r=0.015)
    S["s_res"] = box((1, 1, 1), LEJOS, PAL["rojo"], unique=True); S["s_mot"] = box((1, 1, 1), LEJOS, (0.55, 0.6, 0.68), unique=True)
    # cuatro cestos de ropa y toallas con bacterias
    S["cestos"] = []
    for k, c in enumerate(CESTOS):
        e = empty(LEJOS); cilindro(0.12, 0.2, (0, 0, 0.1), (0.92, 0.80, 0.55), e, r=0.03)
        bola(0.06, (0.0, 0.0, 0.2), ((0.95, 0.45, 0.5), (0.4, 0.6, 0.95), (0.98, 0.9, 0.4), (0.6, 0.85, 0.6))[k], e, escala=(1.3, 1.2, 0.6))
        S["cestos"].append(e)
    S["toallas"] = empty(LEJOS)
    for k, c in enumerate(((0.97, 0.6, 0.68), (0.99, 0.99, 0.99), (0.55, 0.75, 0.95))):
        caja((0.34, 0.24, 0.05), (0, 0, 0.025 + 0.05 * k), c, S["toallas"], r=0.02)
    S["bact"] = [bola(0.012, LEJOS, BACT, sub=1) for _ in range(NR)]
    dyn = [cam, S["disco"], S["lav"], S["pared"], S["cut"], S["res"], S["agua"], S["burb"], S["ropa"], S["polea_m"], S["fl_motor"],
           S["mano"], S["columna"], S["b20"], S["b60"], S["s_res"], S["s_mot"], S["cestos"], S["toallas"], S["bact"]]
    join_static(dyn)
    return sc, S

def back_(u):
    u = max(0.0, min(1.0, u)); c = 1.70158
    return 1 + (c + 1) * (u - 1) ** 3 + c * (u - 1) ** 2

def bar(o, base, w, d, h):
    if h < 0.002: o.location = LEJOS; return
    o.location = base + Vector((0, 0, 0.04 + h / 2)); o.scale = (w, d, h)

def pose(t, S):
    S["mando"].rotation_euler = (0, math.radians(ang_mando(t)), 0)
    c = calor(t)
    set_color(S["res"], (mix(0.45, 1.0, c), mix(0.45, 0.25, c), mix(0.48, 0.12, c)))
    # tambor: gira despacio (el motor hace poca fuerza); la ropa da vueltas por la mitad que se ve
    S["tambor"].rotation_euler = (0, t * 1.6, 0); S["polea"].rotation_euler = (0, t * 1.6, 0); S["polea_m"].rotation_euler = (0, t * 9, 0)
    for k, r in enumerate(S["ropa"]):
        a = t * 1.6 + k * 0.42; ang = -1.25 + ((a % 2.5) / 2.5) * 1.6; rad = 0.15 - 0.03 * (k % 3)
        r.location = DRUM + Vector((rad * math.cos(ang) + 0.02, -0.12 + 0.08 * (k % 4), rad * math.sin(ang)))
        r.rotation_euler = (t + k, 0.3 * k, t * 0.7)
    for k, b in enumerate(S["burb"]):
        if c < 0.4: b.location = LEJOS; continue
        u = (t * 0.8 + k / NB) % 1.0
        b.location = RES + Vector((0.035 + 0.03 * math.sin(k * 2.3), -0.2 + 0.24 * ((k * 0.37) % 1.0), 0.02 + 0.07 * u)); b.scale = ((c - 0.4) / 0.6 * (1 - u * 0.5),) * 3
    S["disco"].rotation_euler = (0, t * (1.5 + 10 * c), 0)
    w = win01(t, T("el motor") - 0.1, T("pero calentar") - 0.2, 0.3, 0.3)
    S["fl_motor"].location = MOTOR + Vector((-0.05, -0.12, 0.14)) if w > 0.01 else LEJOS; S["fl_motor"].scale = (max(w * 0.6, 0.001),) * 3
    # mano en el mando
    tramos = [(0.0, 1.6), (T("giras") - 0.2, T("sesenta grados", fin=True) + 0.4), (T("si bajas") - 0.1, T("cuarenta", fin=True) + 0.4),
              (T("gira ahora") - 0.4, T("cuarenta", 2, fin=True) + 0.4), (T("tu lavadora calentando") - 0.4, DUR + 0.5)]
    h = max(win01(t, a, b, 0.25, 0.25) for a, b in tramos)
    if h > 0.01 or t < 0.3:
        hh = 1.0 if t < 0.3 else h
        S["mano"].location = KNOB + Vector((0, -0.03 - 0.25 * (1 - hh), 0)); S["mano"].rotation_euler = (0, math.radians(ang_mando(t)), 0)
    else: S["mano"].location = LEJOS
    # termómetro
    hcol = 0.72 * temp(t) / 100.0
    S["columna"].location = TERMO + Vector((0, -0.056, 0.19 + hcol / 2)); S["columna"].scale = (0.022, 0.008, hcol)
    # barras de kWh: 20 °C → 0,33; 60 °C → 1,5 (×0,6 m por kWh)
    u20 = seg(t, T("de veinte") - 0.1, T("de veinte") + 0.6); u60 = seg(t, T("de cero coma"), T("uno coma cinco", fin=True))
    vis = t > T("de veinte") - 0.3
    bar(S["b20"], BARS + Vector((-0.13, 0, 0)), 0.16, 0.16, 0.2 * u20 if vis else 0)
    bar(S["b60"], BARS + Vector((0.13, 0, 0)), 0.16, 0.16, (0.2 * u20 + 0.7 * u60 + 0.2 * seg(t, T("el gasto"), T("cuatro", fin=True)) * (1 - u60)) if vis else 0)
    # barra partida: resistencia 80-85 % y motor
    us = seg(t, T("entre el ochenta") - 0.2, T("calentar el agua", fin=True))
    bar(S["s_res"], SPLIT, 0.18, 0.18, 0.82 * 0.9 * us)
    sm = 0.18 * 0.9 * us
    if sm > 0.002: S["s_mot"].location = SPLIT + Vector((0, 0, 0.04 + 0.82 * 0.9 * us + sm / 2)); S["s_mot"].scale = (0.18, 0.18, sm)
    else: S["s_mot"].location = LEJOS
    # cuatro cestos (cuatro coladas por semana)
    for k, e in enumerate(S["cestos"]):
        u = seg(t, T("con cuatro") + 0.25 * k, T("con cuatro") + 0.25 * k + 0.4)
        if u < 0.01: e.location = LEJOS; continue
        e.location = CESTOS[k]; s_ = back_(u); e.scale = (s_, s_, s_)
    # toallas encima de la lavadora con bacterias que desaparecen con el calor
    ut = seg(t, T("pero y la") - 0.2, T("pero y la") + 0.3)
    S["toallas"].location = TOALLA if ut > 0.01 else LEJOS
    vb = win01(t, T("pero y la") - 0.1, T("desinfecta", fin=True) + 0.1, 0.3, 0.6)
    rb = random.Random(4)
    for k, b in enumerate(S["bact"]):
        x, y = rb.uniform(-0.15, 0.15), rb.uniform(-0.1, 0.1)
        if vb < 0.01: b.location = LEJOS; continue
        b.location = TOALLA + Vector((x, y, 0.155)); b.scale = (vb * (1 + 0.3 * math.sin(t * 6 + k)),) * 3
    apply_cam(S["cam"], *cam_cortes(t, CAM()))

def cam_cortes(t, ks, drift=0.003):
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

def CAM():
    k = Claves(); add = k.add
    ini = V(tuple(KNOB), (-0.32, -0.6, 0.14), 38)
    add(0.0, ini)
    add(1.6, V(tuple(DRUM + Vector((0, 0, -0.08))), (-0.95, -0.55, 0.22), 34))
    add(T("escribe") - 0.2, V(SALA, (-1.1, -2.7, 1.2), 30))
    add(T("giras") - 0.2, V(tuple(KNOB), (-0.2, -0.5, 0.1), 40))
    add(T("dentro") - 0.2, V(tuple(DRUM + Vector((0, 0, -0.08))), (-0.95, -0.45, 0.2), 34))
    add(T("una resistencia") + 0.6, V(tuple(RES), (-0.55, -0.28, 0.14), 40))
    add(T("el motor") - 0.2, V(tuple(MOTOR), (-0.55, -0.1, 0.2), 38))
    add(T("con poca") - 0.2, V(tuple(DRUM), (-0.7, -0.3, 0.15), 38))
    add(T("pero calentar") - 0.2, V(SALA, (1.0, -2.5, 1.0), 30))
    add(T("subir el agua") - 0.2, V(tuple(TERMO + Vector((0.2, 0, 0.55))), (-0.35, -1.6, 0.3), 32))
    add(T("mira una") - 0.2, V(tuple(DRUM), (-1.0, -0.7, 0.4), 32))
    add(T("de veinte") - 0.2, V(tuple(BARS + Vector((0, 0, 0.45))), (-0.45, -1.7, 0.45), 32))
    add(T("el gasto") - 0.1, V(tuple(BARS + Vector((0.32, 0, 0.6))), (0.4, -1.5, 0.3), 32))
    add(T("de cero coma") - 0.2, V((0.85, 0.5, 0.85), (-0.2, -2.0, 0.15), 30))
    add(T("y aquí viene") - 0.2, V(SALA, (0.0, -1.6, 1.2), 40))
    add(T("entre el ochenta") - 0.2, V(tuple(SPLIT + Vector((-0.2, 0, 0.45))), (-0.5, -1.6, 0.35), 32))
    add(T("casi todo") - 0.2, V(tuple(RES), (-0.5, -0.36, 0.17), 40))
    add(T("si bajas") - 0.2, V(tuple(KNOB), (-0.3, -0.5, 0.1), 40))
    add(T("ahorras") - 0.2, V(tuple(METER + Vector((-0.1, 0, -0.2))), (-0.3, -1.1, 0.1), 34))
    add(T("con cuatro") - 0.2, V(tuple(CESTOS[1] + Vector((0.15, 0, 0.15))), (-0.3, -1.4, 0.55), 32))
    add(T("pero y la") - 0.2, V(tuple(TOALLA), (-0.45, -0.8, 0.3), 36))
    add(T("el calor") - 0.2, V(tuple(TOALLA), (-0.3, -0.55, 0.2), 40))
    add(T("así que guarda") - 0.2, V(tuple(L + Vector((0, 0, 0.6))), (0.6, -1.7, 0.6), 32))
    add(T("qué haces") - 0.2, V(tuple(KNOB), (0.25, -0.5, 0.1), 40))
    add(T("gira ahora") + 0.4, V(tuple(KNOB), (-0.3, -0.45, 0.12), 40))
    add(T("mismo lavado") - 0.2, V(tuple(DRUM), (-1.0, -0.5, 0.3), 32))
    add(T("y menos luz") - 0.2, V(tuple(METER + Vector((-0.1, 0, -0.2))), (-0.3, -1.1, 0.1), 34))
    add(T("te has acercado") - 0.2, V(SALA, (-1.1, -2.7, 1.2), 30))
    add(T("y si quieres") - 0.2, V(tuple(DRUM), (-1.0, -0.7, 0.4), 32))
    add(T("pídelo") - 0.2, V(tuple(RES), (-0.5, -0.36, 0.17), 40))
    add(T("lo más pedido") - 0.2, V(SALA, (1.0, -2.5, 1.0), 30))
    add(T("sígueme") - 0.2, V(SALA, (0.0, -2.9, 1.6), 30))
    add(T("y ahora ya sabes") - 0.2, V(tuple(RES), (-0.55, -0.28, 0.14), 40))
    add(T("tu lavadora calentando") - 0.3, ini)
    add(DUR + 1, ini)
    return k.k

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, Vector(v))
    return {"mando": Pj(KNOB + Vector((0, 0, 0.12))), "termo": Pj(TERMO + Vector((0, 0, 1.1))), "drum": Pj(DRUM + Vector((0, 0, 0.3))),
            "bars": Pj(BARS + Vector((0.13, 0, 1.05))), "meter": Pj(METER + Vector((0, 0, 0.3))), "split": Pj(SPLIT + Vector((0, 0, 1.05))),
            "res": Pj(RES + Vector((0, 0, 0.08))), "cestos": Pj(CESTOS[1] + Vector((0.15, 0, 0.45))), "toalla": Pj(TOALLA + Vector((0, 0, 0.3)))}

if __name__ == "__main__":
    run("lavar30", build, pose, anchors)
