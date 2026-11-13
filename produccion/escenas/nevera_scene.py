# «¿Guardas la leche en la puerta de la nevera?» Cocina de maqueta sobre una isla cortada (baldosas, hormigón, tierra):
# pared de azulejos, bancada con fogones a la derecha y la nevera con la pared izquierda cortada (cantos crema) para ver
# las baldas, el panel frío del fondo y los balcones de la puerta. La puerta se abre de verdad (bisagra a la derecha) con
# el cartón de leche en su balcón. Aire frío (bolitas azules) que cae por abajo al abrir, aire de la cocina (naranja) que
# entra por arriba y toca la puerta, regla del fondo a la puerta, termómetros de la balda de arriba y de la puerta, una
# segunda isla con 200 neveras (6 de cada 10 puertas en rojo), bacterias que crecen en el cartón y el cartón que se muda
# a la balda del medio, al fondo, mientras salsas y refrescos entran en la puerta.
# Planos (fotografía → motion; esquina libre arriba-izquierda salvo el mini del juego, que la ocupa desde 7 s):
#  0 puerta abriéndose con el cartón, a 1,2 m · 1,7 balcón de la puerta · 2,7 nevera entera · 4,4 balda de arriba ·
#  5,6 puerta abierta · 7,0 cocina entera · 9,4 mano en el tirador · 11,7 aire frío que cae · 14,1 suelo frío ·
#  15,7 aire caliente arriba · 17,1 22 °C · 19,4 aire que llega a la puerta · 22,4 corte lateral, panel del fondo ·
#  24,3 regla fondo → puerta · 26,1 puerta que se abre 3 veces · 28,2 isla de 200 neveras · 30,8 termómetro de arriba ·
#  33,9 termómetro de la puerta · 36,6 revelación · 38,4 fila de 10 neveras · 41,3 bacterias en el cartón ·
#  43,4 bacterias cerca · 45,4 cartón 17 días · 48,1 cartón 14 días · 50,8 puerta abierta · 52,4 balda del medio ·
#  54,5 al fondo · 55,4 salsas en la puerta · 57,9 cocina · 60,4 nevera · 62,7 cocina · 65,0 vuelta al primer plano.
import bpy, math, sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from modelos import *
from maqueta import *
from marcas import cargar
from mathutils import Vector, Matrix

T, DUR = cargar("nevera")
WHITE = (0.97, 0.97, 0.98); LINER = (0.92, 0.94, 0.96); GRIS = (0.80, 0.82, 0.86); CRISTAL = (0.78, 0.90, 0.96)
FRIO = (0.30, 0.62, 1.0); CALIDO = (1.0, 0.58, 0.20); PIEL = (0.96, 0.78, 0.64); BACT = (0.45, 0.85, 0.30)
SUELO = (0.90, 0.86, 0.78); LECHE_AZ = (0.25, 0.50, 0.90)

FW, FD, FH = 0.62, 0.62, 1.75                  # nevera: ancho, fondo, alto
FY = 0.35                                      # centro de la nevera en Y (frontal en y = FY - FD/2 = 0.04)
HINGE = Vector((0.31, 0.0, 0.0))               # bisagra de la puerta (derecha)
YB = FY + FD / 2 - 0.03                        # pared del fondo por dentro
BALDAS = (0.52, 0.97, 1.42)                    # alturas de las baldas (abajo, medio, arriba)
BALC = (0.36, 0.76, 1.16, 1.46)                # alturas de los balcones de la puerta
G0 = Vector((-3.3, 0.3, 0.0))                  # isla de las 200 neveras
NC, NF = 20, 10                                # columnas y filas de neveras pequeñas
N_FRIO, N_CAL, N_BAC = 26, 22, 30

def puerta_ang(t):
    """grados de apertura de la puerta (0 cerrada, 95 abierta)"""
    a = T("abres"); c = T("el frío sale"); v = T("varias veces"); h = T("qué haces"); f = T("ya sabes")
    if t < 2.7: return mix(20, 95, ss(t / 2.7))
    if t < a - 0.2: return 95 * (1 - seg(t, 6.6, 7.6))
    if t < c: return 95 * seg(t, a + 0.1, a + 1.2) * (1 - seg(t, c - 0.9, c - 0.1))
    if t < v - 0.1: return 0.0
    if t < T("investigadores"): return 70 * abs(math.sin((t - v) * math.pi * 3 / max(T("al día", fin=True) - v, 0.5)))
    if t < h: return 0.0
    if t < T("te has acercado"): return 95 * seg(t, h - 0.2, h + 0.7) * (1 - seg(t, T("salsas", fin=True) + 0.3, T("te has acercado") + 0.2))
    if t < f - 0.1: return 0.0
    return 95 * seg(t, f - 0.1, f + 1.2) * (1 - seg(t, f + 1.5, DUR + 0.4)) + 20 * seg(t, f + 1.5, DUR + 0.4)

