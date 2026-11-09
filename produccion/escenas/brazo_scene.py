# «Si tuvieras que inventar un brazo…»: brazo en corte de perfil (piel detrás, huesos y músculos delante).
# Abre con la mano levantando un móvil y el bíceps encogiéndose; luego se construye: hueso del antebrazo, bisagra del codo,
# el hueso cae sin motor, bíceps que se encoge y tira (nunca empuja), tendón a 4 cm del codo, mano a 35 cm, fuerza ×8,
# móvil de 200 g → casi 2 kg; 1 cm de músculo → 9 cm de mano; lanzamiento de una pelota; tríceps detrás; los dos por parejas.
import bpy, math, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector, Quaternion

T, DUR = cargar("brazo")
BG = (0.09, 0.1, 0.13); SKIN = (0.93, 0.72, 0.6); SKIN_IN = (0.98, 0.84, 0.75); BONE = (0.96, 0.93, 0.84)
MUS = (0.86, 0.27, 0.3); MUS2 = (0.72, 0.24, 0.42); TEND = (0.97, 0.97, 0.95); PIN = (0.55, 0.62, 0.72)
PH_BODY = (0.18, 0.2, 0.25); PH_SCR = (0.25, 0.55, 0.95); BALL = (1.0, 0.78, 0.2); NAIL = (0.98, 0.86, 0.8)
LEJOS = (0, 80, -300)
FA_LEN = 3.5                                  # 1 unidad = 10 cm: la mano queda a 35 cm del codo
B_TOP = Vector((0.45, -0.15, 2.6)); B_INS = (0.4, 0.12)      # bíceps: origen arriba, inserción a 4 cm del codo
T_TOP = Vector((-0.42, -0.15, 2.6)); T_INS = (-0.34, 0.02)   # tríceps: detrás, al olécranon
B_TEN = 0.55; T_TEN = 0.45

def K():
    return dict(inv=T("vamos a inventar"), hueso=T("un hueso rígido"), bis=T("y una bisagra"), dobl=T("para que pueda"),
                solo=T("pero un hueso"), motor=T("necesita un motor"), musc=T("así que le pones"), bic=T("el bíceps"),
                cosa=T("un músculo solo sabe"), enc=T("encogerse"), nunca=T("nunca empuja"), atas=T("lo atas al hueso"),
                tend=T("el tendón"), ojo=T("pero ojo"), mano=T("no lo atas cerca"), cuatro=T("lo atas a solo"),
                tres=T("y la mano queda"), cur=T("y aquí viene"), como=T("como tira"), ocho=T("tiene que hacer"),
                movil=T("por eso tu móvil"), gram=T("de doscientos"), cuesta=T("le cuesta"), mal=T("entonces es"),
                camb=T("a cambio"), cm1=T("si el bíceps se encoge"),
                sube=T("tu mano sube"), pierd=T("pierdes fuerza"), lanz=T("por eso puedes lanzar"), falta=T("pero falta"),
                tira=T("si el músculo solo tira"), quien=T("quién vuelve"), otro=T("así que pones otro"), tri=T("el tríceps"),
                uno=T("uno tira"), par=T("siempre trabajan"), sig=T("sígueme"))

def capsule(p0, p1, r, col, parent=None):
    """cilindro con extremos redondos entre p0 y p1 (coordenadas locales del padre)"""
    p0, p1 = Vector(p0), Vector(p1); d = p1 - p0
    o = cyl(r, d.length, (p0 + p1) / 2, col, parent=parent, v=32)
    o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())
    sph(r, p0, col, parent=parent); sph(r, p1, col, parent=parent)
    return o

def fa_world(x, z, th):
    c, s = math.cos(th), math.sin(th)
    return Vector((x * c - z * s, 0, x * s + z * c))

