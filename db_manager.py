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


    def add_employee(
    connection, cursor, name, sex, departament, chief, age, hire_date, payment):
    
        sql_command = f"""INSERT INTO employee (name, sex, departament, chief, age, hire_date, payment)
            VALUES 
            (
            "{name}", "{sex}", "{departament}", "{chief}", "{age}", "{hire_date}", "{payment}"
            )
        """
    #     try:
        if True:
            cursor.execute(sql_command)
            connection.commit()
            return True
    #     except Exception as e:
    #         return False

connection = connect()