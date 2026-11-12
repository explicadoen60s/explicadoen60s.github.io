# «Así frena un avión de 60 toneladas» (Avión, parte 2): maqueta de una pista con un avión de pasillo único que aterriza.
# Aerofrenos que se levantan (las flechas de sustentación encogen y las de peso crecen), inversores de empuje que abren
# compuertas y mandan el aire hacia delante, y en una segunda isla una rueda gigante cortada con la pila de discos de carbono:
# rotores que giran, estátores quietos, pistones que aprietan, discos que se ponen al rojo, balanza acero/carbono y ABS.
# La pista, las luces y los árboles se desplazan bajo el avión: la velocidad se ve en el suelo y en la pastilla (250 → 0 km/h).
# Planos (fotografía → motion; esquina libre arriba salvo indicación):
#  0,0 tren principal tocando pista (primer plano, humo) · 1,6 rueda de lado · 3,7 avión entero · 5,5 frontal 3/4 (60 t)
#  7,6 picado · 8,8 ala · 12,5 aerofrenos subiendo · 15 flechas de sustentación · 16,3 flechas de peso · 18,8 ruedas
#  20,6 motor · 22 compuertas · 24,7 aire hacia delante · 26,7 ala+motor · 27,5 ruedas · 29,4 coche en la vía de servicio
#  31,2 rueda gigante cortada · 33 discos · 35 estátores · 36,3 pistones (aprietan) · 38,4 isla entera · 40,3 balanza
#  43,1 rueda · 44,9 ruedas del avión calientes · 46,3 discos (1.000 °C) · 48,4 rojo vivo · 49,9 calor que sube
#  51,4 / 52,5 otro ángulo (30 min) · 55,7 rueda bloqueada y marca de frenazo · 57,5 ordenador · 60,1 suelta · 61,5 aprieta
#  62,8 pulsos · 64,1 coche (ABS) · 65,7 avión frenando · 67,6 empujón suave · 69,9 vuelta al primer plano (bucle).
import bpy, math, sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from modelos import *
from maqueta import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("frenoavion")
BLANCO = (0.97, 0.97, 0.98); AZUL = (0.20, 0.42, 0.85); GRIS = (0.62, 0.64, 0.68); OSCURO = (0.18, 0.19, 0.22)
CARB = (0.24, 0.24, 0.26); CARB2 = (0.36, 0.36, 0.39); NEUM = (0.15, 0.15, 0.17)
BW = Vector((0.0, -16.0, 1.9))          # centro de la rueda gigante (segunda isla)
BAL = BW + Vector((3.6, 0.3, -BW.z))     # balanza
PC = BW + Vector((-2.3, -1.4, -BW.z))      # ordenador del antibloqueo
E = [Vector((1.2, s * 2.3, 0.62)) for s in (-1, 1)]   # motores
RW = 0.28                                # radio de la rueda del avión
LW = 46.0                                # largo de la pista que se repite

# ---------------- velocidad y distancia ----------------
def kmh(t):
    if t >= T("sígueme") - 0.05: return 250.0
    return keyed(t, [(0, 250), (12.6, 250), (18.5, 218), (22.5, 205), (28.0, 150), (36.6, 132), (39.5, 85), (55.0, 40),
                     (65.5, 14), (68.6, 0.0)])
_S = [0.0]
for i in range(1, 7300): _S.append(_S[-1] + kmh(i * 0.01) * 0.035 * 0.01)
def dist(t):
    i = max(0, min(len(_S) - 2, int(t / 0.01))); u = t / 0.01 - i; return _S[i] + (_S[i + 1] - _S[i]) * u

def bloqueo(t):  # 1 = rueda bloqueada
    return 1.0 if T("bloquea") - 0.1 < t < T("ordenador") else 0.0

def abs_gap(t):  # separación de la pila: 1 = suelto, 0 = apretado
    if t < T("al frenar", fin=True): return 1.0
    if t < T("suelta"): return 0.0
    if t < T("vuelve a"): return seg(t, T("suelta"), T("suelta") + 0.3)
    if t < T("muchas veces"): return 1 - seg(t, T("vuelve a"), T("vuelve a") + 0.25)
    if t < T("como el abs", fin=True) + 0.3: return 0.5 + 0.5 * math.sin((t - T("muchas veces")) * 2 * math.pi * 3.0)
    return 0.0

def calor(t):  # 0 frío … 1 rojo vivo
    h = 0.25 * seg(t, T("se aprietan"), T("se aprietan") + 1.4)
    h = mix(h, 0.45, seg(t, T("aguanta"), T("brutal", fin=True)))
    h = mix(h, 1.0, seg(t, T("pueden pasar"), T("grados", fin=True)))
    h = mix(h, 0.3, seg(t, T("ordenador"), T("ordenador") + 1.2))
    return h

def color_calor(h, base):
    if h < 0.5: return tuple(mix(b, c, h / 0.5) for b, c in zip(base, (0.75, 0.18, 0.10)))
    return tuple(mix(b, c, (h - 0.5) / 0.5) for b, c in zip((0.75, 0.18, 0.10), (1.0, 0.62, 0.18)))

