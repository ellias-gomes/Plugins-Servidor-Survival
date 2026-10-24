#!/usr/bin/env python3
"""
Gerador do datapack "aurelion_modelos".

Cria modelos 3D customizados para bosses/semi-bosses/pilares usando display entities
(block_display / item_display) 100% vanilla, SEM resource pack, SEM plugin extra.

Cada entidade "base" (mob invisível que mantém IA, vida e hitbox) recebe um modelo
composto por várias peças que seguem sua posição/rotação e são animadas com
interpolação (andar, respirar/idle, ataque, habilidade especial, dano e colapso na morte).

Uso:  python3 scripts/gerar_modelos.py      (gera world/datapacks/aurelion_modelos)
Depois: /reload no jogo ou reiniciar o servidor.
"""
import math, os, shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "world", "datapacks", "aurelion_modelos")

# ----------------------------- matemática (quaternions) -----------------------------
def qmul(a, b):
    x1, y1, z1, w1 = a; x2, y2, z2, w2 = b
    return (w1*x2 + x1*w2 + y1*z2 - z1*y2, w1*y2 - x1*z2 + y1*w2 + z1*x2,
            w1*z2 + x1*y2 - y1*x2 + z1*w2, w1*w2 - x1*x2 - y1*y2 - z1*z2)

def qaxis(ax, deg):
    h = math.radians(deg) / 2; s = math.sin(h)
    return (ax[0]*s, ax[1]*s, ax[2]*s, math.cos(h))

def qeuler(rx, ry, rz):  # ordem: X, depois Y, depois Z
    return qmul(qaxis((0, 0, 1), rz), qmul(qaxis((0, 1, 0), ry), qaxis((1, 0, 0), rx)))

def qrot(q, v):
    x, y, z, w = q
    tx = 2*(y*v[2] - z*v[1]); ty = 2*(z*v[0] - x*v[2]); tz = 2*(x*v[1] - y*v[0])
    return (v[0] + w*tx + (y*tz - z*ty), v[1] + w*ty + (z*tx - x*tz), v[2] + w*tz + (x*ty - y*tx))

def vadd(a, b): return (a[0]+b[0], a[1]+b[1], a[2]+b[2])
def vsub(a, b): return (a[0]-b[0], a[1]-b[1], a[2]-b[2])
def vmul(a, k): return (a[0]*k, a[1]*k, a[2]*k)

# ----------------------------- definição de peças e poses -----------------------------
def B(n, block, c, s, g=None, pv=None, gl=False, st=None, r0=(0, 0, 0)):
    return dict(n=n, k="b", id=block, c=c, s=s, g=g or n, pv=pv, gl=gl, st=st, r0=r0)

def I(n, item, c, s, g=None, pv=None, gl=False, r0=(0, 0, 0)):
    return dict(n=n, k="i", id=item, c=c, s=s, g=g or n, pv=pv, gl=gl, st=None, r0=r0)

def P(rot=(0, 0, 0), mov=(0, 0, 0), sc=1.0, sp=1.0, piv=(0, 0, 0)):
    if not isinstance(sc, tuple): sc = (sc, sc, sc)
    return dict(rot=rot, mov=mov, sc=sc, sp=sp, piv=piv)

POSES = ["idle0", "idle1", "walk0", "walk1", "attack", "special", "hurt"]
DUR = {"idle0": 10, "idle1": 10, "walk0": 10, "walk1": 10, "attack": 8, "special": 10, "hurt": 3}

def std_poses(lean=(0, 1.4, 0), arm_up=130):
    ps = {p: {} for p in POSES}
    ps["idle1"] = {"*": P(mov=(0, .05, 0)), "arm_l": P(rot=(0, 0, -5)), "arm_r": P(rot=(0, 0, 5))}
    ps["walk0"] = {"leg_l": P(rot=(28, 0, 0)), "leg_r": P(rot=(-28, 0, 0)),
                   "arm_l": P(rot=(-22, 0, 0)), "arm_r": P(rot=(22, 0, 0)), "*": P(mov=(0, .04, 0))}
    ps["walk1"] = {"leg_l": P(rot=(-28, 0, 0)), "leg_r": P(rot=(28, 0, 0)),
                   "arm_l": P(rot=(22, 0, 0)), "arm_r": P(rot=(-22, 0, 0))}
    ps["attack"] = {"arm_r": P(rot=(-arm_up, 0, 0)), "arm_l": P(rot=(-40, 0, 0)),
                    "*": P(rot=(18, 0, 0), piv=lean)}
    ps["special"] = {"arm_l": P(rot=(-20, 0, -70)), "arm_r": P(rot=(-20, 0, 70)), "*": P(mov=(0, .15, 0))}
    ps["hurt"] = {"*": P(rot=(-12, 0, 0), mov=(0, 0, -.12), piv=lean)}
    return ps

def merge(ps, pose, extra):
    for k, v in extra.items():
        ps[pose][k] = v

def ring(prefix, block, n, radius, y, size, group, plane="xz", gl=False, phase=0.0):
    out = []
    for i in range(n):
        a = 2*math.pi*i/n + phase
        if plane == "xz": c = (radius*math.sin(a), y, radius*math.cos(a))
        else: c = (radius*math.sin(a), y + radius*math.cos(a), 0.0)
        out.append(B(f"{prefix}{i}", block, c, (size, size, size), g=group, pv=(0, y, 0), gl=gl))
    return out

def flare(phi, a):  # inclina membro pendurado "para fora" na direção angular a
    return (-phi*math.cos(a), 0, phi*math.sin(a))

MODELS = []

# =====================================================================================
# 1. VERDELITH - Golem Ancestral de Musgo (base: iron_golem)
# =====================================================================================
def verdelith():
    parts = [
        B("torso", "moss_block", (0, 2.6, 0), (2.2, 2.0, 1.4)),
        B("peito", "oak_log", (0, 2.6, 0.75), (1.3, 1.2, 0.2), gl=False),
        B("nucleo", "verdant_froglight", (0, 2.65, 0.86), (0.5, 0.5, 0.1), gl=True),
        B("costas", "mangrove_roots", (0, 3.1, -0.9), (1.7, 1.4, 0.5), g="raizes"),
        B("raiz_b", "mangrove_roots", (0.6, 2.2, -0.85), (0.8, 0.9, 0.4), g="raizes", pv=(0, 3.0, -0.7)),
        B("head", "mossy_stone_bricks", (0, 4.2, 0.1), (1.2, 1.0, 1.2)),
        B("olho_l", "verdant_froglight", (-0.3, 4.25, 0.72), (0.25, 0.2, 0.1), g="head", pv=(0, 3.7, 0.1), gl=True),
        B("olho_r", "verdant_froglight", (0.3, 4.25, 0.72), (0.25, 0.2, 0.1), g="head", pv=(0, 3.7, 0.1), gl=True),
        B("antler_l", "dark_oak_log", (-0.55, 5.0, 0.1), (0.15, 1.0, 0.15), pv=(-0.4, 4.7, 0.1)),
        B("antler_r", "dark_oak_log", (0.55, 5.0, 0.1), (0.15, 1.0, 0.15), pv=(0.4, 4.7, 0.1)),
        B("galho_l", "dark_oak_log", (-0.8, 5.3, 0.1), (0.5, 0.12, 0.12), g="antler_l", pv=(-0.4, 4.7, 0.1)),
        B("galho_r", "dark_oak_log", (0.8, 5.3, 0.1), (0.5, 0.12, 0.12), g="antler_r", pv=(0.4, 4.7, 0.1)),
        B("folha_l", "azalea_leaves", (-1.55, 3.95, 0), (0.9, 0.5, 0.9), g="arm_l", pv=(-1.55, 3.4, 0)),
        B("folha_r", "azalea_leaves", (1.55, 3.95, 0), (0.9, 0.5, 0.9), g="arm_r", pv=(1.55, 3.4, 0)),
    ]
    for sx, sd in ((-1, "l"), (1, "r")):
        parts += [
            B(f"ombro_{sd}", "mossy_cobblestone", (1.55*sx, 3.4, 0), (0.9, 0.9, 0.9), g=f"arm_{sd}", pv=(1.55*sx, 3.4, 0)),
            B(f"braco_{sd}", "oak_log", (1.55*sx, 2.3, 0), (0.7, 2.2, 0.7), g=f"arm_{sd}", pv=(1.55*sx, 3.4, 0)),
            B(f"punho_{sd}", "mossy_cobblestone", (1.55*sx, 1.1, 0), (1.0, 0.9, 1.0), g=f"arm_{sd}", pv=(1.55*sx, 3.4, 0)),
            B(f"perna_{sd}", "mossy_stone_bricks", (0.55*sx, 0.9, 0), (0.8, 1.8, 0.9), g=f"leg_{sd}", pv=(0.55*sx, 1.8, 0)),
        ]
    ps = std_poses(lean=(0, 1.8, 0), arm_up=150)
    merge(ps, "idle1", {"nucleo": P(sc=1.3), "raizes": P(rot=(0, 0, 2))})
    merge(ps, "attack", {"antler_l": P(rot=(0, 0, 15)), "antler_r": P(rot=(0, 0, -15))})
    merge(ps, "special", {"antler_l": P(rot=(0, 0, -25)), "antler_r": P(rot=(0, 0, 25)),
                          "raizes": P(sc=1.4, sp=1.3), "nucleo": P(sc=1.8)})
    return dict(name="verdelith", id=1, scale=1.7, parts=parts, poses=ps)

