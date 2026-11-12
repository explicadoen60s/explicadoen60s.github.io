# Utilidades comunes para las escenas estilizadas (Blender Workbench)
import bpy, bmesh, math, os, sys, json
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

FPS = 30; RES = (1080, 1920)
HERE = os.path.dirname(os.path.abspath(__file__))

def lin(c): return tuple(v ** 2.2 for v in c)
MATS = {}
def mat(rgb, unique=False):
    key = rgb
    if key in MATS and not unique: return MATS[key]
    m = bpy.data.materials.new("m%d" % len(MATS)); m.diffuse_color = (*lin(rgb), 1)
    if not unique: MATS[key] = m
    return m

def setup(o, color, parent=None, smooth=False, unique=False):
    if color is not None: o.data.materials.append(mat(color, unique))
    if smooth and hasattr(o.data, "polygons"):
        for p in o.data.polygons: p.use_smooth = True
    if parent: o.parent = parent
    return o

def box(size, loc, color, parent=None, rot=(0, 0, 0), unique=False):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot); o = bpy.context.object; o.scale = size
    return setup(o, color, parent, unique=unique)

def cyl(r, depth, loc, color, parent=None, rot=(0, 0, 0), v=32, smooth=True, unique=False):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, location=loc, rotation=rot, vertices=v); o = bpy.context.object
    return setup(o, color, parent, smooth, unique)

def sph(r, loc, color, parent=None, scale=(1, 1, 1), seg=24, unique=False):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=seg, ring_count=seg // 2); o = bpy.context.object; o.scale = scale
    return setup(o, color, parent, True, unique)

def torus(R, r, loc, color, parent=None, rot=(0, 0, 0), unique=False):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, location=loc, rotation=rot, major_segments=48, minor_segments=10)
    o = bpy.context.object; return setup(o, color, parent, True, unique)

def empty(loc=(0, 0, 0), parent=None):
    o = bpy.data.objects.new("e", None); bpy.context.collection.objects.link(o); o.location = loc
    if parent: o.parent = parent
    return o

def rounded_slab(w, h, r, thick, loc, color, parent=None, seg=8, unique=False):
    """rectángulo redondeado extruido (tarjetas, pantallas...). Base en z=0 local, centrado en x,y."""
    me = bpy.data.meshes.new("slab"); bm = bmesh.new(); pts = []
    for cx, cy, a0 in ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180), (w / 2 - r, -h / 2 + r, 270)):
        for k in range(seg + 1):
            a = math.radians(a0 + 90 * k / seg); pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    vb = [bm.verts.new((x, y, 0)) for x, y in pts]; vt = [bm.verts.new((x, y, thick)) for x, y in pts]
    bm.faces.new(list(reversed(vb))); bm.faces.new(vt)
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n; bm.faces.new((vb[i], vb[j], vt[j], vt[i]))
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("slab", me); bpy.context.collection.objects.link(o); o.location = loc
    return setup(o, color, parent, unique=unique)

def text3d(s, loc, size, color, parent=None, extrude=0.02, rot=(0, 0, 0), align='CENTER', unique=False):
    bpy.ops.object.text_add(location=loc, rotation=rot); o = bpy.context.object
    o.data.body = s; o.data.size = size; o.data.extrude = extrude; o.data.align_x = align; o.data.align_y = 'CENTER'
    return setup(o, color, parent, unique=unique)

def bar_obj(color, r=0.006, parent=None, unique=False):
    bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=1, location=(0, 0, 0), vertices=12); o = bpy.context.object
    for vv in o.data.vertices: vv.co.z += 0.5
    setup(o, color, parent, True, unique); o["r"] = r; return o

def bar_set(o, p0, p1):
    p0, p1 = Vector(p0), Vector(p1); d = p1 - p0; L = max(d.length, 1e-5)
    o.location = p0; o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())
    o.scale = (o["r"], o["r"], L)

def set_color(o, rgb):
    o.active_material.diffuse_color = (*lin(rgb), 1)

def scene_setup(world=(0.6, 0.8, 0.95), light_rot=35, shadow=0.28):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = 'BLENDER_WORKBENCH'; sc.render.resolution_x, sc.render.resolution_y = RES; sc.render.resolution_percentage = 100
    sc.render.fps = FPS; sc.view_settings.view_transform = 'Standard'; sc.display.render_aa = 'FXAA'
    sh = sc.display.shading; sh.light = 'STUDIO'; sh.studio_light = 'paint.sl'; sh.color_type = 'MATERIAL'
    sh.show_shadows = True; sh.shadow_intensity = shadow
    sh.show_cavity = True; sh.cavity_type = 'BOTH'; sh.cavity_ridge_factor = 0.6; sh.cavity_valley_factor = 0.8
    sh.curvature_ridge_factor = 0.6; sh.curvature_valley_factor = 0.7
    sh.use_world_space_lighting = True; sh.studiolight_rotate_z = math.radians(light_rot)
    sc.display.light_direction = (-0.45, -0.55, 0.7); sc.display.shadow_shift = 0.05; sc.display.shadow_focus = 0.3
    w = bpy.data.worlds.new("w"); sc.world = w; w.color = lin(world)
    bpy.ops.object.camera_add(); cam = bpy.context.object; sc.camera = cam; cam.data.clip_start = 0.01; cam.data.clip_end = 5000
    return sc, cam

