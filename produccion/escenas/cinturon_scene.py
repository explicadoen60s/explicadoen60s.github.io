# «Tu cinturón… ¿cuánto pesas en un choque?» (formato A, error común)
# Coche de maqueta (1 unidad = 1 m) sobre una isla de carretera, con el lado del conductor cortado (cantos crema) para ver
# el asiento, la persona y el pilar B. Abajo del pilar, el carrete del cinturón en corte (el doble de grande que uno real
# para que se lea): carrete con la correa enrollada, rueda dentada delante, diente (trinquete), péndulo con su bolita colgada
# sobre el gancho, tubo del pretensor con su carga y barra de torsión (limitador) en el eje del carrete.
# El coche frena (la bolita se inclina), choca contra un muro a 50 km/h (el cuerpo va hacia delante, flecha roja) y luego
# se ven los errores: correa floja, torcida, bajo el brazo y sobre un abrigo gordo; al final, la banda bien puesta.
# Planos (fotografía → motion; esquina libre arriba-izquierda, que ocupa el mini del juego desde 4,1 s):
#  0,0 mano tirando de la correa en primer plano del carrete · 2,9 coche entero · 4,7 carrete: sale despacio · 7,4 de golpe: se clava
#  9,5 péndulo · 11,1 bolita y gancho · 13,2 coche frenando · 14,6 bolita inclinada · 16 0,45 g · 20 diente en la rueda
#  23,9 golpe serio · 27,1 pretensor · 28,6 la carga dispara · 32,5 coche hacia el muro · 34,6 choque · 35,3 3.000 kg
#  38,1 costillas · 40,8 limitador (barra de torsión) · 44,4 errores · 48,5 holgura · 52,1 banda bien puesta · 55,6 cierre
#  62,6 vuelta al primer plano del carrete.
import bpy, math, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from modelos import *
from maqueta import *
from marcas import cargar
from mathutils import Vector, Quaternion

T, DUR = cargar("cinturon")
CARRO = (0.92, 0.24, 0.20); TAPIZ = (0.25, 0.28, 0.35); CORREA = (0.18, 0.19, 0.22); ACERO = (0.74, 0.76, 0.80)
PIEL = (0.96, 0.78, 0.64); ROPA = (0.30, 0.55, 0.85); ABRIGO = (0.95, 0.60, 0.25); NARANJA = (1.0, 0.55, 0.15)
R0 = Vector((-0.32, -0.36, 0.50))           # centro del carrete (local del coche); eje del carrete a lo largo de Y
DRING = Vector((-0.30, -0.36, 1.16)); HIP = Vector((-0.08, 0.0, 0.50))
XMURO = 2.6

def back(x):
    x = max(0.0, min(1.0, x)); c = 1.70158; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

# ---------------- movimiento ----------------
def coche_x(t):
    """posición del coche: frena en 13-15 s; choca en el muro (frente en XMURO) hacia 34,6 s"""
    a = T("cuando el coche"); b = T("se inclina", fin=True)
    if a - 1.0 < t < b + 1.0:
        u = (t - (a - 1.0)) / (b + 2.0 - a)
        return -3.0 + 3.0 * (1 - (1 - min(u, 1)) ** 2.2)
    c0 = T("y aquí viene"); c1 = T("a cincuenta", fin=True) + 0.15
    if c0 - 0.2 < t < c1: return mix(-7.0, XMURO - 1.7, (t - c0 + 0.2) / (c1 - c0 + 0.2))
    if c1 <= t < T("y tú la llevas"): return XMURO - 1.7
    return 0.0 if not (c0 - 0.2 < t < T("y tú la llevas")) else XMURO - 1.7

def choque(t):
    return T("a cincuenta", fin=True) + 0.15

def frenada(t):
    """inclinación del péndulo (0..1)"""
    a = T("cuando el coche"); b = T("así que un")
    f1 = win01(t, a + 0.3, T("así que un diente") + 0.5, 0.4, 0.5)
    f2 = win01(t, choque(t) - 0.05, choque(t) + 2.5, 0.1, 0.6)
    f3 = win01(t, T("si tiras") + 0.1, T("dentro hay") + 0.3, 0.2, 0.3) * 0.7
    return max(f1, f2, f3)

