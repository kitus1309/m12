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
    return render_template('list.html', products=products)