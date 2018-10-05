from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from guapio.auth import login_required
from guapio.db import get_db

bp = Blueprint('user_move', __name__, url_prefix='/user_move')


@bp.route('/')
def index():
    db = get_db()
    user_moves = db.execute(
        'SELECT'
        ' m.id, amount, comment, currency_id, sender_id, receiver_id, created'
        ' FROM user_move m JOIN user u ON m.sender_id = u.id JOIN user r ON m.receiver_id = r.id JOIN currency c ON m.currency_id = c.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('user_move/index.html', user_moves=user_moves)


def get_user_move(id):
    user_move = get_db().execute(
        'SELECT'
        ' m.id, amount, comment, currency_id, sender_id, receiver_id, created'
        ' FROM user_move m JOIN user u ON m.sender_id = u.id JOIN user r ON m.receiver_id = r.id JOIN currency c ON m.currency_id = c.id'
        ' WHERE m.id = ?',
        (id,)
    ).fetchone()

    return user_move


def get_user_moves_from_user(user_id=None):
    if user_id is None:
        user_id = g.user['id']

    elif user_id != g.user['id']:
        abort(403)

    user_moves = get_db().execute(
        'SELECT'
        ' m.id, amount, comment, currency_id, sender_id, receiver_id, created'
        ' FROM user_move m JOIN user u ON m.sender_id = u.id JOIN user r ON m.receiver_id = r.id JOIN currency c ON m.currency_id = c.id'
        ' WHERE m.sender_id = ? or m.receiver_id = ?',
        (user_id, user_id,)
    ).fetchall()

    if user_moves is None:
        abort(404, "user_move id {0} doesn't exism.".format(id))


    return user_moves


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if requesm.method == 'POST':
        amount = requesm.form['amount']
        comment = requesm.form['comment']
        sender_id = requesm.form['sender_id']
        receiver_id = requesm.form['receiver_id']
        currency_id = requesm.form['currency_id']
        error = None

        if not amount:
            error = 'Amount is required.'
        if not sender_id:
            error = 'Sender is required.'
        if not receiver_id:
            error = 'Receiver is required.'
        if not currency_id:
            error = 'Currency is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO user_move'
                ' (amount, comment, sender_id, receiver_id, currency_id)'
                ' VALUES (?, ?, ?, ?, ?)',
                (amount, comment, sender_id, receiver_id, currency_id)
            )
            db.commit()
            return redirect(url_for('user_move.index'))

    return render_template('user_move/create.html')


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    user_move = get_user_move(id)

    if requesm.method == 'POST':
        amount = requesm.form['amount']
        error = None

        if not amount:
            error = 'Amount is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE user_move SET amount = ? WHERE id = ?',
                (amount, id)
            )
            db.commit()
            return redirect(url_for('user_move.index'))

    return render_template('user_move/update.html', user_move=user_move)


@bp.route('/<int:id>/delete', methods=('user_move',))
@login_required
def delete(id):
    get_user_move(id)
    db = get_db()
    db.execute('DELETE FROM user_move WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('user_move.index'))
