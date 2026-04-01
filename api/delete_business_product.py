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

@app.route('/delete_business_product', methods=['POST'])
def delete_business_product():
    try:
        
        
        # Get JSON body
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON body'}), 400
        
        user_guid = data.get('guid')
        business_guid = data.get('bid')
        product_guid = data.get('product_guid')

        connection = get_connection()
        cursor = connection.cursor()

        # Validate required fields
        if not user_guid or not business_guid or not product_guid:
            print('here')  # console.log('here')
            return jsonify({'error': 'Missing required fields'}), 400
        
        cursor = connection.cursor()

        # Check if product exists and get product_image_filename and id
        cursor.execute(
            """SELECT id, product_image_filename FROM tbl_business_gallery_products
               WHERE user_guid = %s AND business_guid = %s AND product_guid = %s""",
            (user_guid, business_guid, product_guid)
        )
        product = cursor.fetchone()
        
        if not product:
            cursor.close()
            return jsonify({'message': 'Product does not exist'}), 200


        # Extract values (assuming id is first column, product_image_filename is second)
        product_id = product["id"]
        product_image_filename = product["product_image_filename"]
        
        # Delete image file
        if product_image_filename:
            image_path = os.path.join(UPLOAD_DIR, product_image_filename)
            try:
                if os.path.exists(image_path):
                    os.unlink(image_path)
                    print(f"Deleted old file: {image_path}")  # console.log equivalent
            except Exception as e:
                print(f"Error deleting file: {e}")
                cursor.close()
                return jsonify({'error': 'File deletion failed'}), 500
        
        # Delete database record
        cursor.execute(
            """DELETE FROM tbl_business_gallery_products
               WHERE user_guid = %s AND business_guid = %s AND product_guid = %s""",
            (user_guid, business_guid, product_guid)
        )
        connection.commit()
        cursor.close()
        
        return jsonify({
            'message': 'File deleted successfully',
            'insertId': product_id
        }), 200
    except Exception as e:
        print(f"Deletion error: {e}")
        return jsonify({'error': str(e) or 'Deletion failed'}), 500


    