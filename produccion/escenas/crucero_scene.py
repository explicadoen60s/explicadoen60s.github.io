# «¿Y si te caes de un crucero?» · formato D (simulación sin voz, rótulos en crucero_rotulos.json).
# Noche de tormenta en mar abierto. Un pasajero resbala en la cubierta y cae 25 m junto al casco; bajo el agua
# (choque por frío); en superficie el casco pasa a un metro, llega la popa y su estela; el barco se aleja; le lanzan
# un aro que cae lejos; nada hasta él y lo agarra; el barco da la vuelta a lo lejos y llega la lancha de rescate.
# El último plano repite el primero (bucle).
import bpy, math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib3d import *
from modelos import caja, cilindro, bola, persona
from mathutils import Vector, Euler

DUR = 71.0
CIELO = (0.09, 0.13, 0.17); MAR = (0.13, 0.36, 0.38); MAR_FONDO = (0.06, 0.20, 0.22); ESPUMA = (0.86, 0.93, 0.95)
CASCO = (0.12, 0.17, 0.32); BLANCO = (0.88, 0.89, 0.91); LUZ = (1.0, 0.86, 0.45); CRISTAL = (0.30, 0.45, 0.60)
ROJO = (0.92, 0.22, 0.18); NARANJA = (1.0, 0.42, 0.10); PIEL = (0.95, 0.76, 0.62); MANGA = (0.80, 0.16, 0.20); MADERA = (0.62, 0.42, 0.26)
L = 180.0                  # eslora del barco (unidades = metros)
DECK = 24.0                # cubierta superior
YC = -14.0                 # costado de babor (el lado por el que cae)
XP = 40.0                  # posición de la persona respecto al centro del barco
LEJOS = (0, 0, -500)


def barco_x(t):
    """Posición x del centro del barco: quieto hasta los 15 s, luego avanza (el casco pasa junto a ti) y se aleja."""
    if t < 15 or t >= 68.8: return 0.0
    if t < 37: return (t - 15) * 9.0                       # 9 m/s: la popa llega a los ~30 s
    return 198 + (t - 37) * 11.0


