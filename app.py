import os
from flask import Flask, render_template, request, redirect, url_for
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

# Sua URL do Neon configurada
DATABASE_URL = "postgresql://neondb_owner:npg_FWjUN2XYlku0@ep-quiet-sound-aco0b99g-pooler.sa-east-1.aws.neon.tech/neondb?channel_binding=require&sslmode=require"

def get_db_connection():
    # Usa a variável da Vercel se existir, senão usa a sua direta
    target_url = os.getenv('postgresql://neondb_owner:npg_FWjUN2XYlku0@ep-quiet-sound-aco0b99g-pooler.sa-east-1.aws.neon.tech/neondb?channel_binding=require&sslmode=require', DATABASE_URL)
    return psycopg2.connect(target_url)

@app.route('/')
def index():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('SELECT * FROM produtos ORDER BY criado_em DESC;')
        produtos = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('index.html', produtos=produtos)
    except Exception as e:
        return f"Erro ao conectar no banco: {e}"

@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

@app.route('/adicionar', methods=['POST'])
def adicionar():
    nome = request.form['nome']
    descricao = request.form['descricao']
    preco = request.form['preco']
    estoque = request.form['estoque']
    categoria = request.form.get('categoria', 'Geral')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (%s, %s, %s, %s, %s)',
        (nome, descricao, preco, estoque, categoria)
    )
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)