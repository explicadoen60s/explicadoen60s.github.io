# Capa 2D de «¿Y si construyes un campo de fútbol?»
# Pastillas previstas (motion → fotografía): 10 min sobre el charco · ≈2 m junto a la cota del hoyo (derecha) ·
# termómetro de las raíces a la izquierda (invierno → calefacción) · 20 cm junto al hilo · 5 % / 95 % arriba al centro.
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("estadio")
SUB_ESTILO = "centro"
KEYWORDS = {"fútbol", "césped", "campo", "cavar", "hierba", "tierra", "lluvia", "diez", "minutos", "barrizal", "dos", "metros", "capas",
            "piedras", "grava", "arena", "tubos", "agujeros", "agua", "invierno", "frío", "raíces", "caliente", "calefacción", "tacos",
            "natural", "máquina", "hilos", "plástico", "veinte", "centímetros", "cinco", "ciento", "gradas", "sol", "noche", "luz",
            "rampas", "día"}

def cota(ctx, t, a, b, p0, p1, dx=110, col=(1, 0.82, 0.16)):
    if t < a or t > b: return
    al = min(1, (t - a) / 0.25, (b - t) / 0.2); x = p0[0] + dx
    ctx.save(); ctx.set_line_width(8); ctx.set_source_rgba(*col, al)
    ctx.move_to(x, p0[1]); ctx.line_to(x, p1[1]); ctx.stroke()
    for y in (p0[1], p1[1]): ctx.move_to(x - 28, y); ctx.line_to(x + 28, y); ctx.stroke()
    ctx.restore()

def termometro(C, ctx, t, a, b, x, y, nivel):
    """medidor vertical frío (azul) → caliente (rojo), sin cifras"""
    if t < a or t > b: return
    al = min(1, (t - a) / 0.25, (b - t) / 0.2); h = 300
    ctx.save()
    C.rrect(ctx, x - 34, y - h, 68, h + 40, 34); ctx.set_source_rgba(0.17, 0.18, 0.21, 0.9 * al); ctx.fill()
    col = (0.35 + 0.6 * nivel, 0.55 - 0.3 * nivel, 0.95 - 0.75 * nivel)
    hh = (h - 50) * (0.15 + 0.85 * nivel)
    C.rrect(ctx, x - 14, y - 10 - hh, 28, hh, 14); ctx.set_source_rgba(*col, al); ctx.fill()
    ctx.arc(x, y, 30, 0, 7); ctx.fill()
    C.outlined(ctx, "❄" if nivel < 0.4 else "☀", x, y - h - 45, 56, fill=(1, 1, 1), stroke=8, alpha=al, shadow=False)
    ctx.restore()

def seg01(t, a, b):
    x = max(0.0, min(1.0, (t - a) / max(b - a, 1e-4))); return x * x * (3 - 2 * x)

