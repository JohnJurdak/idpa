from flask import Flask, request, render_template, jsonify, flash, redirect, url_for
from werkzeug.utils import secure_filename
import os
# Import Elasticsearch functions
from idf import tf_search, idf_search, bm25_search, get_prev
from searching import search, knn_search, upload_and_compare, build_and_execute_query, search_as_you_type, search_specific

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
        print('results', results)
        return jsonify(results)  # Adjust the upload_and_compare function to return results

    flash('File not allowed')
    return redirect(request.url)

# Elasticsearch routes
@app.route('/tf_search', methods=['POST'])
def tf_search_api():
    data = request.json
    index_name = data.get("index_name")
    if not index_name:
        return jsonify({"status": "error", "message": "Index name is required"}), 400
    result = tf_search(index_name)
    return jsonify(result)

@app.route('/idf_search', methods=['POST'])
def idf_search_api():
    data = request.json
    index_name = data.get("index_name")
    if not index_name:
        return jsonify({"status": "error", "message": "Index name is required"}), 400
    result = idf_search(index_name)
    return jsonify(result)

@app.route('/bm25_search', methods=['POST'])
def bm25_api():
    data = request.json
    index_name = data.get("index_name")
    if not index_name:
        return jsonify({"status": "error", "message": "Index name is required"}), 400
    result = bm25_search(index_name)
    return jsonify(result)


@app.route('/custom_search', methods=['POST'])
def do_custom_search():
    input_str = request.form['input_str']
    results = build_and_execute_query(input_str)
    return jsonify(results)

@app.route('/search_books', methods=['GET'])
def search_books():
    query = request.args.get('query', '')
    results = search_as_you_type(query)
    return jsonify(results)

@app.route('/get_prev', methods=['GET'])
def get_prev_api():
    items = get_prev()
    return jsonify(list(items))


@app.route('/search_specific', methods=['GET'])
def search_specific_api():
    word = request.args.get('word')
    index_name = request.args.get('index')
    if not word or not index_name:
        return jsonify({"error": "Missing word or index name"}), 400

    try:
        hits = search_specific(word, index_name)
        return jsonify(hits)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
