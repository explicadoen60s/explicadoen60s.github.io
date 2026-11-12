# «La punta de tu cinta métrica está suelta a propósito»: maqueta de taller sobre una isla cortada. La cinta sale disparada
# con el gancho bailando; después se inventa pieza a pieza: cinta de acero que se enrolla, muelle en espiral que se carga
# y la recoge (¡zas!), la cinta plana que se dobla y la curva de teja que la pone rígida (más de 1 m en el aire), el gancho
# de 1 mm que robaría o sumaría ese milímetro, el gancho suelto que sale y entra justo su grosor, y el botón de freno.
# Planos (fotografía → motion): 0 punta en primer plano (libre: arriba) · 2,9 gancho · 4,9 maqueta · 8 cinta larga ·
# 11 bobina · 16 muelle · 18 tirar · 21 ¡zas! · 24 cinta que se dobla · 26,5 perfil de teja · 28,6 voladizo · 32,4 mesa ·
# 34,6 gancho · 36,7 grosor · 41 por fuera · 44,5 pared · 48 tirar/empujar · 55 primeras marcas · 60,6 botón · vuelta al inicio.
import bpy, bmesh, math, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from modelos import *
from maqueta import *
from marcas import cargar
from mathutils import Vector

T, DUR = cargar("cintametrica")
CASE = (0.92, 0.24, 0.20); BLADE = (1.0, 0.82, 0.16); STEEL = (0.8, 0.82, 0.86); DARK = (0.16, 0.16, 0.18)
XC = -0.6; ZC = 1.25; XEX = -0.95; ZB = 0.96; XE = -1.5; LMAX = 2.3; TAB = 0.025
NX, NY, HW = 60, 7, 0.15

def blade_mesh():
    me = bpy.data.meshes.new("cinta"); bm = bmesh.new(); V = []
    for i in range(NX + 1):
        fila = []
        for j in range(NY):
            fila.append((bm.verts.new((0, 0, 0)), bm.verts.new((0, 0, 0))))
        V.append(fila)
    for i in range(NX):
        for j in range(NY - 1):
            bm.faces.new((V[i][j][0], V[i + 1][j][0], V[i + 1][j + 1][0], V[i][j + 1][0]))
            bm.faces.new((V[i][j][1], V[i][j + 1][1], V[i + 1][j + 1][1], V[i + 1][j][1]))
        for j in (0, NY - 1):
            bm.faces.new((V[i][j][0], V[i][j][1], V[i + 1][j][1], V[i + 1][j][0]))
    for j in range(NY - 1):
        bm.faces.new((V[NX][j][0], V[NX][j][1], V[NX][j + 1][1], V[NX][j + 1][0]))
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("cinta", me); bpy.context.collection.objects.link(o)
    return setup(o, BLADE)

def blade_z(x, kd):
    return ZB - kd * max(0.0, XE - x) ** 2

def blade_set(o, L, curv, kd):
    co = []
    for i in range(NX + 1):
        x = XEX - max(L, 0.001) * i / NX; z0 = blade_z(x, kd)
        for j in range(NY):
            y = -HW + 2 * HW * j / (NY - 1); zp = curv * 0.035 * (y / HW) ** 2
            co += [x, y, z0 + zp, x, y, z0 + zp - 0.008]
    o.data.vertices.foreach_set("co", co); o.data.update()

