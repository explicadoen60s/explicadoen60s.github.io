# «El ticket del súper no lleva tinta»: caja de supermercado de maqueta sobre una isla de suelo. La impresora escupe el
# ticket y las líneas salen negras una a una. Se abre la impresora (rollo, rodillo y cabezal) y, en otra isla, un corte
# gigante del papel: capa térmica con dos polvos (tinte sin color y ácido). Baja el cabezal, un punto pasa de 100 °C,
# la capa se derrite, tinte y ácido se tocan y el punto se vuelve negro. El papel avanza (1.000 líneas/s), el sol y la
# crema deshacen la reacción, la letra se borra y la uña la vuelve a ennegrecer.
# Planos (fotografía → motion): 0 impresora+ticket (libre: arriba) · 2,7 letras · 4,4 caja entera · 5,9 se abre ·
# 7,9 corte del papel · 10 polvos · 12,6 tinte · 14,7 ácido · 19 cabezal baja · 20 fila de puntos · 22,7 8 por mm ·
# 24,7 cabezal en la impresora · 27,4 punto caliente · 29,6 se derrite · 33 negro · 34,6 vista general · 36,3 papel avanza ·
# 41,7 caja · 45,9 marcha atrás · 48 sol · 49,6 crema · 51 se deshace · 53 letra borrada · 57,5 uña · 61,6 vuelta al inicio.
import bpy, math, sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from maqueta import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("ticket")
MX = 3.6                      # centro del corte gigante del papel
SLOT = 1.3                    # cota de la ranura de salida del ticket
PAPER = (0.98, 0.97, 0.94); LETRA = (0.06, 0.06, 0.07); HEAD = (0.3, 0.32, 0.36); DOT = (0.55, 0.56, 0.6)
DYE = (0.95, 0.96, 0.99); ACID = (1.0, 0.86, 0.45); LAYER = (0.8, 0.88, 0.96); HOT = (1.0, 0.3, 0.12); SKIN = (0.95, 0.74, 0.62)
WHITE = (0.95, 0.95, 0.96); GREY = (0.72, 0.74, 0.78)
NROWS = 30
def drow(i): return 0.06 + 0.03 * i

