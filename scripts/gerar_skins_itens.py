#!/usr/bin/env python3
"""
Gerador do Resource Pack Oficial "Cinzas de Aurelion - Skins & Modelos de Itens" (Minecraft 26.3).

Gera 32 texturas Pixel-Art RPG (32x32 RGBA com sombreamento, brilho rúnico e contorno) e
modelos 3D calibrados ergonomicamente tanto para 1ª pessoa (firstperson_righthand/lefthand)
quanto para 3ª pessoa (thirdperson_righthand/lefthand, gui, ground e fixed).

Compatível com:
  - Novo pipeline de Itens do Minecraft 1.21.4+ / 26.3 (assets/minecraft/items/<item>.json)
  - Pipeline clássico de Overrides (assets/minecraft/models/item/<item>.json)

Uso:
  python3 scripts/gerar_skins_itens.py
Gera:
  resourcepack/aurelion_resourcepack.zip
  resourcepack/aurelion_resourcepack.sha1
"""
import hashlib
import json
import math
import os
import shutil
import struct
import zipfile
import zlib

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RP_DIR = os.path.join(ROOT, "resourcepack", "build")
ZIP_PATH = os.path.join(ROOT, "resourcepack", "aurelion_resourcepack.zip")
SHA_PATH = os.path.join(ROOT, "resourcepack", "aurelion_resourcepack.sha1")