# ---------------- modelos propios ----------------
def rueda_avion(loc, parent):
    e = empty(loc, parent); s = empty((0, 0, 0), e)
    cilindro(RW, 0.17, (0, 0, 0), NEUM, s, rot=(math.pi / 2, 0, 0), r=0.05)
    hub = cilindro(RW * 0.55, 0.18, (0, 0, 0), GRIS, s, rot=(math.pi / 2, 0, 0), r=0.015, unique=True)
    for k in range(6):
        a = k * math.tau / 6
        bola(0.022, (math.cos(a) * RW * 0.35, -0.095, math.sin(a) * RW * 0.35), OSCURO, s)
    caja((RW * 0.9, 0.012, 0.05), (0, -0.092, 0), (0.95, 0.85, 0.2), s, r=0.004)   # marca para ver el giro
    return e, s, hub

def avion():
    root = empty((0, 0, 0)); P = {"root": root}
    cilindro(0.55, 8.4, (0.2, 0, 1.3), BLANCO, root, rot=(0, math.pi / 2, 0), r=0.1)
    bola(0.55, (4.4, 0, 1.27), BLANCO, root, escala=(1.9, 1.0, 0.95))                    # morro
    bola(0.55, (-4.0, 0, 1.42), BLANCO, root, escala=(2.6, 0.7, 0.6))                    # cola
    caja((0.7, 0.012, 0.22), (5.0, -0.43, 1.42), OSCURO, root, r=0.03, rot=(0, -0.35, 0.25))   # cabina
    caja((0.7, 0.012, 0.22), (5.0, 0.43, 1.42), OSCURO, root, r=0.03, rot=(0, -0.35, -0.25))
    caja((8.0, 0.02, 0.1), (0.0, -0.548, 1.12), AZUL, root, r=0.01)                      # franja
    caja((8.0, 0.02, 0.1), (0.0, 0.548, 1.12), AZUL, root, r=0.01)
    for i in range(16):
        x = -3.1 + i * 0.43
        for sy in (-1, 1): caja((0.13, 0.03, 0.17), (x, sy * 0.54, 1.42), (0.35, 0.55, 0.78), root, r=0.04)
    caja((0.22, 0.03, 0.5), (3.6, -0.545, 1.25), GRIS, root, r=0.03)                       # puerta
    # deriva y estabilizadores
    d = caja((1.6, 0.12, 1.5), (-4.4, 0, 2.2), AZUL, root, r=0.05); d.rotation_euler = (0, -0.45, 0)
    for sy in (-1, 1):
        h = caja((1.0, 1.9, 0.08), (-4.6, sy * 1.0, 1.55), BLANCO, root, r=0.03); h.rotation_euler = (0, 0, sy * 0.35)
    # alas con aerofrenos
    P["spoil"] = []; P["lift"] = []
    for sy in (-1, 1):
        ala = empty((0.6, sy * 0.4, 0.92), root); ala.rotation_euler = (0, 0, sy * 0.42)
        caja((1.9, 5.0, 0.13), (0, sy * 2.5, 0), BLANCO, ala, r=0.05)
        caja((0.5, 0.08, 0.5), (-0.4, sy * 5.0, 0.25), AZUL, ala, r=0.04)               # winglet
        for k in range(3):
            pv = empty((-0.05, sy * (1.4 + k * 1.0), 0.075), ala)
            caja((0.6, 0.9, 0.04), (-0.3, 0, 0.0), (0.55, 0.62, 0.74), pv, r=0.015)
            P["spoil"].append(pv)
        f = flecha3d((0.0, sy * 3.0, 0.2), (0, 0, 1), 1.3, 0.09, color=(0.25, 0.55, 0.95), parent=ala); P["lift"].append(f)
    # motores con inversores
    P["fan"] = []; P["doors"] = []
    for e in E:
        cilindro(0.38, 1.5, tuple(e), (0.85, 0.86, 0.9), root, rot=(0, math.pi / 2, 0), r=0.06)
        cilindro(0.33, 0.04, (e.x + 0.74, e.y, e.z), OSCURO, root, rot=(0, math.pi / 2, 0), r=0.01)
        caja((0.8, 0.12, 0.35), (e.x - 0.1, e.y, e.z + 0.38), GRIS, root, r=0.04)          # pilón
        cilindro(0.2, 0.3, (e.x - 0.85, e.y, e.z), OSCURO, root, rot=(0, math.pi / 2, 0), r=0.03)   # tobera
        fan = empty((e.x + 0.77, e.y, e.z), root); P["fan"].append(fan)
        bola(0.1, (0.05, 0, 0), (0.9, 0.9, 0.92), fan, escala=(1.4, 1, 1))
        for k in range(8):
            b = caja((0.02, 0.06, 0.3), (0, 0, 0.17), (0.55, 0.57, 0.62), fan, r=0.008); b.rotation_euler = (k * math.tau / 8, 0, 0)
            b.location = (0, -math.sin(k * math.tau / 8) * 0.17, math.cos(k * math.tau / 8) * 0.17)
        for sy in (-1, 1):
            pv = empty((e.x - 0.15, e.y + sy * 0.37, e.z), root)
            caja((0.55, 0.06, 0.42), (-0.28, 0, 0), (0.55, 0.62, 0.74), pv, r=0.02)
            P["doors"].append((pv, sy))
    # tren de aterrizaje
    P["ruedas"] = []; P["hubs"] = []
    for sy in (-1, 1):
        cilindro(0.06, 0.62, (0.3, sy * 1.1, 0.62), GRIS, root, r=0.01)
        caja((0.12, 0.45, 0.08), (0.3, sy * 1.1, 0.31), GRIS, root, r=0.02)
        for dy in (-0.14, 0.14):
            e, s, hub = rueda_avion((0.3, sy * 1.1 + dy * 1.0, RW + 0.03), root); P["ruedas"].append(s); P["hubs"].append(hub)
    cilindro(0.05, 0.6, (3.9, 0, 0.55), GRIS, root, r=0.01)
    for dy in (-0.1, 0.1):
        e, s, hub = rueda_avion((3.9, dy, 0.2), root); e.scale = (0.68,) * 3; P["ruedas"].append(s)
    return P

