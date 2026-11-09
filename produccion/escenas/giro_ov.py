# Capa 2D de «Giras el móvil y la pantalla gira: así sabe dónde está el suelo»
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("giro")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"giras", "gira", "suelo", "chip", "arroz", "acelerómetro", "silicio", "flota", "muelles", "dedos", "peine", "fijos",
            "gravedad", "abajo", "nanómetros", "virus", "electricidad", "carga", "diferencia", "tres", "tumbas", "lado",
            "uno", "cero", "cientos", "segundo", "pasos"}

def sg(t, a, b):
    x = max(0.0, min(1.0, (t - a) / (b - a))); return x * x * (3 - 2 * x)
def coma(v, n=1): return f"{v:.{n}f}".replace(".", ",")

def drop(t, t0, amp=-0.32):
    if t < t0: return 0.0
    u = t - t0; return amp * (1 - math.exp(-3.2 * u) * math.cos(8.5 * u))

def mass_d(t):
    g = T("la gravedad tira") + 0.5; n = T("el bloque se mueve")
    if t < g: return 0.0
    if t < n - 0.3: return drop(t, g)
    if t < n + 0.1: return drop(t, g) * (1 - sg(t, n - 0.3, n))
    return drop(t, n + 0.1)

def cargas(t):
    """reparto de carga (%) entre los huecos de abajo y de arriba de cada dedo móvil"""
    d = mass_d(t); ca = 1 / max(0.05, 0.53 - d); cb = 1 / max(0.05, 0.53 + d)
    return 100 * ca / (ca + cb), 100 * cb / (ca + cb)

def phone_icon(ctx, x, y, p, ang=0.0):
    if p <= 0: return
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang); s = 0.6 + 0.4 * sg(p, 0, 1); ctx.scale(s, s)
    C_ = (0.95, 0.96, 1.0)
    ctx.set_source_rgba(0.08, 0.09, 0.13, 0.9 * p); rr(ctx, -62, -112, 124, 224, 22); ctx.fill()
    ctx.set_line_width(9); ctx.set_source_rgba(*C_, p); rr(ctx, -50, -100, 100, 200, 18); ctx.stroke()
    ctx.arc(0, 78, 8, 0, math.tau); ctx.fill()
    ctx.restore()

def rr(ctx, x, y, w, h, r):
    ctx.new_sub_path(); ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0); ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi); ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi); ctx.close_path()

def down_arrow(ctx, x, y0, y1, p, col):
    if p <= 0: return
    y1 = y0 + (y1 - y0) * sg(p, 0, 1)
    ctx.save(); ctx.set_line_cap(1); ctx.set_line_join(1)
    for lw, c in ((26, (0, 0, 0)), (14, col)):
        ctx.set_line_width(lw); ctx.set_source_rgba(*c, p)
        ctx.move_to(x, y0); ctx.line_to(x, y1); ctx.stroke()
        ctx.move_to(x - 30, y1 - 34); ctx.line_to(x, y1); ctx.line_to(x + 30, y1 - 34); ctx.stroke()
    ctx.restore()

def cross(ctx, x, y, r, p, col=(0.93, 0.2, 0.22)):
    if p <= 0: return
    ctx.save(); ctx.set_line_cap(1)
    for lw, c in ((24, (0, 0, 0)), (13, col)):
        ctx.set_line_width(lw); ctx.set_source_rgba(*c, p)
        ctx.move_to(x - r, y - r); ctx.line_to(x + r, y + r); ctx.move_to(x + r, y - r); ctx.line_to(x - r, y + r); ctx.stroke()
    ctx.restore()

def meter(ctx, x, y, w, h, frac, txt, val, col, p, glow=0.0):
    """barra horizontal con su etiqueta a la izquierda y el valor a la derecha"""
    if p <= 0: return
    ctx.save(); ctx.translate(x, y)
    ctx.set_source_rgba(0.08, 0.09, 0.13, 0.88 * p); rr(ctx, -20, -h / 2 - 14, w + 40, h + 28, 18); ctx.fill()
    if glow > 0:
        ctx.set_line_width(6); ctx.set_source_rgba(*col, glow * p); rr(ctx, -20, -h / 2 - 14, w + 40, h + 28, 18); ctx.stroke()
    ctx.select_font_face("Poppins", 0, 1); ctx.set_font_size(h * 0.8)
    ctx.set_source_rgba(*col, p); ctx.move_to(4, h * 0.28); ctx.text_path(txt); ctx.fill()
    bx = h * 1.15; bw = w - bx - h * 2.3
    ctx.set_source_rgba(1, 1, 1, 0.15 * p); rr(ctx, bx, -h / 3, bw, 2 * h / 3, h / 3); ctx.fill()
    if frac > 0.01:
        ctx.set_source_rgba(*col, p); rr(ctx, bx, -h / 3, max(2 * h / 3, bw * frac), 2 * h / 3, h / 3); ctx.fill()
    ctx.set_source_rgba(1, 1, 1, p); e = ctx.text_extents(val); ctx.move_to(w - e.x_advance - 4, h * 0.28); ctx.text_path(val); ctx.fill()
    ctx.restore()

