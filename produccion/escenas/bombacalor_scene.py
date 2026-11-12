# «¿Cuánto calor saca tu aire acondicionado de cada kWh de luz?» Piso de maqueta en corte sobre una isla de césped:
# salón (izquierda) con el split en la pared, sofá y persona; balcón (derecha) con la máquina exterior abierta (ventilador,
# batería de tubos y compresor) y nieve cayendo. Un circuito cerrado de tubos en corte une las dos máquinas; el gas son
# bolitas que cambian de color (azul frío → rojo caliente) según por dónde pasan. Resistencia falsa y radiador, −50 °C,
# aire de la calle que pasa calor, compresor que aprieta, gas caliente que llega al salón, ventilador que sopla, válvula,
# cable con la luz, flecha «de fuera a dentro», 1 kWh → 4 kWh, radiador 1 → 1, verano al revés y vuelta al primer plano.
# Planos (fotografía → motion), esquina libre arriba-izquierda salvo indicación:
#  0 ventilador exterior girando con nieve (primer plano) · 1,5 split soplando calor · 4,5 maqueta entera · 7,5 balcón ·
#  9,5 calle a 5 °C · 13 split con resistencia · 15,7 radiador · 17,5 circuito entero · 20 gas a −50 °C · 23 máquina
#  exterior · 26,5 aire que entra · 30 tubo · 32 compresor · 35 gas caliente (libre: arriba-derecha) · 37 sube al salón ·
#  39,6 ventilador del split · 41 salón caliente · 43 válvula · 45,5 maqueta · 47 cable y compresor · 49,6 flecha fuera→dentro ·
#  52,6 maqueta para la cifra · 54,5 split 4 kWh · 56,2 radiador 1 kWh · 58,3 verano · 60,6 vuelta al primer plano.
import bpy, math, sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from modelos import *
from maqueta import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("bombacalor")
WHITE = (0.97, 0.97, 0.98); DARK = (0.18, 0.19, 0.22); COBRE = (0.86, 0.56, 0.36); WOOD = (0.86, 0.64, 0.42)
FRIO = (0.22, 0.52, 1.0); TIBIO = (0.95, 0.95, 0.95); CALOR = (0.96, 0.26, 0.14); YEL = (1.0, 0.85, 0.2)
Y0 = 0.9            # plano del circuito
HW = 2.3            # altura de las paredes

# ---------- circuito (en el plano XZ, y = Y0) ----------
def _circuito():
    pts = []
    for i, x in enumerate((0.55, 0.65, 0.75, 0.85, 0.95)):               # batería exterior (sube y baja)
        z0, z1 = (0.2, 0.68) if i % 2 == 0 else (0.68, 0.2)
        pts += [(x, z0), (x, z1)]
    n_ext = len(pts) - 1
    pts += [(1.22, 0.68), (1.22, 0.45), (1.22, 0.15), (1.38, 0.15)]       # compresor
    n_comp = len(pts) - 1
    pts += [(1.38, 2.02), (-0.7, 2.02)]                                   # tubo caliente al salón
    n_ind0 = len(pts) - 1
    for i, x in enumerate((-0.7, -0.9, -1.1, -1.3, -1.5, -1.7)):          # batería del split
        z0, z1 = (1.9, 1.68) if i % 2 == 0 else (1.68, 1.9)
        if i: pts.append((x, z0))
        pts.append((x, z1))
    n_ind1 = len(pts) - 1
    pts += [(-1.85, 1.9), (-1.85, 1.45), (0.3, 1.45), (0.3, 0.95), (0.3, 0.2), (0.55, 0.2)]   # vuelta (válvula en 0,3 · 0,95)
    return [Vector((x, Y0, z)) for x, z in pts], n_ext, n_comp, n_ind0, n_ind1

CIRC, N_EXT, N_COMP, N_IND0, N_IND1 = _circuito()
LOOP = poly(CIRC); LTOT = largo(LOOP); LC = LOOP[1]
S_EXT, S_COMP, S_IND0, S_IND1 = LC[N_EXT], LC[N_COMP], LC[N_IND0], LC[N_IND1]
S_VALV = LC[len(CIRC) - 3]
NP = 46

