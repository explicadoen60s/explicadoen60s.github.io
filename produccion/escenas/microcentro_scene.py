# «¿Pones la comida en el centro del microondas?» Cocina de maqueta sobre una isla cortada (suelo, hormigón, tierra):
# bancada con fogones y olla, pared de azulejos, planta y el microondas encima, con el frontal cortado (cantos crema) para
# ver la cavidad y el compartimento del magnetrón. Un bol de comida en corte gira en el plato: por fuera naranja (caliente)
# y por dentro azul (frío). Dedo que pulsa el botón, ondas (bolitas) que salen del magnetrón por la guía y rebotan en las
# paredes, dos ondas que se cruzan, capa de puntos calientes (rojos) y fríos (azules) cada 6 cm, plato que gira con trozos
# que se calientan al pasar por los puntos rojos, rastro del borde frente al centro que no viaja, flechas cortas de 3 cm,
# tableta de chocolate con manchas derretidas cada 6 cm y la onda de 12 cm encima con regla, comida en anillo y cuchara.
# Planos (fotografía → motion; esquina libre arriba-izquierda salvo el mini del juego, que la ocupa desde 7 s):
#  0 bol girando, primer plano a 0,5 m · 2,4 bol en corte (frío dentro) · 4,4 microondas entero · 6,8 cocina entera ·
#  9,2 botón y dedo · 10,6 magnetrón · 12,2 onda que vibra · 15,8 rebotes · 17,6 dos ondas · 18,7 puntos calientes ·
#  21,3 puntos fríos · 23,6 capa entera · 27,9 plato desde arriba · 29,4 trozos que pasan · 31,4 microondas · 34,0 cenital ·
#  37,0 borde frente a centro · 38,7 punto frío del centro · 40,8 bol en corte · 43,1 flechas de 3 cm · 46,2 cocina ·
#  48,3 sale el plato y entra el chocolate · 50,7 manchas · 52,9 cada 6 cm · 54,4 onda y regla · 57,8 microondas ·
#  58,6 anillo en el borde · 62,4 cuchara · 64,1 cocina · 66,9 microondas · 69,8 bol · 71,2 vuelta al primer plano.
import bpy, math, sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from modelos import *
from maqueta import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("microcentro")
WHITE = (0.97, 0.97, 0.98); DARK = (0.18, 0.19, 0.22); GRIS = (0.80, 0.82, 0.86); CAV = (0.93, 0.92, 0.86)
CALOR = (0.96, 0.36, 0.14); TEMPL = (0.98, 0.72, 0.38); FRIO = (0.25, 0.55, 1.0); ONDA = (1.0, 0.78, 0.15)
COBRE = (0.86, 0.56, 0.36); CHOCO = (0.36, 0.20, 0.11); CHOCO_D = (0.62, 0.38, 0.20); PIEL = (0.96, 0.78, 0.64)
CRISTAL = (0.80, 0.90, 0.96); SUELO = (0.90, 0.84, 0.74)

M = Vector((-0.6, 0.45, 0.905))                 # base del microondas (centro de la base)
def P(x, y, z): return M + Vector((x, y, z))
CX, CY = -0.065, -0.01                          # centro del plato (local)
PLATE_Z = 0.035
PC = P(CX, CY, PLATE_Z)                         # centro del plato (mundo)
SPOT_Z = 0.165                                  # capa de puntos calientes/fríos (sobre el bol)
GRID = [(i, j) for i in range(5) for j in range(5)]
def spot_xy(i, j): return (CX + (i - 2) * 0.06, CY + (j - 2) * 0.06)
def caliente(i, j): return (i + j) % 2 == 1   # el centro (2,2) es frío
NW = 26                                          # bolitas de cada onda

# recorrido de las ondas: magnetrón → guía → cavidad, rebotando en las paredes
RUTA = poly([P(0.18, 0.0, 0.17), P(0.18, 0.0, 0.25), P(0.09, -0.02, 0.25), P(-0.22, -0.06, 0.06), P(0.08, -0.08, 0.04),
             P(-0.22, -0.10, 0.25), P(0.08, -0.12, 0.24), P(-0.22, -0.14, 0.05)])

