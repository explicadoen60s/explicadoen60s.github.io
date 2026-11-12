"""Modelos 3D de estilo «maqueta de día» (referencia @conrazon_es): bordes redondeados, formas suaves y detalles
que hacen reconocible cada cosa a la primera. Úsalos en lugar de cajas sueltas: una casa es `casa(...)`, no un cubo.

Todas las funciones devuelven un empty padre (muévelo, gíralo o escálalo para animar) salvo `caja` y `cilindro`,
que devuelven el objeto. Las medidas van en metros de la escena; `s` escala el modelo entero.
Uso:  from modelos import *     (después de `from lib3d import *`)
"""
import math, random
import bpy, bmesh
from lib3d import setup, empty, PAL, mat

# ---------------- piezas básicas suaves ----------------
def _suavizar(me, ang=35):
    me.shade_smooth()
    try: me.set_sharp_from_angle(angle=math.radians(ang))
    except Exception: pass

def caja(size, loc, color, parent=None, r=None, rot=(0, 0, 0), seg=3, unique=False):
    """Caja con las aristas redondeadas (radio r; por defecto el 12 % del lado más corto). Medidas reales, escala 1."""
    sx, sy, sz = size
    r = min(sx, sy, sz) * 0.12 if r is None else min(r, min(sx, sy, sz) * 0.49)
    if min(sx, sy, sz) < 0.05: seg = min(seg, 1)        # piezas pequeñas: un chaflán basta (y el render va más rápido)
    if r < 0.002: r = 0
    me = bpy.data.meshes.new("caja"); bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts: v.co.x *= sx; v.co.y *= sy; v.co.z *= sz
    if r > 1e-4:
        bmesh.ops.bevel(bm, geom=list(bm.edges) + list(bm.verts), offset=r, segments=seg, profile=0.5, affect='EDGES')
    bm.to_mesh(me); bm.free(); _suavizar(me)
    o = bpy.data.objects.new("caja", me); bpy.context.collection.objects.link(o); o.location = loc; o.rotation_euler = rot
    return setup(o, color, parent, unique=unique)

def cilindro(rad, h, loc, color, parent=None, r=None, rot=(0, 0, 0), v=40, seg=3, unique=False):
    """Cilindro con el borde de las tapas redondeado."""
    me = bpy.data.meshes.new("cil"); bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=v, radius1=rad, radius2=rad, depth=h)
    r = min(rad, h) * 0.15 if r is None else r
    if r > 1e-4:
        bordes = [e for e in bm.edges if abs(e.verts[0].co.z - e.verts[1].co.z) < 1e-6 and abs(abs(e.verts[0].co.z) - h / 2) < 1e-6
                  and (e.verts[0].co.xy.length > rad * 0.99)]
        bmesh.ops.bevel(bm, geom=bordes, offset=r, segments=seg, profile=0.5, affect='EDGES')
    bm.to_mesh(me); bm.free(); _suavizar(me, 40)
    o = bpy.data.objects.new("cil", me); bpy.context.collection.objects.link(o); o.location = loc; o.rotation_euler = rot
    return setup(o, color, parent, unique=unique)

def bola(rad, loc, color, parent=None, escala=(1, 1, 1), sub=3, unique=False):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub, radius=rad, location=loc); o = bpy.context.object; o.scale = escala
    _suavizar(o.data, 180); return setup(o, color, parent, unique=unique)

def _hijo(o, p): o.parent = p; return o

# ---------------- naturaleza ----------------
def arbol(loc, s=1.0, parent=None, copa=None, seed=0):
    """Árbol de maqueta: tronco marrón y copa redonda de varias bolas."""
    r = random.Random(seed); e = empty(loc, parent)
    cilindro(0.07 * s, 0.6 * s, (0, 0, 0.3 * s), (0.50, 0.33, 0.20), e)
    col = copa or random.Random(seed + 7).choice([PAL["planta"], (0.42, 0.74, 0.32), (0.33, 0.64, 0.28)])
    bola(0.38 * s, (0, 0, 0.85 * s), col, e)
    for i in range(3):
        a = i * 2.1 + r.uniform(0, 0.5)
        bola(0.24 * s, (math.cos(a) * 0.25 * s, math.sin(a) * 0.25 * s, (0.72 + r.uniform(-0.05, 0.12)) * s), col, e)
    return e

