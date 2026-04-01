from init import app
from flask import jsonify, request
from .conn import get_connection
from .lib import allowed_file, process_image_to_jpeg
from PIL import Image
import io
from datetime import datetime
import uuid
import os



DESTINATION_DIR = '/business_gallery_pics'
UPLOAD_DIR = app.config['media'] + DESTINATION_DIR

@app.route('/business_gallery_pic_upload', methods=['POST'])
def business_gallery_pic_upload():
    try:
        file = request.files.get('file')
        guid = request.form.get('guid')
        bid = request.form.get('bid')
        image_title = request.form.get('image_title')

        connection = get_connection()
        cursor = connection.cursor()

        # Validations
        if not file or file.filename == '':
            return jsonify({'message': 'No file uploaded'}), 405
        
        if not guid or not bid or not image_title:
            return jsonify({'message': 'Please enter picture title.'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'message': 'File type not allowed'}), 400
        

        # Process image to JPEG 
        processed_image = process_image_to_jpeg(file.stream)

        # Generate unique filename
        unique_name = f"{int(datetime.now().timestamp() * 1000)}_{uuid.uuid4().hex}.jpg"
        file_path = os.path.join(UPLOAD_DIR, unique_name)

        with open(file_path, 'wb') as f:
            f.write(processed_image.read())

        
        # Database insert
        image_guid = uuid.uuid4().hex
        cursor.execute(
            """INSERT INTO tbl_business_gallery_image 
               (image_filename, user_guid, image_guid, image_url, mimetype, business_guid, image_title)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (unique_name, guid, image_guid, f"{DESTINATION_DIR}/{unique_name}", 
             'image/jpeg', bid, image_title)
        )
        connection.commit()
        insert_id = cursor.lastrowid
        cursor.close()

        return jsonify({
            'message': 'File uploaded and saved to database successfully',
            'fileUrl': f"{DESTINATION_DIR}/{unique_name}",
            'insertId': insert_id
        }), 200


    except Exception as e:
        print(f"Upload error: {e}")
        return jsonify({'message': str(e) or 'Database save failed'}), 500


@app.route('/vmedia/business_gallery_pics/<string:filename>')
def serve_business_gallery_pics(filename):
    """Serve uploaded images"""
    from flask import send_from_directory
    image_folder = os.path.join(UPLOAD_DIR)
    return send_from_directory(image_folder, filename)