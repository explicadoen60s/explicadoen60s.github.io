# Capa 2D de «¿Qué hay dentro de tu móvil cuando vibra?»
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("vibracion")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"vibra", "vueltas", "motor", "lenteja", "ocho", "milímetros", "centrada", "pesa", "media", "luna", "arriba", "abajo",
            "tiembla", "doce", "mil", "doscientas", "zumbido", "arrancar", "frenar", "muelle", "imán", "bobina", "corriente",
            "altavoz", "ritmo", "muchísimo", "cortísimo", "clic", "botón", "rebotando"}

def sg(t, a, b):
    x = max(0.0, min(1.0, (t - a) / (b - a))); return x * x * (3 - 2 * x)
def miles(v): return f"{int(round(v)):,}".replace(",", ".")

def th(t):
    a = T("cuando el motor"); b1 = T("arriba"); b2 = T("lado", 2); b3 = T("abajo")
    ks = [(a, -90.0), (b1, 90.0), (b2, 180.0), (b3, 270.0), (b3 + 0.2, 280.0)]
    if t <= a: return math.radians(270)
    for (x0, v0), (x1, v1) in zip(ks, ks[1:]):
        if x0 <= t <= x1: return math.radians(v0 + (v1 - v0) * sg(t, x0, x1))
    return math.radians(280)

def overlay(ctx, t, A, C):
    Y, R, G, B = C.YL, C.RED, C.GREEN, (0.45, 0.8, 1.0)
    BY = H * 0.265
    if t < T("dentro hay"):
        C.badge(ctx, "LLAMADA ENTRANTE", W / 2, BY, win(t, 0.05, T("dentro hay")), G, size=66)
    label(C, ctx, t, T("vueltas") - 0.2, T("en muchos"), "MOTOR", A, "erm", dx=0, dy=-200, size=62)
    label(C, ctx, t, T("lenteja") - 0.2, T("pero su eje"), "LENTEJA", A, "lentil", dx=0, dy=200, size=60)
    if T("ocho") <= t < T("pero su eje"):
        C.badge(ctx, "%d MM" % round(8 * sg(t, T("ocho"), T("milímetros", fin=True))), W / 2, BY, win(t, T("ocho"), T("pero su eje")), Y, size=90)
    if T("pero su eje") <= t < T("lleva una pesa"):
        C.badge(ctx, "✗ 0 SACUDIDAS", W / 2, BY, win(t, T("rueda"), T("lleva una pesa")), R, size=70)
    label(C, ctx, t, T("lleva una pesa") + 0.2, T("cuando el motor"), "PESA", A, "weight", dx=0, dy=-170, size=64)
    if T("cuando el motor") <= t < T("y el móvil entero"):
        ang = (math.degrees(th(t)) % 360) if t < T("una y otra") else None
        if ang is not None and t >= T("arriba") - 0.3:
            C.badge(ctx, "ÁNGULO %d°" % round(ang), W / 2, BY, win(t, T("arriba") - 0.3, T("una y otra")), Y, size=78)
        if t >= T("una y otra"):
            C.badge(ctx, "VUELTAS: %d" % int(1 + 4 * (t - T("una y otra"))), W / 2, BY, 1.0, Y, size=78)
    if T("hasta doce") - 0.2 <= t < T("por eso suena"):
        v = 12000 * sg(t, T("hasta doce"), T("minuto", fin=True))
        C.badge(ctx, miles(v) + " VUELTAS/MIN", W / 2, BY, win(t, T("hasta doce") - 0.2, T("por eso suena")), Y, size=70)
        if t >= T("doscientas"):
            C.badge(ctx, "%d / S" % round(200 * sg(t, T("doscientas"), T("segundo", fin=True))), W / 2, BY + 140, win(t, T("doscientas"), T("por eso suena")), B, size=78)
    if T("por eso suena") <= t < T("pero un motor"):
        C.badge(ctx, "200 HZ", W / 2, BY, win(t, T("por eso suena"), T("pero un motor")), B, size=84)
    label(C, ctx, t, T("arrancar"), T("y aquí viene"), "ARRANCA", A, "g_start", dx=-60, dy=-160, size=56)
    label(C, ctx, t, T("frenar"), T("y aquí viene"), "FRENA", A, "g_end", dx=40, dy=-200, size=56)
    label(C, ctx, t, T("no puede"), T("y aquí viene"), "TOQUE", A, "g_cmd", dx=0, dy=-110, size=52)
    if T("no puede") <= t < T("y aquí viene"):
        C.badge(ctx, "✗ DEMASIADO LENTO", W / 2, BY, win(t, T("no puede"), T("y aquí viene")), R, size=64)
    label(C, ctx, t, T("muelle"), T("la corriente"), "MUELLE", A, "spring", dx=0, dy=-260, size=58)
    label(C, ctx, t, T("con un imán"), T("la corriente"), "IMÁN", A, "magnet", dx=-80, dy=260, size=58)
    label(C, ctx, t, T("bobina"), T("la corriente"), "BOBINA", A, "coil", dx=60, dy=-260, size=58)
    if T("la corriente") <= t < T("como un altavoz"):
        s = "CORRIENTE: -" if t < T("luego hacia el") else "CORRIENTE: +"
        C.badge(ctx, s, W / 2, BY, win(t, T("la corriente"), T("como un altavoz")), Y, size=72)
    label(C, ctx, t, T("como un altavoz") + 0.1, T("pero que en"), "ALTAVOZ", A, "spk", dx=0, dy=-120, size=60)
    if T("y si la") <= t < T("así puede"):
        C.badge(ctx, "EMPUJE: 10 %", W / 2, BY, win(t, T("y si la"), T("así puede")), B, size=66)
        if t >= T("con muy"):
            v = 10 + 90 * sg(t, T("con muy"), T("muchísimo", fin=True))
            C.badge(ctx, "MOVIMIENTO: %d %%" % round(v), W / 2, BY + 135, win(t, T("con muy"), T("así puede")), G, size=66)
    if T("así puede") <= t < T("como cuando"):
        C.badge(ctx, "✓ TOQUE CORTO", W / 2, BY, win(t, T("toque"), T("como cuando")), G, size=70)
    if T("no es un") <= t < T("es una pesa"):
        C.badge(ctx, "✗ BOTÓN", W / 2, BY, win(t, T("no es un"), T("es una pesa")), R, size=80)
    label(C, ctx, t, T("es una pesa") + 0.3, T("sígueme") + 0.3, "PESA", A, "lra", dx=0, dy=-180, size=62)

