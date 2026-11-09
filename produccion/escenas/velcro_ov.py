# Capa 2D de «Si tuvieras que inventar el velcro…»
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("velcro")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"velcro", "cardos", "microscopio", "ganchito", "ganchos", "bucles", "anillo", "algodón", "nailon", "cortas", "duros",
            "trescientos", "golpe", "todos", "borde", "pocos", "catorce", "cincuenta", "suizo"}
NC = 25
BY = H * 0.265

def ss(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def sg(t, a, b): return ss((t - a) / (b - a))

def arrow(ctx, x, y, L, p, col, lw=12, up=True):
    if p <= 0 or L < 4: return
    d = -1 if up else 1; y1 = y + d * L * p
    ctx.save(); ctx.set_line_cap(1); ctx.set_line_join(1)
    for w, c in ((lw + 8, (0, 0, 0)), (lw, col)):
        ctx.set_line_width(w); ctx.set_source_rgba(*c, min(1, p * 2))
        ctx.move_to(x, y); ctx.line_to(x, y1); ctx.stroke()
        ctx.move_to(x - 22, y1 - d * 22); ctx.line_to(x, y1); ctx.line_to(x + 22, y1 - d * 22); ctx.stroke()
    ctx.restore()

def cross(ctx, x, y, r, p, col=(0.93, 0.2, 0.22)):
    if p <= 0: return
    ctx.save(); ctx.set_line_cap(1)
    for lw, c in ((26, (0, 0, 0)), (15, col)):
        ctx.set_line_width(lw); ctx.set_source_rgba(*c, p)
        ctx.arc(x, y, r, 0, math.tau); ctx.stroke()
        ctx.move_to(x - r * 0.7, y - r * 0.7); ctx.line_to(x + r * 0.7, y + r * 0.7); ctx.stroke()
    ctx.restore()

def scope(ctx, p):
    """máscara redonda de microscopio"""
    if p <= 0: return
    cx, cy, r = W / 2, H * 0.47, 470 + 900 * (1 - p)
    ctx.save(); ctx.set_fill_rule(1)
    ctx.rectangle(0, 0, W, H); ctx.arc(cx, cy, r, 0, math.tau); ctx.set_source_rgba(0.02, 0.02, 0.03, 0.96 * p); ctx.fill()
    ctx.set_line_width(14); ctx.set_source_rgba(0.6, 0.62, 0.7, p); ctx.arc(cx, cy, r, 0, math.tau); ctx.stroke()
    ctx.set_line_width(3); ctx.set_source_rgba(1, 1, 1, 0.25 * p)
    ctx.move_to(cx - r, cy); ctx.line_to(cx + r, cy); ctx.move_to(cx, cy - r); ctx.line_to(cx, cy + r); ctx.stroke()
    ctx.restore()

def eng(A): return int(round(A("eng")[0] / W * 1000))

def overlay(ctx, t, A, C):
    Y, R, G, B = C.YL, C.RED, C.GREEN, (0.45, 0.75, 1.0)
    # contador de ganchos enganchados al despegar (inicio)
    a1 = T("vamos a inventar") + 0.6
    if t < a1:
        n = eng(A); C.badge(ctx, "%d ENGANCHADOS" % n, W / 2, BY, win(t, -1, a1), G if n > 150 else (Y if n > 0 else R), size=66)
        for i in range(NC):
            l = A("l%d" % i)[0] / W
            if 0.05 < l < 1.2:
                x, y = A("c%d" % i); arrow(ctx, x, y - 20, 120, 1 - abs(l - 0.5) * 1.6, Y, lw=10)
    C.callout(ctx, "GANCHOS", W * 0.66, H * 0.38, win(t, T("la funda"), T("vamos a inventar")), size=58)
    C.callout(ctx, "BUCLES", W * 0.34, H * 0.66, win(t, T("la funda") + 0.3, T("vamos a inventar")), size=58)
    # 1941
    a0, a1 = T("en mil novecientos cuarenta"), T("los mira")
    if a0 <= t < a1: C.badge(ctx, "1941", W / 2, BY, win(t, a0, a1), Y, size=96)
    label(C, ctx, t, T("los dos van") + 0.4, T("los mira") - 0.1, "CARDOS", A, "burr", dx=0, dy=-260, size=64)
    # microscopio
    a0, a1 = T("los mira"), T("así que quieres") - 0.5
    scope(ctx, win(t, a0 - 0.2, a1, fade=0.3))
    if a0 <= t < a1:
        z = 1 + int(49 * sg(t, a0, a0 + 1.2))
        C.badge(ctx, "×%d" % (z * 2 if z > 1 else 1), W - 240, H * 0.70, win(t, a0 + 0.2, a1), B, size=60)
        if t > T("y cada pinchito"):
            C.callout(ctx, "GANCHO", W / 2, H * 0.30, win(t, T("y cada pinchito") + 0.5, a1), size=64)
    # sin bucles: ✗
    a0 = T("pero los ganchos")
    p = win(t, a0 + 1.2, T("así que la otra"))
    if p: x, y = A("hooks"); cross(ctx, W / 2, y + 140, 80, p)
    label(C, ctx, t, T("hilos en forma"), T("al apretar"), "BUCLES", A, "loops", dx=60, dy=160, size=60)
    a0, a1 = T("al apretar"), T("pero el algodón")
    if a0 + 0.3 <= t < a1:
        n = eng(A); C.badge(ctx, "%d ENGANCHADOS" % n, W / 2, BY, win(t, a0 + 0.3, a1), G, size=66)
    a0, a1 = T("pero el algodón"), T("tejes bucles") - 0.2
    if a0 <= t < a1:
        nyl = t > T("así que usas")
        C.badge(ctx, ("✓ NAILON" if nyl else "✗ ALGODÓN"), W / 2, BY, win(t, a0, a1), (B if nyl else R), size=72)
    # taller de corte
    label(C, ctx, t, T("y luego cortas") + 0.3, T("así salen"), "CORTE", A, "blade", dx=0, dy=-170, size=60)
    a0, a1 = T("así salen"), T("y aquí viene")
    if a0 <= t < a1: C.badge(ctx, "✓ NAILON = GANCHO", W / 2, BY, win(t, a0, a1), B, size=62)
    # un solo gancho: medidor casi a cero y la anilla se suelta
    a0, a1 = T("y aquí viene"), T("pero hay unos") - 0.3
    if a0 + 0.3 <= t < a1:
        p = win(t, a0 + 0.3, a1)
        f = 0.12 * sg(t, T("un solo gancho") + 0.4, T("un solo gancho") + 1.2) * (1 - sg(t, T("un solo gancho") + 1.35, T("un solo gancho") + 1.6))
        x0, y0, w, h = 200, BY - 40, 680, 70
        C.rrect(ctx, x0 - 10, y0 - 10, w + 20, h + 20, 22); ctx.set_source_rgba(0.13, 0.15, 0.19, 0.92 * p); ctx.fill()
        C.rrect(ctx, x0, y0, max(12, w * f), h, 16); ctx.set_source_rgba(*R, p); ctx.fill()
        C.outlined(ctx, "FUERZA", W / 2, y0 + h / 2, 46, alpha=p, stroke=8)
        x, y = A("ring"); arrow(ctx, x, y + 30, 150, p * (1 if f > 0.01 else 0), R, up=False)
    # 300 en un cuadrado de 2,5 cm
    a0, a1 = T("pero hay unos"), T("si tiras de golpe")
    if a0 <= t < a1:
        p = win(t, a0, a1)
        pts = [A("sq%d" % i) for i in range(4)]
        ctx.save(); ctx.set_line_join(1)
        for lw, c in ((16, (0, 0, 0)), (9, Y)):
            ctx.set_line_width(lw); ctx.set_source_rgba(*c, p)
            ctx.move_to(*pts[0]); [ctx.line_to(*q) for q in pts[1:]]; ctx.close_path(); ctx.stroke()
        ctx.restore()
        n = int(300 * sg(t, a0 + 0.4, T("pulgada", fin=True) + 0.2))
        C.badge(ctx, "%d" % n, W / 2, BY, p, Y, size=96)
        q = win(t, T("un cuadrado"), a1)
        if q:
            yb = max(pts[0][1], pts[1][1]) + 70
            C.arrow_dim(ctx, pts[0][0], pts[1][0], yb, Y, q)
            C.outlined(ctx, "2,5 cm", (pts[0][0] + pts[1][0]) / 2, yb + 80, 58, fill=Y, alpha=q, stroke=10)
    # tirón de golpe: todos a la vez
    a0, a1 = T("si tiras de golpe"), T("pero si lo despegas")
    if a0 <= t < a1:
        p = win(t, a0, a1)
        for i in range(0, NC, 2):
            x, y = A("c%d" % i); arrow(ctx, x, y - 20, 150 * sg(t, a0 + 0.1, a0 + 0.6), p, Y, lw=9)
        C.badge(ctx, "%d ENGANCHADOS" % eng(A), W / 2, BY, p, G, size=66)
    # despegar desde el borde: de pocos en pocos
    a0, a1 = T("pero si lo despegas"), T("tardó")
    if a0 <= t < a1:
        p = win(t, a0, a1); n = eng(A)
        C.badge(ctx, "%d ENGANCHADOS" % n, W / 2, BY, p, G if n > 150 else (Y if n > 0 else R), size=66)
        for i in range(NC):
            l = A("l%d" % i)[0] / W
            if 0.02 < l < 1.0:
                x, y = A("c%d" % i); arrow(ctx, x, y - 20, 140, p * (1 - abs(l - 0.4) * 1.5), Y, lw=11)
    # 1941 → 1955
    a0, a1 = T("tardó"), T("sígueme") + 0.2
    if a0 <= t < a1:
        yr = int(round(1941 + 14 * sg(t, a0 + 0.2, T("catorce", fin=True) + 0.4)))
        C.badge(ctx, "%d" % yr, W / 2, H * 0.31, win(t, a0, a1), Y if yr < 1955 else G, size=96)
        q = win(t, T("lo patentó"), a1)
        if q: C.badge(ctx, "PATENTE", W / 2, H * 0.31 + 150, q, B, size=56)

def sfx_events(C):
    E = [(0.0, C.s_buzz(2.6), 0.35), (0.05, C.s_whoosh(), 0.4), (T("vamos a inventar"), C.s_whoosh(), 0.4),
         (T("en mil novecientos cuarenta"), C.s_pop(), 0.5), (T("los dos van") + 0.4, C.s_pop(), 0.4), (T("los mira"), C.s_whoosh(), 0.45),
         (T("y cada pinchito") + 0.5, C.s_pop(), 0.5), (T("así que quieres") - 0.5, C.s_whoosh(), 0.4), (T("una tira cubierta"), C.s_pop(), 0.45),
         (T("pero los ganchos") + 1.2, C.s_fail(), 0.4), (T("así que la otra"), C.s_pop(), 0.45), (T("al apretar") + 0.8, C.s_thud(), 0.5),
         (T("pero el algodón") + 0.5, C.s_fail(), 0.4), (T("así que usas"), C.s_win(), 0.4), (T("tejes bucles") - 0.3, C.s_whoosh(), 0.4),
         (T("y aquí viene"), C.s_pop(), 0.4), (T("un solo gancho") + 1.4, C.s_fail(), 0.4), (T("pero hay unos") - 0.2, C.s_whoosh(), 0.4),
         (T("si tiras de golpe"), C.s_thud(), 0.55), (T("y aguanta"), C.s_win(), 0.4), (T("pero si lo despegas"), C.s_buzz(4.0), 0.3),
         (T("y por eso suena"), C.s_buzz(1.5), 0.35), (T("tardó"), C.s_whoosh(), 0.4), (T("lo patentó") + 0.5, C.s_win(), 0.4),
         (T("sígueme"), C.s_whoosh(), 0.4)]
    for k in range(3): E.append((T("y luego cortas") + 0.55 + 0.65 * k, C.s_clank(), 0.35))
    return E
