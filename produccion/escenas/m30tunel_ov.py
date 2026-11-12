# Capa 2D de «¿Cuántos metros de diámetro tenía la tuneladora de la M-30?» (Lo que esconde tu ciudad)
# Pastillas previstas (motion → fotografía), todas en el tercio de arriba y apartadas del eje de la pieza:
#  3.200 t sobre la máquina (34-37,6 s) · 5 pisos sobre el edificio de comparación (41-43,7 s) · 148 m sobre el tren
#  de remolques (44,5-46 s) · 46 m/día sobre la rueda (46,2-48,6 s) · 3,5 km arriba al centro (48,6-50,6 s)
#  · 3 carriles sobre la calzada del túnel (51-53 s). La tarjeta del juego (15,2 m) va arriba y se encoge a la esquina.
from _ovbase import *
from marcas import cargar
T, DUR = cargar("m30tunel")
SUB_ESTILO = "centro"
SUB_Y = 0.50
KEYWORDS = {"madrid", "eme", "treinta", "tierra", "metros", "diámetro", "tuneladora", "túnel", "río", "manzanares", "ruido", "humo",
            "coches", "ciudad", "mano", "lentísimo", "rueda", "cuchillas", "cinta", "brazos", "anillos", "hormigón", "paredes",
            "sur", "tres", "mil", "doscientas", "toneladas", "quince", "coma", "dos", "edificio", "cinco", "pisos", "ciento",
            "cuarenta", "ocho", "seis", "día", "kilómetros", "medio", "carriles", "parque", "tubo"}

def pastilla(C, ctx, t, v, u, a, b, A, key, dx=0, dy=-150, desde=0, dec=0, dur=0.9, size=66):
    x, y = A(key); C.pastilla(ctx, t, v, u, a, b, clampx(x + dx, 330), clampy(y + dy, 430, 640), desde=desde, dec=dec, dur=dur, size=size)

def overlay(ctx, t, A, C):
    C.cifra_juego(ctx, t, 15.2, "METROS DE DIÁMETRO", T("cuántos metros"), T("y su rueda"), T("sígueme"), dec=1)
    # rótulos de pieza (uno cada vez)
    C.rotulo(ctx, t, "M-30", T("la eme", 2), T("la eme", 2) + 1.5)
    C.rotulo(ctx, t, "RÍO MANZANARES", T("junto al río"), T("ruido") - 0.1)
    C.rotulo(ctx, t, "TUNELADORA", T("así que traes") + 0.3, T("delante") - 0.1)
    C.rotulo(ctx, t, "RUEDA DE CORTE", T("una rueda"), T("cuchillas") - 0.1)
    C.rotulo(ctx, t, "CUCHILLAS", T("cuchillas"), T("muerde") + 0.5)
    C.rotulo(ctx, t, "CINTA", T("y una cinta"), T("y una cinta") + 1.6)
    C.rotulo(ctx, t, "ANILLOS DE HORMIGÓN", T("anillos"), T("anillos") + 1.8)
    C.rotulo(ctx, t, "PARQUE", T("parque"), T("parque") + 1.4)
    # cifras
    pastilla(C, ctx, t, 3200, "toneladas", T("pesaba"), T("y su rueda"), A, "maquina", dx=140, dur=1.6)
    pastilla(C, ctx, t, 5, "pisos", T("más alta"), T("y de largo"), A, "edif", dy=-110, dur=0.9)
    pastilla(C, ctx, t, 148, "m de largo", T("ciento") - 0.1, T("avanzaba"), A, "tren", dur=1.2)
    pastilla(C, ctx, t, 46, "m al día", T("cuarenta y seis") - 0.1, T("así cavó"), A, "rueda", dx=-160, dur=1.0)
    C.pastilla(ctx, t, 3.5, "km de túnel", T("así cavó"), T("dentro"), W * 0.58, H * 0.27, desde=0, dec=1, dur=1.4, size=72)
    pastilla(C, ctx, t, 3, "carriles", T("cada tubo"), T("y arriba"), A, "tunel", dy=-170, dur=0.8)
    # ruido y golpes
    p = win(t, T("ruido"), T("así que decides"))
    if p:
        x, y = A("carretera"); C.callout(ctx, "¡BRRRUM!", clampx(x + 120, 340), clampy(y - 200, 430, 640), p, size=58)
    x, y = A("anillo")
    for k in range(3): C.chispa(ctx, t, x, y, T("colocan") + 0.7 * k, r=60)
    x, y = A("rueda"); C.chispa(ctx, t, x, y, T("muerde"), r=80)
    x, y = A("obrero"); C.chispa(ctx, t, x, y - 40, T("pero cavar") + 0.6, r=50); C.chispa(ctx, t, x, y - 40, T("es lentísimo"), r=50)

def sfx_events(C):
    E = [(0.0, C.s_whoosh(), 0.35), (0.05, C.s_buzz(1.6), 0.12), (T("bajo tierra"), C.s_whoosh(0.7), 0.4),
         (T("antes la"), C.s_whoosh(), 0.35), (T("junto al río"), C.s_pop(), 0.35), (T("ruido"), C.s_buzz(1.8), 0.2),
         (T("humo"), C.s_bleep(380), 0.2), (T("cortando"), C.s_fail(), 0.35), (T("así que decides"), C.s_whoosh(), 0.4),
         (T("meterla"), C.s_thud(), 0.45), (T("pero cavar") + 0.6, C.s_clank(), 0.3), (T("es lentísimo"), C.s_clank(), 0.3),
         (T("así que traes"), C.s_thud(), 0.5), (T("una rueda"), C.s_pop(), 0.4), (T("gira"), C.s_buzz(1.6), 0.15),
         (T("muerde"), C.s_clank(), 0.45), (T("y una cinta"), C.s_whoosh(), 0.3), (T("colocan"), C.s_clank(), 0.4),
         (T("colocan") + 0.7, C.s_clank(), 0.35), (T("colocan") + 1.4, C.s_clank(), 0.35), (T("así el túnel"), C.s_whoosh(), 0.3),
         (T("pesaba") - 0.3, C.s_thud(), 0.5), (T("y su rueda"), C.s_whoosh(), 0.35), (T("más alta"), C.s_pop(), 0.45),
         (T("y de largo"), C.s_whoosh(), 0.35), (T("avanzaba") - 0.3, C.s_tick(), 0.35), (T("así cavó") - 0.3, C.s_coin(), 0.4),
         (T("dentro"), C.s_whoosh(), 0.35), (T("cada tubo"), C.s_pop(), 0.4), (T("y arriba"), C.s_whoosh(), 0.35),
         (T("parque") - 0.3, C.s_win(), 0.35), (T("dime en"), C.s_bleep(620), 0.25), (T("y si quieres"), C.s_whoosh(), 0.3),
         (T("lo más pedido"), C.s_pop(), 0.35), (T("sígueme"), C.s_whoosh(), 0.4)]
    E += C.sfx_cifra(T("cuántos metros"), T("y su rueda"))
    return E