def vbar(ctx, x, y, h, frac, txt, val, col, p):
    if p <= 0: return
    ctx.save(); ctx.translate(x, y)
    ctx.set_source_rgba(0.08, 0.09, 0.13, 0.88 * p); rr(ctx, -95, -h - 70, 190, h + 160, 22); ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.15 * p); rr(ctx, -32, -h, 64, h, 18); ctx.fill()
    fh = max(36, h * frac); ctx.set_source_rgba(*col, p); rr(ctx, -32, -fh, 64, fh, 18); ctx.fill()
    ctx.select_font_face("Poppins", 0, 1); ctx.set_font_size(46)
    e = ctx.text_extents(val); ctx.set_source_rgba(1, 1, 1, p); ctx.move_to(-e.x_advance / 2, -h - 18); ctx.text_path(val); ctx.fill()
    ctx.set_font_size(34); e = ctx.text_extents(txt); ctx.set_source_rgba(*col, p); ctx.move_to(-e.x_advance / 2, 62); ctx.text_path(txt); ctx.fill()
    ctx.restore()

def overlay(ctx, t, A, C):
    Y, R, G, B = C.YL, C.RED, C.GREEN, (0.45, 0.75, 1.0)
    BY = H * 0.265
    # suelo
    p = win(t, T("cómo sabe") + 0.4, T("dentro hay"))
    if p:
        x, y = A("grav_tip"); C.callout(ctx, "?", clampx(x + 120), clampy(y, 500, 1450), p, size=120)
    label(C, ctx, t, T("más pequeño") + 0.5, T("vamos a abrirlo"), "CHIP", A, "chip", dx=-60, dy=-190, size=66)
    label(C, ctx, t, T("grano") + 0.3, T("vamos a abrirlo"), "ARROZ", A, "rice", dx=40, dy=190, size=62)
    label(C, ctx, t, T("dentro hay", 2) + 0.5, T("está colgado"), "MASA", A, "mass", dx=0, dy=0, size=70)
    label(C, ctx, t, T("está colgado") + 0.4, T("y tiene dedos"), "MUELLES", A, "spring", dx=0, dy=-40, size=60)
    label(C, ctx, t, T("pegados") - 0.1, T("cuando sujetas") + 0.3, "ANCLADOS", A, "wall", dx=170, dy=-330, size=56)
    # móvil de pie
    p = win(t, T("cuando sujetas"), T("los muelles ceden"))
    if p:
        phone_icon(ctx, 880, 700, p)
        down_arrow(ctx, 880, 840, 980, win(t, T("la gravedad tira"), T("los muelles ceden")), Y)
    # nanómetros y virus
    a0 = T("el bloque se mueve") + 0.6; a1 = T("cuanto más")
    if a0 <= t < a1:
        C.badge(ctx, "< 10 NM", W / 2, BY, win(t, a0, a1), Y, size=86)
    a0 = T("mucho menos")
    if a0 <= t < a1:
        C.badge(ctx, "VIRUS ≈ 100 NM", W / 2, BY + 140, win(t, a0 + 0.2, a1), G, size=70)
    # carga en los huecos
    a0 = T("más carga"); a1 = T("y lo hace")
    if a0 - 0.2 <= t < a1:
        pa, pb = cargas(t); p = win(t, a0 - 0.2, a1)
        vbar(ctx, 330, 1420, 210, pb / 100, "ABAJO", f"{round(pb)} %", (1.0, 0.45, 0.32), p)
        vbar(ctx, 700, 1420, 210, pa / 100, "ARRIBA", f"{round(pa)} %", (0.4, 0.62, 1.0), p)
    a0 = T("el chip mide")
    if a0 <= t < T("y sabe cuánto"):
        pa, pb = cargas(t); C.badge(ctx, f"DIFERENCIA {round(pb - pa)} %", W / 2, BY, win(t, a0, T("y sabe cuánto")), Y, size=72)
    a0 = T("y sabe cuánto")
    if a0 <= t < T("y lo hace"):
        v = sg(t, a0 + 0.3, T("gravedad", 2, fin=True))
        C.badge(ctx, f"GRAVEDAD {coma(v)} g", W / 2, BY, win(t, a0, T("y lo hace")), Y, size=74)
    # ejes
    for key, txt, col, tt in (("ax_y", "Y", (0.3, 0.88, 0.45), T("arriba y")), ("ax_x", "X", (0.95, 0.3, 0.28), T("a los lados")),
                              ("ax_z", "Z", (0.3, 0.6, 1.0), T("y delante"))):
        p = win(t, tt, T("el móvil lo lee") + 0.5)
        if p:
            x, y = A(key); C.callout(ctx, txt, clampx(x, 120), clampy(y, 480, 1480), p, size=84)
    p = win(t, T("la gravedad ya") + 0.6, T("ahora tira") + 0.3)
    if p:
        x, y = A("ax_y"); cross(ctx, clampx(x, 150), clampy(y + 90, 480, 1480), 34, p)
    # medidores Y / X
    a0 = T("ahora tira") + 0.6; a1 = T("con ese mismo")
    if a0 <= t < a1:
        p = win(t, a0, a1)
        vy = 1 - sg(t, T("el primer número") + 0.6, T("cero", fin=True))
        vx = sg(t, T("el del lado") + 0.5, T("cero a uno", fin=True))
        glow = 0.5 + 0.5 * math.sin(t * 10) if T("cuando gana") <= t < T("gira la pantalla") + 0.6 else 0.0
        meter(ctx, 190, 1300, 700, 80, vy, "Y", coma(vy), (0.3, 0.88, 0.45), p)
        meter(ctx, 190, 1430, 700, 80, vx, "X", coma(vx), (0.95, 0.3, 0.28), p, glow)
    a0 = T("el móvil lo lee")
    if a0 <= t < T("con ese mismo"):
        n = int(max(0, t - a0 - 0.2) * 200)
        C.badge(ctx, f"LECTURAS {n:,}".replace(",", "."), W / 2, BY, win(t, a0, T("con ese mismo")), B, size=72)
    a0 = T("cuenta tus")
    if a0 - 0.4 <= t:
        w0 = T("con ese mismo") + 0.6; n = int(max(0, t - w0) / 0.55 + 0.5)
        C.badge(ctx, f"PASOS {n}", W / 2, BY, win(t, a0 - 0.4, DUR + 1), G, size=80)