def cerrado(t):
    """el diente está metido en la rueda (0..1)"""
    return max(win01(t, T("se clava") - 0.15, T("dentro hay") + 0.3, 0.12, 0.3),
               win01(t, T("encaja") - 0.1, T("pero si el golpe") + 0.3, 0.15, 0.3),
               win01(t, choque(t) - 0.05, T("y tú la llevas"), 0.1, 0.3),
               win01(t, T("así que ya sabes") + 0.2, T("el carrete de tu") + 0.8, 0.12, 0.3))

def tirar(t):
    """cuánto sale la correa por la mano (m) en el primer plano"""
    if t < T("dentro hay"): return keyed(t, [(0, 0.0), (T("tira despacio"), 0.02), (T("la correa sale", fin=True), 0.09),
                                              (T("si tiras"), 0.09), (T("se clava") - 0.15, 0.13)])
    if t > T("así que ya sabes") - 0.3:
        return keyed(t, [(T("así que ya sabes") - 0.3, 0.0), (T("se clava", 2) - 0.15, 0.05)])
    return 0.0

def giro(t):
    """ángulo del carrete (rad): sale correa (+), recoge (-) con el pretensor, cede con el limitador"""
    g = tirar(t) / 0.06 + 0.4 * math.sin(t * 0.4) * (t < 1.5)
    g -= 2.5 * seg(t, T("tira de ella") - 0.05, T("tira de ella") + 0.15) * (t < T("y tú la llevas"))
    g += 1.6 * seg(t, T("cede"), T("de correa", fin=True)) * (t < T("y tú la llevas"))
    return g

def lean(t):
    """el cuerpo va hacia delante en el choque (rad): con limitador cede unos cm más; con holgura recorre más"""
    c = choque(t); l = 0.0
    if c - 0.05 < t < T("y tú la llevas"):
        l = 0.22 * seg(t, c, c + 0.35) + 0.08 * seg(t, T("cede"), T("de correa", fin=True))
        l -= 0.25 * seg(t, T("pero tanta") + 0.2, T("así que el limitador")) * 0.0
    h = win01(t, T("esa holgura"), T("quítate"), 0.4, 0.4)
    return max(l, 0.42 * h * seg(t, T("esa holgura") + 0.3, T("que recorres", fin=True)))