def build():
    sc, cam = scene_setup(world=PAL["cielo"], shadow=0.25); entorno_claro(sc)
    S = {"cam": cam}; rnd = random.Random(7)
    nubes(10, (1.8, 8, 1.8), 8, 1.6, 1.0, s=1.0, seed=5)
    # isla de la caja: suelo de baldosa y capas
    isla(3.4, 2.6, (0, 0.5, 0), capas=[((0.9, 0.9, 0.86), 0.06), (PAL["hormigon"], 0.25), (PAL["tierra"], 0.35), (PAL["tierra2"], 0.3)])
    # mostrador de caja
    box((2.4, 0.8, 0.95), (0, 0.15, 0.475), (0.35, 0.55, 0.85))
    box((2.45, 0.85, 0.05), (0, 0.15, 0.975), PAL["encimera"])
    box((1.25, 0.5, 0.03), (-0.65, 0.15, 1.015), (0.18, 0.19, 0.22))
    for x, c, sz in ((-1.1, (0.95, 0.35, 0.3), (0.12, 0.12, 0.22)), (-0.85, (0.98, 0.98, 1.0), (0.1, 0.1, 0.26)), (-0.6, (0.98, 0.8, 0.3), (0.2, 0.14, 0.1))):
        box(sz, (x, 0.15, 1.03 + sz[2] / 2), c)
    for k in range(3): sph(0.05, (-0.35 + 0.1 * k, 0.12 + 0.05 * (k % 2), 1.08), (0.85, 0.15, 0.15), seg=12)
    box((0.12, 0.18, 0.04), (0.75, 0.0, 1.02), (0.2, 0.2, 0.24)); box((0.08, 0.06, 0.005), (0.75, -0.02, 1.042), (0.4, 0.7, 0.9))
    # estantería del súper al fondo
    box((3.2, 0.45, 2.0), (0, 1.5, 1.0), PAL["madera"])
    for j in range(4):
        box((3.1, 0.4, 0.04), (0, 1.45, 0.25 + 0.48 * j), (0.95, 0.9, 0.8))
        x = -1.45
        while x < 1.4:
            w = rnd.uniform(0.1, 0.22); h = rnd.uniform(0.15, 0.32)
            box((w * 0.9, 0.25, h), (x + w / 2, 1.35, 0.27 + 0.48 * j + h / 2), rnd.choice([PAL["rojo"], PAL["amarillo"], PAL["rosa"], PAL["maceta"], PAL["planta"], (1, 1, 1)]))
            x += w
    # impresora en corte
    box((0.42, 0.03, 0.3), (0, 0.17, 1.15), WHITE); box((0.42, 0.36, 0.02), (0, 0.0, 1.01), WHITE)
    for sx in (-1, 1): box((0.02, 0.36, 0.3), (sx * 0.21, 0.0, 1.15), WHITE)
    S["tapa"] = empty((0, 0, 0))
    box((0.44, 0.38, 0.03), (0, 0.0, 1.315), WHITE, parent=S["tapa"]); box((0.44, 0.03, 0.3), (0, -0.18, 1.15), WHITE, parent=S["tapa"])
    box((0.3, 0.012, 0.02), (0, -0.05, 1.333), (0.15, 0.15, 0.17), parent=S["tapa"])
    box((0.16, 0.005, 0.05), (0.08, -0.198, 1.2), (0.3, 0.6, 0.95), parent=S["tapa"])
    S["rollo"] = cyl(0.09, 0.3, (0, 0.06, 1.11), PAPER, rot=(0, math.pi / 2, 0), unique=True)
    S["rayita"] = box((0.31, 0.01, 0.02), (0, 0, 0), (0.75, 0.75, 0.72), unique=True)
    cyl(0.025, 0.31, (0, 0.06, 1.11), (0.8, 0.65, 0.45), rot=(0, math.pi / 2, 0))
    S["rodillo"] = cyl(0.028, 0.32, (0, -0.085, 1.22), (0.12, 0.12, 0.13), rot=(0, math.pi / 2, 0))
    S["marca"] = box((0.33, 0.012, 0.012), (0, 0, 0), (0.9, 0.3, 0.25), unique=True)
    box((0.32, 0.04, 0.06), (0, -0.01, 1.22), HEAD)
    S["pdots"] = [box((0.025, 0.006, 0.012), (-0.14 + 0.028 * i, -0.031, 1.22), DOT, unique=True) for i in range(11)]
    bp = box((0.3, 0.004, 0.2), (0, -0.05, 1.2), PAPER)          # papel por dentro
    o = bar_obj(PAPER, 0.004); bar_set(o, (0, 0.06 - 0.09, 1.11), (0, -0.05, 1.1))
    # ticket que sale y sus líneas impresas
    S["tk"] = box((0.3, 0.003, 1.0), (0, -0.05, SLOT), PAPER)
    S["rows"] = []
    for i in range(NROWS):
        e = empty(LEJOS); x = -0.13
        if i in (3, 4): parts = [(0.26, 0.016)]
        else:
            parts = []
            while x < 0.1:
                w = rnd.uniform(0.02, 0.07); parts.append((w, 0.011)); x += w + 0.012
        x = -0.13
        for w, h in parts:
            b = box((w, 0.002, h), (x + w / 2, 0, 0), LETRA, parent=e); x += w + 0.012
        if i % 4 == 1: box((0.05, 0.002, 0.011), (0.105, 0, 0), LETRA, parent=e)
        S["rows"].append(e)
    S["raya"] = box((1.0, 0.003, 0.012), LEJOS, LETRA, unique=True)       # la uña
    S["dedo"] = empty(LEJOS)
    cyl(0.03, 0.16, (0.08, 0, 0), SKIN, parent=S["dedo"], rot=(0, math.pi / 2, 0)); sph(0.03, (0, 0, 0), SKIN, parent=S["dedo"])
    box((0.012, 0.03, 0.028), (-0.022, 0, 0), (0.98, 0.88, 0.85), parent=S["dedo"])
    # sol y crema
    S["sol"] = sph(0.22, LEJOS, PAL["amarillo"], seg=16)
    S["rayos"] = [bar_obj((1.0, 0.9, 0.35), 0.012) for _ in range(6)]
    S["crema"] = empty(LEJOS)
    cyl(0.04, 0.2, (0, 0, 0), (0.97, 0.6, 0.7), parent=S["crema"], rot=(0, math.pi / 2, 0)); cyl(0.025, 0.04, (-0.12, 0, 0), WHITE, parent=S["crema"], rot=(0, math.pi / 2, 0))
    S["gota"] = sph(0.035, LEJOS, (1, 1, 1), seg=12)
    # isla del corte gigante del papel
    isla(2.6, 1.4, (MX, 0.2, 0.6), capas=[(PAL["cesped"], 0.1), (PAL["tierra"], 0.3), (PAL["tierra2"], 0.3)])
    box((2.0, 0.8, 0.35), (MX, 0, 0.775), PAPER)
    box((2.0, 0.8, 0.3), (MX, 0, 1.1), LAYER)
    box((2.0, 0.8, 0.03), (MX, 0, 1.265), (0.95, 0.97, 1.0))
    S["mancha"] = box((0.16, 0.6, 0.006), LEJOS, LETRA)
    S["parts"] = []
    for j, zr in enumerate((1.02, 1.1, 1.18)):
        for i in range(28):
            x = MX - 0.96 + 1.92 * (i + 0.5 + 0.5 * (j % 2)) / 28.5; z = zr + rnd.uniform(-0.012, 0.012)
            tipo = "t" if (i + j) % 2 == 0 else "a"
            s = sph(0.045 if tipo == "t" else 0.036, (x, -0.4, z), DYE if tipo == "t" else ACID, seg=12, unique=True)
            S["parts"].append((s, Vector((x, -0.4, z)), tipo))
    S["hm"] = empty((0, 0, 0))
    box((2.0, 0.5, 0.18), (MX, -0.1, 1.3), HEAD, parent=S["hm"])
    S["hdots"] = [box((0.12, 0.3, 0.03), (MX - 0.8 + 0.2 * i, -0.2, 1.2), DOT, parent=S["hm"], unique=True) for i in range(9)]
    S["calor"] = [flecha3d(LEJOS, (0, 0, -1), 0.12, 0.012) for _ in range(2)]
    S["avance"] = flecha3d(LEJOS, (0, 0, 1), 0.22, 0.018)
    S["roce"] = flecha3d(LEJOS, (1, 0, 0), 0.14, 0.012)
    dyn = [cam, S["tapa"], S["rollo"], S["rayita"], S["rodillo"], S["marca"], S["pdots"], S["tk"], S["rows"], S["raya"], S["dedo"], S["sol"],
           S["rayos"], S["crema"], S["gota"], S["mancha"], [p[0] for p in S["parts"]], S["hm"], S["calor"], S["avance"], S["roce"]]
    join_static(dyn)
    return sc, S

