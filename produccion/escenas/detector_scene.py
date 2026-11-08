# «Si tuvieras que inventar el detector de humo…»: primer plano de la cámara óptica con humo entrando y el haz del led
# rebotando en las partículas; luego se construye pieza a pieza (en corte, tapa levantada): base y pared con rendijas,
# aire entrando, cámara negra en laberinto, led que parpadea, sensor (primero enfrente ✗, luego en ángulo) y pared
# separadora; con aire limpio el haz va recto a la trampa; el humo dispersa la luz hacia el sensor; sirena piezoeléctrica
# con ondas; polvo e insecto que también reflejan, malla fina que frena al insecto; pila de 9 V que se agota, pitidos
# cortos, cambio de pila y pila sellada de diez años; al final la tapa baja y el detector se cierra.
import bpy, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("detector")
BG = (0.07, 0.06, 0.13); WHITE = (0.93, 0.93, 0.9); WHITE2 = (0.8, 0.8, 0.78); BLACK = (0.06, 0.06, 0.07); PCB = (0.12, 0.35, 0.22)
LEDON = (1.0, 0.28, 0.3); LEDOFF = (0.35, 0.1, 0.12); RAY = (1.0, 0.55, 0.5); SMOKE = (0.62, 0.62, 0.66); AIR = (0.45, 0.8, 1.0)
SENW = (0.25, 0.4, 0.75); SENON = (0.6, 0.9, 1.0); BRASS = (0.85, 0.65, 0.3); MESH = (0.7, 0.72, 0.76); BUG = (0.22, 0.14, 0.08)
DUST = (0.55, 0.4, 0.25); FLAME = (1.0, 0.55, 0.1); FLAME2 = (1.0, 0.9, 0.35)
LEJOS = (0, 0, -900)
YCUT = -1.2                      # lo que queda delante de este plano está cortado (se ve el interior)
ZC = 2.5                         # altura del haz
LED_A, SEN_A, SEN_A0, TRAP_A, WALL_A = 170, 50, 350, 350, 110
RIN = 4.2
SIREN = Vector((-6.06, -4.24, 1.0)); BATT = Vector((5.23, -5.23, 1.0)); FLM = Vector((-24, -4, -3))
RNG = random.Random(11)

def P(a, r, z=ZC): a = math.radians(a); return Vector((r * math.cos(a), r * math.sin(a), z))
LED_TIP = P(LED_A, 3.6); TRAP = P(TRAP_A, 4.55)

def alpha(o, a):
    m = o.active_material; m.diffuse_color = (*m.diffuse_color[:3], a); m.surface_render_method = 'BLENDED'
def show(o, on):
    o.hide_render = not on
    for c in o.children: show(c, on)
def grow(o, u, base=1.0):
    u = max(u, 0.001); o.scale = (base * u, base * u, base * u)
def hide_bar(o): bar_set(o, LEJOS, Vector(LEJOS) + Vector((0, 0, 0.01)))
def poly(pts, u):
    Pt = [Vector(p) for p in pts]; L = [(b - a).length for a, b in zip(Pt, Pt[1:])]; s = u * sum(L)
    for a, b, l in zip(Pt, Pt[1:], L):
        if s <= l: return a.lerp(b, s / max(l, 1e-6))
        s -= l
    return Pt[-1]
def arrow(col, r=0.18):
    e = empty(LEJOS)
    cyl(r, 2.0, (0, 0, 1.0), col, parent=e, v=10)
    bpy.ops.mesh.primitive_cone_add(radius1=r * 2.6, radius2=0, depth=1.0, location=(0, 0, 2.4), vertices=14); setup(bpy.context.object, col, parent=e)
    return e
def aim(o, p, d, s=1.0):
    o.location = p; o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(Vector(d).normalized())
    o.scale = (s, s, s)

# humo: recorrido de cada partícula (entra por las rendijas, deambula dentro y sale)
NP = 70
SMK = []
for k in range(NP):
    a0 = RNG.uniform(95, 265); z0 = RNG.uniform(1.6, 3.8)
    pin = P(RNG.uniform(0, 360), RNG.uniform(0.3, 3.6), RNG.uniform(1.5, 3.6))
    pin2 = P(RNG.uniform(0, 360), RNG.uniform(0.3, 3.6), RNG.uniform(1.5, 3.6))
    SMK.append([P(a0, 19, z0), P(a0, 9.8, z0), P(a0 + RNG.uniform(-10, 10), 5.2, z0), pin, pin2, P(RNG.uniform(-75, 75), 16, z0 + 1)])
