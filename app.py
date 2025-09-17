from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import csv
import io
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder='.', static_folder='.', static_url_path='')
app.config['SECRET_KEY'] = 'change-this-secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///verdetch.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Usuario {self.nome}>'

class Auth(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    usuario = db.relationship('Usuario', backref=db.backref('auth', uselist=False))

class PegadaCarbono(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    transporte = db.Column(db.Float, nullable=False)
    energia = db.Column(db.Float, nullable=False)
    alimentacao = db.Column(db.Integer, nullable=False)
    lixo = db.Column(db.Integer, nullable=False)
    total_co2 = db.Column(db.Float, nullable=False)
    data_calculo = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PegadaCarbono {self.total_co2} kg CO2>'

class ResultadoQuiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    pontuacao = db.Column(db.Integer, nullable=False)
    total_perguntas = db.Column(db.Integer, nullable=False)
    data_realizacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ResultadoQuiz {self.pontuacao}/{self.total_perguntas}>'

with app.app_context():
    db.create_all()

def login_required(fn):
    def wrapper(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('login'))
        return fn(*args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        auth = Auth.query.filter_by(username=username).first()
        if not auth:
            return render_template('login.html', error='Conta ainda não existe', email=username)
        if not check_password_hash(auth.password_hash, password):
            return render_template('login.html', error='Senha incorreta', email=username)
        session['user_id'] = auth.usuario_id
        session['username'] = auth.username
        session['nome'] = auth.usuario.nome
        return redirect(url_for('login_success'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        if not (nome and email and password and confirm_password):
            return render_template('cadastro.html', error='Preencha todos os campos')
        if len(password) < 8:
            return render_template('cadastro.html', error='A senha deve ter ao menos 8 caracteres')
        if password.lower() == password or password.upper() == password:
            return render_template('cadastro.html', error='A senha deve conter letras maiúsculas e minúsculas')
        if password != confirm_password:
            return render_template('cadastro.html', error='As senhas não conferem')
        if Auth.query.filter_by(username=email).first():
            return render_template('cadastro.html', error='E-mail já está em uso')
        if Usuario.query.filter_by(email=email).first():
            return render_template('cadastro.html', error='E-mail já cadastrado')
        usuario = Usuario(nome=nome, email=email)
        db.session.add(usuario)
        db.session.flush()
        auth = Auth(usuario_id=usuario.id, username=email, password_hash=generate_password_hash(password))
        db.session.add(auth)
        db.session.commit()
        session['user_id'] = usuario.id
        session['username'] = email
        session['nome'] = nome
        return redirect(url_for('register_success'))
    return redirect(url_for('cadastro'))

@app.route('/login-success')
def login_success():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    return render_template('login_success.html', nome=session.get('nome'), username=session.get('username'))

@app.route('/register-success')
def register_success():
    if not session.get('user_id'):
        return redirect(url_for('register'))
    return render_template('register_success.html', nome=session.get('nome'), username=session.get('username'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/minha-conta')
@login_required
def minha_conta():
    usuario_id = session.get('user_id')
    usuario = Usuario.query.get(usuario_id)
    return render_template('minha_conta.html', usuario=usuario, email=session.get('username'))

@app.route('/api/me')
def api_me():
    if not session.get('user_id'):
        return jsonify({'authenticated': False})
    return jsonify({'authenticated': True, 'id': session['user_id'], 'username': session.get('username'), 'nome': session.get('nome')})

@app.route('/curiosidades')
@login_required
def curiosidades():
    return render_template('curiosidades.html')

@app.route('/maquete')
@login_required
def maquete():
    return render_template('maquete.html')

@app.route('/carbono')
@login_required
def carbono():
    return render_template('carbono.html')

@app.route('/quiz')
@login_required
def quiz():
    return render_template('quiz.html')

@app.route('/api/calcular-pegada', methods=['POST'])
def calcular_pegada():
    try:
        data = request.get_json()
        
        co2_transporte = data['transporte'] * 0.21
        co2_energia = data['energia'] * 0.5
        co2_alimentacao = data['alimentacao'] * 2.5
        co2_lixo = data['lixo'] * 10
        
        total_co2 = co2_transporte + co2_energia + co2_alimentacao + co2_lixo
        
        usuario_id = session.get('user_id')
        nova_pegada = PegadaCarbono(
            usuario_id=usuario_id,
            transporte=data['transporte'],
            energia=data['energia'],
            alimentacao=data['alimentacao'],
            lixo=data['lixo'],
            total_co2=total_co2
        )
        db.session.add(nova_pegada)
        db.session.commit()
        
        return jsonify({
            'transporte': round(co2_transporte, 2),
            'energia': round(co2_energia, 2),
            'alimentacao': round(co2_alimentacao, 2),
            'lixo': round(co2_lixo, 2),
            'total': round(total_co2, 2),
            'id': nova_pegada.id
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/salvar-quiz', methods=['POST'])
def salvar_quiz():
    try:
        data = request.get_json()
        
        usuario_id = session.get('user_id')
        novo_resultado = ResultadoQuiz(
            usuario_id=usuario_id,
            pontuacao=data['pontuacao'],
            total_perguntas=data['total_perguntas']
        )
        db.session.add(novo_resultado)
        db.session.commit()
        
        return jsonify({
            'message': 'Resultado salvo com sucesso!',
            'id': novo_resultado.id
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/admin/dados')
def admin_dados():
    pegadas = PegadaCarbono.query.all()
    resultados = ResultadoQuiz.query.all()
    
    dados = {
        'pegadas_carbono': [{
            'id': p.id,
            'transporte': p.transporte,
            'energia': p.energia,
            'alimentacao': p.alimentacao,
            'lixo': p.lixo,
            'total_co2': p.total_co2,
            'data_calculo': p.data_calculo.strftime('%Y-%m-%d %H:%M:%S')
        } for p in pegadas],
        'resultados_quiz': [{
            'id': r.id,
            'pontuacao': r.pontuacao,
            'total_perguntas': r.total_perguntas,
            'data_realizacao': r.data_realizacao.strftime('%Y-%m-%d %H:%M:%S')
        } for r in resultados]
    }
    
    return jsonify(dados)

@app.route('/admin/relatorio')
def admin_relatorio():
    relatorio = []
    usuarios = Usuario.db.session.query(Usuario).all() if hasattr(Usuario, 'db') else Usuario.query.all()
    for u in usuarios:
        pegada = (
            PegadaCarbono.query
            .filter_by(usuario_id=u.id)
            .order_by(PegadaCarbono.data_calculo.desc(), PegadaCarbono.id.desc())
            .first()
        )
        quiz = (
            ResultadoQuiz.query
            .filter_by(usuario_id=u.id)
            .order_by(ResultadoQuiz.data_realizacao.desc(), ResultadoQuiz.id.desc())
            .first()
        )
        relatorio.append({
            'id': u.id,
            'nome': u.nome,
            'email': u.email,
            'pegada_total_co2': round(pegada.total_co2, 2) if pegada else None,
            'quiz_pontuacao': quiz.pontuacao if quiz else None,
            'quiz_total_perguntas': quiz.total_perguntas if quiz else None
        })
    return jsonify(relatorio)

@app.route('/admin/relatorio.csv')
def admin_relatorio_csv():
    rows = []
    usuarios = Usuario.query.all()
    for u in usuarios:
        pegada = (
            PegadaCarbono.query
            .filter_by(usuario_id=u.id)
            .order_by(PegadaCarbono.data_calculo.desc(), PegadaCarbono.id.desc())
            .first()
        )
        quiz = (
            ResultadoQuiz.query
            .filter_by(usuario_id=u.id)
            .order_by(ResultadoQuiz.data_realizacao.desc(), ResultadoQuiz.id.desc())
            .first()
        )
        rows.append({
            'id': u.id,
            'nome': u.nome,
            'email': u.email,
            'pegada_total_co2': round(pegada.total_co2, 2) if pegada else '',
            'quiz_pontuacao': quiz.pontuacao if quiz else '',
            'quiz_total_perguntas': quiz.total_perguntas if quiz else ''
        })

    output = io.StringIO()
    fieldnames = ['id', 'nome', 'email', 'pegada_total_co2', 'quiz_pontuacao', 'quiz_total_perguntas']
    writer = csv.DictWriter(output, fieldnames=fieldnames, delimiter=';')
    writer.writeheader()
    for r in rows:
        writer.writerow(r)

    csv_data = output.getvalue()
    output.close()

    from flask import Response
    return Response(
        csv_data,
        mimetype='text/csv; charset=utf-8',
        headers={
            'Content-Disposition': 'attachment; filename="relatorio_verdetech.csv"'
        }
    )

if __name__ == '__main__':
    app.run(debug=True)