def overlay(ctx, t, A, C):
    C.rotulo(ctx, t, "PIEDRAS", T("piedras gordas"), T("grava y") - 0.05)
    C.rotulo(ctx, t, "GRAVA", T("grava y"), T("arena") - 0.05)
    C.rotulo(ctx, t, "ARENA", T("arena"), T("bajo todo"))
    C.rotulo(ctx, t, "TUBOS DE DRENAJE", T("una red de tubos"), T("que se lleva", fin=True) + 0.3)
    C.rotulo(ctx, t, "TUBOS DE AGUA CALIENTE", T("así que metes"), T("como una"))
    C.rotulo(ctx, t, "HILOS DE PLÁSTICO", T("una máquina") + 0.3, T("uno a uno", fin=True))
    C.rotulo(ctx, t, "RAÍCES", T("las raíces de"), T("y ya no"))
    C.rotulo(ctx, t, "RAMPAS DE LUZ", T("acercan") + 0.3, T("la hierba cree"))
    # 10 minutos de lluvia
    x, y = A("charco")
    C.pastilla(ctx, t, 10, "min", T("a los diez") - 0.2, T("así que bajas"), clampx(x), clampy(y - 200, 430), desde=0, dur=1.2)
    # casi 2 m de hoyo
    cota(ctx, t, T("así que bajas") + 0.2, T("y lo rellenas"), A("top"), A("fondo"))
    x, y = A("top"); x2, y2 = A("fondo")
    C.pastilla(ctx, t, 1.8, "m", T("casi"), T("y lo rellenas") + 0.3, clampx(x + 110, 300), clampy((y + y2) / 2, 430, 1350), desde=0, dec=1, dur=1.4)
    # flecha de la lluvia que se cuela al drenaje
    x, y = A("dren")
    C.pastilla(ctx, t, 100, "% del agua", T("que se lleva"), T("pero en invierno"), clampx(x), clampy(y - 170, 430, 1350), desde=0, dur=1.0, size=60)
    # termómetro de las raíces
    if T("pero en invierno") <= t < T("pero los tacos"):
        nv = 0.75 - 0.65 * seg01(t, T("pero en invierno"), T("con el frío", fin=True)) + 0.85 * seg01(t, T("con agua caliente"), T("como una") + 0.5)
        termometro(C, ctx, t, T("pero en invierno"), T("pero los tacos"), 170, H * 0.62, max(0, min(1, nv)))
    # bota: trozos de césped arrancados y luego aguanta
    x, y = A("bota")
    C.pastilla(ctx, t, 4, "trozos fuera", T("arrancan"), T("y aquí viene"), clampx(x + 60, 300), clampy(y - 220, 430), desde=0, dur=0.8, size=58)
    C.chispa(ctx, t, x, y + 120, T("y ya no") + 0.4, r=80)
    # 20 cm de hilo
    cota(ctx, t, T("cada hilo"), T("las raíces de") + 0.6, A("hilo_top"), A("hilo_bot"), dx=90)
    x, y = A("hilo_top")
    C.pastilla(ctx, t, 20, "cm", T("veinte") - 0.1, T("las raíces de") + 0.6, clampx(x + 250, 300), clampy(y + 40, 430, 1350), desde=0, dur=0.8)
    # 5 % plástico / 95 % hierba
    C.pastilla(ctx, t, 5, "% plástico", T("solo un cinco") + 0.2, T("el resto"), W / 2, H * 0.30, desde=0, dur=0.8)
    C.pastilla(ctx, t, 95, "% hierba", T("el resto"), T("pero dentro"), W / 2, H * 0.30, desde=5, dur=0.9)
    # sol tapado y luz artificial
    x, y = A("rampa")
    C.pastilla(ctx, t, 100, "% luz", T("acercan") + 0.5, T("y sigue", fin=True) + 0.3, clampx(x + 120, 300), clampy(y - 110, 430), desde=0, dur=1.2, size=60)

def sfx_events(C):
    E = [(0.0, C.s_thud(), 0.45), (0.62, C.s_thud(), 0.35), (1.25, C.s_thud(), 0.3), (0.0, C.s_buzz(4.5), 0.08),
         (T("y el césped") + 0.4, C.s_whoosh(), 0.3), (T("y si tuvieras"), C.s_whoosh(), 0.35), (T("vamos a cavar"), C.s_clank(), 0.45),
         (T("la lluvia se"), C.s_buzz(3.0), 0.12), (T("a los diez") - 0.3, C.s_tick(), 0.4), (T("barrizal"), C.s_fail(), 0.4),
         (T("así que bajas"), C.s_whoosh(0.8), 0.45), (T("casi") - 0.3, C.s_tick(), 0.35), (T("piedras gordas"), C.s_thud(), 0.5),
         (T("grava y"), C.s_pop(), 0.45), (T("arena"), C.s_pop(), 0.4), (T("una red de tubos"), C.s_clank(), 0.45),
         (T("que se lleva"), C.s_coin(), 0.35), (T("pero en invierno"), C.s_whoosh(), 0.35), (T("con el frío"), C.s_bleep(330), 0.25),
         (T("así que metes"), C.s_clank(), 0.45), (T("con agua caliente"), C.s_bleep(660), 0.25), (T("pero para el"), C.s_win(), 0.35),
         (T("pero los tacos") + 0.4, C.s_thud(), 0.55), (T("arrancan"), C.s_fail(), 0.4), (T("y aquí viene"), C.s_whoosh(), 0.4),
         (T("natural"), C.s_pop(), 0.4), (T("una máquina"), C.s_buzz(2.6), 0.18), (T("veinte") - 0.35, C.s_tick(), 0.4),
         (T("las raíces de"), C.s_whoosh(), 0.35), (T("y ya no") + 0.4, C.s_thud(), 0.5), (T("y ya no") + 0.6, C.s_win(), 0.35),
         (T("solo un cinco") - 0.1, C.s_coin(), 0.4), (T("el resto"), C.s_coin(), 0.35), (T("pero dentro"), C.s_whoosh(), 0.35),
         (T("tapan el sol"), C.s_fail(), 0.35), (T("por la noche"), C.s_whoosh(), 0.35), (T("acercan"), C.s_clank(), 0.5),
         (T("enormes"), C.s_buzz(1.2), 0.2), (T("la hierba cree"), C.s_pop(), 0.4), (T("y sigue"), C.s_win(), 0.4),
         (T("sígueme"), C.s_whoosh(), 0.4), (T("sígueme") + 0.4, C.s_thud(), 0.35)]
    for k in range(10): E.append((T("una máquina") + 0.4 + 0.3 * k, C.s_tick(), 0.18))
    return E