NB = 9
BEAMP = [(0.12 + 0.76 * k / (NB - 1) + RNG.uniform(-0.03, 0.03), RNG.uniform(-0.25, 0.25), RNG.uniform(-0.25, 0.25), RNG.random() * 6) for k in range(NB)]
RAYD = [[Vector((RNG.uniform(-1, 1), RNG.uniform(-1, 1), RNG.uniform(-0.7, 0.7))).normalized() for _ in range(4)] for _ in range(NB)]
FSM = [(RNG.uniform(-2, 2), RNG.uniform(-2, 2), RNG.random()) for _ in range(26)]

def smoke_density(t):
    if t < T("vamos"): return 1.0
    d = 0.0
    a = T("cuando entra")
    d = keyed(t, [(a - 0.2, 0.0), (a + 1.0, 0.45), (T("cuanto más"), 0.5), (T("límite"), 1.0), (T("curioso") - 0.4, 1.0), (T("curioso") + 0.8, 0.0)])
    if t > T("sígueme") - 0.3: d = 0.5 * seg(t, T("sígueme") - 0.3, T("sígueme") + 0.6)
    return d

def glint(t):
    """número de partículas de humo dentro del haz (0..1)"""
    if t < T("vamos"): return 1.0
    a = T("choca")
    g = keyed(t, [(a - 0.3, 0.0), (a + 0.3, 0.45), (T("cuanto más"), 0.45), (T("más luz") + 0.2, 0.75), (T("límite"), 1.0), (T("curioso") - 0.4, 1.0), (T("curioso") + 0.6, 0.0)])
    if t > T("sígueme"): g = 0.6
    return g

LIMITE = 0.65
def lum(t):
    """luz que llega al sensor (0..1), la misma que enseña el medidor"""
    v = keyed(t, [(0, 0.0), (T("una parte") - 0.2, 0.0), (T("una parte") + 0.5, 0.3), (T("cuanto más"), 0.32), (T("más luz", fin=True) + 0.4, 0.55),
                  (T("límite"), 0.58), (T("salta"), 0.85), (T("curioso") - 0.4, 0.85), (T("curioso") + 0.6, 0.0),
                  (T("el polvo") + 1.0, 0.0), (T("el polvo") + 1.8, 0.72), (T("mide") + 0.9, 0.72), (T("mide") + 2.0, 0.05)])
    if t < T("vamos"): v = 0.8
    return v

def beam_on(t):
    if t < T("vamos") - 0.1: return True
    if t < T("a ratos") - 0.4: return False
    if t < T("con el aire"):                     # parpadeo «a ratos»
        return (t - T("a ratos") + 0.4) % 1.1 < 0.45
    if T("el polvo") - 0.4 < t < T("se acaba") and t > T("mide") - 0.2:
        return (t - T("mide") + 0.2) % 0.7 < 0.3   # mide varias veces
    if t > T("se acaba") and t < T("algunos"):
        return (t % 1.2) < 0.5 and t < T("no puede avisarte") - 0.6 or t > T("cambias") + 0.6
    return True

def sen_angle(t):
    return keyed(t, [(0, SEN_A + 360), (T("un sensor") - 0.5, SEN_A0), (T("en ángulo") - 0.1, SEN_A0), (T("en ángulo") + 0.9, SEN_A + 360)])

