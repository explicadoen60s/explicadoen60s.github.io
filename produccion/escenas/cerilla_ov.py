# Capa 2D de «Si tuvieras que inventar la cerilla…»
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("cerilla")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"cerilla", "segundo", "fuego", "calor", "madera", "palos", "minutos", "fósforo", "blanco", "treinta", "grados",
            "bolsillo", "venenoso", "dos", "caja", "marrón", "rojo", "vidrio", "clorato", "potasio", "oxígeno", "azufre",
            "rascar", "calienta", "chispa", "llama", "suspiro", "parafina", "despacio", "mitad", "pared", "sueco", "nada"}

def sg(t, a, b):
    x = max(0.0, min(1.0, (t - a) / (b - a))); return x * x * (3 - 2 * x)
def keyed(t, keys):
    if t <= keys[0][0]: return keys[0][1]
    for (a, va), (b, vb) in zip(keys, keys[1:]):
        if a <= t <= b: return va + (vb - va) * sg(t, a, b)
    return keys[-1][1]

def cross(ctx, x, y, r, p, col=(0.93, 0.2, 0.22)):
    if p <= 0: return
    ctx.save(); ctx.set_line_cap(1)
    for lw, c in ((26, (0, 0, 0)), (15, col)):
        ctx.set_line_width(lw); ctx.set_source_rgba(*c, p)
        ctx.arc(x, y, r, 0, math.tau); ctx.stroke()
        ctx.move_to(x - r * 0.7, y - r * 0.7); ctx.line_to(x + r * 0.7, y + r * 0.7); ctx.stroke()
    ctx.restore()

def skull(ctx, x, y, s, p):
    if p <= 0: return
    ctx.save(); ctx.translate(x, y); sc = 0.5 + 0.5 * ss_(p); ctx.scale(s * sc, s * sc)
    ctx.set_source_rgba(0, 0, 0, 0.6 * p); ctx.arc(0, 0, 1.25, 0, math.tau); ctx.fill()
    ctx.set_source_rgba(0.45, 0.9, 0.35, p)
    ctx.arc(0, -0.15, 0.85, 0, math.tau); ctx.fill()
    ctx.rectangle(-0.5, 0.4, 1.0, 0.55); ctx.fill()
    ctx.set_source_rgba(0.05, 0.08, 0.05, p)
    for dx in (-0.33, 0.33): ctx.arc(dx, -0.15, 0.24, 0, math.tau); ctx.fill()
    ctx.move_to(0, 0.12); ctx.line_to(-0.1, 0.3); ctx.line_to(0.1, 0.3); ctx.close_path(); ctx.fill()
    ctx.set_line_width(0.07)
    for dx in (-0.25, 0, 0.25): ctx.move_to(dx, 0.5); ctx.line_to(dx, 0.92); ctx.stroke()
    ctx.restore()

def ss_(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)

def meter(ctx, label_, v, cx, cy, p, col_a, col_b, w=720):
    """barra horizontal con texto: v 0..1"""
    if p <= 0: return
    ctx.save(); ctx.translate(cx, cy); s = 0.6 + 0.4 * ss_(p); ctx.scale(s, s)
    h = 84
    ctx.set_source_rgba(0.08, 0.09, 0.12, 0.92 * p); C_rr(ctx, -w / 2 - 14, -h / 2 - 14, w + 28, h + 28, 22); ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.15 * p); C_rr(ctx, -w / 2, -h / 2, w, h, 16); ctx.fill()
    if v > 0.01:
        col = tuple(a + (b - a) * v for a, b in zip(col_a, col_b))
        ctx.set_source_rgba(*col, p); C_rr(ctx, -w / 2, -h / 2, max(32, w * v), h, 16); ctx.fill()
    ctx.select_font_face("Poppins", 0, 1); ctx.set_font_size(54); e = ctx.text_extents(label_)
    ctx.move_to(-e.x_advance / 2, 19); ctx.text_path(label_)
    ctx.set_source_rgba(0, 0, 0, p); ctx.set_line_width(7); ctx.stroke_preserve(); ctx.set_source_rgba(1, 1, 1, p); ctx.fill()
    ctx.restore()

def C_rr(ctx, x, y, w, h, r):
    ctx.new_sub_path(); ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0); ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi); ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi); ctx.close_path()

