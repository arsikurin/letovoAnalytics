# from functools import wraps


def update_data(
        chat_id,
        student_id=None,
        mail_address=None,
        mail_password=None,
        analytics_login=None,
        analytics_password=None,
        token=None
):
    pas = '"tmp": ""'
    si = f'"student_id": {student_id}'
    ma = f'"mail_address": "{mail_address}"'
    mp = f'"mail_password": "{mail_password}"'
    al = f'"analytics_login": "{analytics_login}"'
    ap = f'"analytics_password": "{analytics_password}"'
    t = f'"token": "{token}"'
    request_payload = '''
        {''' + \
                      f'{si if student_id else pas},' + \
                      f'{ma if mail_address else pas},' + \
                      f'{mp if mail_password else pas},' + \
                      f'{al if analytics_login else pas},' + \
                      f'{ap if analytics_password else pas},' + \
                      f'{t if token else pas}' + \
                      '''}
                  '''
    ref = db.reference(f"/users/{chat_id}")
    ref.child("data").update(json.loads(request_payload))


def init_user(
        chat_id,
        student_id=None,
        mail_address=None,
        mail_password=None,
        analytics_login=None,
        analytics_password=None,
        token=None
):
    pas = '"tmp": ""'
    st = f'"student_id": {student_id}'
    ma = f'"mail_address": "{mail_address}"'
    mp = f'"mail_password": "{mail_password}"'
    al = f'"analytics_login": "{analytics_login}"'
    ap = f'"analytics_password": "{analytics_password}"'
    t = f'"token": "{token}"'
    request_payload = '''
    {
        "data": {''' + \
                      f'{st if student_id else pas},' + \
                      f'{ma if mail_address else pas},' + \
                      f'{mp if mail_password else pas},' + \
                      f'{al if analytics_login else pas},' + \
                      f'{ap if analytics_password else pas},' + \
                      f'{t if token else pas}' + \
                      '''},
                      "preferences": {
                          "lang": "en"
                      }
                  }
                  '''
    ref = db.reference(f"/users/{chat_id}")
    ref.update(json.loads(request_payload))


def get_users() -> KeysView:
    ref = db.reference("/users")
    return ref.get().keys()


# -----------------------------------------------SQL funcs--------------------------------------------------------------
# def create_table(conn: sqlite3.Connection, c: sqlite3.Cursor) -> None:
#     with conn:
#         c.execute(
#             """CREATE TABLE users (
#                 chat_id INTEGER PRIMARY KEY,
#                 student_id INTEGER,
#                 mail_address VARCHAR (255),
#                 mail_password VARCHAR (255),
#                 analytics_login VARCHAR (255),
#                 analytics_password VARCHAR (255),
#                 token TEXT
#                 )""")


# def clear_db(conn: sqlite3.Connection, c: sqlite3.Cursor) -> None:
#     with conn:
#         c.execute("DELETE FROM users")


# def add_column_to_db(conn: sqlite3.Connection, c: sqlite3.Cursor) -> None:
#     with conn:
#         c.execute("ALTER TABLE users ADD COLUMN name TEXT")


def init_user_sql(chat_id: int, conn: sqlite3.Connection, c: sqlite3.Cursor) -> None:
    with conn:
        c.execute(
            """INSERT INTO users VALUES 
            (:chat_id, :student_id, :mail_address, :mail_password, :analytics_login, :analytics_password, :token)""",
            {"mail_address": None, "mail_password": None, "analytics_password": None, "analytics_login": None,
             "token": None, "student_id": None, "chat_id": chat_id})


def delete_user_sql(chat_id: int, conn: sqlite3.Connection, c: sqlite3.Cursor) -> None:
    with conn:
        c.execute("DELETE FROM users WHERE chat_id = :chat_id", {"chat_id": chat_id})


# --------------------- Setters
def set_student_id_sql(student_id: int, chat_id: int, conn: sqlite3.Connection, c: sqlite3.Cursor) -> None:
    with conn:
        c.execute("UPDATE users SET student_id = :student_id WHERE chat_id = :chat_id",
                  {"student_id": student_id, "chat_id": chat_id})


