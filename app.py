import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'francedecor_2026_final'

# --- CONFIGURAÇÃO AUTOMÁTICA DE BANCO ---
# Garante que a pasta 'instance' exista para evitar o erro de 'Read-Only'
if not os.path.exists(app.instance_path):
    try:
        os.makedirs(app.instance_path)
    except:
        pass

# Banco de dados dentro da pasta instance (Padrão Seguro)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'catalogo.db')
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
        flash('Usuário ou senha inválidos.')
    return render_template('login.html')

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if request.method == 'POST':
        try:
            nome = request.form.get('name')
            desc = request.form.get('description')
            img = request.form.get('image_url')
            preco_raw = request.form.get('price')
            
            # Limpeza de preço para aceitar vírgula ou ponto
            preco = 0.0
            if preco_raw:
                preco = float(preco_raw.replace(',', '.'))

            novo = Product(name=nome, description=desc, image_url=img, price=preco)
            db.session.add(novo)
            db.session.commit()
            flash('Produto adicionado!')
            return redirect(url_for('admin'))
        except Exception as e:
            db.session.rollback()
            return f"Erro ao salvar: {e}"

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

# --- INICIALIZAÇÃO ---
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        db.session.add(User(
            username='admin', 
            password=generate_password_hash('password123')
        ))
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)