def arbusto(loc, s=1.0, parent=None, seed=0):
    r = random.Random(seed); e = empty(loc, parent)
    for i in range(3):
        bola(0.18 * s * r.uniform(0.8, 1.15), ((i - 1) * 0.16 * s, r.uniform(-0.05, 0.05) * s, 0.14 * s), (0.40, 0.70, 0.30), e)
    return e

def planta(loc, s=1.0, parent=None, maceta=None):
    """Planta de interior en maceta (baños, cocinas, salones)."""
    e = empty(loc, parent)
    cilindro(0.16 * s, 0.26 * s, (0, 0, 0.13 * s), maceta or PAL["maceta"], e)
    cilindro(0.14 * s, 0.02 * s, (0, 0, 0.255 * s), PAL["tierra"], e, r=0.003)
    for i in range(7):
        a = i * math.tau / 7
        h = bola(0.06 * s, (math.cos(a) * 0.1 * s, math.sin(a) * 0.1 * s, 0.42 * s), PAL["planta"], e, escala=(0.6, 0.6, 2.4))
        h.rotation_euler = (math.sin(a) * 0.45, -math.cos(a) * 0.45, 0)
    return e

# ---------------- ciudad ----------------
def casa(loc, s=1.0, parent=None, pared=None, tejado=None, rot=0.0, plantas=1):
    """Casa unifamiliar: paredes claras, tejado a dos aguas de tejas, puerta y ventanas con marco blanco."""
    e = empty(loc, parent); e.rotation_euler = (0, 0, rot)
    pared = pared or (0.98, 0.93, 0.82); tejado = tejado or (0.85, 0.36, 0.26)
    w, d, h = 1.6 * s, 1.3 * s, (0.9 + 0.7 * (plantas - 1)) * s
    caja((w, d, h), (0, 0, h / 2), pared, e, r=0.03 * s)
    # tejado a dos aguas con alero
    ang = math.radians(32); lado = (d / 2 + 0.12 * s) / math.cos(ang)
    for sg in (-1, 1):
        t = caja((w + 0.24 * s, lado, 0.07 * s), (0, sg * (d / 4 + 0.03 * s), h + math.tan(ang) * d / 4), tejado, e, r=0.02 * s)
        t.rotation_euler = (-sg * ang, 0, 0)
        for k in range(4):   # hileras de tejas
            f = caja((w + 0.24 * s, 0.03 * s, 0.025 * s), (0, sg * (0.1 + k * 0.17) * s, h + math.tan(ang) * (d / 2 - (0.1 + k * 0.17) * s) + 0.05 * s),
                     (tejado[0] * 0.85, tejado[1] * 0.85, tejado[2] * 0.85), e, r=0.01 * s)
            f.rotation_euler = (-sg * ang, 0, 0)
    # hastiales (triángulos de pared bajo el tejado)
    for sx in (-1, 1):
        me = bpy.data.meshes.new("hastial"); bm = bmesh.new()
        hh = math.tan(ang) * d / 2
        vs = [bm.verts.new(v) for v in ((sx * w / 2, -d / 2, h), (sx * w / 2, d / 2, h), (sx * w / 2, 0, h + hh))]
        bm.faces.new(vs); bm.to_mesh(me); bm.free()
        o = bpy.data.objects.new("hastial", me); bpy.context.collection.objects.link(o); setup(o, pared, e)
    # chimenea
    caja((0.18 * s, 0.18 * s, 0.4 * s), (w * 0.28, d * 0.18, h + 0.35 * s), (0.75, 0.42, 0.33), e, r=0.02 * s)
    # puerta y ventanas
    caja((0.3 * s, 0.04 * s, 0.55 * s), (-w * 0.22, -d / 2 - 0.01 * s, 0.28 * s), (0.55, 0.36, 0.22), e, r=0.02 * s)
    for p in range(plantas):
        z = (0.55 + 0.7 * p) * s
        for x in ((w * 0.2,) if p == 0 else (-w * 0.22, w * 0.2)):
            ventana((x, -d / 2 - 0.01 * s, z), s, e)
    return e