def sector_toro(R, r, c, color, a0=180, a1=450, n=54, m=18):
    """neumático en corte: toro (eje Y) sin el cuarto de arriba-delante; las caras cortadas, en crema"""
    import bmesh
    me = bpy.data.meshes.new("toro"); bm = bmesh.new(); rings = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n); ring = []
        for j in range(m):
            b = j * math.tau / m; rr = R + r * math.cos(b)
            ring.append(bm.verts.new((c.x + rr * math.cos(a), c.y + r * math.sin(b), c.z + rr * math.sin(a))))
        rings.append(ring)
    for i in range(n):
        for j in range(m):
            k = (j + 1) % m; bm.faces.new((rings[i][j], rings[i][k], rings[i + 1][k], rings[i + 1][j]))
    for ring in (rings[0], rings[-1]):
        f = bm.faces.new(ring); f.material_index = 1
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("toro", me); bpy.context.collection.objects.link(o)
    o.data.materials.append(mat(color)); o.data.materials.append(mat(PAL["corte"]))
    for p in o.data.polygons: p.use_smooth = p.material_index == 0
    return o

def sector_anillo(ri, ro, y0, y1, c, color, a0=180, a1=450, n=54):
    """llanta en corte: tubo grueso (eje Y) sin el cuarto de arriba-delante"""
    import bmesh
    me = bpy.data.meshes.new("anillo"); bm = bmesh.new(); Q = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n); ca, sa = math.cos(a), math.sin(a)
        Q.append([bm.verts.new((c.x + rr * ca, c.y + yy, c.z + rr * sa)) for rr, yy in ((ri, y0), (ro, y0), (ro, y1), (ri, y1))])
    for i in range(n):
        for j in range(4):
            k = (j + 1) % 4; bm.faces.new((Q[i][j], Q[i][k], Q[i + 1][k], Q[i + 1][j]))
    for q in (Q[0], Q[-1]):
        f = bm.faces.new(q); f.material_index = 1
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("anillo", me); bpy.context.collection.objects.link(o)
    o.data.materials.append(mat(color)); o.data.materials.append(mat(PAL["corte"]))
    return o

