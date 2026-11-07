# «Así funciona la olla exprés»: olla en corte sobre el fuego. Gancho: la válvula suelta un chorro de vapor. Cazuela
# abierta: el agua hierve, el fuego sube pero se queda en 100 °C y el vapor se escapa. Se cierra con tapa y goma: el vapor
# atrapado empuja (flechas), la presión sube a +1 bar y el agua llega a 120 °C; la comida se hace en un tercio. Válvula con
# muelle que se levanta y silba; dos válvulas de seguridad más; la goma se deforma por un lado; cierre que se bloquea.
import bpy, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from marcas import cargar
from mathutils import Vector

T0, DUR = cargar("ollaexpres")
_TC = {}
def T(k, n=1, fin=False):
    key = (k, n, fin)
    if key not in _TC: _TC[key] = T0(k, n, fin)
    return _TC[key]

BG = (0.08, 0.09, 0.12); WALL = (0.12, 0.13, 0.17); COUNTER = (0.2, 0.21, 0.25); STOVE = (0.07, 0.07, 0.08); GRATE = (0.25, 0.25, 0.27)
STEEL = (0.72, 0.75, 0.8); STEEL_IN = (0.88, 0.9, 0.93); WATER = (0.3, 0.6, 0.95); BUBBLE = (0.75, 0.88, 1.0); STEAM = (0.95, 0.96, 0.98)
FLAME = (0.3, 0.55, 1.0); FLAME_IN = (0.7, 0.85, 1.0); GASKET = (0.95, 0.5, 0.15); BLACK = (0.1, 0.1, 0.12); RED = (0.92, 0.22, 0.2)
GREEN = (0.3, 0.85, 0.45); FOOD = [(0.95, 0.8, 0.4), (0.95, 0.55, 0.25), (0.6, 0.8, 0.3), (0.9, 0.75, 0.45)]; SPRING = (0.95, 0.78, 0.25); SKIN = (0.93, 0.72, 0.58)
LEJOS = Vector((0, 300, -300))
R = 1.0; ZB = 0.06; ZT = 1.16; WL = 0.72      # radio, fondo, borde y nivel del agua
V = Vector((0, 0, ZT + 0.05))                 # base de la válvula
rng = random.Random(7)
BUB = [(rng.uniform(-0.85, 0.85), rng.uniform(0, 1), rng.uniform(0.025, 0.05)) for _ in range(26)]
STM = [(rng.uniform(-0.8, 0.8), rng.uniform(0, 1), rng.uniform(0.05, 0.1), rng.uniform(0, 6.28)) for _ in range(18)]

def tube(r, depth, loc, color, inner, th, bottom=False, v=64):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, location=loc, vertices=v, end_fill_type='NGON' if bottom else 'NOTHING')
    o = bpy.context.object
    if bottom:
        import bmesh
        bm = bmesh.new(); bm.from_mesh(o.data)
        top = [f for f in bm.faces if f.normal.z > 0.9]; bmesh.ops.delete(bm, geom=top, context='FACES'); bm.to_mesh(o.data); bm.free()
    setup(o, color, None, True)
    m = o.modifiers.new("sol", "SOLIDIFY"); m.thickness = th; m.offset = -1
    o.data.materials.append(mat(inner)); m.material_offset = 1; m.material_offset_rim = 1
    return o

def cut(o, cutter):
    m = o.modifiers.new("cut", "BOOLEAN"); m.operation = 'DIFFERENCE'; m.object = cutter; return o

def cone(r, h, color, unique=False):
    bpy.ops.mesh.primitive_cone_add(radius1=r, radius2=0, depth=h, location=(0, 0, 0), vertices=12); o = bpy.context.object
    for vv in o.data.vertices: vv.co.z += h / 2
    return setup(o, color, None, True, unique)

