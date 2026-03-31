from init import app
from flask import jsonify, request
from .conn import get_connection
from .lib import allowed_file, process_image_to_jpeg
from PIL import Image
import io
from datetime import datetime
import uuid
import os


DESTINATION_URL = '/business_gallery_pics'
UPLOAD_DIR = app.config['media'] + DESTINATION_URL


@app.route('/delete_business_gallery_pic', methods=['DELETE'])
def delete_business_gallery_pic():
    try:
        # Check content type
        content_type = request.headers.get('Content-Type', '')
        if not content_type.startswith('application/json'):
            return jsonify({'error': 'Invalid content type. Expected JSON.'}), 415
        
        # Get JSON body
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON body'}), 400
        
        user_guid = data.get('guid')
        business_guid = data.get('bid')
        image_guid = data.get('image_guid')

        connection = get_connection()
        cursor = connection.cursor()
        
        # Validate required fields
        if not user_guid or not business_guid or not image_guid:
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if image exists
        cursor.execute(
            """SELECT * FROM tbl_business_gallery_image
               WHERE user_guid = %s AND business_guid = %s AND image_guid = %s""",
            (user_guid, business_guid, image_guid)
        )

        existing = cursor.fetchone()
        
        if not existing:
            cursor.close()
            return jsonify({'message': 'Image does not exist'}), 200
        
        # Extract values (assuming id is first column, image_filename is second)
        image_id = existing["id"]
        image_filename = existing["image_filename"]

        # Delete image file
        if image_filename:
            image_path = os.path.join(UPLOAD_DIR, image_filename)
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
            """DELETE FROM tbl_business_gallery_image
               WHERE user_guid = %s AND business_guid = %s AND image_guid = %s""",
            (user_guid, business_guid, image_guid)
        )
        
        connection.commit()
        cursor.close()
        
        return jsonify({
            'message': 'File deleted successfully',
            'insertId': image_id
        }), 200

    except Exception as e:
        print(f"Deletion error: {e}")
        return jsonify({'error': str(e) or 'Deletion failed'}), 500