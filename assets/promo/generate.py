#!/usr/bin/env python3
"""
aniket-a14 — terminal profile hero.

Renders `aniket-terminal.gif`: a looping sequence that opens with a shell
login, runs a query through Wizard's ingest/retrieve/reason/answer pipeline,
fans out into the project graph, walks the trajectory that led here, and
signs off.

One accent color is spent, once per scene, on whatever is "live" right now
(the active pipeline stage, the current project, today on the timeline).
Everything else lives on a neutral gray ramp.

Deps: pillow >= 10
Run:  python3 generate.py
"""

from __future__ import annotations

import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

# --------------------------------------------------------------------------
# Canvas
# --------------------------------------------------------------------------

W, H = 960, 480
SS = 2  # supersample factor, discarded on export
FW, FH = W * SS, H * SS

FPS = 20
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "aniket-terminal.gif")

RNG = random.Random(14)

def S(v: float) -> float:
    return v * SS

# --------------------------------------------------------------------------
# Palette
# --------------------------------------------------------------------------

BG      = (0x0b, 0x0c, 0x10)
LINE    = (0x24, 0x27, 0x31)
FAINT   = (0x50, 0x55, 0x62)
MUTED   = (0x7a, 0x80, 0x8f)
BODY    = (0xa8, 0xad, 0xba)
HEADING = (0xe8, 0xea, 0xef)
ACCENT  = (0x9b, 0x8c, 0xf5)
WHITE   = (0xff, 0xff, 0xff)

FONT_PATH = "/System/Library/Fonts/Menlo.ttc"

def font(size, bold=False):
    return ImageFont.truetype(FONT_PATH, int(size * SS), index=1 if bold else 0)

# --------------------------------------------------------------------------
# Background texture (precomputed once, reused every frame)
# --------------------------------------------------------------------------

GLYPHS = list("λΣ∞◇○□△≈+×÷⋅⟨⟩01∇∂μφψ")

def make_texture():
    tex = Image.new("RGBA", (FW, FH), (0, 0, 0, 0))
    d = ImageDraw.Draw(tex)
    f = font(13)
    rng = random.Random(7)
    for _ in range(46):
        x = rng.uniform(0.05, 0.97) * FW
        y = rng.uniform(0.03, 0.55) * FH
        g = rng.choice(GLYPHS)
        a = rng.randint(6, 16)
        d.text((x, y), g, font=f, fill=(*FAINT, a))
    return tex

def make_vignette():
    vg = Image.new("L", (FW, FH), 0)
    d = ImageDraw.Draw(vg)
    cx, cy = FW * 0.5, FH * 0.38
    maxr = math.hypot(FW, FH) * 0.62
    steps = 48
    for i in range(steps, 0, -1):
        t = i / steps
        r = maxr * t
        val = int(14 * (1 - t))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=val)
    return vg.filter(ImageFilter.GaussianBlur(S(40)))

TEXTURE = make_texture()
VIGNETTE = make_vignette()

# --------------------------------------------------------------------------
# Chrome: corner brackets + footer caption bar
# --------------------------------------------------------------------------

MARGIN = 32
BRACKET = 18

def draw_chrome(img: Image.Image, draw: ImageDraw.ImageDraw, caption_l: str, caption_r: str, caption_alpha=255):
    # background
    draw.rectangle([0, 0, FW, FH], fill=BG)
    # soft vignette lightening
    img.paste(Image.new("RGB", (FW, FH), (18, 19, 24)), (0, 0), VIGNETTE)
    img.alpha_composite(TEXTURE) if img.mode == "RGBA" else img.paste(TEXTURE, (0, 0), TEXTURE)

    m, b = S(MARGIN), S(BRACKET)
    for (x, y, dx, dy) in [(m, m, 1, 1), (FW - m, m, -1, 1)]:
        draw.line([(x, y), (x, y + b * dy)], fill=LINE, width=max(1, int(S(1))))
        draw.line([(x, y), (x + b * dx, y)], fill=LINE, width=max(1, int(S(1))))

    rule_y = FH - S(56)
    draw.line([(m, rule_y), (FW - m, rule_y)], fill=LINE, width=max(1, int(S(1))))

    f = font(13)
    cap_col = fade(MUTED, caption_alpha) if caption_alpha < 255 else MUTED
    draw.text((m, rule_y + S(14)), caption_l, font=f, fill=cap_col)
    w = draw.textlength(caption_r, font=f)
    draw.text((FW - m - w, rule_y + S(14)), caption_r, font=f, fill=cap_col)

