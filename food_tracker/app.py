from flask import Flask, render_template


app = Flask(__name__)




@app.route('/')
def index():
    return "Hello, world!"

@app.route('/view')
def view():
    return None

@app.route('/food')
def food():
    return None

if __name__ == '__main__':
    app.run(debug=True)