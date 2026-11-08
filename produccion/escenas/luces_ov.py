# Capa 2D de «Así funcionan las luces de Navidad»
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("luces")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"luces", "navidad", "bombilla", "fundida", "guirnalda", "fila", "serie", "corriente", "primera", "última", "camino",
            "apagan", "truco", "alambre", "filamento", "derivación", "aislado", "tensión", "hueco", "aislante", "quema", "suelda",
            "encendidas", "salta", "repartir", "brillan", "funden", "avería", "noventa", "nueve", "cincuenta", "seis", "diez",
            "ciento", "dos", "cambiar", "enseguida"}

def ss(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def keyed(t, keys):
    if t <= keys[0][0]: return keys[0][1]
    for (a, va), (b, vb) in zip(keys, keys[1:]):
        if a <= t <= b: return va + (vb - va) * ss((t - a) / max(b - a, 1e-4))
    return keys[-1][1]
def num(v, d=1):
    return f"{v:.{d}f}".replace(".", ",")

def voltimetro(ctx, C, t, A, v, p):
    if p <= 0: return
    cx, cy, w, h = 225, 1370, 300, 180
    # puntas de prueba hasta las patillas de la bombilla
    for key, col, dx in (("postL", (0.95, 0.25, 0.25), -70), ("postR", (0.15, 0.15, 0.15), 70)):
        x1, y1 = A(key)
        ctx.set_line_width(7); ctx.set_source_rgba(*col, p); ctx.move_to(cx + dx, cy - h / 2)
        ctx.curve_to(cx + dx, cy - h / 2 - 120, x1, y1 + 160, x1, y1); ctx.stroke()
        ctx.arc(x1, y1, 11, 0, 7); ctx.fill()
    ctx.save(); ctx.translate(cx, cy); s = C.back(p); ctx.scale(s, s)
    C.rrect(ctx, -w / 2, -h / 2, w, h, 26); ctx.set_source_rgba(0.95, 0.75, 0.15, 1); ctx.fill()
    C.rrect(ctx, -w / 2 + 16, -h / 2 + 16, w - 32, h - 32, 16); ctx.set_source_rgba(0.08, 0.1, 0.12, 1); ctx.fill()
    # arco 0-230 V con aguja
    r = 60; ox, oy = -68, 36
    ctx.set_line_width(10); ctx.set_source_rgba(0.35, 0.38, 0.45, 1); ctx.arc(ox, oy, r, math.pi, 2 * math.pi); ctx.stroke()
    f = max(0, min(1, v / 230)); ctx.set_source_rgba(1.0, 0.3 + 0.6 * (1 - f), 0.2, 1)
    ctx.arc(ox, oy, r, math.pi, math.pi + math.pi * max(f, 0.01)); ctx.stroke()
    a = math.pi + math.pi * f; ctx.set_line_width(6); ctx.set_source_rgb(1, 1, 1)
    ctx.move_to(ox, oy); ctx.line_to(ox + (r - 8) * math.cos(a), oy + (r - 8) * math.sin(a)); ctx.stroke()
    txt = f"{num(v) if v < 20 else int(round(v))} V"
    C.text_path(ctx, txt, 56); e = ctx.text_extents(txt)
    ctx.move_to(62 - e.x_advance / 2, 22); ctx.text_path(txt); ctx.set_source_rgb(1, 0.9 if v < 20 else 0.35, 0.3 if v < 20 else 0.3); ctx.fill()
    ctx.restore()

def overlay(ctx, t, A, C):
    Y, R, G, B = C.YL, C.RED, C.GREEN, (0.45, 0.75, 1.0)
    Yb = H * 0.265
    label(C, ctx, t, T("fundida") - 0.1, T("mira por"), "FUNDIDA", A, "hero", dx=0, dy=-170, size=64)
    label(C, ctx, t, T("la corriente entra") - 0.1, T("si se rompe"), "230 V", A, "enchufe", dx=40, dy=-150, size=66)
    a0, a1 = T("en serie"), T("así que dentro")
    if a0 <= t < a1:
        n = int(round(keyed(t, [(T("y se apagan") - 0.05, 50), (T("y se apagan") + 0.5, 0)])))
        C.badge(ctx, f"ENCENDIDAS {n}/50", W / 2, Yb, win(t, a0, a1), G if n else R, size=74)
    label(C, ctx, t, T("si se rompe") + 0.3, T("y se apagan") + 0.4, "CORTE", A, "b5", dx=0, dy=-150, size=62)
    # dentro de la bombilla
    label(C, ctx, t, T("filamento") - 0.1, T("mientras"), "FILAMENTO", A, "fil", dx=0, dy=-250, size=58)
    label(C, ctx, t, T("derivación") - 0.1, T("mientras") + 0.6, "DERIVACIÓN", A, "shunt", dx=170, dy=230, size=58)
    label(C, ctx, t, T("aislado") - 0.1, T("la corriente prefiere") + 0.5, "AISLANTE", A, "shunt", dx=170, dy=230, size=58)
    a0, a1 = T("mientras"), T("y aquí")
    if a0 <= t < a1:
        v = keyed(t, [(a0, 4.6), (T("toda la tensión") - 0.1, 4.6), (T("hueco", fin=True), 230), (T("se suelda") + 0.3, 230), (T("se suelda") + 1.0, 0.2)])
        voltimetro(ctx, C, t, A, v, win(t, a0, a1))
    label(C, ctx, t, T("el aislante") + 0.1, T("se suelda"), "SE QUEMA", A, "shunt", dx=170, dy=230, size=58)
    label(C, ctx, t, T("se suelda") + 0.1, T("la corriente pasa") + 1.0, "SOLDADO", A, "shunt", dx=170, dy=230, size=58)
    # menos bombillas, más tensión
    a0, a1 = T("cada bombilla que"), T("noventa") - 0.4
    if a0 <= t < a1:
        n = 50 - (t > a0 + 0.5) - (t > T("y se funden") + 0.1) - (t > T("una avería") + 0.1)
        v = 230 / n
        C.badge(ctx, f"{n} BOMBILLAS · {num(v)} V", W / 2, Yb, win(t, a0, a1), Y, size=70)
    label(C, ctx, t, T("y se funden") + 0.1, T("una avería") + 0.1, "FUNDIDA", A, "b6", dx=0, dy=-150, size=60)
    label(C, ctx, t, T("una avería") + 0.1, T("una avería") + 1.3, "FUNDIDA", A, "b1", dx=0, dy=-150, size=60)
    # probabilidad
    a0, a1 = T("noventa") - 0.3, T("una guirnalda de")
    if a0 <= t < a1:
        C.badge(ctx, "1 BOMBILLA: 99 %", W / 2, Yb, win(t, a0, a1), G, size=72)
    a0, a1 = T("una guirnalda de"), T("con ciento")
    if a0 <= t < a1:
        ok = 10 if t < T("seis") - 0.2 else 6
        C.badge(ctx, f"50 BOMBILLAS · {ok}/10 ENTERAS", W / 2, Yb, win(t, a0, a1), G if ok == 10 else Y, size=62)
        p = win(t, T("seis"), a1)
        if p: C.badge(ctx, "60 %", W / 2, Yb + 120, p, Y, size=80)
    a0, a1 = T("con ciento"), T("por eso")
    if a0 <= t < a1:
        ok = 6 if t < T("dos de cada") - 0.3 else 2
        C.badge(ctx, f"150 BOMBILLAS · {ok}/10 ENTERAS", W / 2, Yb, win(t, a0, a1), Y if ok == 6 else R, size=60)
        p = win(t, T("dos de cada"), a1)
        if p: C.badge(ctx, "22 %", W / 2, Yb + 120, p, R, size=80)
    a0 = T("cambiar") + 1.6
    if a0 <= t:
        C.badge(ctx, "✓ 50 BOMBILLAS · 4,6 V", W / 2, Yb, win(t, a0, DUR + 1), G, size=66)

def sfx_events(C):
    E = [(0.0, C.s_buzz(0.5), 0.15), (0.55, C.s_pop(), 0.6), (0.57, C.s_clank(), 0.25), (T("fundida"), C.s_fail(), 0.3),
         (T("mira por"), C.s_whoosh(), 0.4), (T("van en fila"), C.s_whoosh(), 0.35), (T("la corriente entra"), C.s_buzz(4.0), 0.2),
         (T("si se rompe") + 0.3, C.s_pop(), 0.5), (T("y se apagan"), C.s_fail(), 0.45), (T("así que dentro"), C.s_whoosh(), 0.4),
         (T("filamento") - 0.1, C.s_pop(), 0.35), (T("derivación") - 0.1, C.s_pop(), 0.4), (T("aislado"), C.s_pop(), 0.35),
         (T("la corriente prefiere"), C.s_buzz(1.6), 0.2), (T("se rompe", 2) + 0.15, C.s_pop(), 0.55), (T("hueco"), C.s_coin(), 0.35),
         (T("el aislante"), C.s_buzz(0.7), 0.35), (T("se suelda"), C.s_clank(), 0.4), (T("siguen"), C.s_win(), 0.35),
         (T("y aquí"), C.s_whoosh(), 0.35), (T("cada bombilla que") + 0.5, C.s_pop(), 0.35), (T("reciben"), C.s_coin(), 0.3),
         (T("y se funden") + 0.1, C.s_pop(), 0.55), (T("una avería") + 0.1, C.s_pop(), 0.55), (T("noventa") - 0.3, C.s_whoosh(), 0.4)]
    E += [(T("una guirnalda de") + 0.08 * r, C.s_bleep(900 + 40 * r), 0.25) for r in range(10)]
    E += [(T("seis"), C.s_fail(), 0.35), (T("con ciento"), C.s_whoosh(), 0.35), (T("dos de cada"), C.s_fail(), 0.4)]
    a = T("cambiar") - 0.1
    E += [(a + 0.7 * k + 0.4, C.s_clank(), 0.3) for k in range(3)] + [(a + 1.8, C.s_win(), 0.4), (T("sígueme"), C.s_whoosh(), 0.4)]
    return E
