import sqlite3
import hashlib
import os
import json
from datetime import datetime
from functools import wraps
from flask import Flask, request, jsonify, session, send_file, send_from_directory

app = Flask(__name__, static_folder='.', static_url_path='')
app.secret_key = os.environ.get('SECRET_KEY', 'saude-masculina-secret-2026-dev')

DB_PATH = 'health.db'


# ── Database ──────────────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA foreign_keys=ON')
    return conn


def init_db():
    with get_db() as conn:
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                name          TEXT    NOT NULL,
                email         TEXT    UNIQUE NOT NULL,
                password_hash TEXT    NOT NULL,
                role          TEXT    NOT NULL,
                created_at    TEXT    DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS records (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id  INTEGER NOT NULL,
                doctor_id   INTEGER,
                input_data  TEXT    NOT NULL,
                results     TEXT    NOT NULL,
                notes       TEXT    DEFAULT '',
                created_at  TEXT    DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS doctor_patients (
                doctor_id   INTEGER NOT NULL,
                patient_id  INTEGER NOT NULL,
                PRIMARY KEY (doctor_id, patient_id)
            );
        ''')


def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


def require_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Não autenticado'}), 401
        return f(*args, **kwargs)
    return wrapper


def require_doctor(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get('role') != 'doctor':
            return jsonify({'error': 'Acesso restrito a médicos'}), 403
        return f(*args, **kwargs)
    return wrapper


# ── Static Pages ──────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return send_file('index.html')


@app.route('/app')
@app.route('/app/')
def app_page():
    return send_file('app.html')


# ── Auth API ──────────────────────────────────────────────────────────────────

@app.route('/api/auth/register', methods=['POST'])
def register():
    d = request.json or {}
    name     = (d.get('name') or '').strip()
    email    = (d.get('email') or '').strip().lower()
    password = d.get('password') or ''
    role     = d.get('role') or ''

    if not all([name, email, password, role]):
        return jsonify({'error': 'Preencha todos os campos'}), 400
    if role not in ('doctor', 'patient'):
        return jsonify({'error': 'Perfil inválido'}), 400
    if len(password) < 6:
        return jsonify({'error': 'Senha deve ter ao menos 6 caracteres'}), 400

    try:
        with get_db() as conn:
            conn.execute(
                'INSERT INTO users (name,email,password_hash,role) VALUES (?,?,?,?)',
                (name, email, hash_pw(password), role)
            )
            user = conn.execute(
                'SELECT id,name,role FROM users WHERE email=?', (email,)
            ).fetchone()
        session['user_id'] = user['id']
        session['role']    = user['role']
        return jsonify(dict(user)), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'E-mail já cadastrado'}), 409


@app.route('/api/auth/login', methods=['POST'])
def login():
    d = request.json or {}
    email    = (d.get('email') or '').strip().lower()
    password = d.get('password') or ''

    with get_db() as conn:
        user = conn.execute(
            'SELECT id,name,role FROM users WHERE email=? AND password_hash=?',
            (email, hash_pw(password))
        ).fetchone()

    if not user:
        return jsonify({'error': 'E-mail ou senha incorretos'}), 401

    session['user_id'] = user['id']
    session['role']    = user['role']
    return jsonify(dict(user))


@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'ok': True})


@app.route('/api/me')
@require_auth
def me():
    with get_db() as conn:
        user = conn.execute(
            'SELECT id,name,email,role,created_at FROM users WHERE id=?',
            (session['user_id'],)
        ).fetchone()
    if not user:
        return jsonify({'error': 'Não encontrado'}), 404
    return jsonify(dict(user))


# ── Patient: own records ───────────────────────────────────────────────────────

@app.route('/api/records', methods=['GET'])
@require_auth
def get_my_records():
    if session['role'] != 'patient':
        return jsonify({'error': 'Rota apenas para pacientes'}), 403
    with get_db() as conn:
        rows = conn.execute(
            '''SELECT r.id, r.patient_id, r.doctor_id,
                      r.input_data, r.results, r.notes, r.created_at,
                      u.name AS doctor_name
               FROM records r
               LEFT JOIN users u ON r.doctor_id = u.id
               WHERE r.patient_id = ?
               ORDER BY r.created_at DESC''',
            (session['user_id'],)
        ).fetchall()
    return jsonify([_expand_record(r) for r in rows])


@app.route('/api/records', methods=['POST'])
@require_auth
def create_record():
    d = request.json or {}

    if session['role'] == 'patient':
        patient_id = session['user_id']
        doctor_id  = None
    else:
        patient_id = d.get('patient_id')
        doctor_id  = session['user_id']
        if not patient_id:
            return jsonify({'error': 'patient_id é obrigatório'}), 400

    input_data = json.dumps(d.get('input_data', {}))
    results    = json.dumps(d.get('results', []))
    notes      = (d.get('notes') or '').strip()

    with get_db() as conn:
        conn.execute(
            'INSERT INTO records (patient_id,doctor_id,input_data,results,notes) VALUES (?,?,?,?,?)',
            (patient_id, doctor_id, input_data, results, notes)
        )
        if doctor_id and patient_id:
            conn.execute(
                'INSERT OR IGNORE INTO doctor_patients VALUES (?,?)',
                (doctor_id, patient_id)
            )
        row = conn.execute(
            'SELECT * FROM records WHERE rowid=last_insert_rowid()'
        ).fetchone()
    return jsonify(_expand_record(row)), 201


# ── Doctor: patient management ─────────────────────────────────────────────────

@app.route('/api/patients', methods=['GET'])
@require_auth
@require_doctor
def get_patients():
    uid = session['user_id']
    with get_db() as conn:
        rows = conn.execute(
            '''SELECT u.id, u.name, u.email, u.created_at,
                      COUNT(r.id)         AS record_count,
                      MAX(r.created_at)   AS last_visit
               FROM users u
               JOIN doctor_patients dp ON dp.patient_id=u.id AND dp.doctor_id=?
               LEFT JOIN records r ON r.patient_id=u.id AND r.doctor_id=?
               GROUP BY u.id
               ORDER BY last_visit DESC NULLS LAST, u.name''',
            (uid, uid)
        ).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route('/api/patients/create', methods=['POST'])
@require_auth
@require_doctor
def create_patient():
    d        = request.json or {}
    name     = (d.get('name') or '').strip()
    email    = (d.get('email') or '').strip().lower()
    password = d.get('password') or ''

    if not all([name, email, password]):
        return jsonify({'error': 'Preencha todos os campos'}), 400
    if len(password) < 6:
        return jsonify({'error': 'Senha deve ter ao menos 6 caracteres'}), 400

    try:
        with get_db() as conn:
            conn.execute(
                'INSERT INTO users (name,email,password_hash,role) VALUES (?,?,?,?)',
                (name, email, hash_pw(password), 'patient')
            )
            patient = conn.execute(
                'SELECT id,name,email FROM users WHERE email=?', (email,)
            ).fetchone()
            conn.execute(
                'INSERT OR IGNORE INTO doctor_patients VALUES (?,?)',
                (session['user_id'], patient['id'])
            )
        return jsonify(dict(patient)), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'E-mail já cadastrado'}), 409


@app.route('/api/patients/search', methods=['GET'])
@require_auth
@require_doctor
def search_patient():
    email = (request.args.get('email') or '').strip().lower()
    if not email:
        return jsonify({'error': 'Informe o e-mail'}), 400
    with get_db() as conn:
        user = conn.execute(
            'SELECT id,name,email FROM users WHERE email=? AND role="patient"',
            (email,)
        ).fetchone()
    if not user:
        return jsonify({'error': 'Paciente não encontrado'}), 404
    return jsonify(dict(user))


@app.route('/api/patients/<int:pid>/records', methods=['GET'])
@require_auth
@require_doctor
def get_patient_records(pid):
    with get_db() as conn:
        patient = conn.execute(
            'SELECT id,name,email FROM users WHERE id=? AND role="patient"', (pid,)
        ).fetchone()
        if not patient:
            return jsonify({'error': 'Paciente não encontrado'}), 404
        rows = conn.execute(
            '''SELECT r.id, r.patient_id, r.doctor_id,
                      r.input_data, r.results, r.notes, r.created_at,
                      u.name AS doctor_name
               FROM records r
               LEFT JOIN users u ON r.doctor_id = u.id
               WHERE r.patient_id=?
               ORDER BY r.created_at DESC''',
            (pid,)
        ).fetchall()
    return jsonify({
        'patient': dict(patient),
        'records': [_expand_record(r) for r in rows]
    })


@app.route('/api/patients/<int:pid>/link', methods=['POST'])
@require_auth
@require_doctor
def link_patient(pid):
    with get_db() as conn:
        patient = conn.execute(
            'SELECT id FROM users WHERE id=? AND role="patient"', (pid,)
        ).fetchone()
        if not patient:
            return jsonify({'error': 'Paciente não encontrado'}), 404
        conn.execute(
            'INSERT OR IGNORE INTO doctor_patients VALUES (?,?)',
            (session['user_id'], pid)
        )
    return jsonify({'ok': True})


# ── Helpers ────────────────────────────────────────────────────────────────────

def _expand_record(row):
    d = dict(row)
    try:
        d['input_data'] = json.loads(d['input_data'])
    except Exception:
        d['input_data'] = {}
    try:
        d['results'] = json.loads(d['results'])
    except Exception:
        d['results'] = []
    return d


# ── Serve other static files ───────────────────────────────────────────────────

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)


# ── Run ────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=False)
