#!/usr/bin/python

from flask import Flask
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
    conn = sqlite3.connect('datebase.db')
    cursor = conn.cursor()
    cursor.execute('SELECT title, description, photo, price FROM products')
    products = cursor.fetchall()
    conn.close()
    return products

@app.route('/products/list')
def list_products():
    products = get_product_list()
    return render_template('/products/list.html', products=products)

@app.route('/products/create', methods=['GET'])
def show_create_form():
    return render_template('create.html')

@app.route('/products/create', methods=['POST'])
def create_product():
    if request.method == 'POST':
        # Obtener los datos del formulario
        title = request.form['title']
        description = request.form['description']
        photo = request.form['photo']
        price = request.form['price']

        # Insertar los datos en la base de datos
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO products (title, description, photo, price) VALUES (?, ?, ?, ?)",
                       (title, description, photo, price))
        conn.commit()
        conn.close()
        flash('Producto creado exitosamente', 'success')
        return redirect('/products/list')
    
@app.route('/products/update/<int:id>/edit', methods=['GET'])
def show_update_form(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products WHERE id = ?', (id,))
    product = cursor.fetchone()
    conn.close()
    return render_template('update.html', product=product)

@app.route('/products/update/<int:id>', methods=['POST'])
def update_product(id):
    if request.method == 'POST':
        # Obtener los datos del formulario
        title = request.form['title']
        description = request.form['description']
        photo = request.form['photo']
        price = request.form['price']

        # Actualizar los datos en la base de datos
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE products SET title=?, description=?, photo=?, price=? WHERE id=?",
                       (title, description, photo, price, id))
        conn.commit()
        conn.close()
        flash('Producto actualizado exitosamente', 'success')
        return redirect('/products/list')

@app.route('/products/delete/<int:id>', methods=['GET'])
def delete_product(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM products WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Producto eliminado exitosamente', 'success')
    return redirect('/products/list')


