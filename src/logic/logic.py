def check_login(login):
    # Имитация базы данных: список пользователей
    users_in_db = ["admin", "manager", "client1"]
    
    # проверяем, есть ли логин в списке
    if login in users_in_db: 
        return "Вход разрешён"
    else:
        return "Ошибка: неверный логин"

def calculate_price(price, has_orders):
    if not has_orders:
        return price * 0.75
    else:
        return price


def check_order(size, quantity, stock):
    if size is None:
        return "Ошибка: выберите размер"
    if quantity <= 0:
        return "Ошибка: количество должно быть > 0"
    if quantity > stock:
        return "Ошибка: недостаточно на складе"
    return "Можно добавить в заказ"