# =====================================================================================
# 2. THALASSA - Rainha das Marés (base: drowned)
# =====================================================================================
def thalassa():
    parts = [
        B("torso", "prismarine_bricks", (0, 2.3, 0), (1.0, 1.4, 0.6)),
        B("perola", "sea_lantern", (0, 2.4, 0.34), (0.35, 0.35, 0.1), gl=True),
        B("head", "dark_prismarine", (0, 3.4, 0), (0.7, 0.7, 0.7)),
        B("olho_l", "sea_lantern", (-0.2, 3.45, 0.37), (0.15, 0.12, 0.05), g="head", pv=(0, 3.1, 0), gl=True),
        B("olho_r", "sea_lantern", (0.2, 3.45, 0.37), (0.15, 0.12, 0.05), g="head", pv=(0, 3.1, 0), gl=True),
        B("coroa1", "fire_coral_block", (-0.3, 3.95, 0), (0.15, 0.5, 0.15), g="coroa", pv=(0, 3.8, 0)),
        B("coroa2", "horn_coral_block", (0, 4.05, 0), (0.15, 0.7, 0.15), g="coroa", pv=(0, 3.8, 0)),
        B("coroa3", "tube_coral_block", (0.3, 3.95, 0), (0.15, 0.5, 0.15), g="coroa", pv=(0, 3.8, 0)),
        B("nadadeira_l", "blue_ice", (-0.5, 2.7, -0.45), (0.1, 1.0, 0.6), pv=(-0.5, 2.7, -0.3)),
        B("nadadeira_r", "blue_ice", (0.5, 2.7, -0.45), (0.1, 1.0, 0.6), pv=(0.5, 2.7, -0.3)),
        # tridente construído com blocos (sem depender da orientação do item)
        B("tri_haste", "lightning_rod", (1.0, 2.2, 0.55), (0.3, 3.2, 0.3), g="arm_r", pv=(0.75, 3.0, 0)),
        B("tri_centro", "prismarine", (1.0, 3.95, 0.55), (0.12, 0.5, 0.12), g="arm_r", pv=(0.75, 3.0, 0)),
        B("tri_esq", "prismarine", (0.82, 3.85, 0.55), (0.12, 0.4, 0.12), g="arm_r", pv=(0.75, 3.0, 0)),
        B("tri_dir", "prismarine", (1.18, 3.85, 0.55), (0.12, 0.4, 0.12), g="arm_r", pv=(0.75, 3.0, 0)),
    ]
    for sx, sd in ((-1, "l"), (1, "r")):
        parts.append(B(f"braco_{sd}", "prismarine", (0.75*sx, 2.4, 0), (0.35, 1.3, 0.35), g=f"arm_{sd}", pv=(0.75*sx, 3.0, 0)))
    n = 6
    for i in range(n):
        a = 2*math.pi*i/n
        parts.append(B(f"tent{i}", "dark_prismarine" if i % 2 else "prismarine_bricks",
                       (0.55*math.sin(a), 0.9, 0.55*math.cos(a)), (0.4, 1.8, 0.4),
                       g=f"tent{i}", pv=(0.55*math.sin(a), 1.8, 0.55*math.cos(a))))
    ps = {p: {} for p in POSES}
    def tents(phi, sign=1):
        d = {}
        for i in range(n):
            a = 2*math.pi*i/n
            d[f"tent{i}"] = P(rot=flare(phi*(sign if i % 2 == 0 else -sign), a))
        return d
    ps["idle0"] = {**tents(10), "*": P(mov=(0, -.05, 0))}
    ps["idle1"] = {**tents(10, -1), "*": P(mov=(0, .15, 0)), "arm_l": P(rot=(0, 0, -6)), "arm_r": P(rot=(0, 0, 6)),
                   "perola": P(sc=1.3)}
    ps["walk0"] = {**tents(24), "*": P(rot=(8, 0, 0), piv=(0, 1.8, 0))}
    ps["walk1"] = {**tents(24, -1), "*": P(rot=(8, 0, 0), piv=(0, 1.8, 0), mov=(0, .1, 0))}
    ps["attack"] = {**tents(45), "arm_r": P(rot=(-80, 0, 0)), "arm_l": P(rot=(-60, 0, -20)),
                    "nadadeira_l": P(rot=(0, 0, -45)), "nadadeira_r": P(rot=(0, 0, 45)),
                    "*": P(rot=(12, 0, 0), piv=(0, 1.8, 0))}
    ps["special"] = {**tents(20), "arm_r": P(rot=(-170, 0, 0)), "arm_l": P(rot=(-30, 0, -45)),
                     "coroa": P(sc=1.5, sp=1.4), "perola": P(sc=2.0), "*": P(mov=(0, .5, 0))}
    ps["hurt"] = {**tents(30), "*": P(rot=(-14, 0, 0), mov=(0, 0, -.15), piv=(0, 1.8, 0))}
    return dict(name="thalassa", id=2, scale=1.9, parts=parts, poses=ps)