def build():
    sc, cam = scene_setup(world=PAL["cielo"], shadow=0.25); entorno_claro(sc)
    S = {"cam": cam}
    nubes(9, (-1, 7, 1.4), 7, 1.6, 1.0, s=0.9, seed=5)
    # isla de taller: suelo de madera y capas de tierra
    isla(4.4, 2.2, (-1.0, 0.3, 0.0), capas=[(PAL["madera"], 0.08), (PAL["hormigon"], 0.2), (PAL["tierra"], 0.35), (PAL["tierra2"], 0.35)])
    azulejos(4.4, 2.2, (-1.0, 1.4, 1.1), color=PAL["turquesa"]); box((4.4, 0.04, 2.2), (-1.0, 1.43, 1.1), PAL["turquesa"])
    # mesa
    box((2.6, 1.2, 0.06), (-0.2, 0.15, 0.87), (0.9, 0.66, 0.4))
    for sx, sy in ((-1.4, -0.35), (-1.4, 0.65), (0.98, -0.35), (0.98, 0.65)): box((0.07, 0.07, 0.84), (sx, sy, 0.42), (0.75, 0.52, 0.3))
    # detalles: lápiz, tablón, maceta y caja de herramientas
    box((0.5, 0.025, 0.025), (0.5, 0.45, 0.915), (1.0, 0.75, 0.2), rot=(0, 0, 0.4)); box((0.9, 0.25, 0.05), (0.4, -0.25, 0.925), (0.95, 0.8, 0.55))
    planta((-2.9, 1.15, 0), 1.2)
    box((0.6, 0.35, 0.3), (0.8, 0.9, 0.15), (0.25, 0.45, 0.8)); box((0.3, 0.05, 0.05), (0.8, 0.9, 0.34), DARK)
    # carcasa de la cinta, abierta por delante (cantos en crema)
    S["casco"] = empty((0, 0, 0))
    box((0.7, 0.04, 0.7), (XC, 0.16, ZC), CASE, parent=S["casco"])
    for dz in (-0.34, 0.34): box((0.7, 0.34, 0.03), (XC, 0.0, ZC + dz), CASE, parent=S["casco"])
    for dx in (-0.34, 0.34): box((0.03, 0.34, 0.7), (XC + dx, 0.0, ZC), CASE, parent=S["casco"])
    for dz in (-0.34, 0.34): box((0.7, 0.01, 0.03), (XC, -0.172, ZC + dz), PAL["corte"], parent=S["casco"])
    for dx in (-0.34, 0.34): box((0.03, 0.01, 0.7), (XC + dx, -0.172, ZC), PAL["corte"], parent=S["casco"])
    box((0.16, 0.05, 0.4), (XC + 0.2, 0.2, ZC), DARK, parent=S["casco"])                       # clip del cinturón
    S["boton"] = box((0.1, 0.12, 0.05), (XC - 0.2, 0.0, ZC + 0.37), DARK, unique=True)
    # bobina con la cinta enrollada, eje y muelle en espiral delante
    S["rollo"] = cyl(1.0, 0.24, (XC, 0.0, ZC), BLADE, rot=(math.pi / 2, 0, 0), v=48, smooth=False)
    S["eje"] = cyl(0.07, 0.3, (XC, 0.0, ZC), STEEL, rot=(math.pi / 2, 0, 0), smooth=False)
    S["tramo"] = bar_obj(BLADE, 0.012)
    S["muelle"] = empty((XC, -0.15, ZC))
    pts = []
    for k in range(121):
        a = k / 120 * 4.5 * math.tau; r = 0.075 + 0.17 * k / 120
        pts.append((r * math.cos(a), 0, r * math.sin(a)))
    sp = tubo(pts, 0.009, DARK); sp.parent = S["muelle"]
    # cinta, marcas y gancho
    S["cinta"] = blade_mesh()
    S["marcas"] = [box((0.012, 0.1, 0.004), LEJOS, DARK) for _ in range(26)]
    S["gancho"] = empty(LEJOS)
    box((0.09, 0.32, 0.012), (0.045, 0, 0.04), STEEL, parent=S["gancho"])
    box((TAB, 0.32, 0.14), (-TAB / 2, 0, -0.03), STEEL, parent=S["gancho"])
    for yy in (-0.06, 0.06): cyl(0.015, 0.02, (0.05, yy, 0.05), (0.6, 0.62, 0.66), parent=S["gancho"])
    S["pared"] = empty(LEJOS); azulejos(0.3, 0.6, (-0.15, 0, 0.0), rot=(0, 0, math.pi / 2), color=PAL["rosa"], paso=0.15, parent=S["pared"])
    # flechas
    S["fl_muelle"] = flecha3d(LEJOS, (1, 0, 0), 0.3, 0.025)
    S["fl_peso"] = flecha3d(LEJOS, (0, 0, -1), 0.3, 0.025)
    S["fl_mano"] = flecha3d(LEJOS, (-1, 0, 0), 0.3, 0.025)
    dyn = [cam, S["casco"], S["boton"], S["rollo"], S["eje"], S["tramo"], S["muelle"], S["cinta"], S["marcas"], S["gancho"], S["pared"],
           S["fl_muelle"], S["fl_peso"], S["fl_mano"]]
    join_static(dyn)
    return sc, S

