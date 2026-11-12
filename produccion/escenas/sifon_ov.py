# Capa 2D de «El sifón de tu fregadero»
# Pastillas previstas (motion → fotografía): altura del tapón junto al agua (x+170), % de agua nueva sobre la U,
# días de vacaciones arriba a la derecha del plano, nivel 5→0 cm junto al agua, 10 s sobre el grifo.
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("sifon")
SUB_ESTILO = "frase"
KEYWORDS = {"fregadero", "armario", "tubo", "u", "fontanero", "alcantarilla", "desagüe", "saneamiento", "cloacas", "gases", "puerta",
            "curva", "agua", "tapón", "gas", "cinco", "siete", "centímetros", "grifo", "vacaciones", "mes", "evapora", "cero",
            "diez", "segundos", "anillos", "pendientes", "comida", "desenrosca", "limpiarla"}

def cota(C, ctx, t, a, b, p0, p1, col=(1, 0.82, 0.16)):
    """línea de cota vertical entre dos puntos de pantalla (altura del tapón)"""
    if t < a or t > b: return
    al = min(1, (t - a) / 0.25, (b - t) / 0.2)
    x = p0[0] + 120; ctx.save(); ctx.set_line_width(8); ctx.set_source_rgba(*col, al)
    ctx.move_to(x, p0[1]); ctx.line_to(x, p1[1]); ctx.stroke()
    for y in (p0[1], p1[1]):
        ctx.move_to(x - 30, y); ctx.line_to(x + 30, y); ctx.stroke()
    ctx.set_line_width(4); ctx.set_dash([12, 10])
    ctx.move_to(p0[0] - 20, p0[1]); ctx.line_to(x, p0[1]); ctx.move_to(p1[0] - 20, p1[1]); ctx.line_to(x, p1[1]); ctx.stroke()
    ctx.restore()

def overlay(ctx, t, A, C):
    # rótulos de pieza (uno cada vez)
    C.rotulo(ctx, t, "SIFÓN", T("ves ese"), T("ves ese") + 1.6)
    C.rotulo(ctx, t, "RED DE SANEAMIENTO", T("saneamiento"), T("saneamiento") + 1.7)
    C.rotulo(ctx, t, "TAPÓN DE AGUA", T("ese tapón"), T("ese tapón") + 1.6)
    C.rotulo(ctx, t, "ROSCA", T("se desenrosca"), T("se desenrosca") + 1.4)
    # altura del tapón: cota y pastilla 5 → 7 cm
    a0, a1 = T("la norma"), T("si es más")
    cota(C, ctx, t, a0, a1, A("agua"), A("fondo"))
    x, y = A("agua")
    C.pastilla(ctx, t, 5, "cm", T("cinco") - 0.1, T("siete") - 0.05, clampx(x + 240, 300), clampy(y - 40, 420), desde=0)
    C.pastilla(ctx, t, 7, "cm", T("siete") - 0.05, a1, clampx(x + 240, 300), clampy(y - 40, 420), desde=5, dur=0.5)
    # grifo: agua nueva que sustituye a la vieja
    x, y = A("u")
    C.pastilla(ctx, t, 100, "% agua nueva", T("el agua nueva"), T("una y otra", fin=True) + 0.3, clampx(x, 330), clampy(y + 230, 420, 1300),
               desde=0, dur=2.2, size=62)
    # vacaciones: días que pasan
    C.pastilla(ctx, t, 30, "días fuera", T("pero si te vas"), T("el nivel baja"), W * 0.5, H * 0.30, desde=0, dur=3.0, size=72)
    # nivel del tapón 5 → 0 cm
    x, y = A("agua")
    C.pastilla(ctx, t, 0, "cm", T("el nivel baja"), T("la puerta se abre") + 0.6, clampx(x + 240, 300), clampy(y - 40, 420), desde=5, dur=2.3)
    if T("la puerta se abre") <= t < T("la casa huele", fin=True):
        x, y = A("nube"); C.callout(ctx, "OLOR", clampx(x), clampy(y - 90, 360), win(t, T("la puerta se abre") + 0.4, T("la casa huele", fin=True)), size=60)
    # diez segundos de grifo
    x, y = A("grifo")
    a0 = T("basta con")
    if a0 <= t < T("y la u"):
        u = min(1, max(0, (t - a0 - 0.3) / 1.6)); v = 10 * (1 - u)
        C.pastilla(ctx, t, v, "s", a0, T("y la u"), clampx(x + 200, 300), clampy(y - 60, 420), dec=0)
        x2, y2 = A("agua")
        if t > a0 + 1.0: C.pastilla(ctx, t, 5, "cm", a0 + 1.0, T("y la u"), clampx(x2 + 240, 300), clampy(y2 - 40, 420, 1300), desde=0, dur=1.0)
    # clic al encajar / soltar
    x, y = A("rosca")
    C.chispa(ctx, t, x, y, T("para poder") + 0.2, r=70)
    x, y = A("anillo")
    C.chispa(ctx, t, x, y, T("y la u") + 1.4, r=55, col=(1, 0.85, 0.3))

def sfx_events(C):
    E = [(0.0, C.s_whoosh(), 0.35), (0.25, C.s_clank(), 0.35), (0.1, C.s_buzz(2.2), 0.12),
         (T("ves ese"), C.s_pop(), 0.45), (T("parece"), C.s_whoosh(), 0.35), (T("tu cocina"), C.s_fail(), 0.35),
         (T("vamos a"), C.s_whoosh(0.7), 0.45), (T("saneamiento"), C.s_thud(), 0.5), (T("y desde ahí"), C.s_buzz(1.8), 0.25),
         (T("huele") - 0.2, C.s_fail(), 0.4), (T("así que el tubo"), C.s_pop(), 0.45), (T("hace una curva"), C.s_pop(), 0.45),
         (T("y vuelve a subir"), C.s_clank(), 0.45), (T("una parte"), C.s_bleep(520), 0.25), (T("ese tapón"), C.s_win(), 0.35),
         (T("el gas empuja"), C.s_thud(), 0.45), (T("pero no puede"), C.s_thud(), 0.4), (T("la norma") - 0.3, C.s_whoosh(), 0.35),
         (T("cinco") - 0.35, C.s_tick(), 0.4), (T("siete") - 0.35, C.s_tick(), 0.4), (T("cualquier soplido"), C.s_whoosh(), 0.4),
         (T("cada vez que"), C.s_buzz(1.5), 0.15), (T("el agua nueva"), C.s_whoosh(), 0.35), (T("el tapón se renueva"), C.s_coin(), 0.4),
         (T("pero si te vas"), C.s_whoosh(), 0.35), (T("el nivel baja") - 0.3, C.s_tick(), 0.35), (T("la puerta se abre"), C.s_fail(), 0.45),
         (T("la casa huele"), C.s_buzz(1.0), 0.2), (T("basta con"), C.s_buzz(1.8), 0.15), (T("segundos", fin=True), C.s_win(), 0.4),
         (T("y la u") + 1.4, C.s_coin(), 0.45), (T("pendientes") + 0.8, C.s_pop(), 0.35), (T("se desenrosca"), C.s_clank(), 0.5),
         (T("para poder") + 0.2, C.s_thud(), 0.45), (T("sígueme"), C.s_whoosh(), 0.4)]
    return E
