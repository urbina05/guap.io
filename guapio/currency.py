from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from guapio.auth import login_required
from guapio.db import get_db

bp = Blueprint('currency', __name__, url_prefix='/currency')

def get_currencies():
    db = get_db()
    return db.execute(
        'SELECT c.id, title, code, created, purchase_rate, sale_rate'
        ' FROM currency c'
        ' ORDER BY created DESC'
    ).fetchall()


@bp.route('/')
def index():
    return render_template('currency/index.html', currencies=get_currencies())


def get_currency(id, check_author=True):
    currency = get_db().execute(
        'SELECT c.id,  title, code, created, purchase_rate, sale_rate'
        ' FROM currency c'
        ' WHERE c.id = ?',
        (id,)
    ).fetchone()

    if currency is None:
        abort(404, "currency id {0} doesn't exist.".format(id))

    return currency


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        code = request.form['code']
        purchase_rate = request.form['purchase_rate']
        sale_rate = request.form['sale_rate']
        error = None

        if not title:
            error = 'Title is required.'
        elif not code:
            error = 'Code is required.'
        elif not purchase_rate:
            error = 'Purchase Rate is required.'
        elif not sale_rate:
            error = 'Sale Rate is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO currency (title, code, purchase_rate, sale_rate)'
                ' VALUES (?, ?, ?, ?)',
                (title, code, purchase_rate, sale_rate)
            )
            db.commit()
            return redirect(url_for('currency.index'))

    return render_template('currency/create.html')


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    currency = get_currency(id)

    if request.method == 'POST':
        title = request.form['title']
        code = request.form['code']
        purchase_rate = request.form['purchase_rate']
        sale_rate = request.form['sale_rate']
        error = None

        if not title:
            error = 'Title is required.'
        elif not code:
            error = 'Code is required.'
        elif not purchase_rate:
            error = 'Purchase Rate is required.'
        elif not sale_rate:
            error = 'Sale Rate is required.'


        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE currency SET title = ?, code = ?, purchase_rate, sale_rate = ? WHERE id = ?',
                (title, code, purchase_rate, sale_rate, id)
            )
            db.commit()
            return redirect(url_for('currency.index'))

    return render_template('currency/update.html', currency=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_currency(id)
    db = get_db()
    db.execute('DELETE FROM currency WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('currency.index'))