def D(t, local):
    """punto de la puerta (coordenadas locales desde la bisagra) en el mundo"""
    a = math.radians(puerta_ang(t))
    return HINGE + Matrix.Rotation(a, 3, 'Z') @ Vector(local)

def carton_pos(t):
    """el cartón: en el balcón de la puerta, se muda a la balda del medio (al fondo) y vuelve al final a la puerta"""
    en_puerta = D(t, (-0.2, 0.09, BALC[1] + 0.11))
    medio = Vector((-0.12, YB - 0.1, BALDAS[1] + 0.115))
    medio_delante = Vector((-0.12, 0.25, BALDAS[1] + 0.115))
    u1 = seg(t, T("leche y yogures"), T("balda del medio", fin=True))
    u2 = seg(t, T("al fondo") - 0.1, T("al fondo", fin=True) + 0.2)
    u3 = seg(t, T("ya sabes") - 0.4, T("ya sabes") + 0.4)
    p = en_puerta.lerp(medio_delante, u1)
    if u1 > 0: p = p + Vector((0, 0, 0.12 * math.sin(math.pi * u1)))
    p = p.lerp(medio, u2)
    return p.lerp(D(t, (-0.2, 0.09, BALC[1] + 0.11)), u3)

def build():
    sc, cam = scene_setup(world=PAL["cielo"], shadow=0.25, light_rot=60); entorno_claro(sc)
    S = {"cam": cam}
    nubes(9, (-1.0, 7, 3.4), 7, 1.2, 1.0, s=1.2, seed=7)
    # ---------- isla de la cocina ----------
    isla(3.4, 2.4, (0, 0.1, 0), capas=[(SUELO, 0.08), (PAL["hormigon"], 0.16), (PAL["tierra"], 0.32), (PAL["tierra2"], 0.36)])
    for k in range(8): box((0.012, 2.4, 0.006), (-1.5 + k * 0.43, 0.1, 0.003), (0.80, 0.74, 0.65))
    for k in range(6): box((3.4, 0.012, 0.006), (0, -1.0 + k * 0.43, 0.003), (0.80, 0.74, 0.65))
    box((3.4, 0.1, 2.3), (0, 1.25, 1.15), PAL["pared"]); box((3.4, 0.102, 0.03), (0, 1.25, 2.285), PAL["corte"])
    azulejos(3.2, 0.62, (0.0, 1.19, 1.22), color=PAL["turquesa"], paso=0.15)
    cocina((1.1, 0.85, 0), 1.0, ancho=1.1)
    olla((1.0, 0.85, 0.905), 0.7)
    caja((1.05, 0.32, 0.5), (1.1, 1.03, 1.8), (0.97, 0.74, 0.55), r=0.02)
    planta((1.6, 1.0, 0.905), 0.8)
    planta((-1.4, 0.95, 0.0), 1.6)
    alfombrilla((-0.6, -0.45, 0.01), 0.7, 0.45, color=PAL["rosa"])
    caja((0.5, 0.5, 0.75), (-1.2, -0.2, 0.375), PAL["madera"], r=0.03)          # mesita auxiliar
    cilindro(0.06, 0.12, (-1.25, -0.25, 0.81), (0.97, 0.55, 0.30), r=0.02)       # frutero
    for k in range(3): bola(0.035, (-1.27 + 0.04 * k, -0.24 + 0.02 * (k % 2), 0.9), (0.95, 0.35 + 0.2 * k, 0.2))
    # ---------- nevera (pared izquierda cortada) ----------
    x0, x1 = -FW / 2, FW / 2; yf, yb = FY - FD / 2, FY + FD / 2
    caja((0.03, FD, FH), (x1 - 0.015, FY, FH / 2), WHITE, r=0.01)                 # pared derecha
    caja((FW, 0.03, FH), (0, yb - 0.015, FH / 2), WHITE, r=0.01)                  # fondo
    caja((FW, FD, 0.05), (0, FY, FH - 0.025), WHITE, r=0.012)                     # techo
    caja((FW, FD, 0.2), (0, FY, 0.1), WHITE, r=0.012)                             # base (compresor)
    box((0.004, FD - 0.06, FH - 0.27), (x1 - 0.032, FY, FH / 2 + 0.07), LINER)     # forro interior
    box((FW - 0.06, 0.004, FH - 0.27), (0, yb - 0.032, FH / 2 + 0.07), LINER)
    for z in (0.2, FH - 0.05):                                                    # cantos del corte (pared izquierda)
        box((0.012, FD, 0.025), (x0 + 0.006, FY, z), PAL["corte"])
    box((0.012, 0.025, FH), (x0 + 0.006, yb - 0.012, FH / 2), PAL["corte"])
    box((0.012, 0.025, FH), (x0 + 0.006, yf + 0.012, FH / 2), PAL["corte"])
    box((0.03, 0.012, FH), (x0 + 0.015, yb + 0.006, FH / 2), PAL["corte"])
    # panel frío del fondo (evaporador) con rejilla
    caja((0.4, 0.02, 0.35), (0, YB - 0.01, 1.55), (0.62, 0.80, 0.96), r=0.008)
    for k in range(6): box((0.34, 0.006, 0.012), (0, YB - 0.022, 1.42 + 0.05 * k), (0.48, 0.66, 0.88))
    S["evap"] = caja((0.3, 0.008, 0.06), (0, YB - 0.026, 1.66), FRIO, r=0.003, unique=True)
    # baldas de cristal con perfil, cajón de verduras
    for z in BALDAS:
        caja((FW - 0.07, FD - 0.2, 0.012), (0, FY + 0.07, z), CRISTAL, r=0.004)
        box((FW - 0.07, 0.012, 0.02), (0, FY - 0.03, z + 0.01), (0.86, 0.88, 0.9))
    caja((FW - 0.08, FD - 0.22, 0.24), (0, FY + 0.07, 0.34), (0.86, 0.94, 0.88), r=0.02)
    for k in range(4): bola(0.05, (-0.18 + 0.12 * k, FY + 0.05, 0.43), ((0.4, 0.8, 0.3), (0.95, 0.3, 0.2), (0.98, 0.6, 0.2), (0.4, 0.8, 0.3))[k])
    # cosas en las baldas (quietas): queso, táper, huevera, tarro
    caja((0.14, 0.1, 0.06), (0.12, FY + 0.15, BALDAS[2] + 0.04), (1.0, 0.86, 0.35), r=0.01)
    caja((0.16, 0.12, 0.07), (0.1, FY + 0.12, BALDAS[0] + 0.045), (0.55, 0.85, 0.75), r=0.015)
    caja((0.2, 0.08, 0.05), (0.08, FY + 0.18, BALDAS[1] + 0.035), (0.96, 0.92, 0.8), r=0.01)
    for k in range(3): bola(0.022, (0.03 + 0.05 * k, FY + 0.18, BALDAS[1] + 0.07), (0.98, 0.9, 0.78), escala=(1, 1, 1.25))
    cilindro(0.04, 0.09, (0.2, FY + 0.18, BALDAS[0] + 0.055), (0.9, 0.35, 0.3), r=0.01)
    # termómetro de la balda de arriba (columna roja que sube y baja)
    S["t1col"] = termometro(Vector((-0.17, FY + 0.12, BALDAS[2] + 0.012)))
    # ---------- puerta (hijos del empty de la bisagra) ----------
    S["puerta"] = empty(HINGE); S["puerta"].rotation_mode = 'XYZ'
    caja((FW, 0.07, FH - 0.02), (-FW / 2, -0.035, FH / 2), WHITE, S["puerta"], r=0.02)
    caja((0.03, 0.035, 0.42), (-FW + 0.045, -0.09, 1.05), (0.70, 0.72, 0.76), S["puerta"], r=0.012)      # tirador
    for dz in (0.84, 1.26): caja((0.03, 0.04, 0.03), (-FW + 0.045, -0.075, dz), (0.70, 0.72, 0.76), S["puerta"], r=0.01)
    S["forro"] = caja((FW - 0.06, 0.01, FH - 0.12), (-FW / 2, 0.002, FH / 2), LINER, S["puerta"], r=0.004, unique=True)
    for z in BALC:
        caja((FW - 0.1, 0.1, 0.015), (-FW / 2, 0.06, z), (0.86, 0.9, 0.94), S["puerta"], r=0.004)
        caja((FW - 0.1, 0.012, 0.07), (-FW / 2, 0.11, z + 0.035), (0.80, 0.90, 0.97), S["puerta"], r=0.004)
    S["t2col"] = termometro(Vector((-0.12, 0.075, BALC[2] + 0.008)), parent=S["puerta"])
    # yogures (en la puerta al principio, luego a la balda del medio) y salsas/refrescos que entran al final
    S["yogures"] = [cilindro(0.028, 0.06, LEJOS, c, r=0.008, unique=True) for c in ((0.98, 0.6, 0.7), (0.98, 0.85, 0.4), (0.75, 0.55, 0.9))]
    S["botes"] = []
    for k, (c, h_, rr) in enumerate((((0.9, 0.18, 0.15), 0.16, 0.028), ((0.98, 0.8, 0.15), 0.15, 0.026), ((0.25, 0.65, 0.95), 0.12, 0.03),
                                     ((0.95, 0.3, 0.35), 0.12, 0.03), ((0.35, 0.8, 0.45), 0.12, 0.03))):
        b = empty(LEJOS); cilindro(rr, h_, (0, 0, h_ / 2), c, b, r=0.008); cilindro(rr * 0.5, 0.03, (0, 0, h_ + 0.012), (0.95, 0.95, 0.95), b, r=0.004)
        S["botes"].append(b)
    # cartón de leche (blanco con franja azul y tejadillo)
    S["carton"] = empty(LEJOS)
    caja((0.09, 0.09, 0.2), (0, 0, 0), (0.98, 0.98, 0.99), S["carton"], r=0.006)
    caja((0.092, 0.092, 0.05), (0, 0, 0.02), LECHE_AZ, S["carton"], r=0.004)
    caja((0.09, 0.07, 0.045), (0, 0, 0.11), (0.97, 0.97, 0.98), S["carton"], r=0.003, rot=(math.radians(45), 0, 0))
    caja((0.092, 0.01, 0.03), (0, 0, 0.14), (0.97, 0.97, 0.98), S["carton"], r=0.002)
    cilindro(0.012, 0.012, (0.02, -0.02, 0.135), LECHE_AZ, S["carton"], rot=(math.radians(45), 0, 0))
    S["bact"] = [bola(0.009, LEJOS, BACT, sub=1) for _ in range(N_BAC)]
    # aire frío (azul) y aire de la cocina (naranja)
    S["frio"] = [sph(0.018, LEJOS, FRIO, seg=10) for _ in range(N_FRIO)]
    S["cal"] = [sph(0.02, LEJOS, CALIDO, seg=10) for _ in range(N_CAL)]
    S["fl_frio"] = flecha3d(LEJOS, (0, -0.3, -1), 0.3, 0.025, color=FRIO)
    S["fl_cal"] = flecha3d(LEJOS, (0, 1, -0.25), 0.3, 0.025, color=CALIDO)
    S["fl_fondo"] = [flecha3d(LEJOS, (0, -1, 0), 0.22, 0.02, color=FRIO) for _ in range(3)]
    S["regla"] = box((0.012, 1, 0.012), LEJOS, PAL["amarillo"], unique=True)
    S["topes"] = [box((0.012, 0.012, 0.06), LEJOS, PAL["amarillo"]) for _ in range(2)]
    # mano que tira del tirador y empuja el cartón
    S["mano"] = empty(LEJOS)
    caja((0.07, 0.05, 0.1), (0, -0.03, 0), PIEL, S["mano"], r=0.02)
    for k in range(4): cilindro(0.009, 0.05, (0.02, 0.0, -0.035 + 0.023 * k), PIEL, S["mano"], rot=(0, math.pi / 2, 0), r=0.004)
    cilindro(0.032, 0.25, (-0.02, -0.17, 0.0), (0.42, 0.6, 0.9), S["mano"], rot=(math.pi / 2, 0, 0), r=0.01)
    # ---------- isla de las 200 neveras ----------
    isla(2.3, 1.45, tuple(G0), capas=[(PAL["cesped"], 0.08), (PAL["tierra"], 0.25), (PAL["tierra2"], 0.3)])
    S["minis"] = []
    for j in range(NF):
        for i in range(NC):
            m = nevera((G0.x - 0.95 + i * 0.1, G0.y - 0.5 + j * 0.12, 0.0), 0.12, unique=(j == 0 and i < 10))
            S["minis"].append(m)
    S["mini_puertas"] = [[c for c in S["minis"][i].children if c.name.startswith("puerta")][0] for i in range(10)]
    dyn = [cam, S["evap"], S["t1col"], S["puerta"], S["yogures"], S["botes"], S["carton"], S["bact"], S["frio"], S["cal"],
           S["fl_frio"], S["fl_cal"], S["fl_fondo"], S["regla"], S["topes"], S["mano"], S["minis"]]
    join_static(dyn)
    return sc, S

