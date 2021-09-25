from sqlite3 import connect as sqlite3_connect, Error


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3_connect(db_file)
        # print(sqlite3.version)
    except Error as e:
        print(e)

    return conn


def create_table(conn, create_table_sql):
    try:
        cursor = conn.cursor()
        cursor.execute(create_table_sql)

    except Error as e:
        print(e)
    return None

def connect(
    db_file='./employee.db'):
    
    sql_create_employee = """ 
    CREATE TABLE IF NOT EXISTS employee 
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name text,
        sex text,
        departament text,
        chief text,
        age integer,
        hire_date text,
        finish_date text,
        payment integer,
        leave_reason text
    );"""



    conn = create_connection(db_file)

    if conn is not None:
        create_table(conn, sql_create_employee)
        conn.commit()


    return conn


connection = connect()