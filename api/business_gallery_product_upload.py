from init import app
from flask import jsonify, request
from .conn import get_connection
from .lib import allowed_file, process_image_to_jpeg, clean_amount
from PIL import Image
import io
from datetime import datetime
import uuid
import os

DESTINATION_DIR = '/business_gallery_products'
UPLOAD_DIR = app.config['media'] + DESTINATION_DIR


@app.route('/business_gallery_product_upload', methods=['POST'])
def business_gallery_product_upload():
    try:
        # Get form data
        file = request.files.get('file')
        guid = request.form.get('guid')
        bid = request.form.get('bid')
        product_title = request.form.get('product_title')
        product_description = request.form.get('product_description')
        raw_amount = request.form.get('product_amount', '')
        product_currency_country_id = request.form.get('product_currency_country_id', '')
        product_link = request.form.get('product_link')


        connection = get_connection()
        cursor = connection.cursor()

        # Clean and convert amount
        print(f"Raw amount: {raw_amount}")
        product_amount = clean_amount(raw_amount)

        # Validate
        if not file or file.filename == '':
            return jsonify({'message': 'No file selected'}), 405
        
        if not guid or not bid or not product_title:
            return jsonify({'message': 'Missing required fields. Product title is compulsory'}), 400
        
        # Process image to JPEG
        processed_image = process_image_to_jpeg(file.stream)

        # Generate unique filename
        unique_name = f"{int(datetime.now().timestamp() * 1000)}_{uuid.uuid4().hex}.jpg"
        file_path = os.path.join(UPLOAD_DIR, unique_name)

        # Save file
        with open(file_path, 'wb') as f:
            f.write(processed_image.read())

        
        # Prepare data
        image_file_url = f"{DESTINATION_DIR}/{unique_name}"
        mime_type = 'image/jpeg'
        product_guid = uuid.uuid4().hex

        # Insert into database
        
        cursor.execute(
            """INSERT INTO tbl_business_gallery_products
               (product_image_filename, user_guid, product_guid, product_image_url,
                mimetype, business_guid, product_title, product_description,
                product_link, product_amount, product_currency_country_id)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (unique_name, guid, product_guid, image_file_url, mime_type,
             bid, product_title, product_description, product_link,
             product_amount, product_currency_country_id)
        )

        connection.commit()
        insert_id = cursor.lastrowid
        cursor.close()

        return jsonify({
            'message': 'File uploaded and saved to database successfully',
            'imageFileUrl': image_file_url,
            'insertId': insert_id
        }), 200

    except Exception as e:
        print(f"Upload error: {e}")
        return jsonify({'message': str(e) or 'Database save failed'}), 500

@app.route('/vmedia/business_gallery_products/<string:filename>')
def serve_business_gallery_products(filename):
    """Serve uploaded images"""
    from flask import send_from_directory
    image_folder = os.path.join(UPLOAD_DIR)
    return send_from_directory(image_folder, filename)