def build():
    sc, cam = scene_setup(world=BG, shadow=0.32); cam.data.clip_start = 0.01
    S = {"cam": cam}
    box((14, 0.3, 10), (0, 3.0, 4), WALL)
    box((14, 6, 0.9), (0, 0.5, -0.5), COUNTER)
    box((3.6, 3.2, 0.08), (0, 0.1, -0.03), STOVE)
    for a in range(4):
        g = box((3.0, 0.08, 0.06), (0, 0, 0.01), GRATE); g.rotation_euler = (0, 0, a * math.pi / 4)
    torus(0.45, 0.035, (0, 0, -0.01), GRATE)
    # llamas
    S["flames"] = []
    for k in range(18):
        a = k / 18 * math.tau; f = cone(0.06, 0.25, FLAME); f.location = (0.42 * math.cos(a), 0.42 * math.sin(a), -0.02)
        S["flames"].append(f)
    # cortador: quita la mitad delantera (y < 0)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -2.0, 1.0)); ct = bpy.context.object; ct.scale = (6, 4, 6); ct.hide_render = True
    S["ct"] = ct
    # cuerpo de la olla
    S["pot"] = cut(tube(R, ZT - ZB + 0.02, (0, 0, (ZT + ZB) / 2), STEEL, STEEL_IN, 0.05, bottom=True), ct)
    for sx in (-1, 1):
        h = box((0.35, 0.16, 0.08), (sx * (R + 0.15), 0.25, ZT - 0.12), BLACK)
    S["handle"] = box((1.4, 0.16, 0.1), (R + 0.75, 0.0, ZT - 0.06), BLACK)
    # agua
    S["water"] = cut(cyl(R - 0.05, 1.0, (0, 0, 0), WATER, v=64), ct)
    # comida
    S["food"] = []
    for k, (x, z) in enumerate(((-0.5, 0.25), (0.05, 0.2), (0.5, 0.28), (-0.15, 0.45))):
        f = sph(0.16, (x, -0.02, z), FOOD[k], scale=(1.2, 0.9, 0.85), unique=True); S["food"].append(f)
    S["bub"] = [sph(r, LEJOS, BUBBLE) for _, _, r in BUB]
    S["stm"] = [sph(r, LEJOS, STEAM) for _, _, r, _ in STM]
    S["jet"] = [sph(0.06, LEJOS, STEAM) for _ in range(14)]
    S["side"] = [sph(0.05, LEJOS, STEAM) for _ in range(8)]
    # tapa (grupo que sube/baja y gira)
    lid = empty(LEJOS); S["lid"] = lid
    S["lidm"] = cut(cyl(R + 0.06, 0.06, (0, 0, 0.03), STEEL, lid, v=64), ct)
    S["lidrim"] = cut(tube(R + 0.06, 0.12, (0, 0, -0.03), STEEL, STEEL_IN, 0.03), ct); S["lidrim"].parent = lid
    S["gasket"] = cut(torus(R - 0.01, 0.035, (0, 0, -0.035), GASKET, lid), ct)
    S["bulge"] = sph(0.05, LEJOS, GASKET, scale=(1.4, 1, 1))
    # asa superior con el cierre
    box((1.6, 0.16, 0.08), (0, 0.32, 0.22), BLACK, lid)
    for x in (-0.55, 0.55): box((0.08, 0.14, 0.18), (x, 0.32, 0.12), BLACK, lid)
    S["pin"] = cyl(0.035, 0.12, (0.25, 0.32, 0.2), RED, lid)
    # válvula principal (en corte): carcasa, muelle, vástago y contrapeso
    S["vhouse"] = cut(tube(0.07, 0.14, (0, 0, 0.13), STEEL, STEEL_IN, 0.012), ct); S["vhouse"].parent = lid
    S["spring"] = empty((0, 0, 0.07), lid)
    for k in range(7): torus(0.045, 0.008, (0, 0, k / 6), SPRING, S["spring"])
    S["cap"] = empty((0, 0, 0.21), lid)
    cyl(0.085, 0.06, (0, 0, 0.03), BLACK, S["cap"]); cyl(0.012, 0.16, (0, 0, -0.06), STEEL_IN, S["cap"])
    # válvulas de seguridad extra
    S["safe"] = [cyl(0.045, 0.06, (x, 0.45, 0.09), (0.45, 0.47, 0.52), lid, unique=True) for x in (-0.55, 0.55)]
    # flechas de empuje del vapor
    S["arr"] = [(bar_obj(RED, r=0.025), cone(0.06, 0.12, RED)) for _ in range(5)]
    # mano
    S["hand"] = sph(0.12, LEJOS, SKIN, scale=(1.3, 0.8, 0.7)); S["arm"] = bar_obj(SKIN, r=0.07)
    join_static([cam, S["flames"], ct, S["pot"], S["water"], S["food"], S["bub"], S["stm"], S["jet"], S["side"], lid, S["bulge"],
                 S["arr"], S["hand"], S["arm"]])
    return sc, S

def hide_bar(o): bar_set(o, LEJOS, LEJOS + Vector((0, 0, 0.01)))

