from functools import wraps
import os
from flask import Flask, request, g, session, \
     redirect, url_for, send_from_directory 

app = Flask(__name__)


from raven.contrib.flask import Sentry
sentry = Sentry(app, dsn='https://c51e9f1ac5fd4dfc8c3f3bea6cd99099:5bda923b137e4f5eb928da4fb9a11579@app.getsentry.com/310')


@app.before_request
def before_request():
    g.user = None
    if 'openid' in session:
        pass

def check_auth():
    if 'DOMAIN' in os.environ:
        if 'openid' in session:
            return True
        return False
    else:
        return True
        
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not check_auth():
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated


@app.route('/')
@requires_auth
def index():
    f = open("templates/index.html")
    return "".join(f.readlines())
    
@app.route('/<path:filename>')
@requires_auth
def stuff(filename):
    if filename.endswith("/"):
        f = open("templates/"+filename+"index.html")
        return "".join(f.readlines())
    if filename.find(".") == -1:
        f = open("templates/"+filename+".html")
        return "".join(f.readlines())
    elif filename.find(".html") != -1:
        f = open("templates/"+filename)
        return "".join(f.readlines()) 
    return send_from_directory('templates', filename)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    if 'DEBUG' in os.environ:
        if os.environ['DEBUG'] == 'True':
            DEBUG=True
        else:
            DEBUG=False
    else:
        DEBUG = False
    app.run(debug=DEBUG, host='0.0.0.0', port=port)
