from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_sessions'

def get_db_connection():
    return mysql.connector.connect(
        host="185.114.247.43",
        port=3306,
        database="sch688_vvedenie",
        user="sch688_vvedenie",
        password="Qwerty123"
    )

@app.route('/user_register', methods=['POST'])
def user_register():
    req = request.get_json()
    name = req['name']
    email = req['email']
    password = req['password']
    hashed_password = generate_password_hash(password)
    
    try:
        cnx = get_db_connection()
        cur = cnx.cursor()
        cur.execute('INSERT INTO `users`(`username`, `email`, `password_hash`, `balance`) VALUES (%s, %s, %s, %s)', (name, email, hashed_password, 100))
        cnx.commit()
        user_id = cur.lastrowid
        
        cur.execute('INSERT INTO `transactions`(`user_id`, `type`, `cost`, `description`) VALUES (%s, %s, %s, %s)', 
                   (user_id, 'пополнение', 100, 'Приветственный бонус'))
        cnx.commit()
        cnx.close()

        session['user_id'] = user_id
        session['username'] = name
        session['balance'] = 100
        
        return jsonify({"result": True})
    except Exception as e:
        print("Ошибка регистрации:", e)
        return jsonify({"result": False})

@app.route('/user_login', methods=['POST'])
def user_login():
    req = request.get_json()
    uname = req['uname']
    password = req['p_hash']
    
    try:
        cnx = get_db_connection()
        cur = cnx.cursor(dictionary=True)
        cur.execute('SELECT * FROM users WHERE username=%s OR email=%s', (uname, uname))
        user = cur.fetchone()
        cnx.close()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['balance'] = user.get('balance', 0)
            return jsonify({"result": True})
        else:
            return jsonify({"result": False})
    except Exception as e:
        print("Ошибка входа:", e)
        return jsonify({"result": False})

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route("/")
def registration():
    if 'user_id' in session:
        return redirect(url_for('to_lk'))
    return render_template('registration.html')

@app.route("/login")
def login():
    if 'user_id' in session:
        return redirect(url_for('to_lk'))
    return render_template('login.html')

@app.route("/lk")
def to_lk():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    udt = {
        'username': session.get('username'),
        'balance': session.get('balance'),
    }
    return render_template('lk.html', user=udt)

@app.route("/history")
def history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        cnx = get_db_connection()
        cur = cnx.cursor(dictionary=True)
        cur.execute('SELECT type, cost, description, created_at FROM transactions WHERE user_id=%s ORDER BY created_at DESC LIMIT 50', 
                   (session['user_id'],))
        transactions = cur.fetchall()
        
        cur.execute('SELECT SUM(cost) as total_spent FROM transactions WHERE user_id=%s AND type=%s', 
                   (session['user_id'], 'списание'))
        result = cur.fetchone()
        total_spent = abs(result['total_spent']) if result['total_spent'] else 0
        cnx.close()
        
        for tx in transactions:
            tx['amount'] = tx['cost'] if tx['type'] == 'пополнение' else -abs(tx['cost'])
        
        dt = {
            'balance': session.get('balance'),
            'sum_sp': total_spent,
            'transactions': transactions
        }
        return render_template('history.html', user=dt)
    except Exception as e:
        print("Ошибка получения истории:", e)
        return render_template('history.html', user={'balance': session.get('balance'), 'sum_sp': 0, 'transactions': []})

@app.route("/topup_balance", methods=['POST'])
def topup_balance():
    if 'user_id' not in session:
        return jsonify({"result": False, "error": "Не авторизован"})
    
    req = request.get_json()
    amount = req.get('amount', 0)
    
    if not isinstance(amount, (int, float)) or amount < 1 or amount > 10000:
        return jsonify({"result": False, "error": "Сумма должна быть от 1 до 10000 рублей"})
    
    try:
        cnx = get_db_connection()
        cur = cnx.cursor()
        
        cur.execute('SELECT balance FROM users WHERE id=%s', (session['user_id'],))
        user = cur.fetchone()
        new_balance = user[0] + amount
        
        cur.execute('UPDATE users SET balance=%s WHERE id=%s', (new_balance, session['user_id']))
        cur.execute('INSERT INTO `transactions`(`user_id`, `type`, `cost`, `description`) VALUES (%s, %s, %s, %s)', 
                   (session['user_id'], 'пополнение', amount, 'Пополнение баланса'))
        cnx.commit()
        cnx.close()
        
        session['balance'] = new_balance
        return jsonify({"result": True, "new_balance": new_balance})
    except Exception as e:
        print("Ошибка пополнения:", e)
        return jsonify({"result": False, "error": "Ошибка базы данных"})

@app.route("/make_request", methods=['POST'])
def make_request():
    if 'user_id' not in session:
        return jsonify({"result": False, "error": "Не авторизован"})
    
    current_balance = session.get('balance', 0)
    
    if current_balance >= 3:
        new_balance = current_balance - 3
        try:
            cnx = get_db_connection()
            cur = cnx.cursor()
            cur.execute('UPDATE users SET balance=%s WHERE id=%s', (new_balance, session['user_id']))
            cur.execute('INSERT INTO `transactions`(`user_id`, `type`, `cost`, `description`) VALUES (%s, %s, %s, %s)', 
                       (session['user_id'], 'списание', 3, 'Выполнение запроса'))
            cnx.commit()
            cnx.close()
            
            session['balance'] = new_balance
            return jsonify({"result": True, "new_balance": new_balance})
        except Exception as e:
            print("Ошибка запроса:", e)
            return jsonify({"result": False, "error": "Ошибка базы данных"})
    else:
        return jsonify({"result": False, "error": "Недостаточно средств на балансе"})

if __name__ == '__main__':
    app.run(debug=True)