def build():
    sc, cam = scene_setup(world=PAL["cielo"], shadow=0.25, light_rot=-30); entorno_claro(sc)
    S = {"cam": cam}
    nubes(8, (0, 7, 3.4), 6, 1.2, 1.0, s=1.2, seed=5)
    isla(3.4, 2.2, (0, 0.15, 0), capas=[(SUELO, 0.08), (PAL["hormigon"], 0.16), (PAL["tierra"], 0.32), (PAL["tierra2"], 0.36)])
    for k in range(7): box((0.012, 2.2, 0.006), (-1.5 + k * 0.5, 0.15, 0.003), (0.80, 0.74, 0.65))
    # pared del fondo con azulejos y pared lateral
    box((3.4, 0.1, 2.2), (0, 1.2, 1.1), PAL["pared"]); box((3.4, 0.102, 0.03), (0, 1.2, 2.185), PAL["corte"])
    azulejos(3.2, 0.62, (0, 1.14, 1.22), color=PAL["menta"], paso=0.15)
    box((0.1, 2.2, 2.2), (-1.65, 0.15, 1.1), PAL["pared"]); box((0.102, 2.2, 0.03), (-1.65, 0.15, 2.185), PAL["corte"])
    # bancada, fogones, olla, armario alto, planta, botes
    cocina((0, 0.85, 0), 1.0, ancho=2.8)
    olla((0.42, 0.85, 0.905), 0.8)
    caja((1.0, 0.32, 0.55), (0.75, 1.0, 1.75), (0.52, 0.69, 0.91), r=0.02)
    for x in (0.5, 1.0): caja((0.46, 0.02, 0.5), (x, 0.83, 1.75), (0.58, 0.74, 0.94), r=0.01)
    planta((1.15, 0.95, 0.905), 0.9)
    for k, c in enumerate(((0.95, 0.55, 0.3), (0.42, 0.78, 0.8), (0.97, 0.55, 0.66))):
        cilindro(0.045, 0.14, (-1.15 + k * 0.11, 1.0, 0.975), c, r=0.012)
    # ---------- microondas (frontal cortado) ----------
    W2, D2, H = 0.25, 0.19, 0.30
    caja((0.5, 0.02, H), tuple(P(0, D2 - 0.01, H / 2)), WHITE, r=0.006)                          # fondo
    caja((0.5, 2 * D2, 0.02), tuple(P(0, 0, H - 0.01)), WHITE, r=0.006)                          # techo
    caja((0.5, 2 * D2, 0.02), tuple(P(0, 0, 0.01)), WHITE, r=0.006)                               # suelo
    for x in (-W2 + 0.01, W2 - 0.01): caja((0.02, 2 * D2, H), tuple(P(x, 0, H / 2)), WHITE, r=0.006)
    caja((0.02, 2 * D2, H - 0.04), tuple(P(0.11, 0, H / 2)), GRIS, r=0.004)                        # tabique cavidad | magnetrón
    for p in ((P(0, -D2, H - 0.01), (0.5, 0.004, 0.02)), (P(0, -D2, 0.01), (0.5, 0.004, 0.02)),
              (P(-W2 + 0.01, -D2, H / 2), (0.02, 0.004, H)), (P(W2 - 0.01, -D2, H / 2), (0.02, 0.004, H)),
              (P(0.11, -D2, H / 2), (0.02, 0.004, H - 0.04))):
        box(p[1], tuple(p[0]), PAL["corte"])                                                          # cantos cortados
    # interior claro de la cavidad (pared del fondo y suelo)
    box((0.31, 0.004, 0.24), tuple(P(-0.065, D2 - 0.022, 0.145)), CAV)
    box((0.31, 0.34, 0.004), tuple(P(-0.065, 0.0, 0.022)), CAV)
    for k in range(5): cyl(0.006, 0.004, tuple(P(-0.2 + 0.03 * k, D2 - 0.024, 0.24)), (0.7, 0.7, 0.68), rot=(math.pi / 2, 0, 0), v=8)
    # magnetrón (cobre con aletas), antena y guía de ondas
    S["mag"] = empty(P(0.18, 0.02, 0.12))
    cilindro(0.04, 0.09, (0, 0, 0), COBRE, S["mag"], r=0.008, unique=True)
    for k in range(5): cilindro(0.055, 0.004, (0, 0, -0.035 + k * 0.017), (0.78, 0.80, 0.84), S["mag"], r=0.001)
    cilindro(0.008, 0.05, (0, 0, 0.065), (0.85, 0.86, 0.88), S["mag"], r=0.002)
    caja((0.05, 0.06, 0.04), tuple(P(0.18, 0.02, 0.255)), (0.78, 0.80, 0.84), r=0.006)
    caja((0.09, 0.06, 0.03), tuple(P(0.13, 0.02, 0.255)), (0.78, 0.80, 0.84), r=0.006)
    # panel de mandos (abajo, delante del compartimento) con pantalla y botón
    caja((0.11, 0.015, 0.11), tuple(P(0.18, -D2 + 0.005, 0.065)), (0.22, 0.23, 0.27), r=0.008)
    S["pantalla"] = box((0.07, 0.004, 0.022), tuple(P(0.18, -D2 - 0.003, 0.095)), (0.2, 0.9, 0.5), unique=True)
    S["boton"] = cilindro(0.016, 0.012, tuple(P(0.18, -D2 - 0.004, 0.045)), (0.3, 0.85, 0.45), rot=(math.pi / 2, 0, 0), r=0.004, unique=True)
    S["bombilla"] = sph(0.012, tuple(P(0.085, 0.12, 0.25)), (1.0, 0.95, 0.6), unique=True)
    # plato giratorio (con marcas para que se vea girar) y aro de rodillos
    torus(0.09, 0.006, tuple(P(CX, CY, 0.028)), (0.6, 0.6, 0.62))
    S["plato"] = empty(PC)
    cilindro(0.135, 0.008, (0, 0, 0), CRISTAL, S["plato"], r=0.003)
    for k in range(3):
        a = k * math.tau / 3
        caja((0.03, 0.012, 0.003), (math.cos(a) * 0.12, math.sin(a) * 0.12, 0.005), (0.55, 0.7, 0.85), S["plato"], r=0.001,
             rot=(0, 0, a + math.pi / 2))
    S["marca"] = sph(0.009, (0.12, 0, 0.012), PAL["rojo"], S["plato"])
    # bol con comida en corte: fuera caliente, dentro frío (cortadores fijos: el corte mira siempre a cámara)
    ct1 = cortador_sin((0.4, 0.3, 0.4), tuple(P(CX, CY - 0.15, 0.1))); ct2 = cortador_sin((0.4, 0.3, 0.4), tuple(P(CX, CY - 0.152, 0.1)))
    S["ct"] = [ct1, ct2]
    S["bol"] = cylinder_bol(); cortar(S["bol"], ct1)
    S["comida"] = bola(0.066, tuple(P(CX, CY, PLATE_Z + 0.055)), TEMPL, escala=(1, 1, 0.62), unique=True); cortar(S["comida"], ct1)
    S["nucleo"] = bola(0.036, tuple(P(CX, CY, PLATE_Z + 0.05)), FRIO, escala=(1, 1, 0.7), unique=True); cortar(S["nucleo"], ct2)
    # trozos que pasan por los puntos calientes y comida en anillo (hijos del plato)
    S["trozos"] = [bola(0.016, (0.1 * math.cos(k * math.tau / 3), 0.1 * math.sin(k * math.tau / 3), 0.02), TEMPL, S["plato"],
                        escala=(1.2, 1, 0.7), unique=True) for k in range(3)]
    S["anillo"] = [bola(0.02, (0.105 * math.cos(k * math.tau / 9), 0.105 * math.sin(k * math.tau / 9), 0.02), TEMPL, S["plato"],
                        escala=(1.25, 1, 0.75), unique=True) for k in range(9)]
    # puntos calientes y fríos
    S["spots"] = [sph(0.013, LEJOS, CALOR if caliente(i, j) else FRIO, seg=12, unique=True) for i, j in GRID]
    # ondas (bolitas)
    S["onda1"] = [sph(0.005, LEJOS, ONDA, seg=8) for _ in range(NW)]
    S["onda2"] = [sph(0.005, LEJOS, (1.0, 0.55, 0.15), seg=8) for _ in range(NW)]
    S["ruta"] = [sph(0.006, LEJOS, ONDA, seg=8) for _ in range(10)]
    # rastro del borde y punto del centro (la trampa)
    S["rastro"] = [sph(0.007, LEJOS, PAL["rojo"], seg=8) for _ in range(14)]
    S["centro"] = sph(0.012, LEJOS, FRIO, seg=12)
    # flechas: ondas que entran solo 3 cm y frío que cae en el centro
    S["fl"] = [flecha3d(LEJOS, d, 0.05, 0.005) for d in ((1, 0, 0), (-1, 0, 0), (0, 0, -1))]
    S["flfrio"] = flecha3d(LEJOS, (0, 0, -1), 0.06, 0.006, color=FRIO)
    # chocolate con manchas derretidas cada 6 cm y regla de la onda
    S["choco"] = empty(LEJOS)
    caja((0.26, 0.1, 0.012), (0, 0, 0.006), CHOCO, S["choco"], r=0.003)
    for k in range(6):
        for j in range(2): caja((0.038, 0.042, 0.004), (-0.105 + k * 0.042, -0.024 + j * 0.048, 0.013), (0.42, 0.24, 0.13), S["choco"], r=0.002)
    S["manchas"] = [cilindro(0.016, 0.006, (-0.09 + 0.06 * k, 0, 0.016), CHOCO_D, S["choco"], r=0.003, unique=True) for k in range(4)]
    S["regla"] = box((1, 0.008, 0.008), LEJOS, PAL["amarillo"], unique=True)
    S["topes"] = [box((0.004, 0.008, 0.03), LEJOS, PAL["amarillo"]) for _ in range(2)]
    # dedo y cuchara
    S["dedo"] = empty(LEJOS)
    cilindro(0.011, 0.09, (0, -0.045, 0), PIEL, S["dedo"], rot=(math.pi / 2, 0, 0), r=0.004)
    bola(0.0115, (0, 0, 0), PIEL, S["dedo"]); caja((0.05, 0.12, 0.035), (0.0, -0.13, -0.005), PIEL, S["dedo"], r=0.015)
    S["cuchara"] = empty(LEJOS)
    caja((0.008, 0.008, 0.16), (0, 0, 0.08), GRIS, S["cuchara"], r=0.003); bola(0.018, (0, 0, 0), GRIS, S["cuchara"], escala=(1, 1.4, 0.4))
    dyn = [cam, S["mag"], S["pantalla"], S["boton"], S["bombilla"], S["plato"], ct1, ct2, S["bol"], S["comida"], S["nucleo"],
           S["spots"], S["onda1"], S["onda2"], S["ruta"], S["rastro"], S["centro"], S["fl"], S["flfrio"], S["choco"],
           S["regla"], S["topes"], S["dedo"], S["cuchara"]]
    join_static(dyn)
    return sc, S