def build():
    sc, cam = scene_setup(world=BG, shadow=0.38, light_rot=60)
    S = {"cam": cam}
    # base (siempre presente: es el soporte de techo)
    cyl(10.2, 1.0, (0, 0, 0.5), WHITE)
    cyl(10.4, 0.3, (0, 0, 0.15), WHITE2)
    # pared con rendijas (mitad trasera) y mitad delantera (solo al final)
    S["pared"] = empty((0, 0, 0)); S["frente"] = empty((0, 0, 0))
    for k in range(40):
        a = k * 9 + 4.5; p = P(a, 9.75, 2.8)
        par = S["pared"] if p.y > YCUT else S["frente"]
        box((1.15, 0.5, 3.6), (p.x, p.y, 2.8), WHITE, parent=par, rot=(0, 0, math.radians(a + 90)))
    for par, sgn in ((S["pared"], 1), (S["frente"], -1)):
        for k in range(20):
            a0 = (k * 9 if sgn > 0 else 180 + k * 9)
            q0, q1 = P(a0, 9.75, 4.75), P(a0 + 9, 9.75, 4.75)
            o = bar_obj(WHITE, 0.3, parent=par); bar_set(o, q0, q1)
    # tapa (levantada, en explosión) con su piloto rojo y el botón
    S["tapa"] = empty((0, 0, 14))
    cyl(10.3, 0.9, (0, 0, 0), WHITE, parent=S["tapa"]); cyl(7.0, 0.7, (0, 0, 0.75), WHITE, parent=S["tapa"])
    for k in range(6): torus(3.2 + k * 0.9 if k < 2 else 8.0 + (k - 2) * 0.55, 0.12, (0, 0, 0.47 if k >= 2 else 1.12), WHITE2, parent=S["tapa"])
    cyl(1.4, 0.4, (-3.5, -3.0, 1.15), WHITE2, parent=S["tapa"])
    S["piloto"] = sph(0.45, (3.0, -3.2, 1.15), LEDOFF, parent=S["tapa"], unique=True)
    # cámara oscura: suelo negro, laberinto de aletas (mitad trasera)
    S["camara"] = empty((0, 0, 0))
    cyl(5.3, 0.2, (0, 0, 1.1), BLACK, parent=S["camara"])
    for k in range(18):
        a = k * 20 + 10; p = P(a, 4.95, 2.6)
        if p.y < YCUT and a != TRAP_A + 10: continue
        box((1.9, 0.3, 3.0), (p.x, p.y, 2.6), BLACK, parent=S["camara"], rot=(0, 0, math.radians(a + 90 + 35)))
    box((0.6, 0.6, 3.0), tuple(P(TRAP_A, 4.95, 2.6)), BLACK, parent=S["camara"], rot=(0, 0, math.radians(TRAP_A)))  # trampa de luz
    # led
    S["led"] = empty(P(LED_A, 4.25)); S["led"].rotation_euler = (0, 0, math.radians(LED_A + 180))
    cyl(0.55, 1.0, (0, 0, 0), (0.15, 0.15, 0.17), parent=S["led"], rot=(0, math.pi / 2, 0))
    S["ledbulb"] = sph(0.5, (0.55, 0, 0), LEDOFF, parent=S["led"], scale=(1.1, 1, 1), unique=True)
    for dz in (-0.25, 0.25):
        o = bar_obj((0.75, 0.75, 0.75), 0.07, parent=S["led"]); bar_set(o, (-0.4, 0, dz), (-1.6, 0, dz - 1.1)); o.location = (-0.4, 0, dz)
    # sensor (fotodiodo)
    S["sensor"] = empty(P(SEN_A0, 4.3))
    box((0.7, 1.4, 1.4), (0, 0, 0), (0.18, 0.18, 0.22), parent=S["sensor"])
    S["senwin"] = box((0.12, 1.0, 1.0), (0.38, 0, 0), SENW, parent=S["sensor"], unique=True)
    # pared separadora
    a = math.radians(WALL_A); S["sep"] = box((3.2, 0.3, 2.8), tuple(P(WALL_A, 3.3, 2.5)), (0.12, 0.12, 0.14), rot=(0, 0, a))
    # haz y rayos dispersados
    S["haz"] = bar_obj(LEDON, 0.26, unique=True)
    S["bp"] = [sph(0.26, LEJOS, SMOKE, seg=10, unique=True) for _ in range(NB)]
    S["rays"] = [[bar_obj(RAY, 0.055) for _ in range(4)] for _ in range(NB)]
    S["tosen"] = [bar_obj(SENON, 0.08) for _ in range(NB)]
    # humo
    S["humo"] = [sph(RNG.uniform(0.28, 0.45), LEJOS, SMOKE, seg=10) for _ in range(NP)]
    S["aire"] = [arrow(AIR) for _ in range(7)]
    # fuego lejano (antes que el fuego)
    S["fuego"] = empty(FLM); f = S["fuego"]
    box((3.5, 1.2, 1.2), (0, 0, -0.6), (0.3, 0.15, 0.08), parent=f, rot=(0, 0, 0.4)); box((3.2, 1.1, 1.1), (0, 0, -0.6), (0.35, 0.18, 0.1), parent=f, rot=(0, 0, -0.5))
    S["llamas"] = []
    for k, (dx, h, c) in enumerate(((0, 2.4, FLAME), (-0.8, 1.6, FLAME), (0.8, 1.8, FLAME), (0, 1.3, FLAME2))):
        bpy.ops.mesh.primitive_cone_add(radius1=0.6 if k < 3 else 0.4, radius2=0, depth=h, location=(dx, -0.2 * (k == 3), h / 2), vertices=16)
        o = setup(bpy.context.object, c, parent=f); S["llamas"].append(o)
    S["fhumo"] = [sph(RNG.uniform(0.7, 1.2), LEJOS, SMOKE, seg=10) for _ in FSM]
    # sirena piezoeléctrica y ondas
    S["sirena"] = empty(SIREN); s = S["sirena"]
    cyl(2.3, 0.9, (0, 0, 0.45), (0.15, 0.15, 0.17), parent=s); cyl(1.9, 0.12, (0, 0, 0.95), BRASS, parent=s)
    S["piezo"] = cyl(1.25, 0.14, (0, 0, 1.05), (0.95, 0.95, 0.92), parent=s, unique=True)
    S["ondas"] = [torus(1, 0.03, LEJOS, (1.0, 0.85, 0.4), unique=True) for _ in range(5)]
    # polvo, insecto y malla
    S["polvo"] = [box((0.32, 0.26, 0.22), LEJOS, DUST, rot=(RNG.random(), RNG.random(), RNG.random())) for _ in range(3)]
    S["bicho"] = empty(LEJOS); b = S["bicho"]
    sph(0.55, (0, 0, 0), BUG, parent=b, scale=(1.7, 0.9, 0.8)); sph(0.35, (1.05, 0, 0.05), BUG, parent=b)
    for dx in (-0.4, 0.15, 0.6):
        for sy in (-1, 1):
            o = bar_obj(BUG, 0.05, parent=b); bar_set(o, (dx, sy * 0.3, -0.1), (dx + 0.2, sy * 1.0, -0.6)); o.location = (dx, sy * 0.3, -0.1)
    S["alas"] = [sph(0.5, (-0.2, sy * 0.45, 0.45), (0.85, 0.9, 1.0), parent=b, scale=(1.4, 0.7, 0.12)) for sy in (-1, 1)]
    for o in S["alas"]: alpha(o, 0.55)
    S["malla"] = empty((0, 0, 0)); m = S["malla"]
    for k in range(37):
        a = -10 + k * 5.55; p0, p1 = P(a, 6.0, 1.1), P(a, 6.0, 4.1)
        o = bar_obj(MESH, 0.045, parent=m); bar_set(o, p0, p1)
    for z in (1.4, 2.0, 2.6, 3.2, 3.8):
        for k in range(18):
            a = -10 + k * 11.1; o = bar_obj(MESH, 0.04, parent=m); bar_set(o, P(a, 6.0, z), P(a + 11.1, 6.0, z))
    # pila de 9 V y pila sellada
    S["pila"] = empty(BATT); pl = S["pila"]; pl.rotation_euler = (0, 0, math.radians(45))
    S["pilac"] = box((6.6, 2.5, 3.6), (0, 0, 1.8), (0.2, 0.22, 0.26), parent=pl, unique=True)
    box((6.62, 2.52, 0.9), (0, 0, 3.2), (0.85, 0.6, 0.25), parent=pl)
    cyl(0.45, 0.6, (-1.4, 0, 3.9), (0.8, 0.8, 0.82), parent=pl, v=12)
    cyl(0.5, 0.6, (1.4, 0, 3.9), (0.8, 0.8, 0.82), parent=pl, v=6)
    S["pila2"] = empty(LEJOS); p2 = S["pila2"]; p2.rotation_euler = (0, 0, math.radians(45))
    cyl(1.35, 6.4, (0, 0, 1.35), (0.78, 0.8, 0.84), parent=p2, rot=(0, math.pi / 2, 0))
    cyl(0.5, 0.5, (3.4, 0, 1.35), (0.6, 0.62, 0.66), parent=p2, rot=(0, math.pi / 2, 0))
    box((3.0, 0.1, 1.2), (0, -1.36, 1.35), (0.3, 0.75, 0.45), parent=p2)
    for dx in (-2.6, 2.6):
        o = bar_obj((0.85, 0.6, 0.25), 0.12, parent=p2); bar_set(o, (dx, 0, 0), (dx, 0, 2.8)); o.location = (dx, 0, 0)
    # cables de la placa
    S["placa"] = box((4.0, 2.4, 0.25), (6.5, 2.5, 1.13), PCB, rot=(0, 0, math.radians(-30)))
    dyn = [cam, S["pared"], S["frente"], S["tapa"], S["camara"], S["led"], S["sensor"], S["sep"], S["haz"], S["bp"], S["rays"],
           S["tosen"], S["humo"], S["aire"], S["fuego"], S["fhumo"], S["sirena"], S["ondas"], S["polvo"], S["bicho"], S["malla"],
           S["pila"], S["pila2"], S["placa"]]
    join_static(dyn)
    return sc, S

