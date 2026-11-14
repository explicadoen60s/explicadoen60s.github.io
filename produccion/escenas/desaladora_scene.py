# «¿Cuánta agua bebible hace la desaladora del Llobregat?» (Lo que esconde tu ciudad): maqueta de la planta junto al mar
# sobre una isla cortada. Torre de toma en el mar, tubería abierta con agua y sal, bomba de alta presión con su rodete,
# manómetro de 1 a 60 bar con una rueda de coche al lado (2,3 bar), tubo de membranas abierto en dos (el agua pasa la
# membrana y la sal no), depósito de agua potable (45 de cada 100 litros), salmuera que vuelve al mar, recuperador de
# presión que gira y barra de energía que baja a la mitad. Aparte: la ciudad con poca lluvia y un río casi seco, y una
# isla con 80 piscinas olímpicas que se llenan.
# Cámara por cortes (lección de nevera, 14-nov): cada plano empuja un 8 % y cambia de golpe; nunca viaja a través de nada.
# Planos (fotografía → motion; esquina libre arriba-izquierda salvo el mini del juego, que la ocupa desde 2,6 s):
#  0 bomba y tubería con agua a 1,6 m · 1,5 planta entera · 3,2 otro lado · 6 ciudad · 7,4 nube · 8,3 ciudad y mar ·
#  9,8 torre de toma · 11,9 sal en la tubería · 12,9 tubería · 14,3 tubo de membranas · 15,8 membrana cerca ·
#  17,6 tubo de lado · 19,8 agua parada · 21,5 bomba · 23,8 manómetro · 25,1 manómetro y rueda · 28,1 entrada (100 L) ·
#  30 depósito (45 L) · 32,1 salmuera · 33,9 vuelta al mar · 34,8 recuperador · 37,4 barra de energía · 39,3 planta alta ·
#  40,9 planta · 43,4 depósito con la cifra · 46 piscinas · 47,6 piscinas cerca · 49,4 piscinas · 51,7 planta ·
#  52,7 ciudad · 56,2 membranas · 59,3 bomba · 61 planta · 62,2 tubería · 64,4 vuelta al primer plano.
import bpy, math, sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from modelos import *
from maqueta import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("desaladora")
ARENA = (0.96, 0.86, 0.62); AZUL_T = (0.30, 0.52, 0.86); GRIS = (0.80, 0.82, 0.86); SAL = (0.99, 0.99, 1.0)
MEMB = (1.0, 0.80, 0.25); SALM = (0.36, 0.50, 0.62); VERDE = (0.35, 0.78, 0.45); ACERO = (0.70, 0.73, 0.78)
YP = -1.0                                           # plano de las tuberías abiertas (se ven desde -Y)
PUMP = Vector((0.55, YP, 0.3))                      # bomba de alta presión (eje Y)
VX0, VX1, VZ, VR = 1.4, 3.5, 0.75, 0.3              # tubo de membranas
MAN = Vector((1.15, -1.3, 1.0))                     # manómetro
RUEDA = Vector((1.85, -1.55, 0.3))
TANQ = Vector((4.25, -1.0, 0.0))                    # depósito de agua potable
REC = Vector((0.95, -0.25, 0.35))                   # recuperador de presión (eje X)
BARRA = Vector((0.0, -0.35, 0.0))                   # barra de energía
C0 = Vector((0.5, 10.0, 0.0))                       # isla de la ciudad
P0 = Vector((13.0, 0.0, 0.0))                       # isla de las 80 piscinas
TOMA = [(-2.6, YP, -0.15), (-2.6, YP, 0.18), (-1.9, YP, 0.18), (0.3, YP, 0.18), (0.3, YP, 0.3)]
ALTA = [(0.8, YP, 0.3), (1.05, YP, 0.3), (1.15, YP, 0.75), (VX0, YP, VZ)]
SALMP = [(VX1 + 0.1, YP, VZ + 0.1), (VX1 + 0.3, YP, VZ + 0.1), (VX1 + 0.3, -0.25, VZ + 0.1), (REC.x + 0.4, -0.25, 0.35),
         (REC.x - 0.35, -0.25, 0.35), (-0.6, -0.25, 0.35), (-0.6, -0.25, 0.12), (-2.0, -0.25, 0.12), (-2.6, -0.25, -0.1)]
