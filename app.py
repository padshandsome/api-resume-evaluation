from flask import Flask, jsonify, request
import os
from flask_cors import CORS
from score import score_model

app =  Flask(__name__)

# This is the path to the directory where you want to save the uploaded files
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

CORS(app, resources = {r"/evaluate/*": {"origins": "http://localhost:3000"}})

@app.route('/evaluate', methods=['POST'])
def evaluate():
    print("Request Headers:", request.headers)
    print("Request Form:", request.form)
    print("Request Files:", request.files)
    
    if 'pdf' not in request.files:
        return jsonify({'message': 'No file part', 'api_response': 'Not valid for calling the api.'}), 400 
    file = request.files['pdf']

    if file.filename == '':
        return jsonify({'message': 'No selected file', 'api_response': 'Not valid for calling the api.'}), 400 
    
    
    if file and file.filename.endswith('.pdf'):
        filename = file.filename 
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        print("Successfully post pdf to the api")

        model = score_model()
        print("Successfully load scoring module")

        response_json = model.score(file_path = file_path)
        response_json['message'] = 'File uploaded successfully'

        # clean up cache
        try:
            os.remove(file_path)
            print("Successfully delete file")
        except:
            print("Error deleting file, please check if the app still running.")

        return jsonify(response_json), 200

    else:
        return jsonify({'message': 'Invalid file type', 'api_response': 'Not valid for calling the api.'}), 400


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
