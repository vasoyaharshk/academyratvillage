import os
from PIL import Image, ImageDraw, ImageFont

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define folders in reverse order (16 to 1)
folders = [str(i) for i in range(16, 0, -1)]
grid_size = (4, 4)  # 4x4 grid

# Load the first image from each folder
images = []
labels = []

for folder in folders:
    folder_path = os.path.join(script_dir, folder)
    if os.path.isdir(folder_path):
        files = sorted(os.listdir(folder_path))  # Sort to get the first image consistently
        if files:
            img_path = os.path.join(folder_path, files[0])
            img = Image.open(img_path)
            images.append(img)
            labels.append(folder)

# Resize images to a uniform size
img_width, img_height = 128*2, 102*2  # Adjust

# Create a blank image canvas
canvas_width = grid_size[1] * img_width
canvas_height = grid_size[0] * (img_height + 30)  # Extra space for labels
canvas = Image.new("RGB", (canvas_width, canvas_height), "white")
draw = ImageDraw.Draw(canvas)

# Load font
try:
    font = ImageFont.truetype("arial.ttf", 20)
except:
    font = ImageFont.load_default()

# Arrange images in a grid with labels
for idx, (img, label) in enumerate(zip(images, labels)):
    row = idx // grid_size[1]
    col = idx % grid_size[1]
    x = col * img_width
    y = row * (img_height + 30)
    text_bbox = draw.textbbox((0, 0), label, font=font)
    text_x = x + (img_width - (text_bbox[2] - text_bbox[0])) // 2
    draw.text((text_x, y+5), label, fill="black", font=font)
    
    # Create a bordered image
    bordered_img = Image.new("RGB", (img_width + 4, img_height + 4), "black")
    bordered_img.paste(img.resize((img_width, img_height)), (2, 2))
    
    # Paste bordered image onto canvas
    canvas.paste(bordered_img, (x, y + 30))

# Save the final image
output_path = os.path.join(script_dir, "list_all_conditions.png")
canvas.save(output_path)
print(f"Image saved as {output_path}")
