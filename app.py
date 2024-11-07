from flask import Flask, request, make_response
from flask_cors import CORS
from routers import user, result

app = Flask(__name__)
CORS(app,
    resources={
        r"/api/*":
        {
            "origins": ["https://porcalabs.github.io"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["*"],
            "expose_headers": ["*"],
            "supports_credentials": True,
            "send_wildcard": False,
            "max_age": 3600
        }
    }
)


@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin",
                            "https://porcalabs.github.io")
        response.headers.add("Access-Control-Allow-Headers", "*")
        response.headers.add("Access-Control-Allow-Methods",
                            "GET, POST, PUT, DELETE, OPTIONS")
        response.headers.add("Access-Control-Max-Age", "86400")
        return response


# Register blueprints with api prefix
app.register_blueprint(user.bp, url_prefix='/api/users')
app.register_blueprint(result.bp, url_prefix='/api/results')

application = app

if __name__ == "__main__":
    app.run()
