# «¿Y si construyes un campo de fútbol?»: una porción de campo como maqueta, cortada por delante para ver las capas.
# Balón botando bajo la lluvia → cavas → la hierba sobre tierra se encharca (10 min) → bajas casi 2 m → piedras, grava y
# arena → tubos de drenaje con el agua bajando → invierno: tubos de agua caliente bajo las raíces → los tacos arrancan
# la hierba → la máquina clava hilos de plástico de 20 cm → las raíces se enredan (5 % plástico) → las gradas dan sombra
# → rampas de luz por la noche y la hierba crece.
# Planos (fotografía → motion; esquina libre arriba a la izquierda salvo indicación): 0 balón · 1,6 campo con lluvia ·
# 5 maqueta · 7 cavar · 9,4 charco · 13 corte del hoyo (cota a la derecha) · 15,9 piedras · 18 grava/arena · 19,7 drenaje ·
# 23 invierno · 26,5 calefacción · 32 bota · 36 césped · 39 máquina · 42,6 hilo (cota) · 44 raíces · 46 bota · 48 5 % ·
# 51,7 gradas · 53 sombra · 54,6 rampas · 57,6 hierba que crece · 60,5 vuelta al balón.
import bpy, math, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from maqueta import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("estadio")
WX = 4.0; YF = -1.0                       # ancho de la maqueta y cara del corte
Z_ST, Z_GR, Z_AR, Z_RA = -1.8, -1.3, -0.9, -0.25   # bases de piedras, grava, arena y capa de raíces
STONE = (0.62, 0.63, 0.66); GRAVA = (0.74, 0.7, 0.62); ARENA = (0.95, 0.84, 0.58); RAIZ = (0.52, 0.36, 0.22)
GRASS = PAL["cesped"]; GRASS2 = (0.36, 0.7, 0.3); MUD = (0.45, 0.33, 0.2); FRIO = (0.72, 0.82, 0.72); WHITE = (0.98, 0.98, 0.98)
FRIA = (0.35, 0.6, 0.95); CALIENTE = (0.95, 0.3, 0.2); DUSK = (0.42, 0.5, 0.78)
XB = [-1.8 + 0.12 * i for i in range(31)]         # briznas de la fila delantera
XH = [-1.62 + 0.36 * i for i in range(10)]         # hilos de plástico
XD = (-1.25, 0.0, 1.25)                            # tubos de drenaje
XC = [-1.65 + 0.55 * i for i in range(7)]          # tubos de agua caliente

def capa(z0, z1, color, dot, seed, n=26, r=(0.04, 0.09)):
    """capa de relleno que crece desde abajo (escala z del empty) con piedrecitas en la cara del corte"""
    import random; R = random.Random(seed)
    e = empty((0, 0, z0)); h = z1 - z0
    box((WX, 2.0, h), (0, 0, h / 2), color, parent=e)
    for _ in range(n):
        rr = R.uniform(*r); sph(rr, (R.uniform(-1.9, 1.9), YF - 0.005, R.uniform(rr, h - rr)), dot, parent=e, scale=(1, 0.35, 0.8), seg=8)
    e.scale.z = 1.0
    return e