# --------------------------------------------------------------------------
# Text helpers
# --------------------------------------------------------------------------

def typewriter(s: str, t: float) -> str:
    n = max(0, min(len(s), int(round(len(s) * t))))
    return s[:n]

def ease_out(t: float) -> float:
    return 1 - (1 - t) ** 3

def ease_in_out(t: float) -> float:
    return 0.5 - 0.5 * math.cos(math.pi * max(0, min(1, t)))

def clamp01(t):
    return max(0.0, min(1.0, t))

def fade(color, alpha255, base=BG):
    """Blend color toward base as if it had alpha255/255 opacity.

    ImageDraw does not alpha-composite RGBA fills onto an RGBA image (it
    overwrites pixels), and the final frame is flattened to RGB anyway — so
    fades must be pre-blended into a solid color rather than passed as an
    alpha channel.
    """
    k = clamp01(alpha255 / 255)
    return tuple(int(round(base[i] + (color[i] - base[i]) * k)) for i in range(3))

# --------------------------------------------------------------------------
# Scenes
# --------------------------------------------------------------------------
# Each scene is (n_frames, draw_fn(draw, img, t)) where t in [0, 1] is local progress.

ORIGIN_X = S(56)
TOP_Y = S(60)

def scene_login(draw, img, t):
    draw_chrome(img, draw, "session", "aniketdesign.in")
    f = font(20)
    fs = font(16)
    line1 = "aniket-a14 on main [wizard]"
    y = TOP_Y
    draw.text((ORIGIN_X, y), typewriter(line1, clamp01(t / 0.22)), font=f, fill=MUTED)

    y2 = y + S(40)
    t2 = clamp01((t - 0.22) / 0.30)
    if t2 > 0:
        arrow = "→ "
        cmd = "ssh aniket@aniketdesign.in"
        draw.text((ORIGIN_X, y2), arrow, font=f, fill=ACCENT)
        aw = draw.textlength(arrow, font=f)
        draw.text((ORIGIN_X + aw, y2), typewriter(cmd, t2), font=f, fill=HEADING)

    t3 = clamp01((t - 0.55) / 0.20)
    if t3 > 0:
        y3 = y2 + S(36)
        label = "handshake"
        draw.text((ORIGIN_X + S(20), y3), label, font=fs, fill=MUTED)
        dotsw = S(230)
        lw = draw.textlength(label, font=fs)
        dots_n = int(18 * ease_out(clamp01(t3 / 0.7)))
        draw.text((ORIGIN_X + S(20) + lw + S(14), y3), "." * dots_n, font=fs, fill=FAINT)
        if t3 > 0.75:
            ok_a = int(255 * clamp01((t3 - 0.75) / 0.25))
            draw.text((ORIGIN_X + S(20) + lw + dotsw, y3), "ok", font=fs, fill=fade(HEADING, ok_a))


def scene_prompt_pause(draw, img, t):
    draw_chrome(img, draw, "session", "aniketdesign.in")
    f = font(20)
    blink = int(t * 6) % 2 == 0
    cursor = "█" if blink else " "
    draw.text((ORIGIN_X, TOP_Y), "→ " + cursor, font=f, fill=ACCENT)


PIPELINE_STAGES = ["ingest", "retrieve", "reason", "answer"]

