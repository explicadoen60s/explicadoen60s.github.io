# «¿Cuánta batería pierde tu móvil lleno cada noche?» (formato A, error común)
# Dormitorio de maqueta (1 unidad = 1 m) sobre una isla cortada (tarima, hormigón, tierra): cama, mesilla con el móvil
# cargando (cable al enchufe de la pared) y, en el suelo, una celda de la batería gigante en corte (cantos crema):
# cátodo (rojo) a la izquierda, separador blanco, ánodo de grafito (gris oscuro) a la derecha y electrolito azul claro.
# Los iones de litio (bolitas amarillas) pasan al grafito al cargar y se apretujan al 100 %; el electrolito se mancha.
# Al lado, un voltímetro con aguja (4,0 → 4,2 V), una segunda celda para comparar y dos barras de capacidad.
# Planos (fotografía → motion; esquina libre arriba-izquierda, que ocupa el mini del juego desde 2,6 s):
#  0,0 pantalla del móvil con la batería llenándose y el cable conectado, en primer plano · 2,9 dormitorio · 6,1 enchufe
#  8,4 pantalla al 100 · 11,4 celda apretada · 15,3 dormitorio (365 noches) · 18,2 litio contra el grafito · 21 voltímetro
#  24,6 electrolito manchado · 28 dos celdas · 33,9 celda de 4 V · 36,1 plano amplio · 38 barras de capacidad (revelación)
#  42,7 celda al 40 % · 46 calor · 52,1 móvil bajo la almohada · 54,4 ajustes: límite al 80 % · 60,5 cierre
#  67,2 vuelta al primer plano de la pantalla.
import bpy, math, sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from modelos import *
from maqueta import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("bateria100")
NEGRO = (0.12, 0.13, 0.16); PANT = (0.20, 0.26, 0.40); VERDE = (0.30, 0.85, 0.45); LITIO = (1.0, 0.82, 0.18)
CATODO = (0.85, 0.35, 0.30); GRAFITO = (0.30, 0.31, 0.34); ELEC = (0.70, 0.88, 0.97); SEP = (0.97, 0.97, 0.97)
PH = Vector((0.55, 0.45, 0.515))                 # móvil sobre la mesilla
C1 = Vector((1.45, 0.25, 0.0)); C2 = Vector((2.25, 0.25, 0.0))   # celdas gigantes
CW, CH = 0.5, 0.7
N_LI = 36

def back(x):
    x = max(0.0, min(1.0, x)); c = 1.70158; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

def carga(t):
    """porcentaje de la pantalla (0..1)"""
    if t < T("lo enchufas"): return mix(0.55, 0.85, seg(t, 0.0, 2.5))
    if t < T("y ahora ya sabes") - 0.3:
        c = keyed(t, [(T("lo enchufas"), 0.3), (T("las dos"), 0.75), (T("ya está al"), 1.0)])
        if t > T("abre ahora"): c = mix(1.0, 0.8, seg(t, T("el límite"), T("ochenta por", fin=True)))
        return c
    return mix(0.55, 0.85, seg(t, T("y ahora ya sabes") - 0.3, DUR))

def volt(t):
    return keyed(t, [(0, 3.7), (T("cuanto más"), 3.8), (T("más tensión"), 4.2), (T("en laboratorio"), 4.2)])

def daño(t):
    return seg(t, T("esa tensión"), T("el electrolito", fin=True)) * (1 - seg(t, T("en laboratorio"), T("en laboratorio") + 0.4)) \
        + 0.8 * seg(t, T("a sesenta"), T("tres meses", fin=True)) * (1 - seg(t, T("así que no la"), T("así que no la") + 0.4))

