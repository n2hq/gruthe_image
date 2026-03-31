from flask import Flask
from api.conn import get_connection
from init import app

from api import (
    business_gallery_pic_update, 
    business_gallery_pic_upload,
    business_gallery_product_update,
    business_gallery_product_upload,
    business_profile_bg_upload,
    business_profile_pic_upload,
    delete_business_gallery_pic,
    delete_business_product,
    user_profile_bg_upload,
    user_profile_pic_upload
    )



@app.route('/', methods=['GET'])
def hello_world():
    return 'API-v1.0'


if __name__== '__main__':
    app.run(debug=True, port=8882)