def ventana(loc, s=1.0, parent=None, w=0.34, h=0.32, vidrio=(0.62, 0.82, 0.95)):
    e = empty(loc, parent)
    caja((w * s, 0.03 * s, h * s), (0, 0, 0), (1, 1, 1), e, r=0.012 * s)
    caja(((w - 0.07) * s, 0.04 * s, (h - 0.07) * s), (0, -0.006 * s, 0), vidrio, e, r=0.01 * s)
    caja((0.018 * s, 0.05 * s, (h - 0.07) * s), (0, -0.008 * s, 0), (1, 1, 1), e, r=0.004 * s)
    return e

def edificio(loc, pisos=5, s=1.0, parent=None, color=None, rot=0.0, ancho=1.6, fondo=1.4, simple=None):
    """Bloque de pisos con ventanas, balcones y azotea (para ciudades; mejor que un cubo)."""
    e = empty(loc, parent); e.rotation_euler = (0, 0, rot)
    color = color or random.Random(pisos * 13 + int(ancho * 10)).choice([(0.97, 0.86, 0.70), (0.93, 0.74, 0.62), (0.86, 0.90, 0.93), (0.98, 0.95, 0.88)])
    w, d, hp = ancho * s, fondo * s, 0.42 * s; h = pisos * hp + 0.1 * s
    caja((w, d, h), (0, 0, h / 2), color, e, r=0.03 * s)
    caja((w + 0.06 * s, d + 0.06 * s, 0.06 * s), (0, 0, h + 0.02 * s), (0.92, 0.89, 0.84), e, r=0.02 * s)  # cornisa
    if simple is None: simple = s < 0.5     # a lo lejos (ciudades enteras): una franja de ventanas por piso
    if simple:
        for p in range(pisos):
            z = (0.27 + p * 0.42) * s
            for cara in (-1, 1):
                caja((w * 0.86, 0.02 * s, 0.2 * s), (0, cara * (d / 2 + 0.005 * s), z), (0.62, 0.82, 0.95), e, r=0)
                caja((0.02 * s, d * 0.86, 0.2 * s), (cara * (w / 2 + 0.005 * s), 0, z), (0.62, 0.82, 0.95), e, r=0)
        return e
    n = max(2, int(w / (0.4 * s)))
    for p in range(pisos):
        z = (0.27 + p * 0.42) * s
        for i in range(n):
            x = -w / 2 + (i + 0.5) * w / n
            ventana((x, -d / 2 - 0.01 * s, z), s * 0.72, e)
        if p > 0 and p % 2 == 0:
            caja((w * 0.9, 0.12 * s, 0.03 * s), (0, -d / 2 - 0.06 * s, z - 0.16 * s), (0.96, 0.96, 0.96), e, r=0.01 * s)
    return e

def coche(loc, s=1.0, parent=None, color=None, rot=0.0):
    """Turismo de maqueta: carrocería redondeada, cabina con cristales y ruedas. Mira hacia +X."""
    e = empty(loc, parent); e.rotation_euler = (0, 0, rot)
    color = color or PAL["rojo"]
    caja((1.6 * s, 0.75 * s, 0.32 * s), (0, 0, 0.28 * s), color, e, r=0.1 * s)
    caja((0.9 * s, 0.68 * s, 0.32 * s), (-0.1 * s, 0, 0.55 * s), color, e, r=0.12 * s)
    caja((0.82 * s, 0.70 * s, 0.22 * s), (-0.1 * s, 0, 0.56 * s), (0.62, 0.80, 0.93), e, r=0.08 * s)   # cristales
    for fx in (-0.5, 0.5):
        for fy in (-1, 1):
            cilindro(0.16 * s, 0.12 * s, (fx * s, fy * 0.36 * s, 0.16 * s), (0.17, 0.17, 0.19), e, rot=(math.pi / 2, 0, 0), r=0.03 * s)
            cilindro(0.07 * s, 0.13 * s, (fx * s, fy * 0.36 * s, 0.16 * s), (0.82, 0.83, 0.85), e, rot=(math.pi / 2, 0, 0), r=0.01 * s)
    for fy in (-0.24, 0.24):
        bola(0.05 * s, (0.8 * s, fy * s, 0.32 * s), (1.0, 0.95, 0.70), e)   # faros
    return e

