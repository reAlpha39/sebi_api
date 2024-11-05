from quart import Quart
from quart_cors import cors
from routes.user import user_bp

app = Quart(__name__)
app = cors(app, allow_origin="*", allow_credentials=True,
           allow_methods=["*"], allow_headers=["*"])

# Register blueprints
app.register_blueprint(user_bp)

application = app

if __name__ == "__main__":
    app.run()
