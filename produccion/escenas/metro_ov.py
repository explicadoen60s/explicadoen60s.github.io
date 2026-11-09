# Capa 2D de «¿Y si construyes el metro bajo tu ciudad?»
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("metro")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"metro", "veinte", "calles", "tráfico", "zanja", "pozo", "tuneladora", "cien", "toneladas", "cuchillas", "derrumba",
            "escudo", "dovelas", "siete", "anillo", "empujándose", "cinta", "camiones", "madrid", "dieciocho", "ciento",
            "kilómetros", "cúbicos", "hundir", "milímetro", "vías", "estaciones"}

def ss(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def sg(t, a, b): return ss((t - a) / (b - a))
def miles(v): return f"{int(round(v)):,}".replace(",", ".")
BY = H * 0.265

def cross(ctx, x, y, r, p, col=(0.93, 0.2, 0.22)):
    if p <= 0: return
    ctx.save(); ctx.set_line_cap(1)
    for lw, c in ((26, (0, 0, 0)), (15, col)):
        ctx.set_line_width(lw); ctx.set_source_rgba(*c, p)
        ctx.arc(x, y, r, 0, math.tau); ctx.stroke()
        ctx.move_to(x - r * 0.7, y - r * 0.7); ctx.line_to(x + r * 0.7, y + r * 0.7); ctx.stroke()
    ctx.restore()

def vdim(C, ctx, x, y0, y1, p, col, text):
    """cota vertical con texto al lado"""
    if p <= 0: return
    y1b = y0 + (y1 - y0) * C.ease(p)
    for lw, c in ((17, (0, 0, 0)), (9, col)):
        ctx.set_line_width(lw); ctx.set_source_rgb(*c); ctx.set_line_cap(1)
        ctx.move_to(x, y0); ctx.line_to(x, y1b); ctx.stroke()
        for yy in (y0, y1b):
            ctx.move_to(x - 30, yy); ctx.line_to(x + 30, yy); ctx.stroke()
        ctx.move_to(x - 20, y1b - 26); ctx.line_to(x, y1b); ctx.line_to(x + 20, y1b - 26); ctx.stroke()
    C.badge(ctx, text, clampx(x + 150, 200), (y0 + y1b) / 2, p, col, size=62)

def overlay(ctx, t, A, C):
    Y, R, G, B = C.YL, C.RED, C.GREEN, (0.45, 0.75, 1.0)
    # profundidad del túnel
    a0, a1 = T("bajo tus pies") + 0.3, T("y si tuvieras") + 0.3
    p = win(t, a0, a1)
    if p:
        (xs, ys), (xa, ya) = A("surf"), A("axis")
        d = 20 * sg(t, a0, T("veinte", fin=True))
        vdim(C, ctx, xs, ys, ya, p, Y, "−%d M" % round(d))
    # la zanja no vale
    p = win(t, T("no puedes") + 0.9, T("así que bajas"))
    if p: x, y = A("zanja"); cross(ctx, clampx(x, 200), clampy(y - 40, 600, 1300), 80, p)
    # pozo: profundidad mientras baja la tuneladora
    a0, a1 = T("así que bajas"), T("mide casi")
    p = win(t, a0, a1)
    if p:
        x, y = A("tbm"); d = 20 * sg(t, a0, T("la tuneladora") + 0.2)
        C.badge(ctx, "−%d M" % round(d), W / 2, BY, p, Y, size=80)
    # 100 m y 1.500 t
    a0, a1 = T("mide casi"), T("delante tiene")
    p = win(t, a0, a1)
    if p:
        (xa, ya), (xb, yb) = A("rA"), A("rB")
        u = sg(t, a0, T("cien metros", fin=True))
        C.arrow_dim(ctx, xa, xa + (xb - xa) * u, ya + 60, Y, p)
        C.badge(ctx, "%d M" % round(100 * u), (xa + xb) / 2, ya + 170, p, Y, size=72)
        q = win(t, T("y pesa"), a1)
        if q: C.badge(ctx, miles(1500 * sg(t, T("y pesa"), T("toneladas", fin=True))) + " T", W / 2, BY, q, (1, 1, 1), size=84)
    # derrumbe
    p = win(t, T("se derrumba"), T("así que justo"))
    if p: x, y = A("derr"); cross(ctx, x, clampy(y - 130, 600, 1300), 75, p)
    # escudo aguanta
    badge(C, ctx, t, T("sujeta el terreno"), T("y a cada paso"), "✓ 0 DERRUMBES", G, size=70)
    # piezas y anillos
    a0, a1 = T("unos brazos") - 0.2, T("la tuneladora avanza")
    if a0 <= t < a1:
        b0, b1 = a0, T("siete piezas") + 1.4
        if t < T("luego otro"):
            n = int(7 * sg(t, b0, b1) + 0.999) if t > b0 + 0.05 else 0
            C.badge(ctx, "PIEZA %d/7" % max(n, 1), W / 2, BY, win(t, a0, T("luego otro")), Y, size=76)
        else:
            n = 2 if t < T("y otro") + 0.4 else 3
            C.badge(ctx, "ANILLO %d" % n, W / 2, BY, win(t, T("luego otro"), a1), Y, size=78)
    # avance empujando: anillos y metros
    a0, a1 = T("la tuneladora avanza"), T("pero la tierra")
    if a0 <= t < a1:
        C.badge(ctx, "+1,6 M", W / 2, BY, win(t, a0 + 0.4, a1), G, size=76)
    # metros al día, días, kilómetros
    a0, a1 = T("avanzó"), T("y sacó")
    if a0 <= t < a1:
        if t < T("en ciento"):
            C.badge(ctx, "%d M / DÍA" % round(18 * sg(t, a0, a0 + 2.2)), W / 2, BY, win(t, a0, T("en ciento")), Y, size=78)
        else:
            u = sg(t, T("en ciento"), T("casi tres") + 0.8)
            C.badge(ctx, "DÍA %d" % round(1 + 146 * u), W / 2, BY, win(t, T("en ciento"), a1), Y, size=78)
            C.badge(ctx, "%s M" % miles(18 + (2646 - 18) * u), W / 2, BY + 140, win(t, T("en ciento") + 0.2, a1), (1, 1, 1), size=66)
    a0, a1 = T("y sacó"), T("pero no puede")
    if a0 <= t < a1:
        C.badge(ctx, miles(189000 * sg(t, a0 + 0.3, T("cúbicos", fin=True))) + " M³", W / 2, BY, win(t, a0, a1), Y, size=80)
    # el edificio no se puede hundir
    p = win(t, T("hundir") , T("así que se mide"))
    if p: x, y = A("casa"); cross(ctx, clampx(x, 220), clampy(y - 60, 600, 1300), 75, p)
    a0, a1 = T("así que se mide"), T("cuando termina")
    if a0 <= t < a1:
        v = 0.4 + 0.6 * sg(t, T("aunque sea"), T("milímetro", fin=True)) + 0.05 * math.sin(t * 9)
        C.badge(ctx, ("%.1f MM" % v).replace(".", ","), W / 2, BY, win(t, a0 + 0.4, a1), G, size=80)
    label(C, ctx, t, T("llegan las vías"), T("sígueme"), "VÍAS", A, "vias", dx=0, dy=110, size=52)
    label(C, ctx, t, T("los cables"), T("sígueme"), "CABLES", A, "cables", dx=0, dy=-110, size=52)

def sfx_events(C):
    E = [(0.0, C.s_thud(), 0.5), (0.2, C.s_buzz(1.2), 0.25), (T("bajo tus pies"), C.s_whoosh(), 0.4), (T("vamos a excavarlo") - 0.4, C.s_whoosh(), 0.5),
         (T("no puedes") + 0.9, C.s_fail(), 0.45), (T("así que bajas"), C.s_whoosh(), 0.4), (T("la tuneladora") + 0.1, C.s_thud(), 0.6),
         (T("mide casi"), C.s_whoosh(), 0.4), (T("y pesa"), C.s_thud(), 0.5), (T("delante tiene"), C.s_buzz(2.5), 0.25),
         (T("se derrumba"), C.s_fail(), 0.5), (T("un escudo"), C.s_clank(), 0.5), (T("sujeta el terreno"), C.s_win(), 0.35),
         (T("la tuneladora avanza"), C.s_thud(), 0.5), (T("así que una cinta"), C.s_whoosh(), 0.4), (T("y de ahí"), C.s_thud(), 0.4),
         (T("avanzó"), C.s_whoosh(), 0.4), (T("en ciento"), C.s_coin(), 0.35), (T("y sacó"), C.s_coin(), 0.35),
         (T("hundir"), C.s_fail(), 0.45), (T("así que se mide"), C.s_pop(), 0.4), (T("llegan las vías"), C.s_clank(), 0.4),
         (T("los cables"), C.s_pop(), 0.35), (T("y las estaciones"), C.s_whoosh(), 0.45), (T("sígueme"), C.s_win(), 0.35)]
    for j in range(7): E.append((mix_t(T("unos brazos") - 0.2, T("siete piezas") + 1.4, (j + 1) / 7), C.s_clank(), 0.4))
    E += [(T("luego otro") + 0.3, C.s_clank(), 0.4), (T("y otro") + 0.3, C.s_clank(), 0.4)]
    return E

def mix_t(a, b, u):
    # momento en que la pieza j queda colocada con la rampa suave del 3D
    lo, hi = 0.0, 1.0
    for _ in range(30):
        m = (lo + hi) / 2
        if ss(m) < u: lo = m
        else: hi = m
    return a + (b - a) * lo