# ---------- tiempo ----------
def ss(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def seg(t, a, b): return ss((t - a) / (b - a))
def mix(a, b, u): return a + (b - a) * u
def vmix(a, b, u): return Vector(a).lerp(Vector(b), u)
def win01(t, a, b, fi=0.3, fo=0.3):
    if t <= a or t >= b: return 0.0
    return min(ss((t - a) / fi), ss((b - t) / fo))

def keyed(t, keys):
    """keys: [(t, valor)] con valores Vector/float/tupla; interpolación suave por tramos"""
    if t <= keys[0][0]: return keys[0][1]
    for (a, va), (b, vb) in zip(keys, keys[1:]):
        if a <= t <= b:
            u = ss((t - a) / max(b - a, 1e-4))
            if isinstance(va, (int, float)): return mix(va, vb, u)
            return Vector(va).lerp(Vector(vb), u)
    return keys[-1][1]

def catmull(p0, p1, p2, p3, u):
    return 0.5 * ((2 * p1) + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u + (-p0 + 3 * p1 - 3 * p2 + p3) * u ** 3)

def cam_state(t, ks, drift=0.006):
    for i in range(len(ks) - 1):
        if ks[i][0] <= t <= ks[i + 1][0]: break
    a, b = ks[i], ks[i + 1]
    u = max(0, min(1, (t - a[0]) / (b[0] - a[0]))); u = u * u * (3 - 2 * u) * 0.5 + u * 0.5
    g = lambda j, k: Vector(ks[max(0, min(len(ks) - 1, j))][k])
    pos = catmull(g(i - 1, 1), g(i, 1), g(i + 1, 1), g(i + 2, 1), u)
    tgt = catmull(g(i - 1, 2), g(i, 2), g(i + 1, 2), g(i + 2, 2), u)
    lens = mix(a[3], b[3], u)
    pos += Vector((math.sin(t * 0.9), 0.7 * math.sin(t * 0.7), 0.8 * math.sin(t * 1.1))) * drift
    return pos, tgt, lens

def apply_cam(cam, pos, tgt, lens):
    cam.location = pos; cam.rotation_euler = (Vector(tgt) - pos).to_track_quat('-Z', 'Y').to_euler(); cam.data.lens = lens

def proj(sc, cam, v):
    c = world_to_camera_view(sc, cam, Vector(v)); return [round(c.x, 4), round(1 - c.y, 4), round(c.z, 3)]

def join_static(dyn_objs):
    dyn = set()
    def add(o):
        if isinstance(o, bpy.types.Object):
            dyn.add(o); [add(c) for c in o.children]
        elif isinstance(o, (list, tuple)): [add(x) for x in o]
    for o in dyn_objs: add(o)
    stat = [o for o in bpy.context.scene.objects if o.type == 'MESH' and o not in dyn and o.parent is None]
    if len(stat) < 2: return
    bpy.ops.object.select_all(action='DESELECT')
    for o in stat: o.select_set(True)
    bpy.context.view_layer.objects.active = stat[0]; bpy.ops.object.join()

def run(name, build, pose, anchors):
    """bucle de render: python3 escena.py f0 f1 [step]"""
    f0, f1 = int(sys.argv[1]), int(sys.argv[2]); step = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    out = os.path.join(HERE, "frames", name if step == 1 else name + "_prev"); os.makedirs(out, exist_ok=True)
    sc, S = build(); anc = {}
    for f in range(f0, f1 + 1, step):
        t = f / FPS; pose(t, S); bpy.context.view_layer.update(); anc[f] = anchors(sc, S, t)
        p = os.path.join(out, f"{f:05d}.png")
        if os.environ.get("ANCHORS_ONLY") or (os.path.exists(p) and step == 1): continue
        sc.render.filepath = p; bpy.ops.render.render(write_still=True)
    json.dump(anc, open(os.path.join(HERE, "frames", f"anchors_{name}_{f0}_{f1}_{step}.json"), "w"))
    print("DONE", f0, f1)

# ---------- estilo «maqueta de día» (referencia @conrazon_es, 12-nov-2026) ----------
# Mundo claro y alegre: cielo celeste con nubes low-poly, el objeto en su sitio real (baño, cocina, calle)
# sobre una «isla» de terreno cortada que enseña las capas de tierra. Colores planos, saturados y suaves.
PAL = {
    "cielo": (0.70, 0.85, 0.96), "nube": (1.0, 1.0, 1.0),
    "menta": (0.58, 0.84, 0.74), "turquesa": (0.42, 0.78, 0.80), "junta": (0.97, 0.98, 0.98),
    "cesped": (0.47, 0.80, 0.36), "cesped2": (0.40, 0.72, 0.31), "tierra": (0.55, 0.36, 0.22), "tierra2": (0.42, 0.27, 0.17),
    "hormigon": (0.78, 0.78, 0.76), "asfalto": (0.30, 0.31, 0.34), "encimera": (0.98, 0.74, 0.47), "madera": (0.86, 0.62, 0.36),
    "pared": (0.97, 0.94, 0.86), "corte": (0.99, 0.96, 0.88), "agua": (0.40, 0.68, 0.95), "rojo": (0.92, 0.24, 0.20),
    "amarillo": (1.0, 0.80, 0.18), "rosa": (0.97, 0.55, 0.66), "planta": (0.36, 0.70, 0.30), "maceta": (0.24, 0.46, 0.80),
}

def entorno_claro(sc, cielo=None):
    """Fondo celeste (sustituye al fondo oscuro). Llamar después de scene_setup."""
    sc.world.color = lin(cielo or PAL["cielo"])
    sh = sc.display.shading; sh.shadow_intensity = 0.22; sh.cavity_ridge_factor = 0.45; sh.cavity_valley_factor = 0.6

def nube(loc, s=1.0, parent=None, seed=0):
    """Nube low-poly: varias esferas facetadas blancas."""
    import random; r = random.Random(seed); out = []
    for i in range(5):
        dx = (i - 2) * 0.55 * s + r.uniform(-0.1, 0.1) * s; rad = s * (0.55 + 0.35 * (1 - abs(i - 2) / 2) + r.uniform(-0.08, 0.08))
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=rad, location=(loc[0] + dx, loc[1] + r.uniform(-0.2, 0.2) * s, loc[2] + r.uniform(-0.1, 0.25) * s))
        o = bpy.context.object; setup(o, PAL["nube"], parent); o.scale.z = 0.75; out.append(o)
    return out

