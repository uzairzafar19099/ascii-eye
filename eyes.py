import math
import sys

import numpy as np
import pygame

COLS, ROWS = 120, 54
CW, CH = 8, 16
W, H = COLS * CW, ROWS * CH
FPS = 30
LOOP = 24.0
CHARS = " .:-|/\\tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
EYE_W = 0.95

rng = np.random.default_rng(7)
ratio = W / H
ys, xs = np.mgrid[0:ROWS, 0:COLS].astype(np.float32)
U = (xs / (COLS - 1) * 2 - 1) * ratio
V = -(ys / (ROWS - 1) * 2 - 1)

star_seed = rng.random((ROWS, COLS)).astype(np.float32)
star_phase = rng.random((ROWS, COLS)).astype(np.float32) * 6.28
hair_seed = rng.random((ROWS, COLS)).astype(np.float32)
flicker_seed = rng.random((ROWS, COLS)).astype(np.float32)


def make_atlas():
    pygame.font.init()
    font = pygame.font.SysFont("consolas,couriernew,dejavusansmono,monospace", 15, bold=True)
    out = []
    for c in CHARS:
        surf = pygame.Surface((CW, CH))
        if c != " ":
            g = font.render(c, True, (255, 255, 255))
            surf.blit(g, ((CW - g.get_width()) // 2, (CH - g.get_height()) // 2))
        out.append(pygame.surfarray.array3d(surf)[:, :, 0].T.astype(np.float32) / 255)
    out = np.stack(out)
    out = out[np.argsort(out.reshape(len(out), -1).sum(1))]
    return out / max(out.max(), 1e-6)


def smooth(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def bump(x, center, width):
    return np.exp(-(((x - center) / width) ** 2))


def wobble(u, v, t):
    a = np.sin(u * 7.1 + t * 0.6 + np.sin(v * 5.3 - t * 0.4))
    b = np.sin(v * 9.7 - t * 0.5 + np.sin(u * 3.9 + t * 0.3)) * 0.7
    c = np.sin((u + v) * 13 + t * 0.2) * 0.4
    return (a + b + c) / 2.1


def blink(t):
    p = t % 4.3
    b = 0.0
    if p < 0.22:
        b = math.sin(p / 0.22 * math.pi)
    if int(t / 4.3) % 3 == 2 and 0.35 < p < 0.55:
        b = max(b, math.sin((p - 0.35) / 0.2 * math.pi))
    return b


def space_level(t, forced):
    if forced:
        return 1.0
    p = t % LOOP
    return float(smooth(13, 17, p) * (1 - smooth(21, 24, p)))


def draw_colors(t, forced=False):
    u, v = U, V
    openness = 1.0 - blink(t)
    gx = 0.26 * math.sin(t * 0.7) + 0.08 * math.sin(t * 2.3)
    gy = 0.07 * math.sin(t * 1.1 + 1.0)
    space = space_level(t, forced)

    k = np.clip(1 - (u / EYE_W) ** 2, 0, 1)
    top = (0.02 + openness * 0.56) * k ** 0.85 - 0.04
    bottom = -0.30 * k ** 0.9 * (0.55 + 0.45 * openness) - 0.02
    inside = (v < top) & (v > bottom) & (np.abs(u) < EYE_W)

    shade = 0.62 + 0.30 * smooth(-0.9, 0.5, v) + 0.08 * wobble(u, v, t * 0.3)
    skin = np.array([0.82, 0.50, 0.38], np.float32) * shade[..., None]
    crease = bump(v, top + 0.20, 0.05) * (np.abs(u) < 1.05)
    skin *= (1 - 0.45 * crease)[..., None]
    socket = bump(v, top + 0.08, 0.14) * k
    skin *= (1 - 0.35 * socket)[..., None]

    brow_y = top + 0.62 + 0.10 * (u / ratio) ** 2 - 0.12 * (u / ratio)
    brow = bump(v, brow_y, 0.12) * smooth(-1.4, -0.6, u) * (1 - smooth(0.9, 1.4, u))
    strands = np.sin(u * 55 + v * 14 + hair_seed * 3) * 0.5 + 0.5
    hair = np.clip(brow * (0.35 + 0.9 * strands), 0, 1)[..., None]
    skin = skin * (1 - hair * 0.92) + np.array([0.10, 0.06, 0.04], np.float32) * hair * 0.92

    wet = (bump(v, bottom - 0.012, 0.016) * (np.abs(u) < 0.9))[..., None]
    skin = skin * (1 - 0.6 * wet) + np.array([0.74, 0.34, 0.30], np.float32) * 0.6 * wet

    r = np.hypot(u - gx, v - gy)
    angle = np.arctan2(v - gy, u - gx)
    iris_r = 0.34
    pupil_r = 0.125 + 0.035 * math.sin(t * 0.8)

    white = np.array([0.70, 0.60, 0.58], np.float32) * np.ones_like(u)[..., None]
    white *= (0.55 + 0.45 * (1 - smooth(0.2, 0.95, np.abs(u) / EYE_W)))[..., None]
    white *= (1 - 0.65 * bump(v, top, 0.10))[..., None]

    fibers = 0.5 + 0.5 * np.sin(angle * 34 + 3 * wobble(u * 3, v * 3, t * 0.1))
    iris = np.array([0.62, 0.40, 0.29], np.float32) * (0.45 + 0.65 * fibers)[..., None]
    iris *= (1 - 0.55 * smooth(iris_r * 0.45, iris_r, r))[..., None]
    iris += np.array([0.25, 0.14, 0.05], np.float32) * bump(r, pupil_r * 1.5, 0.05)[..., None]
    iris *= (1 - 0.80 * smooth(iris_r * 0.88, iris_r, r))[..., None]

    eye = np.where((r < iris_r)[..., None], iris, white)
    eye = np.where((r < pupil_r)[..., None], np.array([0.02, 0.015, 0.012], np.float32), eye)

    spec1 = np.exp(-(((u - gx + 0.11) ** 2 + (v - gy - 0.12) ** 2) / 0.0012))
    spec2 = np.exp(-(((u - gx - 0.12) ** 2 + (v - gy + 0.10) ** 2) / 0.0006)) * 0.6
    eye = eye + (spec1 + spec2)[..., None] * 1.2
    eye *= (0.65 + 0.35 * smooth(0.0, 0.14, top - v))[..., None]

    corner = np.exp(-(((u + 0.82) ** 2) / 0.006 + ((v + 0.02) ** 2) / 0.004))[..., None]
    eye = eye * (1 - corner) + np.array([0.82, 0.42, 0.38], np.float32) * corner

    col = np.where(inside[..., None], eye, skin)

    edge = bump(v, top + 0.005, 0.030) * (np.abs(u) < EYE_W + 0.05)
    lashes = bump(v, top + 0.07, 0.07) * (np.sin(u * 46 + 0.6 * np.sin(u * 5)) > 0.55) * (u > -0.1)
    ink = np.clip(edge * 1.1 + lashes * 0.8, 0, 1)[..., None]
    col = col * (1 - ink * 0.95) + np.array([0.05, 0.03, 0.022], np.float32) * ink
    col = col * (1 - 0.35 * bump(v, bottom, 0.015))[..., None]

    if space > 0.001:
        reach = iris_r * 0.9 + space * 1.9
        mask = smooth(reach, reach - 0.12, r)
        mask = np.where(inside | (space > 0.55), mask, 0.0)
        twinkle = 0.5 + 0.5 * np.sin(t * 3 + star_phase * 6)
        small = (star_seed > 0.935) * (0.35 + 0.65 * twinkle)
        big = (star_seed > 0.985) * (0.7 + 0.3 * twinkle)
        cloud = np.clip(wobble(u * 1.6, v * 1.6, t * 0.5) * 0.5 + 0.35, 0, 1) ** 2.2
        sky = (
            np.array([0.45, 0.16, 0.55], np.float32) * (cloud * 0.28)[..., None]
            + np.array([0.20, 0.30, 0.65], np.float32) * (cloud[::-1] * 0.16)[..., None]
            + np.array([0.95, 0.90, 1.00], np.float32) * (small * 0.8 + big)[..., None]
        )
        col = col * (1 - mask[..., None]) + sky * mask[..., None]

    fade = 1 - smooth(0.55, 1.05, np.hypot(u / 1.25, v / 0.80))
    return np.clip(col * fade[..., None], 0, 1)


def render(t, atlas, forced=False):
    rgb = draw_colors(t, forced)
    lum = rgb @ np.array([0.299, 0.587, 0.114], np.float32)
    lum = np.clip(lum * 1.25, 0, 1) ** 0.85
    n = len(atlas)

    idx = lum * (n - 1)
    jitter = (np.floor(t * 12 + flicker_seed * 9) % 3).astype(np.float32) - 1
    idx = np.clip(np.rint(idx + jitter * (lum > 0.08)), 0, n - 1).astype(np.int32)
    idx[lum < 0.03] = 0

    tint = np.clip(rgb / np.maximum(rgb.max(2, keepdims=True), 1e-3), 0, 1)
    tint = np.clip(tint * (0.6 + 0.8 * lum[..., None]), 0, 1)

    img = atlas[idx][..., None] * tint[:, :, None, None, :]
    img = img.transpose(0, 2, 1, 3, 4).reshape(H, W, 3)
    return (img * 255).astype(np.uint8).swapaxes(0, 1)


def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Eye -> Space")
    clock = pygame.time.Clock()
    atlas = make_atlas()
    forced = False
    shots = 0
    start = pygame.time.get_ticks()

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif ev.key == pygame.K_SPACE:
                    forced = not forced
                elif ev.key == pygame.K_s:
                    pygame.image.save(screen, f"eye_{shots:03d}.png")
                    shots += 1

        t = (pygame.time.get_ticks() - start) / 1000
        pygame.surfarray.blit_array(screen, render(t, atlas, forced))
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()