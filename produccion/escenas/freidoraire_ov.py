# Capa 2D de «¿A cuántos grados sopla tu freidora de aire?»
# Experimento de motion (14-nov): 9 rótulos de pieza y 6 contadores como mucho, con la cifra del juego como el más grande.
# Pastillas (motion → fotografía): entran ≤0,3 s después del corte de su plano, como mucho 2 por plano, por debajo de y=560.
#  1.700 W sobre la resistencia (13,2) · 15 min sobre el horno (40,3) · 5 min sobre el display (43,9) · −20 °C sobre el mando (47,9)
# Juego: 200 °C; la tarjeta no desaparece tras la revelación (queda en la esquina en verde y vuelve en «¿Te has acercado?»).
from _ovbase import *
from marcas import cargar
T, DUR = cargar("freidoraire")
SUB_ESTILO = "centro"
SUB_Y = 0.50
KEYWORDS = {"freidora", "aire", "grados", "blanda", "horno", "turbo", "resistencia", "mil", "setecientos", "vatios", "ventilador",
            "agua", "crujiente", "cesto", "agujeros", "patata", "patatas", "vapor", "veinte", "doscientos", "diez", "quince",
            "minutos", "tres", "cinco", "capa", "sacude"}

def pastilla(C, ctx, t, v, u, a, b, A, key, dx=0, dy=-110, desde=None, dec=0, dur=0.9, size=62, lo=560):
    x, y = A(key); C.pastilla(ctx, t, v, u, a, b, clampx(x + dx, 280), clampy(y + dy, lo, 1380), desde=desde, dec=dec, dur=dur, size=size)

def tarjeta_resuelta(C, ctx, t):
    a0, s0, b0, fin = T("el aire sube") + 1.1, T("tu horno") - 0.4, T("te has acercado") - 0.3, T("sígueme")
    if t < a0 or t > fin: return
    m = C.ease((t - s0) / 0.45) if t < b0 else 1 - C.ease((t - b0) / 0.45)
    G, M = (C.W / 2, C.H * 0.22), (C.W * 0.21, C.H * 0.205)
    cx, cy = G[0] + (M[0] - G[0]) * m, G[1] + (M[1] - G[1]) * m
    C._tarjeta_cifra(ctx, cx, cy, 1 - 0.45 * m, "¿TE HAS ACERCADO?" if t >= b0 else "LA CIFRA", "200", "°C DE AIRE", C.GREEN,
                     alpha=min(1.0, (fin - t) / 0.3))

def overlay(ctx, t, A, C):
    C.cifra_juego(ctx, t, 200, "°C DE AIRE", T("a cuántos grados"), T("el aire sube"), T("el aire sube") + 1.45, grande=(C.W / 2, C.H * 0.22))
    tarjeta_resuelta(C, ctx, t)
    # rótulos de pieza (uno cada vez, nunca a la vez que una pastilla)
    C.rotulo(ctx, t, "FREIDORA DE AIRE", T("tu freidora no") + 0.2, T("es un horno"))
    C.rotulo(ctx, t, "HORNO", T("horno"), T("con turbo") - 0.05)
    C.rotulo(ctx, t, "TURBO", T("turbo"), T("arriba", 2) - 0.15)
    C.rotulo(ctx, t, "RESISTENCIA", T("resistencia"), T("mil setecientos") - 0.2)
    C.rotulo(ctx, t, "VENTILADOR", T("ventilador"), T("contra la comida") + 0.6)
    C.rotulo(ctx, t, "AGUA", T("el agua"), T("por eso se dora") - 0.2)
    C.rotulo(ctx, t, "CESTO CON AGUJEROS", T("el cesto"), T("pero llenas") - 0.2)
    C.rotulo(ctx, t, "PATATA", T("cada patata") + 0.1, T("las patatas se tapan") - 0.2)
    C.rotulo(ctx, t, "VAPOR", T("vapor"), T("y aquí viene") - 0.1)
    # cifras (con la del juego, 5 contadores)
    pastilla(C, ctx, t, 1700, "vatios", T("mil setecientos") - 0.1, T("un ventilador") - 0.25, A, "res", desde=0, dur=1.0)
    pastilla(C, ctx, t, 15, "min horno", T("de diez") - 0.1, T("tu freidora", 3) - 0.25, A, "horno", desde=10, dur=1.6)
    pastilla(C, ctx, t, 5, "min freidora", T("de tres") - 0.1, T("y si copias") - 0.25, A, "display", desde=3, dur=0.8)
    pastilla(C, ctx, t, -20, "°C", T("quince o") - 0.1, T("qué haces") - 0.25, A, "mando", desde=0, dur=1.2)
    # textos cortos y chispas
    p = win(t, T("pon una sola") + 0.2, T("y sacude") - 0.1)
    if p: x, y = A("cesto"); C.callout(ctx, "1 CAPA", clampx(x), clampy(y - 120, 560), p, size=72)
    x, y = A("res"); C.chispa(ctx, t, x, y, T("calienta") + 0.1, r=70, col=(1, 0.5, 0.3))
    x, y = A("cesto"); C.chispa(ctx, t, x, y, T("crujiente", fin=True) - 0.1, r=70)
    x, y = A("mando"); C.chispa(ctx, t, x, y, T("veinte grados", fin=True), r=60)

