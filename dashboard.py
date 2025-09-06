from flask import Flask, render_template_string, redirect, url_for, request, session
from datetime import datetime
from bot import users
import os

app = Flask(__name__)
app.secret_key = os.getenv("DASHBOARD_SECRET", "supersecret")

ADMIN_USER = os.getenv("DASHBOARD_USER", "admin")
ADMIN_PASS = os.getenv("DASHBOARD_PASS", "password")

# 🔹 قوالب HTML
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar">
<head>
    <meta charset="UTF-8">
    <title>تسجيل الدخول</title>
    <style>
        body { font-family: Tahoma; background: #f4f4f9; display: flex; justify-content: center; align-items: center; height: 100vh; }
        .login { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 0 10px rgba(0,0,0,0.1); width: 300px; text-align: center; }
        input { width: 90%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 6px; }
        button { padding: 10px; width: 100%; background: #333; color: white; border: none; border-radius: 6px; cursor: pointer; }
        .error { color: red; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="login">
        <h2>🔒 تسجيل الدخول</h2>
        <form method="post">
            <input type="text" name="username" placeholder="اسم المستخدم" required><br>
            <input type="password" name="password" placeholder="كلمة السر" required><br>
            <button type="submit">دخول</button>
        </form>
        {% if error %}<p class="error">{{ error }}</p>{% endif %}
    </div>
</body>
</html>
"""

DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar">
<head>
    <meta charset="UTF-8">
    <title>لوحة التحكم</title>
    <style>
        body { font-family: Tahoma, sans-serif; background: #f4f4f9; margin: 0; padding: 20px; }
        h1 { color: #333; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 10px; text-align: center; }
        th { background: #333; color: white; }
        tr:nth-child(even) { background: #f9f9f9; }
        .premium { color: green; font-weight: bold; }
        .btn { padding: 6px 12px; border-radius: 6px; text-decoration: none; }
        .btn-prem { background: green; color: white; }
        .btn-free { background: red; color: white; }
        .logout { float: left; margin-bottom: 20px; }
    </style>
</head>
<body>
    <a class="logout" href="{{ url_for('logout') }}">🚪 تسجيل خروج</a>
    <h1>📊 لوحة تحكم البوت</h1>
    <p>عدد المستخدمين: {{ total_users }}</p>
    <p>عدد عمليات اليوم: {{ total_ops }}</p>
    <h2>👥 المستخدمين</h2>
    <table>
        <tr>
            <th>User ID</th>
            <th>Premium</th>
            <th>عمليات اليوم</th>
            <th>آخر دخول</th>
            <th>تحكم</th>
        </tr>
        {% for uid, data in users.items() %}
        <tr>
            <td>{{ uid }}</td>
            <td class="{{ 'premium' if data.premium else '' }}">{{ "✔️" if data.premium else "❌" }}</td>
            <td>{{ data.count }}</td>
            <td>{{ data.last_day }}</td>
            <td>
                {% if not data.premium %}
                    <a class="btn btn-prem" href="{{ url_for('make_premium', uid=uid) }}">تفعيل بريميوم</a>
                {% else %}
                    <a class="btn btn-free" href="{{ url_for('remove_premium', uid=uid) }}">إلغاء بريميوم</a>
                {% endif %}
            </td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

# 🔹 حماية
def login_required(f):
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        if request.form["username"] == ADMIN_USER and request.form["password"] == ADMIN_PASS:
            session["logged_in"] = True
            return redirect(url_for("home"))
        else:
            error = "❌ بيانات الدخول غير صحيحة"
    return render_template_string(LOGIN_TEMPLATE, error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
@login_required
def home():
    total_users = len(users)
    total_ops = sum(u["count"] for u in users.values())
    return render_template_string(DASHBOARD_TEMPLATE, users=users, total_users=total_users, total_ops=total_ops)

@app.route("/make_premium/<int:uid>")
@login_required
def make_premium(uid):
    if uid in users:
        users[uid]["premium"] = True
    return redirect(url_for('home'))

@app.route("/remove_premium/<int:uid>")
@login_required
def remove_premium(uid):
    if uid in users:
        users[uid]["premium"] = False
    return redirect(url_for('home'))