# ---------------- estado ----------------
def largo_cinta(t):
    return keyed(t, [(0.0, 0.75), (1.4, 1.3), (T("vamos a") , 1.3), (T("vamos a") + 0.6, 0.0), (T("necesitas"), 0.0),
                     (T("varios metros", fin=True), 2.0), (T("así que haces"), 2.0), (T("la enrollas", fin=True), 0.3),
                     (T("pero luego") , 0.3), (T("quién", fin=True), 1.2), (T("al sacar"), 1.2), (T("más y más", fin=True), 2.0),
                     (T("zas") - 0.05, 2.0), (T("zas") + 0.25, 0.08), (T("pero una cinta"), 0.08), (T("un palmo", fin=True), 1.15),
                     (T("esa curva"), 1.15), (T("más de un metro", fin=True), 1.65), (T("ahora necesitas") + 0.3, 1.65),
                     (T("de la mesa", fin=True), 0.55)])

def curvatura(t): return 1.0 if t < T("vamos a") + 0.3 else seg(t, T("así que la curvas"), T("teja", fin=True))
def kd(t): return mix(0.05, mix(1.6, 0.04, curvatura(t)), seg(t, T("pero una cinta"), T("un palmo", fin=True))) if t > T("pero una cinta") else 0.05

def holgura(t):
    """desplazamiento del gancho respecto a la cinta (+ hacia fuera); 1 mm de verdad = 0,025 en la maqueta"""
    if t < T("vamos a"): return TAB * math.sin(t * 7)
    if t < T("así que lo dejas"): return 0.0
    if t < T("al tirar"): return TAB * math.sin((t - T("así que lo dejas")) * 9) * 0.6
    if t < T("al empujar"): return TAB * seg(t, T("al tirar"), T("sale un", fin=True))
    if t < T("justo"): return TAB * mix(1, -1, seg(t, T("al empujar"), T("entra un", fin=True)))
    if t < T("por eso al"): return TAB * math.sin((t - T("justo")) * 5 + 4.7)
    return 0.0

def gancho_visible(t): return t < T("vamos a") + 0.4 or t > T("un gancho") - 0.2

def pared(t): return T("si empujas") - 0.3 < t < T("así que lo dejas") or T("al empujar") - 0.2 < t < T("justo", fin=True) + 0.4

