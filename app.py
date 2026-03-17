import os
import tempfile
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'francedecor_ultra_safe_key_2026'

# --- CONFIGURAÇÃO DE BANCO ANTI-ERRO ---
# Se estiver no Vercel, usa o Postgres deles. 
# Se estiver no PC, usa um banco temporário que o Windows NÃO PODE bloquear como "readonly"
if os.environ.get('DATABASE_URL'):
    db_url = os.environ.get('DATABASE_URL').replace("postgres://", "postgresql://", 1)
else:
    # Cria o banco na pasta temporária do sistema (impossível dar erro de readonly)
    temp_db = os.path.join(tempfile.gettempdir(), 'francedecor_temp.db')
    db_url = f'sqlite:///{temp_db}'

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Modelos
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    image_url = db.Column(db.String(500))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- ROTAS ---
@app.route('/')
def index():
    produtos = Product.query.order_by(Product.id.desc()).all()
    return render_template('index.html', produtos=produtos)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and check_password_hash(user.password, request.form.get('password')):
            login_user(user)
            return redirect(url_for('admin'))
        flash('Credenciais Inválidas')
    return render_template('login.html')

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if request.method == 'POST':
        try:
            nome = request.form.get('name')
            preco_raw = request.form.get('price') or "0"
            preco = float(preco_raw.replace(',', '.'))
            
            novo = Product(
                name=nome,
                description=request.form.get('description'),
                image_url=request.form.get('image_url'),
                price=preco
            )
            db.session.add(novo)
            db.session.commit()
            return redirect(url_for('admin'))
        except Exception as e:
            db.session.rollback()
            return f"Erro Crítico: {e}"
            
    produtos = Product.query.all()
    return render_template('admin.html', produtos=produtos)

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    p = Product.query.get(id)
    if p:
        db.session.delete(p)
        db.session.commit()
    return redirect(url_for('admin'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# Inicia o banco de dados
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        db.session.add(User(username='admin', password=generate_password_hash('password123')))
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)