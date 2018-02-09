from flask import Flask


from app.apis import api_v1 as api1

def create_app(config_name):
    app = Flask(__name__)
    app.config.SWAGGER_UI_JSONEDITOR = True
    app.register_blueprint(api1)

    # attach routes and custom error pages here
    return app