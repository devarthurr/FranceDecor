import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'uma_chave_secreta_muito_forte' # Troque por algo seguro

# Lógica para usar SQLite localmente ou Postgres no Vercel
db_url = os.environ.get('DATABASE_URL', 'sqlite:///catalogo.db')
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1) # Correção padrão para SQLAlchemy

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Por favor, faça login para acessar esta página."

# --- MODELOS DE BANCO DE DADOS ---

class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(255), nullable=True) # Link da imagem
    is_visible = db.Column(db.Boolean, default=True) # Controle de visibilidade

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

# --- ROTAS (PÁGINAS) ---

# 1. Catálogo Público (Para os clientes)
@app.route('/')
def index():
    search_query = request.args.get('search')
    if search_query:
        # Busca produtos visíveis que contenham o texto no nome
        products = Product.query.filter(Product.is_visible == True, Product.name.ilike(f'%{search_query}%')).all()
    else:
        # Mostra todos os produtos visíveis
        products = Product.query.filter_by(is_visible=True).all()
    
    return render_template('index.html', products=products)

# 2. Login do Administrador
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and check_password_hash(admin.password_hash, password):
            login_user(admin)
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Usuário ou senha incorretos.', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# 3. Painel de Administração (Protegido)
@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    if request.method == 'POST':
        # Adicionar novo produto
        name = request.form.get('name')
        price = float(request.form.get('price').replace(',', '.'))
        description = request.form.get('description')
        image_url = request.form.get('image_url')
        
        new_product = Product(name=name, price=price, description=description, image_url=image_url)
        db.session.add(new_product)
        db.session.commit()
        flash('Produto adicionado com sucesso!', 'success')
        return redirect(url_for('admin_dashboard'))

    products = Product.query.all()
    return render_template('admin.html', products=products)

# 4. Deletar Produto
@app.route('/admin/delete/<int:id>')
@login_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('Produto excluído!', 'success')
    return redirect(url_for('admin_dashboard'))

# --- INICIALIZAÇÃO ---
def criar_banco():
    with app.app_context():
        db.create_all()
        # Cria um admin padrão se não existir (Usuário: admin | Senha: password123)
        if not Admin.query.first():
            hashed_pw = generate_password_hash('password123')
            admin = Admin(username='admin', password_hash=hashed_pw)
            db.session.add(admin)
            db.session.commit()

# Executa a criação do banco ao carregar
criar_banco()

if __name__ == '__main__':
    app.run(debug=True)