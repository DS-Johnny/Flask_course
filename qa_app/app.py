from flask import Flask, render_template, g, request, session, redirect, url_for
from database import get_db
from werkzeug.security import generate_password_hash, check_password_hash
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24) # Gera uma SECRET_KEY aleatória para a sessão

@app.teardown_appcontext
def close_db(error):
    """
    Fecha a conexão com o banco de dados armazenada em g, se existir.
    Esta função é chamada automaticamente ao final de cada requisição.
    """
    if hasattr(g, 'sqlite_db'):  # Verifica se 'sqlite_db' existe em 'g'
        g.sqlite_db.close()  # Fecha a conexão com o banco de dados

def get_current_user():
    """
    Função para retornar as informações do usuário atual. É utilizada em cada route.
    Quando um usuário faz login, seu nome de usuário fica salvo na session.
    Essa função verifica se há algum usuário na session, e busca suas informações no BD pelo nome.
    Retorna uma linha do banco de dados em formato de dicionário.
    """
    user_result = None
    if 'user' in session: 
        user = session['user']
        db = get_db()
        user_cur = db.execute('select * from users where name = ?', [user])
        user_result = user_cur.fetchone()

    return user_result

# HOMEPAGE - Contém acessos para funcionalidades do app e exibe uma lista com as perguntas já respondidas
@app.route('/')
def index():
    user = get_current_user() # Obtém as informações do usuário na session, os links do template variam de acordo com o tipo de usuário
    db = get_db()
    # Query para obter apenas as perguntas já respondidas, nome do usuário que perguntou, e especialista que respondeu
    question_cur = db.execute('''select 
                                    questions.id as question_id, 
                                    questions.question_text, 
                                    askers.name as asker_name, 
                                    experts.name as expert_name 
                                from questions join users as askers on askers.id = questions. asked_by_id 
                                                join users as experts on experts.id = questions.expert_id 
                                where questions.answer_text is not null''')
    question_results = question_cur.fetchall()

    return render_template('home.html', user=user, questions=question_results) # Envia os dados do usuário e perguntas respondidas para o template

# REGISTER - Local para o usuário se cadastrar, apenas nome e senha. Todo usuário cadastrado aqui não é admin e nem expert
# Um admin deve ser definido manualmente no BD e após isso ele pode promover um usário comum a expert diretamente na aplicação
@app.route('/register', methods=['GET', 'POST'])
def register():
    user = get_current_user()
    if request.method == 'POST':
        db = get_db()

        #Verifica se o nome de usuário digitado pelo usuário já existe no BD
        name = request.form['name']
        existing_user_cur = db.execute('select id from users where name = ?', [name])
        existing_user = existing_user_cur.fetchone()

        if existing_user: # Se o nome já existir, exibe uma mensagem de erro e recarrega a página
            return render_template('register.html', user=user, error='User already exists!')
        
        # Gera um HASH para a senha digitada pelo usuário e atribui à variável HASH 
        hashed_password = generate_password_hash(request.form['password'])
        expert = 0 # EXPERT = False
        admin = 0 # ADMIN = False
        #Cadastra as informações no banco de dados
        db.execute('insert into users (name, password, expert, admin) values (?, ?, ?, ?)', [name, hashed_password, expert, admin])
        db.commit()

        # Inicia a session e redireciona o usuário recém criado para a homepage
        session['user'] = name

        return redirect(url_for('index'))

    return render_template('register.html', user=user)

# LOGIN
@app.route('/login', methods=['GET', 'POST']) # adm cadastrado : (USER: 'admin', PASSWORD: 'adminpass')
def login():
    user = get_current_user()
    error = None # Váriavel para enviar a mensagem de erro para o template, caso usuário ou senha estejam incorretos
    if request.method == 'POST':
        db = get_db()

        # Dados digitados pelo usuário
        name = request.form['name']
        password = request.form['password']
        
        # Faz a busca pelo nome do usuário
        user_cur = db.execute('select id, name, password from users where name = ?', [name])
        user_result = user_cur.fetchone()

        # Se o usuário existir, confere as senhas, caso contrário recarrega a página com mensagem de erro
        if user_result:
            # Confere se o hash da senha digitada bate com o hash da senha no banco de dados
            if check_password_hash(user_result['password'], password):
                session['user'] = user_result['name'] # Inicia a session no login
                return redirect(url_for('index')) # Redireciona para a HOME
            else: # Se a senha não confere, exibe mensagem de erro
                error = 'The password is incorrect'
                return render_template('login.html', user=user, error=error)
            
        error = 'The username is incorrect'        

    return render_template('login.html', user=user, error=error)

