from flask import Flask, jsonify, request, render_template, redirect, url_for, session
from database import ServerDatabaseManager
import os

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.urandom(24)
db = ServerDatabaseManager()


@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user_id' in session:
        return redirect(url_for('stats_page'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = db.get_user_by_username(username)

        if user and user['password_hash'] == db._hash_password(password):
            session['user_id'] = user['id']
            return redirect(url_for('stats_page'))
        else:
            return render_template('index.html', error="Неверное имя пользователя или пароль")
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            return render_template('register.html', error="Пароли не совпадают")

        if db.get_user_by_username(username):
            return render_template('register.html', error="Пользователь с таким именем уже существует")

        db.add_user(username, password)
        return redirect(url_for('index'))
    return render_template('register.html')


@app.route('/stats')
def stats_page():
    if 'user_id' not in session:
        return redirect(url_for('index'))

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


# === НОВОЕ: API endpoints для десктопного клиента ===
@app.route('/api/login', methods=['POST'])
def api_login():
    """API endpoint для входа десктопного клиента"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'success': False, 'message': 'Missing credentials'}), 400

    user = db.get_user_by_username(username)
    if user and user['password_hash'] == db._hash_password(password):
        return jsonify({'success': True, 'user_id': user['id']}), 200
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401


@app.route('/api/register', methods=['POST'])
def api_register():
    """API endpoint для регистрации десктопного клиента"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'success': False, 'message': 'Missing credentials'}), 400

    if db.get_user_by_username(username):
        return jsonify({'success': False, 'message': 'User already exists'}), 409

    db.add_user(username, password)
    return jsonify({'success': True, 'message': 'User registered'}), 201


@app.route('/api/test_result', methods=['POST'])
def api_save_test_result():
    """API endpoint для сохранения результата теста"""
    data = request.get_json()
    user_id = data.get('user_id')
    results = data.get('results')

    if not user_id or not results:
        return jsonify({'success': False, 'message': 'Missing data'}), 400

    # Сохраняем результат в БД
    db.cursor.execute("""
                      INSERT INTO test_results (user_id, test_date, avg_reaction_time, missed_go, false_alarms)
                      VALUES (?, ?, ?, ?, ?)
                      """, (user_id,
                            __import__('datetime').datetime.now().isoformat(),
                            sum(results.get('reaction_times', [])) / len(results.get('reaction_times', [1])),
                            results.get('missed_go', 0),
                            results.get('false_alarms', 0)))
    db.conn.commit()

    return jsonify({'success': True}), 200


@app.route('/api/test_results/<int:user_id>', methods=['GET'])
def api_get_test_results(user_id):
    """API endpoint для получения результатов тестов"""
    results = db.get_test_results(user_id)
    return jsonify({'results': [
        {
            'test_date': r['test_date'],
            'avg_reaction_time': r['avg_reaction_time'],
            'missed_go': r['missed_go'],
            'false_alarms': r['false_alarms']
        } for r in results
    ]}), 200


# =====================================================

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, port=5000)