from PIL import Image, ImageDraw

def create_icon():
    # Generate a simple icon (Blue/White flag style)
    width = 64
    height = 64
    color1 = "blue"
    color2 = "white"

    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    
    # Top half White (Flag style variation or just simple blocks)
    # The original was: 
    # Rect 1: width//2, 0, width, height//2 (Top Right) -> White
    # Rect 2: 0, height//2, width//2, height (Bottom Left) -> White
    # Result is a Checker pattern Blue/White
    
    dc.rectangle(
        (width // 2, 0, width, height // 2),
        fill=color2)
    dc.rectangle(
        (0, height // 2, width // 2, height),
        fill=color2)

    return image
