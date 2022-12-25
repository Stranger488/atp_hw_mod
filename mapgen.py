from PIL import Image

IMPASSABLE = 0, 0, 0
PASSABLE = 220, 220, 220


def generate_map(size):
    return Image.new('RGB', (size, size), color=PASSABLE)
