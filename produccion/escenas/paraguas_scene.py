# «Si tuvieras que inventar el paraguas automático…»: un pulgar pulsa el botón y el paraguas se abre de golpe bajo la
# lluvia. Se construye pieza a pieza: el palo, ocho varillas, la tela; las varillas se doblan solas, así que llevan ocho
# tirantes unidos a una corredera que sube y baja; el palo se hace de tubos que se meten unos en otros y las varillas se
# doblan por la mitad (1928). En rayos X: al cerrar se comprime un muelle dentro del tubo, un gancho lo retiene y el
# botón lo suelta: el muelle sube la corredera y abre las ocho varillas.
import bpy, bmesh, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector

T0, DUR = cargar("paraguas")
_TC = {}
def T(k, n=1, fin=False):
    key = (k, n, fin)
    if key not in _TC: _TC[key] = T0(k, n, fin)
    return _TC[key]

BG = (0.07, 0.09, 0.13); FLOOR = (0.12, 0.14, 0.18); SHAFT = (0.72, 0.75, 0.8); SHAFT_IN = (0.9, 0.92, 0.95); HANDLE = (0.12, 0.12, 0.14)
RIB = (0.25, 0.27, 0.3); STR = (0.85, 0.6, 0.2); RUN = (0.95, 0.75, 0.25); CAN1 = (0.2, 0.5, 0.95); CAN2 = (0.14, 0.38, 0.8)
RAIN = (0.55, 0.75, 1.0); RED = (0.92, 0.22, 0.2); SPRING = (0.95, 0.8, 0.3); SKIN = (0.93, 0.72, 0.58); BAG = (0.2, 0.45, 0.35)
LEJOS = Vector((0, 300, -300))
NR = 8; L_IN = 0.5; L_OUT = 0.5; D_STR = 0.4; S_STR = 0.4
PH_C = math.radians(5); PH_O = math.radians(74)
AZ = [k / NR * math.tau + math.pi / 8 for k in range(NR)]
rng = random.Random(3)
DROPS = [(rng.uniform(-1.4, 1.4), rng.uniform(-1.0, 1.4), rng.uniform(0, 1)) for _ in range(44)]

def dirv(ang, a): return Vector((math.sin(ang) * math.cos(a), math.sin(ang) * math.sin(a), -math.cos(ang)))

def ext(t):
    """1 = palo estirado, 0 = tubos metidos"""
    return 1 - seg(t, T("así que haces"), T("dentro de otro", fin=True)) * (1 - seg(t, T("y aquí viene"), T("y aquí viene") + 0.9))

def top_z(e): return 0.25 + 0.05 + e * 0.5 + 0.05 + e * 0.5 + 0.55 + 0.05

def opening(t):
    """0 cerrado … 1 abierto"""
    if t < T("vamos a inventarlo"):
        return seg(t, T("y tu paraguas") + 0.05, T("y tu paraguas") + 0.35)
    if t < T("así que pones"): return 0.0
    if t < T("al subirla"):
        if t >= T("los ocho tirantes"):
            return 1 - 0.75 * seg(t, T("una pieza") - 0.2, T("sube y")) + 0.0
        return 1.0
    if t < T("pero sigue"): return 0.25 + 0.75 * seg(t, T("al subirla"), T("como una flor", fin=True))
    if t < T("y aquí viene"): return 1 - seg(t, T("pero sigue"), T("pero sigue") + 0.8)
    if t < T("cuando cierras"): return seg(t, T("y aquí viene") + 0.9, T("el muelle que"))
    if t < T("al pulsar"): return 1 - seg(t, T("cuando cierras"), T("clic", fin=True))
    if t < T("el muelle se estira"): return 0.0
    return seg(t, T("el muelle se estira"), T("en un instante", fin=True))

