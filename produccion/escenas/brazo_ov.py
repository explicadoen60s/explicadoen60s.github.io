# Capa 2D de «Si tuvieras que inventar un brazo…»
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("brazo")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"móvil", "dos", "kilos", "hueso", "bisagra", "codo", "motor", "músculo", "bíceps", "tirar", "empuja", "tendón",
            "cuatro", "treinta", "cinco", "ocho", "doscientos", "gramos", "centímetro", "nueve", "rapidez", "pelota", "tríceps", "parejas"}
BY = H * 0.265
YEL = (1.0, 0.82, 0.16); PINK = (1.0, 0.45, 0.75); BLUE = (0.45, 0.75, 1.0)

def ss(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def sg(t, a, b): return ss((t - a) / (b - a))

def arrow(C, ctx, x0, y0, x1, y1, col, p, lw=16):
    if p <= 0: return
    x1 = x0 + (x1 - x0) * C.ease(p); y1 = y0 + (y1 - y0) * C.ease(p)
    d = math.hypot(x1 - x0, y1 - y0)
    if d < 4: return
    ux, uy = (x1 - x0) / d, (y1 - y0) / d; hl = lw * 2.4
    bx, by = x1 - ux * hl, y1 - uy * hl
    ctx.save(); ctx.set_line_cap(1); ctx.set_line_join(1)
    for w, c in ((lw + 10, (0, 0, 0)), (lw, col)):
        ctx.set_source_rgba(*c, min(1, p * 2)); ctx.set_line_width(w)
        ctx.move_to(x0, y0); ctx.line_to(bx, by); ctx.stroke()
        ctx.move_to(x1, y1); ctx.line_to(bx - uy * hl * 0.7, by + ux * hl * 0.7); ctx.line_to(bx + uy * hl * 0.7, by - ux * hl * 0.7)
        ctx.close_path(); ctx.fill_preserve(); ctx.stroke()
    ctx.restore()

def cross(ctx, x, y, r, p, col=(0.93, 0.2, 0.22)):
    if p <= 0: return
    ctx.save(); ctx.set_line_cap(1)
    for lw, c in ((26, (0, 0, 0)), (15, col)):
        ctx.set_line_width(lw); ctx.set_source_rgba(*c, p)
        ctx.move_to(x - r, y - r); ctx.line_to(x + r, y + r); ctx.move_to(x + r, y - r); ctx.line_to(x - r, y + r); ctx.stroke()
    ctx.restore()

def gauge(C, ctx, v, vmax, p, col=YEL):
    """medidor de la fuerza del bíceps (kg): cifra + barra horizontal"""
    if p <= 0: return
    C.badge(ctx, ("%.2f KG" % v).replace(".", ","), W / 2, BY, p, col, size=80)
    w = 520 * C.ease(p); x0 = W / 2 - w / 2; y0 = BY + 92
    C.rrect(ctx, x0, y0, w, 34, 17); ctx.set_source_rgba(0.1, 0.12, 0.16, 0.92 * p); ctx.fill()
    f = max(0.0, min(1.0, v / vmax))
    if f * w > 30: C.rrect(ctx, x0 + 5, y0 + 5, (w - 10) * f, 24, 12); ctx.set_source_rgba(*col, p); ctx.fill()
    for k in range(1, 4):
        xx = x0 + w * k / 4; ctx.set_source_rgba(1, 1, 1, 0.4 * p); ctx.set_line_width(3); ctx.move_to(xx, y0 + 4); ctx.line_to(xx, y0 + 30); ctx.stroke()

def num(C, ctx, s, x, y, p, col=YEL, size=72):
    if p > 0: C.outlined(ctx, s, clampx(x, 120), y, size, fill=col, stroke=12, alpha=min(1, p * 1.5), scale=C.back(p))

def overlay(ctx, t, A, C):
    R, G = C.RED, C.GREEN
    # --- apertura: el móvil en la mano y el medidor del bíceps sube a 1,75 kg ---
    a1 = T("vamos a inventar")
    p = win(t, 0.0, a1)
    if p:
        v = 1.75 * sg(t, 0.2, T("kilos", fin=True))
        gauge(C, ctx, v, 2.0, p)
        x0, y0 = A("ins"); x1, y1 = A("btop")
        arrow(C, ctx, x0, y0 - 30, x0 + (x1 - x0) * 0.55, y0 + (y1 - y0) * 0.55, YEL, sg(t, 0.3, 1.0), lw=14)
        x, y = A("hand"); num(C, ctx, "200 G", x + 10, y + 150, win(t, 0.9, T("por qué")), BLUE, 60)
    label(C, ctx, t, T("un hueso rígido") + 0.3, T("y una bisagra"), "HUESO", A, "fa", dy=-150, size=60)
    label(C, ctx, t, T("y una bisagra") + 0.5, T("pero un hueso"), "CODO", A, "elbow", dx=-60, dy=-170, size=60)
    p = win(t, T("pero un hueso") + 0.9, T("así que le pones"))
    if p: C.badge(ctx, "✗ MOTOR", W / 2, BY, p, R, size=72)
    label(C, ctx, t, T("el bíceps") - 0.2, T("encogerse"), "BÍCEPS", A, "bic", dx=150, dy=-60, size=60)
    # tira (sí) / empuja (no)
    a, b = T("encogerse"), T("nunca empuja")
    p = win(t, a, b + 0.1)
    if p:
        x0, y0 = A("ins"); x1, y1 = A("btop")
        arrow(C, ctx, x0 + 70, y0, x0 + 70 + (x1 - x0) * 0.6, y0 + (y1 - y0) * 0.6, YEL, sg(t, a, a + 0.5))
    a, b = T("nunca empuja"), T("lo atas al hueso")
    p = win(t, a, b)
    if p:
        x0, y0 = A("bic"); x1, y1 = A("ins")
        arrow(C, ctx, x0 + 90, y0 - 60, x1 + 90, y1, (0.85, 0.85, 0.9), sg(t, a, a + 0.4))
        cross(ctx, x0 + 90, (y0 + y1) / 2, 70, sg(t, a + 0.3, a + 0.6))
    label(C, ctx, t, T("el tendón") - 0.1, T("pero ojo") + 0.4, "TENDÓN", A, "ins", dx=190, dy=-40, size=60)
    p = win(t, T("no lo atas cerca") + 0.6, T("lo atas a solo"))
    if p: x, y = A("ghost"); cross(ctx, x, y - 110, 55, p)
    # cotas: 4 cm y 35 cm
    a, b = T("lo atas a solo"), T("como tira")
    p = win(t, a + 0.6, b)
    if p:
        xe, ye = A("elbow"); xi, yi = A("ins"); yy = ye + 150
        C.arrow_dim(ctx, xe, xi, yy, G, p, lw=8)
        num(C, ctx, "4 CM", (xe + xi) / 2, yy + 85, sg(t, a + 0.9, a + 1.3), G, 72)
    a2 = T("y la mano queda")
    p = win(t, a2 + 0.3, b)
    if p:
        xe, ye = A("elbow"); xh, yh = A("hand"); yy = ye + 290
        C.arrow_dim(ctx, xe, xh, yy, YEL, p, lw=8)
        num(C, ctx, "35 CM", (xe + xh) / 2, yy + 85, sg(t, a2 + 1.0, a2 + 1.5), YEL, 72)
    # fuerza ×8
    a, b = T("como tira"), T("por eso tu móvil")
    p = win(t, a + 0.3, b)
    if p:
        xh, yh = A("hand"); arrow(C, ctx, xh, yh + 40, xh, yh + 100, BLUE, sg(t, a + 0.3, a + 0.8))
        x0, y0 = A("ins"); x1, y1 = A("btop")
        L = 120 + 330 * sg(t, T("tiene que hacer"), T("más fuerza", fin=True))
        arrow(C, ctx, x0 + 80, y0 + 20, x0 + 80, y0 + 20 - L, YEL, sg(t, a + 0.6, a + 1.0), lw=26)
        n = 1 + int(round(7 * sg(t, T("tiene que hacer"), T("más fuerza", fin=True))))
        C.badge(ctx, "×%d" % n, W / 2, BY, win(t, T("tiene que hacer"), b), YEL, size=96)
    # 200 g → 1,75 kg
    a, b = T("por eso tu móvil"), T("entonces es")
    p = win(t, a, b + 0.8)
    if p:
        v = 1.75 * sg(t, T("le cuesta"), T("kilos", 2, fin=True))
        gauge(C, ctx, v, 2.0, p)
        x, y = A("phone"); num(C, ctx, "200 G", x - 20, y - 50, win(t, T("de doscientos"), b + 0.8), BLUE, 64)
    # 1 cm → 9 cm
    a, b = T("si el bíceps se encoge"), T("pierdes fuerza")
    p = win(t, a + 0.3, b + 0.3)
    if p:
        u = sg(t, a + 0.6, T("tu mano sube") + 1.0)
        x, y = A("bic"); arrow(C, ctx, x + 150, y + 60, x + 150, y - 10, YEL, sg(t, a + 0.5, a + 0.9), lw=12)
        num(C, ctx, ("%.1f CM" % (1.0 * u)).replace(".", ","), x + 150, y + 120, sg(t, a + 0.4, a + 0.8), YEL, 58)
        xh, yh = A("hand"); arrow(C, ctx, xh - 30, yh + 110, xh - 30, yh - 40, G, sg(t, T("tu mano sube"), T("tu mano sube") + 0.5), lw=16)
        num(C, ctx, "%d CM" % int(round(9 * u)), xh - 30, yh + 180, sg(t, T("tu mano sube") - 0.2, T("tu mano sube") + 0.2), G, 66)
    a, b = T("pierdes fuerza"), T("por eso puedes lanzar")
    p = win(t, a + 0.2, b + 0.4)
    if p:
        C.badge(ctx, "FUERZA ÷9", W / 2 - 230, BY, win(t, a, b + 0.4), R, size=56)
        C.badge(ctx, "RAPIDEZ ×9", W / 2 + 200, BY, win(t, T("pero ganas"), b + 0.4), G, size=56)
    # pelota
    a, b = T("por eso puedes lanzar"), T("pero falta")
    p = win(t, a + 1.0, b + 0.4)
    if p:
        x, y = A("ball")
        for k in range(3):
            ctx.set_source_rgba(1, 1, 1, 0.6 * p); ctx.set_line_width(8); ctx.set_line_cap(1)
            ctx.move_to(x - 70 - 40 * k, y + 50 + 30 * k); ctx.line_to(x - 170 - 40 * k, y + 110 + 30 * k); ctx.stroke()
    # ¿quién estira?
    a, b = T("si el músculo solo tira"), T("así que pones otro")
    p = win(t, T("quién vuelve"), b + 0.3)
    if p:
        x, y = A("fa"); C.outlined(ctx, "?", x + 230, y - 60, 170, fill=YEL, stroke=14, alpha=p, scale=C.back(p))
    label(C, ctx, t, T("el tríceps") - 0.2, T("uno tira") + 0.3, "TRÍCEPS", A, "tri", dx=-60, dy=-260, size=60)
    # por parejas: flechas que se alternan
    a = T("uno tira")
    if a <= t < DUR:
        ph = math.sin((t - a) / 1.6 * math.pi)
        x0, y0 = A("ins"); x1, y1 = A("btop"); xt, yt = A("tri")
        fade = win(t, a, DUR - 0.3)
        if ph < 0: arrow(C, ctx, x0 + 80, y0, x0 + 80 + (x1 - x0) * 0.5, y0 + (y1 - y0) * 0.5, YEL, min(fade, -ph * 2))
        else: arrow(C, ctx, xt - 90, yt - 120, xt - 90, yt + 170, PINK, min(fade, ph * 2))

def sfx_events(C):
    E = [(0.0, C.s_whoosh(), 0.45), (0.4, C.s_pop(), 0.35), (T("vamos a inventar"), C.s_whoosh(), 0.4),
         (T("un hueso rígido"), C.s_thud(), 0.5), (T("y una bisagra") + 0.2, C.s_clank(), 0.5), (T("pero un hueso") + 0.3, C.s_thud(), 0.5),
         (T("pero un hueso") + 0.9, C.s_fail(), 0.35), (T("el bíceps") - 0.3, C.s_pop(), 0.5), (T("encogerse"), C.s_whoosh(), 0.45),
         (T("nunca empuja") + 0.3, C.s_fail(), 0.4), (T("el tendón"), C.s_pop(), 0.45), (T("no lo atas cerca") + 0.6, C.s_fail(), 0.35),
         (T("lo atas a solo") + 0.9, C.s_pop(), 0.45), (T("y la mano queda") + 1.0, C.s_pop(), 0.45), (T("tiene que hacer"), C.s_whoosh(), 0.4),
         (T("le cuesta"), C.s_coin(), 0.4), (T("tu mano sube"), C.s_whoosh(), 0.4), (T("por eso puedes lanzar") + 0.8, C.s_whoosh(), 0.6),
         (T("quién vuelve"), C.s_pop(), 0.4), (T("el tríceps") - 0.2, C.s_pop(), 0.5), (T("siempre trabajan"), C.s_win(), 0.4),
         (T("sígueme"), C.s_whoosh(), 0.4)]
    return E
