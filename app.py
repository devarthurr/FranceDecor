import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'chave_secreta_france_decor'

db_url = os.environ.get('DATABASE_URL', 'sqlite:///catalogo.db')
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=True) # Nova funcionalidade
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=True)
    image_url = db.Column(db.String(255), nullable=True)
    is_visible = db.Column(db.Boolean, default=True)

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

@app.route('/')
def index():
    search_query = request.args.get('search')
    category_filter = request.args.get('category')
    
    query = Product.query.filter_by(is_visible=True)
    
    if search_query:
        query = query.filter(Product.name.ilike(f'%{search_query}%'))
    if category_filter:
        query = query.filter(Product.category == category_filter)
        
    products = query.all()
    
    # Pegar todas as categorias únicas para os botões de filtro
    categories = db.session.query(Product.category).filter(Product.category != None).distinct().all()
    categories = [c[0] for c in categories]

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
        flash('Credenciais inválidas.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    if request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category')
        price_str = request.form.get('price')
        price = float(price_str.replace(',', '.')) if price_str else None
        description = request.form.get('description')
        image_url = request.form.get('image_url')
        
        new_product = Product(name=name, category=category, price=price, description=description, image_url=image_url)
        db.session.add(new_product)
        db.session.commit()
        flash('Produto adicionado!', 'success')
        return redirect(url_for('admin_dashboard'))

    products = Product.query.all()
    return render_template('admin.html', products=products)

@app.route('/admin/delete/<int:id>')
@login_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

def criar_banco():
    with app.app_context():
        db.create_all()
        if not Admin.query.first():
            hashed_pw = generate_password_hash('password123')
            admin = Admin(username='admin', password_hash=hashed_pw)
            db.session.add(admin)
            db.session.commit()

criar_banco()

if __name__ == '__main__':
    app.run(debug=True)