def scene_pipeline(draw, img, t):
    draw_chrome(img, draw, "agent pipeline", "wizard")
    f = font(19)
    header = "→ run wizard --query policy.pdf"
    th = clamp01(t / 0.18)
    draw.text((ORIGIN_X, TOP_Y), typewriter(header, th), font=f, fill=MUTED)

    n = len(PIPELINE_STAGES)
    box_w, box_h = S(170), S(56)
    gap = S(56)
    total_w = n * box_w + (n - 1) * gap
    start_x = (FW - total_w) / 2
    y = S(240)

    seq_t = clamp01((t - 0.22) / 0.68)
    fb = font(16)
    for i, name in enumerate(PIPELINE_STAGES):
        x0 = start_x + i * (box_w + gap)
        x1 = x0 + box_w
        y0, y1 = y - box_h / 2, y + box_h / 2

        stage_progress = clamp01((seq_t - i / n) * n * 1.3)
        active = stage_progress > 0.05 and stage_progress < 1.0
        done = stage_progress >= 1.0

        col = LINE
        text_col = MUTED
        if active or done:
            col = ACCENT if active else FAINT
            text_col = HEADING if (active or done) else MUTED

        draw.rounded_rectangle([x0, y0, x1, y1], radius=S(10), outline=col, width=max(1, int(S(1.6))))
        tw = draw.textlength(name, font=fb)
        draw.text((x0 + (box_w - tw) / 2, y - S(9)), name, font=fb, fill=text_col)

        if i < n - 1:
            lx0, lx1 = x1, x1 + gap
            line_col = ACCENT if done else LINE
            draw.line([(lx0, y), (lx1, y)], fill=line_col, width=max(1, int(S(1.6))))
            if stage_progress > 0 and stage_progress < 1.0:
                px = lx0 + (lx1 - lx0) * stage_progress
                r = S(4)
                draw.ellipse([px - r, y - r, px + r, y + r], fill=ACCENT)

    if seq_t > 0.97:
        msg = "4 clauses · justified"
        mw = draw.textlength(msg, font=fb)
        draw.text(((FW - mw) / 2, y + S(48)), msg, font=fb, fill=MUTED)


PROJECTS = [
    ("wizard", 0.0, -0.62, True),
    ("sra", -0.86, 0.10, False),
    ("ai-friend", -0.42, 0.62, False),
    ("resume-analyzer", 0.42, 0.62, False),
    ("crime-analysis", 0.86, 0.10, False),
    ("soulspace", 0.0, 0.82, False),
]

def scene_graph(draw, img, t):
    draw_chrome(img, draw, "projects", "github.com/Aniket-a14")
    f = font(19)
    header = "→ ls -la projects/"
    draw.text((ORIGIN_X, TOP_Y), typewriter(header, clamp01(t / 0.15)), font=f, fill=MUTED)

    cx, cy = FW / 2, S(290)
    rx, ry = FW * 0.34, S(150)
    fb = font(15)

    hub = next(p for p in PROJECTS if p[3])
    hub_pos = (cx + hub[1] * rx, cy + hub[2] * ry)

    reveal = clamp01((t - 0.18) / 0.5)
    n_shown = int(round((len(PROJECTS) - 1) * ease_out(reveal)))

    others = [p for p in PROJECTS if not p[3]]
    positions = {}
    for name, ox, oy, _ in PROJECTS:
        positions[name] = (cx + ox * rx, cy + oy * ry)

    for i, (name, ox, oy, _) in enumerate(others):
        if i >= n_shown:
            continue
        pos = positions[name]
        local_t = clamp01((reveal * (len(others)) - i))
        draw.line([hub_pos, pos], fill=LINE, width=max(1, int(S(1.4))))
        if local_t < 1.0:
            px = hub_pos[0] + (pos[0] - hub_pos[0]) * local_t
            py = hub_pos[1] + (pos[1] - hub_pos[1]) * local_t
            draw.ellipse([px - S(3), py - S(3), px + S(3), py + S(3)], fill=ACCENT)

    for name, ox, oy, is_hub in PROJECTS:
        pos = positions[name]
        if not is_hub:
            idx = others.index((name, ox, oy, is_hub))
            if idx >= n_shown:
                continue
        r = S(9) if is_hub else S(6)
        fill = ACCENT if is_hub else MUTED
        draw.ellipse([pos[0] - r, pos[1] - r, pos[0] + r, pos[1] + r], fill=fill)
        tw = draw.textlength(name, font=fb)
        label_col = HEADING if is_hub else BODY
        draw.text((pos[0] - tw / 2, pos[1] + r + S(8)), name, font=fb, fill=label_col)


TIMELINE = [
    ("LPU", "b.tech cse"),
    ("SRA", "shipped · 22 stars"),
    ("Wizard-AIA", "founded org"),
    ("now", "building"),
]