def sfx_events(C):
    E = [(0.0, C.s_whoosh(), 0.45), (1.9, C.s_pop(), 0.35), (T("cómo sabe") - 0.1, C.s_whoosh(), 0.35), (T("cómo sabe") + 0.5, C.s_pop(), 0.3),
         (T("dentro hay"), C.s_whoosh(), 0.4), (T("grano"), C.s_pop(), 0.4), (T("vamos a abrirlo") + 0.1, C.s_whoosh(), 0.45),
         (T("dentro hay", 2) + 0.5, C.s_pop(), 0.35), (T("está colgado") + 0.5, C.s_clank(), 0.3), (T("y tiene dedos"), C.s_pop(), 0.35),
         (T("entre sus dedos") + 0.2, C.s_pop(), 0.35), (T("la gravedad tira") + 0.5, C.s_thud(), 0.45), (T("sus dedos se"), C.s_whoosh(), 0.3),
         (T("y aquí viene"), C.s_whoosh(), 0.4), (T("el bloque se mueve") + 0.1, C.s_thud(), 0.35), (T("mucho menos"), C.s_pop(), 0.4),
         (T("pero entre"), C.s_buzz(0.8), 0.3), (T("más carga"), C.s_bleep(1300), 0.3), (T("y sabe cuánto"), C.s_coin(), 0.35),
         (T("y lo hace"), C.s_whoosh(), 0.4), (T("arriba y"), C.s_pop(), 0.35), (T("a los lados"), C.s_pop(), 0.35), (T("y delante"), C.s_pop(), 0.35),
         (T("si tumbas"), C.s_whoosh(), 0.4), (T("la gravedad ya") + 0.6, C.s_fail(), 0.3), (T("ahora tira"), C.s_thud(), 0.35),
         (T("el primer número") + 0.6, C.s_bleep(900), 0.3), (T("el del lado") + 0.5, C.s_bleep(1500), 0.3),
         (T("gira la pantalla"), C.s_win(), 0.4), (T("con ese mismo"), C.s_whoosh(), 0.35), (T("sígueme"), C.s_whoosh(), 0.4)]
    w0 = T("con ese mismo") + 0.6; k = 1
    while w0 + k * 0.55 < DUR: E.append((w0 + k * 0.55 - 0.28, C.s_thud(), 0.18)); k += 1
    return E