def build():
    sc, cam = scene_setup(world=PAL["cielo"], shadow=0.25); entorno_claro(sc)
    S = {"cam": cam, "world": sc.world}
    nubes(10, (0, 9, 3.0), 9, 1.5, 1.5, s=1.2, seed=5)
    # base de la isla (tierra profunda)
    isla(WX, 2.0, (0, 0, Z_ST), capas=[(PAL["tierra2"], 0.45)])
    # capas del campo
    S["piedras"] = capa(Z_ST, Z_GR, STONE, (0.48, 0.49, 0.53), 1, n=22, r=(0.07, 0.13))
    S["grava"] = capa(Z_GR, Z_AR, GRAVA, (0.55, 0.52, 0.47), 2, n=40, r=(0.03, 0.05))
    S["arena"] = capa(Z_AR, Z_RA, ARENA, (0.85, 0.72, 0.45), 3, n=30, r=(0.015, 0.025))
    S["raiz"] = capa(Z_RA, 0.0, RAIZ, (0.42, 0.28, 0.16), 4, n=10, r=(0.015, 0.02))
    S["cesped"] = box((WX, 2.0, 0.06), (0, 0, 0.03), GRASS, unique=True)
    for i in range(9):                                       # rayas de corte del césped
        if i % 2: box((WX / 9, 2.0, 0.005), (-WX / 2 + WX / 9 * (i + 0.5), 0, 0.062), GRASS2, parent=S["cesped"])
    box((0.05, 2.0, 0.008), (0.9, 0, 0.064), WHITE, parent=S["cesped"])     # línea de cal
    # tierra original (antes de cavar) con su hierba
    S["tierra"] = empty((0, 0, Z_ST))
    box((WX + 0.01, 2.01, 1.8), (0, 0, 0.9), PAL["tierra"], parent=S["tierra"])
    S["tierra_top"] = box((WX + 0.01, 2.01, 0.06), (0, 0, 1.83), GRASS, parent=S["tierra"], unique=True)
    S["charco"] = box((WX - 0.2, 1.8, 0.04), LEJOS, PAL["agua"])
    # tubos de drenaje (atraviesan la capa de piedras; se ve su boca en el corte)
    S["dren"] = []
    for x in XD:
        e = empty((x, 0, Z_ST + 0.2))
        cyl(0.11, 2.03, (0, 0, 0), WHITE, parent=e, rot=(math.pi / 2, 0, 0))
        cyl(0.085, 2.05, (0, 0, 0), (0.25, 0.27, 0.3), parent=e, rot=(math.pi / 2, 0, 0))
        S["dren"].append(e)
    S["gotas"] = [sph(0.035, LEJOS, PAL["agua"], seg=10) for _ in range(18)]
    S["fl_agua"] = [flecha3d(LEJOS, (0, 0, -1), 0.35, 0.035) for _ in range(2)]
    # tubos de agua caliente bajo las raíces
    S["calor"] = []
    for x in XC:
        o = cyl(0.045, 2.03, (x, 0, -0.13), FRIA, rot=(math.pi / 2, 0, 0), unique=True); S["calor"].append(o)
    S["fl_calor"] = [flecha3d(LEJOS, (0, 0, 1), 0.3, 0.03) for _ in range(3)]
    # fila delantera de briznas y raíces
    S["briznas"] = [bar_obj(GRASS2, 0.012, unique=True) for _ in XB]
    S["raices"] = [bar_obj((0.92, 0.88, 0.75), 0.006) for _ in XB]
    S["hilos"] = [bar_obj(WHITE, 0.008) for _ in XH]
    # balón
    S["balon"] = empty(LEJOS); sph(0.11, (0, 0, 0), WHITE, parent=S["balon"], seg=16)
    torus(0.11, 0.012, (0, 0, 0), (0.15, 0.15, 0.18), parent=S["balon"]); torus(0.11, 0.012, (0, 0, 0), (0.15, 0.15, 0.18), parent=S["balon"], rot=(math.pi / 2, 0, 0))
    S["lluvia"] = [bar_obj((0.55, 0.75, 1.0), 0.008) for _ in range(40)]
    S["nieve"] = [sph(0.025, LEJOS, WHITE, seg=8) for _ in range(30)]
    # bota con tacos
    S["bota"] = empty(LEJOS)
    box((0.34, 0.13, 0.1), (0.04, 0, 0.05), (0.15, 0.15, 0.2), parent=S["bota"]); box((0.13, 0.12, 0.28), (-0.07, 0, 0.2), (0.15, 0.15, 0.2), parent=S["bota"])
    box((0.12, 0.13, 0.03), (0.05, 0, 0.09), (0.95, 0.75, 0.15), parent=S["bota"])
    for k in range(4): cyl(0.015, 0.04, (-0.1 + 0.09 * k, 0, -0.02), (0.9, 0.9, 0.9), parent=S["bota"], v=10)
    S["trozos"] = [box((0.06, 0.04, 0.03), LEJOS, GRASS) for _ in range(7)]
    # máquina que cose los hilos
    S["maq"] = empty(LEJOS)
    box((0.7, 0.5, 0.35), (0, 0, 0.35), (0.95, 0.5, 0.12), parent=S["maq"]); box((0.25, 0.4, 0.25), (-0.2, 0, 0.62), (0.85, 0.9, 0.95), parent=S["maq"])
    for sx in (-1, 1):
        for sy in (-1, 1): cyl(0.1, 0.06, (sx * 0.25, sy * 0.27, 0.1), (0.15, 0.15, 0.18), parent=S["maq"], rot=(math.pi / 2, 0, 0))
    S["aguja"] = bar_obj((0.6, 0.62, 0.66), 0.015)
    # gradas, sombra y rampas de luz
    S["gradas"] = empty((0, 0, 0))
    for k in range(5): box((WX + 1.0, 0.45, 0.35 * (k + 1)), (0, 1.35 + 0.45 * k, 0.175 * (k + 1)), (0.9, 0.3, 0.28) if k % 2 else (0.95, 0.95, 0.96), parent=S["gradas"])
    S["sombra"] = box((WX, 1.2, 0.01), LEJOS, (0.3, 0.55, 0.25))
    S["rampas"] = []
    for sx in (-1, 1):
        e = empty(LEJOS)
        for dz in (0.0, 1.6): bar = bar_obj((0.85, 0.86, 0.9), 0.025, parent=e); bar_set(bar, (0, -0.6 + 1.2 * (dz > 0), 0), (0, -0.6 + 1.2 * (dz > 0), 1.6))
        o = bar_obj((0.85, 0.86, 0.9), 0.025, parent=e); bar_set(o, (0, -0.6, 1.6), (0, 0.6, 1.6))
        box((0.15, 1.3, 0.1), (0, 0, 1.55), (0.3, 0.3, 0.33), parent=e)
        for k in range(5): box((0.12, 0.18, 0.04), (0, -0.48 + 0.24 * k, 1.49), (1.0, 0.92, 0.5), parent=e)
        S["rampas"].append(e)
    S["rayos"] = [bar_obj((1.0, 0.93, 0.55), 0.01) for _ in range(12)]
    dyn = [cam, S["piedras"], S["grava"], S["arena"], S["raiz"], S["cesped"], S["tierra"], S["charco"], S["dren"], S["gotas"], S["fl_agua"],
           S["calor"], S["fl_calor"], S["briznas"], S["raices"], S["hilos"], S["balon"], S["lluvia"], S["nieve"], S["bota"], S["trozos"],
           S["maq"], S["aguja"], S["gradas"], S["sombra"], S["rampas"], S["rayos"]]
    join_static(dyn)
    return sc, S

