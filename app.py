import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'france_decor_permanente_2026'

# --- CONFIGURAÇÃO ANTIBLOQUEIO ---
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'database_france.db')

# Forçamos o Flask a usar o caminho absoluto e removemos restrições de leitura
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# O timeout de 30 evita que o banco trave quando você cola muitos links
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"connect_args": {"timeout": 30}}

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ... (Mantenha o restante dos seus modelos e rotas como estão)