def persona(loc, s=1.0, parent=None, ropa=None, piel=(0.96, 0.78, 0.64), pelo=(0.30, 0.20, 0.14)):
    """Muñeco sencillo y simpático (para dar escala: ¿cuánto mide esto al lado de una persona?)."""
    e = empty(loc, parent)
    ropa = ropa or (0.25, 0.50, 0.85)
    for x in (-0.06, 0.06): cilindro(0.045 * s, 0.4 * s, (x * s, 0, 0.2 * s), (0.22, 0.25, 0.35), e, r=0.02 * s)
    caja((0.26 * s, 0.16 * s, 0.4 * s), (0, 0, 0.6 * s), ropa, e, r=0.07 * s)
    for x in (-0.16, 0.16): cilindro(0.035 * s, 0.34 * s, (x * s, 0, 0.62 * s), ropa, e, r=0.015 * s)
    bola(0.11 * s, (0, 0, 0.92 * s), piel, e)
    bola(0.115 * s, (0, 0.015 * s, 0.96 * s), pelo, e, escala=(1, 1, 0.65))
    return e

def farola(loc, s=1.0, parent=None):
    e = empty(loc, parent)
    cilindro(0.04 * s, 1.6 * s, (0, 0, 0.8 * s), (0.30, 0.32, 0.36), e)
    caja((0.3 * s, 0.1 * s, 0.06 * s), (0.12 * s, 0, 1.6 * s), (0.30, 0.32, 0.36), e, r=0.02 * s)
    bola(0.06 * s, (0.22 * s, 0, 1.55 * s), (1.0, 0.93, 0.6), e)
    return e

def calle(largo, loc, parent=None, ancho=1.6, rot=0.0, aceras=True):
    """Calle con asfalto, línea discontinua y aceras con bordillo."""
    e = empty(loc, parent); e.rotation_euler = (0, 0, rot)
    caja((largo, ancho, 0.04), (0, 0, 0.02), PAL["asfalto"], e, r=0.005)
    n = int(largo / 0.5)
    for i in range(n):
        caja((0.25, 0.05, 0.01), (-largo / 2 + (i + 0.5) * largo / n, 0, 0.045), (0.97, 0.97, 0.97), e, r=0.003)
    if aceras:
        for sg in (-1, 1):
            caja((largo, 0.45, 0.09), (0, sg * (ancho / 2 + 0.225), 0.045), (0.80, 0.80, 0.78), e, r=0.02)
    return e

# ---------------- casa por dentro ----------------
def inodoro(loc, s=1.0, parent=None, rot=0.0):
    """Inodoro con cisterna, taza, tapa y pulsador. Mira hacia -Y."""
    e = empty(loc, parent); e.rotation_euler = (0, 0, rot); b = (0.98, 0.98, 0.98)
    caja((0.42 * s, 0.2 * s, 0.4 * s), (0, 0.25 * s, 0.62 * s), b, e, r=0.05 * s)          # cisterna
    cilindro(0.04 * s, 0.02 * s, (0, 0.25 * s, 0.83 * s), (0.82, 0.84, 0.88), e, r=0.008 * s)   # pulsador
    cilindro(0.12 * s, 0.34 * s, (0, 0.02 * s, 0.17 * s), b, e, r=0.04 * s)                     # pie
    c = cilindro(0.22 * s, 0.14 * s, (0, -0.05 * s, 0.38 * s), b, e, r=0.05 * s); c.scale = (0.85, 1.15, 1)  # taza
    t = cilindro(0.21 * s, 0.03 * s, (0, -0.05 * s, 0.465 * s), (0.95, 0.95, 0.97), e, r=0.012 * s); t.scale = (0.85, 1.15, 1)
    return e

def lavabo(loc, s=1.0, parent=None, rot=0.0):
    e = empty(loc, parent); e.rotation_euler = (0, 0, rot)
    caja((0.6 * s, 0.45 * s, 0.6 * s), (0, 0, 0.3 * s), (0.62, 0.45, 0.30), e, r=0.03 * s)   # mueble
    caja((0.64 * s, 0.48 * s, 0.1 * s), (0, 0, 0.65 * s), (0.98, 0.98, 0.98), e, r=0.04 * s)
    grifo((0, 0.17 * s, 0.7 * s), s, e)
    return e