def temp_en(s):
    """temperatura del gas según el punto del circuito (modo calor)"""
    s %= LTOT
    if s < S_EXT: return mix(-12, -2, s / S_EXT)                               # batería exterior: coge calor de la calle
    if s < LC[N_EXT + 2]: return -2
    if s < S_COMP: return mix(-2, 75, (s - LC[N_EXT + 2]) / (S_COMP - LC[N_EXT + 2]))   # compresor
    if s < S_IND0: return 72
    if s < S_IND1: return mix(70, 28, (s - S_IND0) / (S_IND1 - S_IND0))         # suelta el calor en el salón
    if s < S_VALV: return 26
    return mix(-18, -12, (s - S_VALV) / (LTOT - S_VALV))                       # tras la válvula, muy frío

def col_temp(T_):
    if T_ < 10: return tuple(mix(a, b, max(0, (T_ + 20) / 30)) for a, b in zip(FRIO, TIBIO))
    return tuple(mix(a, b, min(1, (T_ - 10) / 50)) for a, b in zip(TIBIO, CALOR))

# ---------- modelos propios ----------
def radiador(loc, s=1.0):
    e = empty(loc)
    for i in range(7):
        caja((0.06 * s, 0.22 * s, 0.55 * s), ((i - 3) * 0.075 * s, 0, 0.36 * s), WHITE, e, r=0.025 * s)
    caja((0.55 * s, 0.05 * s, 0.05 * s), (0, 0, 0.08 * s), (0.85, 0.86, 0.88), e)
    for sx in (-1, 1): caja((0.05 * s, 0.3 * s, 0.03 * s), (sx * 0.22 * s, 0, 0.03 * s), (0.85, 0.86, 0.88), e)
    caja((0.08 * s, 0.06 * s, 0.1 * s), (0.3 * s, 0, 0.55 * s), DARK, e, r=0.015 * s)       # mando
    return e

def aspas(loc, r, n, color, rot=(math.pi / 2, 0, 0)):
    """hélice: buje y aspas; gira en su eje local Z"""
    e = empty(loc); e.rotation_euler = rot
    cilindro(r * 0.22, 0.05, (0, 0, 0), DARK, e)
    for i in range(n):
        a = i * math.tau / n
        b = caja((r * 0.85, r * 0.32, 0.02), (math.cos(a) * r * 0.55, math.sin(a) * r * 0.55, 0), color, e, r=0.008)
        b.rotation_euler = (0.35, 0, a)
    return e

def borde(size, loc):   # canto cortado en color crema
    box(size, loc, PAL["corte"])

