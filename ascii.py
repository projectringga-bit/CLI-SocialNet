import os
import urllib.request
import tempfile
from PIL import Image

ASCII_CHARS = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", "."]

def image_to_ascii(image_path):
    if not os.path.exists(image_path):
        return False, f"Image file does not exist: {image_path}."
    
    extensions = [".png", ".jpg", ".jpeg", ".bmp", ".webp"]
    file_ext = os.path.splitext(image_path)[1].lower()
    if file_ext not in extensions:
        return False, "Unsupported image format. Supported formats: PNG, JPG, JPEG, BMP, WEBP."
    
    try:
        image = Image.open(image_path)
        image.load()

        if image.mode == "P":
            image = image.convert("RGBA")

        if image.mode == "RGBA":
            background = Image.new("RGB", image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[3])
            image = background

        elif image.mode != "RGB":
            image = image.convert("RGB")


        aspect_ratio = image.height / image.width
        new_width = 80
        new_height = int(aspect_ratio * new_width * 0.5)

        image = image.resize((new_width, new_height))

        image = image.convert("L")

        pixels = list(image.getdata())

        num_chars = len(ASCII_CHARS)

        ascii = ""
        for i, pixel in enumerate(pixels):
            index = int(pixel / 255 * (num_chars - 1))

            if index >= num_chars:
                index = num_chars - 1

            ascii += ASCII_CHARS[index]

            if (i + 1) % new_width == 0:
                ascii += "\n"
        
        return True, ascii
    
    except Exception as e:
        return False, f"Error processing image: {e}"
    

def image_url_to_ascii(image_url):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
            urllib.request.urlretrieve(image_url, tmp_file.name)
            temp_path = tmp_file.name

        result = image_to_ascii(temp_path)

        os.unlink(temp_path)

        return result
    
    except Exception as e:
        return False, f"Error downloading image: {e}"