def grifo(loc, s=1.0, parent=None):
    e = empty(loc, parent); m = (0.82, 0.84, 0.88)
    cilindro(0.025 * s, 0.18 * s, (0, 0, 0.09 * s), m, e, r=0.01 * s)
    cilindro(0.018 * s, 0.14 * s, (0, -0.06 * s, 0.17 * s), m, e, rot=(math.pi / 2, 0, 0), r=0.006 * s)
    caja((0.03 * s, 0.1 * s, 0.02 * s), (0, 0.03 * s, 0.2 * s), m, e, r=0.008 * s)   # maneta
    return e

def cocina(loc, s=1.0, parent=None, ancho=2.4):
    """Bancada de cocina con armarios, encimera, placa con fuegos y horno."""
    e = empty(loc, parent); w = ancho * s
    caja((w, 0.6 * s, 0.85 * s), (0, 0, 0.425 * s), (0.45, 0.62, 0.86), e, r=0.02 * s)
    n = int(ancho / 0.6)
    for i in range(n):
        x = -w / 2 + (i + 0.5) * w / n
        caja((w / n - 0.04 * s, 0.02 * s, 0.75 * s), (x, -0.3 * s, 0.43 * s), (0.52, 0.69, 0.91), e, r=0.015 * s)
        caja((0.12 * s, 0.03 * s, 0.025 * s), (x, -0.32 * s, 0.75 * s), (0.85, 0.86, 0.88), e, r=0.008 * s)
    caja((w + 0.06 * s, 0.66 * s, 0.05 * s), (0, -0.01 * s, 0.875 * s), PAL["encimera"], e, r=0.015 * s)
    caja((0.6 * s, 0.5 * s, 0.015 * s), (0, 0, 0.905 * s), (0.15, 0.16, 0.18), e, r=0.01 * s)   # placa
    for fx in (-0.14, 0.14):
        for fy in (-0.11, 0.11):
            cilindro(0.08 * s, 0.006 * s, (fx * s, fy * s, 0.915 * s), (0.30, 0.31, 0.34), e, r=0.002 * s)
    return e

def olla(loc, s=1.0, parent=None, color=(0.80, 0.82, 0.86)):
    e = empty(loc, parent)
    cilindro(0.22 * s, 0.26 * s, (0, 0, 0.13 * s), color, e, r=0.03 * s)
    cilindro(0.23 * s, 0.03 * s, (0, 0, 0.27 * s), color, e, r=0.012 * s)
    bola(0.035 * s, (0, 0, 0.3 * s), (0.2, 0.2, 0.22), e)
    for sg in (-1, 1):
        caja((0.1 * s, 0.04 * s, 0.03 * s), (sg * 0.27 * s, 0, 0.2 * s), (0.2, 0.2, 0.22), e, r=0.012 * s)
    return e

def alfombrilla(loc, w=0.6, d=0.4, parent=None, color=None):
    return caja((w, d, 0.02), loc, color or PAL["rosa"], parent, r=0.01)

def rollo_papel(loc, s=1.0, parent=None):
    e = empty(loc, parent)
    cilindro(0.06 * s, 0.11 * s, (0, 0, 0), (1, 1, 1), e, rot=(0, math.pi / 2, 0), r=0.015 * s)
    cilindro(0.012 * s, 0.16 * s, (0, 0, 0), (0.82, 0.84, 0.88), e, rot=(0, math.pi / 2, 0), r=0.004 * s)
    return e

