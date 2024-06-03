from flask import Flask, jsonify, request, url_for, redirect, session, render_template, g
import sqlite3


app = Flask(__name__) # app = instância da classe Flask / __name__ faz referencia ao módulo "app.py" que é o arquivo atual
app.config['Debug'] = True
app.config['SECRET_KEY'] = 'Thisisasecret!'

# -------------------------------------------------- DATABASE HELPER FUNCTIONS
def connect_db():
    """
    Estabelece uma conexão com o banco de dados SQLite.
    Configura a fábrica de linhas para retornar dicionários ao invés de tuplas.
    """
    sql = sqlite3.connect('data.db')
    sql.row_factory = sqlite3.Row  # Retorna as linhas como dicionários ao invés de tuplas
    return sql

def get_db():
    """
    Obtém a conexão com o banco de dados armazenada em g.
    Se não existir, cria uma nova conexão e a armazena em g.
    """
    if not hasattr(g, 'sqlite_db'):  # Verifica se 'sqlite_db' não existe em 'g'
        g.sqlite_db = connect_db()  # Conecta ao banco de dados e armazena a conexão em 'g'
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """
    Fecha a conexão com o banco de dados armazenada em g, se existir.
    Esta função é chamada automaticamente ao final de cada requisição.
    """
    if hasattr(g, 'sqlite_db'):  # Verifica se 'sqlite_db' existe em 'g'
        g.sqlite_db.close()  # Fecha a conexão com o banco de dados


# ----------------------------------------------- MANAGING DB
@app.route('/viewresults')
def viewresults():
    db = get_db()
    cur = db.execute('SELECT id, name, location FROM users')
    results = cur.fetchall()

    return 'The id is: {}. The name is: {}. The locaion is: {}.'.format(results[0]['id'], results[0]['name'], results[0]['location'])

@app.route('/welcome')
def welcome():
    name = session['name'] 
    return render_template('welcome.html', name=name, mylist=[1,2,3], 
                           dictionaryList=[{'name' : 'Zoe'},{'name' : 'Gary'}])

# ------------------------------------------------INDEX BASIC-----------------------------------------------------------------------
@app.route('/')
def index():
    session.pop('name', None)
    db = get_db()
    cur = db.execute('SELECT * FROM users')
    results = cur.fetchall()
    list_result = []
    for linha in results:
        lin = {}
        lin['id'] = linha['id']
        lin['name'] = linha['name']
        lin['location'] = linha['location']
        list_result.append(lin)

    return 'Resultado: {}'.format(list_result)



# -----------------------------------------------------------PLACEHOLDER VARIABLE AND DEFAULTS------------------------------------------------------------


@app.route('/home', methods=['POST', 'GET'], defaults={'name':'default'})
@app.route('/home/<name>', methods=['POST', 'GET'])
def home(name):
    session['name'] = name
    return '<h1>Hello, {}. You are on the home page!!</h1>'.format(name)



# ----------------------------------------------------QUERY STRIG URL-------------------------------------------------------------------
@app.route('/query')
def query():
    name = request.args.get('name')
    location = request.args.get('location')
    return '<h1>Hi {}, you are from {}. You are on the query page</h1>'.format(name, location)


# ----------------------------------------------------JSON-------------------------------------------------------------------
@app.route('/json')
def json():
    name = session['name']
    return jsonify({'key' : 'value', 'key2' : [1,2,3], 'name' : name})

@app.route('/processjson', methods=['POST'])
def processjson():
    
    data = request.get_json( ) # converte os dados json para estrutura de dados python
    name = data['name']
    location = data['location']
    randomlist = data['randomlist']
    return jsonify({'result' : 'Success!', 'name' : name, 'location' : location, 'randomlist' : randomlist[1]})



# --------------------------------------------------------------FORM---------------------------------------------------------
@app.route('/theform', methods=['POST', 'GET'])
def theform():
    if request.method == 'GET':
        return '''<form method="POST" action="/theform">
                    <input type="text" name="name">
                    <input type="text" name="location">
                    <input type="submit" value="Submit">
                    </form>'''
    else:
        name = request.form['name']
        location = request.form['location']

        

        #return '<h1>Hello {}, you are from {}. Form submitted successfully!</h1>'.format(name, location)
        return redirect(url_for('home', name=name))


# -------------------------------------------------------------RENDER_TEMPLATE----------------------------------------------------
@app.route('/form', methods=['POST', 'GET'])
def form():
    if request.method == 'GET':
        return render_template('form.html')
    
    else:
        name = request.form['name']
        location = request.form['location']
        db = get_db()
        db.execute('INSERT INTO users (name, location) VALUES (?,?)', [name, location])
        db.commit()

        return '<h1>Hello {}, you are from {}. Form submitted successfully!</h1>'.format(name, location)





if __name__ == '__main__':
    app.run(debug=True)
