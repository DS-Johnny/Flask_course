from flask import Flask, render_template, request, g
from datetime import datetime
from database import get_db, connect_db


app = Flask(__name__)

# -------------------------------------------------- DATABASE HELPER FUNCTIONS
@app.teardown_appcontext
def close_db(error):
    """
    Fecha a conexão com o banco de dados armazenada em g, se existir.
    Esta função é chamada automaticamente ao final de cada requisição.
    """
    if hasattr(g, 'sqlite_db'):  # Verifica se 'sqlite_db' existe em 'g'
        g.sqlite_db.close()  # Fecha a conexão com o banco de dados



@app.route('/', methods=['POST', 'GET'])
def index():
    db = get_db()

    if request.method == 'POST':
        date = request.form['date']

        dt = datetime.strptime(date, '%Y-%m-%d')
        database_date = datetime.strftime(dt, '%Y%m%d')    

        db.execute('INSERT INTO log_date (entry_date) VALUES (?)', [database_date])
        db.commit()

    cur = db.execute('select log_date.entry_date, sum(food.protein) as protein, sum(food.carbohydrates) as carbohydrates, sum(food.fat) as fat, sum(food.calories) as calories from log_date join food_date on food_date.log_date_id = log_date.id join food on food.id = food_date.food_id group by log_date.id order by log_date.entry_date desc')
    results = cur.fetchall()

    date_results = []
    for i in results:
        single_date = {}

        single_date['entry_date'] = i['entry_date']
        single_date['protein'] = i['protein']
        single_date['carbohydrates'] = i['carbohydrates']
        single_date['fat'] = i['fat']
        single_date['calories'] = i['calories']

        d = datetime.strptime(str(i['entry_date']), '%Y%m%d')
        single_date['pretty_date'] = datetime.strftime(d, '%B %d, %Y')
        date_results.append(single_date)

    return render_template('home.html', results=date_results)

@app.route('/view/<date>', methods=['GET', 'POST'])
def view(date):
    db = get_db()
    cur = db.execute('SELECT * FROM log_date WHERE entry_date = ?', [date])
    date_result = cur.fetchone()

    if request.method == 'POST':
        db.execute('INSERT INTO food_date (food_id, log_date_id) VALUES (?,?)', [request.form['food-select'], date_result['id']])
        db.commit()
    
    d = datetime.strptime(str(date_result['entry_date']), '%Y%m%d')
    pretty_date = datetime.strftime(d, '%B %d, %Y')

    food_cur = db.execute('SELECT id, name FROM food')
    food_results = food_cur.fetchall()

    log_cur = db.execute('''SELECT food.name, food.protein, food.carbohydrates, food.fat, food.calories
                            FROM log_date JOIN food_date ON food_date.log_date_id = log_date.id 
                                        JOIN food ON food.id = food_date.food_id
                            WHERE log_date.entry_date = ?''', [date])
    log_results = log_cur.fetchall()

    totals = {}
    totals['protein'] = 0
    totals['carbohydrates'] = 0
    totals['fat'] = 0
    totals['calories'] = 0

    for food in log_results:
        totals['protein'] += food['protein']
        totals['carbohydrates'] += food['carbohydrates']
        totals['fat'] += food['fat']
        totals['calories'] += food['calories']


    return render_template('day.html', entry_date=date_result['entry_date'], pretty_date=pretty_date, food_results=food_results, log_results=log_results, totals=totals)

@app.route('/food', methods=['POST', 'GET'])
def food():
    db = get_db()

    if request.method == 'POST':
        name = request.form['food-name']    
        protein = int(request.form['protein'])
        carbs = int(request.form['carbohydrates'])
        fat = int(request.form['fat'])        
        calories = protein * 4 + carbs * 4 + fat * 9

        db = get_db()
        db.execute('INSERT INTO food (name, protein, carbohydrates, fat, calories) VALUES(?,?,?,?,?)', [name, protein, carbs, fat, calories])
        db.commit()
    
    cur = db.execute('SELECT * FROM food')
    results = cur.fetchall()

    return render_template('add_food.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)