DULCE = [(VX1 - 0.1, YP, VZ - 0.25), (VX1 - 0.1, YP, 0.25), (TANQ.x - 0.3, YP, 0.25)]
PT_TOMA, PT_ALTA, PT_SALM, PT_DULCE = poly(TOMA), poly(ALTA), poly(SALMP), poly(DULCE)
NF, NS, NM, NMS, NB, NP = 34, 10, 22, 10, 24, 80

def build():
    sc, cam = scene_setup(world=PAL["cielo"], shadow=0.25, light_rot=40); entorno_claro(sc)
    S = {"cam": cam}
    nubes(9, (1.0, 6.5, 3.6), 7, 1.0, 1.0, s=1.3, seed=4)
    # ---------- isla de la planta, playa y mar ----------
    isla(6.2, 5.0, (1.9, 0.5, 0), capas=[(PAL["hormigon"], 0.08), (PAL["tierra"], 0.5), (PAL["tierra2"], 0.5)])
    box((1.0, 5.0, 0.07), (-1.7, 0.5, -0.035), ARENA); box((1.0, 5.0, 1.01), (-1.7, 0.5, -0.575), PAL["tierra"])
    S["mar"] = box((2.4, 5.0, 0.62), (-3.4, 0.5, -0.36), PAL["agua"], unique=True); S["mar"].data.materials.append(mat(PAL["corte"]))
    S["cut_mar"] = cortador((0.9, 1.02, 0.7), (-2.6, -1.5, -0.33)); cortar(S["mar"], S["cut_mar"])   # muesca para ver la torre por dentro
    box((2.4, 5.0, 0.46), (-3.4, 0.5, -0.9), ARENA)
    for k in range(1, 5): box((2.4, 0.02, 0.012), (-3.4, -1.5 + k * 0.8, -0.045), (0.62, 0.82, 1.0))   # olas
    box((0.16, 5.0, 0.012), (-2.24, 0.5, -0.045), (1, 1, 1))                                          # espuma de la orilla
    # nave de la planta (cortada: sin techo ni pared delantera)
    caja((4.0, 0.12, 1.5), (2.2, 1.0, 0.75), PAL["pared"], r=0.02); caja((0.12, 2.2, 1.5), (4.2, -0.05, 0.75), PAL["pared"], r=0.02)
    box((4.0, 0.125, 0.04), (2.2, 1.0, 1.5), PAL["corte"]); box((0.125, 2.2, 0.04), (4.2, -0.05, 1.5), PAL["corte"])
    for k in range(4): ventana((0.7 + k * 0.9, 0.93, 1.0), 0.8)
    for x in (0.3, 4.6): arbol((x, 1.9, 0.0), 0.6, seed=int(x * 10)); arbusto((x + 0.35, 1.6, 0), 0.6)
    farola((-0.9, -1.6, 0.0), 0.5)
    # torre de toma en el mar y tubería abierta hasta la bomba
    # torre de toma cortada por la mitad (corte real: modificador BOOLEAN) con el agua del mar subiendo por dentro
    S["torre"] = cilindro(0.16, 0.85, (-2.6, YP, -0.38), GRIS, r=0.03, unique=True); S["torre"].data.materials.append(mat(PAL["corte"]))
    m = S["torre"].modifiers.new("hueco", "SOLIDIFY"); m.thickness = 0.03; m.offset = -1
    S["cut_torre"] = cortador((0.5, 0.3, 1.2), (-2.6, YP - 0.15, -0.3))
    caja((0.86, 1.0, 0.04), (-2.6, -1.5, -0.66), ARENA, r=0.01)                      # fondo del mar en la muesca
    cortar(S["torre"], S["cut_torre"])
    cyl(0.12, 0.8, (-2.6, YP + 0.02, -0.42), (0.35, 0.62, 1.0))
    for k in range(6): caja((0.04, 0.34, 0.08), (-2.6 + 0.17 * math.cos(k), YP + 0.17 * math.sin(k), 0.0), (0.3, 0.32, 0.36), r=0.01)
    cilindro(0.2, 0.05, (-2.6, YP, 0.06), (0.95, 0.4, 0.3), r=0.015)
    S["t_toma"] = medio_tubo([Vector(p) for p in TOMA[1:]], 0.11, 0.025, AZUL_T)
    for x in (-1.6, -0.9, -0.2): caja((0.08, 0.2, 0.12), (x, YP + 0.02, 0.06), GRIS, r=0.02)
    # bomba de alta presión: carcasa, rodete (gira) y motor
    cilindro(0.26, 0.24, tuple(PUMP + Vector((0, 0.1, 0))), (0.25, 0.45, 0.85), rot=(math.pi / 2, 0, 0), r=0.04)
    torus(0.24, 0.035, tuple(PUMP + Vector((0, -0.04, 0))), (0.25, 0.45, 0.85), rot=(math.pi / 2, 0, 0))
    caja((0.36, 0.4, 0.36), tuple(PUMP + Vector((0, 0.45, 0.0))), (0.30, 0.32, 0.36), r=0.04)
    for k in range(5): box((0.37, 0.02, 0.3), tuple(PUMP + Vector((0, 0.3 + 0.07 * k, 0))), (0.4, 0.42, 0.46))
    caja((0.5, 0.7, 0.1), tuple(PUMP + Vector((0, 0.25, -0.25))), GRIS, r=0.02)
    S["rodete"] = empty(tuple(PUMP + Vector((0, -0.03, 0)))); S["rodete"].rotation_mode = 'XYZ'
    cilindro(0.05, 0.05, (0, 0, 0), ACERO, S["rodete"], rot=(math.pi / 2, 0, 0))
    for k in range(6):
        a = k * math.pi / 3
        caja((0.17, 0.03, 0.05), (0.1 * math.cos(a), 0, 0.1 * math.sin(a)), (0.96, 0.75, 0.25), S["rodete"], rot=(0, -a + 0.4, 0), r=0.01)
    # tubería de alta presión (abierta) hasta las membranas, con el manómetro
    S["t_alta"] = medio_tubo([Vector(p) for p in ALTA], 0.08, 0.03, (0.85, 0.3, 0.28))
    cilindro(0.015, 0.36, (MAN.x, MAN.y + 0.2, MAN.z - 0.3), ACERO, r=0.005)
    cilindro(0.19, 0.06, tuple(MAN), ACERO, rot=(math.pi / 2, 0, 0), r=0.02)
    cilindro(0.165, 0.03, tuple(MAN + Vector((0, -0.025, 0))), (0.99, 0.99, 0.97), rot=(math.pi / 2, 0, 0), r=0.005)
    for k in range(8):
        a = math.radians(210 - 240 * k / 7)
        box((0.012, 0.01, 0.04), tuple(MAN + Vector((0.13 * math.cos(a), -0.045, 0.13 * math.sin(a)))), (0.2, 0.2, 0.25), rot=(0, -a + math.pi / 2, 0))
    a = math.radians(210 - 240 * 6 / 7)
    for k in range(3): box((0.03, 0.012, 0.03), tuple(MAN + Vector(((0.1 + 0.02 * k) * math.cos(a - 0.15 * k), -0.046, (0.1 + 0.02 * k) * math.sin(a - 0.15 * k)))), PAL["rojo"])
    S["aguja"] = empty(tuple(MAN + Vector((0, -0.05, 0)))); S["aguja"].rotation_mode = 'XYZ'
    caja((0.012, 0.012, 0.13), (0, 0, 0.055), PAL["rojo"], S["aguja"], r=0.004); bola(0.02, (0, 0, 0), (0.2, 0.2, 0.22), S["aguja"])
    # rueda de coche junto al manómetro
    S["rueda"] = empty(tuple(RUEDA)); S["rueda"].rotation_mode = 'XYZ'
    torus(0.22, 0.09, (0, 0, 0), (0.16, 0.16, 0.18), S["rueda"], rot=(math.pi / 2, 0, 0))
    cilindro(0.14, 0.12, (0, 0, 0), (0.80, 0.82, 0.86), S["rueda"], rot=(math.pi / 2, 0, 0), r=0.02)
    for k in range(5): caja((0.03, 0.13, 0.1), (0.07 * math.cos(k * 1.257), -0.01, 0.07 * math.sin(k * 1.257)), (0.6, 0.62, 0.66), S["rueda"], rot=(0, -k * 1.257, 0), r=0.01)
    caja((0.5, 0.5, 0.04), (RUEDA.x, RUEDA.y, 0.0), PAL["amarillo"], r=0.01)
    # tubo de membranas abierto en dos: cámara de arriba (mar), membrana amarilla, cámara de abajo (agua potable)
    pts = [Vector((VX0, YP, VZ)), Vector((VX1, YP, VZ))]
    S["vaso"] = medio_tubo(pts, VR, 0.04, (0.95, 0.96, 0.98))
    for x in (VX0, VX1): torus(VR + 0.02, 0.035, (x, YP, VZ), (0.25, 0.45, 0.85), rot=(0, math.pi / 2, 0))
    for x in (VX0 + 0.35, VX1 - 0.35): caja((0.12, 0.5, VZ - VR + 0.02), (x, YP + 0.05, (VZ - VR) / 2), GRIS, r=0.02)
    caja((VX1 - VX0, VR * 1.4, 0.025), ((VX0 + VX1) / 2, YP + 0.12, VZ - 0.05), MEMB, r=0.006)
    for k in range(28): box((0.012, VR * 1.3, 0.027), (VX0 + 0.05 + k * 0.075, YP + 0.12, VZ - 0.05), (0.85, 0.62, 0.12))
    S["agua_baja"] = box((1, 1, 1), LEJOS, (0.45, 0.75, 1.0), unique=True)
    # salida de agua potable al depósito y salmuera de vuelta al mar
    tubo([Vector(p) for p in DULCE], 0.06, (0.35, 0.65, 0.95)); tubo([Vector(p) for p in SALMP], 0.07, SALM)
    caja((0.9, 0.9, 0.06), (TANQ.x, TANQ.y + 0.15, 0.03), GRIS, r=0.02)
    S["tanque"] = medio_tubo([TANQ + Vector((0, 0.15, 0.06)), TANQ + Vector((0, 0.15, 1.25))], 0.38, 0.04, (0.85, 0.88, 0.92))
    S["nivel"] = cyl(0.37, 1.0, LEJOS, (0.40, 0.70, 1.0), unique=True)
    for k in range(5): box((0.06, 0.01, 0.01), (TANQ.x - 0.1, TANQ.y - 0.235, 0.3 + 0.2 * k), (0.2, 0.2, 0.25))
    # recuperador de presión (tambor que gira) y barra de energía
    caja((0.7, 0.5, 0.08), (REC.x, REC.y, 0.04), GRIS, r=0.02)
    S["tambor"] = empty(tuple(REC)); S["tambor"].rotation_mode = 'XYZ'
    cilindro(0.2, 0.5, (0, 0, 0), (0.55, 0.78, 0.40), S["tambor"], rot=(0, math.pi / 2, 0), r=0.03)
    for k in range(6): caja((0.52, 0.03, 0.05), (0, 0.2 * math.cos(k * 1.047), 0.2 * math.sin(k * 1.047)), (0.30, 0.55, 0.25), S["tambor"], rot=(k * 1.047, 0, 0), r=0.01)
    caja((0.24, 0.24, 1.0), (BARRA.x, BARRA.y + 0.02, 0.5), (0.25, 0.27, 0.31), r=0.03)
    S["energia"] = box((1, 1, 1), LEJOS, PAL["amarillo"], unique=True)
    cilindro(0.06, 0.04, (BARRA.x, BARRA.y + 0.02, 1.02), (0.25, 0.27, 0.31), r=0.01)
    S["fl_rec"] = flecha3d(LEJOS, (0, -1, 0), 0.35, 0.03)
    S["fl_bomba"] = flecha3d(LEJOS, (0, 0, -1), 0.3, 0.03)
    S["fl_presion"] = [flecha3d(LEJOS, (0, 0, -1), 0.22, 0.022) for _ in range(4)]
    # partículas: agua del mar, sal, agua de las membranas, salmuera
    S["gotas"] = [sph(0.035, LEJOS, (0.35, 0.62, 1.0), seg=10) for _ in range(NF)]
    S["sal"] = [caja((0.045, 0.045, 0.045), LEJOS, SAL, r=0.006) for _ in range(NS)]
    S["mg"] = [sph(0.03, LEJOS, (0.35, 0.62, 1.0), seg=10) for _ in range(NM)]
    S["ms"] = [caja((0.04, 0.04, 0.04), LEJOS, SAL, r=0.005) for _ in range(NMS)]
    S["sb"] = [sph(0.035, LEJOS, SALM, seg=10) for _ in range(NB)]
    # ---------- ciudad con poca lluvia, río casi seco y el mar al lado ----------
    isla(5.0, 3.6, tuple(C0), capas=[(PAL["cesped"], 0.1), (PAL["tierra"], 0.4), (PAL["tierra2"], 0.4)])
    box((1.4, 3.6, 0.5), (C0.x - 3.2, C0.y, -0.25), PAL["agua"]); box((1.4, 3.6, 0.4), (C0.x - 3.2, C0.y, -0.7), ARENA)
    box((0.35, 3.6, 0.02), (C0.x - 0.6, C0.y, 0.005), (0.86, 0.78, 0.58))                        # cauce seco
    box((0.06, 3.6, 0.025), (C0.x - 0.6, C0.y, 0.01), PAL["agua"])                                # hilo de agua
    rr = random.Random(3)
    for i in range(4):
        for j in range(3):
            x = C0.x + 0.1 + i * 0.6; y = C0.y - 1.1 + j * 1.0
            if rr.random() < 0.7: edificio((x, y, 0), pisos=rr.randint(3, 7), s=0.28, color=rr.choice((PAL["pared"], (0.98, 0.78, 0.6), (0.85, 0.9, 0.98))))
            else: casa((x, y, 0), 0.35)
    for k in range(5): arbol((C0.x - 1.4 + 0.25 * (k % 2), C0.y - 1.4 + 0.7 * k, 0), 0.4, seed=k)
    calle(3.6, (C0.x - 0.05, C0.y, 0.004), ancho=0.25, rot=math.pi / 2, aceras=False)
    for k in range(3): coche((C0.x - 0.05, C0.y - 1.0 + k * 0.9, 0.01), 0.18, rot=math.pi / 2)
    S["nube_c"] = nube((C0.x + 0.5, C0.y, 2.6), 0.9, seed=21)
    S["lluvia"] = [cyl(0.012, 0.12, LEJOS, (0.4, 0.62, 1.0), v=8) for _ in range(5)]
    # ---------- isla de las 80 piscinas olímpicas ----------
    isla(6.0, 3.4, tuple(P0), capas=[(PAL["cesped"], 0.1), (PAL["tierra"], 0.35), (PAL["tierra2"], 0.35)])
    S["pisc"] = []
    for j in range(8):
        for i in range(10):
            c = P0 + Vector((-2.45 + i * 0.545, -1.36 + j * 0.39, 0))
            caja((0.5, 0.3, 0.06), (c.x, c.y, 0.03), (0.97, 0.97, 0.98), r=0.012)
            box((0.44, 0.24, 0.005), (c.x, c.y, 0.062), (0.55, 0.8, 0.92))
            S["pisc"].append(box((1, 1, 1), LEJOS, PAL["agua"]))
    dyn = [cam, S["mar"], S["cut_mar"], S["torre"], S["cut_torre"], S["t_toma"], S["t_alta"], S["vaso"], S["tanque"], S["rodete"], S["aguja"], S["rueda"], S["agua_baja"], S["nivel"],
           S["tambor"], S["energia"], S["fl_rec"], S["fl_bomba"], S["fl_presion"], S["gotas"], S["sal"], S["mg"], S["ms"], S["sb"],
           S["nube_c"], S["lluvia"], S["pisc"]]
    join_static(dyn)
    return sc, S

