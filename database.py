import psycopg2
from psycopg2 import pool

class Database:
    def __init__(self):
        self.connection_pool = None
        try:
            self.connection_pool = pool.SimpleConnectionPool(
                1, 5,
                host="localhost", port=5432, database="audio_db",
                user="postgres", password="123"
            )
        except Exception as e:
            print(f"Ошибка БД: {e}")
            self.connection_pool = None

    def get_connection(self):
        if self.connection_pool:
            return self.connection_pool.getconn()
        return None

    def release_connection(self, conn):
        if self.connection_pool and conn:
            self.connection_pool.putconn(conn)

    def close_all(self):
        if self.connection_pool:
            self.connection_pool.closeall()

    def get_products(self):
        conn = self.get_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            query = """
                SELECT 
                    p.product_id, 
                    p.name, 
                    c.name AS category_name, 
                    p.manufacturer, 
                    p.composition, 
                    p.price, 
                    p.image_path,
                    COALESCE(SUM(si.quantity), 0) AS total_quantity
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.category_id
                LEFT JOIN stock_items si ON p.product_id = si.product_id
                GROUP BY p.product_id, c.name, p.name, p.manufacturer, p.composition, p.price, p.image_path
                ORDER BY p.product_id;
            """
            cursor.execute(query)
            products = cursor.fetchall()
            cursor.close()
            return products
        except psycopg2.Error as e:
            print(f"Ошибка запроса: {e}")
            return []
        finally:
            self.release_connection(conn)

    def execute_query(self, sql, params=None):
        conn = self.get_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            result = cursor.fetchall()
            cursor.close()
            return result
        except psycopg2.Error as e:
            print(f"Ошибка запроса: {e}")
            return []
        finally:
            self.release_connection(conn)

    def execute_update(self, sql, params=None):
        conn = self.get_connection()
        if not conn:
            return False
        try:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
            cursor.close()
            return True
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            print(f"Ошибка обновления: {e}")
            return False
        finally:
            self.release_connection(conn)