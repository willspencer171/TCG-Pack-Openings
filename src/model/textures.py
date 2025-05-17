import numpy as np
from pygame.surfarray import array3d, make_surface
from pygame import Surface, Rect

def hsv_to_rgb(h, s, v):
    if s:
        if h == 1.0: h = 0.0
        i = int(h*6.0); f = h*6.0 - i
        
        w = v * (1.0 - s)
        q = v * (1.0 - s * f)
        t = v * (1.0 - s * (1.0 - f))
        
        if i==0: return (v, t, w)
        if i==1: return (q, v, w)
        if i==2: return (w, v, t)
        if i==3: return (w, q, v)
        if i==4: return (t, w, v)
        if i==5: return (v, w, q)
    else: return (v, v, v)

def apply_holo_effect(effect: callable, offset, intensity, image: Surface, array_3d: np.ndarray):
    applied_array = effect(offset, image)

    blended = np.clip(array_3d + applied_array * intensity, 0, 255).astype(np.uint8)

    return make_surface(blended)

def rainbow_shimmer(offset, image: Surface):
    w, h = image.get_size()
    shimmer = np.zeros((w, h, 3), np.uint8)
    for x in range(w):
        hue = ((x + offset) % 360) / 360
        r, g, b = hsv_to_rgb(hue, 1, 1)
        shimmer[x, :, 0] = int(r * 255)
        shimmer[x, :, 1] = int(g * 255)
        shimmer[x, :, 2] = int(b * 255)
    
    return shimmer

def holo_shimmer(offset, image: Surface):
    width, height = image.get_size()
    shimmer = np.zeros((width, height, 3), dtype=np.uint8)
    for x in range(width):
        brightness = int(60 + 40 * np.sin((x + offset) * 0.05))  # smooth wave
        shimmer[x, :, :] = (brightness, brightness, brightness)
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
