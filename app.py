import os
import sqlite3
from flask import Flask, redirect, url_for, g
from flask_login import LoginManager
from config import Config

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'warning'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            Config.SQLITE_DB,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
        with g.db:
            g.db.execute("PRAGMA foreign_keys = ON;")
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    login_manager.init_app(app)

    @app.teardown_appcontext
    def teardown_db(exception):
        close_db(exception)

    from models.user import get_user_by_id
    @login_manager.user_loader
    def load_user(user_id):
        return get_user_by_id(int(user_id))

    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.organizer import organizer_bp
    from routes.student import student_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(organizer_bp, url_prefix='/organizer')
    app.register_blueprint(student_bp, url_prefix='/student')

    @app.route('/')
    def index():
        from flask_login import current_user
        if current_user.is_authenticated:
            if current_user.role == 'admin': return redirect(url_for('admin.dashboard'))
            if current_user.role == 'organizer': return redirect(url_for('organizer.dashboard'))
            if current_user.role == 'student': return redirect(url_for('student.dashboard'))
        from flask import render_template
        return render_template('index.html')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
