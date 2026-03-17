import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'chave_secreta_france_decor'

# Configuração do Banco de Dados
db_path = os.path.join(app.instance_path, 'catalogo.db')
if not os.path.exists(app.instance_path):
    os.makedirs(app.instance_path)

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Modelo do Produto - Corrigido para aceitar campos vazios
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=True, default="Geral")
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=True) # Aceita None (vazio)
    image_url = db.Column(db.String(255), nullable=True)
    is_visible = db.Column(db.Boolean, default=True)

class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

# Rota do Painel Admin - Protegida contra erros de envio
@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            category = request.form.get('category') or "Geral"
            description = request.form.get('description')
            image_url = request.form.get('image_url')
            
            # Tratamento do preço para não quebrar o código
            price_str = request.form.get('price')
            price = None
            if price_str and price_str.strip():
                price = float(price_str.replace(',', '.'))
            
            if not name:
                flash('O nome do produto é obrigatório!', 'danger')
                return redirect(url_for('admin_dashboard'))

            new_product = Product(
                name=name, 
                category=category, 
                price=price, 
                description=description, 
                image_url=image_url
            )
            
            db.session.add(new_product)
            db.session.commit() # <--- Esta linha é a mais importante!
            print(f"Produto {name} salvo com sucesso!") # Isso vai aparecer no seu terminal preto
            return redirect(url_for('admin_dashboard'))
            db.session.commit()
            flash('Produto adicionado com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao salvar: {str(e)}', 'danger')
            print(f"ERRO NO SERVIDOR: {e}") # Isso aparece no seu terminal preto

        return redirect(url_for('admin_dashboard'))

    products = Product.query.all()
    return render_template('admin.html', products=products)

# --- MANTENHA AS OUTRAS ROTAS (index, login, logout) IGUAIS ---
@app.route('/')
def index():
    products = Product.query.filter_by(is_visible=True).all()
    categories = db.session.query(Product.category).distinct().all()
    categories = [c[0] for c in categories if c[0]]
    return render_template('index.html', products=products, categories=categories)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password_hash, password):
            login_user(admin)
            return redirect(url_for('admin_dashboard'))
        flash('Usuário ou senha incorretos.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user(); return redirect(url_for('index'))

@app.route('/admin/delete/<int:id>')
@login_required
def delete_product(id):
    p = Product.query.get_or_404(id); db.session.delete(p); db.session.commit()
    return redirect(url_for('admin_dashboard'))

def criar_banco():
    with app.app_context():
        db.create_all()
        if not Admin.query.filter_by(username='admin').first():
            db.session.add(Admin(username='admin', password_hash=generate_password_hash('password123')))
            db.session.commit()

if __name__ == '__main__':
    criar_banco()
    app.run(debug=True)