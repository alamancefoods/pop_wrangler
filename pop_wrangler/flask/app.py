import sys, traceback, logging
import glob
import os
from flask_cors import CORS
from flask import Flask, flash, request, redirect, url_for, send_file, jsonify
from werkzeug.utils import secure_filename

UPLOAD_FOLDER =  "/tmpdir"
ALLOWED_EXTENSIONS = set(['xlsx'])
path = sys.path[0]
fin_path = path + UPLOAD_FOLDER
app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

logging.getLogger('flask_cors').level = logging.DEBUG

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/pa-deficits', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        file.save(os.path.join(fin_path, file.filename))
        name_dict = {'name' : file.filename}
        return jsonify(name_dict)
    else:
        return('hello hunter.')

@app.route('/pa-deficits/<filename>', methods=['GET'])
def download_file(filename):
    if request.method == 'GET':
        return send_file(os.path.join(fin_path, filename), attachment_filename= filename)