def termometro(base, parent=None):
    """termómetro de nevera: cuerpo blanco, tubo y columna roja (se devuelve la columna, que se escala en z)"""
    e = empty(base, parent)
    caja((0.05, 0.02, 0.17), (0, 0, 0.085), (0.99, 0.99, 0.99), e, r=0.008)
    for k in range(7): box((0.014, 0.004, 0.003), (0.014, -0.011, 0.03 + 0.019 * k), (0.4, 0.4, 0.45), e)
    box((0.01, 0.004, 0.13), (-0.006, -0.011, 0.09), (0.85, 0.9, 0.95), e)
    sph(0.011, (-0.006, -0.012, 0.022), PAL["rojo"], e, seg=12)
    col = box((0.007, 0.006, 1.0), (-0.006, -0.013, 0.03), PAL["rojo"], e, unique=True)
    return col

def termo_set(col, grados):
    """columna para 0-8 °C"""
    h = 0.012 + 0.11 * max(0.0, min(1.0, grados / 8.0))
    col.scale = (0.007, 0.006, h); col.location.z = 0.025 + h / 2

# ---------------- estado ----------------
def temp_puerta(t):
    if t < T("y con cada"): return keyed(t, [(0, 3.5), (T("y la puerta", 2) + 0.2, 3.5), (T("cinco coma"), 5.2)])
    if t < T("un cartón"): return 5.2 + 0.6 * seg(t, T("y con cada"), T("bacterias", fin=True))
    return keyed(t, [(T("un cartón"), 4.0), (T("a seis grados"), 4.0), (T("a seis grados", fin=True) + 0.4, 6.0), (T("qué haces"), 5.0)])

