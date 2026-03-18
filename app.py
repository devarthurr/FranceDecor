import os
import tempfile
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

@app.route('/produto/<int:id>')
def produto_detalhes(id):
    p = Product.query.get_or_404(id)
    # Separamos as imagens para o carrossel
    images = p.image_urls.split(',') if p.image_urls else []
    return render_template('produto.html', p=p, images=images)

app = Flask(__name__)
app.secret_key = 'france_decor_v5_pro'

# Banco de dados temporário para evitar erro de leitura
temp_db = os.path.join(tempfile.gettempdir(), 'francedecor_v5.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{temp_db}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    # Agora aceita várias URLs separadas por vírgula
    image_urls = db.Column(db.Text) 

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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
    return render_template('login.html')

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if request.method == 'POST':
        nome = request.form.get('name')
        preco = float(request.form.get('price').replace(',', '.')) if request.form.get('price') else 0.0
        # Pegamos as URLs e limpamos espaços
        urls = request.form.get('image_urls')
        
        novo = Product(name=nome, description=request.form.get('description'), 
                       image_urls=urls, price=preco)
        db.session.add(novo)
        db.session.commit()
        return redirect(url_for('admin'))
    
    produtos = Product.query.all()
    return render_template('admin.html', produtos=produtos)

@app.route('/admin/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    p = Product.query.get_or_404(id)
    if request.method == 'POST':
        p.name = request.form.get('name')
        p.description = request.form.get('description')
        p.image_urls = request.form.get('image_urls')
        p.price = float(request.form.get('price').replace(',', '.')) if request.form.get('price') else 0.0
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

with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        db.session.add(User(username='admin', password=generate_password_hash('password123')))
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)
