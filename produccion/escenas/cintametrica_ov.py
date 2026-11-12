# Capa 2D de «La punta de tu cinta métrica está suelta a propósito»
# Pastillas previstas (motion → fotografía): metros encima de la punta; vueltas del muelle encima de la carcasa;
# metros en el aire encima del medio de la cinta; 1 mm junto al gancho; lectura de la medida arriba (H*0.30).
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("cintametrica")
SUB_ESTILO = "frase"
KEYWORDS = {"cinta", "métrica", "punta", "metal", "suelta", "defecto", "metros", "bolsillo", "acero", "enrollas", "muelle", "espiral",
            "zas", "plana", "palmo", "curvas", "teja", "curva", "rígida", "metro", "mesa", "gancho", "grosor", "milímetro", "pared",
            "suelto", "exacta", "marcas", "botón", "frena"}

def cota_h(ctx, t, a, b, x, y, w, col=(1, 0.82, 0.16)):
    """cota horizontal del grosor del gancho"""
    if t < a or t > b: return
    al = min(1, (t - a) / 0.25, (b - t) / 0.2)
    ctx.save(); ctx.set_line_width(7); ctx.set_source_rgba(*col, al)
    ctx.move_to(x - w / 2, y); ctx.line_to(x + w / 2, y); ctx.stroke()
    for xx in (x - w / 2, x + w / 2): ctx.move_to(xx, y - 26); ctx.line_to(xx, y + 26); ctx.stroke()
    ctx.restore()

def overlay(ctx, t, A, C):
    C.rotulo(ctx, t, "CINTA DE ACERO", T("una cinta fina"), T("una cinta fina") + 1.7)
    C.rotulo(ctx, t, "MUELLE EN ESPIRAL", T("un muelle"), T("un muelle") + 1.7)
    C.rotulo(ctx, t, "GANCHO", T("un gancho"), T("un gancho") + 1.5)
    C.rotulo(ctx, t, "BOTÓN DE FRENO", T("y un botón") + 0.3, T("y un botón") + 1.9)
    # varios metros
    x, y = A("punta")
    C.pastilla(ctx, t, 5, "metros", T("varios metros") - 0.2, T("así que haces"), clampx(x + 60, 300), clampy(y - 170, 470), desde=0, dur=1.6)
    # vueltas del muelle mientras sacas la cinta
    x, y = A("caja")
    a0, a1 = T("al sacar"), T("zas") + 0.6
    if a0 <= t < a1:
        u = min(1, max(0, (t - a0) / (T("más y más", fin=True) - a0)))
        if t > T("zas"): u = max(0, 1 - (t - T("zas")) / 0.3)
        C.pastilla(ctx, t, 4 + 4 * u, "vueltas", a0, a1, clampx(x, 300), clampy(y - 120, 470))
    C.chispa(ctx, t, *A("salida"), T("zas") + 0.25, r=80)
    # flecha de peso: la cinta plana cede
    x, y = A("medio")
    C.pastilla(ctx, t, 1.2, "m en el aire", T("y aguanta"), T("ahora necesitas"), clampx(x, 330), clampy(y - 160, 470), desde=0, dec=1, dur=1.2)
    # grosor del gancho
    x, y = A("tab")
    cota_h(ctx, t, T("pero el gancho"), T("y aquí viene"), x, y + 60, 110)
    C.pastilla(ctx, t, 1, "mm", T("más o menos") , T("y aquí viene"), clampx(x, 300), clampy(y + 150, 470, 1300), desde=0, dur=0.5)
    C.chispa(ctx, t, *A("punta"), T("un gancho") + 0.1, r=60)
    # lectura de la medida: con el gancho fijo falla 1 mm; suelto, acierta
    MX, MY = W * 0.5, H * 0.30
    C.pastilla(ctx, t, 999, "mm", T("el gancho te"), T("si empujas"), MX, MY, desde=1000, dur=0.8, size=80)
    C.pastilla(ctx, t, 1001, "mm", T("te lo sumaría"), T("así que lo dejas"), MX, MY, desde=1000, dur=0.8, size=80)
    x, y = A("tab")
    C.pastilla(ctx, t, 1, "mm fuera", T("sale un"), T("al empujar"), clampx(x - 40, 300), clampy(y + 150, 470, 1300), desde=0, dur=0.5)
    C.pastilla(ctx, t, 1, "mm dentro", T("entra un"), T("justo", fin=True) + 0.3, clampx(x - 40, 300), clampy(y + 150, 470, 1300), desde=0, dur=0.5)
    C.pastilla(ctx, t, 1000, "mm", T("la medida"), T("por eso al"), MX, MY, size=80)
    p = win(t, T("la medida") + 0.4, T("por eso al"))
    if p: C.badge(ctx, "EXACTA ×2", MX, MY + 130, p, C.GREEN, size=60)
    # primeras marcas que faltan
    x, y = A("punta")
    if T("faltan") <= t < T("y un botón"):
        C.callout(ctx, "SIN MARCAS", clampx(x + 160), clampy(y - 150, 470), win(t, T("faltan"), T("y un botón")), size=56)
    C.chispa(ctx, t, *A("boton"), T("y un botón") + 0.3, r=60)

def sfx_events(C):
    E = [(0.0, C.s_whoosh(0.7), 0.4), (0.05, C.s_buzz(1.3), 0.15), (T("esa pieza"), C.s_clank(), 0.4), (T("y no es"), C.s_pop(), 0.35),
         (T("vamos a"), C.s_whoosh(), 0.4), (T("vamos a") + 0.3, C.s_buzz(0.5), 0.2), (T("necesitas"), C.s_whoosh(), 0.35),
         (T("varios metros") - 0.4, C.s_tick(), 0.35), (T("así que haces"), C.s_pop(), 0.4), (T("la enrollas"), C.s_buzz(1.0), 0.2),
         (T("quién") , C.s_fail(), 0.35), (T("un muelle"), C.s_pop(), 0.45), (T("al sacar"), C.s_whoosh(), 0.35),
         (T("más y más") - 0.3, C.s_tick(), 0.35), (T("zas") - 0.05, C.s_whoosh(0.4), 0.5), (T("zas") + 0.25, C.s_clank(), 0.55),
         (T("pero una cinta"), C.s_whoosh(), 0.35), (T("un palmo"), C.s_fail(), 0.4), (T("así que la curvas"), C.s_pop(), 0.4),
         (T("rígida"), C.s_thud(), 0.4), (T("y aguanta"), C.s_tick(), 0.35), (T("más de un metro"), C.s_win(), 0.35),
         (T("ahora necesitas"), C.s_whoosh(), 0.35), (T("un gancho"), C.s_clank(), 0.5), (T("pero el gancho"), C.s_whoosh(), 0.3),
         (T("más o menos") - 0.3, C.s_bleep(660), 0.25), (T("y aquí viene"), C.s_whoosh(), 0.35), (T("el gancho te") , C.s_fail(), 0.4),
         (T("si empujas"), C.s_thud(), 0.45), (T("te lo sumaría"), C.s_fail(), 0.4), (T("así que lo dejas"), C.s_pop(), 0.4),
         (T("al tirar"), C.s_clank(), 0.4), (T("al empujar"), C.s_clank(), 0.4), (T("justo"), C.s_coin(), 0.4),
         (T("la medida") + 0.4, C.s_win(), 0.4), (T("por eso al"), C.s_whoosh(), 0.35), (T("y un botón") + 0.3, C.s_clank(), 0.5),
         (T("sígueme"), C.s_whoosh(), 0.4)]
    return E
