# «El sifón de tu fregadero»: cocina de maqueta sobre una isla de terreno cortada. Se abren las puertas del armario y el
# agua del grifo baja por el tubo en U. Se corta el tubo: sin la U, el gas de la alcantarilla sube hasta la cocina; con la U,
# un tapón de agua lo para. Altura del tapón (5-7 cm), el grifo que renueva el agua, las vacaciones que la evaporan
# (5 → 0 cm), los diez segundos de grifo, el anillo atrapado y la U que se desenrosca.
# Planos (fotografía → motion): 0 armario+chorro (libre: arriba) · 2,6 U · 4,5 maqueta · 6,8 desagüe · 8,6 corte ·
# 9,4 alcantarilla · 12 gas · 14,8 nube · 17,4 U nueva · 21 agua · 25 flecha · 29,7 tapón · 36,4 grifo · 43 vacaciones ·
# 47 nivel · 50 gas · 53 grifo · 56 anillo · 59 rosca · 61,6 vuelta al primer plano.
import bpy, math, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from maqueta import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("sifon")
YP = 0.55; ZW = 0.46; ZVACIO = 0.22
STEEL = (0.78, 0.8, 0.84); PIPE = (0.93, 0.93, 0.95); SEWER = (0.62, 0.6, 0.56); WHITE = (0.97, 0.97, 0.98)
GAS = (0.55, 0.8, 0.22); WATER = PAL["agua"]; OLD = (0.62, 0.58, 0.45); GOLD = (1.0, 0.78, 0.2); FLOOR = (0.93, 0.84, 0.68)

DRAIN = [(0, YP, 0.70), (0, YP, 0.36)]
UARC = arco((0.11, YP, 0.36), 0.11, 180, 360, n=20)
OUT = [(0.22, YP, 0.36), (0.22, YP, 0.42)] + arco((0.32, YP, 0.42), 0.1, 180, 90, n=10)[1:] + [(0.40, YP, 0.52)] + \
      arco((0.40, YP, 0.42), 0.1, 90, 0, n=10)[1:] + [(0.50, YP, -0.60)]
FLOW = poly([(0, YP, 0.9)] + DRAIN + UARC[1:] + OUT[1:] + [(0.50, YP, -0.75), (1.4, YP, -0.75)])
SEW = [(-1.4, YP, -0.78), (0.5, YP, -0.78), (0.5, YP, -0.6), (0.5, YP, 0.42)]
GAS_IN = poly(SEW + arco((0.40, YP, 0.42), 0.1, 0, 90, n=8)[1:] + [(0.32, YP, 0.52)] + arco((0.32, YP, 0.42), 0.1, 90, 135, n=6)[1:])
GAS_OPEN = poly(SEW + arco((0.40, YP, 0.42), 0.1, 0, 90, n=8)[1:] + [(0.32, YP, 0.52)] + arco((0.32, YP, 0.42), 0.1, 90, 180, n=10)[1:] +
                [(0.22, YP, 0.36)] + list(reversed(UARC))[1:] + [(0, YP, 0.7), (0, YP, 1.0)])
GAS_RECTO = poly([(-1.4, YP, -0.78), (0, YP, -0.78), (0, YP, 1.0)])

