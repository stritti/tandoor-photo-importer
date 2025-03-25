import os
import uuid
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.utils import secure_filename
from ai_service import AIService
from ai_providers.prompt_config import get_prompt

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
            filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Absoluten Pfad für die Antwort erstellen
            abs_filepath = os.path.abspath(filepath)
            
            # Hole den Prompt-Typ aus dem Request oder verwende "general" als Standard
            prompt_type = request.form.get('prompt_type', 'general')
            
            response_data = {
                'success': True,
                'message': 'Bild erfolgreich hochgeladen',
                'filename': filename,
                'path': abs_filepath
            }
            
            # Führe immer eine KI-Analyse durch mit dem konfigurierten Prompt
            ai_result = AIService.analyze_image(filepath, get_prompt(prompt_type))
            response_data['ai_analysis'] = ai_result
            
            return jsonify(response_data)
        
        return jsonify({'error': 'Dateityp nicht erlaubt'}), 400
    except Exception as e:
        app.logger.error(f"Fehler beim Hochladen: {str(e)}")
        return jsonify({'error': f'Serverfehler: {str(e)}'}), 500

@app.route('/api/analyze-image', methods=['POST'])
def analyze_image():
    try:
        data = request.json
        
        if not data or 'image_path' not in data:
            return jsonify({'error': 'Kein Bildpfad angegeben'}), 400
        
        image_path = data['image_path']
        prompt_type = data.get('prompt_type', 'general')
        
        # Überprüfen, ob die Datei existiert
        if not os.path.exists(image_path):
            return jsonify({'error': 'Bild nicht gefunden'}), 404
        
        # Bild mit KI analysieren und den konfigurierten Prompt verwenden
        ai_result = AIService.analyze_image(image_path, get_prompt(prompt_type))
        
        return jsonify({
            'success': True,
            'image_path': image_path,
            'ai_analysis': ai_result
        })
        
    except Exception as e:
        app.logger.error(f"Fehler bei der Bildanalyse: {str(e)}")
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