def sfx_events(C):
    E = [(0.0, C.s_buzz(2.0), 0.5), (T("dentro hay"), C.s_whoosh(), 0.4), (T("mira por dentro"), C.s_whoosh(), 0.35),
         (T("lenteja"), C.s_pop(), 0.35), (T("milímetros"), C.s_coin(), 0.35), (T("rueda"), C.s_fail(), 0.3), (T("pesa"), C.s_clank(), 0.35),
         (T("arriba"), C.s_pop(), 0.35), (T("lado", 2), C.s_pop(), 0.35), (T("abajo"), C.s_pop(), 0.35), (T("y el móvil entero"), C.s_buzz(1.3), 0.45),
         (T("minuto"), C.s_coin(), 0.4), (T("por eso suena"), C.s_buzz(1.3), 0.5), (T("no puede"), C.s_fail(), 0.35), (T("y aquí viene"), C.s_whoosh(), 0.4),
         (T("muelle"), C.s_pop(), 0.35), (T("imán"), C.s_pop(), 0.35), (T("bobina"), C.s_pop(), 0.35), (T("la corriente"), C.s_thud(), 0.4),
         (T("luego hacia el"), C.s_thud(), 0.4), (T("como un altavoz"), C.s_buzz(0.8), 0.3), (T("pero que en"), C.s_buzz(1.0), 0.4),
         (T("muchísimo"), C.s_win(), 0.4), (T("cortísimo"), C.s_thud(), 0.4), (T("tecla"), C.s_thud(), 0.4), (T("esa sensación"), C.s_thud(), 0.4),
         (T("no es un"), C.s_fail(), 0.3), (T("es una pesa"), C.s_whoosh(), 0.4), (T("sígueme"), C.s_whoosh(), 0.4)]
    return E
