import os

path_picture = "resources/picture.png"
path_test = "resources/watch_1.png"

if os.path.exists(path_picture):
    print(f"Файл {path_picture}: Существует")
else:
    print(f"Файл {path_picture}: НЕ существует")

if os.path.exists(path_test):
    print(f"Файл {path_test}: Существует")
else:
    print(f"Файл {path_test}: НЕ существует")