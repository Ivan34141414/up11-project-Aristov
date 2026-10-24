import psycopg2

def add_product(name, price, category_id):
    if not name or not isinstance(name, str):
        print("Ошибка: имя не может быть пустым")
        return False
    if not isinstance(price, (int, float)) or price <= 0:
        print("Ошибка: цена должна быть числом > 0")
        return False
    if not isinstance(category_id, int):
        print("Ошибка: category_id должен быть числом")
        return False

    conn = None
    cursor = None

    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="audio_db",
            user="postgres",
            password="123"
        )
        cursor = conn.cursor()
        
        query = "INSERT INTO products (name, price, category_id) VALUES (%s, %s, %s);"
        cursor.execute(query, (name, price, category_id))
        
        conn.commit()
        print(f"Товар '{name}' успешно добавлен!")
        return True

    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        print(f"Ошибка БД: {e}")
        return False
    except Exception as e:
        print(f"Неизвестная ошибка: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    add_product("", 1000, 1)
    add_product("Часы", -100, 1)
    add_product("Часы", 1000, 99999)
    add_product("Тестовые наушники", 1000, 1)