def build():
    sc, cam = scene_setup(world=PAL["cielo"], shadow=0.25, light_rot=-40); entorno_claro(sc)
    S = {"cam": cam}
    nubes(9, (0, 9, 4.2), 8, 1.4, 1.0, s=1.4, seed=3)
    isla(5.6, 2.9, (0, 0, 0), capas=[(PAL["cesped"], 0.12), (PAL["hormigon"], 0.18), (PAL["tierra"], 0.35), (PAL["tierra2"], 0.4)])
    arbol((2.35, 0.6, 0), 1.2, seed=2); arbusto((2.4, -0.9, 0), 1.3, seed=4)
    # suelo del salón (madera) y del balcón (baldosa)
    caja((2.5, 2.1, 0.06), (-1.3, 0.05, 0.03), WOOD, r=0.01)
    caja((1.95, 2.1, 0.06), (1.03, 0.05, 0.03), (0.86, 0.80, 0.74), r=0.01)
    for k in range(8): box((0.012, 2.1, 0.008), (0.1 + k * 0.25, 0.05, 0.063), (0.75, 0.70, 0.65))
    # paredes: fondo (sigue en el balcón), izquierda y fachada entre salón y balcón (cortada)
    box((4.5, 0.12, HW), (-0.27, 1.12, HW / 2), PAL["pared"]); borde((4.5, 0.122, 0.03), (-0.27, 1.12, HW - 0.014))
    azulejos(1.9, 0.9, (1.03, 1.055, 0.45), color=(0.93, 0.88, 0.80), paso=0.3)
    box((0.12, 2.1, HW), (-2.5, 0.05, HW / 2), PAL["pared"]); borde((0.122, 2.1, 0.03), (-2.5, 0.05, HW - 0.014))
    box((0.15, 0.9, HW), (0.0, 0.65, HW / 2), (0.95, 0.88, 0.76))      # fachada cortada más atrás: la cámara no choca con ella
    borde((0.152, 0.9, 0.03), (0.0, 0.65, HW - 0.014)); borde((0.152, 0.02, HW), (0.0, 0.2, HW / 2))
    box((0.15, 0.04, 0.06), (0.0, -0.4, 0.06), (0.75, 0.72, 0.68))      # umbral de la puerta del balcón
    # barandilla del balcón (lado derecho)
    for k in range(9): cyl(0.015, 0.9, (2.0, -0.95 + k * 0.25, 0.48), WHITE, v=10)
    caja((0.06, 2.1, 0.05), (2.0, 0.05, 0.95), WHITE)
    # salón
    sofa((-1.25, 0.6, 0.06), 1.0, color=PAL["turquesa"], ancho=1.5)
    alfombrilla((-1.25, -0.25, 0.07), 1.5, 0.9, color=PAL["rosa"])
    planta((-2.15, 0.75, 0.06), 1.3)
    S["persona"] = persona((-0.75, -0.35, 0.06), 1.05, ropa=(0.95, 0.55, 0.2))
    caja((0.6, 0.35, 0.3), (-1.25, -0.3, 0.21), WOOD, r=0.03)         # mesa baja
    # split interior abierto por delante
    sx0, sx1, sz0, sz1 = -1.8, -0.6, 1.55, 1.97
    caja((sx1 - sx0, 0.03, sz1 - sz0), ((sx0 + sx1) / 2, 1.04, (sz0 + sz1) / 2), WHITE, r=0.01)
    caja((sx1 - sx0, 0.3, 0.04), ((sx0 + sx1) / 2, 0.9, sz1), WHITE, r=0.015)
    caja((sx1 - sx0, 0.3, 0.03), ((sx0 + sx1) / 2, 0.9, sz0 + 0.015), WHITE, r=0.01)
    for x in (sx0, sx1): caja((0.03, 0.3, sz1 - sz0), (x, 0.9, (sz0 + sz1) / 2), WHITE, r=0.01)
    borde((sx1 - sx0, 0.01, 0.04), ((sx0 + sx1) / 2, 0.75, sz1)); borde((sx1 - sx0, 0.01, 0.03), ((sx0 + sx1) / 2, 0.75, sz0 + 0.015))
    S["led"] = sph(0.012, (sx1 - 0.08, 0.745, sz0 + 0.03), (0.3, 0.9, 0.4), unique=True)
    S["aleta"] = empty(((sx0 + sx1) / 2, 0.76, sz0 + 0.01))
    caja((sx1 - sx0 - 0.06, 0.12, 0.012), (0, -0.06, 0), WHITE, S["aleta"], r=0.004)
    S["ventin"] = empty(((sx0 + sx1) / 2, 0.82, 1.61)); S["ventin"].rotation_euler = (0, math.pi / 2, 0)
    cilindro(0.045, 1.1, (0, 0, 0), (0.75, 0.78, 0.82), S["ventin"], r=0.01)
    for k in range(8):
        a = k * math.tau / 8
        caja((0.012, 0.03, 1.08), (math.cos(a) * 0.052, math.sin(a) * 0.052, 0), (0.45, 0.48, 0.55), S["ventin"], r=0.003)
    # resistencia «falsa» (lo que mucha gente cree) dentro del split
    S["resist"] = empty(LEJOS)
    zz = [(-0.5 + 0.1 * i, 0, 0.05 if i % 2 else -0.05) for i in range(11)]
    tubo(zz, 0.012, (1.0, 0.35, 0.1)).parent = S["resist"]
    # máquina exterior abierta por delante
    ex0, ex1, ez0, ez1 = 0.45, 1.5, 0.1, 0.82
    for sx in (ex0 + 0.12, ex1 - 0.12): caja((0.08, 0.5, 0.08), (sx, 0.78, 0.07), DARK)
    caja((ex1 - ex0, 0.03, ez1 - ez0), ((ex0 + ex1) / 2, 1.02, (ez0 + ez1) / 2), (0.9, 0.9, 0.88))
    caja((ex1 - ex0, 0.45, 0.04), ((ex0 + ex1) / 2, 0.8, ez1), (0.93, 0.93, 0.91), r=0.015)
    caja((ex1 - ex0, 0.45, 0.04), ((ex0 + ex1) / 2, 0.8, ez0 + 0.02), (0.93, 0.93, 0.91), r=0.015)
    for x in (ex0, ex1): caja((0.03, 0.45, ez1 - ez0), (x, 0.8, (ez0 + ez1) / 2), (0.93, 0.93, 0.91), r=0.01)
    caja((0.03, 0.45, ez1 - ez0), (1.08, 0.8, (ez0 + ez1) / 2), (0.88, 0.88, 0.86), r=0.01)   # tabique ventilador | compresor
    borde((ex1 - ex0, 0.01, 0.04), ((ex0 + ex1) / 2, 0.575, ez1)); borde((ex1 - ex0, 0.01, 0.04), ((ex0 + ex1) / 2, 0.575, ez0 + 0.02))
    for x in (ex0, ex1, 1.08): borde((0.03, 0.01, ez1 - ez0), (x, 0.575, (ez0 + ez1) / 2))
    S["vent"] = aspas((0.75, 0.66, 0.45), 0.24, 3, (0.35, 0.37, 0.42))
    torus(0.27, 0.015, (0.75, 0.6, 0.45), DARK, rot=(math.pi / 2, 0, 0))
    S["comp"] = empty((1.22, Y0, 0.12))
    cilindro(0.11, 0.36, (0, 0, 0.18), (0.22, 0.24, 0.28), S["comp"], r=0.04, unique=True)
    cilindro(0.115, 0.03, (0, 0, 0.3), (0.3, 0.32, 0.36), S["comp"], r=0.01)
    # tubos del circuito en corte (se ve el gas por dentro) y válvula
    S["tubo"] = medio_tubo([tuple(p) for p in CIRC], 0.038, 0.012, COBRE, eje=(0, 1, 0))
    S["valv"] = caja((0.12, 0.1, 0.14), (0.3, Y0 + 0.02, 0.95), (0.95, 0.75, 0.2), r=0.02, unique=True)
    # cable de la luz desde el enchufe hasta la máquina
    caja((0.09, 0.03, 0.12), (1.75, 1.04, 0.45), WHITE, r=0.01)
    CAB = [Vector((1.75, 1.0, 0.42)), Vector((1.75, 0.95, 0.25)), Vector((1.5, 0.95, 0.25))]
    S["cabpath"] = poly(CAB); tubo(CAB, 0.014, DARK)
    S["chispas_luz"] = [sph(0.028, LEJOS, YEL, seg=10) for _ in range(5)]
    # gas
    S["gas"] = [sph(0.03, LEJOS, FRIO, seg=10, unique=True) for _ in range(NP)]
    # radiador eléctrico (la comparación)
    S["rad"] = radiador(LEJOS, 1.0)
    S["radglow"] = [box((0.062, 0.23, 0.04), LEJOS, (1.0, 0.35, 0.1)) for _ in range(7)]
    # nieve y sol
    S["nieve"] = [sph(0.03, LEJOS, WHITE, seg=8) for _ in range(40)]
    S["sol"] = sph(0.35, LEJOS, (1.0, 0.82, 0.2), seg=20)
    # flechas: aire de la calle que entra, aire frío que sale, calor al salón, fuera→dentro
    S["fin"] = [flecha3d(LEJOS, (0, 1, 0), 0.24, 0.018, color=(1.0, 0.6, 0.2)) for _ in range(3)]
    S["fout"] = [flecha3d(LEJOS, (0, -1, 0), 0.24, 0.018, color=FRIO) for _ in range(2)]
    S["fsal"] = [flecha3d(LEJOS, (0, -0.6, -0.8), 0.4, 0.035) for _ in range(3)]
    S["fgrande"] = flecha3d(LEJOS, (-1, 0, 0), 2.0, 0.08)
    S["fgrande_v"] = flecha3d(LEJOS, (1, 0, 0), 2.0, 0.08, color=FRIO)
    dyn = [cam, S["persona"], S["led"], S["aleta"], S["ventin"], S["resist"], S["vent"], S["comp"], S["tubo"], S["valv"],
           S["chispas_luz"], S["gas"], S["rad"], S["radglow"], S["nieve"], S["sol"], S["fin"], S["fout"], S["fsal"],
           S["fgrande"], S["fgrande_v"]]
    join_static(dyn)
    return sc, S