def pressure(t):
    """bar por encima del ambiente (0 … 1, y algo más antes de que actúe la válvula)"""
    p = seg(t, T("el vapor se queda"), T("un bar", fin=True)) * 1.0
    p += 0.35 * seg(t, T("pero la presión no"), T("la levanta"))
    p -= 0.35 * seg(t, T("la levanta"), T("y sale un") + 0.4)
    if t < T("así que cierras"): p = 0.0
    if t < 5.0: p = 1.0
    p *= 1 - seg(t, T("hasta que no"), T("no se abre"))
    return p

def lid_closed(t):
    return t < T("en una cazuela") or t >= T("así que cierras") + 1.0

def pose(t, S):
    p = pressure(t)
    # tapa: arriba (abierta) en el tramo de la cazuela normal; baja al cerrar; al final se abre
    hz = 0.0
    if T("en una cazuela") <= t < T("así que cierras") + 1.0:
        up = seg(t, T("en una cazuela"), T("en una cazuela") + 0.8) * (1 - seg(t, T("pero") + 0.2, T("así que cierras") + 1.0))
        hz = 3.5 * up
    hz += 1.4 * seg(t, T("no se abre"), T("sígueme"))
    twist = 0.0
    if T("qué pasa si") <= t < T("así que la tapa"):
        twist = 0.12 * math.sin((t - T("intentas")) * 9) * seg(t, T("intentas"), T("intentas") + 0.3)
    S["lid"].location = Vector((0, 0, ZT + 0.06 + hz)); S["lid"].rotation_euler = (0, 0, twist)
    # válvula: se levanta con la presión
    lift = 0.0
    if t < 5.0: lift = 0.035 + 0.008 * math.sin(t * 40)
    if T("la levanta") - 0.2 <= t < T("y aquí viene"): lift = 0.035 * seg(t, T("la levanta") - 0.2, T("la levanta") + 0.2) + 0.008 * math.sin(t * 40)
    if t >= T("pones una válvula") - 0.3: S["spring"].location = Vector((0, 0, 0.07))
    sp_on = t < 5.0 or t >= T("pones una válvula")
    S["spring"].scale = (1, 1, (0.1 - lift * 1.4) / 1.0) if sp_on else (1e-3,) * 3
    S["cap"].location = Vector((0, 0, 0.21 + lift))
    # pasador del cierre
    pin = seg(t, T("un cierre"), T("se bloquea", fin=True)) * (1 - seg(t, T("no se abre") - 0.4, T("no se abre")))
    S["pin"].location = Vector((0.25, 0.32, 0.2 + 0.1 * pin))
    # válvulas de seguridad
    for k, o in enumerate(S["safe"]):
        on = T("dos o tres") + 0.4 * k <= t < T("y si todas")
        set_color(o, GREEN if on else (0.45, 0.47, 0.52))
    # fuego
    big = 1 + 0.9 * seg(t, T("subas el fuego") - 0.3, T("subas el fuego") + 0.3) * (1 - seg(t, T("pero") , T("así que cierras")))
    for k, f in enumerate(S["flames"]):
        fl = 1 + 0.25 * math.sin(t * 23 + k * 1.7)
        f.scale = (1, 1, fl * big)
    # agua y burbujas: hierve abierta; con presión deja de hervir hasta llegar a 120 °C
    S["water"].scale = (1, 1, WL - ZB - 0.05); S["water"].location = Vector((0, 0, ZB + 0.05 + (WL - ZB - 0.05) / 2))
    boil = 1.0
    if T("y con más") <= t < T("hasta los ciento"): boil = 1 - seg(t, T("y con más"), T("al agua le cuesta", fin=True))
    elif T("hasta los ciento") <= t < T("y a esa"): boil = seg(t, T("hasta los ciento"), T("veinte grados", fin=True))
    if T("en una cazuela") <= t < T("así que cierras"): boil = 1.0 + 0.6 * (big - 1)
    for k, (b, (x, ph, r)) in enumerate(zip(S["bub"], BUB)):
        if k >= int(len(BUB) * min(1, boil)): b.location = LEJOS; continue
        u = (t * 0.7 * (1 + 0.4 * (boil > 1.2)) + ph) % 1.0
        b.location = Vector((x + 0.03 * math.sin(t * 5 + k), -0.02, ZB + 0.08 + (WL - ZB - 0.1) * u))
    # vapor: con la tapa abierta sale y se escapa; cerrada queda atrapado en la cámara
    open_pot = T("en una cazuela") <= t < T("así que cierras") + 0.8
    for k, (s, (x, ph, r, a)) in enumerate(zip(S["stm"], STM)):
        if open_pot and t > T("en una cazuela") + 0.5:
            n_on = int(len(STM) * (0.35 + 0.65 * seg(t, T("ese fuego"), T("más vapor", fin=True))))
            if k >= n_on: s.location = LEJOS; continue
            u = (t * 0.45 + ph) % 1.0
            s.location = Vector((x * (1 + u), -0.02 - 0.3 * u, WL + 0.05 + 2.6 * u)); s.scale = (1 + 2 * u,) * 3
        elif lid_closed(t) and t >= T("así que cierras") + 0.8 and t < T("no se abre") and not (T("así que pones") <= t < T("por eso tu")):
            dens = 0.4 + 0.6 * min(1, p)
            if k >= int(len(STM) * dens): s.location = LEJOS; continue
            ww = t * (0.8 + 0.8 * p)
            s.location = Vector((0.85 * math.sin(ww + a), -0.03, WL + 0.12 + 0.28 * (0.5 + 0.5 * math.sin(ww * 1.3 + 2 * a))))
            s.scale = (0.75,) * 3
        elif t < 5.0 and k < 10:
            ww = t * 1.6; s.location = Vector((0.85 * math.sin(ww + a), -0.03, WL + 0.12 + 0.28 * (0.5 + 0.5 * math.sin(ww * 1.3 + 2 * a)))); s.scale = (1.2,) * 3
        else: s.location = LEJOS
    # chorro por la válvula
    jet_on = t < 5.0 or T("y sale un") - 0.2 <= t < T("y aquí viene") + 0.5
    for k, j in enumerate(S["jet"]):
        if not jet_on or hz > 0.01: j.location = LEJOS; continue
        u = (t * 2.2 + k / len(S["jet"])) % 1.0
        j.location = S["lid"].location + Vector((0.03 * math.sin(k * 2.1), -0.05, 0.3 + 1.4 * u)); j.scale = (0.6 + 3.5 * u,) * 3
    # goma deformada y vapor que sale por un lado
    a0 = T("se deforma")
    if a0 - 0.3 <= t < T("pero aún falta") + 0.3:
        bz = seg(t, a0 - 0.3, a0 + 0.4)
        S["bulge"].location = Vector((R + 0.06 + 0.05 * bz, 0.0, ZT + 0.03)); S["bulge"].scale = (1.4 * bz + 0.01, 1.2 * bz + 0.01, bz + 0.01)
    else: S["bulge"].location = LEJOS
    for k, sd in enumerate(S["side"]):
        if T("deja salir") <= t < T("pero aún falta") + 0.3:
            u = (t * 1.8 + k / 8) % 1.0
            sd.location = Vector((R + 0.15 + 1.1 * u, -0.05, ZT + 0.03 + 0.4 * u * u)); sd.scale = (0.6 + 2.5 * u,) * 3
        else: sd.location = LEJOS
    # flechas de empuje (vapor atrapado)
    a0, a1 = T("el vapor se queda"), T("al agua le cuesta")
    for k, (bb, tip) in enumerate(S["arr"]):
        if a0 <= t < a1:
            x = -0.7 + 0.35 * k; L = 0.12 + 0.22 * seg(t, T("y empuja"), T("la presión dentro", fin=True)) + 0.03 * math.sin(t * 8 + k)
            b0 = Vector((x, -0.06, ZT - 0.3)); b1 = b0 + Vector((0, 0, L)); bar_set(bb, b0, b1); tip.location = b1
        else: hide_bar(bb); tip.location = LEJOS
    # mano que intenta abrir
    if T("qué pasa si") <= t < T("hasta que no"):
        hp = S["lid"].location + Vector((0.5, 0.15, 0.3)) + Vector((0, 0, 0.3 * (1 - seg(t, T("qué pasa si"), T("intentas")))))
        S["hand"].location = hp; S["hand"].rotation_euler = (0, 0, twist)
        bar_set(S["arm"], hp, hp + Vector((1.2, -0.9, 0.9)))
    else: S["hand"].location = LEJOS; hide_bar(S["arm"])
    apply_cam(S["cam"], *camera(t))