def scene_trajectory(draw, img, t):
    draw_chrome(img, draw, "trajectory", "since 2023")
    f = font(19)
    header = "→ trajectory --all-time"
    draw.text((ORIGIN_X, TOP_Y), typewriter(header, clamp01(t / 0.15)), font=f, fill=MUTED)

    y = S(300)
    x0, x1 = S(150), FW - S(150)
    fb = font(16)
    fs = font(13)

    reveal = ease_out(clamp01((t - 0.2) / 0.55))
    line_x1 = x0 + (x1 - x0) * reveal
    draw.line([(x0, y), (line_x1, y)], fill=LINE, width=max(1, int(S(1.6))))

    n = len(TIMELINE)
    for i, (title, sub) in enumerate(TIMELINE):
        px = x0 + (x1 - x0) * (i / (n - 1))
        show_t = clamp01((reveal * (n - 1) - i + 1))
        if show_t <= 0:
            continue
        is_last = i == n - 1
        r = S(5) if not is_last else S(6)
        col = ACCENT if is_last else MUTED
        draw.ellipse([px - r, y - r, px + r, y + r], fill=col)
        above = (i % 2 == 0)
        ty = y - S(46) if above else y + S(20)
        tw = draw.textlength(title, font=fb)
        sw = draw.textlength(sub, font=fs)
        title_col = HEADING if is_last else BODY
        draw.text((px - tw / 2, ty), title, font=fb, fill=title_col)
        draw.text((px - sw / 2, ty + S(22)), sub, font=fs, fill=MUTED)
        draw.line([(px, y), (px, ty + (S(20) if above else -S(4)))], fill=LINE, width=max(1, int(S(1))))


def scene_signoff(draw, img, t):
    a = 255
    if t < 0.12:
        a = int(255 * ease_out(t / 0.12))
    elif t > 0.85:
        a = int(255 * (1 - ease_out((t - 0.85) / 0.15)))

    draw_chrome(img, draw, "$ exit 0", "aniketdesign.in", caption_alpha=a)

    cx = FW / 2
    mark_y = S(150)
    mr = S(26)
    pts = [(cx, mark_y - mr), (cx - mr, mark_y + mr * 0.7), (cx + mr, mark_y + mr * 0.7)]
    line_col = fade(LINE, int(a * 0.9))
    draw.line([pts[0], pts[1]], fill=line_col, width=max(1, int(S(1.4))))
    draw.line([pts[0], pts[2]], fill=line_col, width=max(1, int(S(1.4))))
    for p in pts:
        draw.ellipse([p[0] - S(4), p[1] - S(4), p[0] + S(4), p[1] + S(4)], fill=fade(MUTED, a))

    fname = font(40, bold=True)
    name = "Aniket Saha"
    nw = draw.textlength(name, font=fname)
    ny = S(230)
    draw.text((cx - nw / 2, ny), name, font=fname, fill=fade(HEADING, a))

    fsub = font(17)
    sub = "AI Engineer — agents, systems, full-stack"
    sw = draw.textlength(sub, font=fsub)
    draw.text((cx - sw / 2, ny + S(58)), sub, font=fsub, fill=fade(BODY, a))

    line_y = ny + S(100)
    lw = S(160)
    draw.line([(cx - lw / 2, line_y), (cx + lw / 2, line_y)], fill=fade(LINE, a), width=max(1, int(S(1))))

    flinks = font(15)
    links = "github.com/Aniket-a14 · aniketdesign.in"
    lww = draw.textlength(links, font=flinks)
    draw.text((cx - lww / 2, line_y + S(20)), links, font=flinks, fill=fade(MUTED, a))


SCENES = [
    (scene_login, 2.6),
    (scene_prompt_pause, 0.9),
    (scene_pipeline, 4.4),
    (scene_graph, 4.2),
    (scene_trajectory, 4.2),
    (scene_signoff, 4.6),
]

def render():
    frames = []
    for draw_fn, seconds in SCENES:
        n = max(1, int(round(seconds * FPS)))
        for i in range(n):
            t = i / max(1, n - 1)
            img = Image.new("RGBA", (FW, FH), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img, "RGBA")
            draw_fn(draw, img, t)
            small = img.convert("RGB").resize((W, H), Image.LANCZOS)
            frames.append(small)
    print(f"rendered {len(frames)} frames")
    frames[0].save(
        OUT,
        save_all=True,
        append_images=frames[1:],
        duration=int(1000 / FPS),
        loop=0,
        optimize=True,
    )
    print(f"wrote {OUT} ({os.path.getsize(OUT) / 1024:.0f} KB)")

if __name__ == "__main__":
    render()