def temp_arriba(t):
    return keyed(t, [(0, 3.0), (T("la balda de arriba", 2, fin=True), 3.0), (T("uno coma nueve", fin=True), 1.9)])

def pose(t, S):
    a = puerta_ang(t)
    S["puerta"].rotation_euler = (0, 0, math.radians(a))
    # puerta que se calienta cuando le llega el aire de la cocina
    cal = win01(t, T("y qué es lo primero") - 0.5, T("el frío sale") + 0.6, 0.8, 0.6) + 0.6 * win01(t, T("y la puerta", 2) - 0.2, T("tres coma") + 1.0)
    set_color(S["forro"], tuple(mix(x, y, 0.55 * min(cal, 1.0)) for x, y in zip(LINER, (1.0, 0.75, 0.5))))
    set_color(S["evap"], tuple(mix(x, y, 0.5 + 0.5 * math.sin(t * 4)) for x, y in zip(FRIO, (0.75, 0.9, 1.0))))
    termo_set(S["t1col"], temp_arriba(t)); termo_set(S["t2col"], temp_puerta(t))
    # cartón y yogures
    S["carton"].location = carton_pos(t)
    w_ = seg(t, T("leche y yogures"), T("balda del medio", fin=True)) * (1 - seg(t, T("ya sabes") - 0.4, T("ya sabes") + 0.4))
    S["carton"].rotation_euler = (0, 0, math.radians(a) * (1 - w_))
    for k, y in enumerate(S["yogures"]):
        enp = D(t, (-0.42 + 0.075 * k, 0.07, BALC[3] + 0.04))
        med = Vector((0.02 + 0.075 * k - 0.02, YB - 0.13, BALDAS[1] + 0.042))
        u = seg(t, T("yogures") + 0.15 * k, T("yogures") + 0.8 + 0.15 * k)
        y.location = enp.lerp(med, u) + Vector((0, 0, 0.1 * math.sin(math.pi * u)))
    # salsas y refrescos: entran en la puerta
    for k, b in enumerate(S["botes"]):
        u = seg(t, T("salsas") + 0.18 * k, T("salsas") + 0.5 + 0.18 * k)
        if u < 0.01: b.location = LEJOS; continue
        slot = ((-0.47, BALC[2]), (-0.39, BALC[2]), (-0.3, BALC[0]), (-0.22, BALC[0]), (-0.14, BALC[0]))[k]
        b.location = D(t, (slot[0], 0.065, slot[1] + 0.008)); s_ = back_(u); b.scale = (s_, s_, s_)
        b.rotation_euler = (0, 0, math.radians(a))
    # bacterias en el cartón: crecen con cada grado de más
    nb = win01(t, T("bacterias") - 0.3, T("qué haces") + 0.3, 0.3, 0.4)
    cuantas = int(N_BAC * (0.15 + 0.45 * seg(t, T("bacterias"), T("más rápido", fin=True)) + 0.4 * seg(t, T("a seis grados"), T("días menos", fin=True))))
    rnd = random.Random(3); cp = carton_pos(t)
    for k, b in enumerate(S["bact"]):
        ox, oz = rnd.uniform(-0.04, 0.04), rnd.uniform(-0.08, 0.1); side = rnd.choice((-1, 1))
        if nb < 0.01 or k >= cuantas: b.location = LEJOS; continue
        b.location = cp + Vector((-0.047, ox, oz)) if side < 0 else cp + Vector((ox, -0.047, oz))
        pul = 1 + 0.25 * math.sin(t * 6 + k); b.scale = (nb * pul,) * 3
    # aire frío: dentro circula, al abrir cae por abajo y se esparce por el suelo
    caida = win01(t, T("abres") + 0.6, T("y por arriba"), 0.5, 0.6) + win01(t, 0.0001, 4.0, 0.01, 1.0) * 0.8
    fondo = win01(t, T("el frío sale") - 0.2, T("varias veces"), 0.3, 0.3)
    rf = random.Random(11)
    for k, b in enumerate(S["frio"]):
        x, z0, ph = rf.uniform(-0.24, 0.24), rf.uniform(0.6, 1.5), rf.random()
        if fondo > 0.01:   # del panel del fondo hacia la puerta, despacio
            u = (t * 0.22 + ph) % 1.0
            b.location = Vector((x * 0.9, YB - 0.04 - u * (YB - 0.1), 1.55 - 1.0 * (k % 5) / 4 - 0.05 * u)); b.scale = (fondo,) * 3
        elif caida > 0.01:
            u = (t * 0.45 + ph) % 1.0
            if u < 0.45: p = Vector((x, 0.45 - 0.9 * u, z0 * (1 - u / 0.45) + 0.24 * (u / 0.45)))
            else:
                w = (u - 0.45) / 0.55; p = Vector((x * (1 + w), 0.04 - 0.75 * w, 0.24 * (1 - w) ** 2 + 0.03))
            b.location = p; b.scale = (caida,) * 3
        else:
            b.location = LEJOS
    S["fl_frio"].location = Vector((-0.05, -0.12, 0.38 - 0.08 * seg(t, T("se cae"), T("por abajo", fin=True)))) if caida > 0.3 and t > 9 else LEJOS
    S["fl_frio"].scale = (max(win01(t, T("así que se cae") - 0.3, T("y por arriba") + 0.2), 0.001),) * 3
    for k, f in enumerate(S["fl_fondo"]):
        f.location = Vector((-0.12 + 0.12 * k, YB - 0.07 - 0.1 * seg(t, T("el frío sale"), T("fondo de la", fin=True)), 1.3 - 0.35 * k)) if fondo > 0.01 else LEJOS
        f.scale = (max(fondo, 0.001),) * 3
    # aire de la cocina (22 °C): entra por arriba y lo primero que toca es la puerta
    ent = win01(t, T("y por arriba") - 0.1, T("el frío sale") - 0.3, 0.4, 0.5)
    toca = seg(t, T("y qué es lo primero"), T("la puerta", 3))
    rc = random.Random(5)
    for k, b in enumerate(S["cal"]):
        z0, ph = rc.uniform(1.15, 1.65), rc.random()
        if ent < 0.01: b.location = LEJOS; continue
        u = (t * 0.35 + ph) % 1.0
        libre = Vector((rc.uniform(-0.25, 0.2), -0.7 + 0.95 * u, z0 - 0.15 * u))
        balc = D(t, (-0.1 - 0.42 * ((k * 0.37 + t * 0.1) % 1.0), 0.03 - 0.12 * ((k % 3) / 2), BALC[k % 4] + 0.05 + 0.02 * math.sin(t * 3 + k)))
        b.location = libre.lerp(balc, toca * (0.5 + 0.5 * (k % 2))); b.scale = (ent,) * 3
    S["fl_cal"].location = Vector((-0.05, -0.55 + 0.1 * seg(t, T("y por arriba"), T("cocina", fin=True)), 1.62)) if ent > 0.01 else LEJOS
    S["fl_cal"].scale = (max(ent * (1 - toca), 0.001),) * 3
    # regla del fondo a la puerta (lejísimos)
    rg = win01(t, T("y la puerta queda") - 0.2, T("varias veces"), 0.3, 0.3)
    if rg > 0.01:
        L = (YB - 0.07) * seg(t, T("y la puerta queda"), T("lejísimos", fin=True)) + 0.01
        S["regla"].location = Vector((-0.27, YB - L / 2, 1.08)); S["regla"].scale = (0.012, L, 0.012)
        S["topes"][0].location = Vector((-0.27, YB, 1.08)); S["topes"][1].location = Vector((-0.27, YB - L, 1.08))
    else:
        S["regla"].location = LEJOS
        for tp in S["topes"]: tp.location = LEJOS
    # mano: tira del tirador al abrir y empuja el cartón al fondo
    ab = T("abres")
    if ab - 0.6 <= t < ab + 1.8:
        u = seg(t, ab - 0.6, ab) * (1 - seg(t, ab + 1.3, ab + 1.8))
        S["mano"].location = D(t, (-FW + 0.045, -0.13 - 0.25 * (1 - u), 1.05)); S["mano"].rotation_euler = (0, 0, math.radians(a))
    else:
        S["mano"].location = LEJOS
    # 200 neveras que aparecen fila a fila; 6 de cada 10 puertas en rojo
    ap = seg(t, T("investigadores") - 0.3, T("de verdad", fin=True))
    vis_g = T("investigadores") - 0.5 < t < T("y con cada") + 0.3
    for idx, m in enumerate(S["minis"]):
        j, i = divmod(idx, NC)
        if not vis_g: m.scale = (0.001,) * 3; continue
        u = max(0.0, min(1.0, ap * (NF + 2) - j - i / NC))
        s_ = back_(u) if u < 1 else 1.0; m.scale = (max(s_, 0.001),) * 3
    rojas = (0, 2, 3, 5, 7, 8)
    for i, p in enumerate(S["mini_puertas"]):
        r_ = seg(t, T("seis de cada") + 0.25 * rojas.index(i), T("seis de cada") + 0.25 * rojas.index(i) + 0.3) if i in rojas else 0.0
        set_color(p, tuple(mix(x, y, r_) for x, y in zip((0.95, 0.96, 0.97), PAL["rojo"])))
    apply_cam(S["cam"], *cam_lin(t, CAM(), drift=0.006))