def CAMS():
    tv = (0, 0, ZT + 0.3)
    return [
        (0.0, [(0, (0.15, -1.2, ZT + 0.65), (0, 0, ZT + 0.55), 40), (T("usando"), (0.6, -2.4, ZT + 0.5), (0, 0, ZT + 0.2), 36)]),
        (T("usando"), [(0, (0.9, -2.6, 0.35), (0, 0, 0.2), 32), (T("cómo lo hace"), (0.5, -3.4, 0.9), (0, 0, 0.5), 32)]),
        (T("cómo lo hace"), [(0, (0.0, -4.0, 1.4), (0, 0, 0.75), 32), (T("en una cazuela"), (0.3, -2.4, 1.4), (0, 0, 0.95), 34)]),
        (T("en una cazuela"), [(0, (-0.6, -4.6, 2.4), (0, 0, 0.9), 32), (T("y por mucho"), (-0.4, -4.3, 2.0), (0, 0, 0.8), 32),
                                (T("ese fuego"), (0.5, -4.6, 1.3), (0, 0, 0.6), 32), (T("pero"), (0.0, -5.6, 3.0), (0, 0, 1.6), 32)]),
        (T("pero"), [(0, (0.0, -5.6, 3.0), (0, 0, 1.8), 32), (T("así que cierras") + 1.2, (-0.4, -4.4, 2.2), (0, 0, 1.0), 32),
                     (T("la goma") + 0.6, (-1.2, -2.6, 1.6), (-0.9, 0, ZT), 36)]),
        (T("el vapor se queda"), [(0, (0.0, -3.4, 1.5), (0, 0, 0.95), 34), (T("con un bar"), (0.3, -3.8, 1.3), (0, 0, 0.75), 32)]),
        (T("y a esa"), [(0, (0.6, -2.6, 0.8), (0, 0, 0.4), 34), (T("pero la presión no"), (0.0, -3.2, 1.0), (0, 0, 0.6), 34)]),
        (T("pero la presión no"), [(0, (0.0, -4.0, 1.6), (0, 0, 0.9), 32), (T("así que pones"), (0.0, -3.6, 1.6), (0, 0, 0.95), 32)]),
        (T("así que pones"), [(0, (0.12, -0.75, ZT + 0.35), (0, 0, ZT + 0.22), 40), (T("la levanta"), (0.2, -0.85, ZT + 0.4), (0, 0, ZT + 0.28), 40),
                               (T("por eso tu"), (0.4, -1.9, ZT + 0.8), (0, 0, ZT + 0.6), 36), (T("y aquí viene"), (0.0, -3.8, 2.2), (0, 0, 1.3), 32)]),
        (T("y aquí viene"), [(0, (-0.3, -2.6, 2.4), (0, 0.2, ZT + 0.1), 34), (T("y si todas"), (-0.4, -2.8, 2.4), (0, 0.2, ZT + 0.1), 34)]),
        (T("y si todas"), [(0, (1.6, -2.2, 1.6), (R, 0, ZT), 36), (T("pero aún falta"), (1.9, -2.6, 1.7), (R + 0.2, 0, ZT), 36)]),
        (T("pero aún falta"), [(0, (0.2, -3.6, 2.4), (0.2, 0.2, ZT + 0.2), 32), (T("así que la tapa"), (0.5, -2.0, 2.2), (0.25, 0.3, ZT + 0.3), 34),
                                (T("hasta que no"), (0.4, -2.2, 2.1), (0.2, 0.3, ZT + 0.3), 34)]),
        (T("hasta que no"), [(0, (0.0, -4.2, 2.2), (0, 0, 1.2), 32), (DUR + 1, (0.0, -4.8, 2.8), (0, 0, 1.7), 32)]),
    ]