# ---------------- estado ----------------
def verano(t): return T("en verano") - 0.1 < t < T("te has acercado") - 0.1

def flujo(t):
    """posición acumulada del gas a lo largo del circuito (se invierte en verano)"""
    a = T("en verano") - 0.1; b = T("te has acercado") - 0.1; v = 0.45
    if t < a: return t * v
    if t < b: return a * v - (t - a) * v
    return a * v - (b - a) * v + (t - b) * v

def pose(t, S):
    ver = verano(t)
    # gas: aparece cuando la voz dice «circuito»
    gas_on = seg(t, T("dentro hay"), T("circuito", fin=True))
    fs = flujo(t)
    for k, g in enumerate(S["gas"]):
        s = (k / NP * LTOT + fs) % LTOT
        if gas_on < 0.01: g.location = LEJOS; continue
        g.location = at(LOOP, s) + Vector((0, -0.01, 0))
        sc_ = gas_on * (1.0 + (0.25 if S_EXT < s < S_COMP and seg(t, T("compresor"), T("compresor") + 0.4) > 0 and t < T("y ese gas") else 0))
        g.scale = (sc_,) * 3
        Tg = temp_en(s)
        if ver: Tg = 55 - Tg
        set_color(g, col_temp(Tg))
    # ventiladores (más rápidos con la luz)
    extra = 1 + 1.5 * win01(t, T("la luz solo"), T("no fabrica"))
    S["vent"].rotation_euler.z = -t * 9 * extra
    S["ventin"].rotation_euler.x = t * 12 * extra * (0.4 + 0.6 * seg(t, 1.2, 2.0))
    S["aleta"].rotation_euler.x = -0.6 * seg(t, 1.6, 2.4)
    set_color(S["led"], (0.3, 0.9, 0.4) if t > 1.6 else (0.5, 0.5, 0.5))
    # compresor que aprieta (late) y se ilumina con la luz
    ap = win01(t, T("compresor"), T("y ese gas"), 0.2, 0.3)
    S["comp"].scale = (1 + 0.06 * ap * math.sin(t * 22), 1 + 0.06 * ap * math.sin(t * 22), 1 - 0.1 * ap * (0.5 + 0.5 * math.sin(t * 22)))
    luz = win01(t, T("la luz solo"), T("no fabrica"))
    set_color(S["comp"].children[0], tuple(mix(a, b, luz * (0.5 + 0.5 * math.sin(t * 10))) for a, b in zip((0.22, 0.24, 0.28), YEL)))
    # válvula: destella cuando el gas vuelve frío
    set_color(S["valv"], tuple(mix(a, b, win01(t, T("el gas", 3), T("y empieza"))) for a, b in zip((0.95, 0.75, 0.2), FRIO)))
    # pulsos de luz por el cable
    for k, c in enumerate(S["chispas_luz"]):
        if luz > 0.01 or (T("por eso") < t < T("un radiador eléctrico")):
            c.location = at(S["cabpath"], ((t * 0.9 + k / 5) % 1.0) * largo(S["cabpath"]))
        else: c.location = LEJOS
    # resistencia que «no existe» y radiador
    res = win01(t, T("resistencia") - 0.2, T("pero no") + 0.2, 0.3, 0.15)
    S["resist"].location = (-1.2, 0.8, 1.78) if res > 0.01 else LEJOS
    S["resist"].scale = (max(res, 0.01),) * 3
    rad = max(win01(t, T("como un radiador"), T("pero no") + 0.25, 0.3, 0.15), win01(t, T("un radiador eléctrico") - 0.2, T("en verano") + 0.1, 0.3, 0.25))
    S["rad"].location = (-2.0, -0.55, 0.06) if rad > 0.01 else LEJOS
    S["rad"].scale = (max(rad, 0.01),) * 3
    glow = rad > 0.5
    for i, gb in enumerate(S["radglow"]):
        gb.location = (-2.0 + (i - 3) * 0.075, -0.55 - 0.115, 0.36 + 0.06 * math.sin(t * 3 + i)) if glow else LEJOS
    # nieve fuera (en invierno) y sol (en verano)
    rnd = random.Random(5)
    for k, n in enumerate(S["nieve"]):
        x = rnd.uniform(0.15, 2.7); y = rnd.uniform(-1.4, 0.9); z = 3.0 - ((t * 0.35 + k / 40) % 1.0) * 3.0
        n.location = (x + 0.05 * math.sin(t * 2 + k), y, z) if not ver else LEJOS
    S["sol"].location = (2.4, 1.5, 3.3) if ver else LEJOS
    # aire de la calle que entra en la máquina (y sale más frío)
    aire = max(win01(t, T("así que el aire"), T("luego") + 0.2), win01(t, 0.0, 1.5, 0.01, 0.3), win01(t, T("en la máquina"), T("el gas está", fin=True)))
    for k, f in enumerate(S["fin"]):
        if aire > 0.01:
            u = (t * 0.8 + k / 3) % 1.0
            f.location = (0.6 + 0.14 * k, 0.2 + 0.3 * u, 0.62 + 0.08 * (k % 2)); f.scale = (aire,) * 3
            if ver: f.location = LEJOS
        else: f.location = LEJOS
    for k, f in enumerate(S["fout"]):
        if aire > 0.01 and not ver:
            u = (t * 0.8 + k / 2) % 1.0
            f.location = (0.66 + 0.18 * k, 0.5 - 0.35 * u, 0.3); f.scale = (aire,) * 3
        else: f.location = LEJOS
    # calor que sale del split al salón
    sop = max(win01(t, 1.8, 4.4), win01(t, T("un ventilador"), T("el gas", 3)), win01(t, T("te da unos"), T("un radiador eléctrico")),
              win01(t, T("te has acercado"), DUR + 1))
    for k, f in enumerate(S["fsal"]):
        if sop > 0.01:
            u = (t * 0.7 + k / 3) % 1.0
            f.location = (-1.6 + 0.4 * k, 0.72 - 0.55 * u, 1.5 - 0.5 * u); f.scale = (sop * (1 - 0.4 * u),) * 3
        else: f.location = LEJOS
    if ver:
        for f in S["fsal"]: f.location = LEJOS
    # flecha grande: de fuera a dentro (y al revés en verano)
    fg = win01(t, T("lo traslada") - 0.3, T("por eso") + 0.3)
    S["fgrande"].location = (1.2 - 0.4 * seg(t, T("lo traslada"), T("por eso")), 0.2, 2.65) if fg > 0.01 else LEJOS
    S["fgrande"].scale = (max(fg, 0.01),) * 3
    fv = win01(t, T("pero al revés") - 0.3, T("te has acercado") - 0.1)
    S["fgrande_v"].location = (-1.4 + 0.4 * seg(t, T("pero al revés"), T("te has acercado")), 0.2, 2.65) if fv > 0.01 else LEJOS
    S["fgrande_v"].scale = (max(fv, 0.01),) * 3
    # la persona se balancea un poco (contenta con el calor)
    S["persona"].rotation_euler.z = 0.25 * math.sin(t * 1.3)
    S["persona"].location.z = 0.06 + 0.02 * abs(math.sin(t * 3)) * win01(t, T("y el calor sale"), T("el gas", 3))
    apply_cam(S["cam"], *cam_lin(t, CAM(), drift=0.02))

