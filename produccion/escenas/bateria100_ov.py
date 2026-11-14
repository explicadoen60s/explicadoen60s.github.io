# Capa 2D de «¿Cuánta batería pierde tu móvil lleno cada noche?»
# Pastillas (motion → fotografía), tercio de arriba, lado derecho (mini del juego arriba-izquierda):
#  % de carga sobre el móvil (0-15 s y 54-60 s, sube a 100 y baja a 80) · 365 noches (15,3-17,8) · 4,2 V sobre el voltímetro
#  (21-24,4) · 500 ciclos sobre la celda 1 (31,9-35,8) · 1.000 ciclos sobre la celda 2 (33,9-36) · 96 % sobre la barra 2
#  (44,4-46) · 60 % sobre la barra 1 (48,8-52). La revelación (20 % menos) la hace la tarjeta del juego.
from _ovbase import *
from marcas import cargar
T, DUR = cargar("bateria100")
SUB_ESTILO = "centro"
SUB_Y = 0.50
KEYWORDS = {"batería", "móvil", "lleno", "once", "dos", "cien", "trescientas", "sesenta", "cinco", "noches", "litio", "grafito",
            "tensión", "celda", "electrolito", "cuatro", "coma", "voltios", "quinientos", "ciclos", "mil", "veinte", "capacidad",
            "cuarenta", "calor", "grados", "tres", "meses", "almohada", "ajustes", "límite", "ochenta"}

def pastilla(C, ctx, t, v, u, a, b, A, key, dx=0, dy=-150, desde=0, dec=0, dur=0.9, size=66, lo=560, hi=760):
    x, y = A(key); C.pastilla(ctx, t, v, u, a, b, clampx(x + dx, 360), clampy(y + dy, lo, hi), desde=desde, dec=dec, dur=dur, size=size)

def overlay(ctx, t, A, C):
    juego_completo(C, ctx, t, 20, "% MENOS EN UN AÑO", T("cuánta batería"), T("una celda guardada"), T("te has acercado"), T("sígueme"))
    C.rotulo(ctx, t, "LITIO", T("el litio"), T("el grafito") - 0.05)
    C.rotulo(ctx, t, "GRAFITO", T("el grafito"), T("cuanto más") - 0.05)
    C.rotulo(ctx, t, "CELDA", T("la celda"), T("esa tensión") - 0.05)
    C.rotulo(ctx, t, "ELECTROLITO", T("el electrolito"), T("en laboratorio") - 0.05)
    C.rotulo(ctx, t, "LÍMITE DE CARGA", T("el límite"), T("te has acercado") - 0.3)
    pastilla(C, ctx, t, 100, "%", T("las dos"), T("y se queda") - 0.1, A, "movil", dx=170, dy=-200, desde=75, dur=1.8)
    pastilla(C, ctx, t, 365, "noches", T("trescientas") - 0.1, T("dentro,") - 0.1, A, "movil", dx=0, dy=-250, desde=0, dur=1.6)
    pastilla(C, ctx, t, 4.2, "V", T("más tensión"), T("esa tensión") + 1.0, A, "vm", dx=40, dy=-200, desde=3.7, dec=1, dur=1.4)
    pastilla(C, ctx, t, 500, "ciclos", T("aguanta"), T("y aquí viene") - 0.1, A, "celda", dx=0, dy=-120, desde=0, dur=1.2)
    pastilla(C, ctx, t, 1000, "ciclos", T("más de mil") - 0.1, T("y aquí viene") - 0.1, A, "celda2", dx=0, dy=-120, desde=0, dur=1.0)
    pastilla(C, ctx, t, 96, "%", T("pierde solo"), T("pero ojo") - 0.1, A, "barra2", dx=0, dy=-120, desde=100, dur=1.2)
    pastilla(C, ctx, t, 60, "%", T("al sesenta") - 0.1, T("así que no la") - 0.1, A, "barra1", dx=0, dy=-120, desde=80, dur=1.6)
    pastilla(C, ctx, t, 60, "°C", T("a sesenta"), T("una celda llena") + 0.6, A, "celda", dx=0, dy=-240, desde=20, dur=1.0)
    pastilla(C, ctx, t, 80, "% máx.", T("ochenta por") - 0.1, T("te has acercado") - 0.3, A, "movil", dx=170, dy=-220, desde=100, dur=1.0)
    p = win(t, T("lo enchufas"), T("a las dos") - 0.1)
    if p: x, y = A("movil"); C.callout(ctx, "23:00", clampx(x + 120, 330), clampy(y - 230, 560, 760), p, size=64)
    p = win(t, T("a las dos"), T("y se queda") - 0.1)
    if p: x, y = A("movil"); C.callout(ctx, "02:00", clampx(x - 150, 330), clampy(y - 230, 560, 760), p, size=64)
    x, y = A("movil"); C.chispa(ctx, t, x, y, T("lo enchufas") + 0.3, r=60); C.chispa(ctx, t, x, y, T("y activa") + 0.4, r=60, col=(0.4, 1.0, 0.5))
    x, y = A("grafito"); C.chispa(ctx, t, x, y, T("se aprieta"), r=70)

def sfx_events(C):
    E = [(0.0, C.s_buzz(1.5), 0.12), (0.05, C.s_whoosh(), 0.3), (T("lo enchufas") + 0.3, C.s_clank(), 0.4),
         (T("las dos") - 0.25, C.s_tick(), 0.3), (T("ya está al"), C.s_bleep(880), 0.25), (T("y se queda"), C.s_whoosh(), 0.3),
         (T("apretado"), C.s_buzz(1.0), 0.12), (T("trescientas") - 0.2, C.s_tick(), 0.3), (T("dentro,"), C.s_whoosh(), 0.3),
         (T("se aprieta"), C.s_thud(), 0.4), (T("cuanto más"), C.s_whoosh(), 0.3), (T("más tensión") - 0.2, C.s_tick(), 0.3),
         (T("esa tensión"), C.s_fail(), 0.3), (T("en laboratorio"), C.s_whoosh(), 0.35), (T("aguanta"), C.s_pop(), 0.35),
         (T("con cuatro") - 0.35, C.s_whoosh(), 0.3), (T("y aquí viene"), C.s_whoosh(0.8), 0.35), (T("guardada al"), C.s_whoosh(), 0.3),
         (T("pierde solo"), C.s_pop(), 0.35), (T("pero ojo"), C.s_bleep(320), 0.25), (T("una celda llena") + 0.5, C.s_fail(), 0.3),
         (T("así que no la"), C.s_whoosh(), 0.35), (T("almohada"), C.s_thud(), 0.4), (T("qué haces"), C.s_whoosh(), 0.3),
         (T("y activa") + 0.4, C.s_clank(), 0.35), (T("ochenta por") + 1.2, C.s_win(), 0.35), (T("te has acercado"), C.s_whoosh(), 0.35),
         (T("y si quieres"), C.s_whoosh(), 0.3), (T("lo más pedido"), C.s_pop(), 0.35), (T("sígueme"), C.s_whoosh(), 0.4),
         (T("y ahora ya sabes"), C.s_whoosh(), 0.35)]
    E += C.sfx_cifra(T("cuánta batería"), T("una celda guardada"))
    return E
