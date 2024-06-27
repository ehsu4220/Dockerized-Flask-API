import os
import sys
import threading
import ssl
from threading import Thread
from flask import Flask, flash, request, redirect, render_template, make_response
from werkzeug.utils import secure_filename

app=Flask(__name__)

app.secret_key = "secret key"
#app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

path = os.getcwd()

# Location of the permissions and private key
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain('/host/machine/pem/file/location/file.pem', '/host/machine/key/file/location/file.pem')

# Change to earlyscreen directory
UPLOAD_FOLDER = os.path.join(path, 'uploads')

if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

uploaded_files = set()

awaiting_chunks = {}

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'wav', 'mp4', 'db'])

lock = threading.Lock()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def upload_form():
    return render_template('upload.html')

# Uses request form
@app.route('/upload/entire', methods=['POST'])
def upload_entire_file():
    if request.method == 'POST':
        # Verify form values
        if 'fileName' not in request.form or 'ByteData' not in request.files:
            flash('No file or filename part in the request')
            return redirect(request.url)

        # Process and save file to /app/uploads directory
        fileName = request.form['fileName']
        file = request.files['ByteData']
        if file and allowed_file(fileName):
            filename = secure_filename(fileName)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('File successfully uploaded')
            return redirect('/')
        else:
            flash('Allowed file types are txt, pdf, png, jpg, jpeg, gif, wav, mp4, db')
            return redirect(request.url)

# Uses headers
@app.route('/upload/chunk', methods=['POST'])
def upload_chunked_file():
    if request.method == 'POST':
        # Get the headers from the request
        file_name = request.headers.get('fileName')
        total_chunks = int(request.headers.get('TotalChunks'))
        cur_chunk = int(request.headers.get('CurChunk'))
        data = request.get_data()

        if not file_name or not total_chunks or not cur_chunk or not data:
            return jsonify({'error': 'Missing fileName, TotalChunks, CurChunk, or ByteData in headers'}), 400
        
        # Process the request values
        t = Thread(target=process_data, args=(file_name, total_chunks, cur_chunk, data))
        t.start()
    
        response = make_response('chunk received')
        response.status_code = 200
        return response


# Async function that begins processing the request data
def process_data(file_name, total_chunks, cur_chunk, data):
    # Read the data from the request

    with lock:
        # path for the file, make sure that rare dupes don't occur
        if file_name in uploaded_files:
            file_name = secure_filename("1_" + file_name)
        else:
            file_name = secure_filename(file_name)
        path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)

        # Check if earlier chunks of file have arrived
        if file_name not in awaiting_chunks:
            awaiting_chunks[file_name] = dict()

        # Add to the awaiting_chunks
        awaiting_chunks[file_name][cur_chunk] = data

        # If all chunks have arrived, assemble the file
        if len(awaiting_chunks[file_name]) == total_chunks:
            with open(path, 'ab') as f:
                for i in range(total_chunks):
                    f.write(awaiting_chunks[file_name][i])
            
            # Delete the file from awaiting_chunks
            print('File uploaded successfully:', file_name)
            uploaded_files.add(file_name)
            del awaiting_chunks[file_name]



if __name__ == "__main__":
    app.run(host = '0.0.0.0',port = 5000, debug = False, ssl_context=context)
    #app.run(host = '0.0.0.0',port = 5000, debug = False)