FAN = (0.75, 0.62, 0.45); SPLIT = (-1.2, 0.85, 1.75); EXT = (0.98, 0.8, 0.45); COMP = (1.22, 0.9, 0.3)
SALA = (-1.2, 0.2, 0.9); TODO = (-0.25, 0.1, 1.1)

def CAM():
    k = Claves(); add = k.add
    ini = V(FAN, (0.4, -2.05, 0.5), 44)
    add(0.0, V(FAN, (0.15, -1.95, 0.4), 44))
    add(1.3, ini)
    add(T("enciendes") + 0.2, V(SPLIT, (0.5, -2.5, -0.3), 38))
    add(T("modo calor"), V((-1.2, 0.6, 1.4), (0.2, -2.8, 0.1), 34))
    add(T("cuánto calor"), V(TODO, (0.8, -8.6, 3.2), 30))
    add(T("escribe"), V(TODO, (-0.8, -8.0, 2.6), 30))
    add(T("parece magia"), V(EXT, (0.9, -3.0, 1.0), 34))
    add(T("cinco grados") - 0.3, V((1.5, -0.3, 0.8), (1.2, -3.2, 1.0), 34))
    add(T("mucha gente"), V(SPLIT, (0.3, -2.5, -0.1), 40))
    add(T("como un radiador"), V((-1.6, 0.0, 1.0), (-0.4, -3.0, 0.6), 34))
    add(T("pero no"), V(TODO, (0.4, -7.5, 2.4), 30))
    add(T("circuito"), V(TODO, (-0.4, -7.0, 2.0), 30))
    add(T("ese gas hierve"), V((0.3, Y0, 1.2), (0.5, -2.7, 0.3), 40))
    add(T("fuera", 2), V(EXT, (-0.4, -2.4, 0.6), 36))
    add(T("el gas está"), V(EXT, (0.3, -2.2, 0.3), 42))
    add(T("así que el aire"), V(EXT, (1.2, -2.6, 0.9), 34))
    add(T("le pasa calor") - 0.2, V((0.75, Y0, 0.45), (-0.3, -2.3, 0.2), 44))
    add(T("el gas se lo"), V((1.0, Y0, 0.6), (0.6, -2.5, 0.5), 38))
    add(T("compresor"), V(COMP, (0.25, -2.3, 0.25), 48))
    add(T("al apretarlo"), V(COMP, (-0.35, -2.25, 0.5), 46))
    add(T("y ese gas"), V((1.3, Y0, 1.5), (-0.3, -2.8, 0.2), 34))
    add(T("salón"), V(SPLIT, (0.7, -2.3, 0.0), 36))
    add(T("un ventilador"), V(SPLIT, (-0.2, -2.3, -0.25), 46))
    add(T("y el calor sale"), V(SALA, (0.8, -3.6, 0.9), 34))
    add(T("el gas", 3), V((0.3, Y0, 1.0), (0.4, -2.5, 0.2), 40))
    add(T("y empieza"), V(TODO, (0.2, -7.6, 2.6), 30))
    add(T("la luz solo"), V((1.3, 0.9, 0.35), (0.3, -2.4, 0.4), 42))
    add(T("no fabrica"), V((0.0, 0.3, 1.8), (0.0, -6.0, 1.2), 30))
    add(T("lo traslada") + 0.4, V((-0.1, 0.3, 1.8), (-0.6, -6.6, 1.6), 30))
    add(T("por eso"), V(TODO, (0.3, -8.4, 2.8), 30))
    add(T("te da unos"), V(SPLIT, (0.6, -2.6, -0.4), 36))
    add(T("un radiador eléctrico"), V((-1.8, -0.4, 0.6), (0.4, -2.4, 0.4), 36))
    add(T("en verano"), V(TODO, (0.5, -7.6, 2.0), 30))
    add(T("pero al revés"), V(TODO, (-0.4, -7.2, 2.2), 30))
    add(T("te has acercado"), V(FAN, (0.15, -1.95, 0.4), 44))
    add(T("pídelo"), V(FAN, (0.45, -2.1, 0.55), 44))
    add(T("sígueme"), V(FAN, (0.15, -1.95, 0.4), 44))
    add(DUR + 1, ini)
    return k.k

def anchors(sc, S, t):
    cam = S["cam"]; P = lambda v: proj(sc, cam, v)
    return {"fan": P((0.75, 0.6, 0.8)), "split": P((-1.2, 0.85, 2.05)), "ext": P((0.98, 0.8, 0.9)), "comp": P((1.22, 0.9, 0.55)),
            "sala": P((-1.2, 0.0, 1.3)), "calle": P((1.7, -0.6, 1.3)), "gas": P((0.3, Y0, 1.6)), "rad": P((-2.0, -0.55, 0.9)),
            "enchufe": P((1.65, 0.95, 0.75)), "tubo": P((0.9, Y0, 2.2))}

if __name__ == "__main__":
    run("bombacalor", build, pose, anchors)
