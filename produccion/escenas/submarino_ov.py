# Capa 2D de «Si tuvieras que inventar un submarino»
# Pastillas previstas (motion → fotografía): % de lastre sobre el tanque de proa; profundidad (m) y presión (atm) a los lados
# de la vela, en el tercio de arriba; % de los tanques de trimado encima de cada uno; % de lastre al vaciarse.
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("submarino")
SUB_ESTILO = "frase"
KEYWORDS = {"barco", "toneladas", "hunde", "submarino", "flota", "pesa", "agua", "tanques", "compuertas", "aire", "baja", "aprieta",
            "diez", "metros", "profundidad", "presión", "atmósfera", "trescientos", "treinta", "una", "casco", "tubo", "acero",
            "redondo", "pequeños", "delante", "detrás", "aletas", "motor", "botellas", "comprimido", "sube", "corcho", "soplido"}

def overlay(ctx, t, A, C):
    C.rotulo(ctx, t, "TANQUES DE LASTRE", T("tanques"), T("tanques") + 1.5)
    C.rotulo(ctx, t, "COMPUERTAS", T("unas compuertas"), T("unas compuertas") + 1.5)
    C.rotulo(ctx, t, "CASCO RESISTENTE", T("el casco"), T("el casco") + 1.8)
    C.rotulo(ctx, t, "TANQUES DE TRIMADO", T("tanques pequeños"), T("tanques pequeños") + 1.7)
    C.rotulo(ctx, t, "ALETAS", T("y aletas") + 0.1, T("y aletas") + 1.5)
    C.rotulo(ctx, t, "AIRE COMPRIMIDO", T("abres botellas"), T("abres botellas") + 1.6)
    C.rotulo(ctx, t, "HÉLICE", T("ningún motor"), T("ningún motor") + 1.4)
    # lastre que se llena
    x, y = A("proa")
    C.pastilla(ctx, t, 100, "% agua", T("abres unas"), T("y baja") + 0.3, clampx(x, 300), clampy(y - 170, 440), desde=0, dur=4.0, size=64)
    # profundidad y presión
    a0, a1 = T("pero cuanto"), T("así que el casco") + 0.4
    if a0 <= t < a1:
        prof = 0.0
        prof = 10 * min(1, max(0, (t - T("cada diez")) / 1.2))
        if t > T("a trescientos"): prof = 10 + 290 * min(1, max(0, (t - T("a trescientos")) / 1.0))
        atm = 1 + prof / 10
        C.pastilla(ctx, t, prof, "m", a0, a1, W * 0.30, H * 0.31)
        C.pastilla(ctx, t, atm, "atm", a0, a1, W * 0.70, H * 0.31)
    # trimado: delante y detrás
    if T("y mueves") <= t < T("y aletas"):
        f = 50
        u1 = min(1, max(0, (t - T("y mueves")) / (T("delante", fin=True) - T("y mueves"))))
        f = 50 + 35 * u1
        if t > T("detrás") - 0.2: f = 85 - 65 * min(1, (t - T("detrás") + 0.2) / 0.6)
        if t > T("hasta que"): f = 20 + 30 * min(1, (t - T("hasta que")) / 1.5)
        x, y = A("trimd"); C.pastilla(ctx, t, f, "%", T("y mueves"), T("y aletas"), clampx(x + 60, 300), clampy(y - 200, 440), size=58)
        x, y = A("trimt"); C.pastilla(ctx, t, 100 - f, "%", T("y mueves"), T("y aletas"), clampx(x - 60, 300), clampy(y - 200, 440), size=58)
    # lastre que se vacía
    x, y = A("proa")
    C.pastilla(ctx, t, 8, "% agua", T("el aire empuja"), T("el submarino pesa menos") + 0.4, clampx(x, 300), clampy(y - 170, 440),
               desde=100, dur=2.6, size=64)
    # chispas en compuertas y botellas
    x, y = A("compuerta"); C.chispa(ctx, t, x, y, T("abres unas") + 0.2, r=55)
    x, y = A("bot"); C.chispa(ctx, t, x, y, T("abres botellas") + 0.1, r=60)
    if T("ningún motor") <= t < T("abres botellas"):
        x, y = A("sub"); p = win(t, T("ningún motor"), T("abres botellas"))
        C.callout(ctx, "✗ MOTOR HACIA ARRIBA", W / 2, H * 0.30, p, size=56)

def sfx_events(C):
    E = [(0.0, C.s_whoosh(), 0.35), (0.2, C.s_buzz(2.4), 0.12), (1.5, C.s_pop(), 0.3), (T("y vuelve"), C.s_whoosh(), 0.35),
         (T("vamos a"), C.s_thud(), 0.45), (T("un barco flota"), C.s_pop(), 0.4), (T("para hundirlo"), C.s_whoosh(), 0.3),
         (T("tienes que"), C.s_thud(), 0.4), (T("así que le pones"), C.s_clank(), 0.45), (T("abres unas"), C.s_clank(), 0.5),
         (T("el agua entra"), C.s_buzz(1.2), 0.25), (T("y el aire sale"), C.s_whoosh(0.8), 0.35), (T("el submarino pesa más"), C.s_thud(), 0.45),
         (T("y baja"), C.s_whoosh(1.0), 0.35), (T("más aprieta"), C.s_fail(), 0.35), (T("cada diez") - 0.35, C.s_tick(), 0.4),
         (T("la presión sube"), C.s_pop(), 0.35), (T("a trescientos") - 0.35, C.s_tick(), 0.4), (T("son treinta") + 0.6, C.s_fail(), 0.35),
         (T("así que el casco"), C.s_clank(), 0.45), (T("un tubo redondo"), C.s_whoosh(), 0.35), (T("cómo te quedas"), C.s_bleep(440), 0.25),
         (T("tanques pequeños"), C.s_pop(), 0.4), (T("y mueves"), C.s_buzz(1.0), 0.2), (T("delante"), C.s_tick(), 0.35),
         (T("detrás"), C.s_tick(), 0.35), (T("ni sube"), C.s_win(), 0.35), (T("y aletas"), C.s_whoosh(), 0.35),
         (T("para inclinarlo"), C.s_buzz(1.2), 0.2), (T("y aquí viene"), C.s_whoosh(), 0.35), (T("ningún motor"), C.s_fail(), 0.4),
         (T("abres botellas"), C.s_clank(), 0.5), (T("el aire empuja"), C.s_whoosh(1.0), 0.4), (T("hacia fuera"), C.s_buzz(1.0), 0.25),
         (T("y sube solo"), C.s_whoosh(1.0), 0.4), (T("como un corcho"), C.s_coin(), 0.4), (T("suena ese"), C.s_buzz(1.6), 0.4),
         (T("soplido"), C.s_win(), 0.35), (T("sígueme"), C.s_whoosh(), 0.4)]
    return E
