from flask import Flask, g
from database import get_db

app = Flask(__name__)

# --------------------- Database helpers -----------------------------
@app.teardown_appcontext
def close_db(error):
    """
    Fecha a conexão com o banco de dados armazenada em g, se existir.
    Esta função é chamada automaticamente ao final de cada requisição.
    """
    if hasattr(g, 'sqlite_db'):  # Verifica se 'sqlite_db' existe em 'g'
        g.sqlite_db.close()  # Fecha a conexão com o banco de dados




@app.route('/member', methods=['GET'])
def get_members():
    return 'this returns all the members'

@app.route('/member/<int:member_id>', methods=['GET'])
def get_member(member_id):
    return 'this returns one member by ID'

@app.route('/member', methods=['POST'])
def add_member():
    return 'This adds a new member.'

@app.route('/member/<int:member_id>', methods=['PUT', 'PATCH'])
def edit_member(member_id):
    return 'This updates a member by ID.'

@app.route('/member/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    return 'This removes a member by ID.'



if __name__ == '__main__':
    app.run(debug=True)
