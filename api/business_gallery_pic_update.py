from init import app
from flask import jsonify, request
from .conn import get_connection
from PIL import Image
import io
from datetime import datetime
import uuid
import os
from .lib import process_image_to_jpeg

DESTINATION_DIR = '/business_gallery_pics'
UPLOAD_DIR = app.config['media'] + DESTINATION_DIR


@app.route('/business_gallery_pic_update', methods=['POST'])
def business_gallery_pic_update():
    
    try:
        file = request.files.get('file')
        user_guid = request.form.get('guid')
        business_guid = request.form.get('bid')
        image_guid = request.form.get('image_guid')
        image_title = request.form.get('image_title')

        if not all([user_guid, business_guid, image_guid]):
            return jsonify({'error':'Missing required fields'})
        
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM tbl_business_gallery_image WHERE user_guid=%s AND business_guid=%s AND image_guid=%s",
            (user_guid, business_guid, image_guid))
        
        existing = cursor.fetchone()

        

        if not existing:
            cursor.close()
            return jsonify({'error':'Image does not exist'}), 404

        update_data = {
            'image_title': image_title,
            'user_guid': user_guid,
            'business_guid': business_guid,
            'image_guid': image_guid
        }

        

        #Handle file upload
        if file and file.filename:
            processed_image = process_image_to_jpeg(file.stream)

            # Generate filename
            unique_name = f"{datetime.now().timestamp()}_{uuid.uuid4().hex}.jpg"
            file_path = os.path.join(UPLOAD_DIR, unique_name)

            # Save file
            with open(file_path, 'wb') as f:
                f.write(processed_image.read())

            
            # Delete old file
            old_file = existing["image_filename"] or ''

            if len(old_file) > 0:
                old_path = os.path.join(UPLOAD_DIR, old_file)
                if os.path.exists(old_path):
                    os.unlink(old_path)

            
            # Update with new file
            update_data['image_filename'] = unique_name
            update_data['image_url'] = f"{DESTINATION_DIR}/{unique_name}"
            update_data['mimetype'] = 'image/jpeg'

        else:
            #  Keep existing file info
            update_data['image_filename'] = existing["image_filename"]  # Adjust index
            update_data['image_url'] = existing["image_url"]  # Adjust index
            update_data['mimetype'] = existing["mimetype"]  # Adjust index  

        # Update database
        cursor.execute(
            """UPDATE tbl_business_gallery_image 
            SET image_filename=%s, 
            image_url=%s, 
            mimetype=%s, 
            image_title=%s
            WHERE user_guid=%s 
            AND 
            business_guid=%s 
            AND 
            image_guid=%s""",
        (update_data['image_filename'], 
            update_data['image_url'], 
            update_data['mimetype'], 
            update_data['image_title'],
            user_guid, 
            business_guid, 
            image_guid))

        connection.commit()
        cursor.close()

        return jsonify({
                'message': 'Gallery image updated successfully',
                'fileUrl': update_data['image_url'],
                'insertId': existing['id']
            }), 200
        
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e) or 'Update failed'}), 500

        
   
    #print("POST request received!")  # This should now print
    #print("Form data:", request.form)
    #print("Files:", request.files)
    
    

    return 'Cools'