# =====================================================================================
# 3. KORVAN - Ferreiro Caído (base: wither_skeleton)
# =====================================================================================
def korvan():
    parts = [
        B("torso", "blackstone", (0, 2.9, 0), (1.5, 1.6, 0.9)),
        B("magma_peito", "magma_block", (0, 2.9, 0.5), (0.9, 0.9, 0.15), gl=True),
        B("magma_costas", "magma_block", (0, 3.0, -0.55), (0.8, 0.8, 0.15), gl=True),
        B("chamine_a", "polished_blackstone_bricks", (0.5, 3.9, -0.7), (0.3, 1.2, 0.3)),
        B("chamine_b", "polished_blackstone_bricks", (-0.5, 3.8, -0.7), (0.3, 1.0, 0.3)),
        B("head", "polished_blackstone_bricks", (0, 4.05, 0), (0.9, 0.9, 0.9)),
        B("visor", "shroomlight", (0, 4.05, 0.47), (0.7, 0.15, 0.1), g="head", pv=(0, 3.6, 0), gl=True),
        B("chifre_l", "gilded_blackstone", (-0.55, 4.6, 0), (0.15, 0.6, 0.15), g="head", pv=(0, 3.6, 0)),
        B("chifre_r", "gilded_blackstone", (0.55, 4.6, 0), (0.15, 0.6, 0.15), g="head", pv=(0, 3.6, 0)),
        # martelo na mão direita
        B("cabo", "dark_oak_planks", (1.2, 1.9, 0.75), (0.2, 2.4, 0.2), g="arm_r", pv=(1.15, 3.4, 0)),
        B("martelo", "iron_block", (1.2, 3.25, 0.75), (1.0, 0.7, 0.7), g="arm_r", pv=(1.15, 3.4, 0)),
        B("martelo_brasa", "magma_block", (1.2, 3.25, 1.12), (0.5, 0.4, 0.05), g="arm_r", pv=(1.15, 3.4, 0), gl=True),
    ]
    for sx, sd in ((-1, "l"), (1, "r")):
        parts += [
            B(f"ombreira_{sd}", "netherite_block", (1.15*sx, 3.55, 0), (0.85, 0.6, 0.95), g=f"arm_{sd}", pv=(1.15*sx, 3.4, 0)),
            B(f"braco_{sd}", "blackstone", (1.15*sx, 2.6, 0), (0.55, 1.6, 0.55), g=f"arm_{sd}", pv=(1.15*sx, 3.4, 0)),
            B(f"perna_{sd}", "blackstone", (0.5*sx, 1.0, 0), (0.7, 2.0, 0.8), g=f"leg_{sd}", pv=(0.5*sx, 2.0, 0)),
            B(f"bota_{sd}", "magma_block", (0.5*sx, 0.15, 0.2), (0.8, 0.3, 1.0), g=f"leg_{sd}", pv=(0.5*sx, 2.0, 0), gl=True),
        ]
    ps = std_poses(lean=(0, 2.0, 0), arm_up=100)
    for p in ("walk0", "walk1"):
        for k in ("leg_l", "leg_r"):
            r = ps[p][k]["rot"]; ps[p][k] = P(rot=(r[0]*0.8, 0, 0))
    merge(ps, "idle1", {"magma_peito": P(sc=1.2), "magma_costas": P(sc=1.2)})
    ps["attack"]["*"] = P(rot=(32, 0, 0), piv=(0, 2.0, 0), mov=(0, 0, .2))
    ps["attack"]["arm_r"] = P(rot=(-115, 0, 0))
    ps["special"] = {"arm_r": P(rot=(-172, 0, 0)), "arm_l": P(rot=(-60, 0, -25)), "magma_peito": P(sc=1.4),
                     "magma_costas": P(sc=1.4), "visor": P(sc=1.3), "*": P(mov=(0, .1, 0))}
    return dict(name="korvan", id=3, scale=1.8, parts=parts, poses=ps)

# =====================================================================================
# 4. SERAPHEL - Oráculo Quebrado (base: evoker) - paira, asas, auréola, orbe
# =====================================================================================
def seraphel():
    H = 0.6  # altura de levitação do modelo
    parts = [
        B("manto_top", "quartz_block", (0, 2.4+H, 0), (1.1, 1.4, 0.7)),
        B("manto_base", "smooth_quartz", (0, 1.4+H, 0), (0.8, 1.0, 0.5)),
        B("manto_ponta", "quartz_pillar", (0, 0.7+H, 0), (0.4, 0.5, 0.3)),
        B("head", "chiseled_quartz_block", (0, 3.4+H, 0), (0.8, 0.8, 0.8)),
        B("olho", "amethyst_block", (0, 3.45+H, 0.42), (0.3, 0.18, 0.05), g="head", pv=(0, 3.0+H, 0), gl=True),
        B("orbe", "crying_obsidian", (0, 2.6+H, 0.95), (0.4, 0.4, 0.4), gl=True, pv=(0, 2.6+H, 0.4)),
    ]
    parts += ring("halo", "gold_block", 8, 0.8, 4.2+H, 0.2, "halo", gl=True)
    for sx, sd in ((-1, "l"), (1, "r")):
        parts.append(B(f"braco_{sd}", "quartz_slab" if False else "smooth_quartz", (0.75*sx, 2.4+H, 0.1), (0.3, 1.1, 0.3),
                       g=f"arm_{sd}", pv=(0.75*sx, 3.0+H, 0.1)))
        for j, (ln, off) in enumerate(((1.5, 0.0), (1.2, -0.25), (0.9, -0.5))):
            parts.append(B(f"asa_{sd}{j}", "white_concrete", (sx*(0.45+ln/2), 3.15+H+off, -0.4), (ln, 0.1, 0.55),
                           g=f"asa_{sd}", pv=(0.4*sx, 3.0+H, -0.35), r0=(0, 0, 18*sx)))
    ps = {p: {} for p in POSES}
    def asas(rz, ry=0):
        return {"asa_l": P(rot=(0, -ry, -rz), piv=(0, 0, 0)), "asa_r": P(rot=(0, ry, rz))}
    ps["idle0"] = {**asas(-8), "*": P(mov=(0, -.1, 0)), "halo": P(rot=(0, 0, 0))}
    ps["idle1"] = {**asas(14), "*": P(mov=(0, .2, 0)), "halo": P(rot=(0, 45, 0)), "arm_l": P(rot=(0, 0, -6)),
                   "arm_r": P(rot=(0, 0, 6)), "orbe": P(sc=1.25)}
    ps["walk0"] = {**asas(-20, 10), "*": P(rot=(10, 0, 0), piv=(0, 2.0, 0)), "halo": P(rot=(0, 90, 0))}
    ps["walk1"] = {**asas(20, -10), "*": P(rot=(10, 0, 0), piv=(0, 2.0, 0), mov=(0, .12, 0)), "halo": P(rot=(0, 135, 0))}
    ps["attack"] = {**asas(-55, 20), "arm_l": P(rot=(60, 0, -25)), "arm_r": P(rot=(60, 0, 25)),
                    "*": P(rot=(45, 0, 0), piv=(0, 2.4, 0), mov=(0, 0, .35)), "halo": P(rot=(0, 180, 0))}
    ps["special"] = {**asas(35), "arm_l": P(rot=(-150, 0, -10)), "arm_r": P(rot=(-150, 0, 10)),
                     "halo": P(rot=(0, 360, 0), sc=1.0, sp=1.5), "orbe": P(sc=2.6, mov=(0, .6, 0)), "*": P(mov=(0, .5, 0))}
    ps["hurt"] = {**asas(-30), "*": P(rot=(-18, 0, 0), mov=(0, 0, -.2), piv=(0, 2.0, 0))}
    return dict(name="seraphel", id=4, scale=2.0, parts=parts, poses=ps)