# ---------------- estado ----------------
def construido(t): return t < T("vamos a cavar")         # campo terminado al principio
def cavado(t): return seg(t, T("así que bajas"), T("dos metros", fin=True))
def lleno(t, nombre):
    if construido(t): return 1.0
    a = {"piedras": T("piedras gordas"), "grava": T("grava y"), "arena": T("arena"), "raiz": T("arena") + 0.6}[nombre]
    return seg(t, a - 0.1, a + 0.7)
def frio(t): return seg(t, T("pero en invierno"), T("con el frío", fin=True)) * (1 - seg(t, T("con agua caliente"), T("pero para el", fin=True)))
def caliente(t): return seg(t, T("con agua caliente") - 0.3, T("como una") + 0.3)
def noche(t): return seg(t, T("por la noche") - 0.3, T("acercan")) * (1 - seg(t, T("sígueme") - 0.3, DUR))
def hilo_t(i): return mix(T("una máquina") + 0.3, T("uno a uno", fin=True), (i + 0.5) / len(XH))

def pose(t, S):
    S["world"].color = Vector(lin(PAL["cielo"])).lerp(Vector(lin(DUSK)), noche(t))
    # capas
    for n in ("piedras", "grava", "arena", "raiz"):
        u = lleno(t, n); S[n].scale.z = max(u, 0.001); S[n].hide_render = u < 0.01
        for c in S[n].children: c.hide_render = u < 0.01
    fin = construido(t) or t > T("arena") + 0.6
    S["cesped"].location.z = 0 if fin else -50
    # tierra original y su hierba
    vt = (T("vamos a cavar") <= t < T("dos metros", fin=True) + 0.2)
    S["tierra"].location = (0, 0, Z_ST) if vt else LEJOS
    S["tierra"].scale.z = max(1 - cavado(t), 0.001)
    set_color(S["tierra_top"], tuple(mix(a, b, seg(t, T("a los diez"), T("barrizal"))) for a, b in zip(GRASS, MUD)))
    ch = seg(t, T("la lluvia se"), T("barrizal")) * (1 - seg(t, T("así que bajas") - 0.4, T("así que bajas")))
    S["charco"].location = (0, 0, 0.06 + 0.04 * ch - 0.02) if ch > 0.01 else LEJOS; S["charco"].scale.z = max(ch, 0.01)
    # color del césped: frío en invierno, recupera con el calor
    fr = frio(t); set_color(S["cesped"], tuple(mix(a, b, fr) for a, b in zip(GRASS, FRIO)))
    # lluvia
    llueve = t < T("ves un partido") + 4.8 or (T("la lluvia se") - 0.3 < t < T("así que bajas"))
    for k, r in enumerate(S["lluvia"]):
        if llueve:
            x = -1.9 + 3.8 * ((k * 0.618) % 1.0); y = -0.9 + 1.8 * ((k * 0.37) % 1.0); z = 2.6 - ((t * 1.6 + k * 0.29) % 1.0) * 2.6
            bar_set(r, (x, y, z + 0.2), (x, y, z))
        else: bar_set(r, LEJOS, Vector(LEJOS) + Vector((0, 0, 0.01)))
    # nieve en invierno
    for k, p in enumerate(S["nieve"]):
        if fr > 0.05:
            p.location = (-1.9 + 3.8 * ((k * 0.618) % 1.0) + 0.05 * math.sin(t * 2 + k), -0.9 + 1.8 * ((k * 0.41) % 1.0), 2.2 - ((t * 0.5 + k * 0.137) % 1.0) * 2.1)
        else: p.location = LEJOS
    # balón botando (principio y final)
    for a, b in ((0.0, T("y si tuvieras")), (T("sígueme") - 0.2, DUR + 2)):
        if a <= t < b:
            ph = ((t - a) * 1.6) % 1.0; S["balon"].location = (-0.4 + 0.25 * (t - a), -0.35, 0.17 + 0.9 * 4 * ph * (1 - ph))
            S["balon"].rotation_euler = (t * 3, t * 2, 0); break
    else: S["balon"].location = LEJOS
    # drenaje: tubos y agua que baja por las capas
    dv = construido(t) or t > T("una red de tubos") - 0.1
    for k, e in enumerate(S["dren"]):
        e.location = (XD[k], 0, Z_ST + 0.2) if dv else LEJOS
        e.scale = (1, 1, 1) if construido(t) else (seg(t, T("una red de tubos") - 0.1 + 0.15 * k, T("una red de tubos") + 0.3 + 0.15 * k),) * 3
    baja = (T("bajo todo") - 0.2 < t < T("pero en invierno") + 0.2) or t < 4.8
    for k, g in enumerate(S["gotas"]):
        if baja:
            u = (t * 0.45 + k / len(S["gotas"])) % 1.0; x0 = -1.8 + 3.6 * ((k * 0.618) % 1.0); xt = XD[min(range(3), key=lambda j: abs(XD[j] - x0))]
            g.location = (mix(x0, xt, ss(u)), YF - 0.04, mix(0.05, Z_ST + 0.3, u))
        else: g.location = LEJOS
    for k, f in enumerate(S["fl_agua"]):
        f.location = (-0.7 + 1.4 * k, YF - 0.15, -0.35 - 0.15 * ((t * 1.2) % 1.0)) if T("una red de tubos") < t < T("pero en invierno") else LEJOS
    # calefacción
    cv = construido(t) or t > T("así que metes") + 0.2
    for k, o in enumerate(S["calor"]):
        o.location = (XC[k], 0, -0.13) if cv else LEJOS
        set_color(o, tuple(mix(a, b, caliente(t)) for a, b in zip(FRIA, CALIENTE)))
    for k, f in enumerate(S["fl_calor"]):
        on = T("con agua caliente") < t < T("pero los tacos")
        f.location = (-1.1 + 1.1 * k, YF - 0.12, -0.08 + 0.12 * ((t * 1.3 + k * 0.3) % 1.0)) if on else LEJOS
    # máquina e hilos
    t0, t1 = T("una máquina") + 0.1, T("uno a uno", fin=True) + 0.3
    if t0 - 0.6 < t < t1 + 0.8:
        x = mix(-2.6, 2.6, (t - t0 + 0.6) / (t1 - t0 + 1.4)); S["maq"].location = (x, YF + 0.35, 0.06)
        bar_set(S["aguja"], (x + 0.3, YF + 0.05, 0.55), (x + 0.3, YF + 0.05, 0.12 + 0.25 * (0.5 + 0.5 * math.cos(t * 18))))
    else:
        S["maq"].location = LEJOS; bar_set(S["aguja"], LEJOS, Vector(LEJOS) + Vector((0, 0, 0.01)))
    for i, h in enumerate(S["hilos"]):
        th = hilo_t(i)
        if t > th - 0.15 and not construido(t):
            d = seg(t, th - 0.15, th + 0.1); top = 0.13
            bar_set(h, (XH[i], YF - 0.012, top - 0.2 * d), (XH[i], YF - 0.012, top))
        else: bar_set(h, LEJOS, Vector(LEJOS) + Vector((0, 0, 0.01)))
    # briznas y raíces de la fila delantera
    crece = seg(t, T("la hierba cree"), T("y sigue", fin=True) + 0.4)
    enreda = seg(t, T("las raíces de"), T("se enredan", fin=True) + 0.5)
    cesp_vis = construido(t) or t > T("arena") + 0.6
    for k, (b, r) in enumerate(zip(S["briznas"], S["raices"])):
        x = XB[k]
        if cesp_vis:
            h = (0.09 + 0.03 * math.sin(k * 1.7)) * (1 - 0.35 * frio(t)) * (1 + 0.6 * crece)
            sw = 0.012 * math.sin(t * 2.5 + k)
            bar_set(b, (x, YF + 0.03, 0.06), (x + sw, YF + 0.03, 0.06 + h))
            set_color(b, tuple(mix(a, c, frio(t)) for a, c in zip(GRASS2, FRIO)))
            rl = 0.12 + 0.1 * enreda
            bar_set(r, (x, YF - 0.008, 0.0), (x + 0.05 * math.sin(k * 2.3) + 0.04 * enreda * math.sin(k), YF - 0.008, -rl))
        else:
            bar_set(b, LEJOS, Vector(LEJOS) + Vector((0, 0, 0.01))); bar_set(r, LEJOS, Vector(LEJOS) + Vector((0, 0, 0.01)))
    # bota que pisa (dos veces) y trozos que salen la primera vez
    for a, rompe in ((T("pero los tacos"), True), (T("y ya no"), False)):
        if a - 0.4 < t < a + 1.6:
            u = (t - a + 0.4) / 2.0; z = 0.07 + 0.6 * abs(math.sin(u * math.pi * 2))
            S["bota"].location = (0.45 + 0.1 * u, YF + 0.35, z); S["bota"].rotation_euler = (0, -0.2 * math.sin(u * 6), 0)
            for k, c in enumerate(S["trozos"]):
                if rompe and u > 0.25:
                    v = u - 0.25; c.location = (0.45 + 0.08 * (k - 3) + 0.5 * v * (k - 3) * 0.3, YF + 0.3 - 0.4 * v, 0.08 + 1.4 * v - 2.4 * v * v)
                    c.rotation_euler = (t * 5 + k, t * 3, 0)
                else: c.location = LEJOS
            break
    else:
        S["bota"].location = LEJOS
        for c in S["trozos"]: c.location = LEJOS
    # gradas y sombra
    ug = seg(t, T("pero dentro"), T("las gradas")) if T("vamos a cavar") <= t < T("sígueme") - 0.3 else 1.0
    S["gradas"].location = (0, 0, -4.5 * (1 - ug)) if ug > 0.01 else LEJOS
    S["sombra"].location = (0, 0.35, 0.068) if T("tapan el sol") - 0.1 < t < T("acercan") + 0.6 else LEJOS
    # rampas de luz
    ur = seg(t, T("acercan") - 0.2, T("enormes", fin=True))
    for k, e in enumerate(S["rampas"]):
        sx = -1 if k == 0 else 1
        e.location = (sx * mix(3.4, 1.1, ur), -0.1, 0.06) if T("por la noche") < t < T("sígueme") + 0.2 else LEJOS
    for k, r in enumerate(S["rayos"]):
        if ur > 0.8 and t < T("sígueme") + 0.2:
            sx = -1 if k < 6 else 1; j = k % 6; x0 = sx * mix(3.4, 1.1, ur)
            p0 = Vector((x0, -0.58 + 0.23 * (j % 5), 1.48)); p1 = Vector((x0 - sx * (0.4 + 0.15 * j), -0.6 + 0.24 * (j % 5), 0.07))
            bar_set(r, p0, p0.lerp(p1, 0.6 + 0.4 * (0.5 + 0.5 * math.sin(t * 6 + j))))
        else: bar_set(r, LEJOS, Vector(LEJOS) + Vector((0, 0, 0.01)))
    apply_cam(S["cam"], *cam_lin(t, CAM()))