def cortador_sin(size, loc):
    """cortador sin material: la cara cortada coge el color de la propia pieza (comida naranja, núcleo azul)"""
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); c = bpy.context.object; c.scale = size
    c.hide_render = True; c.display_type = 'WIRE'; return c

def cylinder_bol():
    o = cilindro(0.074, 0.05, tuple(P(CX, CY, PLATE_Z + 0.03)), WHITE, r=0.01, unique=True)
    return o

# ---------------- estado ----------------
def fuera_bol(t):   # el bol se va cuando sale el plato y vuelve en el último plano
    return T("quita el plato") + 0.5 <= t < T("ya sabes")

def plato_fuera(t): return T("quita el plato") + 0.2 <= t < T("qué haces") + 0.2

def calor_col(u):  # 0 frío → 1 muy caliente
    if u < 0.5: return tuple(mix(a, b, u / 0.5) for a, b in zip(FRIO, TEMPL))
    return tuple(mix(a, b, (u - 0.5) / 0.5) for a, b in zip(TEMPL, CALOR))

def onda_pos(k, t, dir_=1, fase=0.0, y=-0.05, z=0.15, amp=0.035, lam=0.12, x0=-0.225, x1=0.095):
    x = x0 + (x1 - x0) * k / (NW - 1)
    ph = 2 * math.pi * (x / lam) - dir_ * t * 6.0 + fase
    return P(x, y, z + amp * math.sin(ph))

