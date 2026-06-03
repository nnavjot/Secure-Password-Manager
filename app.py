from flask import Flask
from database import init_db


def create_app():
    app = Flask(__name__, instance_relative_config=True)

   
    app.config["SECRET_KEY"] = "dev-secret-change-in-production"
    import os
    app.config["DATABASE"] = os.path.join(app.instance_path, "securevault.db")
    os.makedirs(app.instance_path, exist_ok=True)


    init_db(app)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
