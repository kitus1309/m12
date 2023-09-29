#!/usr/bin/python

from flask import Flask, request, redirect, url_for, g, render_template
import sqlite3, os, datetime
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

DATABASE = './database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
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
        price = request.form['price']
        category_id = request.form['category_id']
        seller_id = "1"
        
        # Validación de la foto
        photo = request.files['photo']
        if not photo or photo.filename == '':
            return "La foto es obligatoria", 400
        if not allowed_file(photo.filename):
            return "Tipo de archivo no permitido", 400
        if photo.content_length > 2 * 1024 * 1024:
            return "La foto no puede superar los 2MB", 400
        if photo and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            #return redirect(url_for('download_file', name=filename))

            # Obtener la fecha y hora actual en el formato 'Y-m-d H:i:s'
            current_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO products (title, description, photo, price, category_id, seller_id, created, updated) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (title, description, photo.filename, price, category_id, seller_id, current_datetime, current_datetime))
            conn.commit()
            conn.close()
            return redirect(url_for('list_products'))  # Redirige a la lista de productos después de la creación
        else:
            #TODO fitxer invalid
            return redirect(url_for('create_product'))  # Redirige al form
    else:
        # Obtener las categorías desde la base de datos
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id, name FROM categories')
        categories = cursor.fetchall()
        conn.close()
        return render_template('/products/create.html', categories=categories)

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
        price = request.form['price']
        category_id = request.form['category_id']
        seller_id = product[5]  # Mantenemos el seller_id original
        created = product[6]    # Mantenemos el created original

        # Validación de la foto
        photo = request.files['photo']
        if photo and photo.filename:
            if not allowed_file(photo.filename):
                conn.close()
                return "Tipo de archivo no permitido", 400
            if photo.content_length > 2 * 1024 * 1024:
                conn.close()
                return "La foto no puede superar los 2MB", 400

        # Actualizamos el updated con la fecha y hora actual en el formato 'Y-m-d H:i:s'
        updated = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        cursor.execute("UPDATE products SET title=?, description=?, photo=?, price=?, category_id=?, seller_id=?, created=?, updated=? WHERE id=?", (title, description, photo.filename, price, category_id, seller_id, created, updated, id))
        conn.commit()
        conn.close()

        return redirect(url_for('list_products'))  # Redirige a la lista de productos después de la actualización
    else:
        # Obtener las categorías desde la base de datos
        cursor.execute('SELECT id, name FROM categories')
        categories = cursor.fetchall()
        conn.close()
        return render_template('/products/update.html', product=product, categories=categories)

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

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


