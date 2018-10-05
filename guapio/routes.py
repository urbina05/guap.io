from flask import  Flask, Blueprint, url_for, request, render_template

bp = Blueprint('routes', __name__)

@bp.route('/')
def index():
    return 'index'

@bp.route('/login')
def login():
    return 'login'

@bp.route('/hello/')
@bp.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)

# @bp.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         return do_the_login()
#     else:
#         return show_the_login_form()

@bp.route('/user/<username>')
def profile(username):
    return '{}\'s profile'.format(username)

@bp.errorhandler(404)
def not_found(error):
    return render_template('error.html'), 404