# =====================================================================================
# 5. O ECLIPSE - Colosso do Vazio (base: warden) - núcleo, anéis orbitais, braços flutuantes
# =====================================================================================
def eclipse():
    parts = [
        B("nucleo", "obsidian", (0, 2.7, 0), (1.6, 1.6, 1.6)),
        B("olho", "amethyst_block", (0, 2.7, 0.82), (0.7, 0.7, 0.15), gl=True),
        B("pupila", "black_concrete", (0, 2.7, 0.9), (0.25, 0.5, 0.05)),
    ]
    parts += ring("anel_a", "crying_obsidian", 8, 1.7, 2.7, 0.3, "anel_a", gl=True)
    parts += ring("anel_b", "crying_obsidian", 8, 2.0, 2.7, 0.25, "anel_b", plane="xy", gl=True)
    for i in range(5):
        a = 2*math.pi*i/5
        parts.append(B(f"coroa{i}", "obsidian", (0.7*math.sin(a), 3.9, 0.7*math.cos(a)), (0.2, 0.9, 0.2),
                       g="coroa", pv=(0, 3.5, 0)))
    for sx, sd in ((-1, "l"), (1, "r")):
        parts += [
            B(f"braco_{sd}", "obsidian", (1.95*sx, 2.3, 0), (0.6, 1.8, 0.6), g=f"arm_{sd}", pv=(1.6*sx, 3.2, 0)),
            B(f"punho_{sd}", "crying_obsidian", (1.95*sx, 1.3, 0), (0.8, 0.8, 0.8), g=f"arm_{sd}", pv=(1.6*sx, 3.2, 0), gl=True),
            B(f"perna_{sd}", "deepslate_tiles", (0.55*sx, 0.9, 0), (0.9, 1.8, 0.9), g=f"leg_{sd}", pv=(0.55*sx, 1.8, 0)),
        ]
    ps = {p: {} for p in POSES}
    ps["idle0"] = {"anel_a": P(rot=(0, 0, 0)), "anel_b": P(rot=(0, 0, 0))}
    ps["idle1"] = {"anel_a": P(rot=(0, 45, 0)), "anel_b": P(rot=(0, 0, 45)), "nucleo": P(sc=1.07),
                   "*": P(mov=(0, .12, 0)), "olho": P(sc=1.2)}
    ps["walk0"] = {"leg_l": P(rot=(25, 0, 0)), "leg_r": P(rot=(-25, 0, 0)), "anel_a": P(rot=(0, 90, 0)),
                   "anel_b": P(rot=(0, 0, 90)), "arm_l": P(rot=(-15, 0, 0)), "arm_r": P(rot=(15, 0, 0))}
    ps["walk1"] = {"leg_l": P(rot=(-25, 0, 0)), "leg_r": P(rot=(25, 0, 0)), "anel_a": P(rot=(0, 135, 0)),
                   "anel_b": P(rot=(0, 0, 135)), "arm_l": P(rot=(15, 0, 0)), "arm_r": P(rot=(-15, 0, 0))}
    ps["attack"] = {"nucleo": P(sc=1.5), "olho": P(sc=1.8), "anel_a": P(rot=(0, 180, 0), sp=1.6),
                    "anel_b": P(rot=(0, 0, 180), sp=1.6), "arm_l": P(rot=(-70, 0, -30)),
                    "arm_r": P(rot=(-70, 0, 30)), "coroa": P(sp=1.6, sc=1.3)}
    ps["special"] = {"nucleo": P(sc=0.8), "anel_a": P(rot=(0, 360, 0), sp=0.45), "anel_b": P(rot=(0, 0, 360), sp=0.45),
                     "arm_l": P(rot=(-95, 0, 15)), "arm_r": P(rot=(-95, 0, -15)), "coroa": P(sp=1.8),
                     "*": P(mov=(0, .4, 0))}
    ps["hurt"] = {"nucleo": P(sc=0.92), "*": P(rot=(-10, 0, 0), mov=(0, 0, -.1), piv=(0, 1.8, 0))}
    return dict(name="eclipse", id=5, scale=1.5, parts=parts, poses=ps)

# =====================================================================================
# SEMI-BOSSES
# =====================================================================================
def humanoid(name, mid, scale, torso, head, arm, leg, accent, glow, f=1.0, wide=1.0):
    parts = [
        B("torso", torso, (0, 2.0, 0), (1.0*wide, 1.2, 0.6)),
        B("cinto", accent, (0, 1.45, 0), (1.05*wide, 0.2, 0.65)),
        B("head", head, (0, 3.0, 0), (0.7, 0.7, 0.7)),
        B("olho_l", glow, (-0.18, 3.05, 0.36), (0.14, 0.1, 0.05), g="head", pv=(0, 2.7, 0), gl=True),
        B("olho_r", glow, (0.18, 3.05, 0.36), (0.14, 0.1, 0.05), g="head", pv=(0, 2.7, 0), gl=True),
    ]
    for sx, sd in ((-1, "l"), (1, "r")):
        parts += [
            B(f"braco_{sd}", arm, (0.72*sx*wide, 1.95, 0), (0.38, 1.2, 0.38), g=f"arm_{sd}", pv=(0.72*sx*wide, 2.55, 0)),
            B(f"manopla_{sd}", accent, (0.72*sx*wide, 1.45, 0), (0.44, 0.35, 0.44), g=f"arm_{sd}", pv=(0.72*sx*wide, 2.55, 0)),
            B(f"perna_{sd}", leg, (0.28*sx, 0.7, 0), (0.42, 1.4, 0.46), g=f"leg_{sd}", pv=(0.28*sx, 1.4, 0)),
        ]
    return parts

def thorgar():
    parts = humanoid("thorgar", 6, 1.6, "red_nether_bricks", "orange_terracotta", "orange_terracotta",
                     "nether_bricks", "netherite_block", "gold_block", wide=1.25)
    parts += [
        B("presa_l", "bone_block", (-0.2, 2.78, 0.38), (0.1, 0.2, 0.1), g="head", pv=(0, 2.7, 0)),
        B("presa_r", "bone_block", (0.2, 2.78, 0.38), (0.1, 0.2, 0.1), g="head", pv=(0, 2.7, 0)),
        B("chifre_l", "bone_block", (-0.45, 3.5, 0), (0.12, 0.5, 0.12), g="head", pv=(0, 2.7, 0), r0=(0, 0, 20)),
        B("chifre_r", "bone_block", (0.45, 3.5, 0), (0.12, 0.5, 0.12), g="head", pv=(0, 2.7, 0), r0=(0, 0, -20)),
        B("capa", "brown_wool", (0, 2.2, -0.42), (1.5, 1.6, 0.15), g="capa", pv=(0, 3.0, -0.4)),
        B("cabo", "dark_oak_log", (0.9, 1.6, 0.5), (0.14, 2.0, 0.14), g="arm_r", pv=(0.9, 2.55, 0)),
        B("lamina", "iron_block", (0.9, 2.55, 0.5), (0.12, 0.8, 0.8), g="arm_r", pv=(0.9, 2.55, 0)),
        B("fio", "gold_block", (0.9, 2.55, 0.92), (0.1, 0.8, 0.06), g="arm_r", pv=(0.9, 2.55, 0), gl=True),
    ]
    ps = std_poses(arm_up=140)
    merge(ps, "walk0", {"capa": P(rot=(12, 0, 0))}); merge(ps, "walk1", {"capa": P(rot=(18, 0, 0))})
    merge(ps, "attack", {"capa": P(rot=(30, 0, 0))})
    merge(ps, "special", {"capa": P(rot=(20, 0, 0)), "head": P(sc=1.15)})
    return dict(name="thorgar", id=6, scale=1.6, parts=parts, poses=ps)

def morvath():
    parts = humanoid("morvath", 7, 1.7, "deepslate_tiles", "bone_block", "black_wool", "black_wool",
                     "soul_lantern" if False else "cyan_concrete", "sea_lantern")
    parts += [
        B("capuz", "black_wool", (0, 3.1, -0.1), (0.9, 0.9, 0.9), g="head", pv=(0, 2.7, 0)),
        B("manto", "black_wool", (0, 1.0, 0), (1.15, 1.2, 0.7), g="manto", pv=(0, 1.6, 0)),
        B("cajado", "dark_oak_log", (0.85, 1.7, 0.5), (0.12, 2.6, 0.12), g="arm_r", pv=(0.72, 2.55, 0)),
        B("cajado_cranio", "skeleton_skull", (0.85, 3.2, 0.5), (0.5, 0.5, 0.5), g="arm_r", pv=(0.72, 2.55, 0)),
        B("cajado_alma", "sea_lantern", (0.85, 2.8, 0.5), (0.2, 0.2, 0.2), g="arm_r", pv=(0.72, 2.55, 0), gl=True),
    ]
    parts += ring("osso", "bone_block", 6, 1.3, 2.3, 0.22, "osso", gl=False)
    ps = std_poses(arm_up=60)
    merge(ps, "idle0", {"osso": P(rot=(0, 0, 0))}); merge(ps, "idle1", {"osso": P(rot=(0, 60, 0)), "*": P(mov=(0, .12, 0))})
    merge(ps, "walk0", {"osso": P(rot=(0, 90, 0))}); merge(ps, "walk1", {"osso": P(rot=(0, 150, 0))})
    merge(ps, "attack", {"osso": P(rot=(0, 270, 0), sp=1.7), "arm_r": P(rot=(-100, 0, 0))})
    merge(ps, "special", {"osso": P(rot=(0, 360, 0), sp=0.5, sc=1.5), "cajado_alma": P(sc=2.5)})
    return dict(name="morvath", id=7, scale=1.7, parts=parts, poses=ps)

