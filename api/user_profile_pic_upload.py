from init import app
from flask import jsonify, request
from .conn import get_connection
from .lib import allowed_file, process_image_to_jpeg
from PIL import Image
import io
from datetime import datetime
import uuid
import os

DESTINATION_DIR = '/user_profile_pics'
UPLOAD_DIR = app.config['media'] + DESTINATION_DIR

@app.route('/user_profile_pic_upload', methods=['POST'])
def user_profile_pic_upload():
    try:
        # Get form data
        file = request.files.get('file')
        guid = request.form.get('guid')

        connection = get_connection()
        cursor = connection.cursor()
        
        # Validations
        if not file or file.filename == '':
            return jsonify({'error': 'No file uploaded'}), 400
        
        if not guid:
            return jsonify({'error': 'Missing user GUID'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400

        processed_image = process_image_to_jpeg(file.stream)

        # Generate unique filename
        unique_name = f"{int(datetime.now().timestamp() * 1000)}_{uuid.uuid4().hex}.jpg"
        file_path = os.path.join(UPLOAD_DIR, unique_name)
        
        with open(file_path, 'wb') as f:
            f.write(processed_image.read())

        
        # Prepare data
        file_url = f"{DESTINATION_DIR}/{unique_name}"
        mime_type = 'image/jpeg'
        image_guid = uuid.uuid4().hex
        
        # Check if record exists
        cursor.execute(
            "SELECT * FROM tbl_user_profile_image WHERE user_guid = %s",
            (guid,)
        )
        existing = cursor.fetchone()

        if not existing:
            # Insert new record
            cursor.execute(
                """INSERT INTO tbl_user_profile_image 
                   (image_filename, user_guid, image_guid, image_url, mimetype)
                   VALUES (%s, %s, %s, %s, %s)""",
                (unique_name, guid, image_guid, file_url, mime_type)
            )
            connection.commit()
            insert_id = cursor.lastrowid
            
            cursor.close()
            
            return jsonify({
                'message': 'File uploaded and saved to database successfully',
                'fileUrl': file_url,
                'insertId': insert_id
            }), 200
        else:
            # Delete old file
            old_filename = existing["image_filename"]  # Assuming image_filename is second column
            if old_filename:
                old_file_path = os.path.join(UPLOAD_DIR, old_filename)
                print(f"Old file path: {old_file_path}")  # console.log equivalent
                
                try:
                    if os.path.exists(old_file_path):
                        os.unlink(old_file_path)
                except Exception as e:
                    print(f"File deletion error: {e}")
            
            # Update existing record
            cursor.execute(
                """UPDATE tbl_user_profile_image 
                   SET 
                   image_filename = %s, 
                   image_guid = %s, 
                   image_url = %s, 
                   mimetype = %s
                   WHERE 
                   user_guid = %s""",
                (unique_name, image_guid, file_url, mime_type, guid)
            )
            connection.commit()
            
            cursor.close()
            
            return jsonify({
                'message': 'File updated and saved to database successfully',
                'fileUrl': file_url,
                'insertId': existing["id"]  # id is typically first column
            }), 200
        
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({'error': str(e) or 'Upload failed'}), 500
    



@app.route('/vmedia/user_profile_pics/<string:filename>')
def serve_user_profile_pics(filename):
    """Serve uploaded images"""
    from flask import send_from_directory
    image_folder = os.path.join(UPLOAD_DIR)
    return send_from_directory(image_folder, filename)