def plato_ang(t): return t * 0.628      # 6 vueltas por minuto, de verdad

def pose(t, S):
    on = 1.0
    # plato: gira siempre (más rápido en el tramo de las vueltas para que se lea)
    ang = plato_ang(t)
    S["plato"].rotation_euler.z = ang
    lift = seg(t, T("quita el plato"), T("quita el plato") + 0.6) * (1 - seg(t, T("qué haces") - 0.1, T("qué haces") + 0.4))
    S["plato"].location = PC + Vector((0, -0.35 * lift, 0.12 * math.sin(math.pi * min(1, lift))))
    S["plato"].scale = (max(1 - lift, 0.001),) * 3
    # bol (y su corte): fuera durante el chocolate y el anillo
    vis = not fuera_bol(t)
    for o in (S["bol"], S["comida"], S["nucleo"]): o.hide_render = not vis
    calor = 0.82 + 0.06 * math.sin(t * 3)
    set_color(S["comida"], calor_col(calor))
    set_color(S["nucleo"], calor_col(0.08 + 0.05 * win01(t, T("y a mitad"), T("ya sabes"))))
    # bombilla y pantalla
    set_color(S["bombilla"], (1.0, 0.95, 0.6) if on else (0.6, 0.6, 0.6))
    # dedo que pulsa el botón
    a = T("pulsas")
    if a - 0.7 <= t < a + 1.0:
        u = seg(t, a - 0.7, a - 0.05) * (1 - seg(t, a + 0.35, a + 1.0))
        S["dedo"].location = P(0.18, -0.19 - 0.012 - 0.12 * (1 - u), 0.045) + Vector((0.12 * (1 - u), 0, -0.05 * (1 - u)))
    else: S["dedo"].location = LEJOS
    pr = win01(t, a - 0.08, a + 0.3, 0.06, 0.1)
    S["boton"].location = P(0.18, -0.19 - 0.004 + 0.006 * pr, 0.045)
    # magnetrón: late cuando lanza ondas
    lm = 1 + 0.06 * win01(t, T("magnetrón"), T("rebotan"), 0.2, 0.3) * math.sin(t * 40)
    S["mag"].scale = (lm, lm, 1)
    set_color(S["mag"].children[0], tuple(mix(a_, b_, win01(t, T("magnetrón"), T("vibran", fin=True) + 1.5) * (0.5 + 0.5 * math.sin(t * 12)))
                                         for a_, b_ in zip(COBRE, (1.0, 0.85, 0.3))))
    # ondas por el recorrido (salen del magnetrón y rebotan): al principio, al lanzar y al rebotar
    ruta_on = max(win01(t, -1, 2.3, 0.01, 0.3), win01(t, T("lanza"), T("vibran") + 0.3), win01(t, T("rebotan") - 0.2, T("y al cruzarse") + 0.2),
                  win01(t, T("ya sabes"), DUR + 1, 0.2, 0.01))
    L = largo(RUTA)
    for k, b in enumerate(S["ruta"]):
        if ruta_on < 0.01: b.location = LEJOS; continue
        b.location = at(RUTA, ((t * 0.55 + k / 10) % 1.0) * L); b.scale = (ruta_on,) * 3
    # onda que vibra (2450 millones) y dos ondas que se cruzan
    w1 = max(win01(t, T("vibran") - 0.2, T("rebotan") + 0.2), win01(t, T("y al cruzarse") - 0.1, T("tu microondas tiene")),
             win01(t, T("una onda entera") - 0.2, T("qué haces")))
    w2 = win01(t, T("y al cruzarse") - 0.1, T("tu microondas tiene"))
    choc = T("una onda entera") - 0.2 <= t < T("qué haces")
    for k, b in enumerate(S["onda1"]):
        if w1 < 0.01: b.location = LEJOS; continue
        if choc:   # onda estacionaria de 12 cm sobre la tableta (máximos en las manchas)
            x = -0.15 + 0.3 * k / (NW - 1); amp = 0.03 * math.cos(t * 9) * w1
            b.location = PC + Vector((x, 0.0, 0.07 + amp * math.sin(2 * math.pi * (x + 0.03) / 0.12))); b.scale = (w1,) * 3
        else:
            b.location = onda_pos(k, t * (2.2 if t < T("rebotan") else 1.0), 1); b.scale = (w1,) * 3
    for k, b in enumerate(S["onda2"]):
        if w2 < 0.01: b.location = LEJOS; continue
        b.location = onda_pos(k, t, -1, fase=1.0, y=-0.08, z=0.15); b.scale = (w2,) * 3
    # puntos calientes y fríos
    sp_on = max(win01(t, T("en unos sitios"), T("por eso gira") + 0.5), win01(t, T("por eso gira") + 0.5, T("pero hay"), 0.3, 0.3) * 0.7,
                win01(t, T("si ahí cae"), T("además") + 0.2))
    for (i, j), b in zip(GRID, S["spots"]):
        hot = caliente(i, j)
        if sp_on < 0.01: b.location = LEJOS; continue
        if t < T("tu microondas tiene"):   # primero aparecen los que se suman, luego los que se anulan
            vis_ = seg(t, T("en unos sitios"), T("calientan", fin=True)) if hot else seg(t, T("en otros"), T("y no calientan", fin=True))
        else: vis_ = 1.0
        if T("si ahí cae") <= t < T("además") + 0.2 and not (i == 2 and j == 2): vis_ *= 0.6
        x, y = spot_xy(i, j); pul = 1 + 0.25 * math.sin(t * 7 + i + j) if hot else 1.0
        if i == 2 and j == 2 and T("si ahí cae") <= t: pul = 1.6 + 0.3 * math.sin(t * 6)
        b.location = P(x, y, SPOT_Z); b.scale = (max(sp_on * vis_ * pul, 0.001),) * 3
    # trozos que pasan por los puntos calientes (se ponen rojos al pasar)
    tz = win01(t, T("por eso gira"), T("pero hay"), 0.3, 0.3)
    for k, b in enumerate(S["trozos"]):
        if tz < 0.01: b.hide_render = True; continue
        b.hide_render = False
        a_ = ang + k * math.tau / 3; wx, wy = CX + 0.1 * math.cos(a_), CY + 0.1 * math.sin(a_)
        d = min(math.hypot(wx - spot_xy(i, j)[0], wy - spot_xy(i, j)[1]) for i, j in GRID if caliente(i, j))
        set_color(b, calor_col(0.35 + 0.65 * max(0, 1 - d / 0.03)))
    # comida en anillo (pegada al borde, centro vacío) y cuchara que remueve
    ra = T("qué haces") + 0.3 <= t < T("ya sabes")
    for k, b in enumerate(S["anillo"]):
        b.hide_render = not ra
        if ra:
            ap = seg(t, T("ponla en anillo") + 0.1 * k, T("ponla en anillo") + 0.6 + 0.1 * k)
            r = 0.105 * ap + 0.02 * (1 - ap); a0 = k * math.tau / 9
            b.location = Vector((r * math.cos(a0), r * math.sin(a0), 0.02 + 0.08 * (1 - ap)))
            set_color(b, calor_col(0.45 + 0.4 * seg(t, T("pegada al borde"), T("y a mitad")) + 0.1 * math.sin(t * 3 + k)))
    cu = win01(t, T("y a mitad") - 0.2, T("te has acercado") + 0.3, 0.3, 0.3)
    if cu > 0.01:
        a_ = t * 5.0
        S["cuchara"].location = PC + Vector((0.1 * math.cos(a_), 0.1 * math.sin(a_), 0.03 + 0.15 * (1 - cu)))
        S["cuchara"].rotation_euler = (0.35, 0, a_)
    else: S["cuchara"].location = LEJOS
    # la trampa: rastro del borde frente al centro que no viaja
    tr = win01(t, T("el centro del plato"), T("si ahí cae"), 0.3, 0.3)
    for k, b in enumerate(S["rastro"]):
        if tr < 0.01: b.location = LEJOS; continue
        a_ = ang - k * 0.22
        b.location = PC + Vector((0.12 * math.cos(a_), 0.12 * math.sin(a_), 0.015)); b.scale = (tr * (1 - k / 16),) * 3
    S["centro"].location = PC + Vector((0, 0, 0.13)) if tr > 0.01 else LEJOS
    S["centro"].scale = (max(tr, 0.001),) * 3
    # flechas: frío que cae en el centro y ondas que solo entran 3 cm
    ff = win01(t, T("si ahí cae"), T("además"), 0.3, 0.2)
    S["flfrio"].location = P(CX, CY, SPOT_Z - 0.02 - 0.015 * seg(t, T("si ahí cae"), T("tu comida se"))) if ff > 0.01 else LEJOS
    S["flfrio"].scale = (max(ff, 0.001),) * 3
    fp = win01(t, T("las ondas solo"), T("y a qué"), 0.3, 0.3)
    bases = (P(CX - 0.13, CY - 0.02, PLATE_Z + 0.06), P(CX + 0.13, CY - 0.02, PLATE_Z + 0.06), P(CX, CY - 0.02, PLATE_Z + 0.17))
    for k, (f, b0) in enumerate(zip(S["fl"], bases)):
        if fp < 0.01: f.location = LEJOS; continue
        push = 0.03 * seg(t, T("entran"), T("centímetros", 2, fin=True)) if k < 2 else 0.02 * seg(t, T("entran"), T("centímetros", 2, fin=True))
        dirv = Vector(((1, 0, 0), (-1, 0, 0), (0, 0, -1))[k])
        f.location = b0 + dirv * push; f.scale = (fp,) * 3
    # chocolate: entra cuando sale el plato y se derrite cada 6 cm
    ch = seg(t, T("mete una tableta"), T("de chocolate", fin=True)) * (1 - seg(t, T("qué haces"), T("qué haces") + 0.4))
    if ch > 0.01 and T("quita el plato") < t < T("qué haces") + 0.5:
        S["choco"].location = PC + Vector((0, -0.35 * (1 - ch), 0.0))
        for k, m in enumerate(S["manchas"]):
            u = seg(t, T("se derrite") + 0.35 * k, T("se derrite") + 0.35 * k + 0.5)
            m.scale = (max(u, 0.001), max(u, 0.001), 1 + 0.6 * u)
            set_color(m, CHOCO_D if u > 0.02 else CHOCO)
    else: S["choco"].location = LEJOS
    # regla: 12 cm (onda entera) → 6 cm (media onda)
    rg = win01(t, T("una onda entera"), T("qué haces"), 0.2, 0.3)
    if rg > 0.01:
        L_ = 0.12 - 0.06 * seg(t, T("la mitad"), T("la mitad") + 0.6)
        x0 = -0.09
        S["regla"].location = PC + Vector((x0 + L_ / 2, -0.07, 0.03)); S["regla"].scale = (max(L_ * rg, 0.001), 0.008, 0.008)
        for k, tp in enumerate(S["topes"]): tp.location = PC + Vector((x0 + k * L_, -0.07, 0.03))
    else:
        S["regla"].location = LEJOS
        for tp in S["topes"]: tp.location = LEJOS
    apply_cam(S["cam"], *cam_lin(t, CAM(), drift=0.004))