def build():
    sc, cam = scene_setup(world=PAL["cielo"], shadow=0.25, light_rot=55); entorno_claro(sc)
    S = {"cam": cam}
    nubes(9, (0.5, 6, 3.4), 6, 1.0, 1.0, s=1.1, seed=6)
    isla(3.8, 2.4, (0.8, 0.5, 0.0), capas=[(PAL["madera"], 0.06), (PAL["hormigon"], 0.16), (PAL["tierra"], 0.3), (PAL["tierra2"], 0.34)])
    for k in range(11): box((0.008, 2.4, 0.004), (-1.0 + k * 0.34, 0.5, 0.002), (0.74, 0.52, 0.30))
    box((3.8, 0.1, 2.2), (0.8, 1.65, 1.1), (0.80, 0.86, 0.96)); box((3.8, 0.102, 0.03), (0.8, 1.65, 2.185), PAL["corte"])
    caja((0.7, 0.06, 0.6), (-0.4, 1.59, 1.45), (0.62, 0.82, 0.95), r=0.03)
    cama((-0.45, 0.75, 0.0), 1.0, rot=0.0, manta=(0.55, 0.70, 0.95))
    caja((0.5, 0.42, 0.5), (PH.x, PH.y + 0.02, 0.25), PAL["madera"], r=0.03)                 # mesilla
    caja((0.44, 0.02, 0.08), (PH.x, PH.y - 0.2, 0.36), (0.80, 0.56, 0.32), r=0.01)
    cilindro(0.08, 0.3, (PH.x + 0.15, PH.y + 0.12, 0.65), (0.98, 0.92, 0.70), r=0.02)       # lámpara
    alfombrilla((0.4, 0.0, 0.005), 1.1, 0.6, color=PAL["rosa"])
    caja((0.08, 0.02, 0.1), (PH.x + 0.1, 1.59, 0.35), (0.96, 0.96, 0.96), r=0.01)            # enchufe de la pared
    planta((-1.3, 1.3, 0.0), 1.4)
    S["almohada"] = caja((0.42, 0.28, 0.12), LEJOS, (0.98, 0.98, 0.98), r=0.05)
    # móvil (pantalla con el icono de la batería que se llena)
    S["movil"] = mv = empty(PH); mv.rotation_mode = 'XYZ'
    caja((0.08, 0.165, 0.009), (0, 0, 0), NEGRO, mv, r=0.008)
    caja((0.072, 0.155, 0.002), (0, 0, 0.005), PANT, mv, r=0.005)
    caja((0.03, 0.06, 0.002), (0, 0.0, 0.0065), (0.85, 0.87, 0.9), mv, r=0.003)             # marco del icono
    caja((0.012, 0.006, 0.002), (0, 0.033, 0.0065), (0.85, 0.87, 0.9), mv, r=0.001)
    S["nivel"] = box((0.024, 1.0, 0.0022), (0, 0, 0.0072), VERDE, mv, unique=True)
    S["limite"] = box((0.034, 0.002, 0.0025), LEJOS, PAL["rojo"], mv, unique=True)           # marca del 80 %
    S["ajuste"] = empty(LEJOS, mv)
    caja((0.06, 0.03, 0.002), (0, 0, 0), (0.95, 0.95, 0.97), S["ajuste"], r=0.004)
    S["bolita_aj"] = cilindro(0.008, 0.002, (-0.015, 0, 0.0015), VERDE, S["ajuste"], unique=True)
    S["cable"] = [tubo([(PH.x - 0.0, PH.y - 0.08, 0.512), (PH.x, PH.y - 0.16, 0.51), (PH.x + 0.12, PH.y - 0.2, 0.505),
                        (PH.x + 0.25, PH.y + 0.3, 0.505), (PH.x + 0.12, 1.55, 0.45), (PH.x + 0.1, 1.58, 0.35)], 0.004, (0.95, 0.95, 0.96))]
    S["clavija"] = caja((0.012, 0.022, 0.006), LEJOS, (0.85, 0.86, 0.88), r=0.002)
    # celdas gigantes en corte
    def celda(c0, nombre):
        e = empty(c0)
        caja((CW + 0.04, 0.16, 0.03), (0, 0, 0.015), (0.62, 0.64, 0.68), e, r=0.01)               # base
        caja((CW + 0.04, 0.02, CH), (0, 0.07, CH / 2 + 0.03), (0.75, 0.77, 0.80), e, r=0.01)      # funda (fondo)
        caja((0.02, 0.16, CH), (-CW / 2 - 0.01, 0, CH / 2 + 0.03), (0.75, 0.77, 0.80), e, r=0.005)
        caja((0.02, 0.16, CH), (CW / 2 + 0.01, 0, CH / 2 + 0.03), (0.75, 0.77, 0.80), e, r=0.005)
        caja((CW + 0.04, 0.16, 0.02), (0, 0, CH + 0.04), (0.75, 0.77, 0.80), e, r=0.005)
        for x in (-CW / 2 - 0.01, CW / 2 + 0.01): caja((0.022, 0.006, CH), (x, -0.08, CH / 2 + 0.03), PAL["corte"], e)
        caja((0.16, 0.12, CH - 0.04), (-0.16, 0.0, CH / 2 + 0.03), CATODO, e, r=0.01)
        caja((0.012, 0.12, CH - 0.04), (0.0, 0.0, CH / 2 + 0.03), SEP, e, r=0.003)
        an = caja((0.16, 0.12, CH - 0.04), (0.16, 0.0, CH / 2 + 0.03), GRAFITO, e, r=0.01)
        for k in range(8): caja((0.16, 0.122, 0.006), (0.16, 0.0, 0.1 + k * 0.08), (0.42, 0.43, 0.46), e)   # capas de grafito
        el = [caja((0.07, 0.12, CH - 0.04), (sx * 0.042, 0.002, CH / 2 + 0.03), ELEC, e, r=0.005, unique=True) for sx in (-1, 1)]
        for sx, col in ((-1, PAL["rojo"]), (1, NEGRO)): cilindro(0.025, 0.05, (sx * 0.15, 0, CH + 0.075), col, e, r=0.008)
        return e, el
    S["c1"], S["el1"] = celda(C1, "c1"); S["c2"], S["el2"] = celda(C2, "c2")
    S["li"] = [sph(0.016, LEJOS, LITIO, seg=12) for _ in range(N_LI)]
    S["li2"] = [sph(0.016, LEJOS, LITIO, seg=12) for _ in range(N_LI // 2)]
    S["manchas"] = [bola(0.012, LEJOS, (0.35, 0.30, 0.25), sub=1) for _ in range(14)]
    S["calor"] = [flecha3d(LEJOS, (0, 0, 1), 0.18, 0.012) for _ in range(3)]
    # voltímetro
    S["vm"] = empty((C1.x - 0.42, C1.y - 0.05, 0.0))
    caja((0.24, 0.08, 0.24), (0, 0, 0.12), (0.98, 0.80, 0.25), S["vm"], r=0.03)
    cilindro(0.09, 0.01, (0, -0.042, 0.13), (0.98, 0.98, 0.96), S["vm"], rot=(math.pi / 2, 0, 0))
    for k in range(7):
        a = math.radians(150 - k * 20)
        caja((0.004, 0.004, 0.018), (0.075 * math.cos(a), -0.048, 0.13 + 0.075 * math.sin(a)), (0.3, 0.3, 0.33) if k < 5 else PAL["rojo"], S["vm"], rot=(0, math.pi / 2 - a, 0))
    S["aguja"] = empty((C1.x - 0.42, C1.y - 0.05 - 0.05, 0.13)); S["aguja"].rotation_mode = 'XYZ'
    caja((0.004, 0.004, 0.07), (0, 0, 0.035), PAL["rojo"], S["aguja"])
    for k in range(2): cilindro(0.003, 0.25, (C1.x - 0.42 + (0.04 if k else -0.04), C1.y - 0.04, 0.2), (0.2, 0.2, 0.2) if k else PAL["rojo"])
    # barras de capacidad (verdes, junto a cada celda)
    S["barras"] = [box((0.06, 0.06, 1.0), LEJOS, VERDE, unique=True) for _ in range(2)]
    S["marcos"] = [caja((0.08, 0.075, 0.62), LEJOS, (0.85, 0.87, 0.9), r=0.01) for _ in range(2)]
    dyn = [cam, S["almohada"], S["movil"], S["clavija"], S["c2"], S["el1"], S["el2"], S["li"], S["li2"], S["manchas"], S["calor"],
           S["aguja"], S["barras"], S["marcos"]]
    join_static(dyn)
    return sc, S

def pose(t, S):
    c = carga(t)
    S["nivel"].scale = (0.024, max(0.054 * c, 0.001), 0.0022); S["nivel"].location = (0, -0.027 + 0.027 * c, 0.0072)
    set_color(S["nivel"], VERDE if c > 0.2 else PAL["rojo"])
    lim = seg(t, T("el límite"), T("ochenta por", fin=True)) * (t < T("y ahora ya sabes") - 0.3)
    S["limite"].location = (0, -0.027 + 0.054 * 0.8, 0.0078) if lim > 0.01 else LEJOS
    aj = win01(t, T("abre ahora") - 0.1, T("te has acercado"), 0.3, 0.3)
    S["ajuste"].location = (0, -0.05, 0.0075) if aj > 0.01 else LEJOS
    S["bolita_aj"].location = (-0.015 + 0.03 * seg(t, T("y activa"), T("y activa") + 0.4), 0, 0.0015)
    # móvil: en la mesilla; bajo la almohada en la cama
    alm = win01(t, T("así que no la") - 0.2, T("qué haces"), 0.4, 0.3)
    p_cama = Vector((-0.45, 1.05, 0.56))
    S["movil"].location = PH.lerp(p_cama, alm); S["movil"].rotation_euler = (0, 0, 0)
    S["almohada"].location = p_cama + Vector((0, 0, 0.07 + 0.25 * (1 - seg(t, T("bajo la"), T("almohada", fin=True))))) if alm > 0.5 else LEJOS
    # clavija: entra al enchufarlo
    en = seg(t, T("lo enchufas") - 0.1, T("lo enchufas") + 0.4) if t < T("y ahora ya sabes") - 0.3 else 1.0
    if t < T("lo enchufas") - 0.1: en = 1.0
    S["clavija"].location = S["movil"].location + Vector((0, -0.088 - 0.06 * (1 - en), 0.0))
    # litio: en el cátodo cuando la carga es baja; pasa al grafito al cargar; al 100 % apretado y temblando
    full = c; ap = win01(t, T("y se queda"), T("cuanto más") + 1.5, 0.3, 0.5) + 0.7 * win01(t, T("dentro,"), T("cuanto más"), 0.3, 0.3)
    rnd = random.Random(2)
    for k, b in enumerate(S["li"]):
        cx, cz = rnd.uniform(-0.06, 0.06), rnd.uniform(0.08, CH - 0.05)
        cruza = k < N_LI * full
        x = C1.x + (0.16 if cruza else -0.16) + cx
        if cruza: x = C1.x + 0.16 + cx * (1 - 0.4 * ap)
        jit = 0.006 * ap * math.sin(t * 30 + k)
        if abs(t - (T("las dos") + (k / N_LI) * 2.5)) < 0.4 and cruza:   # cruzando el separador
            x = C1.x + mix(-0.16, 0.16, (t - (T("las dos") + (k / N_LI) * 2.5) + 0.4) / 0.8)
        b.location = (x + jit, C1.y - 0.065, cz + jit)
    # celda 2 (comparación): visible desde el laboratorio hasta el calor
    v2 = 1.0 if T("en laboratorio") - 0.2 < t < T("así que no la") else 0.0
    S["c2"].location = C2 if v2 else LEJOS
    for k, b in enumerate(S["li2"]):
        if not v2: b.location = LEJOS; continue
        r2 = random.Random(k); n_in = 0.75 if t < T("guardada al") else 0.4
        cr = k < len(S["li2"]) * n_in
        b.location = (C2.x + (0.16 if cr else -0.16) + r2.uniform(-0.06, 0.06), C2.y - 0.065, r2.uniform(0.08, CH - 0.05))
    # electrolito que se mancha (tensión alta, calor) y aguja del voltímetro
    d = daño(t); rm = random.Random(8)
    for k, m in enumerate(S["manchas"]):
        on = k < 14 * d
        m.location = (C1.x + rm.choice((-0.04, 0.04)) + rm.uniform(-0.02, 0.02), C1.y - 0.064, rm.uniform(0.1, CH - 0.05)) if on else LEJOS
    for e in S["el1"]: set_color(e, tuple(mix(a, b, 0.55 * d) for a, b in zip(ELEC, (0.62, 0.58, 0.45))))
    S["aguja"].rotation_euler = (0, math.radians(60 - (volt(t) - 3.6) / 0.6 * 100), 0)
    # calor (60 °C): flechas rojas que suben y celda que se pone roja
    hot = win01(t, T("pero ojo"), T("así que no la") + 0.4, 0.3, 0.4) + win01(t, T("bajo la"), T("qué haces"), 0.3, 0.3)
    for k, f in enumerate(S["calor"]):
        base = (S["movil"].location + Vector((-0.06 + 0.06 * k, 0, 0.05))) if t > T("así que no la") else (C1 + Vector((-0.18 + 0.18 * k, -0.1, CH + 0.12)))
        f.location = base + Vector((0, 0, 0.04 * ((t * 1.6 + k * 0.3) % 1.0))) if hot > 0.01 else LEJOS
        f.scale = (max(hot, 0.01) * (0.6 if t > T("así que no la") else 1),) * 3
    # barras de capacidad (100 → 80 llena; 100 → 96 al 40 %; 100 → 60 a 60 °C)
    vb = T("una celda guardada") - 0.2 < t < T("así que no la")
    caps = (keyed(t, [(T("pierde un"), 1.0), (T("de capacidad", fin=True), 0.8), (T("a sesenta"), 0.8), (T("al sesenta", fin=True) + 0.6, 0.6)]),
            keyed(t, [(T("pierde solo"), 1.0), (T("un cuatro", fin=True), 0.96)]))
    for i, (bar, mar) in enumerate(zip(S["barras"], S["marcos"])):
        cc = (C1, C2)[i]
        if vb and (i == 0 or t > T("guardada al") - 0.2):
            h = 0.6 * caps[i]; bar.location = (cc.x + CW / 2 + 0.09, cc.y - 0.02, h / 2 + 0.01); bar.scale = (0.06, 0.06, h)
            mar.location = (cc.x + CW / 2 + 0.09, cc.y + 0.01, 0.31)
            set_color(bar, VERDE if caps[i] > 0.85 else ((1.0, 0.70, 0.2) if caps[i] > 0.7 else PAL["rojo"]))
        else: bar.location = LEJOS; mar.location = LEJOS
    apply_cam(S["cam"], *cam_lin(t, CAM(), drift=0.004))

PANTALLA = tuple(PH); CEL = (C1.x, C1.y, 0.42); DOS = ((C1.x + C2.x) / 2, C1.y, 0.4); TODO = (0.9, 0.5, 0.5)

def CAM():
    k = Claves(); add = k.add
    ini = V(PANTALLA, (0.06, -0.22, 0.2), 36)
    add(0.0, V(PANTALLA, (0.05, -0.18, 0.17), 38)); add(1.8, ini)
    add(T("escribe"), V(TODO, (-0.4, -2.0, 0.9), 28))
    add(T("lo enchufas") - 0.1, V(PANTALLA, (0.15, -0.35, 0.18), 36))
    add(T("las dos"), V(PANTALLA, (-0.02, -0.17, 0.2), 40), hold=T("y se queda") - T("las dos") - 0.12)
    add(T("y se queda"), V(CEL, (-0.25, -1.0, 0.25), 34))
    add(T("apretado"), V((C1.x + 0.16, C1.y, 0.4), (0.1, -0.55, 0.12), 38))
    add(T("y lo repites"), V((1.0, 0.4, 0.4), (0.3, -1.6, 0.6), 30))
    add(T("dentro,"), V((C1.x + 0.05, C1.y, 0.45), (-0.15, -0.65, 0.1), 38))
    add(T("cuanto más"), V((C1.x - 0.3, C1.y, 0.3), (0.05, -0.75, 0.15), 36))
    add(T("esa tensión"), V((C1.x, C1.y, 0.4), (0.1, -0.6, 0.05), 40))
    add(T("en laboratorio"), V(DOS, (0.0, -1.5, 0.35), 32))
    add(T("a cuatro coma"), V((C1.x - 0.15, C1.y, 0.35), (-0.15, -0.95, 0.2), 34))
    add(T("con cuatro"), V((C2.x, C2.y, 0.4), (0.2, -0.95, 0.2), 34))
    add(T("y aquí viene"), V(TODO, (-0.5, -3.0, 1.2), 28))
    add(T("una celda guardada"), V((C1.x + 0.15, C1.y, 0.35), (-0.1, -1.0, 0.25), 34))
    add(T("guardada al"), V((C2.x + 0.1, C2.y, 0.35), (0.1, -1.0, 0.25), 34))
    add(T("pero ojo"), V(CEL, (-0.3, -1.1, 0.3), 32))
    add(T("una celda llena") + 0.2, V((C1.x + 0.15, C1.y, 0.35), (0.15, -0.85, 0.2), 36))
    add(T("así que no la"), V((-0.45, 1.05, 0.6), (0.4, -0.9, 0.45), 32))
    add(T("qué haces") - 0.1, V(PANTALLA, (0.12, -0.3, 0.22), 36))
    add(T("y activa"), V(PANTALLA, (0.0, -0.16, 0.2), 40))
    add(T("ochenta por"), V(PANTALLA, (-0.06, -0.18, 0.18), 40))
    add(T("te has acercado"), V(TODO, (0.6, -2.9, 1.2), 28))
    add(T("y si quieres"), V(CEL, (-0.2, -1.2, 0.35), 32))
    add(T("lo más pedido"), V(TODO, (-0.6, -2.8, 1.1), 28))
    add(T("sígueme"), V(PANTALLA, (0.3, -0.5, 0.35), 32))
    add(T("y ahora ya sabes") - 0.2, V(PANTALLA, (0.05, -0.18, 0.17), 38))
    add(DUR - 0.8, ini)
    add(DUR + 1, ini)
    return k.k

def anchors(sc, S, t):
    cam = S["cam"]; P = lambda v: proj(sc, cam, v); m = S["movil"].location
    return {"movil": P(m + Vector((0, 0, 0.03))), "celda": P(C1 + Vector((0, 0, CH + 0.12))), "celda2": P(C2 + Vector((0, 0, CH + 0.12))),
            "grafito": P(C1 + Vector((0.16, -0.07, 0.5))), "vm": P((C1.x - 0.42, C1.y, 0.3)), "cama": P((-0.45, 1.05, 0.8)),
            "barra1": P((C1.x + CW / 2 + 0.09, C1.y, 0.68)), "barra2": P((C2.x + CW / 2 + 0.09, C2.y, 0.68)), "elec": P(C1 + Vector((0, -0.07, 0.4)))}

if __name__ == "__main__":
    run("bateria100", build, pose, anchors)
