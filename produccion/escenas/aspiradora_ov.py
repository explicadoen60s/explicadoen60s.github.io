# Capa 2D de «Las aspas de tu aspiradora no chupan»
# Pastillas (motion → fotografía), tercio de arriba, lado derecho (mini del juego arriba-izquierda):
#  30.000 rpm sobre el ventilador (11,2-14,2) · 101 kPa sobre la boquilla, aire de fuera (34,5-36) · −14 % sobre el filtro
#  (41,7-44,9) · 50 % sobre el depósito (49-52). La revelación (81 kPa dentro) la hace la tarjeta del juego.
from _ovbase import *
from marcas import cargar
T, DUR = cargar("aspiradora")
SUB_ESTILO = "centro"
SUB_Y = 0.50
KEYWORDS = {"aspas", "aspiradora", "kilopascales", "presión", "motor", "ventilador", "treinta", "mil", "vueltas", "aire", "salida",
            "menos", "habitación", "empuja", "polvo", "boquilla", "empujan", "ochenta", "uno", "ciento", "filtro", "tres", "años",
            "catorce", "ciento", "depósito", "mitad", "empuje", "vacía", "lava"}

def pastilla(C, ctx, t, v, u, a, b, A, key, dx=0, dy=-150, desde=0, dec=0, dur=0.9, size=66, lo=560, hi=760):
    x, y = A(key); C.pastilla(ctx, t, v, u, a, b, clampx(x + dx, 360), clampy(y + dy, lo, hi), desde=desde, dec=dec, dur=dur, size=size)

def overlay(ctx, t, A, C):
    juego_completo(C, ctx, t, 81, "kPa DENTRO", T("a cuántos"), T("dentro baja"), T("te has acercado"), T("sígueme"), quedar=1.8)
    C.rotulo(ctx, t, "ASPAS", 0.2, 2.2)
    C.rotulo(ctx, t, "MOTOR", T("un motor"), T("el ventilador") - 0.05)
    C.rotulo(ctx, t, "VENTILADOR", T("el ventilador"), T("gira hasta") - 0.05)
    C.rotulo(ctx, t, "SALIDA", T("por la salida"), T("pero así") - 0.05)
    C.rotulo(ctx, t, "BOQUILLA", T("boquilla"), T("nada tira") - 0.05)
    C.rotulo(ctx, t, "FILTRO", T("mira el filtro"), T("si lleva") - 0.05)
    C.rotulo(ctx, t, "DEPÓSITO", T("con el depósito"), T("cuando llega") - 0.05)
    pastilla(C, ctx, t, 30000, "rpm", T("gira hasta"), T("cada vuelta") - 0.1, A, "fan", dx=200, dy=-260, desde=0, dur=1.8)
    pastilla(C, ctx, t, 101, "kPa fuera", T("frente a") - 0.1, T("pero ahora") - 0.1, A, "boq", dx=60, dy=-240, desde=0, dur=1.0)
    pastilla(C, ctx, t, -14, "% de aire", T("perdió") - 0.1, T("tu aspiradora rinde") - 0.1, A, "fil", dx=220, dy=-260, desde=0, dur=1.0)
    pastilla(C, ctx, t, 50, "% lleno", T("cuando llega"), T("más polvo") - 0.1, A, "dep", dx=230, dy=-260, desde=0, dur=1.0)
    x, y = A("dep"); C.chispa(ctx, t, x, y, T("vacía") + 0.4, r=70)
    x, y = A("fil"); C.chispa(ctx, t, x, y, T("y lava") + 0.3, r=60, col=(0.4, 1.0, 0.5))
    x, y = A("boq"); C.chispa(ctx, t, x, y, T("la empujan"), r=60)

def sfx_events(C):
    E = [(0.0, C.s_buzz(2.2), 0.15), (0.05, C.s_whoosh(), 0.35), (T("llevas años"), C.s_fail(), 0.3),
         (T("un motor"), C.s_buzz(1.6), 0.18), (T("gira hasta") - 0.3, C.s_tick(), 0.3), (T("cada vuelta"), C.s_whoosh(), 0.3),
         (T("por la salida"), C.s_whoosh(0.7), 0.3), (T("pero así"), C.s_pop(), 0.3), (T("menos aire significa"), C.s_bleep(320), 0.22),
         (T("así que el aire"), C.s_whoosh(), 0.35), (T("ese aire pesa"), C.s_thud(), 0.4), (T("y empuja el polvo"), C.s_whoosh(0.7), 0.3),
         (T("la empujan"), C.s_clank(), 0.35), (T("y aquí viene"), C.s_whoosh(), 0.35), (T("frente a") - 0.2, C.s_tick(), 0.3),
         (T("pero ahora"), C.s_whoosh(), 0.3), (T("si lleva"), C.s_buzz(1.0), 0.1), (T("perdió") - 0.2, C.s_fail(), 0.3),
         (T("tu aspiradora rinde"), C.s_buzz(1.2), 0.12), (T("con el depósito"), C.s_whoosh(), 0.3), (T("cuando llega"), C.s_pop(), 0.3),
         (T("más polvo"), C.s_bleep(300), 0.2), (T("así que no compres"), C.s_whoosh(), 0.35), (T("vacía") + 0.4, C.s_clank(), 0.4),
         (T("y lava") + 0.3, C.s_win(), 0.35), (T("te has acercado"), C.s_whoosh(), 0.35), (T("y si quieres"), C.s_whoosh(), 0.3),
         (T("lo más pedido"), C.s_pop(), 0.35), (T("sígueme"), C.s_whoosh(), 0.4), (T("así que ya sabes"), C.s_buzz(1.5), 0.15)]
    E += C.sfx_cifra(T("a cuántos"), T("dentro baja"))
    return E
