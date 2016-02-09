"""The Main module central processing.

Attributes
----------
main : blueprint
    The blueprint with all registered routes.
"""
from flask import Blueprint
from flask import render_template
from flask import session
from flask import redirect
from flask import url_for
from flask import abort
from flask import g

from src import users_only
from src import guests_only

main = Blueprint('main', __name__, template_folder='./templates',
                 static_folder='./static', static_url_path='/public')


@main.route('/')
@guests_only
def index():
    """Serve the Index page.
       Load the 'headlines_widget' widget data.

    Returns
    -------
    render_template : str
        The template output.
    """
    g.lcursor.execute('SELECT * FROM articles ORDER BY id DESC LIMIT 3')
    return render_template('main_index.html',
                           articles_data=g.lcursor.fetchall())


@main.route('/user/signup')
@guests_only
def registration():
    """Serve the Signup page.

    Returns
    -------
    render_template : str
        The template output.
    """
    return render_template('main_signup.html')


@main.route('/home')
@users_only
def homepage():
    """Serve the homepage.
       Load the 'headlines_widget' widget data.

    Returns
    -------
    render_template : str
        The template output.
    """
    g.lcursor.execute("SELECT * FROM articles ORDER BY id DESC LIMIT 8")
    return render_template('main_home.html',
                           articles_data=g.lcursor.fetchall())


@main.route('/welcome')
@users_only
def welcome():
    """Serve the welcoming page.

    Returns
    -------
    render_template : str
        The template output.
    """
    return render_template('main_welcome.html')


@main.route('/maintenance')
def maintenance():
    """Serve the maintenance page.

    Returns
    -------
    render_template : str
        The template output.
    """
    return render_template('main_maintenance.html')


@main.route('/game')
def client():
    """Serve the client page.
       Update the users 'auth_ticket' to prevent hijacking.

    Returns
    -------
    render_template : str
        The template output.
    """
    return render_template('main_client.html')


@main.route('/article/<slug>')
@users_only
def article(slug):
    """Serve an article.

    Parameters
    ----------
    slug : str
        Article slug.

    Returns
    -------
    render_template : str
        The template output.
    """
    g.lcursor.execute('SELECT * FROM articles WHERE slug = ?', (slug,))
    article = g.lcursor.fetchone()
    if article:
        g.lcursor.execute(
            'SELECT title, slug FROM articles ORDER BY id DESC LIMIT 5')
        articles = g.lcursor.fetchall()
    else:
        return abort(404)
    return render_template('main_article.html', article=article,
                           articles=articles)


@main.route('/logout')
@users_only
def logout():
    """Remove login status and redirect.

    Returns
    -------
    redirect : redirection
        Redirect back to index.
    """
    if 'player_login' in session:
        del session['player_login']
        del session['player_id']

        if 'admin_login' in session:
            del session['admin_login']

    return redirect(url_for('main.index'))


@main.route('/community')
def community():
    """Serve the community page.

    Returns
    -------
    name : TYPE
        Description
    """
    return render_template('main_community.html')
