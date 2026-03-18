import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'france_decor_resgate_final_2026'

# --- CONFIGURAÇÃO DO BANCO (RAIZ DO PROJETO) ---
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'france_decor.db')

# Configuração para evitar o erro 500: se estiver na Vercel, o banco é apenas leitura
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- MODELOS ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, default=0.0)
    image_urls = db.Column(db.Text)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- ROTAS ---
@app.route('/')
def index():
    try:
        produtos = Product.query.order_by(Product.id.desc()).all()
    except:
        produtos = [] # Se o banco falhar na Vercel, o site abre vazio mas NÃO CAI
    return render_template('index.html', produtos=produtos)

@app.route('/produto/<int:id>')
def produto_detalhes(id):
    p = Product.query.get_or_404(id)
    images = [img.strip() for img in p.image_urls.split(',') if p.image_urls and img.strip()]
    return render_template('produto.html', p=p, images=images)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and check_password_hash(user.password, request.form.get('password')):
            login_user(user)
            return redirect(url_for('admin'))
    return render_template('login.html')

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if request.method == 'POST':
        # BLOQUEIO DE GRAVAÇÃO NA VERCEL (IMPEDE O ERRO 500)
        if os.environ.get('VERCEL'):
            return "ERRO: Cadastre os produtos no VS Code local e faça o PUSH do arquivo 'france_decor.db'."
        
        try:
            nome = request.form.get('name')
            p_raw = request.form.get('price').replace(',', '.') if request.form.get('price') else '0'
            preco = float(p_raw)
            links = request.form.get('image_urls').strip()
            desc = request.form.get('description')
            novo = Product(name=nome, description=desc, image_urls=links, price=preco)
            db.session.add(novo)
            db.session.commit()
            return redirect(url_for('admin'))
        except Exception as e:
            db.session.rollback()
            return f"Erro local: {e}"
            
    return render_template('admin.html', produtos=Product.query.all())

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# Inicialização segura
with app.app_context():
    try:
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            db.session.add(User(username='admin', password=generate_password_hash('password123')))
            db.session.commit()
    except:
        pass # Ignora erros de criação na Vercel

if __name__ == '__main__':
    app.run(debug=True)