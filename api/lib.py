import os
from PIL import Image
import io
from init import app
import re

def process_image_to_jpeg(file_stream):
    """Convert image to JPEG format"""

    try:
        # Open image with PIL
        img = Image.open(file_stream)

        if img.mode in ('RGBA', 'LA', 'P'):
            rgb_img = Image.new('RGB', img.size, (255,255,255))
            rgb_img.paste(img, mask=img.split()[-1] if img.mode=='RGBA' else None)
            img = rgb_img
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        # Save as JPEG
        output_buffer = io.BytesIO()
        img.save(output_buffer, format='JPEG', quality=90)
        output_buffer.seek(0)

        return output_buffer
    except Exception as e:
        print(f"Image processing error: {e}")
        # If processing fails, return original
        file_stream.seek(0)
        return file_stream


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['allowed_extensions']


def clean_amount(raw_amount):
    """Clean amount string by removing currency symbols, commas, etc."""
    print(f"Raw amount: {raw_amount}")  # console.log equivalent
    cleaned = re.sub(r'[^\d.]', '', raw_amount).strip()
    return float(cleaned) if cleaned else 0.0