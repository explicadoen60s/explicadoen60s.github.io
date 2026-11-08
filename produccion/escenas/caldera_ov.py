# Capa 2D de «Así funciona una caldera de condensación»
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("caldera")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"caldera", "calor", "humo", "gas", "llama", "tubo", "agua", "bomba", "radiadores", "fría", "dióxido", "carbono",
            "vapor", "chimenea", "segundo", "intercambiador", "líquido", "condensarse", "gotea", "ciento", "nueve", "energía",
            "escondido", "sesenta", "setenta", "noventa", "quince", "europa", "veinticinco"}

def ss(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def keyed(t, keys):
    if t <= keys[0][0]: return keys[0][1]
    for (a, va), (b, vb) in zip(keys, keys[1:]):
        if a <= t <= b: return va + (vb - va) * ss((t - a) / max(b - a, 1e-4))
    return keys[-1][1]

HOT = (1.0, 0.36, 0.24); COLD = (0.35, 0.65, 1.0); Bl = (0.45, 0.75, 1.0)

def label(C, ctx, t, a, b, text, A, key, dx=0, dy=-220, size=64):
    """como la de _ovbase, pero sin subir a la zona del subtítulo ni de los marcadores"""
    p = win(t, a, b)
    if p:
        x, y = A(key); C.callout(ctx, text, clampx(x + dx, 250), clampy(y + dy, 640, 1420), p, size=size)

def badge(C, ctx, t, a, b, text, col, size=70):
    p = win(t, a, b)
    if p: C.badge(ctx, text, W / 2, H * 0.29, p, col, size=size)

def tag(C, ctx, x, y, s, col, p, size=50):
    """etiqueta de temperatura pegada a una tubería: pastilla de color con texto blanco"""
    if p <= 0: return
    sc = C.back(p)
    if sc < 1e-3: return
    e = C.text_path(ctx, s, size); w = e.x_advance + 40; h = size * 1.4
    x = max(30 + w / 2, min(930 - w / 2, x)); y = clampy(y, 640, 1440)
    ctx.save(); ctx.translate(x, y); ctx.scale(sc, sc)
    C.rrect(ctx, -w / 2 + 3, -h / 2 + 5, w, h, h / 2); ctx.set_source_rgba(0, 0, 0, 0.3); ctx.fill()
    C.rrect(ctx, -w / 2, -h / 2, w, h, h / 2); ctx.set_source_rgba(*col, 0.95); ctx.fill()
    ctx.move_to(-e.x_advance / 2, size * 0.36); ctx.text_path(s); ctx.set_source_rgb(1, 1, 1); ctx.fill()
    ctx.restore()

def medidor(C, ctx, t, p, v, split):
    """barra de rendimiento: 0-115 %, marca en 100 %; la parte por encima de 100 se vuelve azul (vapor)"""
    if p <= 0: return
    a = C.ease(p); x0, x1, y, hb = 110, 900, 1330, 50
    ctx.save(); ctx.translate(0, (1 - a) * 60)
    C.rrect(ctx, x0 - 30, y - 150, x1 - x0 + 60, 250, 30); ctx.set_source_rgba(0.06, 0.07, 0.1, 0.82 * a); ctx.fill()
    X = lambda q: x0 + (x1 - x0) * q / 112
    C.rrect(ctx, x0, y, x1 - x0, hb, hb / 2); ctx.set_source_rgba(0.3, 0.32, 0.38, a); ctx.fill()
    fv = min(v, 100)
    if fv > 1:
        C.rrect(ctx, x0, y, X(fv) - x0, hb, hb / 2); ctx.set_source_rgba(1.0, 0.55, 0.2, a); ctx.fill()
    if v > 100:
        ctx.rectangle(X(100) - 10, y, X(v) - X(100) + 10, hb)
        col = tuple(o + (b - o) * split for o, b in zip((1.0, 0.55, 0.2), Bl)); ctx.set_source_rgba(*col, a); ctx.fill()
    # marca del 100 %
    ctx.set_source_rgba(1, 1, 1, a); ctx.set_line_width(5); ctx.move_to(X(100), y - 18); ctx.line_to(X(100), y + hb + 18); ctx.stroke()
    C.outlined(ctx, "100 %", X(100), y + hb + 52, 46, fill=(1, 1, 1), stroke=7, alpha=a)
    if split > 0.05:
        C.outlined(ctx, "VAPOR", X(104), y - 44, 50, fill=Bl, stroke=8, alpha=a * split)
        C.outlined(ctx, "GAS", X(50), y + hb + 52, 46, fill=(1.0, 0.65, 0.3), stroke=7, alpha=a * split)
    C.outlined(ctx, f"{int(round(v))} %", x0 + 150, y - 70, 92, fill=C.YL, stroke=12, alpha=a)
    ctx.restore()

def overlay(ctx, t, A, C):
    Y, R, G = C.YL, C.RED, C.GREEN
    Yb = H * 0.265
    # gancho
    label(C, ctx, t, 0.5, T("mira por"), "LLAMA", A, "llama", dx=-60, dy=-200, size=62)
    # grifo y termostato
    a0, a1 = T("o sube"), T("entra gas")
    if a0 - 0.1 <= t < a1:
        v = keyed(t, [(a0 + 0.2, 19), (a0 + 1.2, 22)])
        x, y = A("termo"); C.outlined(ctx, f"{int(round(v))}°", x, y + 10, 64, fill=(1, 0.75, 0.35), stroke=8, alpha=win(t, a0 - 0.1, a1))
        label(C, ctx, t, a0 - 0.1, a1 - 0.4, "TERMOSTATO", A, "termo", dx=0, dy=230, size=56)
    label(C, ctx, t, T("abres") + 0.3, T("o sube") - 0.3, "AGUA CALIENTE", A, "grifo", dx=120, dy=-230, size=54)
    label(C, ctx, t, T("entra gas"), T("encima"), "GAS", A, "gas", dx=160, dy=40, size=66)
    label(C, ctx, t, T("encima") + 0.2, T("una bomba"), "AGUA", A, "coil", dx=0, dy=-170, size=62)
    # temperatura del agua que sale
    a0, a1 = T("que se calienta") - 0.3, T("pero al quemar")
    if a0 <= t < a1:
        v = keyed(t, [(a0, 15), (a0 + 1.5, 70)])
        badge(C, ctx, t, a0, a1, f"AGUA {int(round(v))} °C", HOT, size=78)
    label(C, ctx, t, T("una bomba"), T("radiadores") + 0.4, "BOMBA", A, "bomba", dx=150, dy=-60, size=60)
    a0, a1 = T("radiadores") + 0.3, T("pero al quemar")
    if a0 <= t < a1:
        x, y = A("ida"); tag(C, ctx, x - 120, y, "IDA 70°", HOT, win(t, a0, a1))
    a0 = T("y vuelve") - 0.1
    if a0 <= t < a1:
        v = keyed(t, [(a0, 70), (a0 + 1.2, 40)])
        x, y = A("vuelta"); tag(C, ctx, x + 140, y, f"VUELTA {int(round(v))}°", COLD, win(t, a0, a1))
    label(C, ctx, t, T("que calientan") - 0.2, T("y vuelve"), "RADIADOR", A, "rad", dx=0, dy=-120, size=60)
    # humo: CO2 y vapor
    label(C, ctx, t, T("dióxido"), T("las calderas antiguas"), "CO2", A, "humo", dx=-200, dy=-30, size=70)
    label(C, ctx, t, T("vapor"), T("las calderas antiguas"), "H2O", A, "humo", dx=200, dy=-90, size=70)
    a0, a1 = T("muy caliente") - 0.3, T("así que las nuevas")
    if a0 <= t < a1:
        v = keyed(t, [(a0, 20), (a0 + 1.0, 150)])
        badge(C, ctx, t, a0, a1, f"HUMO {int(round(v))} °C", HOT, size=80)
    label(C, ctx, t, T("chimenea") - 0.1, T("y con él"), "CHIMENEA", A, "chim", dx=-250, dy=80, size=60)
    label(C, ctx, t, T("una parte") - 0.1, T("así que las nuevas") + 0.3, "CALOR PERDIDO", A, "chim", dx=230, dy=140, size=58)
    # segundo intercambiador
    label(C, ctx, t, T("segundo"), T("donde llega"), "2º INTERCAMBIADOR", A, "inter2", dx=0, dy=-190, size=54)
    a0, a1 = T("donde llega") + 0.3, T("el humo se enfría")
    if a0 <= t < a1:
        x, y = A("ret2"); tag(C, ctx, x + 120, y, "VUELTA 40°", COLD, win(t, a0, a1))
    a0, a1 = T("el humo se enfría"), T("por eso")
    if a0 <= t < a1:
        v = keyed(t, [(a0, 150), (T("líquido", fin=True), 50)])
        col = tuple(c + (h - c) * (v - 50) / 100 for c, h in zip(COLD, HOT))
        badge(C, ctx, t, a0, a1, f"HUMO {int(round(v))} °C", col, size=80)
    label(C, ctx, t, T("líquido"), T("por eso"), "GOTAS", A, "bandeja", dx=-120, dy=-150, size=60)
    a0, a1 = T("suelta") - 0.1, T("por eso")
    if a0 <= t < a1:
        x, y = A("ret2"); v = keyed(t, [(a0, 40), (a0 + 1.2, 52)])
        tag(C, ctx, x + 120, y, f"AGUA {int(round(v))}°", HOT, win(t, a0, a1))
    label(C, ctx, t, T("tiene un tubo") - 0.2, T("y aquí"), "CONDENSADOS", A, "tubo", dx=190, dy=60, size=54)
    # rendimiento 109 %
    a0, a1 = T("con las cuentas"), T("para que")
    if a0 <= t < a1:
        v = keyed(t, [(a0 + 0.3, 0), (T("ciento") - 0.1, 90), (T("ciento", 2, fin=True), 109)])
        medidor(C, ctx, t, win(t, a0, a1, 0.25), v, ss((t - T("es que")) / 1.0) if t > T("es que") else 0)
    # temperatura de trabajo
    a0, a1 = T("para que"), T("sesenta") - 0.2
    if a0 <= t < a1:
        x, y = A("ret2"); v = keyed(t, [(a0 + 0.3, 52), (T("volver fría", fin=True), 30)])
        tag(C, ctx, x + 120, y, f"VUELTA {int(round(v))}°", COLD, win(t, a0, a1))
    a0, a1 = T("sesenta"), T("desde dos")
    if a0 <= t < a1:
        v = keyed(t, [(a0, 60), (T("setenta"), 60), (T("setenta", fin=True) + 0.1, 70)])
        if t < T("y no a"): badge(C, ctx, t, a0, a1, f"✓ {int(round(v))} °C", G, size=88)
        else:
            C.badge(ctx, "✓ 60-70 °C", W / 2, H * 0.29, 1.0, G, size=80)
            C.badge(ctx, "✗ 90 °C", W / 2, H * 0.29 + 130, win(t, T("y no a"), a1), R, size=80)
    # 2015 y ahorro
    a0, a1 = T("desde dos"), T("gastan")
    if a0 <= t < a1:
        v = keyed(t, [(a0, 2000), (T("quince", fin=True), 2015)])
        badge(C, ctx, t, a0, a1, f"UE · {int(round(v))}", Bl, size=84)
    a0, a1 = T("gastan"), DUR + 1
    if a0 <= t < a1:
        v = keyed(t, [(a0 + 0.2, 0), (T("menos", fin=True), 25)])
        badge(C, ctx, t, a0, a1, f"−{int(round(v))} % GAS", G, size=88)

def sfx_events(C):
    E = [(0.05, C.s_whoosh(), 0.35), (0.12, C.s_thud(), 0.5), (0.2, C.s_buzz(5.8), 0.18)]
    E += [(T("sabías"), C.s_pop(), 0.35), (T("mira por"), C.s_whoosh(), 0.4), (T("abres"), C.s_whoosh(), 0.4),
          (T("o sube"), C.s_bleep(1200), 0.6), (T("o sube") + 0.4, C.s_bleep(1500), 0.6), (T("entra gas"), C.s_whoosh(), 0.35),
          (T("se enciende una") + 0.1, C.s_thud(), 0.55), (T("que se calienta"), C.s_coin(), 0.35), (T("una bomba"), C.s_buzz(2.2), 0.3),
          (T("radiadores"), C.s_whoosh(), 0.4), (T("y vuelve"), C.s_pop(), 0.4), (T("dióxido"), C.s_pop(), 0.4),
          (T("vapor"), C.s_pop(), 0.4), (T("chimenea"), C.s_whoosh(), 0.4), (T("una parte"), C.s_fail(), 0.4),
          (T("segundo"), C.s_clank(), 0.45), (T("donde llega"), C.s_whoosh(), 0.35), (T("líquido"), C.s_pop(), 0.4),
          (T("suelta"), C.s_coin(), 0.4), (T("gotea"), C.s_pop(), 0.35), (T("gotea") + 0.9, C.s_pop(), 0.3),
          (T("ciento", 2), C.s_win(), 0.45), (T("no crea"), C.s_thud(), 0.4), (T("escondido"), C.s_pop(), 0.4),
          (T("sesenta"), C.s_coin(), 0.35), (T("y no a"), C.s_fail(), 0.4), (T("quince"), C.s_pop(), 0.4),
          (T("veinticinco"), C.s_win(), 0.45), (T("sígueme"), C.s_whoosh(), 0.4)]
    return E
