# Capa 2D de «Tu repetidor wifi puede cortarte la velocidad a la mitad» (Wifi, parte 2)
# Pastillas previstas (motion → fotografía): megas sobre el repetidor o el móvil (180 px encima de la pieza),
# % de señal sobre el móvil, ESCUCHA/HABLA junto a la radio, 2 viajes en el centro de arriba.
import math
from _ovbase import *
from marcas import cargar
T, DUR = cargar("repetidor")
SUB_ESTILO = "centro"
KEYWORDS = {"repetidor", "wifi", "pasillo", "velocidad", "mitad", "router", "ondas", "pared", "señal", "habitación", "móvil",
            "radio", "escuchar", "hablar", "datos", "canal", "turnos", "dos", "veces", "cien", "megas", "cincuenta", "débil",
            "intermedio", "fuerza", "trucos", "banda", "cable", "acceso", "entera", "uno"}

def overlay(ctx, t, A, C):
    # rótulos de pieza
    C.rotulo(ctx, t, "REPETIDOR", 0.2, 1.9)
    C.rotulo(ctx, t, "ROUTER", T("tu router"), T("tu router") + 1.5)
    C.rotulo(ctx, t, "REPETIDOR", T("así que pones") + 0.5, T("así que pones") + 2.0)
    C.rotulo(ctx, t, "RADIO", T("una sola"), T("una sola") + 1.6)
    C.rotulo(ctx, t, "DOBLE BANDA", T("un repetidor que") + 0.6, T("un repetidor que") + 2.2)
    C.rotulo(ctx, t, "PUNTO DE ACCESO", T("segundo punto"), T("segundo punto") + 1.6)
    C.rotulo(ctx, t, "CABLE", T("por el cable"), T("por el cable") + 1.3)
    # gancho: la velocidad cae a la mitad
    x, y = A("rep")
    C.pastilla(ctx, t, 50, "Mb/s", -0.3, T("vamos a ver"), clampx(x, 300), clampy(y - 140, 440), desde=100, dur=4.5)
    # señal en el móvil al pasar las paredes
    x, y = A("phone")
    C.pastilla(ctx, t, 10, "% señal", T("pero cada"), T("así que pones"), clampx(x, 300), clampy(y - 150, 440), desde=100, dur=4.0)
    C.pastilla(ctx, t, 70, "% señal", T("y la vuelve"), T("pero aquí"), clampx(x, 300), clampy(y - 150, 440), desde=10, dur=1.0)
    p = win(t, T("pero cada") + 0.3, T("en la habitación"))
    if p: x, y = A("pared"); C.callout(ctx, "PARED", clampx(x), clampy(y - 120, 420), p, size=58)
    # la radio: escucha o habla
    x, y = A("radio")
    if T("y una radio") < t < T("primero recibe"):
        lado = "ESCUCHA" if math.sin(t * 6) > 0 else "HABLA"
        C.callout(ctx, lado, clampx(x + 200, 320), clampy(y - 160, 440), win(t, T("y una radio"), T("primero recibe")), size=58)
    for a, b, txt in ((T("primero recibe"), T("luego se calla"), "ESCUCHA"), (T("y se los"), T("por el mismo"), "HABLA")):
        p = win(t, a, b)
        if p: x, y = A("radio"); C.callout(ctx, txt, clampx(x + 200, 320), clampy(y - 160, 440), p, size=58)
    # cada dato viaja dos veces
    C.pastilla(ctx, t, 2, "viajes por dato", T("así que cada"), T("si tenías"), W / 2, H * 0.31, desde=1, dur=1.4)
    # 100 → 50 megas
    x, y = A("phone")
    C.pastilla(ctx, t, 100, "Mb/s", T("si tenías"), T("cincuenta") - 0.1, clampx(x, 300), clampy(y - 150, 440), desde=0, dur=0.6)
    C.pastilla(ctx, t, 50, "Mb/s", T("cincuenta") - 0.1, T("y aquí viene"), clampx(x, 300), clampy(y - 150, 440), desde=100, dur=0.9)
    # mal sitio y punto intermedio
    x, y = A("rep")
    C.pastilla(ctx, t, 15, "% señal", T("el repetidor recibe"), T("entonces"), clampx(x, 300), clampy(y - 150, 440), desde=100, dur=1.2)
    C.pastilla(ctx, t, 80, "% señal", T("donde el wifi"), T("y si no"), clampx(x, 300), clampy(y - 150, 440), desde=15, dur=1.2)
    # doble banda y cable
    x, y = A("phone")
    C.pastilla(ctx, t, 95, "Mb/s", T("así no hay"), T("llevar la"), clampx(x, 300), clampy(y - 150, 440), desde=50, dur=1.0)
    C.pastilla(ctx, t, 97, "Mb/s", T("y la velocidad"), DUR, clampx(x, 300), clampy(y - 150, 440), desde=0, dur=1.2)
    x, y = A("rep")
    C.chispa(ctx, t, x, y + 60, T("así que pones") + 0.3, r=70)
    x, y = A("ap")
    C.chispa(ctx, t, x, y + 40, T("llevar la") + 1.0, r=60)

