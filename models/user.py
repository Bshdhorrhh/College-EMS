from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, name, email, password_hash, role, department=None, phone=None, created_at=None):
        self.id = id
        self.name = name
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.department = department
        self.phone = phone
        self.created_at = created_at

def get_user_by_id(user_id):
    from app import get_db
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    if row: return User(**dict(row))
    return None

def get_user_by_email(email):
    from app import get_db
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    if row: return User(**dict(row))
    return None

def create_user(name, email, password_hash, role, department=None, phone=None):
    from app import get_db
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (name, email, password_hash, role, department, phone) VALUES (?, ?, ?, ?, ?, ?)",
        (name, email, password_hash, role, department, phone)
    )
    conn.commit()
    return cursor.lastrowid
        
def get_all_users():
    from app import get_db
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, role, department, created_at FROM users")
    return [dict(r) for r in cursor.fetchall()]
