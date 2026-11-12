# Capa 2D de «El ticket del súper no lleva tinta»
# Pastillas previstas (motion → fotografía), todas en el tercio superior junto a su pieza:
# 0 ml de tinta junto a la parte alta del ticket · 8 puntos/mm y 576 puntos sobre el cabezal · 20→100 °C sobre el punto
# caliente · 0→1.000 líneas/s junto a la ranura · 20→60 °C junto al sol · 0→12 meses junto al ticket.
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("ticket")
SUB_ESTILO = "frase"
KEYWORDS = {"ticket", "súper", "cartera", "tinta", "impresora", "papel", "capa", "polvos", "tinte", "ácido", "blanco", "cabezal",
            "puntos", "ocho", "milímetro", "quinientos", "cien", "grados", "derrite", "negro", "mil", "líneas", "segundo",
            "sol", "calor", "coche", "crema", "letra", "desaparece", "año", "uña", "rascas", "calientas"}

def gota_tachada(C, ctx, x, y, p):
    """gota de tinta tachada (no hay tinta)"""
    if p <= 0: return
    ctx.save(); ctx.translate(x, y); s = C.back(p) if C.back(p) > 1e-3 else 1e-3; ctx.scale(s, s)
    ctx.move_to(0, -70); ctx.curve_to(40, -10, 55, 20, 0, 55); ctx.curve_to(-55, 20, -40, -10, 0, -70)
    ctx.set_source_rgba(0.1, 0.2, 0.55, 0.95); ctx.fill_preserve(); ctx.set_source_rgba(1, 1, 1, 1); ctx.set_line_width(6); ctx.stroke()
    ctx.set_line_width(16); ctx.set_source_rgba(*C.RED, 1); ctx.move_to(-60, -60); ctx.line_to(60, 60); ctx.stroke()
    ctx.restore()

def milimetro(C, ctx, t, a, b, x, y):
    """cota de 1 mm con sus 8 puntos"""
    if t < a or t > b: return
    al = min(1, (t - a) / 0.25, (b - t) / 0.2); w = 320
    ctx.save(); ctx.set_source_rgba(1, 0.82, 0.16, al); ctx.set_line_width(7)
    ctx.move_to(x - w / 2, y); ctx.line_to(x + w / 2, y); ctx.stroke()
    for xx in (x - w / 2, x + w / 2): ctx.move_to(xx, y - 22); ctx.line_to(xx, y + 22); ctx.stroke()
    n = min(8, int((t - a) * 8) + 1)
    for i in range(n):
        ctx.arc(x - w / 2 + w * (i + 0.5) / 8, y + 46, 13, 0, math.tau); ctx.fill()
    ctx.restore()
    C.outlined(ctx, "1 mm", x, y - 50, 54, alpha=al, shadow=False, stroke=8)