def build():
    sc, cam = scene_setup(world=BG, shadow=0.3)
    S = {"cam": cam}
    box((80, 0.2, 80), (0, 6, 0), (0.11, 0.12, 0.16))
    # ---- piel (silueta de corte, detrás) ----
    S["skin_up"] = e = empty((0, 0, 0))
    capsule((0.05, 0.75, 0.05), (0.05, 0.75, 6.5), 0.98, SKIN, parent=e)
    capsule((0.05, 0.66, 0.05), (0.05, 0.66, 6.5), 0.84, SKIN_IN, parent=e)
    # ---- antebrazo (todo hijo de fa, gira en el codo) ----
    S["fa"] = fa = empty((0, 0, 0))
    S["fa_skin"] = fs = empty((0, 0, 0), parent=fa)
    capsule((0.0, 0.7, 0.0), (3.2, 0.7, 0.05), 0.6, SKIN, parent=fs)
    capsule((0.0, 0.62, 0.0), (3.2, 0.62, 0.05), 0.48, SKIN_IN, parent=fs)
    S["fa_bone"] = fb = empty((0, 0, 0), parent=fa)
    capsule((0.15, 0.0, 0.13), (3.15, 0.0, 0.1), 0.1, BONE, parent=fb)        # radio
    capsule((-0.3, 0.05, -0.05), (3.1, 0.05, -0.1), 0.11, BONE, parent=fb)     # cúbito con olécranon
    sph(0.2, (0.0, 0.05, 0.0), BONE, parent=fb)
    # mano cerrada
    S["hand"] = hd = empty((3.55, 0, 0.05), parent=fa)
    sph(0.5, (0, 0.05, 0), SKIN, parent=hd, scale=(0.95, 0.75, 0.85))
    for k in range(4):
        sph(0.17, (0.42, -0.22, 0.32 - 0.21 * k), SKIN, parent=hd, scale=(1.1, 1, 0.95))
        sph(0.07, (0.55, -0.28, 0.32 - 0.21 * k), NAIL, parent=hd)
    capsule((0.0, -0.4, 0.15), (0.25, -0.42, 0.5), 0.14, SKIN, parent=hd)      # pulgar
    # móvil en la mano (se mantiene derecho)
    S["phone"] = ph = empty((0.3, 0.0, 0.55), parent=hd)
    s = rounded_slab(0.78, 1.6, 0.12, 0.1, (0, 0.05, 0), PH_BODY, parent=ph); s.rotation_euler = (math.pi / 2, 0, 0)
    s = rounded_slab(0.7, 1.5, 0.1, 0.02, (0, -0.06, 0), PH_SCR, parent=ph); s.rotation_euler = (math.pi / 2, 0, 0)
    for k in range(3):
        s = rounded_slab(0.45, 0.16, 0.06, 0.02, (-0.06 + 0.1 * (k % 2), -0.085, 0.45 - 0.3 * k), (0.85, 0.92, 1.0), parent=ph)
        s.rotation_euler = (math.pi / 2, 0, 0)
    # ---- brazo: húmero y bisagra ----
    S["hum"] = hu = empty((0, 0, 0))
    capsule((0.0, 0.05, 0.25), (0.0, 0.05, 3.8), 0.17, BONE, parent=hu)
    sph(0.3, (0.0, 0.05, 0.12), BONE, parent=hu, scale=(1.1, 1, 0.9))
    S["pin"] = cyl(0.11, 0.9, (0, -0.15, 0.0), PIN, rot=(math.pi / 2, 0, 0), unique=True)
    # ---- músculos (elipsoides que se estiran entre dos puntos) ----
    S["bic"] = sph(1.0, LEJOS, MUS, seg=32, unique=True)
    S["bten"] = bar_obj(TEND, r=0.07, unique=True)
    S["tri"] = sph(1.0, LEJOS, MUS2, seg=32, unique=True)
    S["tten"] = bar_obj(TEND, r=0.07, unique=True)
    S["bten_top"] = bar_obj(TEND, r=0.07, unique=True); S["tten_top"] = bar_obj(TEND, r=0.07, unique=True)
    # punto fantasma "cerca de la mano"
    S["ghost"] = sph(0.12, LEJOS, (0.95, 0.3, 0.3), unique=True)
    S["ins"] = sph(0.11, LEJOS, (0.3, 0.95, 0.5), unique=True)
    S["ball"] = sph(0.42, LEJOS, BALL, seg=24)
    S["trail"] = [sph(0.42, LEJOS, (1.0, 0.85, 0.45), seg=16, unique=True) for _ in range(6)]
    dyn = [cam, S["skin_up"], S["fa"], S["hum"], S["pin"], S["bic"], S["bten"], S["tri"], S["tten"], S["bten_top"], S["tten_top"],
           S["ghost"], S["ins"], S["ball"], S["trail"]]
    join_static(dyn)
    return sc, S

