from flask import Flask
from flask_cors import CORS
from routers.user import user_bp

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "allow_credentials": True,
        "methods": ["*"],
        "headers": ["*"]
    }
})

# Register blueprints
app.register_blueprint(user_bp)

application = app

if __name__ == "__main__":
    app.run()
