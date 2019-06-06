from ..analytics.excelerator.pc_parser import PaWrangler as paW
import sys, traceback, logging, glob, os, tempfile
from pathlib import Path
from flask_cors import CORS
from flask import Flask, flash, request, redirect, url_for, send_file, jsonify
from werkzeug.utils import secure_filename

# App Constants
ALLOWED_EXTENSIONS = set(['xlsx'])
FLASK_ROOT = Path(__file__).parent
TMP_FILES = FLASK_ROOT / 'files' / 'tmp_files'
PA_DEFICITS = FLASK_ROOT / 'files' / 'pa_deficits'

# App Configuration
app = Flask(__name__)
CORS(app)
logging.getLogger('flask_cors').level = logging.DEBUG

# Utility Functions
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Routes
@app.route('/pa-deficits', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # First, save the file to a tmpfiles directory.
        file = request.files['file']
        file_dst = str(TMP_FILES / file.filename)
        file.save(file_dst)

        # Next, process the file with PaWrangler
        data = paW(file_dst, path= str(PA_DEFICITS) + "/")
        data.truss()
        data.wrangle()
        poop = data.print_to_file()
        print(poop)

        # Next, retrieve the saved file and parse it with paWrangler.
        name_dict = {'name' : file.filename}
        return jsonify(name_dict)
    else:
        return('hello hunter.')

@app.route('/pa-deficits/<filename>', methods=['GET'])
def download_file(filename):
    if request.method == 'GET':
        return send_file(str(new_path / 'tmpdir' / filename), attachment_filename= filename)