def nubes(n, centro, ancho, alto, prof=0.0, s=1.0, seed=1):
    import random; r = random.Random(seed)
    return [nube((centro[0] + r.uniform(-ancho, ancho), centro[1] + r.uniform(-prof, prof), centro[2] + r.uniform(-alto, alto)), s * r.uniform(0.7, 1.3), seed=seed + i) for i in range(n)]

def isla(w, d, loc, capas=None, top="cesped", parent=None):
    """Bloque de terreno cortado tipo maqueta: superficie arriba y capas de tierra debajo.
    capas: [(color, grosor), …] de arriba abajo. Devuelve la cota de la superficie."""
    capas = capas or [(PAL[top], 0.12), (PAL["tierra"], 0.35), (PAL["tierra2"], 0.45)]
    z = loc[2]
    for col, g in capas:
        box((w, d, g), (loc[0], loc[1], z - g / 2), col, parent); z -= g
    return loc[2]

def azulejos(w, h, loc, rot=(0, 0, 0), color=None, paso=0.22, junta=0.012, parent=None):
    """Pared de azulejos: placa de color con juntas blancas en cuadrícula (pared en el plano XZ antes de rotar)."""
    e = empty(loc, parent); e.rotation_euler = rot
    box((w, 0.04, h), (0, 0, 0), color or PAL["menta"], e)
    nx, nz = int(w / paso), int(h / paso)
    for i in range(1, nx + 1):
        x = -w / 2 + i * paso
        if x < w / 2: box((junta, 0.05, h), (x, -0.005, 0), PAL["junta"], e)
    for j in range(1, nz + 1):
        z = -h / 2 + j * paso
        if z < h / 2: box((w, 0.05, junta), (0, -0.005, z), PAL["junta"], e)
    return e

def flecha3d(base, direccion, largo=1.0, grosor=0.08, color=None, parent=None):
    """Flecha gruesa (fuerza, presión, corriente). Devuelve un empty padre: muévelo, escálalo o gíralo para animarla."""
    d = Vector(direccion).normalized(); e = empty(base, parent)
    e.rotation_mode = 'QUATERNION'; e.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d)
    col = color or PAL["rojo"]; cuerpo = largo * 0.62
    cyl(grosor, cuerpo, (0, 0, cuerpo / 2), col, e, v=16)
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=grosor * 2.3, depth=largo * 0.38, location=(0, 0, cuerpo + largo * 0.19))
    setup(bpy.context.object, col, e)
    return e
