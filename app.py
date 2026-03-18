import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'france_decor_final_ultra_v3'

# --- CONFIGURAÇÃO DE PASTAS ---
basedir = os.path.abspath(os.path.dirname(__file__))

# Pasta física no seu VS Code
UPLOAD_FOLDER = os.path.join(basedir, 'static', 'produtos')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# --- BANCO DE DADOS ---
db_dir = os.path.join(basedir, 'database_file')
if not os.path.exists(db_dir): os.makedirs(db_dir)
db_path = os.path.join(db_dir, 'france_decor.db')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
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
    price = db.Column(db.Float, default=0.0)
    image_urls = db.Column(db.Text)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# --- ROTAS ---
@app.route('/')
def index():
    produtos = Product.query.order_by(Product.id.desc()).all()
    return render_template('index.html', produtos=produtos)

@app.route('/produto/<int:id>')
def produto_detalhes(id):
    p = Product.query.get_or_404(id)
    # Importante: limpando espaços e garantindo a lista
    images = [img.strip() for img in p.image_urls.split(',') if img.strip()]
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
        try:
            nome = request.form.get('name')
            preco = float(request.form.get('price').replace(',', '.')) if request.form.get('price') else 0.0
            desc = request.form.get('description')
            
            files = request.files.getlist('fotos')
            saved_paths = []
            
            for file in files:
                if file and allowed_file(file.filename):
                    # Criar nome seguro para o arquivo
                    filename = secure_filename(file.filename)
                    unique_name = f"foto_{nome.replace(' ', '_')}_{filename}"
                    
                    # Salva fisicamente na pasta static/produtos
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_name))
                    
                    # Salva no banco APENAS o nome do arquivo para o Flask achar no static
                    saved_paths.append(unique_name)
            
            urls_final = ",".join(saved_paths)
            novo = Product(name=nome, description=desc, image_urls=urls_final, price=preco)
            db.session.add(novo)
            db.session.commit()
            return redirect(url_for('admin'))
        except Exception as e:
            db.session.rollback()
            return f"Erro ao salvar: {e}"
    return render_template('admin.html', produtos=Product.query.all())

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