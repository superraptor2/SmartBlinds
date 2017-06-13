from flask import Flask
import os
from flask import render_template, redirect, url_for, request, session, flash, g
from functools import wraps
from DbClass import DbClass

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
    # error = None
    # if request.method == 'POST':
    #     if request.form['username'] !='admin' or request.form['password'] != 'admin':
    #         error = ' invalid credentials, Please try again.'
    #     else:
    #         session['logged_in'] = True
    #         flash('You were just logged in!')
    #         return redirect(url_for('index'))
    # return render_template('login.html', error=error)

    error = None
    if request.method == "POST":
        db = DbClass()
        user_credentials = db.getUser(request.form['username'])
        if user_credentials: #Als de lijst NIET leeg is dan...
            if (user_credentials[1]) != request.form['password']:
                error = ' Wrong password. Please try again.'
            else:
                session['logged_in'] = True
                flash('You were just logged in!')
                session['username'] = user_credentials[0]
                return redirect(url_for("index"))
        else:
            error = ' User does not excist. Please try again.'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were just logged out!')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    #g.db = DbClass()
    #cur = g.db.execute('select * from posts')
    #posts = [dict(title=row[0], description=row[1]) for row in cur.fetchall()]
    #g.db.close()
    return render_template('index.html') #, posts=posts)

@app.route('/devices')
@login_required
def devices():
    db = DbClass()
    devicelijst = db.getDevices()
    return render_template('devices.html', devicelijst=devicelijst)

@app.route('/devicedetail/<deviceid>')
@login_required
def devicedetail(deviceid):
    db = DbClass()
    devicedetail = db.getDevice(deviceid)
    return render_template('devicedetail.html' , devicedetail=devicedetail)

@app.route('/logs')
@login_required
def logs():
    db_layer = DbClass()
    list_logs = db_layer.getLogs()
    return render_template('logs.html', list_logs=list_logs)

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