from ..analytics.excelerator.pc_parser import PaWrangler as wrangler
import sys, traceback, logging, glob, os, tempfile
from pathlib import Path
from flask_cors import CORS
from flask import Flask, Blueprint, flash, request, redirect, url_for, send_file, jsonify
from werkzeug.utils import secure_filename

# App Constants
ALLOWED_EXTENSIONS = set(['xlsx'])
FLASK_ROOT = Path(__file__).parent
TMP_FILES = FLASK_ROOT / 'files' / 'tmp_files'
PA_DEFICITS = FLASK_ROOT / 'files' / 'pa_deficits'


# Blueprint Configuration.
bp = Blueprint('parser', __name__)

# Utility Functions
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Routes
@bp.route('/pa-deficits', methods=['POST'])
def upload_file():

    if request.method == 'POST':
        # First, save the file to a tmpfiles directory.
        file = request.files['file']
        file_dst = str(TMP_FILES / file.filename)
        file.save(file_dst)


        # Gather the forecast time deltas, provided they were passed.
        delta_list = []
        if(request.args.getlist('delta')):
            deltas = request.args.getlist('delta')
            for delta in deltas:
                delta_list.append(delta)

        # Next, process the file with PaWrangler and print to 'files/pa_deficits/'
        # The outputted excel file's name will be returned by the print_to_file method.
        file_names = []
        data = wrangler(file_dst, path= str(PA_DEFICITS) + "/")
        data.truss()
        data.wrangle()
        if not len(delta_list):
            file_name = data.print_to_file()
            file_names.append(file_name)
        else:
            for delta in delta_list:
                data.day_count = delta
                file_name = data.print_to_file()
                file_names.append(file_name)


        # Next, retrieve the saved file and parse it with paWrangler.
        name_dict = {'names' : file_names}
        return jsonify(name_dict)
    else:
        return('hello hunter.')

@bp.route('/pa-deficits/<filename>', methods=['GET'])
def download_file(filename):
    if request.method == 'GET':
        return send_file(str(PA_DEFICITS / filename), attachment_filename= filename)
