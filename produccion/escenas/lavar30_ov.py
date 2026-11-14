# Capa 2D de «¿Cuánta luz gasta tu lavadora solo calentando agua?»
# Experimento de motion (14-nov): 9 rótulos de pieza y 6 contadores como mucho, con la cifra del juego como el más grande.
# Pastillas (motion → fotografía): entran ≤0,3 s después del corte de su plano, como mucho 2 por plano, por debajo de y=560.
#  °C 15 → 60 sobre el termómetro (16,2) · 8 kg sobre el tambor (20) · kWh 0,33 → 1,5 sobre las barras / el contador (22,9-31,3)
#  62 kWh al año sobre el contador (42,8) · tarjeta del juego 80 % (revelación 33,1).
# Juego: la tarjeta no desaparece tras la revelación (queda en la esquina con la cifra en verde y vuelve en «¿Te has acercado?»).
from _ovbase import *
from marcas import cargar
T, DUR = cargar("lavar30")
SUB_ESTILO = "centro"
SUB_Y = 0.50
KEYWORDS = {"lavadora", "luz", "agua", "sesenta", "grados", "resistencia", "rojo", "motor", "carísimo", "ocho", "kilos",
            "algodón", "veinte", "cuatro", "cero", "coma", "treinta", "tres", "uno", "cinco", "kilovatios", "ochenta",
            "cuarenta", "sesenta", "dos", "toallas", "sábanas", "mando", "calentar", "desinfecta"}

def pastilla(C, ctx, t, v, u, a, b, A, key, dx=0, dy=-110, desde=None, dec=0, dur=0.9, size=62, lo=560):
    x, y = A(key); C.pastilla(ctx, t, v, u, a, b, clampx(x + dx, 280), clampy(y + dy, lo, 1380), desde=desde, dec=dec, dur=dur, size=size)

def tarjeta_resuelta(C, ctx, t):
    a0, b0, fin = T("casi todo") - 0.3, T("te has acercado") - 0.3, T("sígueme")
    if t < a0 or t > fin: return
    m = C.ease((t - a0) / 0.45) if t < b0 else 1 - C.ease((t - b0) / 0.45)
    G, M = (C.W / 2, C.H * 0.33), (C.W * 0.21, C.H * 0.205)
    cx, cy = G[0] + (M[0] - G[0]) * m, G[1] + (M[1] - G[1]) * m
    C._tarjeta_cifra(ctx, cx, cy, 1 - 0.45 * m, "¿TE HAS ACERCADO?" if m < 0.5 else "LA CIFRA", "80-85", "% EN CALENTAR AGUA", C.GREEN,
                     alpha=min(1.0, (fin - t) / 0.3))

def overlay(ctx, t, A, C):
    C.cifra_juego(ctx, t, 80, "% EN CALENTAR AGUA", T("cuánta luz"), T("entre el ochenta"), T("casi todo") - 0.3)
    tarjeta_resuelta(C, ctx, t)
    # rótulos de pieza (uno cada vez, nunca a la vez que una pastilla)
    C.rotulo(ctx, t, "MANDO", T("el mando") + 0.1, T("y eliges"))
    C.rotulo(ctx, t, "RESISTENCIA", T("resistencia"), T("bajo el agua"))
    C.rotulo(ctx, t, "AGUA", T("bajo el agua") + 0.2, T("el motor") - 0.2)
    C.rotulo(ctx, t, "MOTOR", T("el motor"), T("gira con poca") + 0.6)
    C.rotulo(ctx, t, "AGUA CALIENTE", T("pero calentar"), T("subir el agua") - 0.2)
    C.rotulo(ctx, t, "LAVADORA", T("mira una"), T("ocho") - 0.15)
    C.rotulo(ctx, t, "ALGODÓN", T("con algodón") + 0.1, T("de veinte") - 0.3)
    C.rotulo(ctx, t, "TOALLAS Y SÁBANAS", T("toallas"), T("qué haces") - 0.2)
    C.rotulo(ctx, t, "MANDO A 40", T("gira ahora"), T("mismo lavado") - 0.2)
    # cifras (con la del juego, 5 contadores)
    pastilla(C, ctx, t, 60, "°C", T("subir el agua") - 0.1, T("mira una") - 0.25, A, "termo", desde=15, dur=2.8)
    pastilla(C, ctx, t, 8, "kg", T("ocho") - 0.1, T("de veinte") - 0.25, A, "drum", desde=0, dur=0.6)
    pastilla(C, ctx, t, 0.33, "kWh a 20 °C", T("de veinte") - 0.1, T("y aquí viene") - 0.25, A, "bars", dx=-140, dy=-60, desde=0, dec=2, dur=0.8, size=54)
    pastilla(C, ctx, t, 1.5, "kWh a 60 °C", T("de cero coma") - 0.1, T("y aquí viene") - 0.25, A, "meter", desde=0.33, dec=2, dur=3.0)
    pastilla(C, ctx, t, 62, "kWh al año", T("ahorras") - 0.1, T("con cuatro") - 0.25, A, "meter", desde=0, dur=2.0)
    # textos cortos y chispas
    p = win(t, T("el gasto"), T("de cero coma") - 0.25)
    if p: x, y = A("bars"); C.callout(ctx, "×4", clampx(x), clampy(y - 90, 560), p, size=90)
    x, y = A("mando"); C.chispa(ctx, t, x, y, T("sesenta grados", fin=True), r=60)
    x, y = A("mando"); C.chispa(ctx, t, x, y, T("cuarenta", 2, fin=True), r=60)
    x, y = A("res"); C.chispa(ctx, t, x, y, T("al rojo", fin=True) - 0.1, r=70, col=(1, 0.5, 0.3))
    x, y = A("toalla"); C.chispa(ctx, t, x, y, T("desinfecta", fin=True), r=70)