def pose(t, S):
    L = largo_cinta(t); cv = curvatura(t); k = kd(t)
    blade_set(S["cinta"], L, cv, k)
    caja = t < T("vamos a") + 0.3 or t > T("un muelle") - 0.2
    S["casco"].location = (0, 0, 0) if caja else LEJOS
    S["boton"].location = (XC - 0.2 + 0.12 * seg(t, T("y un botón"), T("y un botón") + 0.3), 0.0, ZC + 0.37) if caja else LEJOS
    bobina = t < T("vamos a") + 0.3 or t > T("así que haces")
    r = math.sqrt(0.08 ** 2 + (0.29 ** 2 - 0.08 ** 2) * max(0.0, LMAX - L) / LMAX)
    S["rollo"].location = (XC, 0, ZC) if bobina else LEJOS; S["eje"].location = S["rollo"].location; S["rollo"].scale = (r, r, 1)
    if bobina: bar_set(S["tramo"], (XC, 0, ZC - r), (XEX, 0, ZB))
    else: bar_set(S["tramo"], LEJOS, Vector(LEJOS) + Vector((0, 0, 0.01)))
    muelle = t < T("vamos a") + 0.3 or t > T("un muelle") - 0.1
    S["muelle"].location = (XC, -0.15, ZC) if muelle else LEJOS
    S["muelle"].rotation_euler.y = -2.2 * L; S["muelle"].scale = (1,) * 3 if not (T("un muelle") - 0.1 < t < T("un muelle") + 0.3) else (seg(t, T("un muelle") - 0.1, T("un muelle") + 0.3) + 0.01,) * 3
    # punta y gancho
    tipx = XEX - L; h = holgura(t)
    S["gancho"].location = (tipx - h, 0, blade_z(tipx, k)) if gancho_visible(t) else LEJOS
    # marcas cada 10 cm desde el principio de la cinta; las primeras faltan (las ocupa el gancho)
    for n, m in enumerate(S["marcas"]):
        x = tipx + 0.12 + 0.09 * n
        if x < XEX - 0.02 and L > 0.15:
            m.location = (x, -0.09, blade_z(x, k) + cv * 0.035 * (0.09 / HW) ** 2 + 0.003)
            m.scale = (0.012, 0.1 if n % 5 else 0.16, 0.004)
        else: m.location = LEJOS
    # pared que empuja el gancho
    S["pared"].location = (tipx - h - TAB - 0.155, 0.0, ZB - 0.03) if pared(t) else LEJOS
    # flechas
    if T("al sacar") < t < T("zas") + 0.3:
        f = 0.4 + 0.6 * min(1, max(0, (L - 1.2) / 0.8)) if t < T("zas") else 1.4
        S["fl_muelle"].location = (XEX - 0.55, -0.3, ZB + 0.12); S["fl_muelle"].scale = (f,) * 3
    else: S["fl_muelle"].location = LEJOS
    if T("pero una cinta") + 0.6 < t < T("esa curva"):
        S["fl_peso"].location = (tipx + 0.1, -0.2, blade_z(tipx + 0.1, k) + 0.4); S["fl_peso"].scale = (1, 1, 1 - 0.6 * curvatura(t))
    else: S["fl_peso"].location = LEJOS
    if T("si mides") < t < T("si empujas") or T("al tirar") - 0.1 < t < T("al empujar"):
        S["fl_mano"].location = (XEX + 0.15, -0.3, ZB + 0.15); S["fl_mano"].rotation_quaternion = Vector((0, 0, 1)).rotation_difference(Vector((1, 0, 0)))
    elif T("al empujar") - 0.1 < t < T("justo"):
        S["fl_mano"].location = (XEX - 0.15, -0.3, ZB + 0.15); S["fl_mano"].rotation_quaternion = Vector((0, 0, 1)).rotation_difference(Vector((-1, 0, 0)))
    else: S["fl_mano"].location = LEJOS
    apply_cam(S["cam"], *cam_lin(t, CAM()))

def tip_t(t): return Vector((XEX - largo_cinta(t), 0, ZB))