def build():
    sc, cam = scene_setup(world=CIELO, light_rot=35, shadow=0.35)
    sh = sc.display.shading; sh.cavity_ridge_factor = 0.4; sh.cavity_valley_factor = 0.5
    S = {"cam": cam}
    # ---------- mar: malla facetada con dos trenes de olas ----------
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=300, y_subdivisions=170, size=900, location=(150, 0, 0))
    mar = bpy.context.object; mar.scale = (1, 0.58, 1); setup(mar, MAR)
    w1 = mar.modifiers.new("o1", 'WAVE'); w1.height = 0.9; w1.width = 9; w1.speed = 0.25; w1.narrowness = 1.2
    w1.use_normal = False; w1.start_position_x = -2; w1.start_position_y = -3; w1.falloff_radius = 0
    w2 = mar.modifiers.new("o2", 'WAVE'); w2.height = 0.45; w2.width = 4; w2.speed = 0.4; w2.use_x = True; w2.use_y = False
    w2.start_position_x = 0.3
    S["mar"] = mar; S["olas"] = (w1, w2)
    # ---------- barco ----------
    b = empty((0, 0, 0)); S["barco"] = b
    caja((L, 28, 16), (0, 0, 2), CASCO, b, r=1.5)                      # casco (z -6..10)
    bpy.ops.mesh.primitive_cylinder_add(vertices=3, radius=16.2, depth=16, location=(L / 2 - 1, 0, 2))   # proa
    proa = bpy.context.object; proa.scale = (1.6, 0.86, 1); proa.rotation_euler = (0, 0, 0); setup(proa, CASCO, b)
    caja((L * 0.92, 27, 14), (-4, 0, 17), BLANCO, b, r=1.2)            # superestructura (z 10..24)
    caja((L * 0.55, 20, 6), (-12, 0, 27), BLANCO, b, r=1.0)            # puente y cubiertas altas
    # filas de ventanas iluminadas y balcones en los dos costados
    for lado in (-1, 1):
        y = lado * 13.55
        for k, z in enumerate((6.0, 8.0)):                               # ojos de buey del casco
            for i in range(44):
                x = -L / 2 + 6 + i * (L - 14) / 44
                bola(0.38, (x, y * 1.03, z), LUZ, b, escala=(1, 0.3, 1), sub=2)
        for z in (12.2, 14.7, 17.2, 19.7, 22.2):                       # cubiertas de camarotes
            caja((L * 0.9, 0.5, 1.15), (-4, y, z), CRISTAL, b, r=0.1)
            for i in range(30):
                x = -4 - L * 0.45 + 3 + i * (L * 0.9 - 6) / 30
                if (i * 7 + int(z)) % 3: caja((2.4, 0.55, 0.9), (x, y * 1.002, z + 0.05), LUZ, b, r=0.08)
            caja((L * 0.9, 0.6, 0.15), (-4, y * 1.01, z - 0.75), BLANCO, b, r=0.05)
        for i in range(60):
            caja((0.12, 0.12, 1.1), (-4 - L * 0.46 + i * L * 0.92 / 60, lado * 13.4, DECK + 0.55), BLANCO, b, r=0.03)
        caja((L * 0.92, 0.3, 0.18), (-4, lado * 13.4, DECK + 1.2), MADERA, b, r=0.06)    # pasamanos
        caja((L * 0.92, 0.08, 0.08), (-4, lado * 13.4, DECK + 0.6), BLANCO, b, r=0.03)   # barra intermedia
        for i in range(6):                                               # botes salvavidas naranjas, bajo la cubierta
            caja((7, 2.2, 1.8), (-55 + i * 18, lado * 13.9, 10.6), NARANJA, b, r=0.8)
    caja((L * 0.9, 26, 0.3), (-4, 0, DECK + 0.05), (0.55, 0.42, 0.30), b, r=0.1)         # cubierta de madera
    cilindro(4.2, 10, (-L / 2 + 30, 0, 34), BLANCO, b, r=1.0)                            # chimenea
    cilindro(4.25, 2.5, (-L / 2 + 30, 0, 38), ROJO, b, r=0.3)
    caja((2, 14, 1), (-L / 2 + 2, 0, 0), CASCO, b, r=0.4)                                # popa
    S["luces_cub"] = [bola(0.9, (x, 0, 31), (1, 0.95, 0.75), b) for x in (-20, 10, 40)]
    # ---------- la persona (tercera persona: caída) ----------
    p = empty((XP, YC + 0.9, DECK)); persona((0, 0, 0), 1.75, parent=p, ropa=MANGA); S["persona"] = p
    # ---------- brazos en primera persona (hijos de la cámara) ----------
    S["brazos"] = []
    for lado in (-1, 1):
        e = empty((0, 0, 0), cam)
        cilindro(0.075, 0.75, (0, 0, -0.375), MANGA, e)
        caja((0.16, 0.06, 0.19), (0, 0, -0.84), PIEL, e, r=0.03)
        for d in range(4): caja((0.028, 0.035, 0.11), (-0.054 + d * 0.036, 0, -0.98), PIEL, e, r=0.012)
        caja((0.03, 0.035, 0.09), (lado * 0.09, 0, -0.8), PIEL, e, r=0.012)
        S["brazos"].append(e)
    # ---------- espuma y salpicaduras ----------
    rnd = random.Random(4)
    S["chapoteo"] = [bola(rnd.uniform(0.25, 0.7), LEJOS, ESPUMA, sub=1) for _ in range(40)]
    S["chap_dir"] = [Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(1.2, 2.6))) for _ in range(40)]
    S["estela"] = [bola(rnd.uniform(1.2, 3.5), LEJOS, ESPUMA, escala=(1, 1, 0.25), sub=1) for _ in range(70)]
    S["estela_p"] = [Vector((rnd.uniform(-60, 0), rnd.uniform(-16, 16), 0.2)) for _ in range(70)]
    S["burbujas"] = [bola(rnd.uniform(0.02, 0.05), LEJOS, (0.75, 0.9, 0.95), sub=2) for _ in range(70)]
    S["burb_p"] = [Vector((rnd.uniform(-1.6, 1.6), rnd.uniform(-1.6, 1.6), rnd.uniform(0, 3))) for _ in range(70)]
    # ---------- aro salvavidas ----------
    a = empty(LEJOS); S["aro"] = a
    torus(0.75, 0.2, (0, 0, 0), NARANJA, a)
    for k in range(4):
        ang = k * math.pi / 2
        caja((0.25, 0.44, 0.44), (math.cos(ang) * 0.75, math.sin(ang) * 0.75, 0), (0.97, 0.97, 0.97), a, rot=(0, 0, ang), r=0.06)
    # ---------- lancha de rescate ----------
    l = empty(LEJOS); S["lancha"] = l
    caja((7, 2.8, 1.2), (0, 0, 0.3), NARANJA, l, r=0.5)
    caja((2.4, 2.0, 1.4), (-0.8, 0, 1.5), BLANCO, l, r=0.3)
    S["foco"] = bola(0.35, (1.2, 0, 2.3), (1, 1, 0.85), l)
    vg = empty((-L / 2 + 22, YC + 1.4, DECK), b); persona((0, 0, 0), 1.75, parent=vg, ropa=(0.95, 0.95, 0.95))
    brazo = cilindro(0.06, 0.75, (0.0, -0.32, 1.45), (0.95, 0.95, 0.95), vg, rot=(math.radians(70), 0, 0)); S["vigia"] = vg
    S["flechas"] = [flecha3d(LEJOS, (1, 0, 0), 2.6, 0.13, ROJO) for _ in range(3)]
    yo = empty(LEJOS); S["yo"] = yo
    bola(0.13, (0, 0, 0.25), PIEL, yo); bola(0.135, (0, 0.02, 0.3), (0.3, 0.2, 0.14), yo, escala=(1, 1, 0.6))
    caja((0.42, 0.24, 0.35), (0, 0, 0.0), MANGA, yo, r=0.1)
    # trayectoria del giro (puntos que se encienden)
    S["giro"] = [bola(1.6, LEJOS, (1, 0.85, 0.3), sub=1) for _ in range(26)]
    join_static([S["mar"], b, p, S["brazos"], S["chapoteo"], S["estela"], S["burbujas"], a, l, S["giro"], yo, S["flechas"]])
    return sc, S


