from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/ping')
def ping():
    return "pong"

if __name__ == '__main__':
    print("Rodando teste.py corretamente")
    app.run(debug=True)
