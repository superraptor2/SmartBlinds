from flask import Flask
import os
from flask import render_template, redirect, url_for, request, session, flash
from functools import wraps

#create the application object
app = Flask(__name__)

#config
app.secret_key = "my precious"

#login required decorator
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap

# use decorators to link the function to a url
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] !='admin' or request.form['password'] != 'admin':
            error = ' invalid credentials, Please try again.'
        else:
            session['logged_in'] = True
            flash('You were just logged in!')
            return redirect(url_for('index'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were just logged out!')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/scenes')
@login_required
def scenes():
    return render_template('scenes.html')

@app.route('/logs')
@login_required
def logs():
    return render_template('logs.html')

@app.route('/about')
@login_required
def about():
    return render_template('about.html')

@app.route('/contact')
@login_required
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT",5000))
    app.run(host='0.0.0.0', port=5000, debug=True)