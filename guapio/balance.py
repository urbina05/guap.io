from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from guapio.auth import login_required
from guapio.db import get_db

bp = Blueprint('balance', __name__, url_prefix='/balance')


@bp.route('/')
def index():
    """Show all the balances, most recent first."""
    db = get_db()
    balances = db.execute(
        'SELECT b.id, balance, user_id, currency_id, b.created'
        ' FROM balance b JOIN user u ON b.user_id = u.id JOIN currency c ON b.currency_id = c.id'
        ' ORDER BY b.created DESC'
    ).fetchall()
    return render_template('balance/index.html', balances=balances)


def get_balance(id, check_author=True):
    """Get a balance by id.

    Checks that the id exists and optionally that the current user is
    the author.

    :param id: id of balance to get
    :param check_author: require the current user to be the author
    :return: the balance with author information
    :raise 404: if a balance with the given id doesn't exist
    :raise 403: if the current user isn't the author
    """
    balance = get_db().execute(
        'SELECT b.id, balance, user_id, currency_id, b.created'
        ' FROM balance b JOIN user u ON b.user_id = u.id JOIN currency c ON b.currency_id = c.id'
        ' WHERE b.id = ?',
        (id,)
    ).fetchone()

    if balance is None:
        abort(404, "balance id {0} doesn't exist.".format(id))

    if check_author and balance['user_id'] != g.user['id']:
        abort(403)

    return balance

def get_current_balance_from_user_id(user_id=None, currency_id=None):
    """Get a balance by user id.

    Checks that the id exists and optionally that the current user is
    the author.

    :param id: id of balance to get
    :param check_author: require the current user to be the author
    :return: the balance with author information
    :raise 404: if a balance with the given id doesn't exist
    :raise 403: if the current user isn't the author
    """
    if user_id is None:
        user_id = g.user['id']

    elif user_id != g.user['id']:
        abort(403)

    if currency_id is None:
        balances = get_db().execute(
            'SELECT '
            ' c.id as currency_id,  title, code, purchase_rate, sale_rate,'
            ' b.id as balance_id, balance, user_id'
            ' FROM currency c'
            ' LEFT JOIN balance b on c.id = b.currency_id'
            ' AND b.user_id = ?',
            (user_id,)
        ).fetchall()

    else:
        balances = get_db().execute(
            'SELECT '
            ' c.id as currency_id,  title, code, purchase_rate, sale_rate,'
            ' b.id as balance_id, balance, user_id'
            ' FROM currency c'
            ' LEFT JOIN balance b on c.id = b.currency_id'
            ' AND b.user_id = ?'
            ' WHERE c.id = ?',
            (user_id, currency_id)
        ).fetchone()

    if balances is None:
        abort(404, "balances for user id {0} doesn't exist.".format(user_id))

    return balances


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    """Create a new balance for the current user."""
    if request.method == 'POST':
        balance = request.form['balance']
        user_id = request.form['user_id']
        currency_id = request.form['currency_id']
        error = None

        if not balance:
            error = 'Balance is required.'
        if not user_id:
            error = 'User is required.'
        if not currency_id:
            error = 'Currency is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO balance (balance, user_id, currency_id)'
                ' VALUES (?, ?, ?)',
                (balance, g.user['id'], currency_id)
            )
            db.commit()
            return redirect(url_for('balance.index'))

    return render_template('balance/create.html')

@bp.route('/<int:currency_id>/load', methods=('GET', 'POST'))
@login_required
def load(currency_id):
    """Update a balance if the current user is the author."""
    balance = get_current_balance_from_user_id(g.user['id'], currency_id)

    print balance.keys()

    if request.method == 'POST':
        balance_id = request.form['id']
        error = None

        if error is not None:
            flash(error)

        print balance_id

        if balance_id:
            update(id=balance_id)
        else:
            create()

        return redirect(url_for('blog.index'))

    return render_template('balance/load.html', balance=balance)


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    """Update a balance if the current user is the author."""
    balance = get_balance(id)

    if request.method == 'POST':
        balance_value = request.form['balance']
        error = None

        if not balance_value:
            error = 'Balance is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE balance SET balance = ? WHERE id = ?',
                (balance_value, id)
            )
            db.commit()
            return redirect(url_for('balance.index'))

    return render_template('balance/update.html', balance=balance)


@bp.route('/<int:id>/delete', methods=('balance',))
@login_required
def delete(id):
    """Delete a balance.

    Ensures that the balance exists and that the logged in user is the
    author of the balance.
    """
    get_balance(id)
    db = get_db()
    db.execute('DELETE FROM balance WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('balance.index'))