def build():
    sc, cam = scene_setup(world=PAL["cielo"], shadow=0.25); entorno_claro(sc)
    S = {"cam": cam}
    nubes(9, (0, 7, 1.2), 7, 1.6, 1.0, s=0.9, seed=3)
    # isla: suelo de la cocina y capas de tierra cortadas detrás del plano de los tubos
    box((3.0, 1.55, 0.06), (0, 0.25, -0.03), FLOOR)
    box((3.0, 1.55, 0.22), (0, 0.25, -0.17), PAL["hormigon"])
    isla(3.0, 0.3, (0, YP + 0.33, -0.28), capas=[(PAL["tierra"], 0.5), (PAL["tierra2"], 0.5)])
    isla(3.0, 1.55, (0, 0.25, -0.95), capas=[(PAL["tierra"], 0.12), (PAL["tierra2"], 0.3)])
    # pared de azulejos y encimera con el hueco del fregadero
    azulejos(3.0, 2.0, (0, 1.0, 1.0), color=PAL["menta"])
    box((3.0, 0.04, 2.0), (0, 1.03, 1.0), PAL["menta"])
    CT = PAL["encimera"]
    box((1.13, 0.8, 0.05), (-0.835, 0.6, 0.875), CT); box((1.13, 0.8, 0.05), (0.835, 0.6, 0.875), CT)
    box((0.54, 0.15, 0.05), (0, 0.275, 0.875), CT); box((0.54, 0.25, 0.05), (0, 0.875, 0.875), CT)
    # fregadero de acero
    box((0.54, 0.4, 0.02), (0, YP, 0.69), STEEL)
    for sx in (-1, 1): box((0.02, 0.4, 0.2), (sx * 0.26, YP, 0.79), STEEL)
    for sy in (-1, 1): box((0.54, 0.02, 0.2), (0, YP + sy * 0.19, 0.79), STEEL)
    torus(0.035, 0.008, (0, YP, 0.705), (0.4, 0.42, 0.45))
    # grifo
    cyl(0.04, 0.03, (0, 0.85, 0.915), STEEL); cyl(0.022, 0.33, (0, 0.85, 1.08), STEEL)
    o = bar_obj(STEEL, 0.02); bar_set(o, (0, 0.85, 1.24), (0, 0.6, 1.24)); sph(0.024, (0, 0.85, 1.24), STEEL)
    cyl(0.018, 0.05, (0, 0.6, 1.215), STEEL)
    S["lever"] = empty((0, 0.85, 1.13)); box((0.025, 0.12, 0.02), (0, -0.06, 0.0), (0.9, 0.3, 0.3), parent=S["lever"])
    S["chorro"] = bar_obj(WATER, 0.016, unique=True)
    # armario bajo el fregadero (sin frente) y sus puertas
    for sx in (-1, 1): box((0.03, 0.66, 0.84), (sx * 0.62, 0.53, 0.43), WHITE)
    box((1.27, 0.03, 0.84), (0, 0.865, 0.43), (0.92, 0.92, 0.93)); box((1.27, 0.66, 0.04), (0, 0.53, 0.06), WHITE)
    box((1.27, 0.06, 0.06), (0, 0.22, 0.03), (0.75, 0.75, 0.78))
    S["pL"] = empty((-0.62, 0.19, 0.46)); S["pR"] = empty((0.62, 0.19, 0.46))
    for p, sx in ((S["pL"], 1), (S["pR"], -1)):
        box((0.6, 0.025, 0.78), (sx * 0.3, 0, 0), (0.98, 0.86, 0.62), parent=p)
        box((0.025, 0.03, 0.14), (sx * 0.52, -0.03, 0.2), STEEL, parent=p)
    # detalles de cocina
    cyl(0.07, 0.12, (-1.0, 0.8, 0.96), PAL["maceta"]); sph(0.12, (-1.0, 0.8, 1.12), PAL["planta"], scale=(1, 1, 1.2), seg=10)
    cyl(0.055, 0.22, (1.05, 0.85, 1.01), WHITE, rot=(0, 0, 0)); cyl(0.02, 0.23, (1.05, 0.85, 1.01), (0.75, 0.6, 0.45))
    box((0.3, 0.2, 0.02), (0.65, 0.7, 0.91), (0.85, 0.9, 0.95)); cyl(0.09, 0.02, (0.65, 0.7, 0.93), (0.95, 0.5, 0.4))
    # tubos: enteros al principio y cortados por la mitad desde «vamos a abrirlo»
    S["cut"] = cortador((4.0, 2.0, 6.0), (0, YP - 1.0, 0))
    S["enteros"] = [tubo(DRAIN, 0.062, PIPE), tubo(UARC, 0.062, PIPE), tubo(OUT, 0.062, PIPE)]
    S["drain"] = medio_tubo(DRAIN, 0.05, 0.012, PIPE); S["u"] = medio_tubo(UARC, 0.05, 0.012, PIPE)
    S["out"] = medio_tubo(OUT, 0.05, 0.012, PIPE)
    S["recto"] = medio_tubo([(0, YP, 0.70), (0, YP, -0.6)], 0.05, 0.012, PIPE)
    medio_tubo([(-1.48, YP, -0.75), (1.48, YP, -0.75)], 0.16, 0.025, SEWER)
    # agua atrapada: sólido recortado por el nivel
    S["nivel"] = cortador((3, 3, 2), (0, YP, ZW - 1.0))
    S["agua"] = tubo([(0, YP, 0.62)] + UARC + [(0.22, YP, 0.42)] + arco((0.32, YP, 0.42), 0.1, 180, 110, n=8)[1:], 0.049, WATER, tapas=True, unique=True)
    for c, op in ((S["cut"], 'DIFFERENCE'), (S["nivel"], 'INTERSECT')):
        m = cortar(S["agua"], c, op); m.material_mode = 'INDEX'
    # tuercas de la U
    S["nuts"] = []
    for x in (0.0, 0.22):
        e = empty((x, YP, 0.37)); torus(0.06, 0.016, (0, 0, 0), (0.85, 0.86, 0.9), parent=e)
        box((0.02, 0.03, 0.035), (0.07, 0, 0), (0.55, 0.57, 0.62), parent=e); S["nuts"].append(e)
    # anillo y restos
    S["ring"] = torus(0.03, 0.008, LEJOS, GOLD, rot=(math.pi / 2, 0, 0))
    S["bits"] = [sph(0.016, LEJOS, (0.55, 0.38, 0.2), seg=8) for _ in range(4)]
    # partículas
    S["pw"] = [sph(0.018, LEJOS, WATER, seg=10) for _ in range(14)]
    S["po"] = [sph(0.018, LEJOS, OLD, seg=10) for _ in range(6)]
    S["pg"] = [sph(0.03, LEJOS, GAS, seg=10) for _ in range(16)]
    S["nube"] = [sph(0.09, LEJOS, GAS, seg=12) for _ in range(7)]
    # flechas rojas (gas que empuja)
    S["fl1"] = flecha3d(LEJOS, (0, 0, -1), 0.17, 0.016)
    S["fl2"] = flecha3d(LEJOS, (1, 0, 0), 0.3, 0.03)
    dyn = [cam, S["lever"], S["chorro"], S["pL"], S["pR"], S["cut"], S["enteros"], S["drain"], S["u"], S["out"], S["recto"], S["nivel"],
           S["agua"], S["nuts"], S["ring"], S["bits"], S["pw"], S["po"], S["pg"], S["nube"], S["fl1"], S["fl2"]]
    join_static(dyn)
    return sc, S