# --------------------------------------------------------------------------------------------------
def pose(t, S):
    built = t < T("vamos") - 0.1
    t_caja, t_aire, t_osc, t_led, t_sen = T("así que haces"), T("para que entre"), T("pero a oscuras"), T("dentro pones"), T("un sensor")
    t_sep, t_limp, t_choca, t_parte, t_lim = T("separados"), T("con el aire"), T("choca"), T("una parte"), T("límite")
    t_sir, t_cur, t_polvo, t_malla, t_mide, t_pila, t_camb, t_alg, t_fin = T("así que pones"), T("curioso"), T("el polvo"), T("malla"), T("mide"), T("se acaba"), T("cambias"), T("algunos"), T("sígueme")
    # pared con rendijas
    pw = built or t > t_caja - 0.2
    show(S["pared"], pw); u = 1 if built else seg(t, t_caja - 0.2, t_caja + 0.7)
    S["pared"].scale = (1, 1, max(u, 0.001))
    fr = t > t_fin - 0.1; show(S["frente"], fr); S["frente"].scale = (1, 1, max(seg(t, t_fin - 0.1, t_fin + 0.6), 0.001))
    # tapa: arriba (explosión) y al final baja
    tp = (t_caja + 0.3 < t < t_osc + 0.6) or t > t_fin - 0.6
    show(S["tapa"], tp)
    if t < t_fin - 0.6: z = mix(40, 14, seg(t, t_caja + 0.3, t_caja + 1.2)) + 40 * seg(t, t_osc - 0.3, t_osc + 0.6)
    else: z = mix(40, 5.05, seg(t, t_fin - 0.6, t_fin + 0.5))
    S["tapa"].location = (0, 0, z)
    alarm = (T("salta") - 0.1 < t < t_cur - 0.3) or built
    chirp = (T("suelta") - 0.1 < t < t_camb) and (t - T("suelta")) % 1.6 < 0.25
    on = (alarm and (t * 4) % 1 < 0.5) or chirp or (t > t_fin and (t % 1.5) < 0.15)
    set_color(S["piloto"], LEDON if on else LEDOFF)
    # cámara oscura
    cm = built or t > t_osc - 0.2
    show(S["camara"], cm); S["camara"].scale = (1, 1, max(1 if built else seg(t, t_osc - 0.2, t_osc + 0.6), 0.001))
    # led
    ld = built or t > t_led - 0.2; show(S["led"], ld); grow(S["led"], 1 if built else seg(t, t_led - 0.2, t_led + 0.5))
    bon = beam_on(t) and ld
    set_color(S["ledbulb"], LEDON if bon else LEDOFF)
    # sensor
    sn = built or t > t_sen - 0.5; show(S["sensor"], sn); grow(S["sensor"], 1 if built else seg(t, t_sen - 0.5, t_sen + 0.2))
    sa = sen_angle(t); S["sensor"].location = P(sa, 4.3); S["sensor"].rotation_euler = (0, 0, math.radians(sa + 180))
    w = lum(t) if bon else 0.0
    if abs(sa - SEN_A0) < 8 and bon and t > 5: w = 1.0
    set_color(S["senwin"], tuple(mix(c, d, min(1, w * 1.3)) for c, d in zip(SENW, SENON)))
    sp = built or t > t_sep - 0.2; show(S["sep"], sp)
    S["sep"].scale = (3.2, 0.3, 2.8 * max(1 if built else seg(t, t_sep - 0.2, t_sep + 0.5), 0.001))
    # haz: al sensor si está enfrente; si no, a la trampa
    facing = abs(sa - SEN_A0) < 8 and t > 5
    end = P(sa, 3.9) if facing else TRAP
    if bon: bar_set(S["haz"], LED_TIP, end)
    else: hide_bar(S["haz"])
    # partículas en el haz + rayos
    g = glint(t); nb = int(round(g * NB))
    polvo_on = t_polvo - 0.1 < t < t_pila - 0.6
    tosen = t > t_parte - 0.2 or built
    lit = 0.0
    for k, (u0, dy, dz, ph) in enumerate(BEAMP):
        o = S["bp"][k]; act = k < nb
        if not act:
            o.location = LEJOS
            for r in S["rays"][k]: hide_bar(r)
            hide_bar(S["tosen"][k]); continue
        u = (u0 + 0.03 * math.sin(t * 0.8 + ph)) % 1
        p = LED_TIP.lerp(TRAP, u) + Vector((0, 0, dz + 0.15 * math.sin(t * 1.3 + ph))) + Vector((-0.17, 0.98, 0)) * dy
        o.location = p
        set_color(o, RAY if bon else SMOKE)
        for j, r in enumerate(S["rays"][k]):
            if bon:
                L = 0.9 + 0.7 * (0.5 + 0.5 * math.sin(t * 9 + j * 2 + ph)); bar_set(r, p, p + RAYD[k][j] * L)
            else: hide_bar(r)
        if bon and tosen and k % 2 == 0:
            q = P(sa, 3.95, ZC); bar_set(S["tosen"][k], p, p.lerp(q, 0.92)); lit += 1
        else: hide_bar(S["tosen"][k])
    # polvo dentro del haz (falsa alarma)
    for k, o in enumerate(S["polvo"]):
        if polvo_on:
            u = seg(t, t_polvo - 0.1 + 0.2 * k, t_polvo + 1.4 + 0.2 * k); out = seg(t, t_mide + 0.9 + 0.3 * k, t_mide + 2.2 + 0.3 * k)
            p0 = P(200 + 12 * k, 12, ZC + 0.3 * k); p1 = LED_TIP.lerp(TRAP, 0.35 + 0.15 * k) + Vector((0, 0, 0.1 * k)); p2 = P(-40 + 15 * k, 14, ZC)
            o.location = p0.lerp(p1, u).lerp(p2, out); o.rotation_euler = (t * 2 + k, t * 1.5, 0)
            if bon and out < 0.2 and u > 0.9: set_color(o, RAY)
            else: set_color(o, DUST)
        else: o.location = LEJOS
    # insecto
    bi = T("insecto") - 1.0 < t < t_mide + 1.0
    show(S["bicho"], bi)
    if bi:
        u = seg(t, T("insecto") - 1.0, T("insecto") + 0.6); back = seg(t, t_malla - 0.1, t_malla + 0.9)
        p0, p1, p2 = P(195, 16, ZC + 2), P(185, 2.0, ZC + 0.2), P(182, 6.8, ZC)
        p = p0.lerp(p1, u).lerp(p2, back) + Vector((0, 0, 0.15 * math.sin(t * 12)))
        S["bicho"].location = p
        S["bicho"].rotation_euler = (0, 0, math.radians(5 if back < 0.5 else 185))
        for k, w in enumerate(S["alas"]): w.rotation_euler = ((-1) ** k * 0.5 * math.sin(t * 40), 0, 0)
    # malla
    ml = t > t_malla - 0.3 or (t > t_fin - 0.3) or built
    show(S["malla"], ml); S["malla"].scale = (1, 1, max(1 if (built or t > t_fin) else seg(t, t_malla - 0.3, t_malla + 0.5), 0.001))
    # humo
    d = smoke_density(t); n = int(round(d * NP))
    for k, o in enumerate(S["humo"]):
        if k < n:
            u = (t * 0.07 + k / NP) % 1; o.location = poly(SMK[k], u) + Vector((0, 0, 0.2 * math.sin(t + k)))
        else: o.location = LEJOS
    # aire entrando por las rendijas
    ai = t_aire - 0.2 < t < t_osc + 0.8
    for k, e in enumerate(S["aire"]):
        show(e, ai)
        if ai:
            a = 125 + k * 20; u = (t * 0.6 + k / 7) % 1
            aim(e, P(a, mix(15, 7, u), 2.8), -P(a, 1, 0), 1.2 * seg(t, t_aire - 0.2, t_aire + 0.3))
        else: e.location = LEJOS
    # fuego lejano
    fz = T("quieres") - 0.3 < t < t_caja + 0.6
    show(S["fuego"], fz); S["fuego"].location = FLM if fz else LEJOS; S["fuego"].scale = (2.2, 2.2, 2.2)
    for k, o in enumerate(S["llamas"]): o.scale = (1, 1, 0.75 + 0.3 * math.sin(t * 13 + k * 2.1))
    for k, o in enumerate(S["fhumo"]):
        if fz:
            dx, dy, ph = FSM[k]; u = (t * 0.28 + ph) % 1
            o.location = poly([FLM + Vector((0, 0, 2)), FLM + Vector((dx, dy, 10)), Vector((-14 + dx * 2, dy, 6)), Vector((-2 + dx, dy, 3))], u)
        else: o.location = LEJOS
    # sirena
    sr = built or t > t_sir - 0.2
    show(S["sirena"], sr); grow(S["sirena"], 1 if built or t > t_sir + 1 else seg(t, t_sir - 0.2, t_sir + 0.5))
    loud = (T("ochenta") - 0.3 < t < t_cur - 0.2)
    for k, o in enumerate(S["ondas"]):
        if loud or chirp:
            if loud: u = (t * 0.9 + k / 5) % 1; R = mix(2, 26, u)
            else: u = seg(t, T("suelta") + 1.6 * ((t - T("suelta")) // 1.6), T("suelta") + 1.6 * ((t - T("suelta")) // 1.6) + 0.25); R = mix(2, 6 + 2 * k, u)
            o.location = SIREN + Vector((0, 0, 1.2 + 0.4 * u)); o.scale = (R, R, 1)
        else: o.location = LEJOS
    vib = 1 + (0.08 * math.sin(t * 60) if (loud or chirp) else 0)
    S["piezo"].scale = (vib, vib, 1)
    # pila
    pl = built or t > t_pila - 0.4
    show(S["pila"], pl)
    out = seg(t, t_camb - 0.2, t_camb + 0.4); inn = seg(t, t_camb + 0.4, t_camb + 0.9); gone = seg(t, t_alg - 0.1, t_alg + 0.5)
    sc_ = (1 if built else seg(t, t_pila - 0.4, t_pila + 0.2)) * (1 - out) + inn * (1 - gone)
    S["pila"].location = BATT if (pl and sc_ > 0.01) else LEJOS; grow(S["pila"], sc_)
    low = seg(t, t_pila, t_pila + 1.0) * (1 - inn)
    set_color(S["pilac"], tuple(mix(c, d, low) for c, d in zip((0.2, 0.22, 0.26), (0.45, 0.12, 0.12))))
    p2 = t > t_alg - 0.1
    show(S["pila2"], p2); S["pila2"].location = BATT if p2 else LEJOS; grow(S["pila2"], seg(t, t_alg + 0.3, t_alg + 0.9))
    S["placa"].hide_render = not (built or t > t_sen)
    apply_cam(S["cam"], *cam_state(t, CAM(), drift=0.12))

def VD(at, dist, yaw, pitch, lens=40):
    at = Vector(at); y, p = math.radians(yaw), math.radians(pitch)
    return (tuple(at + dist * Vector((math.sin(y) * math.cos(p), -math.cos(y) * math.cos(p), math.sin(p)))), tuple(at), lens)

def CAM():
    k = []
    def add(t, v): k.append((t,) + v)
    C0 = (0, 1.2, 2.5)
    add(0.0, VD((0.3, 0.8, 2.6), 17, -18, 34))
    add(2.4, VD((0, 0.8, 2.6), 22, 6, 40))
    add(T("vamos") + 0.3, VD((0, 0, 4), 50, 0, 34))
    add(T("quieres") + 0.4, VD((-11, 0, 2), 82, -4, 20))
    add(T("así que haces") + 0.6, VD((0, 0, 4), 48, -10, 34))
    add(T("para que entre") + 0.2, VD((0, 0, 3), 50, 10, 32))
    add(T("pero a oscuras") + 0.3, VD(C0, 34, 0, 52))
    add(T("dentro pones") + 0.6, VD(tuple(P(LED_A, 3.6, 2.6)), 15, 25, 35))
    add(T("a ratos"), VD(tuple(P(LED_A, 2.6, 2.6)), 17, 18, 38))
    add(T("un sensor") + 0.3, VD(tuple(P(SEN_A0, 3.4, 2.6)), 16, -22, 38))
    add(T("pero no los") + 0.4, VD((0, 0.8, 2.5), 26, 0, 70))
    add(T("separados") + 0.4, VD((0, 0.8, 2.5), 26, -8, 66))
    add(T("con el aire") + 0.3, VD((0, 0.5, 2.5), 23, -12, 52))
    add(T("cuando entra"), VD((0, 0.8, 2.5), 28, 10, 44))
    add(T("una parte") + 0.2, VD(tuple(P(SEN_A, 1.8, 2.5)), 19, 18, 48))
    add(T("límite"), VD(C0, 27, 0, 50))
    add(T("despertarte"), VD((-2, -1, 2.5), 34, -10, 48))
    add(T("así que pones") + 0.4, VD(tuple(SIREN + Vector((1.5, 1.5, 0.5))), 22, -24, 50))
    add(T("medidos"), VD((-5, -2, 1), 70, -6, 62))
    add(T("tráfico") + 0.8, VD((-4, -1, 1), 66, 6, 58))
    add(T("curioso"), VD(C0, 30, -4, 50))
    add(T("insecto"), VD((-2.5, 0.5, 2.5), 22, -22, 44))
    add(T("malla") + 0.2, VD((-4, 0.5, 2.5), 26, -30, 40))
    add(T("mide") + 0.2, VD((0, 0.6, 2.5), 25, 4, 54))
    add(T("se acaba") + 0.4, VD(tuple(BATT + Vector((0, 1, 2))), 24, 22, 44))
    add(T("durante semanas"), VD(tuple(BATT + Vector((-1, 1.5, 2))), 27, 12, 46))
    add(T("algunos") + 0.6, VD(tuple(BATT + Vector((0, 0.5, 1.5))), 20, 18, 38))
    add(T("sígueme"), VD((0, 0, 3.5), 40, -4, 30))
    add(DUR + 3, VD((0, 0, 3.5), 44, 6, 28))
    return k

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v); sa = sen_angle(t)
    return {"rend": Pj(P(150, 10.2, 4.6)), "led": Pj(P(LED_A, 4.25, 3.4)), "sensor": Pj(P(sa, 4.3, 3.4)), "sep": Pj(P(WALL_A, 3.3, 4.0)),
            "haz": Pj(LED_TIP.lerp(TRAP, 0.5)), "camara": Pj(P(140, 5.0, 4.1)), "trap": Pj(TRAP), "sirena": Pj(tuple(SIREN + Vector((0, 0, 1.2)))),
            "pila": Pj(tuple(BATT + Vector((0, 0, 4.5)))), "malla": Pj(P(160, 6.0, 4.2)), "bicho": Pj(P(185, 3.0, 3.5)),
            "humo": Pj(P(0, 0, 3.5)), "fuego": Pj(tuple(FLM + Vector((0, 0, 2.5)))), "fhumo": Pj((-12, 0, 6)), "tapa": Pj((0, 0, 15.2)),
            "centro": Pj((0, 0, 2.5)), "piloto": Pj((3.0, -3.2, 16))}

if __name__ == "__main__":
    run("detector", build, pose, anchors)