def back_(u):
    u = max(0.0, min(1.0, u)); c = 1.70158
    return 1 + (c + 1) * (u - 1) ** 3 + c * (u - 1) ** 2

def presion(t):
    return keyed(t, [(0, 1.0), (T("hasta sesenta") - 0.25, 1.0), (T("sesenta bar", fin=True), 60.0)])

def pose(t, S):
    bomba_on = seg(t, T("una bomba") - 0.2, T("una bomba") + 0.6)
    vel = 0.35 + 0.65 * bomba_on
    S["rodete"].rotation_euler = (0, t * (3 + 14 * bomba_on), 0)
    S["aguja"].rotation_euler = (0, -(math.radians(210 - 240 * presion(t) / 70) - math.pi / 2), 0)
    S["rueda"].rotation_euler = (0, 0, 0.15 * math.sin(t * 1.3))
    # agua del mar que entra por la tubería (la sal aparece cuando la voz la nombra)
    con_sal = t >= T("pero lleva sal") - 0.2
    L = largo(PT_TOMA)
    for k, b in enumerate(S["gotas"]):
        s_ = ((t * 0.45 * vel + k / NF) % 1.0) * L
        p = at(PT_TOMA, s_) + Vector((0, -0.02 * ((k % 3) - 1), 0.03 * math.sin(k * 2.1)))
        b.location = p
    for k, c in enumerate(S["sal"]):
        if not con_sal: c.location = LEJOS; continue
        s_ = ((t * 0.45 * vel + (k + 0.5) / NS) % 1.0) * L
        c.location = at(PT_TOMA, s_) + Vector((0, -0.03, 0.02 * math.cos(k))); c.rotation_euler = (t + k, t * 0.7, k)
        sc_ = 1 + 0.6 * win01(t, T("pero lleva sal") - 0.2, T("y así no") + 0.6); c.scale = (sc_,) * 3
    # dentro del tubo de membranas: el agua no pasa hasta que la bomba aprieta; la sal nunca pasa
    pasa = seg(t, T("una bomba"), T("sesenta bar", fin=True))
    ver = t >= T("así que usas") - 0.4
    rng = random.Random(7)
    for k, b in enumerate(S["mg"]):
        if not ver: b.location = LEJOS; continue
        u = (t * 0.18 + k / NM) % 1.0; x = VX0 + 0.1 + u * (VX1 - VX0 - 0.2); y = YP + rng.uniform(-0.05, 0.22)
        zt = VZ + 0.05 + 0.15 * ((k * 0.37) % 1.0)
        bajada = max(0.0, min(1.0, (u - 0.25 - 0.4 * ((k * 0.61) % 1.0)) / 0.15)) * pasa
        z = mix(zt, VZ - 0.12 - 0.1 * ((k * 0.53) % 1.0), bajada)
        if pasa < 0.05: z = VZ + 0.0 + 0.03 * abs(math.sin(t * 6 + k)) if u > 0.5 else zt     # chocan con la membrana
        b.location = Vector((x, y, z))
    for k, c in enumerate(S["ms"]):
        if not ver: c.location = LEJOS; continue
        u = (t * 0.18 + (k + 0.5) / NMS) % 1.0; x = VX0 + 0.1 + u * (VX1 - VX0 - 0.2)
        c.location = Vector((x, YP + 0.1 * ((k % 3) - 0.5), VZ + 0.02 + 0.04 * abs(math.sin(t * 7 + k * 1.3)))); c.rotation_euler = (t, k, t * 0.5)
    lleno = 0.2 * pasa + 0.1 * seg(t, T("salen cuarenta"), T("salen cuarenta") + 2)
    if lleno > 0.01:
        S["agua_baja"].location = Vector(((VX0 + VX1) / 2, YP + 0.1, VZ - VR + 0.04 + lleno / 2)); S["agua_baja"].scale = (VX1 - VX0 - 0.05, 0.38, lleno)
    else: S["agua_baja"].location = LEJOS
    for k, f in enumerate(S["fl_presion"]):
        w = win01(t, T("una bomba"), T("pero de cada") - 0.2, 0.3, 0.3)
        if w < 0.01: f.location = LEJOS; continue
        f.location = Vector((VX0 + 0.35 + k * 0.45, YP - 0.2, VZ + 0.32 + 0.05 * math.sin(t * 8 + k))); f.scale = (w * (0.6 + 0.6 * seg(t, T("hasta sesenta"), T("sesenta bar", fin=True))),) * 3
    # depósito de agua potable: sube a 45 cuando se dice y sigue llenándose
    niv = 0.15 + 0.35 * seg(t, T("salen cuarenta"), T("de agua potable", fin=True)) + 0.45 * seg(t, T("saca hasta"), T("al día", 2, fin=True))
    S["nivel"].location = TANQ + Vector((0, 0.15, 0.08 + niv * 1.1 / 2)); S["nivel"].scale = (1, 1, niv * 1.1)
    # salmuera de vuelta al mar (empieza a correr en «y el resto»)
    sv = seg(t, T("y el resto") - 0.3, T("y el resto") + 0.4)
    Ls = largo(PT_SALM)
    for k, b in enumerate(S["sb"]):
        if sv < 0.01: b.location = LEJOS; continue
        b.location = at(PT_SALM, ((t * 0.12 + k / NB) % 1.0) * Ls) + Vector((0, 0, 0.02 * math.sin(k))); b.scale = (sv,) * 3
    rec = seg(t, T("así que recuperas"), T("así que recuperas") + 0.8)
    S["tambor"].rotation_euler = (t * (0.6 + 9 * rec), 0, 0)
    w = win01(t, T("así que recuperas"), T("y aquí viene"), 0.3, 0.3)
    S["fl_rec"].location = REC + Vector((-0.4, -0.05, 0.3)) if w > 0.01 else LEJOS; S["fl_rec"].scale = (max(w, 0.001),) * 3
    S["fl_rec"].rotation_mode = 'QUATERNION'; S["fl_rec"].rotation_quaternion = Vector((0, 0, 1)).rotation_difference(Vector((-1, -1.2, -0.3)))
    S["fl_bomba"].location = PUMP + Vector((0, -0.05, 0.62)) if bomba_on > 0.01 and t < T("pero de cada") else LEJOS
    S["fl_bomba"].scale = (max(win01(t, T("una bomba") - 0.1, T("pero de cada"), 0.3, 0.3), 0.001),) * 3
    e = 1.0 - 0.5 * seg(t, T("y ahorras"), T("la mitad", fin=True))
    S["energia"].location = BARRA + Vector((0, -0.1, 0.06 + 0.88 * e / 2)); S["energia"].scale = (0.16, 0.04, 0.88 * e)
    set_color(S["energia"], tuple(mix(a_, b_, min(1.0, 2 * (1 - e))) for a_, b_ in zip(PAL["rojo"], VERDE)))
    # lluvia escasa sobre la ciudad
    ll = win01(t, T("barcelona") - 0.2, T("pero tiene el mar"), 0.3, 0.3)
    for k, d in enumerate(S["lluvia"]):
        if ll < 0.01: d.location = LEJOS; continue
        u = (t * 0.7 + k * 0.23) % 1.0
        d.location = Vector((C0.x + 0.1 + 0.25 * k - 0.5, C0.y + 0.1 * (k % 2), 2.3 - 2.2 * u))
    # 80 piscinas olímpicas que se llenan una tras otra
    a0, a1 = T("ochenta") - 0.2, T("cada día", fin=True)
    for k, p in enumerate(S["pisc"]):
        u = max(0.0, min(1.0, (t - a0) / max(a1 - a0, 0.5) * 1.6 - k / NP * 0.6))
        if t < a0 - 0.5: u = 0.0
        if u < 0.01: p.location = LEJOS; continue
        c = P0 + Vector((-2.45 + (k % 10) * 0.545, -1.36 + (k // 10) * 0.39, 0)); h = 0.05 * u
        p.location = Vector((c.x, c.y, 0.064 + h / 2)); p.scale = (0.44, 0.24, max(h, 0.002))
    apply_cam(S["cam"], *cam_cortes(t, CAM()))

def cam_cortes(t, ks, drift=0.004):
    """planos por corte: la cámara no viaja entre claves (no atraviesa nada); cada plano empuja un 8 %;
    el último plano termina exactamente en la clave del primero (bucle)"""
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

PLANTA = (1.2, -0.4, 0.4); VASO = ((VX0 + VX1) / 2, YP, VZ); CIUDAD = tuple(C0 + Vector((0, 0, 0.4))); PISC = tuple(P0 + Vector((0, 0, 0.0)))
def CAM():
    k = Claves(); add = k.add
    ini = V((0.15, YP, 0.25), (-0.75, -1.35, 0.3), 32)
    add(0.0, ini)
    add(T("desaladora") - 0.1, V(PLANTA, (-1.6, -4.6, 2.4), 30))
    add(T("escribe"), V(PLANTA, (1.6, -4.6, 2.1), 30))
    add(T("barcelona") - 0.2, V(CIUDAD, (-0.8, -4.4, 2.3), 30))
    add(T("y poca") - 0.2, V(tuple(C0 + Vector((0.3, 0, 1.2))), (-0.6, -4.4, 0.0), 30))
    add(T("pero tiene") - 0.2, V(tuple(C0 + Vector((-1.6, 0, 0.2))), (-1.0, -3.6, 1.6), 30))
    add(T("así que sacas") - 0.2, V((-2.4, YP, 0.05), (-0.8, -1.7, 0.55), 32))
    add(T("pero lleva") - 0.2, V((-1.2, YP, 0.18), (-0.15, -1.0, 0.25), 36))
    add(T("y así no") - 0.2, V((-0.5, YP, 0.2), (0.45, -0.95, 0.35), 36))
    add(T("así que usas") - 0.2, V(VASO, (-0.5, -2.0, 0.55), 32))
    add(T("tan fina") - 0.2, V((2.1, YP, 0.72), (-0.25, -0.95, 0.2), 38))
    add(T("se llama") - 0.2, V(VASO, (0.6, -1.7, 0.6), 34))
    add(T("pero el agua no") - 0.2, V((2.3, YP, 0.75), (0.2, -0.9, 0.25), 38))
    add(T("así que una bomba") - 0.2, V(tuple(PUMP), (-0.55, -1.2, 0.35), 34))
    add(T("hasta sesenta") - 0.3, V(tuple(MAN), (0.0, -0.95, 0.05), 36))
    add(T("más de veinticinco") - 0.2, V(tuple((MAN + RUEDA) / 2), (0.15, -2.0, 0.45), 32))
    add(T("pero de cada") - 0.2, V((2.4, YP, 0.55), (0.2, -2.7, 1.0), 30))
    add(T("salen cuarenta") - 0.2, V(tuple(TANQ + Vector((0, 0, 0.6))), (-0.5, -1.6, 0.45), 34))
    add(T("y el resto") - 0.2, V((1.6, -0.25, 0.35), (0.6, -2.4, 1.1), 30))
    add(T("con más sal") - 0.2, V((-2.4, -0.25, 0.0), (0.9, -1.4, 0.5), 32))
    add(T("así que recuperas") - 0.2, V(tuple(REC), (-0.6, -1.1, 0.45), 34))
    add(T("esa salmuera") - 0.2, V(tuple(REC), (0.7, -1.0, 0.5), 34))
    add(T("y ahorras") - 0.2, V(tuple(BARRA + Vector((0, 0, 0.55))), (-0.25, -1.3, 0.25), 36))
    add(T("y aquí viene") - 0.2, V(PLANTA, (0.4, -4.4, 3.4), 30))
    add(T("la planta") - 0.2, V(PLANTA, (-2.6, -4.0, 1.8), 30))
    add(T("saca hasta") - 0.2, V((2.6, -0.6, 0.5), (0.9, -4.0, 1.5), 30))
    add(T("son") - 0.2, V(PISC, (0.0, -5.4, 3.3), 30))
    add(T("ochenta") + 0.6, V(tuple(P0 + Vector((-1.4, -0.6, 0))), (-0.4, -2.1, 1.0), 32))
    add(T("al año") - 0.2, V(PISC, (2.6, -5.2, 3.0), 30))
    add(T("te has acercado") - 0.2, V(PLANTA, (-1.6, -4.6, 2.4), 30))
    add(T("dime") - 0.2, V(CIUDAD, (1.2, -4.2, 2.0), 30))
    add(T("y si quieres") - 0.2, V(VASO, (-0.7, -2.0, 0.95), 32))
    add(T("pídelo") - 0.2, V(PLANTA, (0.2, -3.2, 3.6), 30))
    add(T("lo más pedido") - 0.2, V(tuple(MAN), (0.0, -0.95, 0.05), 36))
    add(T("sígueme") - 0.2, V(PLANTA, (1.6, -4.6, 2.1), 30))
    add(T("así que ya sabes") - 0.2, V((-1.5, YP, 0.2), (-0.3, -1.5, 0.6), 32))
    add(T("la desaladora del", 2) - 0.3, ini)
    add(DUR + 1, ini)
    return k.k

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, Vector(v))
    return {"man": Pj(MAN + Vector((0, 0, 0.3))), "rueda": Pj(RUEDA + Vector((0, 0, 0.4))), "entrada": Pj(Vector((VX0 + 0.3, YP, VZ + 0.45))),
            "tanque": Pj(TANQ + Vector((0, 0, 1.45))), "salmuera": Pj(Vector((-0.6, -0.25, 0.6))), "barra": Pj(BARRA + Vector((0, 0, 1.2))),
            "pisc": Pj(P0 + Vector((0, 0, 0.5))), "bomba": Pj(PUMP + Vector((0, 0, 0.35))), "membrana": Pj(Vector((2.3, YP, VZ))),
            "rec": Pj(REC + Vector((0, 0, 0.3)))}

if __name__ == "__main__":
    run("desaladora", build, pose, anchors)
