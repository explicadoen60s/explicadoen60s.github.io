# Capa 2D de «Si tuvieras que inventar el cepillo eléctrico…»
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("cepillo")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"dientes", "minutos", "cepillo", "movimiento", "mano", "motor", "mango", "gira", "cabezal", "vibre", "imán", "bobina",
            "corriente", "derecha", "izquierda", "treinta", "mil", "quinientos", "cerdas", "pasta", "saliva", "líquido", "aprietas",
            "vibración", "sensor", "tiempo", "reloj", "zona", "pausa", "pausas", "zonas", "cargarlo", "agua", "enchufes", "base",
            "campo", "magnético", "metal", "semanas"}

def ss(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def keyed(t, keys):
    if t <= keys[0][0]: return keys[0][1]
    for (a, va), (b, vb) in zip(keys, keys[1:]):
        if a <= t <= b: return va + (vb - va) * ss((t - a) / max(b - a, 1e-4))
    return keys[-1][1]
TEAL = (0.35, 0.9, 0.85); Bl = (0.45, 0.75, 1.0)
YB = H * 0.29

def badge(C, ctx, t, a, b, text, col, size=70, dy=0):
    p = win(t, a, b)
    if p: C.badge(ctx, text, W / 2, YB + dy, p, col, size=size)

def label(C, ctx, t, a, b, text, A, key, dx=0, dy=-220, size=64):
    p = win(t, a, b)
    if p:
        x, y = A(key); C.callout(ctx, text, clampx(x + dx, 250), clampy(y + dy, 660, 1420), p, size=size)

def flecha(ctx, x0, y0, x1, y1, col, p, lw=12):
    if p <= 0: return
    x1 = x0 + (x1 - x0) * C_ease(p); y1 = y0 + (y1 - y0) * C_ease(p)
    a = math.atan2(y1 - y0, x1 - x0)
    for st, c in ((lw + 8, (0, 0, 0)), (lw, col)):
        ctx.set_line_width(st); ctx.set_source_rgb(*c); ctx.set_line_cap(1); ctx.set_line_join(1)
        ctx.move_to(x0, y0); ctx.line_to(x1, y1); ctx.stroke()
        ctx.move_to(x1 - 34 * math.cos(a - 0.5), y1 - 34 * math.sin(a - 0.5)); ctx.line_to(x1, y1)
        ctx.line_to(x1 - 34 * math.cos(a + 0.5), y1 - 34 * math.sin(a + 0.5)); ctx.stroke()
def C_ease(x): x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3

def giro(ctx, cx, cy, r, t, col, p):
    """flecha circular que gira"""
    if p <= 0: return
    a0 = t * 6; a1 = a0 + 4.6 * p
    for st, c in ((20, (0, 0, 0)), (12, col)):
        ctx.set_line_width(st); ctx.set_source_rgb(*c); ctx.set_line_cap(1)
        ctx.new_path(); ctx.arc(cx, cy, r, a0, a1); ctx.stroke()
        hx, hy = cx + r * math.cos(a1), cy + r * math.sin(a1); ta = a1 + math.pi / 2
        ctx.move_to(hx - 34 * math.cos(ta - 0.5), hy - 34 * math.sin(ta - 0.5)); ctx.line_to(hx, hy)
        ctx.line_to(hx - 34 * math.cos(ta + 0.5), hy - 34 * math.sin(ta + 0.5)); ctx.stroke()

def reloj(C, ctx, t, cx, cy, p):
    """reloj circular de 2 minutos con 4 marcas de 30 s"""
    if p <= 0: return
    t0, t1 = T("pones un reloj") + 0.2, T("cuatro pausas", fin=True) - 0.3
    c = 120 * max(0, min(1, (t - t0) / (t1 - t0)))
    s = C.back(p); ctx.save(); ctx.translate(cx, cy); ctx.scale(s, s)
    R = 150
    ctx.arc(0, 0, R + 34, 0, 7); ctx.set_source_rgba(0.04, 0.08, 0.1, 0.85); ctx.fill()
    ctx.set_line_width(26); ctx.set_source_rgba(0.3, 0.38, 0.4, 1); ctx.arc(0, 0, R, 0, 7); ctx.stroke()
    cols = [(0.4, 0.95, 0.65), (0.45, 0.75, 1.0), (1.0, 0.8, 0.3), (1.0, 0.5, 0.45)]
    for z in range(4):
        a = -math.pi / 2 + z * math.pi / 2; b = a + (math.pi / 2) * max(0, min(1, (c - 30 * z) / 30))
        if b > a: ctx.set_source_rgb(*cols[z]); ctx.arc(0, 0, R, a, b); ctx.stroke()
    for z in range(4):
        a = -math.pi / 2 + z * math.pi / 2
        ctx.set_line_width(8); ctx.set_source_rgb(1, 1, 1); ctx.move_to(0.8 * R * math.cos(a), 0.8 * R * math.sin(a))
        ctx.line_to(1.2 * R * math.cos(a), 1.2 * R * math.sin(a)); ctx.stroke()
    m, sec = int(c) // 60, int(c) % 60
    C.outlined(ctx, f"{m}:{sec:02d}", 0, -10, 86, fill=(1, 1, 1), stroke=10)
    pausa = any(abs(c - q) < 2.2 for q in (30, 60, 90)) or c >= 119.5
    zona = min(4, int(c // 30) + 1)
    C.outlined(ctx, "PAUSA" if pausa else f"ZONA {zona}/4", 0, 72, 50, fill=(1.0, 0.8, 0.3) if pausa else TEAL, stroke=8)
    ctx.restore()

def overlay(ctx, t, A, C):
    Y, R, G = C.YL, C.RED, C.GREEN
    # gancho: tiempo de cepillado
    a0, a1 = T("y casi"), T("vamos") + 0.4
    if a0 - 0.1 <= t < a1:
        v = keyed(t, [(a0, 0), (T("minutos", fin=True), 45)])
        col = R if t > T("dos minutos") else (1, 1, 1)
        badge(C, ctx, t, a0 - 0.1, a1, f"0:{int(round(v)):02d}", col, size=96)
        badge(C, ctx, t, T("dos minutos"), a1, "OBJETIVO 2:00", G, size=60, dy=140)
    # la mano
    a0, a1 = T("frota"), T("así que pones")
    if a0 <= t < a1:
        n = int(max(0, t - a0) * 3.0)
        badge(C, ctx, t, a0, a1, f"FROTES {n}", Bl, size=80)
        badge(C, ctx, t, T("por segundo") - 0.2, a1, "3 POR SEGUNDO", Y, size=60, dy=140)
    label(C, ctx, t, T("motor") , T("pero un motor"), "MOTOR", A, "motor", dx=230, dy=0, size=64)
    p = win(t, T("gira") - 0.1, T("y tú") + 0.2)
    if p:
        x, y = A("headA"); giro(ctx, clampx(x, 260), max(y, 640), 150, t, R, p)
    p = win(t, T("vibre") - 0.1, T("así que usas"))
    if p:
        x, y = A("headA"); y = max(y, 680); C.arrow_dim(ctx, x - 230, x + 230, y, G, p)
    label(C, ctx, t, T("imán") - 0.1, T("cuando la"), "IMÁN", A, "iman", dx=230, dy=-60, size=64)
    label(C, ctx, t, T("bobina") - 0.1, T("cuando la"), "BOBINA", A, "bobina", dx=230, dy=80, size=64)
    # corriente e imán
    a0, a1 = T("cuando la"), T("una y otra")
    if a0 <= t < a1:
        x, y = A("iman"); right = t < T("cuando cambia")
        p = win(t, T("el imán") - 0.3, T("cuando cambia")) if right else win(t, T("a la izquierda") - 0.3, a1)
        if right: flecha(ctx, x - 40, y - 150, x + 200, y - 150, R, p)
        else: flecha(ctx, x + 40, y - 150, x - 200, y - 150, Bl, p)
        badge(C, ctx, t, a0, a1, "CORRIENTE +" if right else "CORRIENTE −", Y if right else Bl, size=70)
    # 31.000 por minuto y 500 por segundo
    a0, a1 = T("así consigues"), T("y aquí")
    if a0 <= t < a1:
        v = keyed(t, [(a0 + 0.3, 0), (T("por minuto", fin=True), 31000)])
        badge(C, ctx, t, a0, a1, f"{int(round(v)):,} / MIN".replace(",", "."), Y, size=88)
        if t > T("más de") - 0.1:
            v2 = keyed(t, [(T("más de"), 0), (T("por segundo", 2, fin=True), 516)])
            badge(C, ctx, t, T("más de") - 0.1, a1, f"{int(round(v2))} / SEGUNDO", Bl, size=70, dy=150)
    # líquido entre las muelas
    label(C, ctx, t, T("pasta") - 0.1, T("y el líquido"), "PASTA + SALIVA", A, "head2", dx=0, dy=-260, size=56)
    label(C, ctx, t, T("y el líquido") + 0.2, T("pero si"), "ENTRE DIENTES", A, "gap", dx=-150, dy=-200, size=56)
    badge(C, ctx, t, T("donde"), T("pero si"), "✗ CERDAS", R, size=72)
    # presión
    a0, a1 = T("pero si"), T("ahora")
    if a0 <= t < a1:
        v = keyed(t, [(a0 + 0.5, 100), (T("frenas", fin=True) + 0.4, 30), (T("por eso") + 1.6, 30), (T("por eso") + 2.4, 100)])
        col = G if v > 70 else R
        badge(C, ctx, t, a0, a1, f"VIBRACIÓN {int(round(v))} %", col, size=76)
    label(C, ctx, t, T("sensor") - 0.1, T("ahora"), "SENSOR", A, "led2", dx=180, dy=120, size=62)
    # reloj
    a0, a1 = T("pones un reloj") - 0.2, T("falta")
    if a0 <= t < a1:
        x, y = A("arch"); reloj(C, ctx, t, x, y, win(t, a0, a1))
    # enchufe
    label(C, ctx, t, T("agua") , T("así que la base"), "AGUA", A, "plug", dx=-200, dy=-260, size=66)
    badge(C, ctx, t, T("enchufes") , T("así que la base"), "✗ 230 V", R, size=84)
    # carga
    label(C, ctx, t, T("bobina", 2) - 0.1, T("otra bobina"), "BOBINA", A, "base", dx=170, dy=80, size=62)
    label(C, ctx, t, T("campo") - 0.1, T("otra bobina"), "CAMPO", A, "base", dx=-200, dy=-280, size=66)
    label(C, ctx, t, T("otra bobina") - 0.1, T("sin ningún"), "BOBINA", A, "bob_m", dx=200, dy=-40, size=62)
    a0, a1 = T("convierte") - 0.3, T("con una carga")
    if a0 <= t < a1:
        v = keyed(t, [(T("otra bobina") + 0.4, 15), (T("sin ningún"), 100)])
        badge(C, ctx, t, a0, a1, f"BATERÍA {int(round(v))} %", G, size=78)
    badge(C, ctx, t, T("sin ningún") + 0.2, T("con una carga"), "✓ 0 CONTACTOS", G, size=78, dy=140)
    a0 = T("con una carga")
    if a0 <= t < DUR + 1:
        v = keyed(t, [(a0 + 0.3, 0), (T("semanas", fin=True), 14)])
        badge(C, ctx, t, a0, DUR + 1, f"{int(round(v))} DÍA" + ("" if int(round(v)) == 1 else "S"), Y, size=92)

def sfx_events(C):
    E = [(0.0, C.s_buzz(4.4), 0.35), (0.1, C.s_whoosh(), 0.3)]
    E += [(T("dos minutos"), C.s_fail(), 0.4), (T("vamos"), C.s_whoosh(), 0.4), (T("frota"), C.s_pop(), 0.3),
          (T("así que pones"), C.s_whoosh(), 0.4), (T("así que pones") + 0.9, C.s_clank(), 0.4), (T("pero un motor"), C.s_buzz(1.5), 0.25),
          (T("vibre"), C.s_fail(), 0.35), (T("así que usas"), C.s_whoosh(), 0.35), (T("así que usas") + 0.9, C.s_clank(), 0.4),
          (T("el imán"), C.s_pop(), 0.45), (T("a la izquierda"), C.s_pop(), 0.45), (T("una y otra"), C.s_buzz(6.5), 0.3),
          (T("por minuto"), C.s_win(), 0.4), (T("y aquí"), C.s_whoosh(), 0.4), (T("las cerdas"), C.s_buzz(6.0), 0.25),
          (T("y el líquido"), C.s_pop(), 0.4), (T("frenas"), C.s_thud(), 0.5), (T("sensor"), C.s_bleep(1400), 0.7),
          (T("sensor") + 0.25, C.s_bleep(1400), 0.7), (T("ahora"), C.s_whoosh(), 0.4)]
    t0, t1 = T("pones un reloj") + 0.2, T("cuatro pausas", fin=True) - 0.3
    for q in (30, 60, 90, 120):
        E.append((t0 + (t1 - t0) * q / 120, C.s_bleep(900), 0.8))
    E += [(T("falta"), C.s_whoosh(), 0.4), (T("enchufes"), C.s_fail(), 0.45), (T("así que la base"), C.s_whoosh(), 0.4),
          (T("campo"), C.s_pop(), 0.4), (T("otra bobina"), C.s_pop(), 0.4), (T("sin ningún"), C.s_win(), 0.4),
          (T("con una carga"), C.s_buzz(2.5), 0.25), (T("semanas"), C.s_coin(), 0.4), (T("sígueme"), C.s_whoosh(), 0.4)]
    return E
