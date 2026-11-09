# Capa 2D de «¿Y si construyes un molino de viento gigante?»
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("aerogenerador")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"viento", "electricidad", "molino", "suelo", "frenan", "alto", "ochenta", "sesenta", "volcaría", "zapata", "hormigón", "acero",
            "palas", "despacio", "generador", "quinientas", "multiplicadora", "engranajes", "punta", "trescientos", "dirección", "gira",
            "tres", "arranca", "noventa", "romperse", "canto", "para", "borrasca", "quietos"}

def ss(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def sg(t, a, b): return ss((t - a) / (b - a))
def miles(v): return f"{int(round(v)):,}".replace(",", ".")
BY = H * 0.265

def bombillas(ctx, t, p, C):
    """cinco bombillas: una se enciende (1 de cada 5)"""
    if p <= 0: return
    lit = sg(t, 1.3, 1.9)
    for i in range(5):
        x = W / 2 + (i - 2) * 150; y = BY + 10
        on = i == 2 and lit > 0.5
        col = C.YL if on else (0.55, 0.57, 0.62)
        ctx.save(); ctx.translate(x, y); s = C.back(p); ctx.scale(s, s)
        if on:
            ctx.arc(0, -10, 74, 0, math.tau); ctx.set_source_rgba(1, 0.85, 0.3, 0.28 * lit); ctx.fill()
        ctx.arc(0, -10, 44, 0, math.tau); ctx.set_source_rgba(0, 0, 0, 0.9); ctx.set_line_width(14); ctx.stroke_preserve()
        ctx.set_source_rgb(*col); ctx.fill()
        ctx.rectangle(-22, 30, 44, 34); ctx.set_source_rgb(0, 0, 0); ctx.fill()
        ctx.rectangle(-16, 34, 32, 26); ctx.set_source_rgb(0.7, 0.72, 0.75); ctx.fill()
        ctx.restore()

def num(C, ctx, s, x, y, p, col, size=64):
    if p > 0: C.outlined(ctx, s, clampx(x), clampy(y), size, fill=col, stroke=12, scale=C.back(p), alpha=min(1, p * 2))

def overlay(ctx, t, A, C):
    Y, R, G, B = C.YL, C.RED, C.GREEN, (0.45, 0.75, 1.0)
    # primer segundo: velocidad de la punta que pasa rozando
    p = win(t, 0.0, 1.1)
    if p:
        v = 280 + 17 * sg(t, 0.0, 0.5)
        C.badge(ctx, f"{int(v)} KM/H", W / 2, BY, p, Y, size=84)
    bombillas(ctx, t, win(t, 1.15, T("y si tuvieras") - 0.1), C)
    # viento frenado cerca del suelo
    label(C, ctx, t, T("cerca del suelo") + 0.2, T("así que subes"), "LENTO", A, "suelo", dx=80, dy=110, size=56)
    label(C, ctx, t, T("los árboles") + 0.4, T("así que subes"), "RÁPIDO", A, "alto", dx=120, dy=110, size=56)
    # regla de altura 80 → 160 m
    a0, a1 = T("así que subes"), T("pero una torre")
    if a0 <= t < a1:
        m = 80 * sg(t, T("ochenta") - 0.4, T("ochenta") + 0.9) + 80 * sg(t, T("sesenta", fin=True) - 1.3, T("sesenta", fin=True))
        x, y = A("regla")
        num(C, ctx, f"{int(m)} M", x + 150, y - 10, win(t, a0 + 0.6, a1), Y, size=74)
    badge(C, ctx, t, T("volcaría") - 0.2, T("así que bajo") + 0.3, "✗ VUELCA", R, size=86)
    label(C, ctx, t, T("zapata") + 0.1, T("arriba colocas"), "ZAPATA", A, "zap", dx=0, dy=260, size=64)
    # palas de 85 m
    a0, a1 = T("de hasta"), T("pero giran")
    if a0 <= t < a1:
        x, y = A("pala"); num(C, ctx, f"{int(85 * sg(t, a0 - 0.1, a0 + 0.8))} M", x - 140, y, win(t, a0, a1), Y, size=70)
    # rpm del rotor y del generador
    a0, a1 = T("entre diez"), T("en la caja") - 0.3
    if a0 <= t < a1:
        rpm = keyed_rpm(t, a0) if t < a0 + 2.4 else 10
        C.badge(ctx, f"ROTOR {int(rpm)} RPM", W / 2, BY, win(t, a0, a1), B, size=70)
        b0 = T("el generador")
        if t > b0:
            C.badge(ctx, "✗ GENERADOR 1.500 RPM", W / 2, BY + 120, win(t, b0, a1), R, size=60)
    # multiplicadora: 10 → 1.500
    a0, a1 = T("en la caja"), T("y aquí viene")
    if a0 <= t < a1:
        label(C, ctx, t, T("pones una multiplicadora"), T("engranajes") + 0.6, "MULTIPLICADORA", A, "nac", dx=0, dy=-300, size=60)
        x, y = A("g1"); num(C, ctx, "10 RPM", x - 40, y + 260, win(t, T("engranajes"), a1), B, size=58)
        g = 10 + 1490 * sg(t, T("cada vuelta lenta"), T("rápidas", fin=True))
        x, y = A("gen")
        num(C, ctx, f"{miles(g)} RPM", x - 60, y + 360, win(t, T("engranajes") + 0.4, a1), G if g > 1490 else Y, size=64)
        C.badge(ctx, "× 150", W / 2, BY, win(t, T("cada vuelta lenta") + 0.8, a1), Y, size=84)
    # punta a 300 km/h
    a0, a1 = T("aunque las palas"), T("pero el viento cambia")
    if a0 <= t < a1:
        C.badge(ctx, "ROTOR 10 RPM", W / 2, BY, win(t, a0, T("la punta va") + 0.1), B, size=70)
        v = 300 * sg(t, T("la punta va"), T("trescientos", fin=True) + 0.5)
        C.badge(ctx, f"PUNTA {int(v)} KM/H", W / 2, BY, win(t, T("la punta va") + 0.1, a1), R, size=78)
    # la góndola gira hacia el viento
    a0, a1 = T("pero el viento cambia"), T("con unos tres")
    if a0 <= t < a1:
        ang = 35 * sg(t, T("así que la caja"), T("hasta mirar") + 0.6)
        C.badge(ctx, f"GIRO {int(ang)}°", W / 2, BY, win(t, T("así que la caja"), a1), Y, size=80)
        brujula(ctx, t, C, win(t, a0 + 0.2, a1))
    # anemómetro: 3 m/s y arranca
    a0, a1 = T("con unos tres"), T("pero si sopla")
    if a0 <= t < a1:
        v = 3 * sg(t, a0, T("segundo", fin=True))
        C.badge(ctx, f"VIENTO {v:.1f} M/S".replace(".", ","), W / 2, BY, win(t, a0, a1), B, size=74)
        label(C, ctx, t, a0 + 0.2, T("el molino arranca"), "ANEMÓMETRO", A, "anem", dx=0, dy=-200, size=54)
        C.badge(ctx, "✓ ARRANCA", W / 2, BY + 130, win(t, T("el molino arranca"), a1), G, size=70)
    # 90 km/h → de canto y freno
    a0, a1 = T("pero si sopla"), T("por eso")
    if a0 <= t < a1:
        v = 15 + 75 * sg(t, a0 + 0.3, T("noventa", fin=True) + 0.6)
        C.badge(ctx, f"VIENTO {int(v)} KM/H", W / 2, BY, win(t, a0, a1), R if v > 80 else Y, size=78)
        r = 10 * (1 - sg(t, T("frena y"), T("se para", fin=True) + 0.3))
        if t > T("pone las palas"):
            C.badge(ctx, f"ROTOR {int(round(r))} RPM", W / 2, BY + 125, win(t, T("pone las palas"), a1), B, size=62)
    a0 = T("por eso")
    if t >= a0:
        C.badge(ctx, "0 RPM", W / 2, BY, win(t, a0 + 0.3, DUR), B, size=80)

def keyed_rpm(t, a0):
    # el contador recorre el rango 10 → 40 y se queda en 10
    u = (t - a0) / 2.4
    if u < 0.5: return 10 + 30 * ss(u / 0.5)
    return 40 - 30 * ss((u - 0.5) / 0.5)

def brujula(ctx, t, C, p):
    if p <= 0: return
    a = math.radians(35) * sg(t, T("pero el viento cambia"), T("pero el viento cambia") + 1.2)   # viento
    g = math.radians(35) * sg(t, T("así que la caja"), T("hasta mirar") + 0.6)                  # góndola
    cx, cy, r = W * 0.27, H * 0.66, 105
    ctx.save(); ctx.translate(cx, cy); s = C.back(p); ctx.scale(s, s)
    ctx.arc(0, 0, r, 0, math.tau); ctx.set_source_rgba(0.13, 0.15, 0.19, 0.9); ctx.fill_preserve()
    ctx.set_line_width(5); ctx.set_source_rgba(1, 1, 1, 0.3); ctx.stroke()
    def flecha(ang, col, L, lw):
        dx, dy = math.cos(ang), -math.sin(ang)
        ctx.set_line_cap(1); ctx.set_line_width(lw); ctx.set_source_rgb(*col)
        ctx.move_to(-dx * L, -dy * L); ctx.line_to(dx * L, dy * L); ctx.stroke()
        hx, hy = dx * L, dy * L
        for s_ in (1, -1):
            b = ang + math.pi + s_ * 0.5
            ctx.move_to(hx, hy); ctx.line_to(hx + math.cos(b) * 30, hy - math.sin(b) * 30); ctx.stroke()
    flecha(a, (0.45, 0.75, 1.0), 80, 12)                     # viento
    ctx.set_source_rgb(0.95, 0.95, 0.97)                      # góndola (mira contra el viento)
    ctx.save(); ctx.rotate(-g); ctx.rectangle(-18, -14, 50, 28); ctx.fill()
    ctx.rectangle(-30, -60, 10, 120); ctx.fill(); ctx.restore()
    ctx.restore()

def sfx_events(C):
    E = [(0.2, C.s_whoosh(0.7), 0.6), (1.4, C.s_pop(), 0.45), (T("vamos a levantarlo"), C.s_whoosh(), 0.4),
         (T("cerca del suelo"), C.s_whoosh(1.2), 0.3), (T("ochenta"), C.s_clank(), 0.4), (T("sesenta"), C.s_clank(), 0.4),
         (T("volcaría"), C.s_fail(), 0.5), (T("zapata"), C.s_thud(), 0.6), (T("hormigón"), C.s_thud(), 0.5),
         (T("arriba colocas"), C.s_clank(), 0.5)]
    for i in range(3): E.append((T("tres palas") + 0.45 * i, C.s_pop(), 0.4))
    E += [(T("el generador"), C.s_fail(), 0.4), (T("pones una multiplicadora"), C.s_clank(), 0.45), (T("cada vuelta lenta"), C.s_buzz(1.8), 0.35),
          (T("la punta va"), C.s_whoosh(0.8), 0.6), (T("la punta va") + 1.3, C.s_whoosh(0.8), 0.6), (T("así que la caja"), C.s_buzz(2.5), 0.25),
          (T("el molino arranca"), C.s_win(), 0.45), (T("a unos noventa"), C.s_whoosh(1.5), 0.5), (T("podría romperse"), C.s_fail(), 0.45),
          (T("pone las palas"), C.s_clank(), 0.45), (T("frena y"), C.s_thud(), 0.5), (T("sígueme"), C.s_whoosh(), 0.4)]
    return E
