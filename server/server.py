from flask import Flask, jsonify, request, render_template, redirect, url_for, session
from database import ServerDatabaseManager
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
db = ServerDatabaseManager()

# --- Веб-страницы ---

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user_id' in session:
        return redirect(url_for('stats_page'))
    if request.method == 'POST':
        user = db.get_user_by_username(request.form['username'])
        if user and user['password_hash'] == db._hash_password(request.form['password']):
            session['user_id'] = user['id']
            return redirect(url_for('stats_page'))
        else:
            return render_template('index.html', error="Неверное имя или пароль")
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        password = request.form['password']
        if password != request.form['confirm_password']:
            return render_template('register.html', error="Пароли не совпадают")
        if db.add_user(request.form['username'], password):
            return redirect(url_for('index'))
        else:
            return render_template('register.html', error="Пользователь уже существует")
    return render_template('register.html')

@app.route('/stats')
def stats_page():
    if 'user_id' not in session: return redirect(url_for('index'))
    current_user = db.get_user_by_id(session['user_id'])
    current_user_stats = db.get_test_results(session['user_id'])
    all_users = db.get_all_users()
    compare_user_id = request.args.get('compare_user_id', type=int)
    compare_user = None
    compare_user_stats = []
    if compare_user_id:
        compare_user = db.get_user_by_id(compare_user_id)
        compare_user_stats = db.get_test_results(compare_user_id)
    return render_template('statistics.html', 
                           current_user=current_user,
                           current_user_stats=current_user_stats,
                           all_users=all_users,
                           compare_user=compare_user,
                           compare_user_stats=compare_user_stats)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

# --- API для десктопного клиента ---

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    user = db.get_user_by_username(data.get('username'))
    if user and user['password_hash'] == db._hash_password(data.get('password')):
        return jsonify({"success": True, "user_id": user['id'], "username": user['username']})
    return jsonify({"success": False, "message": "Неверные данные"}), 401

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    if db.add_user(data.get('username'), data.get('password')):
        return jsonify({"success": True}), 201
    return jsonify({"success": False, "message": "Пользователь уже существует"}), 409

if __name__ == '__main__':
    app.run(debug=True, port=5000)