def camera(t):
    segs = CAMS(); k = 0
    for i, (st, _) in enumerate(segs):
        if t >= st: k = i
    st, ks = segs[k]
    ks = [(st if a == 0 else a, p, q, l) for a, p, q, l in ks]
    if ks[-1][0] <= t: ks = ks + [(t + 1, ks[-1][1], ks[-1][2], ks[-1][3])]
    return cam_state(t, ks, drift=0.01)

def anchors(sc, S, t):
    cam = S["cam"]; Pj = lambda v: proj(sc, cam, v)
    L = S["lid"].location
    return {"valve": Pj(L + Vector((0, 0, 0.3))), "spring": Pj(L + Vector((0, 0, 0.12))), "gasket": Pj(Vector((-R, -0.02, ZT + 0.03))),
            "water": Pj(Vector((0.3, -0.02, 0.4))), "flame": Pj(Vector((0.4, -0.4, 0.05))), "safe0": Pj(L + Vector((-0.55, 0.45, 0.15))),
            "safe1": Pj(L + Vector((0.55, 0.45, 0.15))), "bulge": Pj(Vector((R + 0.1, 0, ZT + 0.05))), "pin": Pj(L + Vector((0.25, 0.32, 0.35))),
            "head": Pj(Vector((0, -0.02, ZT - 0.15)))}

if __name__ == "__main__":
    run("ollaexpres", build, pose, anchors)
