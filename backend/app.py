import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='../dist/frontend', static_url_path='/')
# CORS für alle Routen aktivieren mit zusätzlichen Optionen
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

# Konfiguration für Datei-Uploads
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Stellen Sie sicher, dass der Upload-Ordner existiert
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify(status='ok')

@app.route('/api/upload-image', methods=['POST'])
def upload_image():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'Keine Bilddatei gefunden'}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'error': 'Keine Datei ausgewählt'}), 400
        
        if file and allowed_file(file.filename):
            # Eindeutigen Dateinamen generieren
            import uuid
            filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Absoluten Pfad für die Antwort erstellen
            abs_filepath = os.path.abspath(filepath)
            
            return jsonify({
                'success': True,
                'message': 'Bild erfolgreich hochgeladen',
                'filename': filename,
                'path': abs_filepath
            })
        
        return jsonify({'error': 'Dateityp nicht erlaubt'}), 400
    except Exception as e:
        app.logger.error(f"Fehler beim Hochladen: {str(e)}")
        return jsonify({'error': f'Serverfehler: {str(e)}'}), 500

@app.route('/')
def serve_frontend():
    return app.send_static_file('index.html')

# Fallback-Route für SPA
@app.route('/<path:path>')
def catch_all(path):
    try:
        return app.send_static_file(path)
    except:
        return app.send_static_file('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
