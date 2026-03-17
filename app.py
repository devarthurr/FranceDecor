import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'france_decor_secret_key_2024'

# Configuração do Banco de Dados (Detecta Vercel Postgres ou SQLite Local)
db_url = os.environ.get('DATABASE_URL')
if db_url:
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
else:
    db_path = os.path.join(app.instance_path, 'catalogo.db')
    if not os.path.exists(app.instance_path):
        os.makedirs(app.instance_path)
    db_url = f'sqlite:///{db_path}'

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
    category = db.Column(db.String(50), nullable=True, default="Decoração")
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=True)
    image_url = db.Column(db.String(255), nullable=True)
    is_visible = db.Column(db.Boolean, default=True)

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

@app.route('/')
def index():
    cat_filter = request.args.get('category')
    search = request.args.get('search')
    query = Product.query.filter_by(is_visible=True)
    if cat_filter: query = query.filter_by(category=cat_filter)
    if search: query = query.filter(Product.name.ilike(f'%{search}%'))
    products = query.order_by(Product.id.desc()).all()
    categories = db.session.query(Product.category).distinct().all()
    categories = [c[0] for c in categories if c[0]]
    return render_template('index.html', products=products, categories=categories)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = Admin.query.filter_by(username=request.form.get('username')).first()
        if user and check_password_hash(user.password_hash, request.form.get('password')):
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        flash('Login inválido', 'danger')
    return render_template('login.html')

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    if request.method == 'POST':
        try:
            p_price = request.form.get('price')
            new_p = Product(
                name=request.form.get('name'),
                category=request.form.get('category') or "Geral",
                description=request.form.get('description'),
                image_url=request.form.get('image_url'),
                price=float(p_price.replace(',', '.')) if p_price else None
            )
            db.session.add(new_p)
            db.session.commit()
            flash('Produto salvo!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro: {str(e)}', 'danger')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin.html', products=Product.query.all())

@app.route('/admin/delete/<int:id>')
@login_required
def delete_product(id):
    p = Product.query.get(id)
    db.session.delete(p); db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/logout')
def logout():
    logout_user(); return redirect(url_for('index'))

def init_db():
    with app.app_context():
        db.create_all()
        if not Admin.query.filter_by(username='admin').first():
            db.session.add(Admin(username='admin', password_hash=generate_password_hash('password123')))
            db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(debug=True)