def golem():
    parts = [
        B("torso", "basalt", (0, 2.7, 0), (2.4, 2.2, 1.6)),
        B("nucleo", "magma_block", (0, 2.7, 0.85), (1.0, 1.0, 0.12), gl=True),
        B("rachadura1", "magma_block", (-0.7, 3.3, 0.83), (0.2, 0.7, 0.1), gl=True),
        B("rachadura2", "magma_block", (0.8, 2.2, 0.83), (0.2, 0.8, 0.1), gl=True),
        B("head", "smooth_basalt", (0, 4.3, 0.1), (1.1, 0.9, 1.1)),
        B("olho", "shroomlight", (0, 4.35, 0.67), (0.7, 0.14, 0.08), g="head", pv=(0, 3.8, 0.1), gl=True),
        B("cristal_a", "amethyst_block", (-0.7, 4.0, -0.6), (0.3, 0.8, 0.3), g="costas", pv=(0, 3.5, -0.6), r0=(0, 0, 15)),
        B("cristal_b", "amethyst_block", (0.6, 4.2, -0.6), (0.3, 1.0, 0.3), g="costas", pv=(0, 3.5, -0.6), r0=(0, 0, -15)),
    ]
    for sx, sd in ((-1, "l"), (1, "r")):
        parts += [
            B(f"braco_{sd}", "basalt", (1.6*sx, 2.3, 0), (0.9, 2.4, 0.9), g=f"arm_{sd}", pv=(1.6*sx, 3.5, 0)),
            B(f"punho_{sd}", "smooth_basalt", (1.6*sx, 1.0, 0), (1.2, 1.0, 1.2), g=f"arm_{sd}", pv=(1.6*sx, 3.5, 0)),
            B(f"perna_{sd}", "smooth_basalt", (0.65*sx, 0.85, 0), (1.0, 1.7, 1.1), g=f"leg_{sd}", pv=(0.65*sx, 1.7, 0)),
        ]
    ps = std_poses(lean=(0, 1.7, 0), arm_up=145)
    merge(ps, "idle1", {"nucleo": P(sc=1.25), "costas": P(rot=(0, 0, 2))})
    merge(ps, "special", {"nucleo": P(sc=1.7), "costas": P(sc=1.3), "rachadura1": P(sc=1.8), "rachadura2": P(sc=1.8)})
    return dict(name="golem", id=8, scale=2.0, parts=parts, poses=ps)

def valeria():
    parts = humanoid("valeria", 9, 1.5, "black_concrete", "black_concrete", "black_concrete", "black_concrete",
                     "purple_concrete", "crying_obsidian")
    parts += [
        B("capa", "black_wool", (0, 1.9, -0.38), (1.1, 2.1, 0.12), g="capa", pv=(0, 3.0, -0.35)),
        B("lamina_l", "crying_obsidian", (-0.72, 1.3, 0.55), (0.1, 1.6, 0.12), g="arm_l", pv=(-0.72, 2.55, 0), gl=True),
        B("lamina_r", "crying_obsidian", (0.72, 1.3, 0.55), (0.1, 1.6, 0.12), g="arm_r", pv=(0.72, 2.55, 0), gl=True),
        B("guarda_l", "amethyst_block", (-0.72, 1.55, 0.4), (0.4, 0.1, 0.1), g="arm_l", pv=(-0.72, 2.55, 0)),
        B("guarda_r", "amethyst_block", (0.72, 1.55, 0.4), (0.4, 0.1, 0.1), g="arm_r", pv=(0.72, 2.55, 0)),
    ]
    ps = std_poses(arm_up=100)
    for p in ("walk0", "walk1"):
        ps[p]["*"] = P(rot=(14, 0, 0), piv=(0, 1.4, 0))
    merge(ps, "walk0", {"capa": P(rot=(25, 0, 0))}); merge(ps, "walk1", {"capa": P(rot=(35, 0, 0))})
    ps["attack"] = {"arm_l": P(rot=(-100, 0, -30)), "arm_r": P(rot=(-100, 0, 30)), "capa": P(rot=(40, 0, 0)),
                    "*": P(rot=(28, 0, 0), piv=(0, 1.4, 0), mov=(0, 0, .3))}
    ps["special"] = {"arm_l": P(rot=(-30, 0, -110)), "arm_r": P(rot=(-30, 0, 110)), "capa": P(rot=(20, 0, 0)),
                     "lamina_l": P(sc=1.4), "lamina_r": P(sc=1.4), "*": P(mov=(0, .2, 0))}
    return dict(name="valeria", id=9, scale=1.5, parts=parts, poses=ps)

# =====================================================================================
# PILARES / FORJAS (base: armor_stand)
# =====================================================================================
def pilar_raiz():
    parts = [
        B("tronco", "oak_log", (0, 1.2, 0), (0.9, 2.4, 0.9)),
        B("raizes", "mangrove_roots", (0, 0.2, 0), (1.5, 0.4, 1.5)),
        B("copa", "azalea_leaves", (0, 2.8, 0), (1.5, 1.0, 1.5), pv=(0, 2.3, 0)),
        B("seiva", "verdant_froglight", (0, 1.6, 0.46), (0.3, 0.9, 0.1), gl=True),
        B("seiva_t", "verdant_froglight", (0, 1.6, -0.46), (0.3, 0.9, 0.1), g="seiva", gl=True),
    ]
    ps = {p: {} for p in POSES}
    ps["idle1"] = {"copa": P(rot=(0, 0, 4)), "seiva": P(sc=1.4)}
    ps["walk0"] = ps["idle0"]; ps["walk1"] = ps["idle1"]
    ps["attack"] = {"copa": P(sc=1.3), "seiva": P(sc=1.8)}
    ps["special"] = {"copa": P(rot=(0, 0, -6), sc=1.15)}
    ps["hurt"] = {"*": P(rot=(0, 0, 6), piv=(0, 0, 0)), "copa": P(rot=(0, 0, 8))}
    return dict(name="pilar_raiz", id=10, scale=2.2, parts=parts, poses=ps)

def forja():
    parts = [
        B("base", "magma_block", (0, 0.3, 0), (2.0, 0.6, 2.0)),
        B("fornalha", "blast_furnace", (0, 1.4, 0), (1.8, 1.6, 1.8), st={"facing": "south", "lit": "true"}, gl=True),
        B("chamine", "polished_blackstone_bricks", (0.5, 2.7, -0.4), (0.5, 1.2, 0.5)),
        B("brasa", "shroomlight", (0, 2.45, 0), (0.9, 0.2, 0.9), gl=True),
        B("bigorna", "iron_block", (0, 2.75, 0.2), (0.6, 0.35, 0.9), g="bigorna", pv=(0, 2.7, 0)),
    ]
    ps = {p: {} for p in POSES}
    ps["idle1"] = {"brasa": P(sc=1.3, mov=(0, .1, 0)), "bigorna": P(rot=(0, 20, 0))}
    ps["walk0"] = ps["idle0"]; ps["walk1"] = ps["idle1"]
    ps["attack"] = {"brasa": P(sc=1.8), "bigorna": P(rot=(0, 90, 0))}
    ps["special"] = {"brasa": P(sc=1.5)}
    ps["hurt"] = {"*": P(mov=(0, -.05, 0)), "bigorna": P(rot=(0, 45, 0))}
    return dict(name="forja", id=11, scale=1.4, parts=parts, poses=ps)

