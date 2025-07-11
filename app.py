from flask import Flask, render_template, request, redirect, url_for
import requests
import sqlite3

app = Flask(__name__)


def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('INSERT INTO users (username) VALUES (?)', ('Oğuz',))
    c.execute('INSERT INTO users (username) VALUES (?)', ('Fatih',))
    conn.commit()
    conn.close()

init_db()

products = [
    {"id": 1, "name": "Ayakkabı"},
    {"id": 2, "name": "Çanta"},
    {"id": 3, "name": "Pantolon"},
    {"id": 4, "name": "Tişört"},
    {"id": 5, "name": "Sweatshirt"},
    {"id": 6, "name": "Ceket"},
    {"id": 7, "name": "Mont"},
    {"id": 8, "name": "Şapka"},
    {"id": 9, "name": "Eldiven"},
    {"id": 10, "name": "Atkı"}
]

@app.route('/')
def index():
    return render_template("index.html", products=products)

@app.route('/product/<int:product_id>', methods=["GET", "POST"])
def product(product_id):
    product = next((p for p in products if p['id'] == product_id), None)
    stock_result = None

    if request.method == "POST":
        color = request.form.get("color")
        stock_server = request.headers.get("X-Stock-Server", "http://localhost:5000")
        try:

#                                         SSRF ZAFİYETİ


            response = requests.get(f"{stock_server}/check_stock?product_id={product_id}&color={color}")
            stock_result = response.text
        except:
            stock_result = "Stok kontrolü sırasında hata oluştu."

    return render_template("product.html", product=product, stock_result=stock_result)

@app.route('/check_stock')
def check_stock():
    product_id = request.args.get("product_id")
    color = request.args.get("color")
    # Basit örnek: sadece kırmızı renkte stok var
    if color.lower() == "kirmizi":
        return f"{product_id} için kırmızı stokta var."
    else:
        return f"{product_id} için {color} stokta YOK."

@app.route('/admin', methods=["GET", "POST"])
def admin():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    users = c.fetchall()

    if request.method == "POST":
        user_id = request.form.get("user_id")
        c.execute("DELETE FROM users WHERE id=?", (user_id,))
        conn.commit()

    c.execute("SELECT * FROM users")
    users = c.fetchall()
    conn.close()

    return render_template("admin.html", users=users)

@app.route('/admin/delete_user')
def delete_user():
    user_id = request.args.get("user_id")
    if not user_id:
        return "Kullanıcı ID gerekli", 400

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

    return f"Kullanıcı {user_id} silindi."


if __name__ == '__main__':
    app.run(debug=True)