def sfx_events(C):
    # sin efectos dentro de las cifras dichas: «sesenta grados», «ocho kilos», «de veinte a sesenta», «cuatro»,
    # «cero coma treinta y tres a uno coma cinco», «ochenta y cinco por ciento», «sesenta a cuarenta», «sesenta y dos», «cuatro coladas»
    E = [(0.0, C.s_thud(), 0.45), (0.05, C.s_clank(), 0.35), (0.1, C.s_buzz(1.5), 0.1), (1.55, C.s_whoosh(), 0.3),
         (T("escribe") - 0.25, C.s_whoosh(), 0.3), (T("giras") - 0.2, C.s_clank(), 0.4), (T("sesenta grados", fin=True) + 0.05, C.s_tick(), 0.4),
         (T("dentro") - 0.25, C.s_whoosh(), 0.3), (T("al rojo") - 0.1, C.s_buzz(1.2), 0.18), (T("el motor") - 0.25, C.s_whoosh(), 0.3),
         (T("gira con poca"), C.s_buzz(1.0), 0.1), (T("pero calentar") - 0.25, C.s_whoosh(), 0.3), (T("carísimo", fin=True), C.s_fail(), 0.3),
         (T("subir el agua") - 0.25, C.s_pop(), 0.3), (T("mira una") - 0.25, C.s_whoosh(), 0.3), (T("con algodón"), C.s_pop(), 0.3),
         (T("de veinte") - 0.3, C.s_whoosh(), 0.3), (T("de cero coma") - 0.3, C.s_pop(), 0.3), (T("y aquí viene") - 0.25, C.s_whoosh(), 0.35),
         (T("casi todo") - 0.25, C.s_whoosh(), 0.3), (T("si bajas") - 0.25, C.s_clank(), 0.35), (T("ahorras") - 0.25, C.s_pop(), 0.3),
         (T("pero y la") - 0.2, C.s_whoosh(), 0.3), (T("desinfecta", fin=True), C.s_win(), 0.25), (T("así que guarda") - 0.25, C.s_whoosh(), 0.3),
         (T("qué haces") - 0.2, C.s_whoosh(), 0.35), (T("gira ahora") - 0.2, C.s_clank(), 0.4), (T("cuarenta", 2, fin=True) + 0.05, C.s_tick(), 0.4),
         (T("mismo lavado") - 0.25, C.s_whoosh(), 0.3), (T("y menos luz"), C.s_coin(), 0.3), (T("te has acercado") - 0.25, C.s_whoosh(), 0.35),
         (T("y si quieres") - 0.25, C.s_whoosh(), 0.3), (T("lo más pedido") - 0.25, C.s_pop(), 0.3), (T("sígueme") - 0.25, C.s_whoosh(), 0.4),
         (T("y ahora ya sabes") - 0.25, C.s_whoosh(), 0.35), (T("tu lavadora calentando") - 0.3, C.s_clank(), 0.3)]
    E += [(T("cuánta luz"), C.s_pop(), 0.5), (T("calentar el agua", fin=True) + 0.05, C.s_win(), 0.4)]   # sin tictac encima de la cifra dicha
    return E