# ---------- cámara: (t, posición, objetivo, lente); las posiciones relativas al barco se resuelven en pose ----------
AROD = Vector((XP + 12, YC - 3 + 4, 0.75))
def aro_pos(t):
    """El aro en vuelo (40,5-42 s): sale de la popa y cae a 12 m de ti."""
    u = max(0.0, min(1.0, (t - 40.5) / 1.5)); ini = Vector((barco_x(t) - L / 2 + 30, YC + 1, DECK))
    return ini.lerp(AROD, u) + Vector((0, 0, 14 * math.sin(u * math.pi)))

def aro_flota(t):
    return AROD + Vector((0, 0, 0.25 * math.sin(t * 1.4)))

def camara(t):
    bx = barco_x(t)
    yp, zp = YC - 3.0, 1.7                   # tú, en el agua, a 3 m del casco
    if t < 6.0 or t >= 68.8:                 # en cubierta, junto a la barandilla, en la tormenta (y el bucle final)
        u = t if t < 6 else t - 68.8
        cab = 0.3 * math.sin(u * 2.2)                       # cabeceo del barco en la tormenta
        if t < 6 and u >= 2.0:                              # 2 s: plano bajo y cerca, el cuerpo ya por encima de la barandilla
            k = 1 - 0.12 * seg(u, 2.0, 6.0)
            pos = Vector((XP + 2.4 * k + cab, YC - 2.2 * k, DECK + 0.6 + 0.15 * math.sin(u * 3))); tgt = Vector((XP, YC + 0.6, DECK + 1.5)); return pos, tgt, 24
        k = 1 - 0.15 * seg(u, 0, 2.0)
        pos = Vector((XP + 3.2 * k + cab, YC + 1.0 - 4.6 * k, DECK + 1.4 + 0.9 * k + 0.2 * math.sin(u * 3))); tgt = Vector((XP, YC + 1.0, DECK + 1.3)); return pos, tgt, 26
    if t < 9.3:                              # desde arriba, a lo largo del casco: la caída
        u = seg(t, 6.0, 9.3); pz = DECK - 24.5 * u * u
        pos = Vector((XP + 4.5, YC - 6.5 - 2 * u, pz + 6.5 - 2.5 * u)); tgt = Vector((XP, YC - 2.5, pz - 1.5)); return pos, tgt, 24
    if t < 11.5:                             # el golpe, a ras de agua
        pos = Vector((XP + 7, YC - 9, 1.6)); tgt = Vector((XP, YC - 2.5, 0.8)); return pos, tgt, 30
    if t < 15.0:                             # bajo el agua mirando arriba
        pos = Vector((XP, YC - 3, -3.2 + seg(t, 11.5, 15.0) * 2.0)); tgt = Vector((XP + 0.5, YC - 3, 2.0)); return pos, tgt, 22
    if t < 19.0:                             # sales: el casco gigante a un metro
        pos = Vector((XP - 1, yp, zp)); tgt = Vector((XP + 6, YC + 2, 9 + 4 * math.sin(t * 0.6))); return pos, tgt, 20
    if t < 23.0:                             # el casco pasa (mira a lo largo)
        pos = Vector((XP - 1, yp, zp)); tgt = Vector((XP + 20, YC + 1, 6)); return pos, tgt, 24
    if t < 26.5:                             # miras arriba: cubiertas iluminadas, nadie te oye
        pos = Vector((XP - 1, yp - 0.5, zp)); tgt = Vector((XP + 3, YC + 2, 22)); return pos, tgt, 18
    if t < 33.0:                             # llega la popa y la estela
        pos = Vector((XP - 6, yp - 1.5, 1.4)); tgt = Vector((bx - L / 2, YC + 4, 3)); return pos, tgt, 22
    if t < 37.0:                             # el barco se aleja
        pos = Vector((XP - 6, yp - 2, 1.1)); tgt = Vector((bx - L / 2 + 20, 0, 8)); return pos, tgt, 30 + (t - 33) * 2.2
    if t < 40.5:                             # en cubierta: un tripulante te ha visto y señala
        u = seg(t, 37.0, 40.5); cx = bx - L / 2 + 22
        pos = Vector((cx + 5 - u, YC + 6.5, DECK + 2.6)); tgt = Vector((cx - 1, YC - 4, DECK - 2)); return pos, tgt, 30
    if t < 42.0:                             # el aro vuela: la cámara lo sigue de lado, recortado contra el cielo
        ar = aro_pos(t); pos = ar + Vector((-4.0, -8.0, -1.5)); tgt = ar + Vector((0, 0, -0.6)); return pos, tgt, 32
    if t < 48.0:                             # el aro flotando, siguiéndolo: en el tercio de abajo, bajo la tarjeta del juego
        ar = aro_flota(t); pos = Vector((XP - 6, yp - 2, 2.1)); d = (ar - pos).length
        pos = pos + (ar - pos).normalized() * 0.3 * seg(t, 44.0, 48.0); tgt = ar + Vector((0, 0, 0.12 * d)); return pos, tgt, 48 + 7 * seg(t, 44.0, 45.0)
    if t < 50.0:                             # tus manos sin fuerza, con el aro delante (que no alcanzas)
        ar = aro_flota(t); pos = Vector((XP - 6, yp - 2, 2.1)); d = (ar - pos).length
        tgt = ar + Vector((0, 0, 0.015 * d)); return pos, tgt, 60
    if t < 51.5:                             # empuje hacia el aro
        pos = Vector((XP - 6, yp - 2, 2.1)); tgt = aro_flota(t) + Vector((0, 0, 0.3)); return pos, tgt, 60 - 2 * seg(t, 50.0, 51.5)
    if t < 54.5:                             # nadas hacia el aro
        u = seg(t, 51.5, 54.5); pos = Vector((XP - 6 + u * 16.6, yp - 2 + u * 4.6, 1.9 - 0.9 * u)); tgt = Vector((XP + 12, yp + 4, 0.75)); return pos, tgt, 40 - 14 * u
    if t < 57.3:                             # agarrado al aro (primer plano)
        pos = Vector((XP + 9.4, yp + 1.4, 2.0)); tgt = Vector((XP + 12.2, yp + 4.2, 0.95)); return pos, tgt, 24
    if t < 65.0:                             # a lo lejos el barco gira; luego llega la lancha
        pos = Vector((XP + 10.6, yp + 2.6, 1.3)); tgt = Vector((XP + 120, 40, 6)) if t < 61.5 else Vector((XP + 40, yp + 6, 1.5))
        return pos, tgt, 26 if t < 61.5 else 30
    u = seg(t, 65.0, 68.8)                   # vista desde arriba: tú en el aro, la lancha al lado
    pos = Vector((XP + 12 - 6 * u, yp + 4 - 7 * u, 6 + 14 * u)); tgt = Vector((XP + 12, yp + 4, 0)); return pos, tgt, 28