def set_mail_address_sql(mail_address: str, chat_id: int, conn: sqlite3.Connection, c: sqlite3.Cursor) -> None:
    with conn:
        c.execute("UPDATE users SET mail_address = :mail_address WHERE chat_id = :chat_id",
                  {"mail_address": mail_address, "chat_id": chat_id})


def set_mail_password_sql(mail_password: str, chat_id: int, conn: sqlite3.Connection, c: sqlite3.Cursor) -> None:
    with conn:
        c.execute("UPDATE users SET mail_password = :mail_password WHERE chat_id = :chat_id",
                  {"mail_password": mail_password, "chat_id": chat_id})


def set_analytics_login(analytics_login: str, chat_id: int, conn: sqlite3.Connection, c: sqlite3.Cursor) -> None:
    with conn:
        c.execute("UPDATE users SET analytics_login = :analytics_login WHERE chat_id = :chat_id",
                  {"analytics_login": analytics_login, "chat_id": chat_id})


def set_analytics_password_sql(analytics_password: str, chat_id: int, conn: sqlite3.Connection,
                               c: sqlite3.Cursor) -> None:
    with conn:
        c.execute("UPDATE users SET analytics_password = :analytics_password WHERE chat_id = :chat_id",
                  {"analytics_password": analytics_password, "chat_id": chat_id})


def set_token_sql(token: str, chat_id: int, conn: sqlite3.Connection, c: sqlite3.Cursor) -> None:
    with conn:
        c.execute("UPDATE users SET token = :token WHERE chat_id = :chat_id",
                  {"token": token, "chat_id": chat_id})


# --------------------- Getters
def get_chat_id_sql(chat_id: int, conn: sqlite3.Connection, c: sqlite3.Cursor) -> int:
    with conn:
        c.execute("SELECT chat_id FROM users WHERE chat_id = :chat_id", {"chat_id": chat_id})
        return c.fetchone()[0]


def get_student_id_sql(chat_id: int, conn: sqlite3.Connection, c: sqlite3.Cursor) -> int:
    with conn:
        c.execute("SELECT student_id FROM users WHERE chat_id = :chat_id", {"chat_id": chat_id})
        return c.fetchone()[0]


def get_mail_address_sql(chat_id: int, conn: sqlite3.Connection, c: sqlite3.Cursor) -> str:
    with conn:
        c.execute("SELECT mail_address FROM users WHERE chat_id = :chat_id", {"chat_id": chat_id})
        return c.fetchone()[0]


def get_mail_password_sql(chat_id: int, conn: sqlite3.Connection, c: sqlite3.Cursor) -> str:
    with conn:
        c.execute("SELECT mail_password FROM users WHERE chat_id = :chat_id", {"chat_id": chat_id})
        return c.fetchone()[0]


def get_analytics_login_sql(chat_id: int, conn: sqlite3.Connection, c: sqlite3.Cursor) -> str:
    with conn:
        c.execute("SELECT analytics_login FROM users WHERE chat_id = :chat_id", {"chat_id": chat_id})
        return c.fetchone()[0]


def get_analytics_password_sql(chat_id: int, conn: sqlite3.Connection, c: sqlite3.Cursor) -> str:
    with conn:
        c.execute("SELECT analytics_password FROM users WHERE chat_id = :chat_id", {"chat_id": chat_id})
        return c.fetchone()[0]


def get_token_sql(chat_id: int, conn: sqlite3.Connection, c: sqlite3.Cursor) -> str:
    with conn:
        c.execute("SELECT token FROM users WHERE chat_id = :chat_id", {"chat_id": chat_id})
        return c.fetchone()[0]

# Update some data in realtime db
# ref = db.reference("/users")
# users = ref.get()
# for key, value in users.items():
#     ref.child(key).update({"data/Name": "Arseny"})

# Realtime db initing
# import firebase_admin
# from firebase_admin import credentials, db
# cred_obj = credentials.Certificate("fbAdminConfig.json")
# default_app = firebase_admin.initialize_app(cred_obj, {
#     'databaseURL': "https://authtest-3fcb2-default-rtdb.europe-west1.firebasedatabase.app/"
# })