def build():
    sc, cam = scene_setup(world=BG, shadow=0.3); cam.data.clip_start = 0.01
    S = {"cam": cam}
    box((30, 30, 0.2), (0, 0, -0.4), FLOOR)
    # mango y botón
    S["handle"] = cyl(0.045, 0.25, (0, 0, 0.125), HANDLE)
    S["button"] = cyl(0.016, 0.03, (0.045, 0, 0.18), RED, rot=(0, math.pi / 2, 0))
    # cortador de rayos X (mitad delantera)
    bpy.ops.mesh.primitive_cube_add(size=1, location=LEJOS); ct = bpy.context.object; ct.scale = (1, 1, 6); ct.hide_render = True; S["ct"] = ct
    def tube(r, color):
        bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=1, location=(0, 0, 0), vertices=32, end_fill_type='NOTHING'); o = bpy.context.object
        for vv in o.data.vertices: vv.co.z += 0.5
        setup(o, color, None, True)
        m = o.modifiers.new("sol", "SOLIDIFY"); m.thickness = 0.004; m.offset = -1
        o.data.materials.append(mat(SHAFT_IN)); m.material_offset = 1; m.material_offset_rim = 1
        b = o.modifiers.new("cut", "BOOLEAN"); b.operation = 'DIFFERENCE'; b.object = ct
        return o
    S["tubes"] = [tube(0.03, SHAFT), tube(0.025, SHAFT), tube(0.02, SHAFT)]
    S["hub"] = cyl(0.03, 0.05, LEJOS, RIB); S["tip"] = cyl(0.008, 0.12, LEJOS, RIB)
    S["runner"] = cyl(0.038, 0.06, LEJOS, RUN, unique=True)
    S["inner"] = [bar_obj(RIB, r=0.008) for _ in range(NR)]; S["outer"] = [bar_obj(RIB, r=0.007) for _ in range(NR)]
    S["str"] = [bar_obj(STR, r=0.007) for _ in range(NR)]
    S["ribtip"] = [sph(0.012, LEJOS, RIB) for _ in range(NR)]
    # tela: malla que se actualiza cada fotograma (vértice 0 arriba, 1-8 mitad, 9-16 punta)
    me = bpy.data.meshes.new("can"); bm = bmesh.new()
    vs = [bm.verts.new((0, 0, 0)) for _ in range(1 + 2 * NR)]
    for k in range(NR):
        j = (k + 1) % NR
        f = bm.faces.new((vs[0], vs[1 + k], vs[1 + j])); f.material_index = k % 2
        f = bm.faces.new((vs[1 + k], vs[1 + NR + k], vs[1 + NR + j], vs[1 + j])); f.material_index = k % 2
    bm.to_mesh(me); bm.free()
    can = bpy.data.objects.new("can", me); bpy.context.collection.objects.link(can)
    can.data.materials.append(mat(CAN1)); can.data.materials.append(mat(CAN2)); S["can"] = can
    # muelle, émbolo y gancho (rayos X)
    S["spring"] = empty(LEJOS)
    for k in range(20): torus(0.014, 0.0035, (0, 0, (k + 0.5) / 20), SPRING, S["spring"])
    S["plunger"] = cyl(0.016, 0.03, LEJOS, RUN); S["rod"] = bar_obj(RUN, r=0.005)
    S["hook"] = empty(LEJOS); box((0.012, 0.01, 0.05), (0, 0, -0.025), RED, S["hook"]); box((0.014, 0.01, 0.01), (-0.007, 0, -0.05), RED, S["hook"])
    # lluvia, pulgar y mochila
    S["drops"] = [cyl(0.006, 0.09, LEJOS, RAIN, v=6) for _ in DROPS]
    S["splash"] = [sph(0.015, LEJOS, RAIN) for _ in range(12)]
    S["thumb"] = sph(0.05, LEJOS, SKIN, scale=(1.4, 1, 0.9)); S["thumbarm"] = bar_obj(SKIN, r=0.045)
    bag = empty(LEJOS); S["bag"] = bag
    rounded_slab(0.32, 0.2, 0.06, 0.45, (0, 0, 0), BAG, bag)
    rounded_slab(0.26, 0.21, 0.05, 0.12, (0, 0.005, 0.33), (0.15, 0.36, 0.28), bag)
    join_static([cam, S["button"], ct, S["tubes"], S["hub"], S["tip"], S["runner"], S["inner"], S["outer"], S["str"], S["ribtip"], can,
                 S["spring"], S["plunger"], S["rod"], S["hook"], S["drops"], S["splash"], S["thumb"], S["thumbarm"], bag])
    return sc, S

def hide_bar(o): bar_set(o, LEJOS, LEJOS + Vector((0, 0, 0.001)))

