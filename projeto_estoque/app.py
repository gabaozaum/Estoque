from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'chave_secreta_fecaf'


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///estoque.db'
db = SQLAlchemy(app)


class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    login = db.Column(db.String(20), unique=True, nullable=False)
    senha = db.Column(db.String(20), nullable=False)
    perfil = db.Column(db.String(20), default='Comum') 

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    minimo = db.Column(db.Integer, default=5) 


with app.app_context():
    db.create_all()
    if not Usuario.query.filter_by(login='admin').first():
        admin = Usuario(nome='Admin', login='admin', senha='123', perfil='Administrador')
        db.session.add(admin)
        db.session.commit()

# --- ROTAS ---
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    
    usuario_input = request.form.get('usuario')
    senha_input = request.form.get('senha')
    user = Usuario.query.filter_by(login=usuario_input, senha=senha_input).first()
    
    if user:
        session['user_id'] = user.id
        session['nome'] = user.nome
        session['perfil'] = user.perfil
        return redirect(url_for('dashboard'))
    flash('Erro no login!')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    produtos = Produto.query.all()
    return render_template('dashboard.html', produtos=produtos)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/cadastro')
def pagina_cadastro():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('cadastro.html')

@app.route('/cadastrar', methods=['POST'])
def cadastrar_produto():
    nome = request.form.get('nome')
    quantidade = int(request.form.get('quantidade'))
    minimo = int(request.form.get('minimo'))
    
    novo = Produto(nome=nome, quantidade=quantidade, minimo=minimo)
    db.session.add(novo)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/excluir/<int:id>')
def excluir_produto(id):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    
    produto = Produto.query.get(id)
    
    if produto:
        db.session.delete(produto) 
        db.session.commit()        
    
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    app.run(debug=True)