# ---------------- construcción ----------------
def build():
    sc, cam = scene_setup(world=PAL["cielo"], shadow=0.25, light_rot=40); entorno_claro(sc)
    S = {"cam": cam}
    nubes(9, (0, 9, 4.5), 9, 1.2, 1.0, s=1.3, seed=5)
    # isla de carretera (a lo largo de X) con muro de pruebas
    isla(14.0, 4.0, (-1.0, 0.6, 0.0), capas=[(PAL["asfalto"], 0.08), (PAL["hormigon"], 0.2), (PAL["tierra"], 0.5), (PAL["tierra2"], 0.5)])
    for i in range(12): caja((0.5, 0.08, 0.01), (-7.5 + i * 1.2, 0.6, 0.005), (1, 1, 1), r=0.003)
    caja((14.0, 0.6, 0.06), (-1.0, 2.3, 0.03), (0.84, 0.83, 0.80), r=0.02)
    for k in range(4): arbol((-6.5 + 3.2 * k, 2.4, 0.06), 0.55, seed=k)
    S["muro"] = empty((XMURO + 0.25, 0.4, 0))
    caja((0.5, 2.6, 1.3), (0, 0, 0.65), (0.82, 0.82, 0.80), S["muro"], r=0.04)
    for k in range(6): caja((0.52, 0.22, 1.32), (0, -1.1 + k * 0.44, 0.65), PAL["amarillo"] if k % 2 else (0.15, 0.15, 0.17), S["muro"], r=0.01)
    # coche (lado del conductor abierto y cortado)
    S["car"] = car = empty((0, 0, 0))
    caja((2.6, 1.55, 0.1), (0.15, 0.35, 0.3), CARRO, car, r=0.03)                       # suelo
    caja((2.6, 0.06, 0.55), (0.15, 1.1, 0.6), CARRO, car, r=0.03)                       # puerta del otro lado
    caja((0.9, 0.04, 0.32), (0.25, 1.06, 1.0), (0.62, 0.80, 0.93), car, r=0.02)         # ventanilla
    caja((0.8, 1.55, 0.45), (1.05, 0.35, 0.55), CARRO, car, r=0.06)                     # capó
    caja((0.5, 1.55, 0.45), (-1.0, 0.35, 0.55), CARRO, car, r=0.06)                     # maletero
    caja((0.35, 1.45, 0.25), (0.6, 0.35, 0.82), (0.22, 0.23, 0.27), car, r=0.05)        # salpicadero
    w = caja((0.05, 1.45, 0.6), (0.82, 0.35, 1.05), (0.62, 0.80, 0.93), car, r=0.02); w.rotation_euler = (0, -0.75, 0)   # parabrisas
    caja((1.25, 1.55, 0.05), (-0.05, 0.35, 1.34), CARRO, car, r=0.02)                   # techo
    caja((0.08, 0.07, 0.72), (-0.34, -0.40, 0.98), CARRO, car, r=0.02)                  # pilar B (acaba encima del carrete)
    caja((0.085, 0.072, 0.03), (-0.34, -0.40, 0.63), PAL["corte"], car, r=0.005)
    caja((2.6, 0.03, 0.03), (0.15, -0.44, 0.36), PAL["corte"], car, r=0.005)            # cantos del corte
    caja((1.25, 0.03, 0.03), (-0.05, -0.44, 1.32), PAL["corte"], car, r=0.005)
    for x in (-0.75, 1.05):
        for y in (-0.42, 1.12):
            cilindro(0.26, 0.18, (x, y, 0.26), (0.17, 0.17, 0.19), car, rot=(math.pi / 2, 0, 0), r=0.05)
            cilindro(0.12, 0.19, (x, y, 0.26), (0.82, 0.83, 0.85), car, rot=(math.pi / 2, 0, 0), r=0.02)
    # asiento
    caja((0.5, 0.5, 0.14), (-0.02, 0.0, 0.42), TAPIZ, car, r=0.05)
    sb = caja((0.14, 0.5, 0.7), (-0.25, 0.0, 0.8), TAPIZ, car, r=0.05); sb.rotation_euler = (0, -0.15, 0)
    caja((0.12, 0.28, 0.18), (-0.31, 0.0, 1.22), TAPIZ, car, r=0.05)
    caja((0.06, 0.06, 0.12), (0.0, 0.26, 0.55), (0.55, 0.57, 0.6), car, r=0.01)          # anclaje de la hebilla
    # volante
    S["volante"] = torus(0.17, 0.022, (0.45, 0.0, 0.92), (0.15, 0.15, 0.17), car, rot=(0, math.radians(65), 0))
    # persona sentada: piernas fijas, cuerpo que se inclina (pivote en la cadera)
    caja((0.42, 0.26, 0.13), (0.12, 0.0, 0.55), (0.22, 0.25, 0.35), car, r=0.05)       # muslos
    caja((0.12, 0.24, 0.4), (0.38, 0.0, 0.32), (0.22, 0.25, 0.35), car, r=0.05)         # piernas
    S["cuerpo"] = cu = empty(HIP, car); cu.rotation_mode = 'XYZ'
    caja((0.2, 0.34, 0.5), (0.0, 0.0, 0.27), ROPA, cu, r=0.07)
    bola(0.1, (0.02, 0.0, 0.66), PIEL, cu); bola(0.105, (0.0, 0.0, 0.69), (0.30, 0.20, 0.14), cu, escala=(1, 1, 0.7))
    for y in (-0.19, 0.19):
        a = cilindro(0.04, 0.42, (0.2, y, 0.38), ROPA, cu, r=0.015); a.rotation_euler = (0, math.radians(70), 0)
    S["abrigo"] = caja((0.3, 0.46, 0.5), (0.0, 0.0, 0.29), ABRIGO, cu, r=0.12, unique=True)
    # carrete del cinturón (en corte, el doble de grande), anclado al pilar B
    S["ret"] = ret = empty(R0, car)
    caja((0.16, 0.012, 0.2), (0, 0.045, -0.01), ACERO, ret, r=0.004)                  # chapa del fondo (la de delante está cortada)
    caja((0.16, 0.09, 0.012), (0, 0.0, -0.11), ACERO, ret, r=0.004)                   # base
    caja((0.012, 0.09, 0.03), (-0.08, 0.0, -0.095), PAL["corte"], ret)                 # cantos crema de la chapa cortada
    caja((0.16, 0.004, 0.012), (0, -0.045, -0.11), PAL["corte"], ret)
    S["spool"] = sp = empty((0, 0, 0), ret); sp.rotation_mode = 'XYZ'
    cilindro(0.03, 0.08, (0, 0, 0), (0.8, 0.8, 0.82), sp, rot=(math.pi / 2, 0, 0), r=0.006)
    S["rollo"] = cilindro(0.058, 0.07, (0, 0, 0), CORREA, sp, rot=(math.pi / 2, 0, 0), r=0.01, unique=True)
    for k in range(3): caja((0.004, 0.072, 0.115), (0.0, 0.0, 0.0), (0.12, 0.13, 0.15), sp, rot=(0, k * math.pi / 3, 0))
    S["rueda"] = ru = empty((0, -0.045, 0), ret); ru.rotation_mode = 'XYZ'
    cilindro(0.065, 0.012, (0, 0, 0), (0.95, 0.80, 0.30), ru, rot=(math.pi / 2, 0, 0), r=0.003)
    for k in range(12):
        a = k * math.tau / 12
        caja((0.02, 0.012, 0.014), (0.072 * math.cos(a), 0, 0.072 * math.sin(a)), (0.95, 0.80, 0.30), ru, rot=(0, -a, 0))
    S["barra"] = br = empty((0, -0.052, 0), ret); br.rotation_mode = 'XYZ'                # barra de torsión (raya que gira)
    cilindro(0.012, 0.012, (0, 0, 0), PAL["amarillo"], br, rot=(math.pi / 2, 0, 0))
    caja((0.022, 0.004, 0.004), (0, -0.007, 0), PAL["rojo"], br)
    S["diente"] = di = empty((0.09, -0.05, -0.035), ret); di.rotation_mode = 'XYZ'      # trinquete con pivote
    cilindro(0.008, 0.016, (0, 0, 0), (0.3, 0.3, 0.33), di, rot=(math.pi / 2, 0, 0))
    caja((0.045, 0.01, 0.014), (-0.02, 0, 0.01), (0.55, 0.57, 0.62), di, r=0.003, rot=(0, -0.5, 0))
    caja((0.02, 0.012, 0.012), (-0.042, 0, 0.022), PAL["rojo"], di, r=0.003)
    S["pend"] = pe = empty((0.085, -0.05, -0.06), ret); pe.rotation_mode = 'XYZ'       # péndulo: gancho arriba, bolita abajo
    caja((0.006, 0.006, 0.05), (0, 0, -0.025), (0.3, 0.3, 0.33), pe)
    S["bola"] = bola(0.014, (0, 0, -0.055), (0.9, 0.92, 0.95), pe)
    caja((0.03, 0.006, 0.006), (-0.01, 0, 0.005), (0.3, 0.3, 0.33), pe)
    caja((0.05, 0.03, 0.006), (0.085, -0.05, -0.115), ACERO, ret)                        # cazoleta
    # pretensor: tubo con carga y gas
    S["pret"] = empty((-0.05, -0.02, -0.06), ret)
    cilindro(0.016, 0.14, (-0.06, 0, -0.02), (0.55, 0.57, 0.62), S["pret"], r=0.004, rot=(0, math.pi / 2, 0))
    S["carga"] = cilindro(0.014, 0.03, (-0.12, 0, -0.02), PAL["rojo"], S["pret"], rot=(0, math.pi / 2, 0), unique=True)
    S["gas"] = bola(0.03, LEJOS, NARANJA)
    S["gas2"] = bola(0.05, LEJOS, PAL["amarillo"])
    # correa (tramos que se recolocan cada fotograma)
    S["tramos"] = [box((1, 1, 1), LEJOS, CORREA, unique=True) for _ in range(5)]
    caja((0.06, 0.03, 0.04), (DRING.x, DRING.y + 0.02, DRING.z), ACERO, car, r=0.008)    # anilla del hombro
    S["hebilla"] = caja((0.05, 0.03, 0.07), (0.0, 0.26, 0.6), (0.75, 0.77, 0.80), car, r=0.01)
    # mano que tira de la correa
    S["mano"] = empty(LEJOS)
    caja((0.06, 0.1, 0.08), (0, 0, 0), PIEL, S["mano"], r=0.025)
    cilindro(0.03, 0.22, (0, 0, 0.14), ROPA, S["mano"], r=0.01)
    # flechas
    S["fuerza"] = flecha3d(LEJOS, (1, 0, 0), 0.6, 0.04)
    S["fpecho"] = flecha3d(LEJOS, (-1, 0, 0), 0.3, 0.025)
    S["fhueco"] = flecha3d(LEJOS, (1, 0, 0), 0.25, 0.02, color=PAL["amarillo"])
    S["fgrav"] = flecha3d(LEJOS, (1, 0, 0), 0.08, 0.006)
    dyn = [cam, S["muro"], car, S["gas"], S["gas2"], S["tramos"], S["mano"], S["fuerza"], S["fpecho"], S["fhueco"], S["fgrav"]]
    join_static(dyn)
    return sc, S

