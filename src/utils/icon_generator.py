from PIL import Image, ImageDraw


def create_icon(size=128):
    """A simple original shield mark, suitable for the window and tray."""
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    scale = size / 128
    def points(values):
        return [(round(x * scale), round(y * scale)) for x, y in values]
    draw.rounded_rectangle((0, 0, size - 1, size - 1), radius=round(28 * scale), fill="#4361A9")
    shield = points([(64, 22), (95, 34), (92, 68), (78, 91), (64, 103),
                     (50, 91), (36, 68), (33, 34)])
    draw.polygon(shield, fill="#FFFFFF")
    inner = points([(64, 35), (83, 42), (81, 66), (72, 81), (64, 89),
                    (56, 81), (47, 66), (45, 42)])
    draw.polygon(inner, fill="#4361A9")
    return image
