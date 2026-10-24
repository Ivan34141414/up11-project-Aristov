import psycopg2

def calculate_price(product_id, base_price):
    if not isinstance(product_id, int):
        print("Ошибка: product_id должен быть числом")
        return None

    if not isinstance(base_price, (int, float)):
        print("Ошибка: base_price должен быть числом")
        return None

    if base_price <= 0:
        print("Ошибка: цена должна быть > 0")
        return None

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

        cursor.execute("SELECT name FROM products WHERE product_id = %s;", (product_id,))
        name_result = cursor.fetchone()
        if name_result is None:
            print("Ошибка: товар не найден")
            return None
        product_name = name_result[0]
        
        query = """
            SELECT COUNT(*) 
            FROM order_items oi 
            JOIN orders o ON oi.order_id = o.order_id 
            WHERE oi.product_id = %s 
            AND o.order_date >= CURRENT_DATE - INTERVAL '1 month';
        """
        cursor.execute(query, (product_id,))
        orders_count = cursor.fetchone()[0]
        
        base_price = float(base_price)
        
        if orders_count == 0:
            discount_size = base_price * 0.25
            final_price = base_price * 0.75
        else:
            discount_size = 0.0
            final_price = base_price

        print(f"Товар: {product_name} | Скидка: {discount_size} руб. | Итог: {final_price} руб.")

        return (final_price, discount_size)
        
    except psycopg2.Error as e:
        print(f"Ошибка БД: {e}")
        return None
    except Exception as e:
        print(f"Неизвестная ошибка: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    calculate_price("abc", 1000)
    calculate_price(1, "abc")
    calculate_price(1, -100)
    calculate_price(1, None)
    calculate_price(99999, 1000)