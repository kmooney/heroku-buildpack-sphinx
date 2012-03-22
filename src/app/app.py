from functools import wraps
import os
from flask import Flask, request, g, session, \
     redirect, url_for, send_from_directory 

from flaskext.openid import OpenID

app = Flask(__name__)
app.secret_key = '\xa5\x10\xbfN3\x1f\t\xd0ec\xa1\xe8\xe7B\x1dU4!\xa1N@\xcf\xfe\xa2'

oid = OpenID(app)

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

@oid.after_login
def create_or_login(resp):
    """This is called when login with OpenID succeeded and it's not
    necessary to figure out if this is the users's first login or not.
    This function has to redirect otherwise the user will be presented
    with a terrible URL which we certainly don't want.
    """
    session['openid'] = resp.identity_url
    return redirect(oid.get_next_url())


@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    domain = os.environ['DOMAIN']
    return oid.try_login("https://www.google.com/accounts/o8/site-xrds?hd=%s" % domain )

@app.route('/logout')
def logout():
    session.pop('openid', None)
    return redirect(oid.get_next_url())

@app.route('/')
@requires_auth
def index():
    f = open("index.html")
    return "".join(f.readlines())
    
@app.route('/<path:filename>')
@requires_auth
def stuff(filename):
    if filename.endswith("/"):
        f = open(filename+"index.html")
        return "".join(f.readlines())
    if filename.find(".") == -1:
        f = open(filename+".html")
        return "".join(f.readlines())
    elif filename.find(".html") != -1:
        f = open(filename)
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
