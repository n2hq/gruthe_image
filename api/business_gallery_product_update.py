from init import app
from flask import jsonify, request
from .conn import get_connection
from .lib import allowed_file, process_image_to_jpeg
from PIL import Image
import io
from datetime import datetime
import uuid
import os

DESTINATION_DIR = '/business_gallery_products'
UPLOAD_DIR = app.config['media'] + DESTINATION_DIR

@app.route('/business_gallery_product_update', methods=['POST'])
def business_gallery_product_update():
    try:
        file = request.files.get('file')
        user_guid = request.form.get('guid')
        business_guid = request.form.get('bid')
        product_guid = request.form.get('product_guid')
        product_title = request.form.get('product_title', '')
        product_description = request.form.get('product_description', '')
        product_amount = request.form.get('product_amount', '')
        product_currency_country_id = request.form.get('product_currency_country_id', '')
        product_link = request.form.get('product_link', '')

        
        # Validate
        if not all([user_guid, business_guid, product_guid]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """SELECT * FROM tbl_business_gallery_products
               WHERE user_guid=%s AND business_guid=%s AND product_guid=%s""",
            (user_guid, business_guid, product_guid)
        )
        existing = cursor.fetchone()

        if not existing:
            cursor.close()
            return jsonify({'error': 'Product does not exist'}), 404
        

        # Initialize with existing values
        # Index positions based on your table structure (adjust as needed)
        # Assuming: id, product_image_filename, product_image_url, mimetype, etc.
        file_url = existing["product_image_url"]
        original_name = existing["product_image_filename"]
        mime_type = existing["mimetype"]

        if file and file.filename:
            print(f"Processing file: {file.filename}")
            processed_image = process_image_to_jpeg(file.stream)

            unique_name = f"{int(datetime.now().timestamp() * 1000)}_{uuid.uuid4().hex}.jpg"
            file_path = os.path.join(UPLOAD_DIR, unique_name)

            # Save file
            with open(file_path, 'wb') as f:
                f.write(processed_image.read())

            
            # Delete old file
            if original_name:
                old_path = os.path.join(UPLOAD_DIR, original_name)
                try:
                    if os.path.exists(old_path):
                        os.unlink(old_path)
                        print('done')
                except Exception as e:
                    print(f"Failed to delete old image: {e}")
            
            # Update values
            file_url = f"/{DESTINATION_DIR}/{unique_name}"
            original_name = unique_name
            mime_type = 'image/jpeg'

        
        # Update database
        cursor.execute(
            """UPDATE tbl_business_gallery_products
               SET product_image_filename=%s, product_image_url=%s, mimetype=%s,
                   product_title=%s, product_description=%s, product_link=%s,
                   product_amount=%s, product_currency_country_id=%s
               WHERE user_guid=%s AND business_guid=%s AND product_guid=%s""",
            (original_name, file_url, mime_type, product_title, product_description,
             product_link, product_amount, product_currency_country_id,
             user_guid, business_guid, product_guid)
        )

        connection.commit()
        cursor.close()

        return jsonify({
            'message': 'Gallery image updated successfully',
            'fileUrl': file_url,
            'insertId': existing["id"]  # Assuming id is first column
        }), 200
        
    except Exception as e:
        print(f"Error updating gallery image: {e}")
        return jsonify({'message': str(e) or 'Update failed'}), 500