def rueda_gigante(S):
    """Rueda de avión enorme en corte: neumático, llanta, pila de discos de carbono y pistones."""
    giro = empty(tuple(BW)); S["giro"] = giro
    sector_toro(1.25, 0.45, BW, NEUM)                                   # neumático (le falta el cuarto de delante)
    sector_anillo(0.80, 0.88, -0.5, 0.5, BW, (0.80, 0.82, 0.86))         # llanta
    cilindro(0.86, 0.06, (BW.x, BW.y + 0.53, BW.z), (0.72, 0.74, 0.78), rot=(math.pi / 2, 0, 0), r=0.02)   # tapa trasera
    tapa = cilindro(0.42, 0.06, (0, -0.55, 0), (0.86, 0.87, 0.9), giro, rot=(math.pi / 2, 0, 0), r=0.02)
    for k in range(8):   # tornillos del buje (se ven girar)
        a = k * math.tau / 8
        cilindro(0.04, 0.05, (math.cos(a) * 0.3, -0.59, math.sin(a) * 0.3), OSCURO, giro, rot=(math.pi / 2, 0, 0), r=0.01)
    caja((0.06, 0.03, 0.3), (0, -0.6, 0.15), PAL["rojo"], giro, r=0.01)
    S["discos"] = []
    for i in range(9):
        rotor = i % 2 == 0
        if rotor:
            e = empty((0, 0, 0), giro)
            d = cilindro(0.72, 0.075, (0, 0, 0), CARB, e, rot=(math.pi / 2, 0, 0), r=0.01, unique=True)
            for k in range(8):
                a = k * math.tau / 8
                caja((0.1, 0.075, 0.08), (math.cos(a) * 0.76, 0, math.sin(a) * 0.76), (0.85, 0.66, 0.2), e, r=0.01,
                     rot=(0, -a, 0))
        else:
            e = empty(tuple(BW))
            d = cilindro(0.66, 0.075, (0, 0, 0), CARB2, e, rot=(math.pi / 2, 0, 0), r=0.01, unique=True)
            cilindro(0.24, 0.08, (0, 0, 0), (0.55, 0.57, 0.62), e, rot=(math.pi / 2, 0, 0), r=0.01)
        S["discos"].append((e, d, rotor))
    S["eje"] = cilindro(0.18, 2.2, tuple(BW), (0.62, 0.64, 0.68), rot=(math.pi / 2, 0, 0), r=0.03)
    # carcasa de pistones (detrás, +Y)
    caja((1.2, 0.3, 1.2), (BW.x + 0.1, BW.y + 0.75, BW.z + 0.15), (0.55, 0.57, 0.62), r=0.06)
    S["placa"] = empty((BW.x, BW.y + 0.5, BW.z))
    cilindro(0.7, 0.06, (0, 0, 0), (0.75, 0.76, 0.8), S["placa"], rot=(math.pi / 2, 0, 0), r=0.01)
    for a in (0.6, 1.6, 2.6):
        cilindro(0.09, 0.3, (math.cos(a) * 0.45, 0.15, math.sin(a) * 0.45), (0.85, 0.2, 0.2), S["placa"], rot=(math.pi / 2, 0, 0), r=0.02)
    S["fpres"] = [flecha3d((BW.x - 0.35 - 0.18 * k, BW.y + 1.2, BW.z + 0.55 + 0.12 * k), (0, -1, 0), 0.7, 0.05) for k in range(2)]
    S["fcalor"] = [flecha3d((BW.x + dx, BW.y + dy, BW.z + 1.8), (0, 0, 1), 0.9, 0.07, color=(1.0, 0.45, 0.15)) for dx, dy in ((-0.5, 0), (0.4, -0.3), (0.1, 0.4))]
    # soporte
    caja((0.6, 1.4, 0.26), (BW.x, BW.y, 0.13), (0.95, 0.75, 0.2), r=0.05)

def balanza(S):
    caja((0.9, 0.6, 0.12), (BAL.x, BAL.y, 0.06), OSCURO, r=0.04)
    cilindro(0.08, 1.5, (BAL.x, BAL.y, 0.8), GRIS, r=0.02)
    S["brazo"] = empty((BAL.x, BAL.y, 1.6))
    caja((2.6, 0.1, 0.1), (0, 0, 0), GRIS, S["brazo"], r=0.03)
    S["platos"] = []
    for sx, col, txt in ((-1, (0.82, 0.84, 0.88), "ACERO"), (1, CARB, "CARBONO")):
        p = empty((sx * 1.25, 0, -0.05), S["brazo"])
        cilindro(0.5, 0.05, (0, 0, -0.35), (0.92, 0.75, 0.25), p, r=0.015)
        for dx in (-0.35, 0.35): bar_set(bar_obj(GRIS, 0.012, parent=p), (dx, 0, -0.35), (0, 0, 0))
        cilindro(0.42, 0.14, (0, 0, -0.25), col, p, r=0.03)
        S["platos"].append(p)

def ordenador(S):
    S["pc"] = empty(tuple(PC))
    caja((0.6, 0.45, 0.8), (0, 0, 0.4), (0.85, 0.86, 0.9), S["pc"], r=0.06)
    S["pantalla"] = caja((0.42, 0.02, 0.3), (0, -0.23, 0.55), (0.2, 0.8, 0.4), S["pc"], r=0.02, unique=True)
    S["led"] = bola(0.05, (0.18, -0.23, 0.22), (0.2, 0.9, 0.3), S["pc"], unique=True)
    S["cable"] = tubo([(PC.x, PC.y + 0.2, 0.15), (PC.x - 0.4, PC.y + 1.4, 0.15), (BW.x + 0.3, BW.y + 0.9, 0.3)], 0.04, OSCURO)