def sfx_events(C):
    E = [(0.0, C.s_whoosh(), 0.35), (0.05, C.s_buzz(2.4), 0.15), (T("a la mitad"), C.s_fail(), 0.45),
         (T("vamos a ver"), C.s_whoosh(), 0.35), (T("tu router"), C.s_pop(), 0.4), (T("lanza"), C.s_buzz(1.4), 0.2),
         (T("pero cada"), C.s_thud(), 0.45), (T("se come"), C.s_thud(), 0.4), (T("en la habitación"), C.s_whoosh(), 0.35),
         (T("apenas"), C.s_fail(), 0.4), (T("así que pones") + 0.3, C.s_clank(), 0.5), (T("recoge"), C.s_bleep(660), 0.25),
         (T("y la vuelve"), C.s_pop(), 0.45), (T("pero aquí"), C.s_whoosh(), 0.35), (T("una sola"), C.s_clank(), 0.4),
         (T("y una radio"), C.s_bleep(520), 0.25), (T("pero no las"), C.s_bleep(380), 0.25), (T("primero recibe"), C.s_whoosh(), 0.35),
         (T("luego se calla"), C.s_tick(), 0.4), (T("y se los"), C.s_whoosh(), 0.35), (T("por el mismo"), C.s_tick(), 0.35),
         (T("por turnos"), C.s_tick(), 0.35), (T("así que cada"), C.s_pop(), 0.4), (T("si tenías") - 0.3, C.s_coin(), 0.4),
         (T("en el mejor") , C.s_fail(), 0.4), (T("y aquí viene"), C.s_whoosh(), 0.35), (T("si lo pones"), C.s_whoosh(0.7), 0.35),
         (T("es todavía"), C.s_fail(), 0.4), (T("el repetidor recibe"), C.s_buzz(1.0), 0.15), (T("entonces"), C.s_pop(), 0.4),
         (T("en un punto"), C.s_whoosh(0.7), 0.35), (T("donde el wifi"), C.s_win(), 0.35), (T("y si no"), C.s_whoosh(), 0.35),
         (T("hay dos"), C.s_pop(), 0.4), (T("un repetidor que"), C.s_bleep(700), 0.25), (T("y contigo"), C.s_bleep(900), 0.25),
         (T("así no hay"), C.s_win(), 0.4), (T("llevar la"), C.s_whoosh(), 0.35), (T("llevar la") + 1.0, C.s_clank(), 0.45),
         (T("por el cable"), C.s_buzz(1.2), 0.15), (T("y la velocidad"), C.s_coin(), 0.45), (T("sígueme"), C.s_whoosh(), 0.4)]
    return E