# ---------------- salón y dormitorio ----------------
def sofa(loc, s=1.0, parent=None, color=None, rot=0.0, ancho=1.4):
    """Sofá de tres plazas con respaldo, brazos y cojines. El respaldo queda en +Y."""
    e = empty(loc, parent); e.rotation_euler = (0, 0, rot); c = color or PAL["rosa"]; w = ancho * s
    oscuro = tuple(v * 0.85 for v in c)
    caja((w, 0.6 * s, 0.22 * s), (0, 0, 0.16 * s), oscuro, e, r=0.05 * s)
    caja((w - 0.06 * s, 0.2 * s, 0.42 * s), (0, 0.22 * s, 0.4 * s), c, e, r=0.08 * s)
    for sx in (-1, 1): caja((0.16 * s, 0.6 * s, 0.34 * s), (sx * (w / 2 - 0.08 * s), 0, 0.27 * s), c, e, r=0.07 * s)
    n = 3; cw = (w - 0.34 * s) / n
    for i in range(n): caja((cw - 0.02 * s, 0.42 * s, 0.1 * s), (-w / 2 + 0.17 * s + (i + 0.5) * cw, -0.05 * s, 0.32 * s), c, e, r=0.04 * s)
    for sx in (-1, 1): cilindro(0.025 * s, 0.06 * s, (sx * (w / 2 - 0.08 * s), 0, 0.03 * s), (0.35, 0.25, 0.18), e)
    return e

def cama(loc, s=1.0, parent=None, rot=0.0, manta=None):
    """Cama de matrimonio con cabecero, colchón, almohadas y manta. El cabecero queda en +Y."""
    e = empty(loc, parent); e.rotation_euler = (0, 0, rot)
    caja((1.3 * s, 1.9 * s, 0.25 * s), (0, 0, 0.14 * s), PAL["madera"], e, r=0.04 * s)
    caja((1.24 * s, 1.84 * s, 0.16 * s), (0, 0, 0.34 * s), (0.98, 0.98, 0.98), e, r=0.07 * s)
    caja((1.28 * s, 1.15 * s, 0.05 * s), (0, -0.36 * s, 0.43 * s), manta or PAL["turquesa"], e, r=0.025 * s)
    for sx in (-0.3, 0.3): caja((0.48 * s, 0.28 * s, 0.1 * s), (sx * s, 0.7 * s, 0.46 * s), (0.97, 0.97, 1.0), e, r=0.045 * s)
    caja((1.36 * s, 0.08 * s, 0.75 * s), (0, 0.97 * s, 0.37 * s), tuple(v * 0.85 for v in PAL["madera"]), e, r=0.035 * s)
    return e

def mesita(loc, s=1.0, parent=None, rot=0.0, ancho=0.45, alto=0.5, color=None):
    """Mueble bajo con cajón y tirador (mesilla, mesa del router…)."""
    e = empty(loc, parent); e.rotation_euler = (0, 0, rot); c = color or PAL["madera"]
    caja((ancho * s, 0.4 * s, alto * s), (0, 0, alto * s / 2), c, e, r=0.025 * s)
    caja((ancho * s * 0.86, 0.02 * s, alto * s * 0.32), (0, -0.2 * s, alto * s * 0.7), tuple(v * 1.06 for v in c), e, r=0.01 * s)
    caja((0.1 * s, 0.03 * s, 0.025 * s), (0, -0.215 * s, alto * s * 0.7), (0.85, 0.86, 0.88), e, r=0.008 * s)
    return e

def tele(loc, s=1.0, parent=None, rot=0.0, pantalla=(0.12, 0.14, 0.2)):
    """Televisión plana sobre su mueble. La pantalla mira hacia -Y."""
    e = empty(loc, parent); e.rotation_euler = (0, 0, rot)
    caja((1.0 * s, 0.32 * s, 0.32 * s), (0, 0, 0.16 * s), PAL["madera"], e, r=0.025 * s)
    caja((0.06 * s, 0.06 * s, 0.12 * s), (0, 0, 0.38 * s), (0.2, 0.2, 0.22), e, r=0.02 * s)
    caja((0.96 * s, 0.05 * s, 0.56 * s), (0, 0, 0.72 * s), (0.15, 0.15, 0.17), e, r=0.02 * s)
    caja((0.9 * s, 0.01 * s, 0.5 * s), (0, -0.026 * s, 0.72 * s), pantalla, e, r=0)
    return e