# ---------------- build ----------------
def build():
    sc, cam = scene_setup(world=PAL["cielo"], shadow=0.25); entorno_claro(sc)
    S = {"cam": cam}
    nubes(9, (0, 14, 6), 16, 2.0, 2.0, s=1.8, seed=3)
    nubes(4, (0, -24, 6), 8, 1.5, 1.0, s=1.4, seed=9)
    isla(40.0, 16.0, (0, 0, 0), capas=[(PAL["cesped"], 0.15), (PAL["hormigon"], 0.25), (PAL["tierra"], 0.6), (PAL["tierra2"], 0.8)])
    caja((40.0, 4.8, 0.03), (0, 0, 0.015), PAL["asfalto"], r=0.005)
    caja((40.0, 1.3, 0.03), (0, -5.4, 0.015), PAL["asfalto"], r=0.005)                     # vía de servicio
    for sy in (-1, 1): caja((40.0, 0.08, 0.035), (0, sy * 2.2, 0.02), (0.97, 0.97, 0.97), r=0.005)
    # cosas que pasan (la pista se desplaza bajo el avión)
    S["pasa"] = []
    for i in range(23):
        S["pasa"].append((caja((1.0, 0.1, 0.012), (0, 0, 0.034), (0.97, 0.97, 0.97), r=0.004), i * 2.0, 0.0, 0.034))
    for i in range(23):
        for sy in (-1, 1):
            o = bola(0.07, (0, 0, 0), (1.0, 0.85, 0.3)); S["pasa"].append((o, i * 2.0 + 1.0, sy * 2.5, 0.07))
    for i in range(18):
        S["pasa"].append((caja((0.5, 0.06, 0.01), (0, 0, 0.032), (0.97, 0.97, 0.97), r=0.003), i * 2.55, -5.4, 0.032))
    rnd = random.Random(4)
    for i in range(14):
        e = arbol((0, 0, 0), rnd.uniform(0.9, 1.4), seed=i * 3)
        S["pasa"].append((e, i * 3.3 + rnd.uniform(0, 1.5), 4.8 + rnd.uniform(0, 1.0), 0.0))
        e = arbusto((0, 0, 0), 1.3, seed=i)
        S["pasa"].append((e, i * 3.3 + rnd.uniform(0, 1.5), -7.6, 0.0))
    for i in range(5):
        e = edificio((0, 0, 0), pisos=3, s=0.7, color=(0.9, 0.92, 0.95), ancho=3.0, fondo=1.6)
        S["pasa"].append((e, i * 9.2 + 2, 6.9, 0.0))
    P = avion(); S.update(P)
    # humo del contacto
    S["humo"] = [bola(0.16, (0, 0, -50), (0.96, 0.96, 0.97), sub=1) for _ in range(8)]
    S["marca"] = [caja((1, 0.15, 0.006), (0, 0, -50), (0.08, 0.08, 0.09), r=0) for _ in range(2)]
    # flechas de peso y de empuje
    S["peso"] = [flecha3d((0.3, sy * 1.1, 3.0), (0, 0, -1), 1.0, 0.1) for sy in (-1, 1)]
    S["aire"] = [flecha3d(LEJOS, (1, 0, 0), 1.0, 0.07) for _ in range(4)]
    S["empuje"] = flecha3d(LEJOS, (1, 0, 0), 1.6, 0.13)
    S["coche"] = coche((0, 0, 0), 0.9, color=(0.95, 0.75, 0.2))
    # segunda isla: la rueda gigante en corte
    isla(10.0, 7.0, (BW.x + 0.6, BW.y, 0), capas=[(PAL["hormigon"], 0.15), (PAL["tierra"], 0.45), (PAL["tierra2"], 0.6)])
    for k in range(5): caja((0.5, 0.12, 0.01), (BW.x - 4.0 + k * 1.6, BW.y - 3.0, 0.005), PAL["amarillo"], r=0.003)
    planta((BW.x - 3.6, BW.y + 2.6, 0), 1.6)
    rueda_gigante(S); balanza(S); ordenador(S)
    dyn = [cam, S["root"], [p[0] for p in S["pasa"]], S["humo"], S["marca"], S["peso"], S["aire"], S["empuje"], S["coche"],
           S["giro"], [d[0] for d in S["discos"]], S["placa"], S["fpres"], S["fcalor"], S["brazo"], S["pc"], S["cable"], S["eje"]]
    join_static(dyn)
    return sc, S

# ---------------- pose ----------------
def touch(t):
    """altura y cabeceo del avión: aterriza al principio (y otra vez en el bucle final)"""
    t0 = T("sígueme") if t >= T("sígueme") - 0.05 else 0.0
    u = seg(t, t0, t0 + 0.95)
    return 0.32 * (1 - u), 0.07 * (1 - seg(t, t0 + 0.6, t0 + 2.2))