# ---------------- estado ----------------
def largo_tk(t):
    """longitud del ticket fuera de la impresora"""
    if t < T("el cabezal no"): return mix(0.22, 0.8, seg(t, -0.3, 2.4))
    return mix(0.04, 0.94, seg(t, T("es el papel") - 0.1, T("no hace ruido", fin=True)))

def borrado(t):
    return 0.55 * seg(t, T("el tinte vuelve"), T("desaparece", fin=True)) + 0.37 * seg(t, T("por eso tu"), T("en blanco", fin=True))

def derretido(t):
    return seg(t, T("la capa se derrite"), T("se tocan", fin=True)) * (1 - seg(t, T("el tinte vuelve"), T("forma sin color", fin=True)))

def negro(t):
    return seg(t, T("y el punto"), T("negro", fin=True)) * (1 - seg(t, T("el tinte vuelve"), T("desaparece", fin=True)))

def pose(t, S):
    L = largo_tk(t)
    S["tk"].scale = (0.3, 0.003, L); S["tk"].location = (0, -0.05, SLOT + L / 2)
    imprime = t < 2.5 or (T("es el papel") - 0.1 < t < T("no hace ruido", fin=True))
    for i, e in enumerate(S["rows"]):
        d = drow(i)
        e.location = (0, -0.0535, SLOT + L - d) if L > d + 0.006 else LEJOS
    bl = borrado(t)
    S["rows"][0].children[0].active_material.diffuse_color = (*lin(tuple(mix(a, b, bl) for a, b in zip(LETRA, PAPER))), 1)
    # tapa de la impresora que se levanta
    u = seg(t, T("vamos a abrir"), T("la impresora", fin=True))
    S["tapa"].location = (0.0, -0.9 * u, 0.9 * u); S["tapa"].rotation_euler.x = -0.6 * u
    for c in S["tapa"].children: c.hide_render = u > 0.98
    # rollo y rodillo girando cuando el papel avanza
    ang = (t * 25 if imprime else 0) + (2.4 * 25 if t > 2.5 else 0)
    p = Vector((0, 0.06, 1.11)) + Vector((0, -0.092 * math.cos(ang * 0.3), 0.092 * math.sin(ang * 0.3)))
    S["rayita"].location = p; S["rayita"].rotation_euler.x = -ang * 0.3
    S["marca"].location = Vector((0, -0.085, 1.22)) + Vector((0, -0.03 * math.cos(ang), 0.03 * math.sin(ang)))
    for i, d in enumerate(S["pdots"]):
        on = imprime or (T("más de quinientos") - 0.2 < t < T("en todo el") + 1.2)
        set_color(d, HOT if on and math.sin(t * 40 + i * 2.1) > 0.2 else DOT)
    # cabezal gigante que baja sobre el papel
    S["hm"].location.z = mix(0.85, 0.095, seg(t, T("el cabezal") - 0.2, T("el cabezal", fin=True) + 0.4))
    fila = T("es una fila"); caliente = seg(t, T("cuando un punto"), T("cien grados", fin=True))
    for i, d in enumerate(S["hdots"]):
        c = DOT
        if fila < t < T("hay ocho") and int((t - fila) * 8) % 9 == i: c = HOT
        if T("hay ocho") < t < T("más de quinientos"): c = (1.0, 0.75, 0.3) if (int(t * 6) + i) % 3 == 0 else DOT
        if i == 4 and caliente > 0 and t < T("el tinte vuelve"):
            c = tuple(mix(a, b, caliente) for a, b in zip(DOT, HOT)) if t < T("pero esa") else tuple(mix(a, b, 1 - seg(t, T("pero esa"), T("pero esa") + 0.6)) for a, b in zip(DOT, HOT))
        set_color(d, c)
    for k, f in enumerate(S["calor"]):
        if T("cuando un punto") + 0.4 < t < T("se tocan", fin=True):
            f.location = (MX - 0.04 + 0.08 * k, -0.42, 1.42 - 0.03 * ((t * 2.5 + k * 0.5) % 1.0))
        else: f.location = LEJOS
    # partículas de la capa: se agitan, se juntan bajo el punto caliente y se vuelven negras
    dr, ng = derretido(t), negro(t)
    resalta_t = win01(t, T("uno es un"), T("el otro") - 0.1, 0.15, 0.15); resalta_a = win01(t, T("un ácido"), T("mientras"), 0.15, 0.15)
    for k, (s, b, tipo) in enumerate(S["parts"]):
        pos = b + Vector((0.006 * math.sin(t * 7 + k), 0, 0.006 * math.cos(t * 6 + k * 1.3)))
        cerca = abs(b.x - MX) < 0.2
        if cerca:
            tgt = Vector((MX + (b.x - MX) * 0.45, -0.4, 1.12 + (b.z - 1.1) * 0.5))
            pos = pos.lerp(tgt, dr)
        s.location = pos
        base = DYE if tipo == "t" else ACID
        col = tuple(mix(a, b2, ng if cerca else 0) for a, b2 in zip(base, LETRA))
        set_color(s, col)
        sc_ = 1 + 0.45 * (resalta_t if tipo == "t" else resalta_a)
        s.scale = (sc_,) * 3
    S["mancha"].location = (MX, 0.0, 1.283) if ng > 0.05 else LEJOS; S["mancha"].scale = (0.16 * ng, 0.6, 0.006)
    # flecha de avance del papel
    S["avance"].location = (0.21, -0.07, 1.45 + 0.05 * ((t * 2) % 1.0)) if T("es el papel") < t < T("por eso los") else LEJOS
    # sol y crema
    us = win01(t, T("el sol"), T("el tinte vuelve"), 0.3, 0.3)
    S["sol"].location = (-0.75, -0.45, 2.05) if us > 0 else LEJOS; S["sol"].scale = (us,) * 3
    for k, r in enumerate(S["rayos"]):
        if us > 0:
            a = Vector((-0.75, -0.45, 2.05)); bq = Vector((-0.12 + 0.05 * k, -0.06, 1.45 + 0.08 * k))
            ph = (t * 1.5 + k / 6) % 1.0; bar_set(r, a.lerp(bq, ph * 0.6), a.lerp(bq, ph * 0.6 + 0.3))
        else: bar_set(r, LEJOS, Vector(LEJOS) + Vector((0, 0, 0.01)))
    uc = win01(t, T("la crema"), T("el tinte vuelve") + 0.5, 0.3, 0.3)
    S["crema"].location = (0.38, -0.3, 1.04) if uc > 0 else LEJOS; S["crema"].scale = (uc,) * 3
    ug = seg(t, T("la crema") + 0.3, T("la deshacen", fin=True))
    S["gota"].location = Vector((0.26, -0.3, 1.04)).lerp(Vector((0.1, -0.06, 1.55)), ug) if 0 < ug and uc > 0 else LEJOS
    # la uña que raya
    a0 = T("y si lo rascas")
    ud = seg(t, a0 + 0.3, T("se pone negro", fin=True))
    zr = SLOT + largo_tk(t) - drow(14)
    if a0 < t < DUR - 0.5:
        x = mix(-0.14, 0.14, ud); S["dedo"].location = (x, -0.085, zr + 0.01 * math.sin(t * 30))
        S["raya"].location = ((-0.14 + x) / 2, -0.054, zr); S["raya"].scale = (max(0.001, x + 0.14), 0.003, 0.012)
        S["roce"].location = (x + 0.04, -0.12, zr + 0.06) if ud < 0.99 else LEJOS
    else:
        S["dedo"].location = LEJOS; S["raya"].location = LEJOS; S["roce"].location = LEJOS
    apply_cam(S["cam"], *cam_lin(t, CAM()))