def pose(t, S):
    e = ext(t); top = Vector((0, 0, top_z(e)))
    xray = T("el muelle que") <= t < T("y tú no")
    S["ct"].location = Vector((0, -0.5, 1.0)) if xray else LEJOS
    # tubos telescópicos
    z1a, z2a = 0.25, 0.25 + 0.05 + e * 0.5; z3a = z2a + 0.05 + e * 0.5
    build_on = t < T("vamos a inventarlo") or t >= T("vamos a inventarlo") + 0.6
    for o, za, ln in zip(S["tubes"], (z1a, z2a, z3a), (0.55, 0.6, 0.6 + 0.05)):
        o.location = Vector((0, 0, za)); o.scale = (1, 1, ln)
    S["hub"].location = top + Vector((0, 0, -0.02)); S["tip"].location = top + Vector((0, 0, 0.06))
    # varillas: aparición, caída sin tirantes, plegado
    op = opening(t)
    ph = mix(PH_C, PH_O, op)
    droop = seg(t, T("pero las varillas"), T("hacia abajo", fin=True)) * (1 - seg(t, T("una barrita"), T("desde abajo", fin=True)))
    fold = seg(t, T("y las varillas se doblan"), T("por la mitad", fin=True)) * (1 - seg(t, T("y aquí viene"), T("y aquí viene") + 0.9))
    building = T("así que pones") - 0.1 <= t < T("el muelle que")
    rib_app = []
    for k in range(NR):
        if t < T("vamos a inventarlo"): ap = 1.0
        elif t < T("así que pones"): ap = 0.0
        elif building and t < T("con ocho"): ap = seg(t, T("una tela") + 0.2 * k, T("una tela") + 0.2 * k + 0.3)
        else: ap = 1.0
        rib_app.append(ap)
    tips, mids = [], []
    for k in range(NR):
        a = AZ[k]; pin = ph - math.radians(28) * droop; pout = pin - math.radians(30) * droop + math.pi * 0.97 * fold
        mid = top + dirv(pin, a) * L_IN * rib_app[k]; tip = mid + dirv(pout, a) * L_OUT * rib_app[k]
        tips.append(tip); mids.append(mid)
        if rib_app[k] > 0.01:
            bar_set(S["inner"][k], top, mid); bar_set(S["outer"][k], mid, tip); S["ribtip"][k].location = tip
        else:
            hide_bar(S["inner"][k]); hide_bar(S["outer"][k]); S["ribtip"][k].location = LEJOS
    # tela
    can_app = 1.0
    if building: can_app = seg(t, T("unidas"), T("con ocho") + 0.3)
    if T("vamos a inventarlo") <= t < T("así que pones"): can_app = 0.0
    me = S["can"].data
    off = Vector((0, 0, 0.012))
    me.vertices[0].co = top + off
    for k in range(NR):
        me.vertices[1 + k].co = top.lerp(mids[k], can_app) + off
        me.vertices[1 + NR + k].co = top.lerp(tips[k], can_app) + off
    me.update()
    # tirantes y corredera
    str_on = t < T("vamos a inventarlo") or t >= T("así que a cada")
    zr = top.z - D_STR * math.cos(ph) - math.sqrt(max(0.0, S_STR ** 2 - (D_STR * math.sin(ph)) ** 2))
    S["runner"].location = Vector((0, 0, zr)) if str_on else LEJOS
    set_color(S["runner"], (1.0, 0.9, 0.4) if T("en una pieza") <= t < T("pero sigue") else RUN)
    for k in range(NR):
        sa = seg(t, T("un tirante") + 0.12 * k, T("un tirante") + 0.12 * k + 0.3) if building and t < T("los ocho tirantes") else 1.0
        if str_on and sa > 0.01:
            p1 = top + dirv(ph - math.radians(28) * droop, AZ[k]) * D_STR
            p0 = Vector((0.036 * math.cos(AZ[k]), 0.036 * math.sin(AZ[k]), zr + 0.02))
            bar_set(S["str"][k], p0, p0.lerp(p1, sa))
        else: hide_bar(S["str"][k])
    # muelle (rayos X): de la base del tubo al émbolo, unido a la corredera
    if xray:
        z0 = 0.3; zp = zr - 0.37; S["spring"].location = Vector((0, 0, z0)); S["spring"].scale = (1, 1, max(0.05, zp - 0.015 - z0))
        S["plunger"].location = Vector((0, 0, zp)); bar_set(S["rod"], Vector((0, 0, zp)), Vector((0, 0, zr)))
        zc = top_z(1) - D_STR * math.cos(PH_C) - math.sqrt(S_STR ** 2 - (D_STR * math.sin(PH_C)) ** 2) - 0.37
        S["hook"].location = Vector((0.012, -0.004, zc + 0.045))
        hk = seg(t, T("y un gancho"), T("y un gancho") + 0.4) * (1 - seg(t, T("el gancho se"), T("se suelta", fin=True)))
        S["hook"].rotation_euler = (0, mix(-0.9, 0.0, hk), 0)
    else:
        S["spring"].location = LEJOS; S["plunger"].location = LEJOS; S["hook"].location = LEJOS; hide_bar(S["rod"])
    # pulgar en el botón
    press = None
    if t < T("y tu paraguas") + 0.6: press = seg(t, 0.0, 0.5) * (1 - seg(t, T("y tu paraguas") + 0.1, T("y tu paraguas") + 0.6))
    elif T("al pulsar") - 0.4 <= t < T("el muelle se estira") + 0.5:
        press = seg(t, T("al pulsar") - 0.4, T("el botón")) * (1 - seg(t, T("el muelle se estira"), T("el muelle se estira") + 0.5))
    if press is not None:
        hp = Vector((0.045 + 0.045 + 0.04 * (1 - press), -0.005, 0.18)); S["thumb"].location = hp
        bar_set(S["thumbarm"], hp + Vector((0.02, 0, -0.02)), hp + Vector((0.35, -0.25, -0.35)))
        S["button"].location = Vector((0.045 - 0.006 * press, 0, 0.18))
    else:
        S["thumb"].location = LEJOS; hide_bar(S["thumbarm"]); S["button"].location = Vector((0.045, 0, 0.18))
    # mochila
    bag_on = T("quieres taparte") <= t < T("así que pones") or T("así nació") <= t < T("y aquí viene")
    S["bag"].location = Vector((0.45, 0.05, -0.3)) if bag_on else LEJOS
    # lluvia: se para en la tela si está abierta
    rain = t < T("vamos a inventarlo") + 0.3 or T("quieres taparte") <= t < T("así que pones") + 1.0 or t >= T("y abre las ocho")
    R_open = (L_IN + L_OUT) * math.sin(ph) * (1 - fold) if can_app > 0.9 else 0.0
    zc_can = top.z - (L_IN + L_OUT) * math.cos(ph) * 0.6
    ns = 0
    for k, (d, (x, y, ph0)) in enumerate(zip(S["drops"], DROPS)):
        if not rain: d.location = LEJOS; continue
        u = (t * 0.9 + ph0) % 1.0; z = 3.4 - 3.8 * u
        r = math.hypot(x, y)
        if r < R_open and z < zc_can + 0.05 * (1 - r / max(R_open, 0.01)):
            d.location = LEJOS
            if ns < len(S["splash"]) and z > zc_can - 0.25:
                S["splash"][ns].location = Vector((x, y, zc_can + 0.03)); ns += 1
            continue
        d.location = Vector((x, y, z))
    for s in S["splash"][ns:]: s.location = LEJOS
    apply_cam(S["cam"], *camera(t))