def pose(t, S):
    s = dist(t)
    for o, x0, y0, z0 in S["pasa"]:
        x = ((x0 - s) % LW) - LW / 2
        k = max(0.0, min(1.0, (19.6 - abs(x)) / 0.8))
        o.location = (x, y0, z0) if k > 0.01 else (x, y0, -60)
        if o.type == 'EMPTY': o.scale = (max(k, 0.01),) * 3
    dz, pitch = touch(t)
    S["root"].location = (0, 0, dz); S["root"].rotation_euler = (0, -pitch, 0)
    # ruedas del avión
    ang = -s / RW / 0.035 * 0.035 * 1.0
    pulso = 1.0
    if T("suelta") <= t < T("como el abs", fin=True) + 0.3: pulso = abs_gap(t)
    for i, r in enumerate(S["ruedas"]):
        if dz > 0.01 and i < 4: r.rotation_euler = (0, 0, 0); continue
        if bloqueo(t) and i < 4: r.rotation_euler.y = r.get("ang_bloq", 0.0); continue
        a = -s / (RW if i < 4 else RW * 0.68)
        r.rotation_euler = (0, a, 0); r["ang_bloq"] = a
    h = calor(t) * (0.8 if t < T("aguanta") else 1.0)
    for hub in S["hubs"]: set_color(hub, color_calor(h if t > T("despegue") - 0.3 else 0, GRIS))
    # humo al tocar pista
    for k, b in enumerate(S["humo"]):
        b.location = (0, 0, -50)
        for t0 in (0.0, T("sígueme")):
            u = (t - (t0 + 0.85)) / 1.4
            if 0 <= u <= 1:
                sy = -1 if k < 4 else 1; j = k % 4
                b.location = (0.3 - 0.5 * u * (1 + j * 0.6), sy * 1.1 + (j - 1.5) * 0.12, 0.12 + 0.25 * u)
                b.scale = (0.5 + 3.2 * u * (1 - u) + 0.2 * j,) * 3
    # marca de frenazo con la rueda bloqueada
    if T("bloquea") - 0.1 < t < T("muchas veces"):
        sl = T("bloquea") - 0.1
        L = max(0.02, dist(min(t, T("ordenador"))) - dist(sl)); off = dist(t) - dist(min(t, T("ordenador")))
        for m, y in zip(S["marca"], (-1.24, -0.96)):
            m.scale = (L, 1, 1); m.location = (0.3 - L / 2 - off, y, 0.034)
    else:
        for m in S["marca"]: m.location = (0, 0, -50)
    # aerofrenos y flechas de sustentación / peso
    sp = seg(t, T("se levantan"), T("alas", fin=True)) * (1 - seg(t, T("sígueme") - 0.3, T("sígueme")))
    for pv in S["spoil"]: pv.rotation_euler = (0, 0.85 * sp, 0)
    lift = 1.0 - 0.85 * seg(t, T("rompen"), T("sustentación", fin=True))
    show_lift = T("se levantan") + 0.6 < t < T("así las ruedas")
    for f in S["lift"]: f.scale = (max(lift, 0.05) if show_lift else 0.001,) * 3
    pw = seg(t, T("todo el peso"), T("las ruedas", fin=True))
    show_w = T("todo el peso") - 0.1 < t < T("luego")
    for f in S["peso"]:
        f.scale = ((0.6 + 0.5 * pw) if show_w else 0.001, (0.6 + 0.5 * pw) if show_w else 0.001, (0.4 + 1.0 * pw) if show_w else 0.001)
        f.location.z = 1.95 + 1.4 * (0.4 + pw) + dz
    # motores: ventilador y compuertas del inversor
    for f in S["fan"]: f.rotation_euler.x = t * 14
    op = seg(t, T("se abren"), T("compuertas", fin=True)) * (1 - seg(t, T("pero no son"), T("pero no son") + 0.6))
    for pv, sy in S["doors"]: pv.rotation_euler.z = -sy * 0.75 * op
    va = seg(t, T("desvían"), T("hacia delante", fin=True)) * (1 - seg(t, T("pero no son"), T("pero no son") + 0.4))
    big = 1 + 0.5 * seg(t, T("al revés"), T("al revés") + 0.6)
    for k, f in enumerate(S["aire"]):
        e = E[k // 2]; sy = 1 if k % 2 else -1
        if va > 0.02:
            ph = ((t * 1.6 + k * 0.37) % 1.0)
            f.location = (e.x - 0.35 + 0.9 * ph, e.y + sy * (0.45 + 0.25 * ph), e.z + 0.05)
            f.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(Vector((1, sy * 0.45, 0)).normalized())
            f.scale = (va * big,) * 3
        else: f.location = LEJOS
    # empujón suave al final
    pe = seg(t, T("solo ese"), T("empujón", fin=True)) * (1 - seg(t, T("sígueme") - 0.3, T("sígueme")))
    if pe > 0.02:
        S["empuje"].location = (3.2, 0, 2.2 + dz); S["empuje"].scale = (pe * (1 + 0.1 * math.sin(t * 8)),) * 3
    else: S["empuje"].location = LEJOS
    # coche por la vía de servicio (va casi a la misma velocidad que el avión)
    S["coche"].location = (-6.0 + 1.2 * math.sin(t * 0.4), -5.55, 0.03)
    # ---- rueda gigante ----
    if t < T("al frenar"): w = 2.2
    elif t < T("suelta"): w = mix(2.2, 0.25, seg(t, T("al frenar"), T("se aprietan", fin=True) + 0.5))
    else: w = 0.25 + 2.0 * abs_gap(t)
    S["giro"].rotation_euler.y = -_wint(t)
    g = abs_gap(t); gap = 0.045 * g
    th = 0.075; L = 9 * th + 8 * gap
    for i, (e, d, rotor) in enumerate(S["discos"]):
        y = -L / 2 + th / 2 + i * (th + gap) - 0.05
        if rotor: e.location = (0, y, 0)
        else: e.location = (BW.x, BW.y + y, BW.z)
        hh = calor(t)
        set_color(d, color_calor(hh, CARB if rotor else CARB2))
    S["placa"].location = (BW.x, BW.y + L / 2 + 0.08 - 0.05, BW.z)
    pr = (1 - g) * (1 if T("al frenar") - 0.2 < t < T("y aquí") or T("suelta") - 0.2 < t < T("por eso no") else 0)
    for k, f in enumerate(S["fpres"]):
        f.scale = (max(pr, 0.001),) * 3
    hc = seg(t, T("y el calor"), T("y el calor") + 0.8) * (1 - seg(t, T("bloquea") - 0.6, T("bloquea")))
    for k, f in enumerate(S["fcalor"]):
        f.scale = (max(hc, 0.001),) * 3
        f.location.z = BW.z + 1.7 + ((t * 0.6 + k * 0.33) % 1.0) * 0.6 * hc
    # balanza: el acero pesa más
    bb = seg(t, T("el carbono pesa"), T("el carbono pesa") + 1.2)
    S["brazo"].rotation_euler.y = -0.28 * bb + 0.02 * math.sin(t * 3) * bb
    for p in S["platos"]: p.rotation_euler.y = 0.28 * bb
    # ordenador
    pc = seg(t, T("un ordenador") - 0.3, T("un ordenador") + 0.2)
    S["pc"].scale = (max(pc, 0.01),) * 3; S["cable"].hide_render = pc < 0.5
    on = T("un ordenador") < t < T("por eso no")
    blink = on and (math.sin(t * 2 * math.pi * 3) > 0)
    set_color(S["led"], (1.0, 0.25, 0.2) if blink else (0.2, 0.9, 0.3))
    set_color(S["pantalla"], (0.95, 0.85, 0.2) if blink else (0.2, 0.8, 0.4))
    apply_cam(S["cam"], *camara(t))

_W = [0.0]
def _w(t):
    if t < T("al frenar"): return 2.2
    if t < T("suelta"): return mix(2.2, 0.2, seg(t, T("al frenar"), T("se aprietan", fin=True) + 0.5))
    return 0.2 + 2.0 * abs_gap(t)
for i in range(1, 7300): _W.append(_W[-1] + _w(i * 0.01) * 0.01)
def _wint(t):
    i = max(0, min(len(_W) - 2, int(t / 0.01))); return _W[i]

# ---------------- cámara (con cortes) ----------------
def V_(sujeto, off, lens=35):
    """el sujeto queda en la mitad de arriba del encuadre (deja el centro al subtítulo)"""
    s = Vector(sujeto); o = Vector(off); d = o.length
    return (tuple(s + o), tuple(s - Vector((0, 0, 0.13 * d * 35 / lens))), lens)

_K = []
def add(t, v, cut=True):
    _K.append((t, v, cut))

def CAM():
    _K.clear()
    RU = (0.3, -1.1, 0.32); MO = (1.2, -2.3, 0.62); AL = (0.3, -3.1, 1.05)
    add(0.0, V_(RU, (-3.2, -2.3, 0.3), 38))
    add(1.6, V_(RU, (-2.4, -3.0, 0.45), 38), cut=False)
    add(T("y tiene"), V_((0.5, 0, 1.2), (2.5, -11.0, 2.6), 30))
    add(T("cómo frena"), V_((1.2, 0, 1.3), (8.5, -7.5, 2.4), 30))
    add(T("vamos a"), V_((0.0, 0, 1.0), (-6.0, -9.5, 7.0), 28))
    add(T("lo primero"), V_(AL, (-2.2, -3.4, 2.4), 34))
    add(T("nada más"), V_(AL, (-1.0, -3.8, 2.1), 34), cut=False)
    add(T("se levantan"), V_((-0.5, -2.6, 1.1), (-2.6, -3.4, 1.3), 36))
    add(T("rompen"), V_((0.5, -3.2, 1.5), (4.0, -4.6, 1.2), 32))
    add(T("todo el peso"), V_((0.3, -0.4, 1.4), (0.8, -8.2, 1.0), 30))
    add(T("así las ruedas"), V_(RU, (-2.6, -1.9, 0.25), 42))
    add(T("luego"), V_(MO, (2.6, -3.0, 0.5), 34))
    add(T("se abren"), V_((0.6, -2.4, 0.62), (1.5, -3.5, -0.1), 38))
    add(T("el motor sigue"), V_((1.6, -2.4, 0.75), (3.8, -3.2, 1.3), 30))
    add(T("pero al"), V_((1.2, -2.4, 0.75), (4.2, -2.6, 0.9), 32), cut=False)
    add(T("y por último"), V_(RU, (-1.3, -2.4, 0.55), 36))
    add(T("pero no son"), V_((-6.0, -5.55, 0.45), (2.2, -1.6, 1.0), 34))
    add(T("dentro de"), V_(BW, (-3.4, -4.0, 1.9), 30))
    add(T("pila"), V_(BW + Vector((-0.3, -0.1, 0.4)), (-1.8, -2.0, 1.2), 38), cut=False)
    add(T("otros están"), V_(BW + Vector((-0.3, 0.0, 0.4)), (-2.4, -1.4, 1.4), 38))
    add(T("al frenar"), V_(BW + Vector((-0.3, 0.3, 0.4)), (-2.2, -1.3, 1.6), 36), cut=False)
    add(T("y aquí viene"), V_(BW + Vector((1.6, 0, 0.3)), (-1.5, -7.0, 2.2), 30))
    add(T("el carbono pesa"), V_(BAL + Vector((0, 0, 1.25)), (-0.8, -5.0, 1.5), 32))
    add(T("y aguanta"), V_(BW, (-3.0, -3.8, 1.5), 32))
    add(T("en un despegue"), V_(RU, (-2.2, -2.4, 0.5), 40))
    add(T("los discos pueden"), V_(BW + Vector((-0.3, 0, 0.3)), (-1.9, -2.1, 1.1), 38))
    add(T("se ponen"), V_(BW + Vector((-0.35, 0, 0.35)), (-1.3, -1.5, 0.9), 42))
    add(T("y el calor"), V_(BW + Vector((-0.0, 0, 0.9)), (-2.6, -4.8, 1.4), 30))
    add(T("después de"), V_(BW + Vector((-0.2, 0, 0.6)), (-3.9, -2.6, 2.4), 32))
    add(T("hasta media"), V_(BW + Vector((-0.2, 0, 0.6)), (-2.2, -3.6, 0.9), 34), cut=False)
    add(T("y si una"), V_((-0.4, -1.1, 0.3), (-2.6, -2.0, 0.35), 36))
    add(T("un ordenador"), V_(PC + Vector((0.6, 0.3, 0.9)), (-1.6, -3.6, 1.6), 32))
    add(T("suelta"), V_(BW + Vector((-0.3, 0, 0.3)), (-1.9, -2.1, 1.1), 38))
    add(T("y vuelve"), V_(BW + Vector((-0.3, 0, 0.3)), (-1.5, -2.4, 1.4), 38), cut=False)
    add(T("muchas veces"), V_(BW + Vector((-0.6, -0.4, 0.2)), (-2.8, -3.4, 1.4), 32))
    add(T("como el abs"), V_((-6.0, -5.55, 0.45), (-2.2, -1.6, 1.0), 34))
    add(T("por eso no"), V_((0.5, 0, 1.2), (1.2, -9.5, 2.0), 30))
    add(T("solo ese"), V_((2.8, 0, 1.4), (4.2, -5.0, 1.4), 32))
    add(T("hacia delante", 2) + 0.4, V_((2.8, 0, 1.4), (5.2, -3.8, 1.2), 32), cut=False)
    add(T("sígueme"), V_(RU, (-3.2, -2.3, 0.3), 38))
    add(DUR + 1, V_(RU, (-2.4, -3.0, 0.45), 38), cut=False)
    return list(_K)

_CK = None
def camara(t):
    global _CK
    if _CK is None: _CK = CAM()
    ks = _CK
    i = max(j for j in range(len(ks)) if ks[j][0] <= t) if t >= ks[0][0] else 0
    a = ks[i]; b = ks[i + 1] if i + 1 < len(ks) else ks[i]
    (pa, ta, la) = a[1]
    if b[2]:   # el siguiente plano entra por corte: este hace un empujón suave (8 %) y se mueve un poco de lado
        u = ss((t - a[0]) / max(b[0] - a[0], 1e-3)); pa, ta = Vector(pa), Vector(ta)
        d = pa - ta; lado = d.cross(Vector((0, 0, 1))).normalized() * d.length * 0.06
        pos = ta + d * (1 - 0.08 * u) + lado * (u - 0.5); tgt = ta; lens = la
    else:
        u = ss((t - a[0]) / max(b[0] - a[0], 1e-3)); (pb, tb, lb) = b[1]
        pos = Vector(pa).lerp(Vector(pb), u); tgt = Vector(ta).lerp(Vector(tb), u); lens = mix(la, lb, u)
    pos = pos + Vector((math.sin(t * 0.9), 0.7 * math.sin(t * 0.7), 0.8 * math.sin(t * 1.1))) * 0.01
    return pos, tgt, lens

def anchors(sc, S, t):
    cam = S["cam"]; P = lambda v: proj(sc, cam, v); dz = S["root"].location.z
    return {"rueda": P((0.3, -1.1, 0.6 + dz)), "avion": P((0.5, 0, 2.0 + dz)), "morro": P((4.5, 0, 2.0 + dz)), "ala": P((0.3, -3.1, 1.4 + dz)),
            "motor": P((1.2, -2.3, 1.1 + dz)), "coche": P((-6.0, -5.55, 1.0)), "rg": P(BW + Vector((0, 0, 1.7))),
            "pila": P(BW + Vector((-0.4, 0, 0.8))), "bal": P(BAL + Vector((0, 0, 1.6))), "pc": P(PC + Vector((0, 0, 1.0))),
            "marca": P((-0.6, -1.1, 0.4))}

if __name__ == "__main__":
    run("frenoavion", build, pose, anchors)
