from db import db
from flask import session, redirect
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.sql import text
import secrets

def login(username, password):
    sql = text("SELECT user_id, password FROM users WHERE username=:username")
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()
    if not user:
        return False
    else:
        if check_password_hash(user.password, password):
            sql = text("SELECT * FROM user_roles WHERE user_id=:user_id")
            result = db.session.execute(sql, {"user_id":user.user_id})
            role = result.fetchone()

            if not role:
                create_role(user)
                try:
                    result = db.session.execute(sql, {"user_id":user.user_id})
                    role = result.fetchone()
                    session['user_type'] = role.user_type
                except:
                    return False
            else:
                session['user_type'] = role.user_type
                
            session["user_id"] = user.user_id
            session["username"] = username
            session["csrf_token"] = secrets.token_hex(16)
            return True
        else:
            return False

def logout():
    del session["user_id"]

def register(username, password):
    hash_value = generate_password_hash(password)
    sql = text("INSERT INTO users (username, password, created_at) VALUES (:username, :password, NOW())")
    db.session.execute(sql, {"username":username, "password":hash_value})
    try:
        db.session.commit()
    except:
        return False
    return True

def user_id():
    return session.get("user_id",0)

def is_logged():
    return session.get("username", 0)

def user_type():
    return session.get('user_type', 0)

def create_role(user):
    sql = text("INSERT INTO user_roles (user_id, user_type) VALUES(:user_id,:user_type)")
    db.session.execute(sql, {"user_id":user.user_id, "user_type":100})
    try:
        db.session.commit()
    except:
        return False
    
def get_users():
    id = user_id()
    utype = user_type()
    print(utype)
    sql = text("SELECT U.user_id, U.username, P.alias, R.user_type, U.created_at FROM users U JOIN user_roles R ON U.user_id=R.user_id JOIN permission_levels P ON R.user_type=P.user_type WHERE NOT R.user_id=:user_id AND R.user_type <=:user_type")
    if utype != 300 and utype != 200:
        return False
    else:
        result = db.session.execute(sql, {'user_id': id, 'user_type': utype})
        return result.fetchall()

def role_options(type):
    utype = user_type()
    sql = text("SELECT user_type, alias FROM permission_levels WHERE NOT user_type=:type")
    if utype != 300 and utype != 200:
        return False
    else:
        result = db.session.execute(sql, {'type': type})
        return result.fetchall()

def get_user(user_id):
    utype = user_type()
    sql = text("SELECT U.user_id, U.username, R.user_type, T.alias, U.created_at FROM users U JOIN user_roles R ON U.user_id=R.user_id JOIN permission_levels T ON R.user_type=T.user_type WHERE U.user_id=:user_id")
    if utype != 300 and utype != 200:
        return False
    else:
        result = db.session.execute(sql, {"user_id": user_id})
        return result.fetchone()
    
def delete_user(user_id):
    sql = text("DELETE FROM users WHERE user_id=:user_id")
    db.session.execute(sql, {"user_id": user_id})
    try:
        db.session.commit()
    except:
        return False
    return True

def modify_role(role, user_id):
    sql = text("UPDATE user_roles SET user_type=:user_type WHERE user_id=:user_id")
    db.session.execute(sql, {'user_type': role, 'user_id':user_id})
    try:
        db.session.commit()
    except:
        return False
    return True