# ---------------- estado ----------------
def grifo(t):
    return t < 2.4 or (T("cada vez que") - 0.1 < t < T("una y otra", fin=True) + 0.3) or (T("basta con") < t < T("y la u") )

def recto(t): return T("el desagüe") - 0.15 < t < T("así que el tubo")

def nivel(t):
    z = ZW
    if T("cuando el agua") < t < T("una parte") + 1.6: z = mix(ZVACIO, ZW, seg(t, T("una parte"), T("una parte") + 1.6))
    z -= 0.04 * seg(t, T("pero si te vas"), T("poco a poco", fin=True))
    z = mix(z, ZVACIO, seg(t, T("el nivel baja"), T("a cero", fin=True)))
    z = mix(z, ZW, seg(t, T("basta con"), T("segundos", fin=True)))
    return z

def desenrosca(t): return -0.2 * seg(t, T("para poder"), T("limpiarla", fin=True))

def nube(t):
    return max(seg(t, T("huele") - 1.2, T("huele")) * (1 - seg(t, T("así que el tubo") - 0.3, T("así que el tubo") + 0.3)),
               seg(t, T("la puerta se abre") + 0.4, T("la casa huele")) * (1 - seg(t, T("basta con"), T("basta con") + 0.8)))

def pose(t, S):
    a = mix(0.45, 1.95, seg(t, 0.0, 1.3))
    S["pL"].rotation_euler.z = -a; S["pR"].rotation_euler.z = a
    on = grifo(t)
    S["lever"].rotation_euler.z = 0.6 if on else 0.0
    if on: bar_set(S["chorro"], (0, 0.6, 1.2), (0, 0.6 + 0.01 * math.sin(t * 20), 0.69))
    else: bar_set(S["chorro"], LEJOS, Vector(LEJOS) + Vector((0, 0, 0.01)))
    # corte que barre de izquierda a derecha
    cortado = t > T("abrirlo") + 0.1
    for o in S["enteros"]: o.hide_render = cortado
    S["agua"].modifiers[0].show_render = cortado
    rc = recto(t); dz = desenrosca(t)
    S["recto"].hide_render = not rc
    S["drain"].hide_render = not cortado or rc or (T("el desagüe") < t < T("así que el tubo"))
    S["u"].hide_render = not cortado or rc or (T("el desagüe") < t < T("hace una curva") - 0.05)
    S["out"].hide_render = not cortado or rc or (T("el desagüe") < t < T("y vuelve a subir") - 0.05)
    S["u"].location.z = dz
    lv = nivel(t)
    vis_agua = not (T("el desagüe") - 0.15 < t < T("cuando el agua") + 0.5)
    S["agua"].hide_render = not vis_agua or lv < ZVACIO + 0.01
    S["agua"].location.z = dz; S["nivel"].location.z = lv - 1.0 + dz
    for k, e in enumerate(S["nuts"]):
        e.rotation_euler.z = 9.0 * seg(t, T("se desenrosca") - 0.3, T("para poder"))
        vis = t < T("el desagüe") or t > T("hace una curva") - 0.05
        e.location = (0.22 * k, YP, 0.37 + dz) if vis else LEJOS
    # agua del grifo bajando por el tubo
    L = largo(FLOW)
    for k, p in enumerate(S["pw"]):
        if on and not rc:
            p.location = at(FLOW, ((k / len(S["pw"]) + t * 0.55) % 1.0) * L)
        elif on and rc:
            p.location = Vector((0, YP, 0.9 - ((k / len(S["pw"]) + t * 0.55) % 1.0) * 1.5))
        else: p.location = LEJOS
    # agua vieja empujada fuera del tapón
    u0 = seg(t, T("el agua nueva"), T("hacia abajo", fin=True) + 0.4)
    for k, p in enumerate(S["po"]):
        if T("el agua nueva") - 0.1 < t < T("una y otra", fin=True):
            s = FLOW[1][5] + 0.3 + k * 0.04 + u0 * 1.4
            p.location = at(FLOW, s)
        else: p.location = LEJOS
    # gas
    for k, p in enumerate(S["pg"]):
        p.location = LEJOS
        ph = (k / len(S["pg"]) + t * 0.22) % 1.0
        if rc and t > T("y desde ahí") - 0.6:
            p.location = at(GAS_RECTO, ph * largo(GAS_RECTO)) + Vector((0.03 * math.sin(t * 7 + k), 0, 0))
        elif T("el gas empuja") - 1.5 < t < T("y aquí viene") + 0.5 or (T("pero si te vas") - 0.5 < t < T("la puerta se abre")):
            s = min(largo(GAS_IN) - 0.012 * (k % 6), ph * largo(GAS_IN) * 1.25)
            p.location = at(GAS_IN, s) + Vector((0.012 * math.sin(t * 9 + k), 0, 0.01 * math.sin(t * 11 + k)))
        elif T("la puerta se abre") <= t < T("basta con") + 0.6:
            p.location = at(GAS_OPEN, ph * largo(GAS_OPEN)) + Vector((0.02 * math.sin(t * 7 + k), 0, 0))
    # nube de olor sobre el fregadero
    c = nube(t)
    for k, p in enumerate(S["nube"]):
        if c > 0.02:
            ang = k * 0.9 + t * 0.4
            p.location = (0.22 * math.cos(ang) * c, YP + 0.08 * math.sin(ang), 1.0 + 0.25 * c + 0.06 * k * c)
            p.scale = (c * (0.8 + 0.3 * math.sin(t * 2 + k)),) * 3
        else: p.location = LEJOS
    # flechas
    if T("el gas empuja") - 0.2 < t < T("y aquí viene") + 0.3:
        S["fl1"].location = (0.25, YP - 0.09, 0.66 + 0.025 * math.sin(t * 9))
        S["fl1"].scale = (1, 1, 1 + 0.25 * (0.5 + 0.5 * math.sin(t * 9)))
    else: S["fl1"].location = LEJOS
    S["fl2"].location = (-0.7 + 0.15 * ((t * 0.8) % 1.0), YP - 0.2, -0.75) if T("y desde ahí") < t < T("huele") else LEJOS
    # anillo y restos de comida que caen y se quedan en la U
    ta = T("y la u")
    if t > ta:
        s = min(FLOW[1][3] + 0.06, (t - ta) * 1.0)
        pr = at(FLOW, s) if t < ta + 1.4 else Vector((0.11, YP, 0.27))
        S["ring"].location = pr + Vector((0, -0.02, dz if t > ta + 1.4 else 0))
        S["ring"].rotation_euler = (math.pi / 2, t * 3 if t < ta + 1.4 else 0.4, 0)
    else: S["ring"].location = LEJOS
    for k, b in enumerate(S["bits"]):
        tb = T("pendientes") + 0.25 * k
        if t > tb:
            s = min(FLOW[1][3] + 0.06, (t - tb) * 1.1)
            b.location = (at(FLOW, s) if t < tb + 1.4 else Vector((0.07 + 0.03 * k, YP - 0.02, 0.27 + 0.01 * (k % 2)))) + Vector((0, 0, dz if t > tb + 1.4 else 0))
        else: b.location = LEJOS
    apply_cam(S["cam"], *cam_lin(t, CAM()))