def CAM():
    k = Claves(); add = k.add
    def corte(t, v, hold=0.0):
        add(t - 0.04, k.k[-1][1:]); add(t, v, hold)
    ini = V((0, -0.05, 1.45), (0.5, -1.9, 0.35), 36)
    add(0.0, V((0, -0.05, 1.5), (0.4, -1.6, 0.25), 38)); add(1.6, ini)
    add(T("no lleva"), V((0, -0.06, 1.75), (0.15, -0.9, 0.05), 42), 1.0)
    add(T("entonces"), V((-0.2, 0.2, 1.3), (1.2, -3.6, 1.1), 30))
    add(T("vamos a abrir"), V((0, 0, 1.2), (0.5, -1.3, 0.45), 36), 1.2)
    corte(T("el papel tiene"), V((MX, -0.3, 1.12), (0.4, -1.9, 0.35), 34), 0.8)
    add(T("dentro hay"), V((MX - 0.3, -0.4, 1.1), (0.25, -1.3, 0.15), 38), 1.0)
    add(T("uno es un"), V((MX - 0.5, -0.4, 1.1), (0.1, -0.95, 0.1), 40), 0.8)
    add(T("el otro"), V((MX + 0.4, -0.4, 1.1), (-0.1, -0.95, 0.1), 40), 0.9)
    add(T("mientras"), V((MX, -0.4, 1.15), (-0.3, -1.5, 0.2), 36))
    add(T("ahora"), V((MX, -0.35, 1.3), (0.3, -1.6, 0.2), 36))
    add(T("es una fila"), V((MX, -0.35, 1.3), (0.3, -1.5, 0.05), 38), 1.0)
    add(T("hay ocho"), V((MX - 0.3, -0.35, 1.32), (0.1, -1.05, 0.05), 40), 0.8)
    corte(T("más de quinientos"), V((0, -0.02, 1.22), (0.35, -1.0, 0.2), 40), 1.2)
    corte(T("cuando un punto"), V((MX, -0.4, 1.28), (0.25, -1.2, 0.1), 40), 1.0)
    add(T("la capa se"), V((MX, -0.4, 1.18), (-0.15, -0.9, 0.05), 42), 1.0)
    add(T("el tinte y"), V((MX, -0.4, 1.15), (0.1, -0.8, 0.05), 44), 0.8)
    add(T("y el punto"), V((MX, -0.3, 1.2), (0.3, -1.4, 0.45), 38), 1.2)
    corte(T("y aquí viene"), V((1.7, 0, 1.0), (0.5, -6.5, 2.0), 30), 0.6)
    add(T("el cabezal no"), V((0, -0.05, 1.22), (0.4, -1.1, 0.2), 40), 0.6)
    add(T("es el papel"), V((0, -0.05, 1.55), (-0.4, -1.7, 0.1), 36))
    add(T("más de mil"), V((0, -0.05, 1.45), (0.3, -1.2, 0.0), 40))
    add(T("por eso los"), V((0, 0.1, 1.35), (-1.0, -3.4, 1.0), 30))
    add(T("la impresora casi"), V((0, -0.05, 1.7), (0.5, -2.1, 0.3), 34))
    corte(T("pero esa"), V((MX, -0.4, 1.2), (0.2, -1.1, 0.2), 40), 1.0)
    corte(T("el sol"), V((-0.2, -0.1, 1.65), (0.9, -2.6, 0.3), 32), 0.6)
    add(T("la crema"), V((0.2, -0.2, 1.2), (0.3, -1.3, 0.35), 38))
    corte(T("el tinte vuelve"), V((MX, -0.4, 1.15), (-0.2, -1.1, 0.15), 40), 0.6)
    corte(T("y la letra"), V((0, -0.06, 1.8), (0.15, -1.0, 0.05), 40))
    add(T("por eso tu"), V((0, -0.05, 1.75), (0.6, -2.0, 0.2), 34), 1.2)
    add(T("y si lo rascas") + 0.2, V((0, -0.07, SLOT + 0.94 - drow(14)), (0.3, -0.9, 0.1), 40), 1.0)
    add(T("lo calientas"), V((0, -0.07, SLOT + 0.94 - drow(14)), (-0.3, -1.1, 0.2), 38))
    add(T("sígueme"), V((0, -0.05, 1.5), (0.4, -1.6, 0.25), 38))
    add(DUR + 1, ini)
    return k.k

def anchors(sc, S, t):
    cam = S["cam"]; P = lambda v: proj(sc, cam, v); L = largo_tk(t)
    return {"ticket": P((0, -0.05, SLOT + L * 0.6)), "tktop": P((0, -0.05, SLOT + L)), "slot": P((0, -0.05, SLOT)),
            "impresora": P((0, -0.1, 1.33)), "cabezal": P((0, -0.03, 1.27)), "dot": P((MX, -0.4, 1.42)), "head": P((MX - 0.3, -0.35, 1.62)),
            "capa": P((MX, -0.4, 1.1)), "tinte": P((MX - 0.5, -0.4, 1.25)), "acido": P((MX + 0.4, -0.4, 1.25)),
            "dedo": P((0, -0.07, SLOT + L - drow(14) + 0.08)), "sol": P((-0.75, -0.45, 2.3)), "crema": P((0.38, -0.3, 1.12))}

if __name__ == "__main__":
    run("ticket", build, pose, anchors)
