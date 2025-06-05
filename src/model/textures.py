import numpy as np
from pygame.surfarray import make_surface
from pygame import Surface
from matplotlib.colors import hsv_to_rgb

""" def hsv_to_rgb(h, s, v):
    if s:
        if h == 1.0:
            h = 0.0
        i = int(h * 6.0)
        f = h * 6.0 - i

        w = v * (1.0 - s)
        q = v * (1.0 - s * f)
        t = v * (1.0 - s * (1.0 - f))

        if i == 0:
            return (v, t, w)
        if i == 1:
            return (q, v, w)
        if i == 2:
            return (w, v, t)
        if i == 3:
            return (w, q, v)
        if i == 4:
            return (t, w, v)
        if i == 5:
            return (v, w, q)
    else:
        return (v, v, v) """


def apply_holo_effect(
    effect: callable, offset, intensity, image: Surface, array_3d: np.ndarray
):
    applied_array = effect(offset, image)

    blended = np.clip(array_3d + applied_array * intensity, 0, 255).astype(np.uint8)

    return make_surface(blended)


def rainbow_shimmer(offset, image: Surface):
    w, h = image.get_size()
    shimmer = np.zeros((w, h, 3), np.uint8)
    angle = np.deg2rad(-45)
    cos_a = np.cos(angle)
    sin_a = np.sin(angle)
    x = np.arange(w)
    y = np.arange(h)
    cx, cy = w / 2, h / 2
    dx = x - cx
    dy = y - cy
    dx2d, dy2d = np.meshgrid(dx, dy, indexing='ij')
    rx = cos_a * dx2d - sin_a * dy2d
    hue = ((rx + offset) % 360) / 360
    hsv = np.zeros((w, h, 3), dtype=np.float32)
    hsv[..., 0] = hue
    hsv[..., 1] = 1.0
    hsv[..., 2] = 1.0
    rgb = hsv_to_rgb(hsv)
    rgb255 = (rgb * 255).astype(np.uint8)
    shimmer[:, :, :] = rgb255
    return shimmer


def holo_shimmer(offset, image: Surface):
    width, height = image.get_size()
    shimmer = np.zeros((width, height, 3), dtype=np.uint8)
    angle = np.deg2rad(-45)
    cos_a = np.cos(angle)
    sin_a = np.sin(angle)
    # Create a grid of x, y coordinates
    x = np.arange(width)
    y = np.arange(height)
    cx, cy = width / 2, height / 2
    dx = x - cx
    dy = y - cy
    # Use broadcasting to create 2D arrays of dx and dy
    dx2d, dy2d = np.meshgrid(dx, dy, indexing='ij')
    # Rotate coordinates
    rx = cos_a * dx2d - sin_a * dy2d
    # Compute brightness for all pixels at once
    brightness = 60 + 40 * np.sin((rx + offset) * 0.05)
    brightness = np.clip(brightness, 0, 175).astype(np.uint8)
    shimmer[:, :, 0] = brightness
    shimmer[:, :, 1] = brightness
    shimmer[:, :, 2] = brightness
    return shimmer


def perlin_shimmer(offset, image: Surface):
    from noise import pnoise2

    width, height = image.get_size()
    shimmer = np.zeros((width, height, 3), dtype=np.uint8)

    for x in range(width):
        for y in range(height):
            value = pnoise2(x * 0.03 + offset * 0.05, y * 0.03)
            brightness = int((value + 1) * 127.5) / 2
            adjusted = np.power(brightness, 0.5)
            brightness = (adjusted * 255).astype(np.uint8)
            shimmer[x, y] = (brightness, brightness, brightness)

    return shimmer
