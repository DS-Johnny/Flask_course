from flask import Flask, jsonify, request # flask = lib / Flask = classe


app = Flask(__name__) # app = instância da classe Flask / __name__ faz referencia ao módulo "app.py" que é o arquivo atual
# -----------------------------------------------------------------------------------------------------------------------
@app.route('/<name>' )# decorador para as rotas URL
def name(name):    # Função para a página
    return '<h1>Hello {}.</h1>'.format(name)

# -----------------------------------------------------------------------------------------------------------------------
@app.route('/')
def index():
    return '<h1>Hello, world!</h1>'

# -----------------------------------------------------------------------------------------------------------------------
@app.route('/home', methods=['POST', 'GET'], defaults={'name':'default'})
@app.route('/home/<name>', methods=['POST', 'GET'])
def home(name):
    return '<h1>Hello, {}. You are on the home page!!</h1>'.format(name)

# -----------------------------------------------------------------------------------------------------------------------
@app.route('/query')
def query():
    name = request.args.get('name')
    location = request.args.get('location')
    return '<h1>Hi {}, you are from {}. You are on the query page</h1>'.format(name, location)

# -----------------------------------------------------------------------------------------------------------------------
@app.route('/json')
def json():
    return jsonify({'key' : 'value', 'key2' : [1,2,3]})


# -----------------------------------------------------------------------------------------------------------------------
@app.route('/theform')
def theform():
    return '''<form method="POST" action="/process">
                <input type="text" name="name">
                <input type="text" name="location">
                <input type="submit" value="Submit">
                </form>'''
@app.route('/process', methods=['POST'])
def process():
    name = request.form['name']
    location = request.form['location']

    return '<h1>Hello {}, you are from {}. Form submitted successfully!</h1>'.format(name, location)

# -----------------------------------------------------------------------------------------------------------------------
@app.route('/processjson', methods=['POST'])
def processjson():
    
    data = request.get_json( ) # converte os dados json para estrutura de dados python
    name = data['name']
    location = data['location']
    randomlist = data['randomlist']
    return jsonify({'result' : 'Success!', 'name' : name, 'location' : location, 'randomlist' : randomlist[1]})


if __name__ == '__main__':
    app.run(debug=True)
