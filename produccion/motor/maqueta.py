# Ayudas para escenas en estilo «maqueta de día»: tubos en corte, recorridos, cámara por tramos.
import bpy, math
from mathutils import Vector
from lib3d import setup, box, mat, ss, mix, PAL

LEJOS = (0, 0, -300)

# ---------- recorridos (polilíneas con longitud) ----------
def poly(pts):
    pts = [Vector(p) for p in pts]; L = [0.0]
    for a, b in zip(pts, pts[1:]): L.append(L[-1] + (b - a).length)
    return pts, L

def at(path, s):
    pts, L = path; s = max(0.0, min(L[-1], s))
    for i in range(len(pts) - 1):
        if L[i] <= s <= L[i + 1]: return pts[i].lerp(pts[i + 1], (s - L[i]) / max(L[i + 1] - L[i], 1e-6))
    return pts[-1]

def largo(path): return path[1][-1]

def arco(c, r, a0, a1, plano="xz", n=16):
    """puntos de un arco de circunferencia (ángulos en grados) en el plano xz (y fija) o xy (z fija)"""
    out = []
    for k in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * k / n)
        if plano == "xz": out.append((c[0] + r * math.cos(a), c[1], c[2] + r * math.sin(a)))
        else: out.append((c[0] + r * math.cos(a), c[1] + r * math.sin(a), c[2]))
    return out

# ---------- tubos ----------
def tubo(pts, r, color, grosor=0.0, tapas=False, unique=False):
    """Tubo a lo largo de una polilínea. grosor>0 → pared hueca (solidify). tapas=True → sólido (agua dentro)."""
    cu = bpy.data.curves.new("tb", "CURVE"); cu.dimensions = '3D'
    sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
    for p, q in zip(sp.points, pts): p.co = (q[0], q[1], q[2], 1)
    cu.bevel_depth = r; cu.bevel_resolution = 5; cu.use_fill_caps = tapas
    ob = bpy.data.objects.new("tb", cu); bpy.context.collection.objects.link(ob)
    dg = bpy.context.evaluated_depsgraph_get(); me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    bpy.data.objects.remove(ob); o = bpy.data.objects.new("tubo", me); bpy.context.collection.objects.link(o)
    setup(o, color, smooth=True, unique=unique)
    if grosor:
        m = o.modifiers.new("s", "SOLIDIFY"); m.thickness = grosor; m.offset = 1
    return o

def cortador(size, loc, color=None):
    """Caja invisible que corta (BOOLEAN DIFFERENCE). La cara cortada sale en color crema."""
    c = box(size, loc, color or PAL["corte"], unique=True); c.hide_render = True; c.display_type = 'WIRE'
    return c

def cortar(o, cutter, op='DIFFERENCE'):
    m = o.modifiers.new("b", "BOOLEAN"); m.operation = op; m.object = cutter; m.solver = 'EXACT'
    try: m.material_mode = 'TRANSFER'
    except Exception: pass
    return m

# ---------- cámara por tramos (sin pasarse de largo) ----------
def cam_lin(t, ks, drift=0.01):
    if t <= ks[0][0]: a = b = ks[0]; u = 0
    elif t >= ks[-1][0]: a = b = ks[-1]; u = 0
    else:
        for i in range(len(ks) - 1):
            if ks[i][0] <= t <= ks[i + 1][0]: break
        a, b = ks[i], ks[i + 1]; u = ss((t - a[0]) / max(b[0] - a[0], 1e-4))
    pos = Vector(a[1]).lerp(Vector(b[1]), u); tgt = Vector(a[2]).lerp(Vector(b[2]), u); lens = mix(a[3], b[3], u)
    pos += Vector((math.sin(t * 0.9), 0.7 * math.sin(t * 0.7), 0.8 * math.sin(t * 1.1))) * drift
    return pos, tgt, lens

def V(at_, off, lens=35):
    at_ = Vector(at_); return (tuple(at_ + Vector(off)), tuple(at_), lens)

class Claves:
    """k = Claves(); k.add(t, V(...), hold) … ; k.k es la lista para cam_lin"""
    def __init__(self): self.k = []
    def add(self, t, v, hold=0.0):
        if self.k and t <= self.k[-1][0]: t = self.k[-1][0] + 0.05
        self.k.append((t,) + v)
        if hold: self.k.append((t + hold,) + v)

def medio_tubo(pts, r, grosor, color, eje=(0, 1, 0), corte=None, unique=False):
    """Mitad trasera de un tubo hueco ya cortada (sin booleanas): la polilínea va en un plano perpendicular a `eje`
    (por defecto el plano XZ) y se ve el interior desde el lado -eje. Las caras del corte salen en color crema."""
    import bmesh
    eje = Vector(eje).normalized(); pts = [Vector(p) for p in pts]; n = len(pts); NS = 14
    me = bpy.data.meshes.new("mt"); bm = bmesh.new(); anillos = []
    for i, c in enumerate(pts):
        d = (pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized(); v = d.cross(eje).normalized()
        out, inn = [], []
        for k in range(NS + 1):
            a = math.pi * k / NS; dirv = v * math.cos(a) + eje * math.sin(a)
            out.append(bm.verts.new(c + dirv * (r + grosor))); inn.append(bm.verts.new(c + dirv * r))
        anillos.append((out, inn))
    caras_corte = []
    for i in range(n - 1):
        (o0, i0), (o1, i1) = anillos[i], anillos[i + 1]
        for k in range(NS):
            bm.faces.new((o0[k], o0[k + 1], o1[k + 1], o1[k])); bm.faces.new((i0[k], i1[k], i1[k + 1], i0[k + 1]))
        for k in (0, NS):
            caras_corte.append(bm.faces.new((o0[k], o1[k], i1[k], i0[k])))
    for f in caras_corte: f.material_index = 1
    bm.normal_update(); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("medio_tubo", me); bpy.context.collection.objects.link(o)
    o.data.materials.append(mat(color, unique)); o.data.materials.append(mat(corte or PAL["corte"]))
    for p in o.data.polygons: p.use_smooth = True
    return o