def CAMS():
    btn = (0.045, 0, 0.18)
    return [
        (0.0, [(0, (0.3, -0.35, 0.3), (0.02, 0, 0.2), 40), (T("y tu paraguas"), (0.35, -0.5, 0.45), (0.0, 0, 0.4), 36),
               (T("se abre"), (1.2, -3.2, 1.6), (0, 0, 1.35), 32), (T("qué tiene"), (1.4, -3.6, 1.5), (0, 0, 1.3), 32)]),
        (T("qué tiene"), [(0, (1.2, -3.4, 1.5), (0, 0, 1.3), 32), (T("vamos a inventarlo"), (0.6, -2.2, 1.2), (0, 0, 1.0), 34)]),
        (T("vamos a inventarlo"), [(0, (0.6, -2.6, 1.1), (0, 0, 0.9), 34), (T("así que pones"), (0.5, -2.9, 1.3), (0.15, 0, 0.85), 34)]),
        (T("así que pones"), [(0, (0.9, -3.0, 2.6), (0, 0, 1.6), 32), (T("unidas"), (0.6, -3.4, 2.4), (0, 0, 1.6), 32), (T("con ocho"), (1.2, -3.5, 2.8), (0, 0, 1.5), 32)]),
        (T("pero las varillas"), [(0, (1.6, -3.2, 1.6), (0, 0, 1.3), 32), (T("así que a cada"), (1.0, -3.0, 1.0), (0, 0, 1.25), 32)]),
        (T("así que a cada"), [(0, (0.8, -2.4, 0.9), (0, 0, 1.35), 34), (T("los ocho"), (1.0, -2.8, 0.9), (0, 0, 1.3), 34),
                                (T("al subirla"), (1.1, -3.4, 1.1), (0, 0, 1.3), 32), (T("como una flor"), (0.4, -3.2, 3.2), (0, 0, 1.4), 32)]),
        (T("pero sigue"), [(0, (1.0, -3.6, 1.2), (0, 0, 1.0), 32), (T("así que haces"), (1.0, -3.4, 1.0), (0, 0, 1.0), 32),
                           (T("y las varillas se"), (0.8, -2.6, 0.8), (0, 0, 0.65), 32), (T("así nació"), (0.9, -2.4, 0.7), (0.2, 0, 0.45), 32),
                           (T("y aquí viene"), (1.0, -2.8, 0.9), (0.1, 0, 0.7), 32)]),
        (T("y aquí viene"), [(0, (1.0, -3.2, 1.1), (0, 0, 0.95), 32)]),
        (T("el muelle que"), [(0, (0.14, -0.75, 0.75), (0, 0, 0.82), 40), (T("cuando cierras"), (0.16, -0.8, 0.7), (0, 0, 0.75), 40),
                              (T("aprietas"), (0.1, -0.6, 0.6), (0, 0, 0.62), 40), (T("y un gancho"), (0.07, -0.32, 0.78), (0.01, 0, 0.76), 45), (T("comprimido", fin=True), (0.08, -0.34, 0.78), (0.01, 0, 0.76), 45),
                              (T("al pulsar"), (0.25, -0.4, 0.3), btn, 40), (T("el gancho se"), (0.07, -0.32, 0.78), (0.01, 0, 0.76), 45), (T("se suelta", fin=True), (0.08, -0.36, 0.8), (0.01, 0, 0.78), 45),
                              (T("el muelle se estira"), (0.16, -0.8, 0.8), (0, 0, 0.88), 40), (T("sube la pieza"), (0.3, -1.6, 1.3), (0, 0, 1.3), 34),
                              (T("y abre las"), (1.2, -3.4, 1.5), (0, 0, 1.3), 32)]),
        (T("y tú no"), [(0, (1.3, -3.6, 1.4), (0, 0, 1.3), 32), (DUR + 1, (0.8, -3.9, 1.2), (0, 0, 1.4), 32)]),
    ]

def camera(t):
    segs = CAMS(); k = 0
    for i, (st, _) in enumerate(segs):
        if t >= st: k = i
    st, ks = segs[k]
    ks = [(st if a == 0 else a, p, q, l) for a, p, q, l in ks]
    if ks[-1][0] <= t: ks = ks + [(t + 1, ks[-1][1], ks[-1][2], ks[-1][3])]
    return cam_state(t, ks, drift=0.004)

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v)
    r = S["runner"].location; sp = S["spring"].location
    return {"runner": Pj(r), "rib": Pj(S["ribtip"][6].location), "str": Pj(S["str"][6].matrix_world.translation),
            "spring": Pj(sp + Vector((0, 0, 0.4)) if sp.z < 100 else LEJOS), "hook": Pj(S["hook"].location if S["hook"].location.z > -100 else LEJOS),
            "button": Pj(Vector((0.05, 0, 0.18))), "top": Pj(Vector((0, 0, top_z(ext(t)) + 0.15))), "shaft": Pj(Vector((0, 0, 0.6))),
            "bag": Pj(Vector((0.45, 0.05, 0.25)))}

if __name__ == "__main__":
    run("paraguas", build, pose, anchors)