def strap(o, a, b, w=0.05, th=0.006, twist=0.0):
    d = b - a; L = max(d.length, 0.001)
    o.rotation_mode = 'QUATERNION'
    o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d) @ Quaternion((0, 0, 1), twist)
    o.location = (a + b) / 2; o.scale = (w, th, L)

def W(S, p):
    """punto local del coche → mundo"""
    return S["car"].matrix_world @ Vector(p)

def pose(t, S):
    S["car"].location = (coche_x(t), 0, 0)
    bpy.context.view_layer.update()
    l = lean(t); S["cuerpo"].rotation_euler = (0, l, 0)
    S["volante"].rotation_euler = (0, math.radians(65), 0)
    # piezas del carrete
    g = giro(t)
    S["spool"].rotation_euler = (0, g, 0); S["rueda"].rotation_euler = (0, g if cerrado(t) < 0.5 else g, 0)
    tor = seg(t, T("cede"), T("de correa", fin=True)) * (t < T("y tú la llevas"))
    S["barra"].rotation_euler = (0, g + 1.4 * tor, 0)
    S["diente"].rotation_euler = (0, -0.55 * cerrado(t), 0)
    S["pend"].rotation_euler = (0, -0.6 * frenada(t), 0)
    rr = 1.0 - 0.25 * min(1.0, tirar(t) / 0.13); S["rollo"].scale = (rr, rr, 1)
    # pretensor: la carga dispara y empuja gas
    ex = win01(t, T("tira de ella") - 0.1, T("en treinta") + 0.5, 0.05, 0.5)
    if ex > 0.01:
        p = W(S, R0 + Vector((-0.2, -0.04, -0.08)))
        S["gas"].location = p; S["gas"].scale = (0.6 + 1.2 * ex,) * 3
        S["gas2"].location = p + Vector((0, -0.01, 0.0)); S["gas2"].scale = (0.3 + 0.6 * ex * (0.8 + 0.2 * math.sin(t * 40)),) * 3
    else: S["gas"].location = LEJOS; S["gas2"].location = LEJOS
    set_color(S["carga"], tuple(mix(a, b, seg(t, T("tira de ella") - 0.1, T("tira de ella") + 0.2) * (t < T("y tú la llevas"))) for a, b in zip(PAL["rojo"], (0.2, 0.2, 0.2))))
    # abrigo (error) y correa
    ab = win01(t, T("sobre un abrigo") - 0.1, T("quítate") + 0.5, 0.25, 0.4)
    S["abrigo"].scale = (max(ab, 0.001),) * 3; S["abrigo"].hide_render = ab < 0.01
    cuerpo = S["cuerpo"].matrix_world
    floja = win01(t, T("la llevas floja") - 0.1, T("torcida"), 0.2, 0.2) + win01(t, T("esa holgura"), T("quítate"), 0.3, 0.3)
    torc = win01(t, T("torcida") - 0.05, T("bajo el brazo") - 0.05, 0.15, 0.15)
    brazo = win01(t, T("bajo el brazo") - 0.05, T("sobre un abrigo") - 0.05, 0.15, 0.15)
    hombro_l = Vector((0.02 + 0.06 * ab, -0.13, 0.48));
    if brazo > 0.01: hombro_l = hombro_l.lerp(Vector((0.05, -0.17, 0.22)), brazo)
    pecho_l = Vector((0.11 + 0.08 * ab + 0.1 * floja, 0.0, 0.3)); cad_l = Vector((0.08 + 0.05 * ab, 0.16, 0.08))
    sh = cuerpo @ hombro_l; pe = cuerpo @ pecho_l; ca = cuerpo @ cad_l
    top = W(S, R0 + Vector((-0.03, 0.0, 0.06)))
    dr = W(S, DRING)
    hb = W(S, (0.0, 0.25, 0.62)); lapi = W(S, (-0.15, -0.28, 0.48))
    mano_on = t < T("dentro hay") + 0.2 or t > T("así que ya sabes") - 0.3
    if mano_on:
        # primer plano: la mano tira de la correa hacia arriba desde el carrete
        top2 = W(S, R0 + Vector((0.0, -0.075, 0.07)))
        tip = top2 + Vector((0.03, -0.09, 0.1 + tirar(t) * 1.6 + 0.01 * math.sin(t * 3)))
        strap(S["tramos"][0], top2, tip, w=0.05)
        for o in S["tramos"][1:]: o.location = LEJOS
        S["mano"].location = tip + Vector((0, -0.02, 0.02)); S["mano"].rotation_euler = (0, 0, 0)
    else:
        S["mano"].location = LEJOS
        tw = math.pi * torc
        strap(S["tramos"][0], top, dr, w=0.05)
        strap(S["tramos"][1], dr, sh, w=0.05, twist=tw * 0.5)
        strap(S["tramos"][2], sh, pe, w=0.05, twist=tw)
        strap(S["tramos"][3], pe, ca.lerp(hb, 0.4), w=0.05, twist=tw)
        strap(S["tramos"][4], lapi, hb, w=0.05)
    # flechas: frenada (pendulo), fuerza del choque, presión en el pecho, holgura
    fg = win01(t, T("pero solo") - 0.1, T("así que un diente"), 0.3, 0.3)
    S["fgrav"].location = W(S, R0 + Vector((0.09, -0.07, -0.14))) if fg > 0.01 else LEJOS; S["fgrav"].scale = (fg + 0.01,) * 3
    fz = win01(t, choque(t) - 0.05, T("así que el limitador") + 0.3, 0.15, 0.3)
    if fz > 0.01:
        u = seg(t, T("tu cuerpo"), T("kilos", fin=True))
        S["fuerza"].location = cuerpo @ Vector((0.15, 0.0, 0.3)); S["fuerza"].scale = (fz * (0.4 + 1.1 * u),) * 3
    else: S["fuerza"].location = LEJOS
    fp = win01(t, T("pero tanta"), T("así que el limitador") + 0.2, 0.2, 0.3)
    S["fpecho"].location = pe + Vector((0.32, 0, 0.02)) if fp > 0.01 else LEJOS; S["fpecho"].scale = (fp + 0.01,) * 3
    fh = win01(t, T("esa holgura") + 0.2, T("quítate"), 0.3, 0.3)
    S["fhueco"].location = pe + Vector((-0.16, 0, 0.0)) if fh > 0.01 else LEJOS; S["fhueco"].scale = (fh + 0.01,) * 3
    apply_cam(S["cam"], *cam_coche(t, S))

