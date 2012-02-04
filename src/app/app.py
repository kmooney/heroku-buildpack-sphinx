from functools import wraps
import os
from flask import Flask, render_template, request, g, session, \
     redirect, url_for, send_from_directory 

from flaskext.openid import OpenID

app = Flask(__name__)
app.secret_key = '\xa5\x10\xbfN3\x1f\t\xd0ec\xa1\xe8\xe7B\x1dU4!\xa1N@\xcf\xfe\xa2'

oid = OpenID(app)

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
    return render_template("index.html")
    
@app.route('/<path:filename>')
@requires_auth
def stuff(filename):
    if filename.endswith("/"):
        return render_template(filename + "index.html")        
    if filename.find(".") == -1:
        return render_template(filename + ".html")
    elif filename.find(".html") != -1:
        return render_template(filename)
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