def overlay(ctx, t, A, C):
    # rótulos de pieza (uno cada vez)
    C.rotulo(ctx, t, "CAPA TÉRMICA", T("una capa"), T("una capa") + 1.7)
    C.rotulo(ctx, t, "TINTE", T("uno es un"), T("uno es un") + 1.5)
    C.rotulo(ctx, t, "ÁCIDO", T("un ácido"), T("un ácido") + 1.4)
    C.rotulo(ctx, t, "CABEZAL", T("el cabezal"), T("el cabezal") + 1.5)
    # sin tinta
    x, y = A("tktop")
    a0, a1 = T("no lleva"), T("vamos a abrir")
    gota_tachada(C, ctx, clampx(x + 250, 300), clampy(y + 60, 480), win(t, a0, a1))
    C.pastilla(ctx, t, 0, "ml de tinta", a0 + 0.2, a1, clampx(x + 250, 300), clampy(y + 200, 480), desde=5, dur=1.1, size=60)
    # 8 puntos por milímetro y 576 en todo el ancho
    milimetro(C, ctx, t, T("hay ocho"), T("más de quinientos"), W / 2, H * 0.62)
    x, y = A("head")
    C.pastilla(ctx, t, 8, "puntos/mm", T("hay ocho"), T("más de quinientos"), clampx(x, 300), clampy(y - 120, 480), desde=0, dur=0.8)
    x, y = A("cabezal")
    C.pastilla(ctx, t, 576, "puntos", T("más de quinientos"), T("cuando un punto"), clampx(x, 300), clampy(y - 170, 480), desde=0, dur=1.6)
    # temperatura del punto
    x, y = A("dot")
    a0 = T("cuando un punto")
    C.pastilla(ctx, t, 100, "°C", a0, T("y el punto") + 0.3, clampx(x + 200, 300), clampy(y - 170, 480), desde=20, dur=T("cien grados", fin=True) - a0)
    # líneas por segundo
    x, y = A("slot")
    C.pastilla(ctx, t, 1000, "líneas/s", T("más de mil") - 0.1, T("la impresora casi"), clampx(x + 230, 300), clampy(y - 330, 480), desde=0, dur=1.2)
    # sol y coche: temperatura que deshace
    x, y = A("sol")
    C.pastilla(ctx, t, 60, "°C en el coche", T("el calor"), T("el tinte vuelve"), clampx(x + 120, 330), clampy(y + 160, 480), desde=20, dur=1.6, size=62)
    # un año en la cartera
    x, y = A("ticket")
    C.pastilla(ctx, t, 12, "meses", T("por eso tu"), T("y si lo rascas"), clampx(x + 250, 300), clampy(y - 150, 480), desde=0, dur=2.2)
    # rayitas al rascar
    x, y = A("dedo")
    C.chispa(ctx, t, x, y, T("se pone negro"), r=60)
    C.chispa(ctx, t, *A("dot"), T("y el punto") + 0.4, r=60, col=(1, 0.85, 0.3))

def sfx_events(C):
    E = [(0.0, C.s_buzz(2.4), 0.25), (0.05, C.s_whoosh(), 0.35), (T("no lleva"), C.s_pop(), 0.45), (T("tinta"), C.s_fail(), 0.4),
         (T("entonces"), C.s_whoosh(), 0.35), (T("vamos a abrir"), C.s_clank(), 0.45), (T("el papel tiene"), C.s_whoosh(0.7), 0.4),
         (T("dentro hay"), C.s_pop(), 0.4), (T("pero quietos"), C.s_thud(), 0.35), (T("uno es un"), C.s_pop(), 0.45),
         (T("un ácido"), C.s_pop(), 0.45), (T("el papel sigue"), C.s_bleep(660), 0.25), (T("el cabezal"), C.s_clank(), 0.5),
         (T("es una fila"), C.s_tick(), 0.4), (T("hay ocho") - 0.3, C.s_tick(), 0.4), (T("más de quinientos") - 0.3, C.s_whoosh(), 0.35),
         (T("cuando un punto"), C.s_buzz(1.8), 0.25), (T("la capa se"), C.s_whoosh(), 0.3), (T("se tocan"), C.s_pop(), 0.45),
         (T("y el punto") + 0.4, C.s_win(), 0.4), (T("y aquí viene"), C.s_whoosh(), 0.35), (T("el cabezal no"), C.s_thud(), 0.4),
         (T("es el papel"), C.s_buzz(4.0), 0.22), (T("más de mil") - 0.3, C.s_tick(), 0.4), (T("por eso los"), C.s_coin(), 0.4),
         (T("pero esa"), C.s_whoosh(), 0.35), (T("el sol"), C.s_pop(), 0.45), (T("el calor"), C.s_bleep(440), 0.25),
         (T("la crema"), C.s_pop(), 0.4), (T("el tinte vuelve"), C.s_whoosh(0.7), 0.35), (T("desaparece"), C.s_fail(), 0.4),
         (T("por eso tu"), C.s_thud(), 0.4), (T("y si lo rascas"), C.s_buzz(1.2), 0.25), (T("se pone negro"), C.s_win(), 0.4),
         (T("lo calientas"), C.s_coin(), 0.35), (T("sígueme"), C.s_whoosh(), 0.4)]
    return E