def pilar_vazio():
    parts = [
        B("coluna", "obsidian", (0, 1.4, 0), (0.9, 2.8, 0.9)),
        B("topo", "crying_obsidian", (0, 2.9, 0), (1.2, 0.3, 1.2), gl=True),
        B("cristal", "amethyst_block", (0, 3.8, 0), (0.7, 0.7, 0.7), gl=True),
    ]
    parts += ring("orbita", "crying_obsidian", 4, 0.9, 3.8, 0.18, "orbita", gl=True)
    ps = {p: {} for p in POSES}
    ps["idle0"] = {"cristal": P(rot=(0, 0, 0)), "orbita": P(rot=(0, 0, 0))}
    ps["idle1"] = {"cristal": P(rot=(45, 45, 0), mov=(0, .2, 0)), "orbita": P(rot=(0, 90, 0))}
    ps["walk0"] = ps["idle0"]; ps["walk1"] = ps["idle1"]
    ps["attack"] = {"cristal": P(rot=(90, 90, 0), sc=1.5), "orbita": P(rot=(0, 180, 0), sp=1.6)}
    ps["special"] = {"cristal": P(rot=(0, 180, 0), sc=1.3), "orbita": P(rot=(0, 360, 0))}
    ps["hurt"] = {"cristal": P(sc=0.8), "*": P(mov=(0, -.04, 0))}
    return dict(name="pilar_vazio", id=12, scale=2.0, parts=parts, poses=ps)

MODELS = [verdelith(), thalassa(), korvan(), seraphel(), eclipse(), thorgar(), morvath(), golem(), valeria(),
          pilar_raiz(), forja(), pilar_vazio()]

# ----------------------------- compilação de transformações -----------------------------
def fl(v): return f"{v:.4f}f"
def vec(v): return "[" + ",".join(fl(x) for x in v) + "]"

def compile_part(part, spec):
    g = part["g"]
    sp = spec.get(g) or spec.get(part["n"]) or {}
    gl = spec.get("*") or {}
    rot = sp.get("rot", (0, 0, 0)); mov = sp.get("mov", (0, 0, 0))
    sc = sp.get("sc", (1, 1, 1)); spread = sp.get("sp", 1.0)
    c = part["c"]; pv = part["pv"] or c
    S = (part["s"][0]*sc[0], part["s"][1]*sc[1], part["s"][2]*sc[2])
    c1 = vadd(pv, vmul(vsub(c, pv), spread))
    qp = qeuler(*rot)
    c1 = vadd(pv, qrot(qp, vsub(c1, pv)))
    c1 = vadd(c1, mov)
    q = qmul(qp, qeuler(*part["r0"]))
    if gl:
        gp = gl.get("piv", (0, 0, 0)); qg = qeuler(*gl.get("rot", (0, 0, 0)))
        c1 = vadd(gp, qrot(qg, vsub(c1, gp)))
        c1 = vadd(c1, gl.get("mov", (0, 0, 0)))
        q = qmul(qg, q)
    T = vsub(c1, qrot(q, vmul(S, 0.5))) if part["k"] == "b" else c1
    return ("{left_rotation:%s,right_rotation:[0.0f,0.0f,0.0f,1.0f],translation:%s,scale:%s}"
            % (vec(q), vec(T), vec(S)))

def tag(model, part): return f"aur_{model['name']}_{part['n']}"

def disp_type(part): return "block_display" if part["k"] == "b" else "item_display"

# ----------------------------- geração dos arquivos -----------------------------
def write(path, text):
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(text)

