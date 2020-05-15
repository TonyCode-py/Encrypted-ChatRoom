'''
Store the user information to the database
@auther: Tony Yang

'''
import sqlite3

def insert_to_db(cur, id, username, password):
    try:
        cur.execute(f"INSERT INTO users VALUES({id}, '{username}', '{password}')")
        print(f"success create user {username}")
    except:
        print(f"fail to create user {username}")


def get_next_id(cur):
    cur.execute(f"SELECT max(id) from users")
    next_id = cur.fetchall()[0][0] + 1
    return next_id

def check_username(cur, username):
    #check if the username exist
    cur.execute("SELECT username from users")
    a = cur.fetchall()
    b = []
    for i in a:
        b.append(i[0])
    if username in b:
        return True
    else:
        return False
    
def store_new_info(username, passward, path):
    #return True if success register

    cxn = sqlite3.connect(path)
    cur = cxn.cursor()
    if(check_username(cur, username)):
        cur.close()
        cxn.commit()
        cxn.close()
        return False
    else:
        current_id = get_next_id(cur)
        insert_to_db(cur, current_id, username, passward)
        cur.close()
        cxn.commit()
        cxn.close()
        return True

def show_all_user_info(cur):
    cur.execute("SELECT * from users")
    uinfo = cur.fetchall()
    for i in uinfo:
        print(i)

def check_login_info(username, password, path):
    cxn = sqlite3.connect(path)
    cur = cxn.cursor()
    cur.execute(f"select password from users where username='{username}'")
    a = cur.fetchall()
    if len(a) == 0:
        return False
    
    if a[0][0] == password:
        return True
    else:
        return False