def overlay(ctx, t, A, C):
    Y, R, G, B = C.YL, C.RED, C.GREEN, (0.45, 0.8, 1.0)
    BY = H * 0.265
    # 1) se enciende en menos de un segundo
    if t < T("necesitas"):
        s = 0.8 * sg(t, 0.05, 0.85)
        C.badge(ctx, f"{s:.1f} S".replace(".", ","), W / 2, BY, win(t, 0.0, T("vamos a") + 0.3), Y, size=92)
    # 2) la madera necesita unos 300 °C
    label(C, ctx, t, T("necesitas") + 0.4, T("frotar"), "MADERA", A, "board", dx=40, dy=170, size=60)
    if T("mucho calor") - 0.2 <= t < T("frotar"):
        v = keyed(t, [(T("mucho calor") - 0.2, 20), (T("calor", 2, fin=True), 300)])
        C.badge(ctx, "%d °C" % round(v), W / 2, BY, win(t, T("mucho calor") - 0.2, T("frotar")), R, size=92)
    # 3) frotando: minutos
    if T("frotar") <= t < T("así que buscas"):
        m = 300 * sg(t, T("frotar") + 0.2, T("minutos", fin=True))
        C.badge(ctx, "%d:%02d MIN" % (int(m // 60), int(m % 60)), W / 2, BY, win(t, T("frotar"), T("así que buscas")), R, size=84)
    label(C, ctx, t, T("frotar") + 0.6, T("así que buscas"), "BRASA", A, "ember", dx=-230, dy=40, size=56)
    # 4) fósforo blanco a 30 °C
    label(C, ctx, t, T("el fósforo blanco") + 0.2, T("lo pones"), "FÓSFORO\nBLANCO", A, "lump", dx=-150, dy=-230, size=58)
    if T("el fósforo blanco") <= t < T("lo pones"):
        v = keyed(t, [(T("el fósforo blanco"), 20), (T("treinta"), 24), (T("grados", fin=True), 30)])
        C.badge(ctx, "%d °C" % round(v), W / 2, BY, win(t, T("el fósforo blanco"), T("lo pones")), Y if v < 29.5 else R, size=92)
    # 5) en el bolsillo (cuerpo ~ 33 °C) y venenoso
    if T("bolsillo") - 0.6 <= t < T("y es venenoso"):
        C.badge(ctx, "BOLSILLO: 33 °C", W / 2, BY, win(t, T("bolsillo") - 0.6, T("y es venenoso")), R, size=74)
    if T("y es venenoso") <= t < T("así que separas"):
        p = win(t, T("y es venenoso"), T("así que separas"))
        x, y = A("pocket"); skull(ctx, W / 2, clampy(y - 120, 700, 1150), 120, p)
        C.badge(ctx, "✗ TÓXICO", W / 2, BY, p, R, size=80)
    # 6) la caja: fósforo rojo y vidrio
    label(C, ctx, t, T("fósforo rojo") - 0.1, T("en la cabeza"), "FÓSFORO\nROJO", A, "red", dx=0, dy=230, size=56)
    label(C, ctx, t, T("vidrio") - 0.1, T("en la cabeza"), "VIDRIO", A, "glass", dx=0, dy=230, size=58)
    if T("es mucho más") <= t < T("en la cabeza"):
        v = keyed(t, [(T("es mucho más"), 30), (T("tranquilo", fin=True), 260)])
        C.badge(ctx, "PRENDE A %d °C" % round(v), W / 2, BY, win(t, T("es mucho más"), T("en la cabeza")), G, size=74)
    # 7) la cabeza: clorato + azufre
    label(C, ctx, t, T("clorato de"), T("y aquí viene"), "CLORATO", A, "clor", dx=-200, dy=-150, size=58)
    label(C, ctx, t, T("y azufre"), T("y aquí viene"), "AZUFRE", A, "sulf", dx=200, dy=160, size=58)
    label(C, ctx, t, T("que suelta"), T("y azufre"), "O2", A, "clor", dx=60, dy=-330, size=64)
    # 8) al rascar: calor de roce
    if T("al rascar") <= t < T("esa chispa"):
        v = sg(t, T("al rascar") + 0.2, T("calienta", fin=True))
        C.badge(ctx, "ROCE: %d °C" % round(20 + 30 * v), W / 2, BY, win(t, T("al rascar"), T("esa chispa")), Y if v < 0.95 else R, size=76)
    label(C, ctx, t, T("una pizca") + 0.6, T("esa chispa"), "BLANCO", A, "red", dx=40, dy=220, size=60)
    label(C, ctx, t, T("que da oxígeno") + 0.2, T("fuuu"), "O2", A, "headD", dx=-200, dy=-220, size=66)
    # 9) la llama de la cabeza dura poco
    if T("pero la llama") <= t < T("así que mojas"):
        v = 1 - sg(t, T("suspiro") - 0.4, T("suspiro", fin=True) + 0.1)
        meter(ctx, "CABEZA %d %%" % round(100 * v), v, W / 2, BY, win(t, T("pero la llama"), T("así que mojas")), R, Y)
    label(C, ctx, t, T("parafina") - 0.1, T("que arde despacio") + 0.3, "PARAFINA", A, "parA", dx=0, dy=200, size=60)
    if T("que arde despacio") <= t < T("por eso solo"):
        v = sg(t, T("que arde despacio"), T("madera", 2, fin=True) + 0.4)
        meter(ctx, "MADERA %d %%" % round(100 * v), v, W / 2, BY, win(t, T("que arde despacio"), T("por eso solo")), Y, G)
    # 10) cada mitad sola: nada
    if T("cada mitad") <= t < T("si la rascas"):
        for key, tt in (("headD", T("cada mitad") + 0.2), ("strip", T("sola"))):
            p = win(t, tt, T("si la rascas"))
            if p: x, y = A(key); cross(ctx, clampx(x, 200), clampy(y, 450, 1450), 110, p)
    if T("si la rascas") <= t < T("la inventó"):
        p = win(t, T("no pasa nada") - 0.1, T("la inventó"))
        if p: x, y = A("wallM"); cross(ctx, clampx(x, 200), clampy(y, 450, 1450), 110, p)
        label(C, ctx, t, T("si la rascas") + 0.2, T("la inventó"), "PARED", A, "wall", dx=0, dy=0, size=64)
    # 11) 1844
    if T("la inventó") <= t < DUR + 1:
        yr = int(round(keyed(t, [(T("mil"), 1800), (T("cuatro", fin=True), 1844)])))
        C.badge(ctx, str(yr), W / 2, BY, win(t, T("la inventó"), DUR + 1), Y, size=100)

def sfx_events(C):
    E = [(0.0, C.s_whoosh(0.45), 0.5), (0.75, C.s_pop(), 0.5), (0.85, C.s_buzz(0.6), 0.25), (T("vamos a"), C.s_whoosh(), 0.35),
         (T("necesitas"), C.s_whoosh(), 0.35), (T("calor", 2, fin=True), C.s_pop(), 0.4), (T("minutos"), C.s_fail(), 0.35),
         (T("así que buscas"), C.s_whoosh(), 0.35), (T("grados", fin=True), C.s_pop(), 0.5), (T("lo pones"), C.s_whoosh(), 0.3),
         (T("y listo"), C.s_win(), 0.3), (T("bolsillo"), C.s_pop(), 0.45), (T("y es venenoso"), C.s_fail(), 0.4),
         (T("así que separas"), C.s_whoosh(), 0.4), (T("fósforo rojo"), C.s_pop(), 0.35), (T("vidrio"), C.s_pop(), 0.35),
         (T("clorato de"), C.s_pop(), 0.35), (T("y azufre"), C.s_pop(), 0.35), (T("y aquí viene"), C.s_whoosh(), 0.4),
         (T("al rascar"), C.s_whoosh(0.8), 0.45), (T("y prende"), C.s_pop(), 0.5), (T("que da oxígeno"), C.s_whoosh(), 0.3),
         (T("fuuu"), C.s_buzz(0.9), 0.4), (T("llama"), C.s_win(), 0.35), (T("suspiro"), C.s_fail(), 0.3),
         (T("parafina"), C.s_pop(), 0.35), (T("que arde despacio"), C.s_whoosh(), 0.3), (T("cada mitad"), C.s_fail(), 0.35),
         (T("sola"), C.s_fail(), 0.35), (T("si la rascas"), C.s_whoosh(0.4), 0.35), (T("no pasa nada"), C.s_fail(), 0.35),
         (T("cuatro", fin=True), C.s_coin(), 0.4), (T("sígueme"), C.s_whoosh(), 0.4)]
    return E