def main():
    if os.path.isdir(OUT): shutil.rmtree(OUT)
    write("pack.mcmeta", '{\n  "pack": {\n    "id": "aurelion_modelos",\n    "min_format": 121,\n    "max_format": 121,\n'
                         '    "description": "Aurelion - modelos e animacoes customizadas dos bosses"\n  }\n}\n')
    write("data/minecraft/tags/function/tick.json", '{"values":["aurelion:tick"]}\n')
    write("data/minecraft/tags/function/load.json", '{"values":["aurelion:load"]}\n')
    F = "data/aurelion/function/"
    bossbar_defs = [
        (1, "boss_1", "green", "notched_10", "§a§lVerdelith, o Guardião do Musgo"),
        (2, "boss_2", "blue", "notched_10", "§b§lThalassa, Rainha das Marés"),
        (3, "boss_3", "red", "notched_10", "§c§lKorvan, o Ferreiro Caído"),
        (4, "boss_4", "pink", "notched_10", "§d§lSeraphel, o Oráculo Quebrado"),
        (5, "boss_5", "purple", "notched_20", "§5§lO Eclipse"),
        (6, "semi_1", "red", "notched_6", "§c§l⚔ Thorgar, o Carniceiro dos Ermos"),
        (7, "semi_2", "blue", "notched_6", "§9§l☠ Morvath, o Necromante da Cripta"),
        (8, "semi_3", "yellow", "notched_6", "§6§l⛰ Gólem Esquecido de Basalto"),
        (9, "semi_4", "purple", "notched_6", "§5§l🗡 Valeria, a Lâmina Sombria"),
    ]
    bb_init_lines = []
    for mid, bbid, bcol, bsty, btitle in bossbar_defs:
        bb_init_lines += [
            f'bossbar add aurelion:{bbid} "{btitle}"',
            f'bossbar set aurelion:{bbid} color {bcol}',
            f'bossbar set aurelion:{bbid} style {bsty}',
            f'bossbar set aurelion:{bbid} visible false',
        ]
    write(F + "load.mcfunction",
          "\n".join(f"scoreboard objectives add {o} dummy" for o in
                    ["aur_id", "aur_model", "aur_ph", "aur_cyc", "aur_hold", "aur_anim", "aur_ttl", "aur_px", "aur_pz", "aur_tmp", "aur_phase", "aur_shield"])
          + "\nexecute unless score #next aur_id matches 0.. run scoreboard players set #next aur_id 0\n"
          + "gamerule send_command_feedback false\n"
          + "gamerule command_block_output false\n"
          + "\n".join(bb_init_lines) + "\n")

    tick_cleanup = []
    for mid, bbid, bcol, bsty, btitle in bossbar_defs:
        tick_cleanup += [
            f"execute unless entity @e[tag=aur_base,scores={{aur_model={mid}}}] run bossbar set aurelion:{bbid} visible false",
            f"execute unless entity @e[tag=aur_base,scores={{aur_model={mid}}}] run bossbar set aurelion:{bbid} players",
        ]
    write(F + "tick.mcfunction",
          "execute as @e[tag=aur_base] at @s run function aurelion:base_tick\n"
          "execute as @e[tag=aur_part,tag=!aur_dying] run function aurelion:part_tick\n"
          "execute as @e[tag=aur_part,tag=aur_dying] run function aurelion:part_dying\n"
          + "\n".join(tick_cleanup) + "\n")

    bb_tick_lines = []
    for mid, bbid, bcol, bsty, btitle in bossbar_defs:
        bb_tick_lines += [
            f"execute if score @s aur_model matches {mid} store result bossbar aurelion:{bbid} value run data get entity @s Health 10",
            f"execute if score @s aur_model matches {mid} store result bossbar aurelion:{bbid} max run attribute @s minecraft:max_health get 10",
            f"execute if score @s aur_model matches {mid} run bossbar set aurelion:{bbid} players @a[distance=..70]",
            f"execute if score @s aur_model matches {mid} run bossbar set aurelion:{bbid} visible true",
        ]

    write(F + "base_tick.mcfunction", """# executado AS base AT @s, todo tick
execute if data entity @s {Health:0.0f} run return run function aurelion:base_dead
scoreboard players operation #cur aur_id = @s aur_id
execute as @e[tag=aur_part,tag=!aur_dying,distance=..30] if score @s aur_id = #cur aur_id run function aurelion:part_follow
# atualização em tempo real da barra de vida do boss (20x por segundo)
""" + "\n".join(bb_tick_lines) + """
# detecção de movimento (centésimos de bloco por tick)
execute store result score #nx aur_tmp run data get entity @s Pos[0] 100
execute store result score #nz aur_tmp run data get entity @s Pos[2] 100
scoreboard players operation #dx aur_tmp = #nx aur_tmp
scoreboard players operation #dx aur_tmp -= @s aur_px
scoreboard players operation #dz aur_tmp = #nz aur_tmp
scoreboard players operation #dz aur_tmp -= @s aur_pz
scoreboard players operation @s aur_px = #nx aur_tmp
scoreboard players operation @s aur_pz = #nz aur_tmp
scoreboard players set #mv aur_tmp 0
execute if score #dx aur_tmp matches 3.. run scoreboard players set #mv aur_tmp 1
execute if score #dx aur_tmp matches ..-3 run scoreboard players set #mv aur_tmp 1
execute if score #dz aur_tmp matches 3.. run scoreboard players set #mv aur_tmp 1
execute if score #dz aur_tmp matches ..-3 run scoreboard players set #mv aur_tmp 1
# dano recebido -> pose "hurt" (se nenhuma animação em curso)
execute if data entity @s {HurtTime:10s} unless score @s aur_hold matches 1.. unless score @s aur_anim matches 4.. run scoreboard players set @s aur_anim 6
execute if score @s aur_anim matches 4.. run function aurelion:base_anim
execute if score @s aur_hold matches 1.. run scoreboard players remove @s aur_hold 1
execute if score @s aur_hold matches 0 run function aurelion:base_cycle
""")
    write(F + "part_follow.mcfunction", "tp @s ~ ~ ~ ~ 0\nscoreboard players set @s aur_ttl 6\n")
    write(F + "base_dead.mcfunction", """scoreboard players operation #cur aur_id = @s aur_id
execute as @e[tag=aur_part,tag=!aur_dying,distance=..30] if score @s aur_id = #cur aur_id run scoreboard players set @s aur_ttl 0
""")
    write(F + "base_anim.mcfunction", """scoreboard players operation #pose aur_tmp = @s aur_anim
scoreboard players set @s aur_anim 0
scoreboard players set @s aur_hold 16
execute if score #pose aur_tmp matches 6 run scoreboard players set @s aur_hold 5
scoreboard players set @s aur_cyc 10
function aurelion:dispatch
""")
    write(F + "base_cycle.mcfunction", """scoreboard players add @s aur_cyc 1
execute if score @s aur_cyc matches 10.. run function aurelion:base_step
""")
    write(F + "base_step.mcfunction", """scoreboard players set @s aur_cyc 0
scoreboard players set #t aur_tmp 0
execute if score @s aur_ph matches 0 run scoreboard players set #t aur_tmp 1
scoreboard players operation @s aur_ph = #t aur_tmp
scoreboard players set #pose aur_tmp 0
execute if score #mv aur_tmp matches 1 run scoreboard players set #pose aur_tmp 2
scoreboard players operation #pose aur_tmp += @s aur_ph
function aurelion:dispatch
""")
    write(F + "part_tick.mcfunction", "scoreboard players remove @s aur_ttl 1\nexecute if score @s aur_ttl matches ..0 at @s run function aurelion:part_die\n")
    write(F + "part_die.mcfunction", """tag @s add aur_dying
scoreboard players set @s aur_ttl 24
data merge entity @s {start_interpolation:0,interpolation_duration:20,transformation:{scale:[0.0f,0.0f,0.0f]}}
particle minecraft:poof ~ ~ ~ 0.3 0.3 0.3 0.02 4
""")
    write(F + "part_dying.mcfunction", "scoreboard players remove @s aur_ttl 1\nexecute if score @s aur_ttl matches ..0 run kill @s\n")
    write(F + "attach_fin.mcfunction", """scoreboard players operation @s aur_id = #next aur_id
scoreboard players set @s aur_ttl 20
tag @s remove aur_new
""")
    remover_lines = ["kill @e[tag=aur_part]", "tag @e[tag=aur_base] remove aur_base"]
    for mid, bbid, bcol, bsty, btitle in bossbar_defs:
        remover_lines.append(f"bossbar set aurelion:{bbid} visible false")
        remover_lines.append(f"bossbar set aurelion:{bbid} players")
    write(F + "remover_todos.mcfunction", "\n".join(remover_lines) + "\n")

    # Funções de atualização de fase e escudo nas Bossbars dos 5 Guardiões
    bb_map = {mid: (bbid, bcol, bsty, btitle) for mid, bbid, bcol, bsty, btitle in bossbar_defs}
    for mid in range(1, 6):
        bbid, bcol, bsty, btitle = bb_map[mid]
        write(F + f"bossbar/fase1_{mid}.mcfunction",
              f'bossbar set aurelion:{bbid} color {bcol}\n'
              f'bossbar set aurelion:{bbid} style {bsty}\n'
              f'bossbar set aurelion:{bbid} name "{btitle} §7[Fase I]"\n')
        write(F + f"bossbar/fase2_{mid}.mcfunction",
              f'bossbar set aurelion:{bbid} color {bcol}\n'
              f'bossbar set aurelion:{bbid} name "{btitle} §e[Fase II - Despertar]"\n')
        write(F + f"bossbar/fase3_{mid}.mcfunction",
              f'bossbar set aurelion:{bbid} color {bcol}\n'
              f'bossbar set aurelion:{bbid} name "{btitle} §c[Fase III - Fúria]"\n')
        write(F + f"bossbar/escudo_on_{mid}.mcfunction",
              f'bossbar set aurelion:{bbid} color yellow\n'
              f'bossbar set aurelion:{bbid} name "§e§l🛡 [ESCUDO ATIVO: DESTRUA OS PILARES] {btitle}"\n')
        write(F + f"bossbar/escudo_off_{mid}.mcfunction",
              f'bossbar set aurelion:{bbid} color {bcol}\n'
              f'bossbar set aurelion:{bbid} name "{btitle} §e[Escudo Quebrado!]"\n')

    dispatch = []
    for m in MODELS:
        ps = m["poses"]
        # attach
        lines = ["tag @s add aur_base", "scoreboard players add #next aur_id 1",
                 "scoreboard players operation @s aur_id = #next aur_id",
                 f"scoreboard players set @s aur_model {m['id']}",
                 "scoreboard players set @s aur_ph 0", "scoreboard players set @s aur_cyc 0",
                 "scoreboard players set @s aur_hold 0", "scoreboard players set @s aur_anim 0",
                 "scoreboard players set @s aur_px 0", "scoreboard players set @s aur_pz 0",
                 "effect give @s minecraft:invisibility infinite 0 true",
                 f"attribute @s minecraft:scale base set {m['scale']}",
                 "item replace entity @s weapon.mainhand with minecraft:air",
                 "item replace entity @s weapon.offhand with minecraft:air"]
        if m["id"] in bb_map:
            bbid, bcol, bsty, btitle = bb_map[m["id"]]
            suf = " §7[Fase I]" if m["id"] <= 5 else " §7[Caçada]"
            lines += [
                f'bossbar add aurelion:{bbid} "{btitle}{suf}"',
                f'bossbar set aurelion:{bbid} color {bcol}',
                f'bossbar set aurelion:{bbid} style {bsty}',
                f'bossbar set aurelion:{bbid} name "{btitle}{suf}"',
                f'bossbar set aurelion:{bbid} visible true',
            ]
        for part in m["parts"]:
            tr = compile_part(part, {})
            tags = f'["aur_part","aur_new","{tag(m, part)}"]'
            br = ',brightness:{block:15,sky:15}' if part["gl"] else ""
            if part["k"] == "b":
                body = f'block_state:"minecraft:{part["id"]}"'
            else:
                body = 'item:{id:"minecraft:%s",count:1},item_display:"none"' % part["id"]
            lines.append(f"summon minecraft:{disp_type(part)} ~ ~ ~ {{Tags:{tags},{body},transformation:{tr},"
                         f"teleport_duration:2,interpolation_duration:0,view_range:2.0f{br}}}")
        lines.append("execute as @e[tag=aur_new,distance=..3] run function aurelion:attach_fin")
        write(F + f"attach/{m['name']}.mcfunction", "\n".join(lines) + "\n")
        # poses
        for pi, pname in enumerate(POSES):
            spec = ps.get(pname, {})
            out = []
            for part in m["parts"]:
                tr = compile_part(part, spec)
                out.append(f"execute as @e[type=minecraft:{disp_type(part)},tag={tag(m, part)},distance=..30] "
                           f"if score @s aur_id = #cur aur_id run data merge entity @s "
                           f"{{start_interpolation:0,interpolation_duration:{DUR[pname]},transformation:{tr}}}")
            write(F + f"pose/{m['name']}/{pname}.mcfunction", "\n".join(out) + "\n")
            dispatch.append(f"execute if score @s aur_model matches {m['id']} if score #pose aur_tmp matches {pi} "
                            f"run function aurelion:pose/{m['name']}/{pname}")
    write(F + "dispatch.mcfunction", "\n".join(dispatch) + "\n")
    write(F + "dar_livro_lore.mcfunction",
          'give @s minecraft:written_book[minecraft:written_book_content={title:"Crônicas de Aurelion",author:"Valdric, o Alquimista-Rei",pages:['
          '"§6§lCRÔNICAS DE AURELION§r\\n§8Por Valdric, Alquimista-Rei\\n\\nHá mil anos, o reino brilhava sob a §6Chama-Coração§r. Um cristal vivo que nutria colheitas, erguia cidades e gerava prosperidade. Nós, a Ordem do Fio de Ouro, éramos seus guardiões juramentados.",'
          '"§6§lOS GÊMEOS§r\\n\\nCriei dois aprendizes como meus filhos legítimos:\\n\\nO §2Cartógrafo (Pedro)§r: desbravador de horizontes, construtor de lares, alma ligada à terra e aos animais.\\n\\nO §1Estrategista (Ellias)§r: mestre do combate, artífice de armas e guardião das finanças imperiais.",'
          '"§6§lA RUPTURA§r\\n\\nQuando a doença tocou meu peito, tentei drenar a Chama para viver. Meus filhos entraram em desespero.\\n\\nO Cartógrafo puxou a lâmina para §cdestruir o cristal§r.\\nO Estrategista ergueu o escudo para §asalvar meu corpo§r.\\n\\nA Chama explodiu. O reino ruiu em cinzas.",'
          '"§6§lOS RITUAIS DOS GUARDIÕES§r\\n\\nSegure uma §6Bússola§r e clique com botão direito para achar os Santuários:\\n§21. Verdelith§r: Ateie fogo na mata ou sacrifique um animal.\\n§32. Thalassa§r: Lance Coração do Mar, Concha ou Diamante na água.\\n§43. Korvan§r: Jogue Bloco de Ouro/Ferro na lava ou bata na Bigorna.",'
          '"§6§lSACRIFÍCIOS FINAIS§r\\n\\n§54. Seraphel§r: Nos Picos Congelados, salte para a morte (o Oráculo absorverá seu sacrifício!) ou lance uma Pérola/Ametista.\\n\\n§85. O Eclipse§r: Nas profundezas do Deep Dark, um irmão deve §cderramar seu sangue (morrer)§r no Santuário para despertar a sombra!",'
          '"§6§lO DILEMA FINAL§r\\n\\nAo derrotar o Eclipse, segurem o §6Coração da Chama§r e cliquem com o botão direito para decidir em consenso:\\n\\n§6§l1. RESTAURAR A CHAMA§r\\nReerguer o Império como Novos Reis.\\n\\n§5§l2. LIBERTAR O MUNDO§r\\nDespedaçar o cristal e viver como Lendas Livres."'
          ']}] 1\n')
    # Funções de partículas para ataques e rituais
    write(F + "fx/ritual_despertar.mcfunction",
          "particle minecraft:totem_of_undying ~ ~1.2 ~ 1.2 1.5 1.2 0.25 80 force\n"
          "particle minecraft:soul_fire_flame ~ ~0.5 ~ 1.5 0.5 1.5 0.08 50 force\n"
          "particle minecraft:end_rod ~ ~2.0 ~ 1.0 2.0 1.0 0.1 40 force\n")
    write(F + "fx/espinhos_verdelith.mcfunction",
          "particle minecraft:spore_blossom_air ~ ~1.5 ~ 2.5 1.2 2.5 0.05 45 force\n"
          "particle minecraft:happy_villager ~ ~1.0 ~ 2.0 1.0 2.0 0.1 25 force\n")
    write(F + "fx/jato_thalassa.mcfunction",
          "particle minecraft:splash ~ ~1.2 ~ 2.5 1.0 2.5 0.2 60 force\n"
          "particle minecraft:bubble_pop ~ ~1.2 ~ 2.0 1.0 2.0 0.1 35 force\n"
          "particle minecraft:snowflake ~ ~1.5 ~ 2.0 1.0 2.0 0.05 25 force\n")
    write(F + "fx/chamas_korvan.mcfunction",
          "particle minecraft:flame ~ ~1.0 ~ 2.5 0.8 2.5 0.08 50 force\n"
          "particle minecraft:lava ~ ~1.2 ~ 1.8 1.0 1.8 0.1 25 force\n"
          "particle minecraft:large_smoke ~ ~1.8 ~ 2.0 1.2 2.0 0.05 30 force\n")
    write(F + "fx/luz_seraphel.mcfunction",
          "particle minecraft:end_rod ~ ~1.5 ~ 2.5 1.5 2.5 0.12 45 force\n"
          "particle minecraft:snowflake ~ ~1.2 ~ 2.5 1.0 2.5 0.08 35 force\n"
          "particle minecraft:enchant ~ ~2.0 ~ 2.0 1.5 2.0 0.5 50 force\n")
    write(F + "fx/vazio_eclipse.mcfunction",
          "particle minecraft:sculk_soul ~ ~1.2 ~ 2.5 1.2 2.5 0.08 45 force\n"
          "particle minecraft:soul_fire_flame ~ ~0.8 ~ 2.5 0.8 2.5 0.06 40 force\n"
          "particle minecraft:sonic_boom ~ ~1.5 ~ 0 0 0 0 1 force\n")
    # Feixe Sônico direcional (Fus-Ro-Dah / Ataque Sonar do Warden) lançado na direção exata do olhar (^ ^ ^dist)
    fus_lines = [
        "# Executado AS jogador AT @s ANCHORED EYES",
        "playsound minecraft:entity.warden.sonic_boom master @a[distance=..32] ~ ~ ~ 2.0 0.85",
    ]
    for d in (1.5, 3.0, 4.5, 6.0, 7.5, 9.0, 10.5, 12.0, 13.5, 15.0, 16.5, 18.0):
        fus_lines.append(f"particle minecraft:sonic_boom ^ ^ ^{d:.1f} 0 0 0 0 1 force")
        if d in (3.0, 7.5, 12.0, 16.5):
            fus_lines.append(f"particle minecraft:gust ^ ^ ^{d:.1f} 0.35 0.35 0.35 0 2 force")
            fus_lines.append(f"particle minecraft:soul_fire_flame ^ ^ ^{d:.1f} 0.25 0.25 0.25 0.03 5 force")
    write(F + "fus_ro_dah.mcfunction", "\n".join(fus_lines) + "\n")
    total = sum(len(m["parts"]) for m in MODELS)
    print(f"Datapack gerado em {OUT}: {len(MODELS)} modelos, {total} peças.")

if __name__ == "__main__":
    main()
