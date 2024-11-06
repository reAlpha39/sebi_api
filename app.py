from flask import Flask
from flask_cors import CORS
from routers import user

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://porcalabs.github.io"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Register blueprints
app.register_blueprint(user.bp)

application = app

if __name__ == "__main__":
    app.run()
