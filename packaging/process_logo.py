from PIL import Image

def make_transparent(input_path, output_path):
    img = Image.open(input_path).convert("RGBA")
    datas = img.getdata()

    new_data = []
    for item in datas:
        # If the pixel is black (or very close to black), make it transparent
        if item[0] < 30 and item[1] < 30 and item[2] < 30:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)

    img.putdata(new_data)
    img.save(output_path, "PNG")
    print(f"Red: Logo processed and saved to {output_path}")

if __name__ == "__main__":
    make_transparent("ui/red_logo_raw.jpg", "ui/red_logo.png")