BOL = tuple(PC + Vector((0, 0, 0.06))); MICRO = tuple(P(0, 0, 0.15)); MAG = tuple(P(0.18, 0.02, 0.17)); CAVI = tuple(P(CX, CY, 0.14))
TODO = (-0.15, 0.55, 1.0); BTN = tuple(P(0.18, -0.19, 0.05)); PLT = tuple(PC)

def CAM():
    k = Claves(); add = k.add
    ini = V(BOL, (0.05, -0.44, 0.2), 38)
    add(0.0, ini)
    add(1.2, V(BOL, (-0.06, -0.42, 0.18), 38))
    add(T("por eso se queda"), V(BOL, (0.0, -0.32, 0.06), 42))
    add(T("cada cuántos"), V(MICRO, (0.12, -1.05, 0.22), 36))
    add(T("escribe"), V(TODO, (0.6, -3.4, 1.0), 30))
    add(T("pulsas") - 0.6, V(BTN, (0.12, -0.42, 0.1), 40))
    add(T("magnetrón"), V(MAG, (0.14, -0.5, 0.12), 40))
    add(T("vibran"), V(CAVI, (0.06, -0.62, 0.1), 38))
    add(T("rebotan"), V(CAVI, (-0.12, -0.66, 0.16), 36))
    add(T("y al cruzarse"), V(CAVI, (0.08, -0.6, 0.06), 38))
    add(T("en unos sitios"), V(CAVI, (-0.05, -0.58, 0.22), 38))
    add(T("en otros"), V(CAVI, (0.1, -0.6, 0.16), 38))
    add(T("tu microondas tiene"), V(MICRO, (-0.15, -1.0, 0.35), 36))
    add(T("siempre en"), V(CAVI, (0.0, -0.55, 0.3), 36))
    add(T("por eso gira"), V(PLT, (0.0, -0.36, 0.34), 40))
    add(T("unas seis") + 0.3, V(PLT, (0.15, -0.32, 0.3), 40))
    add(T("así cada"), V(MICRO, (0.2, -1.0, 0.25), 36))
    add(T("pero hay"), V(PLT, (0.0, -0.3, 0.36), 40))
    add(T("solo gira"), V(PLT, (0.08, -0.3, 0.34), 40))
    add(T("si ahí cae"), V(BOL, (0.0, -0.4, 0.22), 38))
    add(T("tu comida se"), V(BOL, (0.05, -0.3, 0.05), 42))
    add(T("además"), V(BOL, (-0.04, -0.34, 0.1), 40), hold=2.6)
    add(T("y a qué"), V(TODO, (-0.5, -3.3, 1.1), 30))
    add(T("quita el plato") - 0.1, V(CAVI, (0.0, -0.75, 0.15), 36))
    add(T("se derrite"), V(PLT, (0.02, -0.46, 0.26), 38))
    add(T("cada", 3), V(PLT, (-0.06, -0.4, 0.22), 40))
    add(T("una onda entera"), V(PLT, (0.0, -0.36, 0.14), 40))
    add(T("qué haces"), V(MICRO, (0.1, -1.0, 0.3), 36))
    add(T("ponla en anillo"), V(PLT, (0.0, -0.34, 0.34), 40))
    add(T("y a mitad"), V(PLT, (0.1, -0.28, 0.3), 40))
    add(T("te has acercado"), V(TODO, (0.4, -3.2, 1.0), 30))
    add(T("pídelo"), V(MICRO, (-0.1, -1.0, 0.25), 36))
    add(T("sígueme"), V(BOL, (-0.05, -0.42, 0.2), 38))
    add(T("ya sabes"), ini)
    add(T("en el centro", 2), V(BOL, (-0.06, -0.42, 0.18), 38))
    add(DUR + 1, ini)
    return k.k

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v)
    return {"bol": Pj(PC + Vector((0, 0, 0.13))), "nucleo": Pj(P(CX, CY - 0.07, PLATE_Z + 0.05)), "borde": Pj(PC + Vector((-0.06, -0.07, 0.09))),
            "mag": Pj(P(0.18, 0.02, 0.3)), "plato": Pj(PC + Vector((0.0, -0.14, 0.04))), "boton": Pj(P(0.18, -0.19, 0.05)),
            "cav": Pj(P(CX, CY, 0.29)), "regla": Pj(PC + Vector((-0.06, -0.07, 0.06))), "centro": Pj(PC + Vector((0, 0, 0.15))),
            "rastro": Pj(PC + Vector((0.12 * math.cos(plato_ang(t)), 0.12 * math.sin(plato_ang(t)), 0.03))), "choco": Pj(PC + Vector((0, 0, 0.08))),
            "pared": Pj(P(-0.23, -0.06, 0.06))}

if __name__ == "__main__":
    run("microcentro", build, pose, anchors)
