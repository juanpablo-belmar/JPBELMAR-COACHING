"""Stories del jueves 12 · Encuestas (§3 del borrador de Venta Perpetua).
Mismo sistema que las del martes: texto blanco grande, etiqueta ámbar girada y logo corto centrado.
Sin foto: fondo ónice con halo ámbar (láminas 1 a 3) y crema (lámina 4, como la 07 del martes).
El espacio del medio queda libre para el sticker de encuesta de Instagram.
Uso: python3 -I build_jueves_encuestas.py <carpeta_salida>
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
W, H, M = 1080, 1920, 90
AMBAR, ONICE, AZUL, CREMA, GRIS = (229, 169, 30), (10, 10, 10), (27, 58, 92), (244, 241, 234), (92, 92, 92)
B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
K = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
fB = ImageFont.truetype(B, 50); fBs = ImageFont.truetype(B, 44)
fS = ImageFont.truetype(K, 40); fT = ImageFont.truetype(K, 70); fN = ImageFont.truetype(K, 30)

def wrap(d, t, f, w):
    out, line = [], ""
    for p in t.split():
        s = (line + " " + p).strip()
        if d.textlength(s, font=f) <= w: line = s
        else: out.append(line); line = p
    out.append(line); return out

def fondo_onice(cx=0.78, cy=0.18):
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xs - cx * W) / W) ** 2 + ((ys - cy * H) / W) ** 2)
    t = np.clip(1 - r / 0.95, 0, 1) ** 2.2 * 0.42
    base = np.array([10, 10, 12], np.float32); amb = np.array(AMBAR, np.float32)
    a = base * (1 - t[..., None]) + amb * t[..., None]
    # vignette suave hacia abajo para que el sticker y el logo se lean
    v = np.clip((ys / H - 0.55) / 0.45, 0, 1)[..., None] * 0.5
    a = a * (1 - v) + base * v
    return Image.fromarray(a.astype(np.uint8))

def etiqueta(im, texto, x, y, rot=-3):
    d = ImageDraw.Draw(im); tw = d.textlength(texto, font=fS)
    st = Image.new("RGBA", (int(tw) + 70, 96), (0, 0, 0, 0)); ds = ImageDraw.Draw(st)
    ds.rounded_rectangle((0, 0, st.width - 1, 95), 48, fill=AMBAR + (255,)); ds.text((35, 22), texto, font=fS, fill=ONICE)
    st = st.rotate(rot, expand=True, resample=Image.BICUBIC); im.paste(st, (x, y), st)
    return st.height

def parrafos(im, bloques, y, color="white", f=fB, gap=24, lead=66):
    d = ImageDraw.Draw(im)
    for b in bloques:
        txt, col = (b if isinstance(b, tuple) else (b, color))
        for l in wrap(d, txt, f, W - 2 * M):
            d.text((M, y), l, font=f, fill=col); y += lead
        y += gap
    return y

def logo(im, claro=False):
    """Logo corto (logo-corto-blanco.svg): círculo, JPB y punto ámbar. Se dibuja al triple y se reduce."""
    k, s = 3, 72
    c = Image.new("RGBA", (140 * k, 140 * k), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    col = ONICE if claro else (255, 255, 255)
    d.ellipse((22 * k, 22 * k, 118 * k, 118 * k), outline=col, width=int(2.5 * k))
    f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40 * k)
    tw = d.textlength("JPB", font=f); d.text((70 * k - tw / 2, 50 * k), "JPB", font=f, fill=col)
    d.ellipse((66 * k, 98 * k, 74 * k, 106 * k), fill=AMBAR)
    c = c.resize((s, s), Image.LANCZOS); im.paste(c, ((W - s) // 2, H - 250), c)

def puntos(im, n, total=3, y=1480, claro=False):
    """Indicador de avance de la encuesta (1 de 3, 2 de 3...)."""
    d = ImageDraw.Draw(im); gap = 34; x0 = W // 2 - (total - 1) * gap // 2
    for i in range(total):
        x = x0 + i * gap; on = i < n
        d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=AMBAR if on else ((70, 70, 70) if not claro else (200, 196, 186)))

def guardar(im, nombre): im.save(os.path.join(OUT, nombre)); print("ok", nombre)

# 01 · Nicho
im = fondo_onice()
etiqueta(im, "Solo por curiosidad", M - 10, 300)
parrafos(im, ["¿Cuál te describe mejor?"], 440, f=fT, lead=84)
puntos(im, 1); logo(im); guardar(im, "01_encuesta_nicho.png")

# 02 · Años de trayectoria
im = fondo_onice(cx=0.22, cy=0.16)
etiqueta(im, "Pregunta 2", M - 10, 300)
parrafos(im, ["¿Cuántos años de trayectoria tienes?"], 440, f=fT, lead=84)
puntos(im, 2); logo(im); guardar(im, "02_encuesta_anios.png")

# 03 · Lo que más cuesta
im = fondo_onice(cx=0.8, cy=0.12)
etiqueta(im, "La última", M - 10, 300)
parrafos(im, ["¿Qué es lo que más te cuesta hoy?"], 440, f=fT, lead=84)
puntos(im, 3); logo(im); guardar(im, "03_encuesta_obstaculo.png")

# 04 · Invitación al recurso (crema, como la 07 del martes)
im = Image.new("RGB", (W, H), CREMA)
parrafos(im, [("Gracias por responder.", GRIS)], 620, f=fBs, lead=58)
y = parrafos(im, ["Si quieres las 3 preguntas que hay que responder antes de tocar tu CV,"], 700, color=ONICE, f=fT, lead=84)
h = etiqueta(im, "Responde PREGUNTAS", M - 10, y + 10)
parrafos(im, [("y te las mando.", AZUL)], y + h + 40, f=fB)
logo(im, claro=True); guardar(im, "04_invitacion_preguntas.png")