def cam_coche(t, S):
    pos, tgt, lens = cam_lin(t, CAM(), drift=0.004)
    off = Vector((coche_x(t), 0, 0))
    return pos + off, Vector(tgt) + off, lens

RET = tuple(R0); RETF = tuple(R0 + Vector((0.08, -0.05, -0.06)))
TODO = (0.2, 0.35, 0.7); PERSONA = (0.0, 0.0, 0.85); PECHO = (0.0, -0.05, 0.85)

def CAM():
    k = Claves(); add = k.add
    ini = V((R0.x, R0.y, R0.z + 0.12), (0.174, -0.797, 0.087), 40)
    add(0.0, V((R0.x, R0.y, R0.z + 0.1), (0.145, -0.652, 0.072), 42)); add(1.6, ini)
    add(T("escribe") - 0.1, V(TODO, (-1.8, -4.0, 1.2), 30))
    add(T("tira despacio") - 0.1, V(RET, (0.217, -0.725, 0.261), 38))
    add(T("si tiras") - 0.1, V(RET, (-0.145, -0.609, 0.087), 42))
    add(T("dentro hay") - 0.1, V(RETF, (0.072, -0.435, 0.029), 48))
    add(T("una bolita"), V(RETF, (0.145, -0.348, -0.029), 52))
    add(T("cuando el coche") - 0.1, V(TODO, (0.3, -4.2, 1.0), 30))
    add(T("la bolita se"), V(RETF, (0.087, -0.377, 0.000), 50))
    add(T("pero solo"), V(RETF, (-0.116, -0.406, 0.043), 50))
    add(T("así que un diente"), V(RET, (0.174, -0.464, 0.072), 46))
    add(T("y la correa"), V(RET, (0.000, -0.652, 0.362), 40))
    add(T("pero si el golpe"), V(PERSONA, (-0.6, -2.4, 0.6), 32))
    add(T("así que salta"), V(RET, (-0.290, -0.652, 0.116), 42))
    add(T("una carga"), V(RET, (-0.174, -0.464, 0.000), 46))
    add(T("en treinta"), V(PERSONA, (0.2, -1.9, 0.3), 34))
    add(T("y aquí viene") - 0.1, V(TODO, (-1.5, -5.0, 1.4), 28))
    add(T("a cincuenta"), V((0.9, 0.35, 0.6), (-2.0, -4.4, 1.0), 28))
    add(T("tu cuerpo") - 0.1, V(PECHO, (0.4, -1.8, 0.35), 32))
    add(T("pero tanta"), V(PECHO, (0.15, -1.2, 0.15), 36))
    add(T("así que el limitador"), V(RET, (0.116, -0.522, 0.072), 46))
    add(T("cede") + 0.2, V(RET, (-0.087, -0.435, 0.029), 50))
    add(T("y tú la llevas") - 0.1, V(PECHO, (0.3, -1.6, 0.3), 32))
    add(T("bajo el brazo"), V(PECHO, (0.6, -1.3, 0.1), 32))
    add(T("sobre un abrigo"), V(PECHO, (0.4, -1.4, 0.25), 32))
    add(T("esa holgura"), V(PECHO, (0.0, -1.2, 0.1), 34))
    add(T("que recorres"), V(PECHO, (-0.2, -1.3, 0.25), 34))
    add(T("quítate"), V(PECHO, (0.5, -1.5, 0.3), 32))
    add(T("sobre el hombro"), V(PECHO, (0.2, -1.1, 0.12), 36))
    add(T("te has acercado"), V(TODO, (-1.8, -4.0, 1.2), 30))
    add(T("y si quieres"), V(PERSONA, (0.6, -2.4, 0.6), 32))
    add(T("lo más pedido"), V(TODO, (1.8, -4.0, 1.0), 30))
    add(T("sígueme"), V(RET, (0.290, -0.870, 0.290), 38))
    add(T("así que ya sabes") - 0.2, V((R0.x, R0.y, R0.z + 0.1), (0.145, -0.652, 0.072), 42))
    add(DUR - 0.8, ini)
    add(DUR + 1, ini)
    return k.k

def anchors(sc, S, t):
    cam = S["cam"]; P = lambda v: proj(sc, cam, v)
    cu = S["cuerpo"].matrix_world
    return {"ret": P(W(S, R0 + Vector((0, 0, 0.12)))), "pend": P(W(S, R0 + Vector((0.085, -0.05, -0.12)))),
            "diente": P(W(S, R0 + Vector((0.07, -0.05, -0.02)))), "pret": P(W(S, R0 + Vector((-0.17, -0.03, -0.08)))),
            "pecho": P(cu @ Vector((0.12, 0.0, 0.35))), "cabeza": P(cu @ Vector((0.0, 0.0, 0.85))), "coche": P(W(S, (0.2, 0.35, 1.5))),
            "hombro": P(cu @ Vector((0.02, -0.13, 0.48))), "cadera": P(cu @ Vector((0.08, 0.16, 0.08))),
            "muro": P((XMURO + 0.25, 0.4, 1.5)), "barra": P(W(S, R0 + Vector((0, -0.06, 0.0))))}

if __name__ == "__main__":
    run("cinturon", build, pose, anchors)
