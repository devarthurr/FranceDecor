import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'france_decor_neon_2026'

# --- CONFIGURAÇÃO DA DATABASE (NEON) ---
# Aqui usamos a sua URL do Neon que você forneceu
NEON_URL = "postgresql://neondb_owner:npg_FWjUN2XYlku0@ep-quiet-sound-aco0b99g-pooler.sa-east-1.aws.neon.tech/neondb?channel_binding=require&sslmode=require"

# A Vercel prefere o prefixo postgresql:// em vez de postgres://
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', NEON_URL).replace("postgresql://neondb_owner:npg_FWjUN2XYlku0@ep-quiet-sound-aco0b99g-pooler.sa-east-1.aws.neon.tech/neondb?channel_binding=require&sslmode=require", "postgresql://neondb_owner:npg_FWjUN2XYlku0@ep-quiet-sound-aco0b99g-pooler.sa-east-1.aws.neon.tech/neondb?channel_binding=require&sslmode=require", 1)
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
    image_urls = db.Column(db.Text) # Links das imagens separados por vírgula

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- ROTAS ---
@app.route('/')
def index():
    produtos = Product.query.order_by(Product.id.desc()).all()
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
        flash('Usuário ou senha inválidos.')
    return render_template('login.html')

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if request.method == 'POST':
        try:
            nome = request.form.get('name')
            p_raw = request.form.get('price').replace(',', '.') if request.form.get('price') else '0'
            preco = float(p_raw)
            links = request.form.get('image_urls').strip()
            desc = request.form.get('description')
            novo = Product(name=nome, description=desc, image_urls=links, price=preco)
            db.session.add(novo)
            db.session.commit()
            flash('Produto cadastrado com sucesso no Neon!')
            return redirect(url_for('admin'))
        except Exception as e:
            db.session.rollback()
            return f"Erro ao salvar: {e}"
    return render_template('admin.html', produtos=Product.query.all())

@app.route('/admin/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    p = Product.query.get_or_404(id)
    if request.method == 'POST':
        p.name = request.form.get('name')
        p_val = request.form.get('price').replace(',', '.')
        p.price = float(p_val)
        p.image_urls = request.form.get('image_urls').strip()
        p.description = request.form.get('description')
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template('edit.html', p=p)

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    p = Product.query.get(id); db.session.delete(p); db.session.commit()
    return redirect(url_for('admin'))

@app.route('/logout')
def logout():
    logout_user(); return redirect(url_for('index'))

# Cria as tabelas no Neon automaticamente
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        db.session.add(User(username='admin', password=generate_password_hash('admin123')))
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)