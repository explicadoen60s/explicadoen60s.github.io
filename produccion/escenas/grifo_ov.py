# Capa 2D de «Si tuvieras que inventar el grifo monomando…»
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("grifo")
SUB_Y = 0.72
SUB_ESTILO = "frase"
KEYWORDS = {"palanca", "fría", "caliente", "templada", "tuberías", "cincuenta", "grados", "llaves", "discos", "cerámica",
            "quieto", "tres", "agujeros", "mezcla", "coinciden", "pasa", "cinco", "bares", "dura", "lisa", "goma", "gotean",
            "subes", "hueco", "giras", "caudal", "temperatura", "salpica", "aireador", "aire", "doce", "seis"}

def sg(t, a, b):
    x = max(0.0, min(1.0, (t - a) / (b - a))); return x * x * (3 - 2 * x)

def keyed(t, keys):
    if t <= keys[0][0]: return keys[0][1]
    for (a, va), (b, vb) in zip(keys, keys[1:]):
        if a <= t <= b: return va + (vb - va) * sg(t, a, b)
    return keys[-1][1]

def tcol(v):
    u = max(0, min(1, (v - 15) / 37)); return (0.35 + 0.6 * u, 0.6 - 0.3 * u, 1.0 - 0.75 * u)

def overlay(ctx, t, A, C):
    Y, R, G, B = C.YL, C.RED, C.GREEN, (0.45, 0.8, 1.0)
    BY = H * 0.265
    if t < T("vamos a inventarlo"):
        rot = keyed(t, [(0, -0.9), (1.0, -0.9), (2.6, 0.9), (4.2, 0.0), (5.5, 0.1)]); v = 15 + 37 * (rot + 1) / 2
        C.badge(ctx, "%d °C" % round(v), W / 2, BY, win(t, 0.2, T("vamos a inventarlo")), tcol(v), size=96)
    if T("quieres agua") <= t < T("pero tienes"):
        C.badge(ctx, "38 °C", W / 2, BY, win(t, T("quieres agua"), T("pero tienes")), tcol(38), size=96)
    a0, a1 = T("pero tienes"), T("con dos llaves")
    label(C, ctx, t, T("una fría"), a1, "15 °C", A, "pc", dx=-60, dy=0, size=64)
    if T("que llega") <= t < a1:
        v = 15 + 37 * sg(t, T("que llega"), T("grados", fin=True))
        x, y = A("ph"); C.badge(ctx, "%d °C" % round(v), clampx(x + 60), clampy(y), win(t, T("que llega"), a1), tcol(v), size=72)
    a0, a1 = T("con dos llaves"), T("así que pones")
    if a0 <= t < a1:
        v = 33 + 17 * math.sin(t * 3.4)
        C.badge(ctx, "%d °C" % round(v), W / 2, BY, win(t, a0, a1), tcol(v), size=96)
        C.badge(ctx, "✗", W / 2, BY + 150, win(t, T("tardas"), a1), R, size=90)
    label(C, ctx, t, T("está quieto"), T("tiene tres"), "FIJO", A, "low", dx=0, dy=120, size=60)
    label(C, ctx, t, T("entra la fría"), T("el de arriba se mueve"), "FRÍA", A, "cold", dx=-60, dy=-120, size=56)
    label(C, ctx, t, T("entra la caliente"), T("el de arriba se mueve"), "CALIENTE", A, "hot", dx=60, dy=-120, size=56)
    label(C, ctx, t, T("y sale"), T("el de arriba se mueve"), "SALIDA", A, "out", dx=0, dy=130, size=56)
    if T("si los agujeros") <= t < T("pero el agua empuja"):
        C.badge(ctx, "0 L/MIN", W / 2, BY, win(t, T("el agua no"), T("pero el agua empuja")), R, size=86)
    a0, a1 = T("pero el agua empuja"), T("y aquí viene")
    if a0 <= t < a1:
        v = 5 * sg(t, a0, T("bares", fin=True)); C.badge(ctx, ("%.1f BAR" % v).replace(".", ","), W / 2, BY, win(t, a0, a1), R, size=90)
    if T("la cerámica") <= t < T("no hace falta"):
        C.badge(ctx, "0 GOTAS", W / 2, BY, win(t, T("no se cuela"), T("no hace falta")), G, size=80)
    label(C, ctx, t, T("no hace falta"), T("por eso los grifos"), "SIN GOMA", A, "ring", dx=0, dy=-120, size=64)
    if T("por eso los grifos") <= t < T("ahora", 3):
        C.badge(ctx, "✓", W / 2, BY, win(t, T("casi no gotean"), T("ahora", 3)), G, size=100)
    a0, a1 = T("ahora", 3), T("pero el chorro")
    if a0 <= t < a1:
        up = sg(t, T("si la subes"), T("el hueco crece", fin=True)) if t < T("si la giras") else 1.0
        C.badge(ctx, "%d L/MIN" % round(12 * up), W / 2, BY, win(t, a0, a1), B, size=84)
        if t >= T("si la giras"):
            rot = keyed(t, [(T("si la giras"), 0.0), (T("tapas un poco"), 0.0), (T("la caliente", 2, fin=True), -0.5), (T("destapas"), -0.5),
                            (T("la fría", 2, fin=True), -0.9), (T("solo la"), -0.9), (T("temperatura", fin=True), 0.1)])
            v = 15 + 37 * (rot + 1) / 2
            C.badge(ctx, "%d °C" % round(v), W / 2, BY + 150, win(t, T("si la giras"), a1), tcol(v), size=84)
    if T("pero el chorro") <= t < T("así que en la punta"):
        C.badge(ctx, "12 L/MIN", W / 2, BY, win(t, T("pero el chorro"), T("así que en la punta")), B, size=84)
    label(C, ctx, t, T("un aireador"), T("un grifo que", 2), "AIREADOR", A, "aer", dx=-200, dy=-80, size=60)
    a0, a1 = T("un grifo que", 2), T("sígueme")
    if a0 <= t < a1:
        v = 12 - 6 * sg(t, T("puede bajar"), T("a seis", fin=True))
        C.badge(ctx, "%d L/MIN" % round(v), W / 2, BY, win(t, a0, a1), G if v < 7 else B, size=90)

def sfx_events(C):
    E = [(0.2, C.s_whoosh(), 0.35), (0.3, C.s_buzz(5.5), 0.18), (T("vamos a inventarlo"), C.s_whoosh(), 0.45),
         (T("una fría"), C.s_pop(), 0.35), (T("y otra caliente"), C.s_pop(), 0.35), (T("cincuenta"), C.s_coin(), 0.4),
         (T("tardas"), C.s_fail(), 0.4), (T("así que pones"), C.s_whoosh(), 0.4), (T("del otro"), C.s_clank(), 0.5),
         (T("entra la fría"), C.s_pop(), 0.35), (T("entra la caliente"), C.s_pop(), 0.35), (T("y sale"), C.s_pop(), 0.35),
         (T("el de arriba se mueve"), C.s_clank(), 0.4), (T("el agua no"), C.s_fail(), 0.35), (T("cinco bares"), C.s_thud(), 0.5),
         (T("no se cuela"), C.s_win(), 0.35), (T("ninguna goma"), C.s_thud(), 0.4), (T("si la subes"), C.s_whoosh(), 0.35),
         (T("si la giras"), C.s_whoosh(), 0.35), (T("salpica"), C.s_buzz(1.6), 0.3), (T("un aireador"), C.s_pop(), 0.4),
         (T("a seis"), C.s_coin(), 0.4), (T("sígueme"), C.s_whoosh(), 0.4)]
    return E
