# Capa 2D de «Así funciona el vaho de la ventana»
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("ventana")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"ventana", "empañada", "fuera", "aire", "habitación", "agua", "invisible", "vapor", "respirar", "ducharte", "cocinar",
            "temperatura", "metro", "cúbico", "veinte", "diecisiete", "gramos", "diez", "nueve", "frío", "cristal", "golpe", "gotitas",
            "vaho", "punto", "rocío", "empaña", "gordo", "dos", "cristales", "doble", "acristalamiento", "cámara", "gas", "calor",
            "cuarto", "minutos", "húmedo", "seco"}
B = (0.45, 0.75, 1.0); ORA = (1.0, 0.6, 0.25)

def ss(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def keyed(t, keys):
    if t <= keys[0][0]: return keys[0][1]
    for (a, va), (b, vb) in zip(keys, keys[1:]):
        if a <= t <= b: return va + (vb - va) * ss((t - a) / max(b - a, 1e-4))
    return keys[-1][1]
def tglass(t):
    return keyed(t, [(0, 20.0), (T("el cristal se") - 0.1, 20.0), (T("calle") + 0.3, 10.0), (T("así que el de dentro") + 0.3, 10.0), (T("cuarto", fin=True), 16.0)])
def tcol(v):
    u = max(0, min(1, (v - 8) / 12)); return tuple(b + (o - b) * u for b, o in zip(B, ORA))

def panel(ctx, C, x, y, w, h, p):
    C.rrect(ctx, x, y, w, h, 24); ctx.set_source_rgba(0.06, 0.08, 0.14, 0.88 * min(1, p * 1.5)); ctx.fill()

def vapor_meter(ctx, C, t, p, content, cap, cx=130, y0=640, h=520):
    """columna de vapor en 1 m³: lo que lleva (relleno) y lo que aguanta (línea), escala 0-25 g"""
    if p <= 0: return
    ctx.save(); s = C.back(p); ctx.translate(cx, y0 + h / 2); ctx.scale(s, s); ctx.translate(0, -h / 2)
    w = 80
    panel(ctx, C, -w / 2 - 16, -70, w + 32, h + 100, 1)
    C.rrect(ctx, -w / 2, 0, w, h, 12); ctx.set_source_rgba(0.2, 0.24, 0.32, 1); ctx.fill()
    hc = h * content / 25; hm = h * cap / 25
    keep = min(hc, hm)
    if keep > 2: C.rrect(ctx, -w / 2, h - keep, w, keep, 12); ctx.set_source_rgb(*B); ctx.fill()
    if hc > hm + 2: ctx.rectangle(-w / 2, h - hc, w, hc - hm); ctx.set_source_rgb(1, 1, 1); ctx.fill()
    if cap < 25: ctx.set_source_rgb(*C.YL); ctx.set_line_width(7); ctx.set_dash([14, 8]); ctx.move_to(-w / 2 - 16, h - hm); ctx.line_to(w / 2 + 16, h - hm); ctx.stroke(); ctx.set_dash([])
    C.text_path(ctx, "VAPOR", 30); e = ctx.text_extents("VAPOR"); ctx.move_to(-e.x_advance / 2, -24); ctx.text_path("VAPOR"); ctx.set_source_rgb(1, 1, 1); ctx.fill()
    ctx.restore()
    if p > 0.5 and cap < 25:
        txt = f"{int(round(cap))} g"
        C.outlined(ctx, txt, cx + 140, y0 + h - h * cap / 25, 58, fill=C.YL, stroke=10, alpha=min(1, (p - 0.5) * 2))

def thermo(ctx, C, t, cx, cy, v, p, name, rocio=False, h=380):
    """termómetro vertical de 0 a 25 °C con el valor y, si se pide, la línea del punto de rocío (12 °C)"""
    if p <= 0: return
    ctx.save(); s = C.back(p); ctx.translate(cx, cy); ctx.scale(s, s)
    panel(ctx, C, -95, -h / 2 - 90, 190, h + 200, 1)
    ctx.set_source_rgb(0.22, 0.25, 0.33); C.rrect(ctx, -18, -h / 2, 36, h, 18); ctx.fill(); ctx.arc(0, h / 2 + 18, 32, 0, 7); ctx.fill()
    col = tcol(v); fh = h * max(0, min(1, v / 25))
    ctx.set_source_rgb(*col); C.rrect(ctx, -10, h / 2 - fh, 20, fh + 10, 10); ctx.fill(); ctx.arc(0, h / 2 + 18, 24, 0, 7); ctx.fill()
    if rocio:
        yr = h / 2 - h * 12 / 25
        ctx.set_source_rgb(1, 1, 1); ctx.set_line_width(5); ctx.set_dash([10, 7]); ctx.move_to(-60, yr); ctx.line_to(60, yr); ctx.stroke(); ctx.set_dash([])
    txt = f"{int(round(v))} °C"; C.text_path(ctx, txt, 44); e = ctx.text_extents(txt)
    ctx.move_to(-e.x_advance / 2, -h / 2 - 32); ctx.text_path(txt); ctx.set_source_rgb(*col); ctx.fill()
    C.text_path(ctx, name, 28); e = ctx.text_extents(name)
    ctx.move_to(-e.x_advance / 2, h / 2 + 88); ctx.text_path(name); ctx.set_source_rgb(1, 1, 1); ctx.fill()
    ctx.restore()
    if rocio and p > 0.5:
        C.outlined(ctx, "ROCÍO", cx + 165, cy + h / 2 - h * 12 / 25, 40, fill=(1, 1, 1), stroke=8, alpha=min(1, (p - 0.5) * 2))

def overlay(ctx, t, A, C):
    Y, R, G = C.YL, C.RED, C.GREEN
    Yb = H * 0.265
    label(C, ctx, t, T("pero ese") + 0.6, T("el aire de"), "SECO", A, "fuera", dx=110, dy=-60, size=62)
    label(C, ctx, t, T("mira") , T("el aire de"), "MOJADO", A, "dentro", dx=-150, dy=60, size=58)
    label(C, ctx, t, T("vapor") - 0.1, T("y lo vas"), "VAPOR", A, "cubo_c", dx=0, dy=-60, size=64)
    # contenido y capacidad del metro cúbico
    t_v0, t_v1 = T("y lo vas"), T("y de noche") + 0.2
    if t_v0 <= t < t_v1:
        content = keyed(t, [(t_v0, 6), (T("respirar"), 6), (T("cocinar", fin=True) + 1.2, 12), (T("a diez") + 0.6, 12), (T("nueve", fin=True) + 0.4, 9)])
        cap = keyed(t, [(0, 17), (T("a diez") - 0.1, 17), (T("grados", 2, fin=True), 9)])
        p_cap = win(t, T("diecisiete") - 0.3, t_v1)
        vapor_meter(ctx, C, t, win(t, t_v0, t_v1), content, cap if p_cap > 0 else 25.5)
    a0, a1 = T("un metro"), T("y de noche") + 0.2
    if a0 <= t < a1:
        label(C, ctx, t, a0, a1, "1 m³", A, "cubo", dx=150, dy=-70, size=66)
        v = keyed(t, [(0, 20), (T("a diez") - 0.1, 20), (T("grados", 2, fin=True), 10)])
        if t > T("veinte") - 0.2:
            C.badge(ctx, f"AIRE {int(round(v))} °C", W / 2, Yb, win(t, T("veinte") - 0.2, a1), tcol(v), size=72)
    # noche: el cristal se enfría
    label(C, ctx, t, T("fuera hace") - 0.1, T("así que el aire"), "CALLE", A, "calle", dx=-40, dy=0, size=62)
    a0, a1 = T("el cristal se") - 0.2, T("curioso")
    if a0 <= t < a1:
        thermo(ctx, C, t, 175, 900, 20, win(t, a0, a1), "AIRE")
        thermo(ctx, C, t, 905 - 140 + 40, 900, tglass(t), win(t, a0, a1), "CRISTAL", rocio=t > T("rocío") - 0.4)
    label(C, ctx, t, T("vapor", 3) - 0.3, T("eso es"), "MÁX 9 g", A, "burb", dx=0, dy=-170, size=58)
    label(C, ctx, t, T("eso es") - 0.1, T("a esa"), "VAHO", A, "cristal", dx=-120, dy=-40, size=66)
    a0, a1 = T("se empaña") - 0.1, T("curioso")
    # cristal más gordo: sigue frío
    a0, a1 = T("gordo") - 0.3, T("es meter")
    if a0 <= t < a1: C.badge(ctx, "✗ 10 °C", W / 2, Yb, win(t, a0, a1), R, size=80)
    # doble acristalamiento
    a0, a1 = T("doble") - 0.2, T("y si aun")
    if a0 <= t < a1:
        p = win(t, a0, a1)
        thermo(ctx, C, t, 175, 950, tglass(t), p, "DENTRO", rocio=True)
        vo = keyed(t, [(a0, 10), (T("se enfría", 3) + 0.3, 4)])
        thermo(ctx, C, t, 805, 950, vo, p, "FUERA")
    label(C, ctx, t, T("cámara") - 0.1, T("así que el de dentro"), "GAS", A, "gas", dx=0, dy=160, size=60)
    label(C, ctx, t, T("apenas") + 0.2, T("así que el de dentro"), "CALOR", A, "base", dx=-260, dy=-260, size=60)
    p = win(t, T("por eso", 1) - 0.2, T("y si aun"))
    if p: C.badge(ctx, "✓ SIN VAHO", W / 2, Yb, p, G, size=78)
    # ventilar
    a0, a1 = T("abre") - 0.1, DUR + 1
    if a0 <= t < a1:
        v = keyed(t, [(a0, 0), (T("sacas"), 10)])
        C.badge(ctx, f"{int(round(v))} MIN", W / 2, Yb, win(t, a0, a1), Y, size=86)
    label(C, ctx, t, T("húmedo") - 0.1, T("sígueme"), "HÚMEDO", A, "fuera", dx=140, dy=-180, size=56)
    label(C, ctx, t, T("seco") - 0.1, DUR + 1, "SECO", A, "base", dx=60, dy=-60, size=60)

def sfx_events(C):
    E = [(0.0, C.s_buzz(3.0), 0.12), (0.2, C.s_whoosh(), 0.3), (T("pero ese"), C.s_fail(), 0.3), (T("mira"), C.s_whoosh(), 0.4),
         (T("el aire de") + 0.6, C.s_pop(), 0.35), (T("respirar"), C.s_pop(), 0.4), (T("ducharte"), C.s_pop(), 0.4), (T("cocinar"), C.s_pop(), 0.4),
         (T("pero el aire no"), C.s_whoosh(), 0.3), (T("diecisiete"), C.s_coin(), 0.35), (T("nueve"), C.s_fail(), 0.35),
         (T("y de noche"), C.s_whoosh(), 0.4), (T("calle"), C.s_thud(), 0.3), (T("golpe"), C.s_thud(), 0.45)]
    E += [(T("gotitas") + 0.1 * k, C.s_bleep(1800 + 120 * k), 0.15) for k in range(6)]
    E += [(T("eso es"), C.s_pop(), 0.4), (T("rocío"), C.s_coin(), 0.35), (T("se empaña"), C.s_fail(), 0.35),
          (T("curioso"), C.s_whoosh(), 0.4), (T("gordo"), C.s_fail(), 0.35), (T("es meter"), C.s_clank(), 0.4),
          (T("doble"), C.s_whoosh(), 0.35), (T("cámara"), C.s_pop(), 0.4), (T("apenas"), C.s_thud(), 0.3),
          (T("cuarto"), C.s_coin(), 0.35), (T("por eso", 1), C.s_win(), 0.4), (T("y si aun"), C.s_fail(), 0.3),
          (T("abre"), C.s_clank(), 0.4), (T("sacas"), C.s_whoosh(), 0.4), (T("seco"), C.s_win(), 0.35), (T("sígueme"), C.s_whoosh(), 0.4)]
    return E
