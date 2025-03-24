from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__, static_folder='../dist/frontend', static_url_path='/')
CORS(app)

@app.route('/api/hello')
def hello():
    return jsonify(message="Hallo von Flask!")

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
