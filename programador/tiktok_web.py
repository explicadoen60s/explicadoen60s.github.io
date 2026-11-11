"""Publica un vídeo en TikTok de verdad (no como borrador) usando TikTok Studio en un navegador, con tu sesión.

La API oficial solo deja mandar el vídeo a la bandeja: el último paso («Publicar») TikTok lo reserva a las
apps auditadas, y no audita apps para una sola cuenta. Así que aquí se hace lo mismo que harías tú:
abrir tiktok.com/tiktokstudio/upload, subir el archivo, escribir el texto y pulsar «Publicar».

La sesión sale del secreto de GitHub TT_SESSIONID (la cookie «sessionid» de tiktok.com) o, mejor aún,
TT_COOKIES (todas las cookies de tiktok.com exportadas en JSON con la extensión «Cookie-Editor»).
Si algo falla, publicar.py vuelve al método de siempre (bandeja + aviso)."""
import json, os, re, time
from pathlib import Path

URL_SUBIR = "https://www.tiktok.com/tiktokstudio/upload?from=webapp&lang=es"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/130.0.0.0 Safari/537.36")
CAPTURA = Path("/tmp/tiktok_fallo.png")


class SesionCaducada(RuntimeError):
    pass


class TrasPulsar(RuntimeError):
    """Error después de pulsar «Publicar»: el vídeo puede haber salido. No se reintenta."""


def hay_sesion():
    return bool(os.environ.get("TT_COOKIES", "").strip() or os.environ.get("TT_SESSIONID", "").strip())


def _cookies():
    crudo = os.environ.get("TT_COOKIES", "").strip()
    if crudo:
        out = []
        for c in json.loads(crudo):
            ss = {"no_restriction": "None", "lax": "Lax", "strict": "Strict"}.get(str(c.get("sameSite", "")).lower(), "Lax")
            k = {"name": c["name"], "value": c["value"], "domain": c.get("domain", ".tiktok.com"),
                 "path": c.get("path", "/"), "secure": bool(c.get("secure", True)), "httpOnly": bool(c.get("httpOnly", False)),
                 "sameSite": ss}
            if c.get("expirationDate"):
                k["expires"] = int(c["expirationDate"])
            out.append(k)
        return out
    sid = os.environ["TT_SESSIONID"].strip()
    return [{"name": n, "value": sid, "domain": ".tiktok.com", "path": "/", "secure": True, "httpOnly": True, "sameSite": "Lax"}
            for n in ("sessionid", "sessionid_ss", "sid_tt")]


def _cerrar_avisos(pg):
    """Cierra los carteles que TikTok pone encima (cookies, «novedades», comprobaciones automáticas)."""
    for txt in ("Aceptar todo", "Accept all", "Entendido", "Got it", "Ahora no", "Not now", "Omitir", "Skip"):
        try:
            b = pg.get_by_role("button", name=txt, exact=True)
            if b.count() and b.first.is_visible():
                b.first.click(timeout=2000)
        except Exception:
            pass


def _boton_publicar(pg):
    b = pg.locator('button[data-e2e="post_video_button"]')
    if b.count():
        return b.first
    return pg.get_by_role("button", name=re.compile(r"^(Publicar|Post)$")).last


def publicar_web(ruta, texto, oculto=True):
    from playwright.sync_api import sync_playwright
    CAPTURA.unlink(missing_ok=True)
    with sync_playwright() as p:
        try:
            nav = p.chromium.launch(channel="chrome", headless=oculto)
        except Exception:
            nav = p.chromium.launch(headless=oculto)
        ctx = nav.new_context(user_agent=UA, locale="es-ES", timezone_id="Europe/Madrid", viewport={"width": 1440, "height": 960})
        ctx.add_cookies(_cookies())
        pg = ctx.new_page()
        pulsado = False
        try:
            pg.goto(URL_SUBIR, wait_until="domcontentloaded", timeout=90000)
            pg.wait_for_timeout(6000)
            if "login" in pg.url or pg.locator('input[type="file"]').count() == 0 and pg.get_by_text(re.compile("Iniciar sesión|Log in")).count():
                raise SesionCaducada("La sesión de TikTok ha caducado: vuelve a copiar la cookie a GitHub (ver programador/LEEME.md).")
            pg.locator('input[type="file"]').first.set_input_files(str(ruta), timeout=60000)
            # espera a que termine la subida: el editor aparece y el botón «Publicar» se activa
            editor = pg.locator('div[contenteditable="true"]').first
            editor.wait_for(state="visible", timeout=180000)
            _cerrar_avisos(pg)
            fin = time.time() + 600
            while time.time() < fin:
                b = _boton_publicar(pg)
                if b.count() and b.is_enabled() and b.get_attribute("aria-disabled") not in ("true",) and b.get_attribute("data-disabled") not in ("true",):
                    if pg.get_by_text(re.compile(r"Subido|Uploaded|\b100\s?%")).count() or not pg.get_by_text(re.compile(r"Subiendo|Uploading")).count():
                        break
                pg.wait_for_timeout(3000)
            else:
                raise RuntimeError("TikTok no terminó de procesar el vídeo en 10 minutos")
            # texto: borra el nombre del archivo que TikTok pone solo y escribe el nuestro
            editor.click()
            pg.keyboard.press("Control+A"); pg.keyboard.press("Backspace")
            for i, trozo in enumerate(re.split(r"(#\w+)", texto)):
                if not trozo:
                    continue
                pg.keyboard.type(trozo, delay=15)
                if trozo.startswith("#"):
                    pg.wait_for_timeout(1500)
                    pg.keyboard.press("Escape")   # cierra la lista de sugerencias de hashtags
            pg.wait_for_timeout(1500)
            _cerrar_avisos(pg)
            b = _boton_publicar(pg)
            b.scroll_into_view_if_needed()
            b.click(timeout=20000)
            pulsado = True
            # a veces pregunta si publicar ya aunque la comprobación de contenido no haya terminado
            pg.wait_for_timeout(3000)
            for txt in ("Publicar ahora", "Post now", "Publicar", "Post"):
                c = pg.locator('div[role="dialog"]').get_by_role("button", name=txt, exact=True)
                if c.count() and c.first.is_visible():
                    c.first.click(timeout=5000); break
            fin = time.time() + 120
            while time.time() < fin:
                if "tiktokstudio/content" in pg.url or "/manage" in pg.url or pg.get_by_text(
                        re.compile(r"se ha publicado|se ha subido|has been (posted|uploaded)|publicado correctamente", re.I)).count():
                    return {"web": True, "confirmado": True}
                pg.wait_for_timeout(2000)
            pg.screenshot(path=str(CAPTURA), full_page=True)
            return {"web": True, "confirmado": False}
        except Exception as e:
            try:
                pg.screenshot(path=str(CAPTURA), full_page=True)
            except Exception:
                pass
            if pulsado:
                raise TrasPulsar(f"Error después de pulsar Publicar (puede que haya salido): {e}") from e
            raise
        finally:
            ctx.close(); nav.close()


if __name__ == "__main__":   # prueba manual: TT_SESSIONID=… python tiktok_web.py video.mp4 "texto #tag"
    import sys
    print(publicar_web(sys.argv[1], sys.argv[2], oculto="--ver" not in sys.argv))
