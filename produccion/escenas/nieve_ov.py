# Capa 2D de «¿Y si tuvieras que fabricar la nieve?»
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("nieve")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"esquí", "nevado", "pistas", "blancas", "nieve", "agua", "balsa", "montaña", "verano", "lluvia", "río", "tuberías",
            "cañón", "hielo", "gotas", "finísimas", "aire", "presión", "pulveriza", "expande", "enfría", "núcleos", "congelan",
            "húmedo", "grados", "cero", "seco", "evapora", "calor", "madrugada", "frío", "centenar", "cañones", "máquinas",
            "cadenas", "aplastan", "invierno"}

def ss(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def keyed(t, keys):
    if t <= keys[0][0]: return keys[0][1]
    for (a, va), (b, vb) in zip(keys, keys[1:]):
        if a <= t <= b: return va + (vb - va) * ss((t - a) / max(b - a, 1e-4))
    return keys[-1][1]

def meter(ctx, C, cx, cy, frac, col, p, label, w=600):
    """barra horizontal con relleno (depósito de agua, humedad...)"""
    if p <= 0: return
    import cairo
    x0 = cx - w / 2; h = 64
    ctx.save(); ctx.translate(cx, cy); s = C.back(p); ctx.scale(s, s); ctx.translate(-cx, -cy)
    C.rrect(ctx, x0 - 10, cy - h / 2 - 10, w + 20, h + 20, 18); ctx.set_source_rgba(0.13, 0.15, 0.19, 0.92); ctx.fill()
    C.rrect(ctx, x0, cy - h / 2, w, h, 12); ctx.set_source_rgba(1, 1, 1, 0.12); ctx.fill()
    if frac > 0.005:
        C.rrect(ctx, x0, cy - h / 2, max(24, w * frac), h, 12); ctx.set_source_rgb(*col); ctx.fill()
    ctx.select_font_face("Poppins", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); ctx.set_font_size(44)
    e = ctx.text_extents(label); ctx.move_to(cx - e.x_advance / 2, cy + 16); ctx.set_source_rgb(1, 1, 1); ctx.text_path(label)
    ctx.set_line_width(5); ctx.set_source_rgb(0, 0, 0); ctx.stroke_preserve(); ctx.set_source_rgb(1, 1, 1); ctx.fill()
    ctx.restore()

def overlay(ctx, t, A, C):
    Y, R, G, B = C.YL, C.RED, C.GREEN, (0.45, 0.8, 1.0)
    Yb = H * 0.31
    def badge(C, ctx, t, a, b, text, col, size=70):
        p = win(t, a, b)
        if p: C.badge(ctx, text, W / 2, Yb, p, col, size=size)
    # apertura: nieve natural 0 cm, la pista se pone blanca
    a0, a1 = T("aún no") - 0.1, T("y si tuvieras")
    if a0 <= t < a1:
        C.badge(ctx, "NIEVE DEL CIELO: 0 CM", W / 2, Yb, win(t, a0, a1), (1, 1, 1), size=62)
    a0 = T("y las pistas")
    if a0 <= t < T("y si tuvieras"):
        v = keyed(t, [(a0, 0), (T("blancas", fin=True), 40)])
        C.badge(ctx, f"PISTA: {int(round(v))} CM", W / 2, Yb + 125, win(t, a0, T("y si tuvieras")), B, size=66)
    # agua: depósito vacío → balsa llena
    a0, a1 = T("primero") + 0.3, T("debajo") + 0.3
    if a0 <= t < a1:
        f = keyed(t, [(T("y la llenas"), 0), (T("río") + 0.7, 1.0)])
        col = R if f < 0.05 else B
        blink = 1.0 if f > 0.05 or int(t * 3) % 2 == 0 else 0.55
        meter(ctx, C, W / 2, Yb, f, col, win(t, a0, a1) * blink, f"AGUA {int(round(100 * f))} %")
    label(C, ctx, t, T("balsa"), T("debajo"), "BALSA", A, "balsa", dx=60, dy=-170, size=64)
    if T("verano") - 0.1 <= t < T("debajo"):
        C.badge(ctx, "VERANO", W / 2, Yb + 120, win(t, T("verano") - 0.1, T("debajo")), Y, size=64)
    label(C, ctx, t, T("río"), T("debajo"), "RÍO", A, "rio", dx=0, dy=-120, size=60)
    label(C, ctx, t, T("tuberías") - 0.1, T("pero si lanzas"), "TUBERÍA", A, "tubo", dx=0, dy=160, size=62)
    label(C, ctx, t, T("cada cañón") - 0.2, T("pero si lanzas"), "CAÑÓN", A, "hidr", dx=0, dy=-160, size=62)
    # agua a chorro → lluvia → hielo
    label(C, ctx, t, T("cae como") , T("y se congela"), "GOTAS GORDAS", A, "lluvia", dx=0, dy=-200, size=56)
    label(C, ctx, t, T("y se congela") + 0.3, T("así que la rompes") + 0.3, "HIELO", A, "hielo", dx=0, dy=-150, size=66)
    badge(C, ctx, t, T("hielo duro"), T("así que la rompes"), "✗ NO ES NIEVE", R, size=72)
    badge(C, ctx, t, T("finísimas") - 0.1, T("en el cañón"), "✓ GOTAS FINAS", G, size=72)
    # boquilla
    label(C, ctx, t, T("el agua sale"), T("y aquí"), "AGUA", A, "dagua", dx=0, dy=130, size=60)
    label(C, ctx, t, T("aire a presión") - 0.1, T("y aquí"), "AIRE", A, "daire", dx=0, dy=-130, size=60)
    a0, a1 = T("aire a presión") - 0.1, T("al salir")
    if a0 <= t < a1:
        v = keyed(t, [(a0 + 0.1, 0), (a0 + 0.9, 100)])
        meter(ctx, C, W / 2, Yb, v / 100, Y, win(t, a0, a1), "PRESIÓN DEL AIRE", w=640)
    # expansión: el aire se enfría
    a0, a1 = T("se expande"), T("las gotas se")
    if a0 <= t < a1:
        v = keyed(t, [(T("se expande"), 0.85), (T("se enfría") - 0.3, 0.6), (T("se enfría", fin=True) + 0.2, 0.12)])
        col = tuple(r + (b - r) * (1 - v) for r, b in zip((1.0, 0.55, 0.3), B))
        meter(ctx, C, W / 2, Yb, v, col, win(t, a0, a1), "TEMPERATURA DEL AIRE", w=640)
    label(C, ctx, t, T("se expande"), T("así crea"), "EXPANSIÓN", A, "puff", dx=-40, dy=260, size=58)
    label(C, ctx, t, T("núcleos") - 0.1, T("las gotas se"), "NÚCLEOS", A, "nuc", dx=0, dy=-150, size=62)
    # la gota que se congela al caer
    a0, a1 = T("las gotas se"), T("pero no vale")
    if a0 <= t < a1:
        v = keyed(t, [(a0, 2.0), (T("se congelan"), 0.0)])
        fr = ss((t - T("se congelan")) / max(T("caen", fin=True) - T("se congelan"), 0.1))
        s = f"GOTA {v:+.0f} °C" if fr < 0.5 else "GOTA 0 °C · HIELO"
        C.badge(ctx, s.replace("+0", "0"), W / 2, Yb, win(t, a0, a1), B if fr < 0.5 else (1, 1, 1), size=72)
    # humedad y temperatura
    a0, a1 = T("si el aire"), T("por eso")
    if a0 <= t < a1:
        p = win(t, a0, a1)
        hum = keyed(t, [(T("si está muy seco"), 90), (T("muy seco", fin=True) + 0.3, 30)])
        tem = keyed(t, [(T("necesitas varios") - 0.2, 0), (T("bajo cero", fin=True), -4), (T("y puedes"), -4), (T("cero grados", fin=True), -1)])
        meter(ctx, C, W / 2, Yb, hum / 100, B, p, f"HUMEDAD {int(round(hum))} %", w=640)
        tc = (1, 1, 1) if tem > -0.5 else (0.55, 0.85, 1.0)
        C.badge(ctx, f"{int(round(tem))} °C", W / 2 - 150, Yb + 130, p, tc, size=74)
        ok = tem <= -3.0 or (hum < 60 and t > T("roba calor"))
        if t > T("necesitas varios"):
            C.badge(ctx, "✓ NIEVE" if ok else "✗ LLUVIA", W / 2 + 140, Yb + 130, p, G if ok else R, size=66)
    label(C, ctx, t, T("se evapora"), T("y puedes"), "VAPOR", A, "canon", dx=-120, dy=-140, size=60)
    # madrugada
    a0, a1 = T("por eso"), T("una gran")
    if a0 <= t < a1:
        hh = keyed(t, [(a0, 22.0), (T("cuando más") + 0.3, 29.0)])
        h = int(hh) % 24; m = int((hh - int(hh)) * 60) // 10 * 10
        tem = keyed(t, [(a0, -1), (T("cuando más") + 0.3, -7)])
        C.badge(ctx, f"{h:02d}:{m:02d}", W / 2 - 130, Yb, win(t, a0, a1), (1, 1, 1), size=80)
        C.badge(ctx, f"{int(round(tem))} °C", W / 2 + 150, Yb, win(t, a0, a1), (0.55, 0.85, 1.0), size=80)
    # centenar de cañones
    a0, a1 = T("una gran"), T("y luego")
    if a0 <= t < a1:
        v = keyed(t, [(a0 + 0.2, 0), (T("centenar", fin=True), 100)])
        C.badge(ctx, f"{int(round(v))} CAÑONES", W / 2, Yb, win(t, a0, a1), Y, size=80)
    # pisapistas y temporada
    label(C, ctx, t, T("cadenas") - 0.1, T("para que"), "CADENAS", A, "pisa", dx=0, dy=-170, size=60)
    a0, a1 = T("para que"), DUR + 1
    if a0 <= t < a1:
        meses = ["DIC", "ENE", "FEB", "MAR", "ABR"]
        k = int(keyed(t, [(a0 + 0.1, 0), (T("invierno", fin=True), 4.0)]) + 0.01)
        C.badge(ctx, " · ".join(meses[:k + 1]), W / 2, Yb, win(t, a0, a1), (1, 1, 1), size=60)

def sfx_events(C):
    E = [(0.0, C.s_whoosh(), 0.45), (0.05, C.s_buzz(6.2), 0.25)]
    E += [(T("aún no"), C.s_fail(), 0.3), (T("y las pistas"), C.s_whoosh(), 0.35), (T("blancas"), C.s_coin(), 0.4),
          (T("vamos a hacerla"), C.s_whoosh(), 0.45), (T("necesitas agua"), C.s_fail(), 0.35), (T("balsa"), C.s_thud(), 0.5),
          (T("y la llenas"), C.s_whoosh(), 0.35), (T("río", fin=True), C.s_coin(), 0.4), (T("tuberías"), C.s_clank(), 0.4),
          (T("cada cañón"), C.s_pop(), 0.45), (T("pero si lanzas"), C.s_buzz(1.8), 0.25), (T("hielo duro"), C.s_fail(), 0.4),
          (T("finísimas"), C.s_win(), 0.35), (T("en el cañón"), C.s_whoosh(), 0.45), (T("aire a presión"), C.s_buzz(1.2), 0.3),
          (T("pulveriza"), C.s_pop(), 0.4), (T("se expande"), C.s_whoosh(), 0.45), (T("se enfría"), C.s_coin(), 0.4),
          (T("núcleos"), C.s_pop(), 0.4), (T("se congelan"), C.s_pop(), 0.4), (T("caen", fin=True), C.s_win(), 0.35),
          (T("pero no vale"), C.s_whoosh(), 0.4), (T("bajo cero"), C.s_coin(), 0.4), (T("muy seco"), C.s_whoosh(), 0.35),
          (T("cero grados"), C.s_win(), 0.35), (T("madrugada"), C.s_whoosh(), 0.4), (T("centenar"), C.s_coin(), 0.45),
          (T("unas máquinas"), C.s_clank(), 0.4), (T("aplastan"), C.s_thud(), 0.5), (T("invierno"), C.s_win(), 0.35),
          (T("sígueme"), C.s_whoosh(), 0.4)]
    return E