def CAM():
    k = Claves(); add = k.add
    ini = V((-1.7, 0.0, 0.96), (0.3, -1.3, 0.75), 34)
    tipm = V((-1.5, 0.0, 0.93), (0.15, -0.8, 0.45), 42)
    ancho = V((-1.1, 0.1, 1.0), (0.5, -2.6, 1.5), 30)
    caja = V((XC, -0.1, ZC), (0.15, -1.35, 0.2), 40)
    add(0.0, V((-1.5, 0.0, 0.96), (0.25, -1.1, 0.65), 36)); add(1.8, ini)
    add(T("esa pieza"), V((-2.2, 0.0, 0.93), (0.15, -0.8, 0.45), 42), 1.2)
    add(T("y no es"), ancho, 0.6)
    add(T("vamos a") + 0.3, V((-1.2, 0.1, 1.0), (0.3, -2.0, 1.0), 32))
    add(T("necesitas") + 0.3, V((-1.9, 0.0, 0.95), (0.0, -3.0, 1.6), 28), 1.6)
    add(T("así que haces"), V((XC, 0.0, 1.15), (0.25, -1.7, 0.35), 38), 1.6)
    add(T("pero luego"), V((-1.3, 0.0, 1.0), (-0.3, -1.8, 0.9), 34))
    add(T("así que pones"), caja, 1.2)
    add(T("al sacar"), V((-1.1, 0.0, 1.1), (0.3, -1.9, 0.8), 34))
    add(T("el muelle se"), V((XC, -0.1, ZC), (-0.2, -1.2, 0.2), 42), 0.9)
    add(T("al soltarla"), V((-1.0, 0.0, 1.0), (0.2, -2.2, 1.0), 32), 1.2)
    add(T("pero una cinta") + 0.3, V((-1.9, 0.0, 0.8), (0.3, -1.9, 0.6), 34), 1.2)
    add(T("así que la curvas"), V((-2.0, 0.0, 0.96), (-0.9, -0.55, 0.25), 40), 1.4)
    add(T("esa curva"), V((-1.9, 0.0, 0.9), (0.2, -2.4, 0.9), 30), 1.0)
    add(T("y aguanta"), V((-2.1, 0.0, 0.92), (-0.4, -1.7, 0.7), 32), 1.0)
    add(T("ahora necesitas"), V((-1.5, 0.0, 0.9), (0.4, -1.3, 0.7), 36), 1.0)
    add(T("así que pones un"), tipm, 1.2)
    add(T("pero el gancho"), V((-1.51, 0.0, 0.92), (-0.05, -0.65, 0.35), 46), 2.2)
    add(T("y aquí viene"), V((-1.2, 0.0, 1.0), (0.3, -1.9, 1.0), 34))
    add(T("si mides"), V((-1.5, 0.0, 0.9), (-0.15, -0.9, 0.45), 40), 2.2)
    add(T("si empujas"), V((-1.55, 0.0, 0.9), (0.25, -0.9, 0.45), 40), 1.6)
    add(T("así que lo dejas"), V((-1.3, 0.0, 1.0), (0.2, -1.4, 0.7), 34))
    add(T("al tirar"), V((-1.52, 0.0, 0.93), (0.1, -0.75, 0.38), 44), 1.6)
    add(T("al empujar") + 0.3, V((-1.52, 0.0, 0.93), (-0.1, -0.75, 0.38), 44), 1.2)
    add(T("justo"), V((-1.4, 0.0, 0.98), (0.3, -1.3, 0.7), 36))
    add(T("la medida"), ancho, 1.2)
    add(T("por eso al"), V((-1.45, 0.0, 0.96), (0.05, -0.6, 0.45), 42), 1.8)
    add(T("ocupa ese"), V((-1.45, 0.0, 0.96), (-0.15, -0.65, 0.4), 42), 1.0)
    add(T("y un botón"), V((XC - 0.2, 0.0, ZC + 0.35), (0.2, -1.2, 0.35), 38), 1.6)
    add(T("sígueme"), V((-1.5, 0.0, 0.96), (0.25, -1.1, 0.65), 36))
    add(DUR + 1, ini)
    return k.k

def anchors(sc, S, t):
    cam = S["cam"]; P = lambda v: proj(sc, cam, v)
    L = largo_cinta(t); k = kd(t); tipx = XEX - L; h = holgura(t)
    return {"punta": P((tipx - h, 0, blade_z(tipx, k) + 0.12)), "tab": P((tipx - h, -0.13, ZB - 0.1)), "caja": P((XC, 0, ZC + 0.45)),
            "muelle": P((XC, -0.15, ZC + 0.3)), "medio": P((XEX - L * 0.5, 0, blade_z(XEX - L * 0.5, k) + 0.15)),
            "boton": P((XC - 0.1, 0, ZC + 0.42)), "salida": P((XEX, -0.1, ZB))}

if __name__ == "__main__":
    run("cintametrica", build, pose, anchors)
