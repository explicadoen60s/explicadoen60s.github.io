# Capa 2D de «¿Y si te caes de un crucero?» (formato D, sin voz): rótulos en serif, pulso, cifras que cuentan,
# juego de la cifra (10 minutos de fuerza en los brazos), lluvia, relámpagos y sonido de ambiente.
import json, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
SUB_ESTILO = "ninguno"
SUB_Y = 0.5
KEYWORDS = []
ROT = [tuple(r) for r in json.load(open(os.path.join(HERE, "crucero_rotulos.json"), encoding="utf-8"))]

BPM = [(0, 92), (3, 104), (6, 138), (9.3, 168), (12, 184), (15, 179), (19, 160), (23, 171), (26.5, 177), (30, 184), (33, 178),
       (37, 170), (40.5, 168), (44, 176), (48, 160), (51.5, 171), (54.5, 150), (57.3, 140), (61.5, 150), (65, 126), (68.8, 108), (71, 96)]
ESTADO = [(0, "en cubierta"), (6, "caída"), (9.3, "choque por frío"), (19, "junto al casco"), (26.5, "la estela"), (33, "el barco se aleja"),
          (37, "hombre al agua"), (44, "fuerza en los brazos"), (54.5, "agarrado al aro"), (61.5, "rescate"), (68.8, "en cubierta")]
RELAMPAGOS = (1.2, 27.6, 46.2, 69.6)


def bpm(t):
    for (a, va), (b, vb) in zip(BPM, BPM[1:]):
        if a <= t <= b: return va + (vb - va) * (t - a) / (b - a)
    return BPM[-1][1]


def estado(t):
    e = ESTADO[0][1]
    for a, s in ESTADO:
        if t >= a: e = s
    return e


def overlay(ctx, t, A, C):
    W, H = C.W, C.H
    bajo_agua = 9.6 <= t < 15.0
    if bajo_agua: C.velo(ctx, 0.28 * min(1, (t - 9.6) / 0.3), (0.05, 0.25, 0.22))
    else: C.lluvia(ctx, t, 1.0 if t < 61.5 else 0.7)
    C.vineta(ctx, 0.6)
    for r in RELAMPAGOS:
        if 0 <= t - r < 0.25: C.velo(ctx, 0.35 * (1 - (t - r) / 0.25), (0.85, 0.9, 1.0))
    if 0 <= t - 9.3 < 0.35: C.velo(ctx, 0.75 * (1 - (t - 9.3) / 0.35))          # golpe contra el agua
    # cifras que cuentan: grandes, centradas debajo del rótulo (la tarjeta grande no sale en esos tramos)
    x, y, z = W / 2, H * 0.47, 110
    C.pastilla(ctx, t, 25, "m de caída", 6.0, 8.5, x, y, desde=0, dur=2.3, size=z)
    C.pastilla(ctx, t, 80, "km/h", 8.5, 11.5, x, y, desde=0, dur=0.8, size=z)
    C.pastilla(ctx, t, 14, "°C el agua", 11.5, 15.0, x, y, desde=20, dur=2.0, size=z)
    C.pastilla(ctx, t, 300, "m de casco", 19.0, 23.0, x, y, desde=0, dur=3.6, size=z)
    C.pastilla(ctx, t, 600, "m · en 1 min", 33.0, 37.0, x, y, desde=0, dur=3.8, size=z)
    C.pastilla(ctx, t, 900, "m", 37.0, 40.5, x, y, desde=600, dur=3.2, size=z)
    C.pastilla(ctx, t, 1000, "m para girar", 57.3, 61.5, x, y, desde=0, dur=3.8, size=z)
    C.pastilla(ctx, t, 1000 - 1000 * C.ease((t - 61.5) / 3.0), "m a la lancha", 61.5, 64.7, W * 0.32, H * 0.72, size=z)
    # fuerza en los brazos: barra verde→roja con el tiempo que baja de 10:00 a 0:00
    if 47.75 <= t < 51.5:
        al = min(1.0, (t - 47.75) / 0.2, (51.5 - t) / 0.2); u = max(0.0, (t - 48.2) / 3.1) ** 1.3; fr = 1 - u
        bx0, by0, bw = W / 2 - 300, H * 0.60, 600
        seg = 600 * fr; mm = int(seg // 60); ss_ = int(seg % 60)
        C.outlined(ctx, f"{mm:02d}:{ss_:02d} MIN", W / 2, by0 - 40, 64, fill=(1, 1, 1), stroke=10, alpha=al)
        C.rrect(ctx, bx0, by0, bw, 40, 20); ctx.set_source_rgba(0, 0, 0, 0.55 * al); ctx.fill()
        col = (0.25 + 0.7 * u, 0.85 - 0.6 * u, 0.3 - 0.1 * u)
        C.rrect(ctx, bx0 + 5, by0 + 5, max(0, (bw - 10) * fr), 30, 15); ctx.set_source_rgba(*col, al); ctx.fill()
        C.outlined(ctx, "FUERZA EN LOS BRAZOS", W / 2, by0 + 80, 34, fill=(1, 1, 1), stroke=7, alpha=al)
    # juego de la cifra
    C.cifra_juego(ctx, t, 10, "MIN DE FUERZA EN LOS BRAZOS", 3.0, 44.0, 47.7, grande=(W / 2, H * 0.55), mini=(W * 0.72, H * 0.205))
    C.cifra_juego(ctx, t, 10, "MIN DE FUERZA EN LOS BRAZOS", 64.6, 65.0, 67.2, grande=(W / 2, H * 0.55), mini=(W * 0.72, H * 0.205), dur_rev=0.6)
    # pulso y rótulos
    C.pulso(ctx, t, bpm(t), estado(t))
    grande = t < 3.0 or t >= 68.8
    C.rotulos_sim(ctx, t, ROT, y=H * 0.36, size=66 if grande else 56, rojo=C.YL, banda=True)


def sfx_events(C):
    E = []
    dur = ROT[-1][1]
    lluvia = C.s_lluvia(dur); olas = C.s_olas(dur)
    SR = C.SR
    for a, b in ((0.0, 9.6), (15.0, dur)):
        E.append((a, lluvia[int(a * SR):int(b * SR)], 0.22))
        E.append((a, olas[int(a * SR):int(b * SR)], 0.33 if a > 0 else 0.25))
    sub = C.s_sumergido(5.4)
    import numpy as np
    n = len(sub); f = np.minimum(1, np.arange(n) / (0.3 * SR)) * np.minimum(1, (n - np.arange(n)) / (0.3 * SR))
    E.append((9.6, sub * f, 0.5))
    E += [ev for ev in C.latidos(bpm, 0.0, dur) if not (9.6 <= ev[0] < 15.0)]
    E += [(ev[0], ev[1], 0.25) for ev in C.latidos(bpm, 9.6, 15.0)]
    E.append((9.3, C.s_chapuzon(1.2), 0.9)); E.append((9.3, C.s_thud(), 0.9))
    E.append((19.0, C.s_whoosh(), 0.35))
    E.append((37.0, C.s_bocina(1.6), 0.55)); E.append((38.9, C.s_bocina(1.2), 0.5))
    E.append((42.0, C.s_chapuzon(0.5), 0.6))
    E.append((61.5, C.s_motor(dur - 61.5), 0.4))
    for r in RELAMPAGOS:
        E.append((r + 0.4, C.s_thud(), 0.45)); E.append((r + 0.45, C.s_whoosh(1.4), 0.2))
    E += C.sfx_cifra(3.0, 44.0)
    E += C.sfx_cifra(64.6, 65.0)
    return E
