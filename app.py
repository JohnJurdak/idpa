from flask import Flask, request, render_template, jsonify, flash, redirect, url_for
from werkzeug.utils import secure_filename
import os
from searching import search, knn_search, upload_and_compare  # Import your functions here

app = Flask(__name__)

# Configure the secret key for session management (used for flashing messages)
app.secret_key = 'your_secret_key'

# Configure the upload folder within the current directory
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Check for allowed file types
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('home.html')  # This HTML page will have the forms for search, KNN search, and upload.

@app.route('/search', methods=['POST'])
def do_search():
    word = request.form['word']
    results = search(word)
    return jsonify(results)  # Adjust the search function to return results

@app.route('/knn_search', methods=['POST'])
def do_knn_search():
    vector = request.form['vector'].split(',')  # Assuming vector is passed as a comma-separated string
    vector = [float(i) for i in vector]  # Convert each element to float
    results = knn_search(vector)
    return jsonify(results)  # Adjust the knn_search function to return results

@app.route('/upload_and_compare', methods=['POST'])
def do_upload_and_compare():
    # Check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        results = upload_and_compare(file_path)
        return jsonify(results)  # Adjust the upload_and_compare function to return results

    flash('File not allowed')
    return redirect(request.url)

if __name__ == '__main__':
    app.run(debug=True)