def back_(u):
    u = max(0.0, min(1.0, u)); c = 1.70158
    return 1 + (c + 1) * (u - 1) ** 3 + c * (u - 1) ** 2

FR = (0.0, 0.3, 0.95); TODO = (0.0, 0.3, 0.9); ARR = (-0.12, FY + 0.12, BALDAS[2] + 0.1); MED = (-0.05, FY + 0.15, BALDAS[1] + 0.1)
FONDO = (-0.05, 0.35, 1.2); SUELO_F = (0.0, -0.3, 0.15); TECHO = (0.0, -0.2, 1.5)
def P_ABIERTA(z): return tuple(HINGE + Matrix.Rotation(math.radians(95), 3, 'Z') @ Vector((-0.3, 0.06, z)))
def P_CERR(z): return (0.11, 0.1, z)          # cartón en la puerta cerrada (se ve por la pared cortada)
GRID = (G0.x, G0.y - 0.1, 0.1); FILA = (G0.x - 0.5, G0.y - 0.5, 0.08)

def CAM():
    k = Claves(); add = k.add
    ini = V((0.09, 0.02, BALC[1] + 0.13), (-0.7, -0.36, 0.17), 36)
    add(0.0, ini)
    add(1.7, V(P_ABIERTA(BALC[1] + 0.1), (-0.6, -0.45, 0.15), 38))
    add(2.75, V(FR, (-1.1, -2.2, 0.5), 30))
    add(T("cuántos grados"), V(ARR, (-0.65, -0.45, 0.12), 38))
    add(T("en la puerta", 2), V(P_ABIERTA(1.1), (-0.7, -0.5, 0.1), 36))
    add(T("escribe"), V(TODO, (-0.4, -3.6, 1.0), 28))
    add(T("abres") - 0.2, V((-0.25, -0.1, 1.05), (-0.75, -0.75, 0.1), 34))
    add(T("el aire frío"), V(SUELO_F, (-0.9, -0.9, 0.55), 32))
    add(T("así que se cae"), V(SUELO_F, (-0.6, -1.0, 0.3), 34))
    add(T("y por arriba"), V(TECHO, (-0.9, -0.85, 0.15), 32))
    add(T("a unos") - 0.3, V(TECHO, (-0.6, -0.9, 0.3), 34))
    add(T("y qué es lo primero"), V(P_ABIERTA(1.2), (-0.75, -0.55, 0.2), 34))
    add(T("la puerta", 3) + 0.1, V(P_ABIERTA(1.0), (-0.55, -0.35, 0.1), 38))
    add(T("el frío sale"), V(FONDO, (-1.2, -0.5, 0.2), 32))
    add(T("y la puerta queda"), V(FONDO, (-1.0, -0.8, 0.35), 32))
    add(T("y tú la abres"), V(FR, (-1.0, -1.9, 0.4), 30), hold=1.95)
    add(T("investigadores") - 0.2, V(GRID, (0.3, -1.9, 1.5), 30))
    add(T("doscientas") - 0.6, V(GRID, (-0.3, -1.6, 1.25), 32), hold=1.4)
    add(T("la balda de arriba", 2) - 0.45, V(ARR, (-0.6, -0.35, 0.1), 40))
    add(T("y la puerta", 2) - 0.05, V((0.19, 0.075, BALC[2] + 0.09), (-0.48, 0.05, 0.12), 38), hold=T("tres coma") + 0.9 - T("y la puerta", 2))
    add(T("seis de cada") - 0.2, V(FILA, (0.0, -1.0, 0.35), 34))
    add(T("pasaban") - 0.1, V(FILA, (0.3, -0.85, 0.25), 36), hold=1.1)
    add(T("y con cada"), V(P_CERR(BALC[1] + 0.12), (-0.62, 0.05, 0.15), 38))
    add(T("bacterias") + 0.1, V(P_CERR(BALC[1] + 0.12), (-0.56, 0.05, 0.1), 38))
    add(T("un cartón") - 0.05, V(P_CERR(BALC[1] + 0.1), (-0.6, 0.06, 0.14), 38))
    add(T("a seis grados") - 0.6, V(P_CERR(BALC[1] + 0.1), (-0.58, 0.04, 0.06), 38), hold=T("días menos", fin=True) - T("a seis grados") + 0.3)
    add(T("qué haces") - 0.1, V(FR, (-1.0, -1.5, 0.3), 32))
    add(T("balda del medio") - 0.2, V(MED, (-0.7, -0.6, 0.2), 36))
    add(T("al fondo") - 0.1, V(MED, (-0.5, -0.45, 0.08), 38))
    add(T("salsas") - 0.3, V(P_ABIERTA(0.8), (-0.75, -0.55, 0.15), 34))
    add(T("te has acercado"), V(TODO, (-0.6, -3.4, 1.0), 28))
    add(T("pídelo") - 0.2, V(FR, (-1.2, -1.6, 0.4), 30))
    add(T("lo más pedido"), V(MED, (-0.75, -0.6, 0.3), 34))
    add(T("sígueme"), V(TODO, (0.4, -3.4, 0.9), 28))
    add(T("ya sabes") - 0.1, V(FR, (-1.0, -1.7, 0.45), 30))
    add(T("la leche de tu") - 0.3, ini)
    add(DUR + 1, ini)
    return k.k

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v)
    cp = carton_pos(t)
    return {"carton": Pj(cp + Vector((0, 0, 0.18))), "carton_lado": Pj(cp + Vector((-0.12, 0, 0.0))),
            "t1": Pj(Vector((-0.17, FY + 0.12, BALDAS[2] + 0.25))), "t2": Pj(D(t, (-0.12, 0.075, BALC[2] + 0.25))),
            "suelo": Pj(Vector((-0.1, -0.4, 0.15))), "techo": Pj(Vector((-0.05, -0.45, 1.75))),
            "grid": Pj(G0 + Vector((0, 0.1, 0.35))), "fila": Pj(Vector((FILA[0], FILA[1], 0.3))),
            "regla": Pj(Vector((-0.27, (YB + 0.04) / 2, 1.18))), "medio": Pj(Vector((-0.12, YB - 0.1, BALDAS[1] + 0.3))),
            "puerta": Pj(D(t, (-0.3, 0.1, 1.0))), "tirador": Pj(D(t, (-FW + 0.045, -0.1, 1.05))),
            "botes": Pj(D(t, (-0.3, 0.1, BALC[0] + 0.2)))}

if __name__ == "__main__":
    run("nevera", build, pose, anchors)
