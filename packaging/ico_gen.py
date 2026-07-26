from PIL import Image

def generate_ico(input_png, output_ico):
    img = Image.open(input_png)
    # Windows icons usually contain multiple sizes: 16, 24, 32, 48, 64, 128, 256
    icon_sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(output_ico, format='ICO', sizes=icon_sizes)
    print(f"Red: ICO generated at {output_ico}")

if __name__ == "__main__":
    generate_ico("ui/red_logo.png", "ui/red_logo.ico")
