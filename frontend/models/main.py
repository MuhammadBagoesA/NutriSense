from flask import Flask

app = Flask(__name__)

@app.route('/')

def hello():
    return '<h1>Hello World!</h1>'

@app.route('/about')
def about():
    return '<h1>About Page</h1>'

@app.route('/contact')
def contact():
    return '<h1>Contact Page</h1>'

@app.route('/profile', defaults={'username': 'Surya ayu rahma'})
@app.route('/profile/<string:username>')
def profile_username(username):
    return f'<h1>Profile Page of {username}</h1>'

app.run(debug=True)