def sfx_events(C):
    # sin efectos dentro de las cifras dichas («mil setecientos vatios», «de veinte a doscientos», «de diez a quince», «de tres a cinco»,
    # «quince o veinte»): van al inicio de cada frase o en las pausas
    E = [(0.0, C.s_thud(), 0.45), (0.05, C.s_whoosh(), 0.35), (0.1, C.s_buzz(2.2), 0.12), (1.35, C.s_whoosh(), 0.25),
         (T("escribe") - 0.25, C.s_whoosh(), 0.3), (T("la llenas") - 0.2, C.s_pop(), 0.3), (T("y sale blanda"), C.s_fail(), 0.3),
         (T("tu freidora no") - 0.2, C.s_thud(), 0.4), (T("es un horno") - 0.2, C.s_whoosh(), 0.3), (T("turbo"), C.s_buzz(0.8), 0.15),
         (T("arriba", 2) - 0.2, C.s_whoosh(), 0.3), (T("calienta"), C.s_buzz(1.0), 0.15), (T("un ventilador") - 0.2, C.s_whoosh(), 0.35),
         (T("contra la comida") - 0.15, C.s_whoosh(0.7), 0.3), (T("ese aire") - 0.2, C.s_whoosh(), 0.3), (T("de la superficie"), C.s_pop(), 0.3),
         (T("por eso se dora") - 0.2, C.s_tick(), 0.4), (T("crujiente", fin=True), C.s_win(), 0.25), (T("por eso el cesto") - 0.2, C.s_clank(), 0.35),
         (T("pero llenas") - 0.2, C.s_pop(), 0.3), (T("cada patata") - 0.2, C.s_whoosh(), 0.3), (T("las patatas se tapan") - 0.2, C.s_thud(), 0.35),
         (T("así que el aire") - 0.2, C.s_fail(), 0.3), (T("se cuecen") - 0.2, C.s_buzz(1.2), 0.12), (T("y aquí viene") - 0.25, C.s_whoosh(), 0.35),
         (T("tu horno") - 0.25, C.s_whoosh(), 0.3), (T("tu freidora", 3) - 0.25, C.s_pop(), 0.3), (T("y si copias") - 0.25, C.s_whoosh(), 0.3),
         (T("baja") - 0.2, C.s_clank(), 0.35), (T("qué haces") - 0.2, C.s_whoosh(), 0.35), (T("pon una sola") - 0.2, C.s_pop(), 0.3),
         (T("y sacude") - 0.2, C.s_clank(), 0.35), (T("cocción", fin=True), C.s_bleep(520), 0.2), (T("te has acercado") - 0.25, C.s_whoosh(), 0.35),
         (T("y si quieres") - 0.25, C.s_whoosh(), 0.3), (T("lo más pedido") - 0.25, C.s_pop(), 0.3), (T("sígueme") - 0.25, C.s_whoosh(), 0.4),
         (T("y ahora ya sabes") - 0.25, C.s_whoosh(), 0.35), (T("la freidora de tu") - 0.3, C.s_thud(), 0.3)]
    E += [(T("a cuántos grados"), C.s_pop(), 0.4), (T("doscientos grados", fin=True) + 0.05, C.s_win(), 0.4)]   # sin tictac encima de la cifra dicha
    return E