def CAM():
    k = Claves(); add = k.add
    ini = V((-0.3, -0.35, 0.3), (0.7, -2.6, 0.8), 34)
    ancho = V((0, 0, -0.8), (2.5, -7.5, 2.2), 30)
    add(0.0, V((-0.35, -0.35, 0.3), (0.6, -2.2, 0.6), 36)); add(1.3, ini)
    add(T("y el césped") + 0.4, V((0, 0, 0.2), (1.5, -4.5, 1.8), 32), 0.6)
    add(T("aunque lleva"), V((0.3, -0.7, 0.1), (-0.6, -2.0, 0.5), 36))
    add(T("y si tuvieras"), ancho, 0.8)
    add(T("vamos a cavar"), V((0, -1, -0.8), (0.8, -5.0, 0.6), 30))
    add(T("si plantas"), V((0, -0.6, 0.05), (1.2, -3.2, 1.4), 32))
    add(T("la lluvia se"), V((-0.4, -0.6, 0.1), (0.4, -2.2, 0.9), 36), 0.6)
    add(T("a los diez"), V((0, 0, -0.2), (-1.8, -5.5, 2.0), 30), 1.0)
    add(T("así que bajas"), V((0, -1, -0.9), (0.6, -5.2, 0.4), 30), 2.0)
    add(T("y lo rellenas"), V((-0.6, -1, -1.4), (0.5, -2.8, 0.3), 34), 0.8)
    add(T("grava y"), V((0.3, -1, -0.8), (-0.4, -2.9, 0.3), 34), 0.8)
    add(T("bajo todo"), V((0, -1, -1.55), (0.4, -2.3, 0.15), 38), 1.6)
    add(T("que se lleva"), V((0, 0, -0.7), (2.4, -6.6, 1.5), 30))
    add(T("pero en invierno") + 0.2, V((0.3, -0.9, 0.05), (0.5, -2.2, 0.5), 38), 1.4)
    add(T("así que metes"), V((0, -1, -0.15), (-0.4, -2.0, 0.2), 40), 1.4)
    add(T("como una"), V((0, -1, -0.3), (0.8, -3.4, 0.6), 34), 1.0)
    add(T("pero los tacos"), V((0.5, -0.7, 0.1), (0.6, -2.2, 0.6), 36), 1.6)
    add(T("y aquí viene"), V((0, 0, 0), (-2.0, -6.0, 3.0), 30))
    add(T("el césped de muchos"), V((0, -0.9, 0.05), (0.4, -1.8, 0.35), 40), 0.8)
    add(T("una máquina"), V((0, -0.6, 0.2), (1.2, -3.0, 1.0), 34), 0.6)
    add(T("en el suelo"), V((0.6, -0.8, 0.2), (0.4, -1.9, 0.35), 40))
    add(T("cada hilo"), V((0.2, -1, -0.06), (0.2, -1.35, 0.05), 45), 1.0)
    add(T("las raíces de"), V((-0.4, -1, -0.06), (-0.3, -1.45, 0.12), 42), 1.0)
    add(T("y ya no"), V((0.5, -0.7, 0.1), (0.6, -2.2, 0.6), 36))
    add(T("solo un cinco"), V((0, -0.5, -0.2), (1.6, -4.6, 1.4), 32), 0.8)
    add(T("el resto"), V((-0.5, -0.9, 0.05), (0.3, -1.6, 0.25), 42))
    add(T("pero dentro"), V((0, 1, 0.5), (1.5, -8.0, 3.0), 30), 0.6)
    add(T("las gradas") + 0.4, V((0, 0, 0), (-1.5, -5.5, 2.5), 30))
    add(T("por la noche") - 0.4, V((0, 0, 0.3), (2.5, -6.5, 2.0), 30), 1.4)
    add(T("enormes"), V((-0.8, -0.4, 0.4), (0.9, -3.4, 1.0), 34))
    add(T("la hierba cree"), V((0.2, -0.9, 0.06), (0.4, -1.8, 0.4), 40), 1.0)
    add(T("y sigue"), V((0, -0.3, 0.2), (-1.0, -3.2, 1.0), 34))
    add(T("sígueme"), V((-0.35, -0.35, 0.3), (0.6, -2.2, 0.6), 36))
    add(DUR + 1, ini)
    return k.k

def anchors(sc, S, t):
    cam = S["cam"]; P = lambda v: proj(sc, cam, v)
    return {"top": P((1.2, YF, 0.0)), "fondo": P((1.2, YF, Z_ST)), "piedras": P((-0.6, YF, -1.55)), "grava": P((0.3, YF, -1.1)),
            "arena": P((0.3, YF, -0.6)), "dren": P((0, YF, Z_ST + 0.2)), "calor": P((0, YF, -0.13)), "cesped": P((0.0, -0.5, 0.15)),
            "hilo_top": P((0.18, YF, 0.13)), "hilo_bot": P((0.18, YF, -0.07)), "raices": P((-0.4, YF, -0.15)), "maq": P((0, YF + 0.35, 0.8)),
            "bota": P((0.5, YF + 0.35, 0.4)), "rampa": P((-1.1, -0.1, 1.7)), "charco": P((0, -0.3, 0.1))}

if __name__ == "__main__":
    run("estadio", build, pose, anchors)
