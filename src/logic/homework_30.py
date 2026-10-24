import psycopg2
import logging

logging.basicConfig(filename='app_errors.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def update_price(product_id, new_price):
    if not isinstance(product_id, int):
        print("Ошибка: product_id должен быть числом")
        return False
    if not isinstance(new_price, (int, float)) or new_price <= 0:
        print("Ошибка: цена должна быть числом > 0")
        return False
        
    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(host="localhost", port=5432, database="audio_db", user="postgres", password="123")
        cursor = conn.cursor()
        cursor.execute("UPDATE products SET price = %s WHERE product_id = %s", (new_price, product_id))

        if cursor.rowcount == 0:
            print(f"Ошибка: товар с ID {product_id} не найден")
            logging.error(f"Попытка обновить цену для несуществующего товара {product_id}")
            return False
            
        conn.commit()
        print(f"Цена для товара {product_id} успешно обновлена на {new_price}")
        return True
    except psycopg2.Error as e:
        if conn: 
            conn.rollback()
        logging.error(f"Ошибка БД при обновлении товара {product_id}: {e}")
        print(f"Ошибка БД: {e}")
        return False
    finally:
        if cursor: 
            cursor.close()
        if conn: 
            conn.close()

if __name__ == "__main__":
    update_price(1, 25000)
    update_price(99999, 25000)