import os
from pathlib import Path
from PIL import Image, ImageOps

# =========================================================
# SETTINGS
# =========================================================
GRID_COLUMNS = 8
GRID_ROWS = 4
IMAGES_PER_SHEET = GRID_COLUMNS * GRID_ROWS  # 32

# Resize every image to a fixed tile size for a clean grid
TILE_WIDTH = 600
TILE_HEIGHT = 600

# Spacing and background
PADDING = 1
GAP_X = 1
GAP_Y = 1
BACKGROUND_COLOR = (255, 255, 255)

# Output folder
OUTPUT_FOLDER_NAME = "grid_output"

# Supported image types
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}


# =========================================================
# HELPERS
# =========================================================
def is_image_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS


def natural_sort_key(text: str):
    import re
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r"(\d+)", text)]


def resize_and_pad_image(img: Image.Image, target_width: int, target_height: int) -> Image.Image:
    """
    Resize image to fit inside target tile while preserving aspect ratio,
    then pad with white background so all tiles are the same size.
    """
    img = img.convert("RGB")
    return ImageOps.pad(
        img,
        (target_width, target_height),
        method=Image.Resampling.LANCZOS,
        color=BACKGROUND_COLOR,
        centering=(0.5, 0.5),
    )


def chunk_list(items, chunk_size):
    for i in range(0, len(items), chunk_size):
        yield items[i:i + chunk_size]


def create_grid_sheet(image_paths, output_path: Path):
    sheet_width = (
        PADDING * 2
        + GRID_COLUMNS * TILE_WIDTH
        + (GRID_COLUMNS - 1) * GAP_X
    )
    sheet_height = (
        PADDING * 2
        + GRID_ROWS * TILE_HEIGHT
        + (GRID_ROWS - 1) * GAP_Y
    )

    canvas = Image.new("RGB", (sheet_width, sheet_height), BACKGROUND_COLOR)

    for idx, image_path in enumerate(image_paths):
        row = idx // GRID_COLUMNS
        col = idx % GRID_COLUMNS

        x = PADDING + col * (TILE_WIDTH + GAP_X)
        y = PADDING + row * (TILE_HEIGHT + GAP_Y)

        try:
            with Image.open(image_path) as img:
                tile = resize_and_pad_image(img, TILE_WIDTH, TILE_HEIGHT)
                canvas.paste(tile, (x, y))
        except Exception as e:
            print(f"Could not process image: {image_path} | Error: {e}")

    canvas.save(output_path, quality=95)
    print(f"Saved: {output_path}")


# =========================================================
# MAIN
# =========================================================
def main():
    script_dir = Path(__file__).resolve().parent
    output_dir = script_dir / OUTPUT_FOLDER_NAME
    output_dir.mkdir(exist_ok=True)

    subfolders = [p for p in script_dir.iterdir() if p.is_dir() and p.name != OUTPUT_FOLDER_NAME]
    subfolders.sort(key=lambda p: natural_sort_key(p.name))

    if not subfolders:
        print("No subfolders found in the script folder.")
        return

    for subfolder in subfolders:
        image_files = [p for p in subfolder.iterdir() if is_image_file(p)]
        image_files.sort(key=lambda p: natural_sort_key(p.name))

        if not image_files:
            print(f"No images found in subfolder: {subfolder.name}")
            continue

        print(f"\nProcessing subfolder: {subfolder.name}")
        print(f"Found {len(image_files)} images")

        for sheet_index, image_chunk in enumerate(chunk_list(image_files, IMAGES_PER_SHEET), start=1):
            output_filename = f"{subfolder.name}_{sheet_index:02d}.jpg"
            output_path = output_dir / output_filename
            create_grid_sheet(image_chunk, output_path)

    print("\nDone.")


if __name__ == "__main__":
    main()