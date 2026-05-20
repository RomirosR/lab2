import sqlite3
import os
from flask import Flask, render_template, request, jsonify, g

app = Flask(__name__)
DATABASE = 'database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys = ON")
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def table_exists(table_name):
    db = get_db()
    res = db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,)
    ).fetchone()
    return res is not None

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.executescript(f.read())
        with app.open_resource('seed.sql', mode='r') as f:
            db.executescript(f.read())
        db.commit()

if not os.path.exists(DATABASE):
    init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/tables')
def get_tables():
    db = get_db()
    tables = db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    ).fetchall()
    return jsonify([t['name'] for t in tables])

@app.route('/api/<table>/meta')
def get_meta(table):
    if not table_exists(table):
        return jsonify({'error': 'Invalid table'}), 404
    db = get_db()
    cols_info = db.execute(f"PRAGMA table_info({table})").fetchall()
    fks = db.execute(f"PRAGMA foreign_key_list({table})").fetchall()
    fk_map = {}
    for fk in fks:
        fk_map[fk['from']] = {
            'table': fk['table'],
            'to': fk['to']
        }
    columns = []
    for col in cols_info:
        name = col['name']
        col_type = col['type'].upper() if col['type'] else ''
        fk_info = fk_map.get(name, None)
        columns.append({
            'name': name,
            'type': col_type,
            'pk': bool(col['pk']),
            'notnull': bool(col['notnull']),
            'fk': fk_info
        })
    return jsonify({'columns': columns})

@app.route('/api/<table>')
def get_table_data(table):
    if not table_exists(table):
        return jsonify({'error': 'Invalid table'}), 404

    sort_column = request.args.get('sort', 'id')
    order = request.args.get('order', 'asc')
    order = order if order in ('asc', 'desc') else 'asc'

    db = get_db()
    cols_info = db.execute(f"PRAGMA table_info({table})").fetchall()
    column_names = [col['name'] for col in cols_info]
    if sort_column not in column_names:
        sort_column = column_names[0]  

    query = f"SELECT * FROM {table} ORDER BY {sort_column} {order}"
    rows = db.execute(query).fetchall()
    data = [dict(row) for row in rows]
    return jsonify({'columns': column_names, 'rows': data})

@app.route('/api/<table>/<int:id>')
def get_record(table, id):
    if not table_exists(table):
        return jsonify({'error': 'Invalid table'}), 404
    db = get_db()
    row = db.execute(f"SELECT * FROM {table} WHERE id = ?", (id,)).fetchone()
    if row is None:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(dict(row))

@app.route('/api/<table>', methods=['POST'])
def create_record(table):
    if not table_exists(table):
        return jsonify({'error': 'Invalid table'}), 404
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data'}), 400
    db = get_db()
    columns = ', '.join(data.keys())
    placeholders = ', '.join(['?' for _ in data])
    try:
        db.execute(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", list(data.values()))
        db.commit()
        return jsonify({'status': 'ok'}), 201
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/<table>/<int:id>', methods=['PUT'])
def update_record(table, id):
    if not table_exists(table):
        return jsonify({'error': 'Invalid table'}), 404
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data'}), 400
    db = get_db()
    set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
    try:
        db.execute(f"UPDATE {table} SET {set_clause} WHERE id = ?", list(data.values()) + [id])
        db.commit()
        return jsonify({'status': 'ok'})
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/<table>/<int:id>', methods=['DELETE'])
def delete_record(table, id):
    if not table_exists(table):
        return jsonify({'error': 'Invalid table'}), 404
    db = get_db()
    try:
        db.execute(f"DELETE FROM {table} WHERE id = ?", (id,))
        db.commit()
        return jsonify({'status': 'ok'})
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Невозможно удалить: есть связанные записи в другом справочнике'}), 409

if __name__ == '__main__':
    app.run(debug=True)