def pose(t, S):
    bx = barco_x(t)
    S["barco"].location = (bx, 0, 0)
    if 57.3 <= t < 65:   # el barco da la vuelta a lo lejos
        S["barco"].location = (XP + 160 + 60 * math.sin(seg(t, 57.3, 65) * math.pi), 60 * (1 - math.cos(seg(t, 57.3, 65) * math.pi)), 0)
        S["barco"].rotation_euler = (0, 0, seg(t, 57.3, 65) * math.pi)
    elif 65 <= t < 68.8:
        S["barco"].location = (XP + 160, 120, 0); S["barco"].rotation_euler = (0, 0, math.pi)
    else:
        S["barco"].rotation_euler = (0, 0, 0)
    # olas (más fuertes en la estela)
    w1, w2 = S["olas"]; w1.time_offset = -t * 30 * 0.9; w2.time_offset = -t * 30 * 1.3
    # la persona: en la barandilla, resbala, cae dando vueltas
    p = S["persona"]
    if t < 6.0 or t >= 68.8:
        u = t if t < 6 else t - 68.8
        lean = (0.45 + 0.25 * math.sin(u * 3.1) + seg(u, 3.2, 6.0) * 0.8) if t < 6 else 0.35 + 0.25 * math.sin(u * 3.1)
        p.location = (bx + XP, YC + 0.9, DECK + 0.1); p.rotation_euler = (lean, 0, math.radians(-90) + 0.1 * math.sin(u * 2))
        p.hide_render = False
    elif t < 9.3:
        u = seg(t, 6.0, 9.3)
        p.location = (XP + 0.0, YC - 1.5 - 2.5 * u, DECK - 24.5 * u * u + 0.5); p.rotation_euler = (1.4 + u * 4.2, 0.6 * u, -1.57 + u * 1.2)
        p.hide_render = False
    else:
        p.location = LEJOS; p.hide_render = True
    # brazos en primera persona: visibles cuando eres tú quien mira (desde el agua)
    pov = 11.5 <= t < 65.0 and not (37.0 <= t < 42.0)   # en cubierta y siguiendo al aro no eres tú quien mira
    for i, e in enumerate(S["brazos"]):
        e.hide_render = not pov
        lado = -1 if i == 0 else 1
        if not pov: e.location = (0, 0, 5); continue
        hombro = Vector((lado * 0.32, -0.75, -0.25))
        if t < 15:                      # bajo el agua: las manos suben hacia la luz
            ph = t * 2.2 + i * math.pi; mano = Vector((lado * 0.22, 0.05 + 0.12 * math.sin(ph), -1.25))
        elif 23.0 <= t < 26.5:          # gritas: brazos arriba agitándose
            ph = t * 6 + i * 1.7; mano = Vector((lado * (0.42 + 0.12 * math.sin(ph)), 0.35, -1.05))
        elif 30.0 <= t < 33.0 or 51.5 <= t < 54.5:   # pataleas / nadas: brazadas alternas (más lentas si ya hay frío)
            ph = t * (3.2 if t >= 48 else 4.5) + i * math.pi
            mano = Vector((lado * 0.2, -0.32 + 0.22 * math.sin(ph), -1.15 - 0.25 * math.cos(ph)))
        elif 54.5 <= t < 65.0:          # agarrado al aro
            mano = Vector((lado * 0.45, -0.42, -1.0))
        else:                           # flotando
            ph = t * 1.3 + i; mano = Vector((lado * 0.38, -0.45 + 0.05 * math.sin(ph), -1.1))
        e.location = hombro; d = mano - hombro
        e.rotation_mode = 'QUATERNION'; e.rotation_quaternion = d.to_track_quat('-Z', 'Y')
        e.scale = (1, 1, d.length / 1.0)
    # chapoteo del golpe (9,3 s) y del aro (42 s)
    for k, (o, d) in enumerate(zip(S["chapoteo"], S["chap_dir"])):
        for t0, c, s in ((9.3, Vector((XP, YC - 4.0, 0)), 1.0), (41.85, Vector((XP + 12, YC - 3 + 4, 0)), 0.45)):
            u = t - t0
            if 0 <= u < 1.4:
                v = d * 6 * s; o.location = c + Vector((v.x * u, v.y * u, v.z * u - 9.8 * u * u * 0.5 * 0.8)); o.scale = (s * (1 - u / 1.6),) * 3; break
        else:
            o.location = LEJOS
    # estela de la popa (26,5-37 s): espuma que se agita detrás del barco
    for o, p0 in zip(S["estela"], S["estela_p"]):
        if 25.0 <= t < 44.0:
            x = bx - L / 2 + p0.x + 3 * math.sin(t * 2 + p0.y)
            o.location = (x, p0.y * (0.6 + 0.4 * abs(p0.x) / 60), 0.35 + 0.2 * math.sin(t * 3 + p0.x)); o.rotation_euler = (0, 0, t + p0.y)
        else:
            o.location = LEJOS
    # burbujas bajo el agua
    cam = S["cam"]
    for o, p0 in zip(S["burbujas"], S["burb_p"]):
        if 9.6 <= t < 15.0:
            z = -3.0 + ((p0.z + (t - 9.6) * 2.4) % 3.4)
            o.location = (XP + p0.x, YC - 3 + p0.y - 1.5, z)
        else:
            o.location = LEJOS
    # aro: lanzado desde el barco (40,5 s), cae lejos (42 s), flota; luego lo agarras
    a = S["aro"]; dest = AROD
    if t < 40.5:
        a.location = LEJOS
    elif t < 42.0:
        u = (t - 40.5) / 1.5; a.location = aro_pos(t); a.rotation_euler = (u * 6, u * 3, 0)
    else:
        a.location = aro_flota(t); a.rotation_euler = (0.15 * math.sin(t), 0.12 * math.cos(t * 1.2), 0)
    # flechas de la estela: el agua tira de ti hacia la popa (30-33 s)
    for k, f in enumerate(S["flechas"]):
        if 30.0 <= t < 33.0:
            u = ((t - 30.0) * 0.9 + k / 3) % 1.0
            f.location = (XP - 2 + 7 * u, YC - 4.5 - 1.6 + k * 1.6, 0.9); f.scale = (1 + 0.4 * seg(t, 30, 32),) * 3
        else:
            f.location = LEJOS
    # lancha: llega de lejos con el foco encendido
    l = S["lancha"]
    if t < 61.5:
        l.location = LEJOS
    else:
        u = seg(t, 61.5, 66.5); l.location = (XP + 140 - 120 * u, YC + 1 + 10 * (1 - u), 0.3 + 0.2 * math.sin(t * 2)); l.rotation_euler = (0.05 * math.sin(t * 2.3), 0, math.pi + 0.15)
    S["foco"].scale = (1 + 0.3 * math.sin(t * 9),) * 3
    S["yo"].location = (dest + Vector((0, 0, 0.1 + 0.25 * math.sin(t * 1.4)))) if 65.0 <= t < 68.8 else LEJOS
    # trayectoria del giro (57,3-61,5 s): puntos que se encienden en arco
    for k, o in enumerate(S["giro"]):
        f = k / (len(S["giro"]) - 1)
        if 57.3 <= t < 61.5 and f <= seg(t, 57.3, 61.0):
            ang = f * math.pi; o.location = (XP + 160 + 60 * math.sin(ang), 60 * (1 - math.cos(ang)), 1.5)
        else:
            o.location = LEJOS
    # luces de cubierta parpadean cuando dan la alarma
    for k, o in enumerate(S["luces_cub"]):
        o.scale = ((1.8 if 37 <= t < 44 and int(t * 4 + k) % 2 else 1.0),) * 3
    pos, tgt, lens = camara(t)
    # balanceo de la cabeza en el agua (cámara a ras de olas)
    if 15.0 <= t < 68.8:
        pos = pos + Vector((0, 0, 0.6 + 0.25 * math.sin(t * 1.3) + 0.1 * math.sin(t * 2.7)))
    apply_cam(cam, pos, tgt, lens)
    # bajo el agua: el mundo se vuelve verde oscuro
    bpy.context.scene.world.color = lin(MAR_FONDO if 9.6 <= t < 15.0 else CIELO)


def anchors(sc, S, t):
    cam = S["cam"]; bx = barco_x(t)
    return {"persona": proj(sc, cam, S["persona"].location if t < 9.3 else Vector((XP, YC - 3, 0))),
            "aro": proj(sc, cam, S["aro"].location), "lancha": proj(sc, cam, S["lancha"].location),
            "barco": proj(sc, cam, Vector((bx - L / 2, 0, 12)) if t < 57.3 else S["barco"].location + Vector((0, 0, 10))),
            "casco": proj(sc, cam, Vector((XP + 8, YC, 6)))}


run("crucero", build, pose, anchors)
