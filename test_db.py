from database import Database

db = Database()
conn = db.get_connection()

if conn:
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM products;")
    result = cursor.fetchone()
    print(f"Количество товаров: {result[0]}")
    cursor.close()
    db.release_connection(conn)
else:
    print("Не удалось получить соединение.")

db.close_all()