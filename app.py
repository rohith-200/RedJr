from flask import Flask, render_template
from config import Config
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'sfsu-team-7-secret'
app.config.from_object(Config)
db = SQLAlchemy(app)

from routes import *

register_blueprints(app)

if __name__ == '__main__':
    register_blueprints(app)
    app.run(debug=True)