# ============================================================================
#  GERADOR PNG RGBA PURO (Zero dependências externas)
# ============================================================================
def save_png(path, width, height, pixels):
    """Salva uma matriz (height x width) de tuplas (R, G, B, A) como arquivo PNG."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    raw_data = bytearray()
    for y in range(height):
        raw_data.append(0)  # filtro None
        for x in range(width):
            r, g, b, a = pixels[y][x]
            raw_data.extend((
                max(0, min(255, int(r))),
                max(0, min(255, int(g))),
                max(0, min(255, int(b))),
                max(0, min(255, int(a))),
            ))

    def chunk(tag, data):
        crc = zlib.crc32(tag + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", crc)

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    idat = zlib.compress(bytes(raw_data), 9)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


def new_canvas(w=32, h=32):
    return [[(0, 0, 0, 0) for _ in range(w)] for _ in range(h)]


def mix(c1, c2, t):
    return (
        int(c1[0] * (1 - t) + c2[0] * t),
        int(c1[1] * (1 - t) + c2[1] * t),
        int(c1[2] * (1 - t) + c2[2] * t),
        255,
    )


def lighten(c, amt=0.25):
    return mix(c, (255, 255, 255, 255), amt)


def darken(c, amt=0.30):
    return mix(c, (10, 10, 18, 255), amt)


def put(px, x, y, c):
    h = len(px)
    w = len(px[0])
    if 0 <= x < w and 0 <= y < h:
        px[y][x] = (c[0], c[1], c[2], c[3] if len(c) > 3 else 255)


def line(px, x0, y0, x1, y1, c, radius=0.0):
    steps = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1
    for i in range(steps + 1):
        t = i / max(1, steps)
        x = x0 + (x1 - x0) * t
        y = y0 + (y1 - y0) * t
        if radius <= 0.1:
            put(px, round(x), round(y), c)
        else:
            r_int = int(math.ceil(radius))
            for dy in range(-r_int, r_int + 1):
                for dx in range(-r_int, r_int + 1):
                    if dx * dx + dy * dy <= radius * radius + 0.25:
                        # Sombreamento cilíndrico automático (luz vindo do topo-esquerda)
                        shade = (dx - dy) / max(1.0, radius * 2.2)
                        col = lighten(c, max(0, -shade * 0.35)) if shade < 0 else darken(c, min(0.45, shade * 0.45))
                        put(px, round(x) + dx, round(y) + dy, col)


def disc(px, cx, cy, r, c_inner, c_outer=None):
    if c_outer is None:
        c_outer = darken(c_inner, 0.35)
    r_int = int(math.ceil(r))
    for dy in range(-r_int, r_int + 1):
        for dx in range(-r_int, r_int + 1):
            d = math.hypot(dx, dy)
            if d <= r:
                t = d / max(0.001, r)
                col = mix(c_inner, c_outer, t)
                put(px, round(cx) + dx, round(cy) + dy, col)


def poly(px, pts, c_base, c_edge=None):
    """Preenche um polígono com sombreamento direcional estilo pixel-art."""
    if c_edge is None:
        c_edge = lighten(c_base, 0.3)
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    min_x, max_x = max(0, int(min(xs))), min(len(px[0]) - 1, int(math.ceil(max(xs))))
    min_y, max_y = max(0, int(min(ys))), min(len(px) - 1, int(math.ceil(max(ys))))
    cx = sum(xs) / len(xs)
    cy = sum(ys) / len(ys)
    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            inside = False
            j = len(pts) - 1
            for i in range(len(pts)):
                xi, yi = pts[i]
                xj, yj = pts[j]
                if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-9) + xi):
                    inside = not inside
                j = i
            if inside:
                # Gradiente sutil topo-esquerda -> baixo-direita
                bias = ((x - cx) - (y - cy)) * 0.04
                col = lighten(c_base, min(0.35, -bias)) if bias < 0 else darken(c_base, min(0.35, bias))
                put(px, x, y, col)
    for i in range(len(pts)):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % len(pts)]
        line(px, x0, y0, x1, y1, c_edge, 0.0)


def apply_rpg_outline_and_shine(px, outline_tint=(18, 16, 26, 255), glow_points=()):
    """Adiciona contorno pixel-art 1px ao redor da silhueta e pontos de brilho rúnico."""
    h = len(px)
    w = len(px[0])
    out = [row[:] for row in px]
    for y in range(h):
        for x in range(w):
            if px[y][x][3] == 0:
                neighbors = []
                for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and px[ny][nx][3] > 0:
                        neighbors.append(px[ny][nx])
                if neighbors:
                    avg = (
                        sum(n[0] for n in neighbors) // len(neighbors),
                        sum(n[1] for n in neighbors) // len(neighbors),
                        sum(n[2] for n in neighbors) // len(neighbors),
                        255,
                    )
                    out[y][x] = mix(avg, outline_tint, 0.68)
    for gx, gy, gcol in glow_points:
        disc(out, gx, gy, 1.8, lighten(gcol, 0.55), gcol)
        put(out, round(gx), round(gy), (255, 255, 255, 255))
    return out


# ============================================================================
#  MATRIZES DE EXIBIÇÃO (DISPLAY) CALIBRADAS PARA 1ª E 3ª PESSOA
# ============================================================================
# Garantem que:
# - Em 1ª pessoa (quem segura): a arma/ferramenta fique em posição confortável
#   no canto inferior, sem obstruir a mira central e mostrando os detalhes da skin.
# - Em 3ª pessoa (quem olha o jogador): o cabo encaixe perfeitamente na mão do
#   personagem, na escala e inclinação corretas de cada categoria (cajado em pé,
#   adaga compacta, martelo/alabarda imponente, picareta equilibrada, mochila leve).

DISPLAY_PROFILES = {
    "tool_pick_scythe": {
        "thirdperson_righthand": {"rotation": [0, -90, 52], "translation": [0, 4.0, 0.5], "scale": [0.86, 0.86, 0.85]},
        "thirdperson_lefthand":  {"rotation": [0, 90, -52], "translation": [0, 4.0, 0.5], "scale": [0.86, 0.86, 0.85]},
        "firstperson_righthand": {"rotation": [0, -90, 24], "translation": [1.20, 2.8, 1.15], "scale": [0.66, 0.66, 0.66]},
        "firstperson_lefthand":  {"rotation": [0, 90, -24], "translation": [1.20, 2.8, 1.15], "scale": [0.66, 0.66, 0.66]},
        "gui":                   {"rotation": [0, 0, 0], "translation": [0, 0, 0], "scale": [1.0, 1.0, 1.0]},
        "ground":                {"rotation": [0, 0, 0], "translation": [0, 2.5, 0], "scale": [0.55, 0.55, 0.55]},
        "fixed":                 {"rotation": [0, 180, 0], "translation": [0, 0, 0], "scale": [1.0, 1.0, 1.0]},
    },
    "heavy_weapon": {
        "thirdperson_righthand": {"rotation": [0, -90, 50], "translation": [0, 5.2, 0.6], "scale": [1.02, 1.02, 0.92]},
        "thirdperson_lefthand":  {"rotation": [0, 90, -50], "translation": [0, 5.2, 0.6], "scale": [1.02, 1.02, 0.92]},
        "firstperson_righthand": {"rotation": [0, -90, 20], "translation": [1.28, 2.3, 1.20], "scale": [0.64, 0.64, 0.64]},
        "firstperson_lefthand":  {"rotation": [0, 90, -20], "translation": [1.28, 2.3, 1.20], "scale": [0.64, 0.64, 0.64]},
        "gui":                   {"rotation": [0, 0, 0], "translation": [0, 0, 0], "scale": [1.0, 1.0, 1.0]},
        "ground":                {"rotation": [0, 0, 0], "translation": [0, 2.8, 0], "scale": [0.60, 0.60, 0.60]},
        "fixed":                 {"rotation": [0, 180, 0], "translation": [0, 0, 0], "scale": [1.05, 1.05, 1.0]},
    },
    "staff": {
        "thirdperson_righthand": {"rotation": [0, -90, 35], "translation": [0, 4.8, 1.0], "scale": [0.95, 1.06, 0.90]},
        "thirdperson_lefthand":  {"rotation": [0, 90, -35], "translation": [0, 4.8, 1.0], "scale": [0.95, 1.06, 0.90]},
        "firstperson_righthand": {"rotation": [6, -85, 22], "translation": [1.35, 2.4, 1.15], "scale": [0.65, 0.72, 0.65]},
        "firstperson_lefthand":  {"rotation": [6, 85, -22], "translation": [1.35, 2.4, 1.15], "scale": [0.65, 0.72, 0.65]},
        "gui":                   {"rotation": [0, 0, 0], "translation": [0, 0, 0], "scale": [1.0, 1.0, 1.0]},
        "ground":                {"rotation": [0, 0, 0], "translation": [0, 2.8, 0], "scale": [0.58, 0.58, 0.58]},
        "fixed":                 {"rotation": [0, 180, 0], "translation": [0, 0, 0], "scale": [1.0, 1.0, 1.0]},
    },
    "dagger": {
        "thirdperson_righthand": {"rotation": [0, -90, 50], "translation": [0, 2.4, 0.6], "scale": [0.65, 0.65, 0.65]},
        "thirdperson_lefthand":  {"rotation": [0, 90, -50], "translation": [0, 2.4, 0.6], "scale": [0.65, 0.65, 0.65]},
        "firstperson_righthand": {"rotation": [0, -90, 32], "translation": [1.15, 3.1, 1.15], "scale": [0.54, 0.54, 0.54]},
        "firstperson_lefthand":  {"rotation": [0, 90, -32], "translation": [1.15, 3.1, 1.15], "scale": [0.54, 0.54, 0.54]},
        "gui":                   {"rotation": [0, 0, 0], "translation": [0, 0, 0], "scale": [0.95, 0.95, 0.95]},
        "ground":                {"rotation": [0, 0, 0], "translation": [0, 2.0, 0], "scale": [0.48, 0.48, 0.48]},
        "fixed":                 {"rotation": [0, 180, 0], "translation": [0, 0, 0], "scale": [0.90, 0.90, 0.90]},
    },
    "sword": {
        "thirdperson_righthand": {"rotation": [0, -90, 55], "translation": [0, 4.2, 0.5], "scale": [0.88, 0.88, 0.85]},
        "thirdperson_lefthand":  {"rotation": [0, 90, -55], "translation": [0, 4.2, 0.5], "scale": [0.88, 0.88, 0.85]},
        "firstperson_righthand": {"rotation": [0, -90, 25], "translation": [1.15, 3.0, 1.13], "scale": [0.66, 0.66, 0.66]},
        "firstperson_lefthand":  {"rotation": [0, 90, -25], "translation": [1.15, 3.0, 1.13], "scale": [0.66, 0.66, 0.66]},
        "gui":                   {"rotation": [0, 0, 0], "translation": [0, 0, 0], "scale": [1.0, 1.0, 1.0]},
        "ground":                {"rotation": [0, 0, 0], "translation": [0, 2.5, 0], "scale": [0.55, 0.55, 0.55]},
        "fixed":                 {"rotation": [0, 180, 0], "translation": [0, 0, 0], "scale": [1.0, 1.0, 1.0]},
    },
    "ranged_bow": {
        "thirdperson_righthand": {"rotation": [-80, 260, -40], "translation": [-1, -2, 2.5], "scale": [0.9, 0.9, 0.9]},
        "thirdperson_lefthand":  {"rotation": [-80, -280, 40], "translation": [-1, -2, 2.5], "scale": [0.9, 0.9, 0.9]},
        "firstperson_righthand": {"rotation": [0, -90, 25], "translation": [1.13, 3.2, 1.13], "scale": [0.66, 0.66, 0.66]},
        "firstperson_lefthand":  {"rotation": [0, 90, -25], "translation": [1.13, 3.2, 1.13], "scale": [0.66, 0.66, 0.66]},
        "gui":                   {"rotation": [0, 0, 0], "translation": [0, 0, 0], "scale": [1.0, 1.0, 1.0]},
        "ground":                {"rotation": [0, 0, 0], "translation": [0, 2.2, 0], "scale": [0.55, 0.55, 0.55]},
        "fixed":                 {"rotation": [0, 180, 0], "translation": [0, 0, 0], "scale": [1.0, 1.0, 1.0]},
    },
    "ranged_crossbow": {
        "thirdperson_righthand": {"rotation": [-90, 0, -60], "translation": [2, 0.1, -3], "scale": [0.9, 0.9, 0.9]},
        "thirdperson_lefthand":  {"rotation": [-90, 0, 30], "translation": [2, 0.1, -3], "scale": [0.9, 0.9, 0.9]},
        "firstperson_righthand": {"rotation": [-90, 0, -55], "translation": [1.13, 3.2, 1.13], "scale": [0.66, 0.66, 0.66]},
        "firstperson_lefthand":  {"rotation": [-90, 0, 35], "translation": [1.13, 3.2, 1.13], "scale": [0.66, 0.66, 0.66]},
        "gui":                   {"rotation": [0, 0, 0], "translation": [0, 0, 0], "scale": [1.0, 1.0, 1.0]},
        "ground":                {"rotation": [0, 0, 0], "translation": [0, 2.2, 0], "scale": [0.55, 0.55, 0.55]},
        "fixed":                 {"rotation": [0, 180, 0], "translation": [0, 0, 0], "scale": [1.0, 1.0, 1.0]},
    },
    "tome_artifact": {
        "thirdperson_righthand": {"rotation": [55, 0, 0], "translation": [0, 2.5, 1.5], "scale": [0.52, 0.52, 0.52]},
        "thirdperson_lefthand":  {"rotation": [55, 0, 0], "translation": [0, 2.5, 1.5], "scale": [0.52, 0.52, 0.52]},
        "firstperson_righthand": {"rotation": [8, -28, -8], "translation": [1.25, 2.3, 1.20], "scale": [0.52, 0.52, 0.52]},
        "firstperson_lefthand":  {"rotation": [8, 152, 8], "translation": [1.25, 2.3, 1.20], "scale": [0.52, 0.52, 0.52]},
        "gui":                   {"rotation": [0, 0, 0], "translation": [0, 0, 0], "scale": [0.95, 0.95, 0.95]},
        "ground":                {"rotation": [0, 0, 0], "translation": [0, 2.0, 0], "scale": [0.50, 0.50, 0.50]},
        "fixed":                 {"rotation": [0, 180, 0], "translation": [0, 0, 0], "scale": [0.95, 0.95, 0.95]},
    },
}


# ============================================================================
#  DESENHO DE CADA SKIN PIXEL-ART 32x32 (SILHUETA + CORES ÚNICAS)
# ============================================================================
def draw_pickaxe(style):
    px = new_canvas()
    if style == "tectonica":
        # Cabo de ferro escuro com anéis dourados + cabeça pesada de ouro tectônico e núcleo ciano
        handle_c = (78, 65, 58, 255)
        gold_c = (235, 180, 45, 255)
        blade_c = (130, 145, 165, 255)
        core_c = (55, 235, 255, 255)
        line(px, 4, 27, 23, 8, handle_c, 1.4)
        for t in (6, 10, 14, 18):
            line(px, t, 31 - t, t + 1, 30 - t, gold_c, 1.5)
        # Cabeça tectônica dupla larga
        poly(px, [(14, 5), (25, 4), (28, 7), (27, 18), (24, 15), (21, 9), (16, 8)], blade_c, gold_c)
        poly(px, [(16, 6), (24, 5), (27, 8), (25, 16), (22, 10)], gold_c, lighten(gold_c, 0.4))
        disc(px, 22, 9, 2.6, core_c, (20, 130, 180, 255))
        return apply_rpg_outline_and_shine(px, glow_points=[(22, 9, core_c), (4, 27, gold_c)])

    if style == "fornalha":
        # Picareta vulcânica negra com veios de lava incandescente e pontas curvas de rubi/magma
        handle_c = (45, 32, 38, 255)
        obs_c = (65, 45, 75, 255)
        lava_c = (255, 110, 20, 255)
        yellow_c = (255, 225, 70, 255)
        line(px, 4, 27, 23, 8, handle_c, 1.3)
        poly(px, [(12, 6), (23, 3), (29, 9), (26, 20), (23, 14), (18, 9)], obs_c, lava_c)
        line(px, 14, 6, 24, 6, lava_c, 1.1)
        line(px, 26, 8, 25, 18, lava_c, 1.1)
        disc(px, 22, 9, 2.5, yellow_c, lava_c)
        return apply_rpg_outline_and_shine(px, (30, 10, 10, 255), [(22, 9, yellow_c), (15, 6, lava_c), (25, 16, lava_c)])

    # picareta_ferreiro (Korvan)
    handle_c = (90, 50, 35, 255)
    nether_c = (75, 65, 72, 255)
    fire_c = (255, 85, 30, 255)
    line(px, 4, 27, 24, 7, handle_c, 1.4)
    poly(px, [(13, 4), (25, 3), (29, 7), (28, 19), (24, 15), (20, 8)], nether_c, fire_c)
    disc(px, 23, 8, 2.2, fire_c)
    return apply_rpg_outline_and_shine(px, glow_points=[(23, 8, fire_c)])


def draw_axe_or_hammer(style):
    px = new_canvas()
    if style == "lenhador":
        # Machado druídico de madeira viva + lâmina prateada larga + vinhas esmeralda
        wood_c = (115, 75, 42, 255)
        vine_c = (45, 205, 85, 255)
        blade_c = (180, 215, 220, 255)
        line(px, 4, 27, 25, 6, wood_c, 1.5)
        # Lâmina barbada grande
        poly(px, [(15, 5), (25, 4), (29, 10), (26, 19), (19, 16), (20, 10)], blade_c, lighten(blade_c, 0.4))
        # Vinhas luminosas
        line(px, 8, 23, 18, 13, vine_c, 0.9)
        disc(px, 22, 10, 2.2, (80, 255, 120, 255), vine_c)
        return apply_rpg_outline_and_shine(px, glow_points=[(22, 10, vine_c), (4, 27, vine_c)])

    if style == "martelo_magma":
        # Martelo de guerra colossal de duas faces com núcleo de magma
        handle_c = (58, 42, 38, 255)
        head_c = (70, 62, 68, 255)
        magma_c = (255, 115, 25, 255)
        line(px, 4, 27, 24, 7, handle_c, 1.6)
        # Cabeça retangular dupla de marreta
        poly(px, [(13, 6), (20, 2), (29, 11), (22, 18)], head_c, magma_c)
        line(px, 16, 6, 25, 15, magma_c, 1.4)
        disc(px, 21, 10, 2.6, (255, 230, 80, 255), magma_c)
        return apply_rpg_outline_and_shine(px, (28, 12, 10, 255), [(21, 10, magma_c), (16, 6, magma_c), (25, 14, magma_c)])

    if style == "berserker":
        # Destruidor do Berserker: Machado Duplo Sanguinário dentado
        handle_c = (65, 30, 30, 255)
        dark_iron = (55, 50, 58, 255)
        blood_c = (220, 30, 45, 255)
        line(px, 4, 27, 25, 6, handle_c, 1.5)
        poly(px, [(12, 8), (19, 2), (25, 5), (29, 12), (23, 19), (16, 13)], dark_iron, blood_c)
        poly(px, [(10, 11), (15, 4), (19, 9)], blood_c, lighten(blood_c, 0.3))
        poly(px, [(21, 13), (28, 10), (24, 18)], blood_c, lighten(blood_c, 0.3))
        disc(px, 20, 10, 2.3, (255, 70, 70, 255), blood_c)
        return apply_rpg_outline_and_shine(px, (30, 8, 12, 255), [(20, 10, blood_c)])

    if style == "alabarda_solar":
        # Alabarda real dourada com ponta de lança + lâmina de sol radiante
        shaft_c = (150, 105, 45, 255)
        gold_c = (255, 205, 55, 255)
        sun_c = (255, 250, 170, 255)
        line(px, 3, 28, 24, 7, shaft_c, 1.3)
        # Ponta de lança no topo-direito
        poly(px, [(22, 9), (30, 1), (27, 10)], sun_c, gold_c)
        # Lâmina crescente solar e contrapeso
        poly(px, [(14, 7), (22, 3), (28, 11), (24, 18), (18, 13)], gold_c, sun_c)
        disc(px, 21, 10, 2.8, sun_c, (255, 150, 30, 255))
        return apply_rpg_outline_and_shine(px, (40, 25, 10, 255), [(21, 10, sun_c), (28, 3, sun_c)])

    # machado_thorgar
    line(px, 4, 27, 24, 7, (95, 55, 35, 255), 1.5)
    poly(px, [(14, 5), (24, 3), (29, 11), (23, 18), (18, 12)], (140, 140, 150, 255), (200, 40, 40, 255))
    return apply_rpg_outline_and_shine(px, glow_points=[(21, 10, (220, 40, 40, 255))])


def draw_scythe():
    # Foicinha da Colheita Dourada: Foice curva larga de luz dourada e esmeralda
    px = new_canvas()
    wood_c = (125, 80, 40, 255)
    gold_c = (250, 205, 50, 255)
    emerald_c = (60, 230, 115, 255)
    line(px, 5, 27, 22, 10, wood_c, 1.3)
    # Lâmina de foice bem arqueada (silhueta inconfundível)
    poly(px, [(10, 7), (19, 3), (28, 5), (25, 11), (18, 9), (11, 11)], gold_c, lighten(gold_c, 0.45))
    disc(px, 21, 9, 2.2, emerald_c, (25, 140, 70, 255))
    return apply_rpg_outline_and_shine(px, glow_points=[(21, 9, emerald_c), (12, 8, gold_c)])


def draw_grappling_hook():
    # Arpéu de Escalada: Lançador com carretel azul-ciano e garra tripla de mithril no topo
    px = new_canvas()
    wood_c = (95, 65, 45, 255)
    mithril_c = (170, 230, 245, 255)
    rope_c = (65, 185, 220, 255)
    line(px, 5, 26, 21, 10, wood_c, 1.4)
    disc(px, 12, 19, 3.2, rope_c, (35, 110, 150, 255))
    # Garra tripla de arpéu no topo-direito
    line(px, 20, 11, 28, 3, mithril_c, 1.2)
    line(px, 23, 8, 16, 4, mithril_c, 1.1)
    line(px, 23, 8, 27, 15, mithril_c, 1.1)
    line(px, 26, 5, 20, 2, mithril_c, 1.0)
    line(px, 26, 5, 29, 11, mithril_c, 1.0)
    return apply_rpg_outline_and_shine(px, glow_points=[(12, 19, rope_c), (26, 5, mithril_c)])


def draw_staff(style):
    px = new_canvas()
    if style == "inverno":
        # Cajado do Inverno Eterno: Haste prateada + coroa de gelo + cristal glacial flutuante
        shaft_c = (140, 175, 205, 255)
        ice_c = (110, 225, 255, 255)
        core_c = (210, 250, 255, 255)
        line(px, 4, 27, 21, 10, shaft_c, 1.3)
        # Chifres de cristal de gelo envolvendo o orbe
        poly(px, [(16, 9), (18, 3), (23, 2), (20, 8)], ice_c, core_c)
        poly(px, [(22, 15), (28, 13), (29, 8), (23, 11)], ice_c, core_c)
        disc(px, 24, 7, 3.4, core_c, (55, 170, 240, 255))
        return apply_rpg_outline_and_shine(px, (15, 35, 65, 255), [(24, 7, core_c), (19, 4, ice_c), (27, 12, ice_c)])

    if style == "singularidade":
        # Cetro da Singularidade: Haste negra e ouro + anel gravitacional + buraco negro roxo
        shaft_c = (55, 42, 72, 255)
        gold_c = (235, 185, 55, 255)
        void_c = (175, 65, 255, 255)
        line(px, 4, 27, 20, 11, shaft_c, 1.3)
        for t in (7, 12, 17):
            put(px, t, 31 - t, gold_c)
        # Anel de acreção e singularidade escura no centro
        disc(px, 23, 8, 5.2, void_c, (75, 20, 130, 255))
        disc(px, 23, 8, 2.8, (15, 5, 28, 255), (90, 25, 160, 255))
        line(px, 17, 6, 29, 10, (240, 170, 255, 255), 0.8)
        return apply_rpg_outline_and_shine(px, (20, 8, 38, 255), [(18, 6, void_c), (28, 10, void_c)])

    # cajado_morvath (Necromante)
    line(px, 4, 27, 21, 10, (70, 65, 60, 255), 1.3)
    disc(px, 23, 8, 4.0, (220, 220, 205, 255), (140, 135, 120, 255))
    disc(px, 22, 7, 1.3, (50, 255, 140, 255))
    disc(px, 25, 9, 1.3, (50, 255, 140, 255))
    return apply_rpg_outline_and_shine(px, glow_points=[(22, 7, (50, 255, 140, 255))])


def draw_sword_or_dagger(style):
    px = new_canvas()
    if style == "adaga_sombria" or style == "adaga_valeria":
        # Adaga curva compacta (ocupa menos espaço para silhueta ágil de Ladino!)
        hilt_c = (50, 35, 65, 255)
        blade_c = (85, 65, 115, 255)
        edge_c = (195, 95, 255, 255) if style == "adaga_sombria" else (80, 235, 125, 255)
        line(px, 7, 24, 12, 19, hilt_c, 1.2)
        line(px, 10, 16, 15, 21, (160, 120, 210, 255), 1.1)
        # Lâmina curta e curva de assassino
        poly(px, [(12, 17), (18, 9), (25, 6), (22, 13), (15, 19)], blade_c, edge_c)
        disc(px, 12, 18, 1.6, edge_c)
        return apply_rpg_outline_and_shine(px, (18, 10, 28, 255), [(12, 18, edge_c), (24, 7, edge_c)])

    if style == "lamina_vampiro":
        # Espada Gêmea Carmesim com guarda de asas de morcego e canal de sangue
        hilt_c = (60, 20, 28, 255)
        guard_c = (110, 30, 40, 255)
        blade_c = (195, 35, 50, 255)
        bright_c = (255, 110, 120, 255)
        line(px, 4, 27, 10, 21, hilt_c, 1.3)
        # Guarda de morcego
        poly(px, [(6, 17), (11, 20), (14, 25), (11, 21)], guard_c, bright_c)
        # Lâmina bifurcada vampírica
        poly(px, [(10, 19), (26, 3), (29, 3), (28, 7), (13, 21)], blade_c, bright_c)
        line(px, 12, 19, 26, 5, (110, 10, 20, 255), 0.8)
        disc(px, 10, 21, 2.0, bright_c, blade_c)
        return apply_rpg_outline_and_shine(px, (32, 8, 12, 255), [(10, 21, bright_c), (27, 4, bright_c)])

    if style == "lamina_musgo":
        line(px, 4, 27, 10, 21, (95, 65, 38, 255), 1.3)
        line(px, 7, 18, 13, 24, (190, 160, 60, 255), 1.3)
        poly(px, [(10, 19), (26, 3), (29, 3), (28, 6), (13, 21)], (85, 200, 110, 255), (180, 255, 190, 255))
        return apply_rpg_outline_and_shine(px, glow_points=[(10, 21, (120, 255, 140, 255))])

    if style == "tridente_mares":
        line(px, 4, 27, 22, 9, (45, 115, 145, 255), 1.3)
        line(px, 18, 9, 24, 15, (90, 220, 245, 255), 1.2)
        line(px, 21, 10, 29, 2, (160, 245, 255, 255), 1.1)
        line(px, 18, 9, 25, 2, (120, 230, 250, 255), 1.0)
        line(px, 23, 14, 30, 7, (120, 230, 250, 255), 1.0)
        return apply_rpg_outline_and_shine(px, glow_points=[(21, 10, (160, 250, 255, 255))])

    # lamina_eclipse
    line(px, 3, 28, 10, 21, (45, 30, 65, 255), 1.4)
    line(px, 6, 17, 14, 25, (230, 180, 55, 255), 1.4)
    poly(px, [(10, 19), (26, 3), (30, 2), (28, 7), (13, 21)], (110, 50, 165, 255), (245, 205, 95, 255))
    disc(px, 10, 21, 2.2, (255, 215, 80, 255), (140, 50, 210, 255))
    return apply_rpg_outline_and_shine(px, (18, 8, 32, 255), [(10, 21, (255, 220, 90, 255)), (28, 4, (210, 120, 255, 255))])


def draw_bow_or_crossbow(style):
    px = new_canvas()
    if style == "arco_estelar" or style == "arco_oraculo":
        c_main = (75, 225, 195, 255) if style == "arco_estelar" else (195, 110, 250, 255)
        c_gold = (250, 210, 75, 255)
        # Corda energética
        line(px, 8, 5, 26, 23, (220, 250, 255, 255), 0.6)
        # Limbo curvo do arco
        line(px, 8, 5, 19, 6, c_main, 1.4)
        line(px, 19, 6, 25, 12, c_gold, 1.6)
        line(px, 25, 12, 26, 23, c_main, 1.4)
        disc(px, 22, 9, 2.2, (255, 255, 200, 255), c_gold)
        return apply_rpg_outline_and_shine(px, glow_points=[(22, 9, c_gold), (8, 5, c_main), (26, 23, c_main)])

    # besta_repeticao (Besta Metralhadora Rúnica com tambor mecânico dourado)
    stock_c = (115, 72, 42, 255)
    steel_c = (155, 170, 185, 255)
    gear_c = (245, 195, 55, 255)
    rune_c = (80, 235, 255, 255)
    line(px, 5, 26, 23, 8, stock_c, 1.6)
    # Arco frontal de aço
    line(px, 11, 5, 22, 9, steel_c, 1.4)
    line(px, 22, 9, 26, 20, steel_c, 1.4)
    # Tambor de repetição mecânico no centro
    disc(px, 16, 15, 3.6, gear_c, (160, 110, 25, 255))
    disc(px, 16, 15, 1.6, rune_c)
    return apply_rpg_outline_and_shine(px, glow_points=[(16, 15, rune_c), (22, 9, gear_c)])


def draw_artifact(style):
    px = new_canvas()
    if style == "ima_runico":
        # Ímã em formato de ferradura (U) com polos Vermelho e Azul + faíscas roxas
        iron_c = (95, 100, 120, 255)
        red_c = (235, 55, 65, 255)
        blue_c = (55, 150, 250, 255)
        spark_c = (215, 110, 255, 255)
        # Base curva do U
        disc(px, 16, 19, 8.5, iron_c)
        disc(px, 16, 19, 4.2, (0, 0, 0, 0), (0, 0, 0, 0))
        for y in range(19, 29):
            for x in range(12, 21):
                if math.hypot(x - 16, y - 19) < 4.2:
                    px[y][x] = (0, 0, 0, 0)
        # Pernas do ímã e polos coloridos
        poly(px, [(8, 8), (12, 8), (12, 19), (8, 19)], iron_c)
        poly(px, [(20, 8), (24, 8), (24, 19), (20, 19)], iron_c)
        poly(px, [(8, 5), (12, 5), (12, 10), (8, 10)], red_c, lighten(red_c, 0.35))
        poly(px, [(20, 5), (24, 5), (24, 10), (20, 10)], blue_c, lighten(blue_c, 0.35))
        return apply_rpg_outline_and_shine(px, glow_points=[(16, 8, spark_c), (10, 6, red_c), (22, 6, blue_c)])

    if style == "mochila_viajante":
        # Mochila de couro de aventureiro com fivelas douradas e gema dimensional roxa
        leather_c = (145, 85, 45, 255)
        flap_c = (175, 108, 58, 255)
        gold_c = (245, 198, 55, 255)
        gem_c = (185, 85, 255, 255)
        # Corpo da mochila
        poly(px, [(7, 10), (25, 10), (26, 26), (6, 26)], leather_c, darken(leather_c, 0.25))
        # Saco de dormir enrolado no topo
        poly(px, [(8, 6), (24, 6), (24, 10), (8, 10)], (65, 145, 95, 255), (95, 195, 125, 255))
        # Aba superior
        poly(px, [(7, 10), (25, 10), (23, 18), (9, 18)], flap_c, gold_c)
        # Tiras de couro e fivelas
        line(px, 11, 10, 11, 25, (90, 50, 25, 255), 1.0)
        line(px, 21, 10, 21, 25, (90, 50, 25, 255), 1.0)
        put(px, 11, 19, gold_c)
        put(px, 21, 19, gold_c)
        disc(px, 16, 15, 2.6, gem_c, (100, 30, 160, 255))
        return apply_rpg_outline_and_shine(px, glow_points=[(16, 15, gem_c)])

    if style == "cristal_fraterno":
        # Cristal duplo entrelaçado (Metade Azul-Ciano e Metade Ouro-Solar)
        cyan_c = (65, 225, 255, 255)
        gold_c = (255, 195, 50, 255)
        poly(px, [(16, 4), (23, 14), (16, 27), (9, 16)], cyan_c, lighten(cyan_c, 0.45))
        poly(px, [(16, 4), (24, 15), (16, 27)], gold_c, lighten(gold_c, 0.45))
        line(px, 9, 15, 23, 15, (255, 240, 150, 255), 1.1)
        return apply_rpg_outline_and_shine(px, glow_points=[(16, 15, (255, 255, 255, 255)), (14, 10, cyan_c), (18, 10, gold_c)])

    if style == "pluma_hermes":
        # Pluma alada celestial branca/dourada com brisa turquesa
        quill_c = (245, 200, 65, 255)
        feather_c = (235, 248, 255, 255)
        wind_c = (95, 240, 255, 255)
        poly(px, [(7, 25), (13, 11), (26, 5), (22, 18), (12, 24)], feather_c, wind_c)
        line(px, 5, 27, 25, 7, quill_c, 1.0)
        return apply_rpg_outline_and_shine(px, glow_points=[(24, 7, wind_c), (16, 15, feather_c)])

    if style == "grimorio_necromante" or style == "tomo_talento":
        cover_c = (48, 35, 70, 255) if style == "grimorio_necromante" else (135, 45, 165, 255)
        trim_c = (85, 245, 185, 255) if style == "grimorio_necromante" else (255, 215, 65, 255)
        pages_c = (235, 228, 205, 255)
        poly(px, [(7, 6), (23, 5), (25, 24), (9, 26)], cover_c, trim_c)
        poly(px, [(23, 6), (26, 8), (26, 25), (24, 24)], pages_c)
        disc(px, 16, 15, 3.2, trim_c, cover_c)
        return apply_rpg_outline_and_shine(px, glow_points=[(16, 15, trim_c)])

    if style == "relicario_antigo":
        # Cofre dourado octogonal com runa solar
        poly(px, [(7, 10), (25, 10), (26, 25), (6, 25)], (75, 55, 95, 255), (245, 195, 55, 255))
        poly(px, [(6, 7), (26, 7), (25, 13), (7, 13)], (235, 180, 45, 255), (255, 235, 120, 255))
        disc(px, 16, 15, 3.0, (80, 245, 230, 255), (245, 195, 55, 255))
        return apply_rpg_outline_and_shine(px, glow_points=[(16, 15, (120, 255, 245, 255))])

    if style == "insignia_rpg":
        # Medalhão real estrelado de sangue & classe
        disc(px, 16, 16, 9.5, (235, 185, 45, 255), (140, 90, 20, 255))
        disc(px, 16, 16, 5.5, (215, 40, 65, 255), (110, 15, 30, 255))
        return apply_rpg_outline_and_shine(px, glow_points=[(16, 16, (255, 220, 110, 255))])

    if style == "nucleo_basalto":
        disc(px, 16, 16, 9.0, (65, 60, 68, 255), (35, 30, 38, 255))
        disc(px, 16, 16, 4.5, (255, 120, 25, 255), (180, 45, 10, 255))
        return apply_rpg_outline_and_shine(px, glow_points=[(16, 16, (255, 220, 80, 255))])

    # coracao_chama
    disc(px, 16, 16, 8.5, (255, 190, 45, 255), (225, 70, 20, 255))
    disc(px, 16, 16, 4.0, (255, 250, 190, 255), (255, 160, 30, 255))
    return apply_rpg_outline_and_shine(px, glow_points=[(16, 16, (255, 255, 255, 255))])


# ============================================================================
#  CATÁLOGO COMPLETO DOS 32 ITENS COM CUSTOM MODEL DATA (1001..1032)
# ============================================================================
ITEMS_CATALOG = [
    # --- 9 FERRAMENTAS UTILITÁRIAS DE JORNADA (1001..1009) ---
    {"cmd": 1001, "id": "picareta_tectonica",  "bases": ["diamond_pickaxe"],                 "parent": "minecraft:item/handheld",     "profile": "tool_pick_scythe", "draw": lambda: draw_pickaxe("tectonica")},
    {"cmd": 1002, "id": "picareta_fornalha",   "bases": ["golden_pickaxe", "diamond_pickaxe"], "parent": "minecraft:item/handheld",   "profile": "tool_pick_scythe", "draw": lambda: draw_pickaxe("fornalha")},
    {"cmd": 1003, "id": "machado_lenhador",    "bases": ["diamond_axe"],                     "parent": "minecraft:item/handheld",     "profile": "heavy_weapon",     "draw": lambda: draw_axe_or_hammer("lenhador")},
    {"cmd": 1004, "id": "foicinha_colheita",   "bases": ["golden_hoe"],                      "parent": "minecraft:item/handheld",     "profile": "tool_pick_scythe", "draw": draw_scythe},
    {"cmd": 1005, "id": "arpeu_escalada",      "bases": ["fishing_rod"],                     "parent": "minecraft:item/handheld_rod", "profile": "tool_pick_scythe", "draw": draw_grappling_hook},
    {"cmd": 1006, "id": "ima_runico",          "bases": ["recovery_compass"],                "parent": "minecraft:item/generated",    "profile": "tome_artifact",    "draw": lambda: draw_artifact("ima_runico")},
    {"cmd": 1007, "id": "mochila_viajante",    "bases": ["bundle", "chest"],                 "parent": "minecraft:item/generated",    "profile": "tome_artifact",    "draw": lambda: draw_artifact("mochila_viajante")},
    {"cmd": 1008, "id": "cristal_fraterno",    "bases": ["amethyst_shard"],                  "parent": "minecraft:item/generated",    "profile": "tome_artifact",    "draw": lambda: draw_artifact("cristal_fraterno")},
    {"cmd": 1009, "id": "pluma_hermes",        "bases": ["feather"],                         "parent": "minecraft:item/generated",    "profile": "tome_artifact",    "draw": lambda: draw_artifact("pluma_hermes")},

    # --- 10 ARMAS DE CLASSE & CO-OP (1010..1019) ---
    {"cmd": 1010, "id": "cajado_inverno",      "bases": ["breeze_rod"],                      "parent": "minecraft:item/handheld",     "profile": "staff",            "draw": lambda: draw_staff("inverno")},
    {"cmd": 1011, "id": "cetro_singularidade", "bases": ["blaze_rod", "end_rod"],            "parent": "minecraft:item/handheld",     "profile": "staff",            "draw": lambda: draw_staff("singularidade")},
    {"cmd": 1012, "id": "grimorio_necromante", "bases": ["enchanted_book", "writable_book"], "parent": "minecraft:item/generated",    "profile": "tome_artifact",    "draw": lambda: draw_artifact("grimorio_necromante")},
    {"cmd": 1013, "id": "arco_estelar",        "bases": ["bow"],                             "parent": "minecraft:item/generated",    "profile": "ranged_bow",       "draw": lambda: draw_bow_or_crossbow("arco_estelar")},
    {"cmd": 1014, "id": "besta_repeticao",     "bases": ["crossbow"],                        "parent": "minecraft:item/generated",    "profile": "ranged_crossbow",  "draw": lambda: draw_bow_or_crossbow("besta_repeticao")},
    {"cmd": 1015, "id": "adaga_sombria",       "bases": ["iron_sword", "netherite_sword"],   "parent": "minecraft:item/handheld",     "profile": "dagger",           "draw": lambda: draw_sword_or_dagger("adaga_sombria")},
    {"cmd": 1016, "id": "lamina_vampiro",      "bases": ["diamond_sword"],                   "parent": "minecraft:item/handheld",     "profile": "sword",            "draw": lambda: draw_sword_or_dagger("lamina_vampiro")},
    {"cmd": 1017, "id": "martelo_magma",       "bases": ["netherite_pickaxe"],               "parent": "minecraft:item/handheld",     "profile": "heavy_weapon",     "draw": lambda: draw_axe_or_hammer("martelo_magma")},
    {"cmd": 1018, "id": "espada_berserker",    "bases": ["netherite_axe"],                   "parent": "minecraft:item/handheld",     "profile": "heavy_weapon",     "draw": lambda: draw_axe_or_hammer("berserker")},
    {"cmd": 1019, "id": "alabarda_solar",      "bases": ["golden_axe"],                      "parent": "minecraft:item/handheld",     "profile": "heavy_weapon",     "draw": lambda: draw_axe_or_hammer("alabarda_solar")},

    # --- 13 RELÍQUIAS DE BOSSES, SKYRIM & EVOLUÇÃO RPG (1020..1032) ---
    {"cmd": 1020, "id": "lamina_musgo",        "bases": ["diamond_sword"],                   "parent": "minecraft:item/handheld",     "profile": "sword",            "draw": lambda: draw_sword_or_dagger("lamina_musgo")},
    {"cmd": 1021, "id": "tridente_mares",      "bases": ["trident"],                         "parent": "minecraft:item/handheld",     "profile": "heavy_weapon",     "draw": lambda: draw_sword_or_dagger("tridente_mares")},
    {"cmd": 1022, "id": "picareta_ferreiro",   "bases": ["netherite_pickaxe"],               "parent": "minecraft:item/handheld",     "profile": "tool_pick_scythe", "draw": lambda: draw_pickaxe("ferreiro")},
    {"cmd": 1023, "id": "arco_oraculo",        "bases": ["bow"],                             "parent": "minecraft:item/generated",    "profile": "ranged_bow",       "draw": lambda: draw_bow_or_crossbow("arco_oraculo")},
    {"cmd": 1024, "id": "lamina_eclipse",      "bases": ["netherite_sword"],                 "parent": "minecraft:item/handheld",     "profile": "sword",            "draw": lambda: draw_sword_or_dagger("lamina_eclipse")},
    {"cmd": 1025, "id": "coracao_chama",       "bases": ["nether_star"],                     "parent": "minecraft:item/generated",    "profile": "tome_artifact",    "draw": lambda: draw_artifact("coracao_chama")},
    {"cmd": 1026, "id": "machado_thorgar",     "bases": ["iron_axe"],                        "parent": "minecraft:item/handheld",     "profile": "heavy_weapon",     "draw": lambda: draw_axe_or_hammer("thorgar")},
    {"cmd": 1027, "id": "cajado_morvath",      "bases": ["bone"],                            "parent": "minecraft:item/handheld",     "profile": "staff",            "draw": lambda: draw_staff("morvath")},
    {"cmd": 1028, "id": "nucleo_basalto",      "bases": ["magma_cream"],                     "parent": "minecraft:item/generated",    "profile": "tome_artifact",    "draw": lambda: draw_artifact("nucleo_basalto")},
    {"cmd": 1029, "id": "adaga_valeria",       "bases": ["iron_sword"],                      "parent": "minecraft:item/handheld",     "profile": "dagger",           "draw": lambda: draw_sword_or_dagger("adaga_valeria")},
    {"cmd": 1030, "id": "insignia_rpg",        "bases": ["nether_star", "heart_of_the_sea"], "parent": "minecraft:item/generated",    "profile": "tome_artifact",    "draw": lambda: draw_artifact("insignia_rpg")},
    {"cmd": 1031, "id": "tomo_talento",        "bases": ["book", "knowledge_book"],          "parent": "minecraft:item/generated",    "profile": "tome_artifact",    "draw": lambda: draw_artifact("tomo_talento")},
    {"cmd": 1032, "id": "relicario_antigo",    "bases": ["ender_chest", "heart_of_the_sea"], "parent": "minecraft:item/generated",    "profile": "tome_artifact",    "draw": lambda: draw_artifact("relicario_antigo")},
]


def fallback_item_model(base_item):
    """Retorna o modelo fallback vanilla para itens normais sem CustomModelData."""
    if base_item == "chest":
        return {
            "type": "minecraft:special",
            "base": "minecraft:item/chest",
            "model": {"type": "minecraft:chest", "texture": "minecraft:normal"}
        }
    if base_item == "ender_chest":
        return {
            "type": "minecraft:special",
            "base": "minecraft:item/ender_chest",
            "model": {"type": "minecraft:chest", "texture": "minecraft:ender"}
        }
    if base_item == "trident":
        return {
            "type": "minecraft:condition",
            "property": "minecraft:using_item",
            "on_true": {"type": "minecraft:special", "base": "minecraft:item/trident_throwing", "model": {"type": "minecraft:trident"}},
            "on_false": {"type": "minecraft:special", "base": "minecraft:item/trident_in_hand", "model": {"type": "minecraft:trident"}},
        }
    if base_item == "bow":
        return {
            "type": "minecraft:condition",
            "property": "minecraft:using_item",
            "on_false": {"type": "minecraft:model", "model": "minecraft:item/bow"},
            "on_true": {
                "type": "minecraft:range_dispatch",
                "property": "minecraft:use_duration",
                "scale": 0.05,
                "entries": [
                    {"threshold": 0.65, "model": {"type": "minecraft:model", "model": "minecraft:item/bow_pulling_1"}},
                    {"threshold": 0.9,  "model": {"type": "minecraft:model", "model": "minecraft:item/bow_pulling_2"}},
                ],
                "fallback": {"type": "minecraft:model", "model": "minecraft:item/bow_pulling_0"},
            },
        }
    if base_item == "crossbow":
        return {
            "type": "minecraft:select",
            "property": "minecraft:charge_type",
            "cases": [
                {"when": "arrow",  "model": {"type": "minecraft:model", "model": "minecraft:item/crossbow_arrow"}},
                {"when": "rocket", "model": {"type": "minecraft:model", "model": "minecraft:item/crossbow_firework"}},
            ],
            "fallback": {
                "type": "minecraft:condition",
                "property": "minecraft:using_item",
                "on_false": {"type": "minecraft:model", "model": "minecraft:item/crossbow_standby"},
                "on_true": {
                    "type": "minecraft:range_dispatch",
                    "property": "minecraft:crossbow/pull",
                    "entries": [
                        {"threshold": 0.58, "model": {"type": "minecraft:model", "model": "minecraft:item/crossbow_pulling_1"}},
                        {"threshold": 1.0,  "model": {"type": "minecraft:model", "model": "minecraft:item/crossbow_pulling_2"}},
                    ],
                    "fallback": {"type": "minecraft:model", "model": "minecraft:item/crossbow_pulling_0"},
                },
            },
        }
    if base_item == "fishing_rod":
        return {
            "type": "minecraft:condition",
            "property": "minecraft:fishing_rod/cast",
            "on_true": {"type": "minecraft:model", "model": "minecraft:item/fishing_rod_cast"},
            "on_false": {"type": "minecraft:model", "model": "minecraft:item/fishing_rod"},
        }
    return {"type": "minecraft:model", "model": f"minecraft:item/{base_item}"}


def build_resource_pack():
    if os.path.exists(RP_DIR):
        shutil.rmtree(RP_DIR)
    os.makedirs(RP_DIR, exist_ok=True)

    # 1. pack.mcmeta compatível com 26.3 (resource_major: 97) e 1.21.x
    pack_meta = {
        "pack": {
            "pack_format": 97,
            "min_format": 34,
            "max_format": 99,
            "supported_formats": [34, 99],
            "description": "§6§lCinzas de Aurelion §7- Skins & Modelos 3D de Armas e Ferramentas",
        }
    }
    with open(os.path.join(RP_DIR, "pack.mcmeta"), "w", encoding="utf-8") as f:
        json.dump(pack_meta, f, indent=2, ensure_ascii=False)

    # 2. Ícone pack.png
    icon_px = draw_artifact("coracao_chama")
    save_png(os.path.join(RP_DIR, "pack.png"), 32, 32, icon_px)

    # 3. Gera as 32 texturas PNG e os 32 modelos JSON em assets/aurelion/
    by_base = {}
    for entry in ITEMS_CATALOG:
        item_id = entry["id"]
        cmd = entry["cmd"]
        bases = entry["bases"]
        parent = entry["parent"]
        profile = entry["profile"]

        tex_path = os.path.join(RP_DIR, "assets", "aurelion", "textures", "item", f"{item_id}.png")
        save_png(tex_path, 32, 32, entry["draw"]())

        model_json = {
            "parent": parent,
            "gui_light": "front",
            "textures": {
                "layer0": f"aurelion:item/{item_id}"
            },
            "display": DISPLAY_PROFILES[profile],
        }
        model_path = os.path.join(RP_DIR, "assets", "aurelion", "models", "item", f"{item_id}.json")
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        with open(model_path, "w", encoding="utf-8") as f:
            json.dump(model_json, f, indent=2)

        for base in bases:
            by_base.setdefault(base, []).append(entry)

    # 4. Gera as definições modernas 1.21.4+ / 26.3 (assets/minecraft/items/<base>.json)
    #    e também os overrides clássicos (assets/minecraft/models/item/<base>.json)
    for base, entries in by_base.items():
        entries_sorted = sorted(entries, key=lambda e: e["cmd"])

        # Modern 1.21.4+ / 26.3 item definition (range_dispatch por custom_model_data)
        dispatch_entries = []
        for e in entries_sorted:
            dispatch_entries.append({
                "threshold": e["cmd"],
                "model": {
                    "type": "minecraft:model",
                    "model": f"aurelion:item/{e['id']}"
                }
            })

        item_def = {
            "model": {
                "type": "minecraft:range_dispatch",
                "property": "minecraft:custom_model_data",
                "index": 0,
                "entries": dispatch_entries,
                "fallback": fallback_item_model(base),
            }
        }
        item_def_path = os.path.join(RP_DIR, "assets", "minecraft", "items", f"{base}.json")
        os.makedirs(os.path.dirname(item_def_path), exist_ok=True)
        with open(item_def_path, "w", encoding="utf-8") as f:
            json.dump(item_def, f, indent=2)

        # Legacy overrides (para clientes usando pipeline clássico)
        if base not in ("chest", "ender_chest", "trident", "bow", "crossbow", "fishing_rod"):
            parent_type = "minecraft:item/handheld" if any(k in base for k in ("sword", "pickaxe", "axe", "hoe", "rod", "bone")) else "minecraft:item/generated"
            legacy_model = {
                "parent": parent_type,
                "textures": {"layer0": f"minecraft:item/{base}"},
                "overrides": [
                    {"predicate": {"custom_model_data": e["cmd"]}, "model": f"aurelion:item/{e['id']}"}
                    for e in entries_sorted
                ],
            }
            legacy_path = os.path.join(RP_DIR, "assets", "minecraft", "models", "item", f"{base}.json")
            os.makedirs(os.path.dirname(legacy_path), exist_ok=True)
            with open(legacy_path, "w", encoding="utf-8") as f:
                json.dump(legacy_model, f, indent=2)

    # 5. Empacota o arquivo aurelion_resourcepack.zip com timestamps fixos (SHA-1 determinístico!)
    if os.path.exists(ZIP_PATH):
        os.remove(ZIP_PATH)
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(RP_DIR):
            for file in sorted(files):
                abs_p = os.path.join(root, file)
                rel_p = os.path.relpath(abs_p, RP_DIR)
                info = zipfile.ZipInfo(rel_p, date_time=(2026, 10, 20, 12, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                with open(abs_p, "rb") as rf:
                    zf.writestr(info, rf.read())

    with open(ZIP_PATH, "rb") as f:
        sha1 = hashlib.sha1(f.read()).hexdigest()
    with open(SHA_PATH, "w", encoding="utf-8") as f:
        f.write(sha1 + "\n")

    print(f"[OK] Resource Pack gerado: {ZIP_PATH}")
    print(f"[OK] Total de Skins/Modelos 3D customizados: {len(ITEMS_CATALOG)}")
    print(f"[OK] SHA-1: {sha1}")


if __name__ == "__main__":
    build_resource_pack()