def CAM():
    k = Claves(); add = k.add
    ini = V((0.1, 0.45, 0.75), (0.45, -2.1, 0.45), 32)
    ucl = V((0.16, YP, 0.4), (0.1, -1.15, 0.12), 38)
    ancho = V((0.15, 0.5, 0.25), (1.2, -4.0, 1.4), 30)
    add(0.0, V((0.1, 0.45, 0.75), (0.35, -1.8, 0.35), 34)); add(1.6, ini)
    add(T("ves ese") + 0.2, ucl, 1.2)
    add(T("parece") + 0.3, ancho, 1.0)
    add(T("tu cocina") + 0.1, V((0, YP, 0.85), (0.3, -0.9, 0.7), 34))
    add(T("vamos a"), V((0.2, YP, 0.38), (-0.15, -1.2, 0.05), 38), 0.6)
    add(T("el desagüe") + 0.7, V((0.0, YP, -0.55), (0.5, -1.7, 0.25), 32), 1.0)
    add(T("y desde ahí"), V((-0.2, YP, -0.75), (0.3, -1.25, 0.15), 38), 0.8)
    add(T("de las cloacas") , V((0, YP, 0.3), (0.45, -1.8, 0.25), 34))
    add(T("huele"), V((0, YP, 1.1), (0.5, -1.6, 0.35), 34), 1.2)
    add(T("así que el tubo"), V((0.2, YP, 0.42), (0.3, -1.4, 0.2), 36), 1.0)
    add(T("y vuelve a subir"), V((0.15, YP, 0.4), (-0.3, -1.1, 0.2), 40))
    add(T("una parte"), V((0.11, YP, 0.34), (0.1, -0.9, 0.02), 40), 1.4)
    add(T("ese tapón"), V((0.2, YP, 0.42), (0.4, -1.3, 0.3), 36))
    add(T("el gas empuja"), V((0.22, YP, 0.5), (0.25, -0.9, 0.15), 40), 1.4)
    add(T("y aquí viene"), V((0.1, 0.5, 0.15), (-1.0, -3.6, 1.0), 30))
    add(T("la norma"), V((0.11, YP, 0.37), (0.0, -0.8, 0.05), 42), 2.6)
    add(T("si es más"), V((0.2, YP, 0.4), (0.5, -1.3, 0.2), 36), 1.4)
    add(T("cada vez que"), V((0, 0.6, 1.0), (0.4, -1.2, 0.45), 34), 0.8)
    add(T("el agua nueva"), V((0.15, YP, 0.36), (-0.2, -1.0, 0.1), 40), 1.4)
    add(T("el tapón se renueva"), ancho, 1.2)
    add(T("pero si te vas"), V((0, 0.5, 0.6), (0.0, -4.4, 1.6), 30), 0.8)
    add(T("el agua se evapora"), V((0.11, YP, 0.36), (0.15, -0.85, 0.1), 42), 0.8)
    add(T("el nivel baja"), V((0.11, YP, 0.34), (-0.1, -0.8, 0.05), 42), 2.0)
    add(T("la puerta se abre"), V((0.1, YP, 0.6), (0.3, -1.45, 0.2), 36))
    add(T("la casa huele"), V((0, YP, 1.0), (0.6, -2.0, 0.6), 32), 0.6)
    add(T("basta con"), V((0, 0.6, 1.0), (-0.4, -1.1, 0.4), 36), 0.8)
    add(T("segundos") - 0.3, V((0.11, YP, 0.36), (0.1, -0.9, 0.05), 40))
    add(T("y la u"), V((0.05, YP, 0.5), (0.2, -1.25, 0.2), 36), 0.6)
    add(T("pendientes"), V((0.11, YP, 0.3), (-0.1, -0.85, 0.05), 42), 0.6)
    add(T("por eso se"), V((0.11, YP, 0.32), (0.3, -1.0, 0.25), 38), 0.6)
    add(T("para poder"), V((0.11, YP, 0.25), (0.0, -1.2, 0.2), 36), 0.6)
    add(T("sígueme"), V((0.1, 0.45, 0.75), (0.35, -1.8, 0.35), 34))
    add(DUR + 1, ini)
    return k.k

def anchors(sc, S, t):
    cam = S["cam"]; P = lambda v: proj(sc, cam, v); dz = desenrosca(t); lv = nivel(t)
    return {"agua": P((0.22, YP, lv)), "fondo": P((0.11, YP, 0.30 + dz)), "sup": P((0.0, YP, lv)), "fregadero": P((0, YP, 0.95)),
            "grifo": P((0, 0.62, 1.3)), "alcan": P((0, YP, -0.55)), "nube": P((0, YP, 1.45)), "armario": P((0, 0.2, 0.9)),
            "u": P((0.11, YP, 0.2 + dz)), "rosca": P((0.0, YP, 0.37 + dz)), "anillo": P((0.11, YP, 0.27 + dz))}

if __name__ == "__main__":
    run("sifon", build, pose, anchors)
