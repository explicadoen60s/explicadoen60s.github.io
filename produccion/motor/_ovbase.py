W, H = 1080, 1920
def clampx(x, m=260): return max(m, min(W - m, x))
def clampy(y, lo=330, hi=1150): return max(lo, min(hi, y))
def win(t, a, b, fade=0.15):
    if t < a or t > b: return 0.0
    return min(1.0, (t - a) / 0.22) * min(1.0, (b - t) / fade)
def label(C, ctx, t, a, b, text, A, key, dx=0, dy=-220, size=68):
    p = win(t, a, b)
    if p:
        x, y = A(key); C.callout(ctx, text, clampx(x + dx), clampy(y + dy), p, size=size)
def badge(C, ctx, t, a, b, text, col, size=70):
    p = win(t, a, b)
    # con subtítulos en frase (arriba) los marcadores bajan para no pisarlos
    if p: C.badge(ctx, text, W / 2, H * (0.265 if getattr(C, "ESTILO_ACTUAL", "") == "frase" else 0.165), p, col, size=size)

def juego_completo(C, ctx, t, valor, unidad, t_preg, t_rev, t_acercado, t_fin, dec=0, quedar=2.6, **kw):
    """Tarjeta del juego de la cifra que no tapa la escena: sale con la pregunta, se encoge a la esquina, vuelve en la
    revelación, se queda `quedar` s y se va; reaparece grande (ya resuelta, en verde) en «¿Te has acercado?» hasta t_fin."""
    C.cifra_juego(ctx, t, valor, unidad, t_preg, t_rev, t_rev + C.__dict__.get("_DUR_REV", 1.1) + quedar, dec=dec, **kw)
    if t_acercado - 0.2 <= t <= t_fin:
        p = C.back(min(1.0, (t - t_acercado + 0.2) / 0.35)); a = min(1.0, (t_fin - t) / 0.3)
        g = kw.get("grande", (W / 2, H * 0.33))
        C._tarjeta_cifra(ctx, g[0], g[1], p, "¿TE HAS ACERCADO?", C.miles(valor, dec), unidad, C.GREEN, alpha=a)
