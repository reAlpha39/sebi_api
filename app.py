from flask import Flask
from flask_cors import CORS
from routers import user

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["https://porcalabs.github.io"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": [
            "Origin",
            "Content-Type",
            "Authorization",
            "Accept",
            "X-Requested-With",
            "Access-Control-Request-Method",
            "Access-Control-Request-Headers",
            "Access-Control-Allow-Methods"
        ],
        "expose_headers": [
            "Access-Control-Allow-Origin",
            "Access-Control-Allow-Methods",
            "Access-Control-Allow-Headers"
        ],
        "supports_credentials": True,
        "max_age": 3600
    }
})

# Register blueprints
app.register_blueprint(user.bp)

application = app

if __name__ == "__main__":
    app.run()