def muscle(ob, ten, ten_top, top, ins, ten_len, R0, L0, vis, anchor):
    """vientre muscular entre top y (ins + ten_len hacia arriba); volumen constante (más corto = más gordo)"""
    d = (top - ins); full = d.length; u = d.normalized()
    q = ins + u * ten_len; t2 = top - u * 0.15
    L = (t2 - q).length; r = R0 * math.sqrt(L0 / max(L, 0.3))
    if vis < 0.01:
        ob.location = LEJOS; ten.location = LEJOS; ten_top.location = LEJOS; return
    ob.location = (q + t2) / 2; ob.rotation_mode = 'QUATERNION'; ob.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(u)
    ob.scale = (r * vis, r * vis * 0.8, L / 2 * vis)
    bar_set(ten, ins, q + u * 0.1); bar_set(ten_top, t2 - u * 0.1, anchor)
    ten.scale = (ten["r"] * vis, ten["r"] * vis, ten.scale.z); ten_top.scale = (ten_top["r"] * vis, ten_top["r"] * vis, ten_top.scale.z)
    return L

def theta(t, k):
    D = math.radians
    if t < k["inv"]:                           # abre levantando el móvil
        return D(keyed(t, [(0, 14), (1.3, 40), (2.4, 30), (3.4, 40), (4.6, 32), (5.8, 38)]))
    if t < k["dobl"]: return D(0)
    if t < k["solo"] + 0.2:                    # demostración de la bisagra
        return D(35 * math.sin((t - k["dobl"]) * 4.5) * seg(t, k["dobl"], k["dobl"] + 0.3))
    if t < k["enc"]:                           # sin motor: cae y cuelga
        return D(keyed(t, [(k["solo"] + 0.2, 0), (k["solo"] + 0.9, -62), (k["solo"] + 1.2, -55), (k["solo"] + 1.5, -60)]))
    if t < k["nunca"] + 0.3:                   # el bíceps se encoge y tira
        return D(keyed(t, [(k["enc"], -60), (k["enc"] + 0.9, 40)]))
    if t < k["atas"]:                          # no puede empujar: cae por su peso
        return D(keyed(t, [(k["nunca"] + 0.3, 40), (k["nunca"] + 0.8, -20)]))
    if t < k["cm1"]:                           # horizontal para medir (con un leve vaivén: nunca quieto)
        return D(keyed(t, [(k["atas"], -20), (k["atas"] + 0.8, 0)]) + 2.5 * math.sin((t - k["atas"]) * 2.2) * seg(t, k["atas"] + 0.8, k["atas"] + 1.5))
    if t < k["pierd"]:                         # 1 cm de músculo → 9 cm de mano
        return D(keyed(t, [(k["cm1"] + 0.6, 0), (k["sube"] + 1.0, 14.9)]))
    if t < k["lanz"] + 0.6: return D(keyed(t, [(k["pierd"], 14.9), (k["lanz"] + 0.5, -45)]))
    if t < k["falta"]:                         # latigazo de lanzamiento
        return D(keyed(t, [(k["lanz"] + 0.6, -45), (k["lanz"] + 1.0, 75), (k["lanz"] + 1.6, 70), (k["falta"], 60)]))
    if t < k["uno"]: return D(60 + 4 * math.sin((t - k["falta"]) * 3.0))
    if t < k["sig"]:                           # por parejas: arriba y abajo
        u = (t - k["uno"]) / 1.6
        return D(15 + 45 * math.cos(u * math.pi))
    return D(keyed(t, [(k["sig"], 45), (k["sig"] + 1.0, 30)]))

def hide(o): o.location = LEJOS

