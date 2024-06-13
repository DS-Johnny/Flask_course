from flask import Flask, g, request, jsonify
from database import get_db
from functools import wraps

app = Flask(__name__)



api_username = 'admin'
api_password = 'password'

def protected(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if auth and auth.username == api_username and auth.password == api_password:
            return f(*args, **kwargs)
        else:
            return jsonify({'message' : 'Authentication Failed!'}), 403
    return decorated

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
@protected
def get_members():
    db = get_db()
    members_cur = db.execute('select * from members')
    members = members_cur.fetchall()
    
    #members_dic = [id, name, email, level in members]
    member_list = []
    for row in members:
        dic = {}
        dic['id'] = row['id']
        dic['name'] = row['name']
        dic['email'] = row['email']
        dic['level'] = row['level']
        member_list.append(dic)

    return jsonify({'members': member_list})
    
@app.route('/member/<int:member_id>', methods=['GET'])
@protected
def get_member(member_id):
    db = get_db()
    member_cur = db.execute('select * from members where id = ?', [member_id])
    member = member_cur.fetchone()

    return jsonify({'member':{'id' : member['id'], 'name' : member['name'], 'email' : member['email'], 'level' : member['level']}})

@app.route('/member', methods=['POST'])
@protected
def add_member():
    new_member_data = request.get_json()
    name = new_member_data['name']
    email = new_member_data['email']
    level = new_member_data['level']
    
    db = get_db()
    
    db.execute('insert into members (name, email, level) values (?,?,?)',   [name,email,level])
    db.commit()
    
    member_cur = db.execute('select * from members where name = ?', [name])
    new_member = member_cur.fetchone()

    return jsonify({'member':{'id' : new_member['id'], 'name' : new_member['name'], 'email' : new_member['email'], 'level' : new_member['level']}})

@app.route('/member/<int:member_id>', methods=['PUT', 'PATCH'])
@protected
def edit_member(member_id):
    new_member_data = request.get_json()
    name = new_member_data['name']
    email = new_member_data['email']
    level = new_member_data['level']
    

    db = get_db()
    db.execute('update members set name = ?, email = ?, level = ? where id = ?', [name, email, level, member_id])
    db.commit()


    return 'This updates a member by ID.'

@app.route('/member/<int:member_id>', methods=['DELETE'])
@protected
def delete_member(member_id):
    
    db = get_db()
    db.execute('delete from members where id = ?', [member_id])
    db.commit()


    return 'This removes a member by ID.'



if __name__ == '__main__':
    app.run(debug=True)
