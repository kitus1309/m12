#!/usr/bin/python

from flask import Flask, request, redirect, url_for
from flask import render_template
import sqlite3
from flask import g

app = Flask(__name__)

DATABASE = './database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route("/")
def hello():
    return render_template('hello.html')

def get_product_list():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT title, description, photo, price FROM products')
    products = cursor.fetchall()
    conn.close()
    return products

@app.route('/products/list')
def list_products():
    products = get_product_list()
    return render_template('/products/list.html', products=products)

@app.route("/products/create", methods=['GET', 'POST'])
def create_product():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        photo = request.form['photo']
        price = request.form['price']
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO products (title, description, photo, price) VALUES (?, ?, ?, ?)", (title, description, photo, price))
        conn.commit()
        conn.close()
        
        return redirect(url_for('list_products'))  # Redirige a la lista de productos después de la creación
    else:
        return render_template('/products/create.html')

@app.route("/products/read/<int:id>")
def read_product(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id=?", (id,))
    product = cursor.fetchone()
    conn.close()

    if product is None:
        return "Producto no encontrado", 404
    else:
        return render_template('/products/read.html', product=product)
    
@app.route("/products/update/<int:id>", methods=['GET', 'POST'])
def update_product(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id=?", (id,))
    product = cursor.fetchone()

    if product is None:
        conn.close()
        return "Producto no encontrado", 404

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        photo = request.form['photo']
        price = request.form['price']

        cursor.execute("UPDATE products SET title=?, description=?, photo=?, price=? WHERE id=?", (title, description, photo, price, id))
        conn.commit()
        conn.close()

        return redirect(url_for('list_products'))  # Redirige a la lista de productos después de la actualización
    else:
        conn.close()
        return render_template('/products/update.html', product=product)

@app.route("/products/delete/<int:id>", methods=['GET', 'POST'])
def delete_product(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id=?", (id,))
    product = cursor.fetchone()

    if product is None:
        conn.close()
        return "Producto no encontrado", 404

    if request.method == 'POST':
        cursor.execute("DELETE FROM products WHERE id=?", (id,))
        conn.commit()
        conn.close()

        return redirect(url_for('list_products'))  # Redirige a la lista de productos después de la eliminación
    else:
        conn.close()
        return render_template('/products/delete.html', product=product)