def pose(t, S):
    k = K(); th = theta(t, k)
    S["fa"].rotation_euler = (0, -th, 0)
    S["phone"].rotation_euler = (0, th, 0)
    # visibilidades
    gone = seg(t, k["inv"], k["inv"] + 0.6)                         # se desmonta para inventarlo
    skin = 1 - gone + seg(t, k["movil"] - 0.3, k["movil"] + 0.4) * gone
    sk = max(skin, 0.0001)
    S["skin_up"].scale = (sk, sk, sk) if skin > 0.01 else (0.0001, 0.0001, 0.0001)
    S["fa_skin"].scale = (sk, sk, sk) if skin > 0.01 else (0.0001, 0.0001, 0.0001)
    bone_fa = 1 - gone + gone * seg(t, k["inv"] + 0.7, k["inv"] + 1.3)
    S["fa_bone"].scale = (1, 1, 1) if bone_fa > 0.99 else (bone_fa + 1e-4,) * 3
    hum = 1 - gone + gone * seg(t, k["bis"], k["bis"] + 0.5)
    S["hum"].scale = (1, 1, hum + 1e-4)
    pin = seg(t, k["bis"] + 0.2, k["bis"] + 0.6) * (1 - seg(t, k["solo"], k["solo"] + 0.5))
    S["pin"].scale = (pin + 1e-4,) * 3
    hand = 1 - gone + gone * seg(t, k["mano"], k["mano"] + 0.5)
    S["hand"].scale = (hand + 1e-4,) * 3
    phone = (1 - gone + gone * seg(t, k["movil"], k["movil"] + 0.5)) * (1 - seg(t, k["lanz"] - 0.5, k["lanz"] - 0.1) * (1 - seg(t, k["falta"], k["falta"] + 0.5)))
    S["phone"].scale = (phone + 1e-4,) * 3
    # bíceps
    ins = fa_world(*B_INS, th) + Vector((0, -0.15, 0))
    bic = 1 - gone + gone * seg(t, k["bic"] - 0.5, k["bic"] + 0.2)
    pulse = 1.0
    muscle(S["bic"], S["bten"], S["bten_top"], B_TOP, ins, B_TEN, 0.36, 1.9, bic, Vector((0.14, -0.1, 3.35)))
    # tendón: rojo (parte del músculo) hasta que lo «atas»
    tw = seg(t, k["atas"] + 0.8, k["tend"] + 0.3) if t > k["inv"] else 1.0
    set_color(S["bten"], tuple(mix(a, b, tw) for a, b in zip(MUS, TEND)))
    if k["tend"] < t < k["tend"] + 0.6:
        g = 1 + 1.2 * math.sin((t - k["tend"]) / 0.6 * math.pi)
        S["bten"].scale = (0.07 * g, 0.07 * g, S["bten"].scale.z)
    # tríceps (al principio también, luego solo cuando se añade)
    tri = (1 - gone) + gone * seg(t, k["tri"] - 0.4, k["tri"] + 0.2)
    tins = fa_world(*T_INS, th) + Vector((0, -0.15, 0))
    muscle(S["tri"], S["tten"], S["tten_top"], T_TOP, tins, T_TEN, 0.34, 1.9, tri, Vector((-0.14, -0.1, 3.35)))
    # colores: músculo activo más intenso
    bic_on = (t < k["inv"]) or (k["enc"] < t < k["nunca"] + 0.3) or (k["cm1"] < t < k["pierd"]) or (k["lanz"] + 0.5 < t < k["lanz"] + 1.1) \
        or (t > k["uno"] and math.sin((t - k["uno"]) / 1.6 * math.pi) < 0 and t < k["sig"])
    tri_on = t > k["uno"] and t < k["sig"] and math.sin((t - k["uno"]) / 1.6 * math.pi) > 0
    set_color(S["bic"], (1.0, 0.33, 0.33) if bic_on else MUS)
    set_color(S["tri"], (0.85, 0.3, 0.6) if tri_on else MUS2)
    # punto de inserción y punto fantasma cerca de la mano
    if k["mano"] < t < k["cuatro"] + 0.5: S["ghost"].location = fa_world(3.0, 0.12, th) + Vector((0, -0.25, 0)); S["ghost"].scale = (1 + 0.3 * math.sin(t * 10),) * 3
    else: hide(S["ghost"])
    if k["cuatro"] < t < k["cur"]: S["ins"].location = ins + Vector((0, -0.12, 0)); S["ins"].scale = (1 + 0.35 * math.sin(t * 10),) * 3
    else: hide(S["ins"])
    # pelota: en la mano, sale disparada
    rel = k["lanz"] + 0.85
    if k["lanz"] - 0.3 < t < rel:
        S["ball"].location = fa_world(3.95, 0.45, th) + Vector((0, -0.1, 0)); S["ball"].scale = (seg(t, k["lanz"] - 0.3, k["lanz"]) + 1e-4,) * 3
    elif rel <= t < k["falta"] + 0.5:
        p0 = fa_world(3.95, 0.45, math.radians(55)) + Vector((0, -0.1, 0)); dt = t - rel
        S["ball"].location = p0 + Vector((9.0 * dt, 0, 8.0 * dt - 4.9 * dt * dt)); S["ball"].scale = (1, 1, 1)
    else: hide(S["ball"])
    for i, o in enumerate(S["trail"]):
        dt = t - rel - 0.05 * (i + 1)
        if rel < t < k["falta"] + 0.5 and dt > 0:
            p0 = fa_world(3.95, 0.45, math.radians(55)) + Vector((0, -0.05, 0))
            o.location = p0 + Vector((9.0 * dt, 0, 8.0 * dt - 4.9 * dt * dt)); s = 0.85 - 0.13 * i; o.scale = (s, s, s)
        else: hide(o)
    apply_cam(S["cam"], *cam_state(t, CAM(k), drift=0.07))