# ---------------- obras ----------------
def tuneladora(loc, s=1.0, parent=None, rot=0.0, vagones=4, color=None):
    """Tuneladora (TBM) de maqueta, avanza hacia +X: rueda de corte con radios y cuchillas delante, escudo amarillo,
    brazo que coloca los anillos de hormigón y tren de remolques con la cinta que saca la tierra hacia atrás.
    `s` es el radio del escudo. Hijos para animar: `tuneladora_pieza(e, "rueda")` (gira en su eje X local),
    `tuneladora_pieza(e, "brazo")` (gira en X). Largo total ≈ 1.5*s + vagones * 1.25*s."""
    e = empty(loc, parent); e.rotation_euler = (0, 0, rot)
    am = color or PAL["amarillo"]; acero = (0.74, 0.76, 0.80); oscuro = (0.22, 0.23, 0.26); R = s; L = 1.4 * s
    ry = (0, math.pi / 2, 0)
    cilindro(R, L, (-L / 2, 0, 0), am, e, rot=ry, r=0.06 * s)                           # escudo
    for k in range(3):                                                                    # aros del escudo
        cilindro(R * 1.01, 0.06 * s, (-0.2 * s - k * 0.45 * s, 0, 0), tuple(v * 0.82 for v in am), e, rot=ry, r=0.01 * s)
    # rueda de corte (gira)
    ru = empty((0.06 * s, 0, 0), e); ru.name = "rueda"; e["rueda"] = ru.name
    cilindro(R * 0.98, 0.1 * s, (0, 0, 0), acero, ru, rot=ry, r=0.03 * s)
    cilindro(R * 0.22, 0.2 * s, (0.06 * s, 0, 0), oscuro, ru, rot=ry, r=0.04 * s)
    for i in range(6):
        a = i * math.tau / 6
        b = caja((0.1 * s, 0.16 * s, R * 0.95), (0.08 * s, math.cos(a) * R * 0.47, math.sin(a) * R * 0.47), (0.35, 0.36, 0.40), ru, r=0.02 * s)
        b.rotation_euler = (a - math.pi / 2, 0, 0)
        for j in range(4):
            d = R * (0.3 + 0.18 * j)
            cilindro(0.045 * s, 0.05 * s, (0.15 * s, math.cos(a + 0.12) * d, math.sin(a + 0.12) * d), (0.85, 0.86, 0.9), ru, rot=ry, r=0.01 * s)
    # brazo erector de anillos (gira)
    br = empty((-L - 0.12 * s, 0, 0), e); br.name = "brazo"; e["brazo"] = br.name
    caja((0.12 * s, 0.12 * s, R * 0.75), (0, 0, R * 0.4), PAL["rojo"], br, r=0.03 * s)
    caja((0.18 * s, 0.3 * s, 0.1 * s), (0, 0, R * 0.78), oscuro, br, r=0.03 * s)
    # remolques con plataformas y cinta transportadora
    x = -L
    for k in range(vagones):
        lv = 1.15 * s; cx = x - 0.1 * s - lv / 2
        caja((lv, R * 1.1, 0.08 * s), (cx, 0, -R * 0.35), (0.85, 0.86, 0.88), e, r=0.02 * s)   # plataforma
        for sx in (-1, 1):
            for sy in (-1, 1):
                caja((0.06 * s, 0.06 * s, R * 0.75), (cx + sx * lv * 0.42, sy * R * 0.48, 0.0), am, e, r=0.015 * s)
        caja((lv, R * 1.0, 0.06 * s), (cx, 0, R * 0.38), am, e, r=0.02 * s)                     # techo
        caja((lv * 0.5, R * 0.4, R * 0.35), (cx, -R * 0.2, -R * 0.12), (0.30, 0.55, 0.85) if k % 2 else (0.92, 0.92, 0.94), e, r=0.04 * s)
        for sx in (-1, 1): cilindro(0.1 * s, 0.06 * s, (cx + sx * lv * 0.35, R * 0.4, -R * 0.5), oscuro, e, rot=(math.pi / 2, 0, 0), r=0.02 * s)
        x = cx - lv / 2
    largo_cinta = -L - x
    caja((largo_cinta + L * 0.6, 0.22 * s, 0.05 * s), (-(L * 0.4) - largo_cinta / 2 + 0.0, R * 0.25, R * 0.48), oscuro, e, r=0.015 * s)  # cinta
    e["largo"] = L + largo_cinta
    return e

def tuneladora_pieza(e, nombre):
    return bpy.data.objects[e[nombre]]
