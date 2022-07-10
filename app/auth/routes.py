import uuid
#from crypt import methods
from webbrowser import get
import requests
from flask import Flask, render_template, session, request, redirect, url_for
from flask_session import Session  # https://pythonhosted.org/Flask-Session
#from werkzeug.middleware.proxy_fix import ProxyFix
import msal

#import app
#import app_config

"""app = Flask(__name__)
app.config.from_object(app_config)
"""
#Session(app)


#from app import app_config
from . import auth_bp, AAD_config
#auth_bp.config.from_object(AAD_config)
#Session(app)
# This section is needed for url_for("foo", _external=True) to automatically
# generate http scheme when this sample is running on localhost,
# and to generate https scheme when it is deployed behind reversed proxy.
# See also https://flask.palletsprojects.com/en/1.0.x/deploying/wsgi-standalone/#proxy-setups





@auth_bp.route("/")
def index():
    if not session.get("user"):
        return redirect(url_for("auth.login"))
    token = _get_token_from_cache(AAD_config.SCOPE)
    if not token:
        return redirect(url_for("auth.login"))
    graph_data = requests.get(  # Use token to call downstream service
        AAD_config.ENDPOINT,
        headers={'Authorization': 'Bearer ' + token['access_token']},
    ).json()

    if graph_data.get('jobTitle') == "ESTUDIANTE":
        return render_template('estudiante/estudiante.html', user=session["user"], version=msal.__version__, result=graph_data)
    else:
        return render_template('test.html', user=session["user"], version=msal.__version__)


@auth_bp.route("/login")
def login():
    # Technically we could use empty list [] as scopes to do just sign in,
    # here we choose to also collect end user consent upfront
    session["flow"] = _build_auth_code_flow(scopes=AAD_config.SCOPE)
    return render_template("login.html", auth_url=session["flow"]["auth_uri"], version=msal.__version__)


# Its absolute URL must match your app's redirect_uri set in AAD
@auth_bp.route(AAD_config.REDIRECT_PATH)
def authorized():
    try:
        cache = _load_cache()
        result = _build_msal_app(cache=cache).acquire_token_by_auth_code_flow(
            session.get("flow", {}), request.args)
        if "error" in result:
            return render_template("auth_error.html", result=result)
        session["user"] = result.get("id_token_claims")
        _save_cache(cache)
    except ValueError:  # Usually caused by CSRF
        pass  # Simply ignore them
    return redirect(url_for('estudiante.estudiante'))


@auth_bp.route("/logout")
def logout():
    session.clear()  # Wipe out user and its token cache from session
    return redirect(  # Also logout from your tenant's web session
        AAD_config.AUTHORITY + "/oauth2/v2.0/logout" +
        "?post_logout_redirect_uri=" + url_for("auth.login", _external=True))


"""@app.route("/graphcall")
def graphcall():
    token = _get_token_from_cache(AAD_config.SCOPE)
    if not token:
        return redirect(url_for("login"))
    graph_data = requests.get(  # Use token to call downstream service
        AAD_config.ENDPOINT,
        headers={'Authorization': 'Bearer ' + token['access_token']},
    ).json()
    return render_template('display.html', result=graph_data)
"""

def _load_cache():
    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])
    return cache


def _save_cache(cache):
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()


def _build_msal_app(cache=None, authority=None):
    return msal.ConfidentialClientApplication(
        AAD_config.CLIENT_ID, authority=authority or AAD_config.AUTHORITY,
        client_credential=AAD_config.CLIENT_SECRET, token_cache=cache)


def _build_auth_code_flow(authority=None, scopes=None):
    return _build_msal_app(authority=authority).initiate_auth_code_flow(
        scopes or [],
        redirect_uri=url_for("auth.authorized", _external=True))


def _get_token_from_cache(scope=None):
    cache = _load_cache()  # This web app maintains one cache per session
    cca = _build_msal_app(cache=cache)
    accounts = cca.get_accounts()
    if accounts:  # So all account(s) belong to the current signed-in user
        result = cca.acquire_token_silent(scope, account=accounts[0])
        _save_cache(cache)
        return result


#app.jinja_env.globals.update(
 #   _build_auth_code_flow=_build_auth_code_flow)  # Used in template