LIFT = 0.55          # mira algo más arriba: el brazo queda en la franja central, bajo los subtítulos
def V_(at, off, lens=38):
    return (tuple(Vector(at) + Vector(off)), tuple(Vector(at) + Vector((0, 0, LIFT))), lens)

def CAM(k):
    c = []
    def add(t, v): c.append((t,) + v)
    add(0.0, V_((1.8, 0, 1.2), (0.6, -9.5, 0.5), 38))      # primer plano: la mano levanta el móvil
    add(2.0, V_((1.2, 0, 1.3), (0.3, -10.0, 0.5), 38))
    add(k["inv"], V_((1.3, 0, 1.0), (0.0, -11, 0.6), 38))
    add(k["hueso"] - 0.3, V_((1.5, 0, -0.3), (0.0, -9.5, 0.6), 38))
    add(k["bis"] + 0.3, V_((1.0, 0, 0.5), (0.3, -9.5, 0.6), 38))
    add(k["solo"], V_((1.1, 0, 0.2), (0.0, -10.5, 0.6), 38))
    add(k["motor"], V_((0.9, 0, 0.3), (0.0, -10.5, 0.6), 38))
    add(k["bic"], V_((0.6, 0, 1.0), (0.3, -9.0, 0.6), 38))
    add(k["nunca"], V_((1.0, 0, 0.9), (0.0, -10, 0.6), 38))
    add(k["tend"], V_((0.6, 0, 0.6), (0.3, -7.0, 0.4), 38))           # cerca del tendón
    add(k["ojo"] - 0.2, V_((1.6, 0, 0.6), (0.0, -11.5, 0.4), 38))
    add(k["mano"] + 0.8, V_((1.6, 0, 0.6), (0.0, -11.5, 0.4), 38))
    add(k["cuatro"] + 0.7, V_((0.6, 0, 0.3), (0.2, -6.5, 0.3), 38))    # zoom a los 4 cm
    add(k["tres"] + 0.3, V_((1.6, 0, 0.6), (0.0, -11.5, 0.4), 38))
    add(k["como"], V_((1.6, 0, 0.8), (0.0, -11.5, 0.4), 38))
    add(k["movil"] + 0.3, V_((1.75, 0, 0.9), (0.2, -12.5, 0.5), 38))
    add(k["mal"], V_((1.75, 0, 0.9), (0.0, -12.5, 0.5), 38))
    add(k["cm1"], V_((1.75, 0, 0.8), (0.0, -12.0, 0.5), 38))
    add(k["pierd"], V_((1.75, 0, 0.8), (0.0, -12.5, 0.5), 38))
    add(k["lanz"] + 0.5, V_((2.0, 0, 1.2), (0.0, -15.5, 0.5), 38))
    add(k["falta"], V_((1.6, 0, 1.4), (0.0, -12.5, 0.5), 38))
    add(k["quien"], V_((1.2, 0, 1.4), (0.0, -10.5, 0.5), 38))
    add(k["tri"], V_((0.5, 0, 1.4), (0.2, -9.0, 0.5), 38))
    add(k["uno"], V_((1.45, 0, 0.9), (0.0, -12.5, 0.5), 38))
    add(k["sig"], V_((1.4, 0, 1.0), (0.0, -12.5, 0.5), 38))
    add(DUR + 2, V_((1.4, 0, 1.0), (0.0, -13.5, 0.5), 38))
    return c

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v); k = K(); th = theta(t, k)
    return {"elbow": Pj((0, -0.2, 0)), "ins": Pj(fa_world(*B_INS, th) + Vector((0, -0.3, 0))),
            "hand": Pj(fa_world(3.55, 0.05, th) + Vector((0, -0.3, 0))), "bic": Pj(S["bic"].location + Vector((0, -0.4, 0))),
            "tri": Pj(S["tri"].location + Vector((0, -0.4, 0))), "btop": Pj(B_TOP), "hum": Pj((0, -0.2, 2.0)),
            "fa": Pj(fa_world(1.8, 0.0, th) + Vector((0, -0.3, 0))), "ghost": Pj(fa_world(3.0, 0.12, th) + Vector((0, -0.3, 0))),
            "phone": Pj(fa_world(3.85, 1.6, th)), "ball": Pj(S["ball"].location)}

if __name__ == "__main__":
    run("brazo", build, pose, anchors)