# QUESTION - o único acesso a esta página é através da lista de perguntas respondidas na HOME, qualquer pessoa pode ter acesso à esta página, esteja logado ou não
@app.route('/question/<question_id>') # a route necessita do id da pergunta, quando clicada na HOME
def question(question_id):
    user = get_current_user()
    db = get_db()
    # Query das informações da pergunta selecionada pelo id 
    question_cur = db.execute('''
                                select 
                                    questions.id as question_id,
                                    questions.answer_text, 
                                    questions.question_text, 
                                    askers.name as asker_name, 
                                    experts.name as expert_name 
                                from questions join users as askers on askers.id = questions. asked_by_id 
                                                join users as experts on experts.id = questions.expert_id 
                                where question_id = ?''', [question_id])

    question = question_cur.fetchone()

    return render_template('question.html', user=user, question=question)

# ANSWER - Exibe uma pergunta e espaço para inserir resposta. O único tipo de usuário que tem acesso à essa página é o expert
@app.route('/answer/<question_id>', methods=['GET', 'POST']) # A única maneira de acessar essa página é através da página de perguntas não respondidas, após uma pergunta for clicada
def answer(question_id):
    user = get_current_user()
    # Se não houver usuário logado, redireciona para a página de login
    if not user:
        return redirect(url_for('login'))
    
    # Se o usuário logado foi um usuário comum, redireciona para home
    if user['expert'] == 0:
        return redirect(url_for('index'))

    db = get_db()

    if request.method == 'POST':
        answer = request.form['answer'] # Resposta digitada no form
        db.execute('update questions set answer_text = ? where id = ?', [answer, question_id]) # atualiza a pergunta no BD com a resposta
        db.commit()

        return redirect(url_for('unanswered'))

    question_cur = db.execute('select id, question_text from questions where id = ?', [question_id])
    question = question_cur.fetchone()

    return render_template('answer.html', user=user, question=question)

# ASK - Página para cadastrar uma pergunta direcionada à um expert, somente um usuário comum tem acesso à essa página
@app.route('/ask', methods=['POST', 'GET'])
def ask():
    user = get_current_user()
    # Se não houver usuário na session redireciona para login
    if not user:
        return redirect(url_for('login'))

    db = get_db()

    if request.method == 'POST':
        question = request.form['question']
        expert = request.form['expert'] # expert escolhido a partir de um dropdown list
        db.execute('insert into questions (question_text, asked_by_id, expert_id) values (?, ?, ?)',[question, user['id'], expert])
        db.commit()
        return redirect(url_for('index'))
        
    # QUERY para obter o id e nome dos experts cadastrados
    expert_cur = db.execute('select id, name from users where expert = 1')
    expert_results = expert_cur.fetchall()


    return render_template('ask.html', user=user, experts=expert_results)

# UNANSWERED - Página com listas de perguntas não respondidas, somente o expert tem acesso
@app.route('/unanswered')
def unanswered():
    user = get_current_user()
    # Se não houver usuário na session, redireciona para login
    if not user:
        return redirect(url_for('login'))
    
    # Se o usuário na session for um usuário comum, redireciona para home
    if user['expert'] == 0:
        return redirect(url_for('index'))

    db = get_db()
    # Query para obter as perguntas não respondidas relacionadas ao usuário expert que estiver online
    questions_cur = db.execute('''  select 
                                        questions.id, 
                                        questions.question_text, 
                                        users.name 
                                    from questions join users on users.id = questions.asked_by_id 
                                    where questions.answer_text is null and questions.expert_id = ?''', [user['id']])
    question_results = questions_cur.fetchall()

    return render_template('unanswered.html', user=user, questions=question_results)

# USERS - Página para promover um usário comum para expert, apenas o ADMIN tem acesso
# Ela apenas exibe uma lista dos usuários
@app.route('/users')
def users ():
    user = get_current_user()
    # Se não houver usuário na session, redireciona para login
    if not user:
        return redirect(url_for('login'))

    # Se o usuário na session não for admin, redireciona para home
    if user['admin'] == 0:
        return redirect(url_for('index'))
    
    db = get_db()
    # Query que seleciona tudo de todos os usuários

    users_cur = db.execute('select * from users')
    user_results = users_cur.fetchall()

    return render_template('users.html', user=user, users=user_results)

#PROMOTE - Não tem template, é uma ação da página USERS. Atualiza o tipo de um usuário 
@app.route('/promote/<user_id>') # Depende de um id de usuário
def promote(user_id):
    user = get_current_user()
    # Se não houver usuário na session, redireciona para login
    if not user:
        return redirect(url_for('login'))
    # Se o usuário na session não for admin, redireciona para home
    if user['admin'] == 0:
        return redirect(url_for('index'))
    
    db = get_db()
    db.execute('update users set expert = 1 where id = ?', [user_id])
    db.commit()
    return redirect(url_for('users'))

# Rota para deslogar o usuário, apenas remove o user da session
@app.route('/logout')
def logout():

    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)