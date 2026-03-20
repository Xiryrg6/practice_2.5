import threading
import requests
import sqlite3
import time
from tkinter import *
import tkinter as tk
from tkinter import ttk

URL = "https://www.cbr-xml-daily.ru/daily_json.js"
con = sqlite3.connect("resource/base_3.db")
cursor = con.cursor()

response = requests.get(URL)
if response.status_code == 200:
    data = response.json()
    valutes = data['Valute']

    for code, valute in valutes.items():
        name = valute.get('Name', '')
        value = valute.get('Value', 0.0)

        cursor.execute("INSERT INTO currencies (code, name, value) \
                        VALUES (?, ?, ?) \
                        ON CONFLICT(code) DO UPDATE SET \
                            name=excluded.name, \
                            value=excluded.value", 
                        (code, name, value))
    con.commit()
else:
    print("Ошибка при получении данных.")


def show_all_currencies():
    cursor.execute("SELECT code, name, value FROM currencies;")
    currency_list = []

    for code, name, value in cursor:
        currency_list.append(f"{code}: {name} - {value} RUB")

    currency_var = StringVar(value=currency_list)
    listbox_1["listvariable"] = currency_var


def searh_currency():
    code = entry_1.get()
    cursor.execute("SELECT code, name, value FROM currencies WHERE code = ?;", (code,))
    currency = cursor.fetchone()
    if currency:
        label_1["text"] = f"{currency[0]}: {currency[1]} - {currency[2]} RUB"
    else:
        label_1["text"] = "Валюта с этим кодом не найдена."


def show_groups():
    cursor.execute("SELECT * FROM groups;")
    groups = cursor.fetchall()
    groups_list = []
    if not groups:
        groups_list.append("Группы пока не созданы")
    else:
        for gr_id, name in groups:
            groups_list.append(f"Группа: {name}")
            cursor.execute("SELECT c.code, c.name, c.value \
                            FROM currencies c \
                            JOIN group_currencies gc ON c.id = gc.currency_id \
                            WHERE gc.group_id = ?;", (gr_id,))
            for code, name, value in cursor:
                groups_list.append(f"  - {code}: {name} - {value} RUB")
            groups_list.append("")
    groups_var = StringVar(value=groups_list)

    listbox_2["listvariable"] = groups_var


import threading
import time

def group_operation(flag):
    def task():
        time.sleep(2)
        label_3["text"] = ''
        butt_1.config(state="normal")
        butt_2.config(state="normal")

    name = entry_3.get()
    code = entry_4.get()

    cursor.execute("SELECT id FROM groups WHERE group_name = ?;", (name,))
    group_row = cursor.fetchone()
    if not group_row:
        label_3["text"] = "Такой группы нет"
        threading.Thread(target=task).start()
        return
    group_id = group_row[0]

    cursor.execute("SELECT id FROM currencies WHERE code = ?;", (code,))
    currency_row = cursor.fetchone()
    if not currency_row:
        label_3["text"] = "Неверный код валюты."
        threading.Thread(target=task).start()
        return
    currency_id = currency_row[0]

    cursor.execute("SELECT id FROM group_currencies WHERE group_id = ? AND currency_id = ?;",
                    (group_id, currency_id))
    link_row = cursor.fetchone()

    if flag:
        if link_row:
            label_3["text"] = "Эта валюта уже входит в группу."
        else:
            cursor.execute("INSERT INTO group_currencies (group_id, currency_id) VALUES (?, ?);",
                            (group_id, currency_id))
            con.commit()
            label_3["text"] = f"Валюта {code} добавлена в группу '{name}'."
    else:
        if link_row:
            cursor.execute("DELETE FROM group_currencies WHERE group_id = ? AND currency_id = ?;",
                            (group_id, currency_id))
            con.commit()
            label_3["text"] = f"Валюта {code} удалена из группы '{name}'."
        else:
            label_3["text"] = "Данная валюта не входит в эту группу"

    threading.Thread(target=task).start()


def create_group():
    def task():
        time.sleep(2)
        label_2["text"] = ''
        butt_3.config(state="normal")

    name = entry_2.get()
    cursor.execute("SELECT group_name FROM groups WHERE group_name = ?;", (name,))
    group = cursor.fetchone()
    if group:
        if name in group:
            label_2["text"] = "Эта группа уже существует"
            threading.Thread(target=task).start()
            return
    cursor.execute("INSERT INTO groups (group_name) VALUES (?);", (name,))
    label_2["text"] = f"Группа '{name}' создана."
    con.commit()
    
    threading.Thread(target=task).start()


def show_frame(frame):
    frame.tkraise()


root = tk.Tk()
root.title("Курс валют")
root.geometry("400x300")
root.resizable(False, False)
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)


frame_menu = ttk.Frame(root)
ttk.Label(frame_menu, text="Выберите действие", font=("", 14)).pack(pady=10)
ttk.Button(frame_menu, text="Посмотреть валюты", width=30, command=lambda:[show_frame(frame_show_all_currencies), show_all_currencies()]).pack(pady=3)
ttk.Button(frame_menu, text="Посмотреть группы", width=30, command=lambda:[show_frame(frame_show_groups), show_groups()]).pack(pady=3)
ttk.Button(frame_menu, text="Выход", width=30, command=lambda:root.destroy()).pack(pady=3)


frame_show_all_currencies = ttk.Frame(root)
frame_butt_1 = ttk.Frame(frame_show_all_currencies)

frame_butt_1.pack(fill='x')
frame_butt_1.columnconfigure(0, weight=1)
frame_butt_1.columnconfigure(1, weight=1)

ttk.Button(frame_butt_1, text="Обратно", command=lambda:show_frame(frame_menu)).grid(column=0, row=1, sticky="w")
ttk.Button(frame_butt_1, text="Просмотреть валюту по коду", command=lambda:[show_frame(frame_view_currency), entry_1.delete(0, END), label_1.config(text='')]).grid(column=1, row=1, sticky='e')

ttk.Label(frame_show_all_currencies, text="Текущие обменные курсы всех валют", font=("", 14)).pack(pady=10)
listbox_1 = Listbox(frame_show_all_currencies)
listbox_1.pack(side=LEFT, fill=BOTH, expand=1)
scrollbar_1 = ttk.Scrollbar(frame_show_all_currencies, orient="vertical", command=listbox_1.yview)
scrollbar_1.pack(side="right", fill='y')
listbox_1["yscrollcommand"]=scrollbar_1.set


frame_view_currency = ttk.Frame(root)
ttk.Button(frame_view_currency, text="Обратно", command=lambda:[show_frame(frame_show_all_currencies), show_all_currencies()]).pack(anchor='nw')
ttk.Label(frame_view_currency, text="Введите код валюты", font=("", 12)).pack(pady=10)
entry_1 = ttk.Entry(frame_view_currency)
entry_1.pack(pady=10)
ttk.Button(frame_view_currency, text="Поиск", command=lambda:searh_currency()).pack(pady=5)
label_1 = ttk.Label(frame_view_currency)
label_1.pack(pady=10)


frame_show_groups = ttk.Frame(root)
frame_butt_2 = ttk.Frame(frame_show_groups)

frame_butt_2.pack(fill='x')
frame_butt_2.columnconfigure(0, weight=1)
frame_butt_2.columnconfigure(1, weight=1)
frame_butt_2.columnconfigure(2, weight=1)

ttk.Button(frame_butt_2, text="Обратно", command=lambda:show_frame(frame_menu)).grid(column=0, row=0, sticky='w')
ttk.Button(frame_butt_2, text="Изменить группу", command=lambda: [show_frame(frame_add_or_delet_currency), entry_3.delete(0, END), entry_4.delete(0, END)]).grid(column=1, row=0)
ttk.Button(frame_butt_2, text="Создать группу валют", command=lambda:[show_frame(frame_create_group), entry_2.delete(0, END)]).grid(column=2, row=0, sticky='e')

ttk.Label(frame_show_groups, text="Группы", font=("", 14)).pack(pady=10)
listbox_2 = Listbox(frame_show_groups)
listbox_2.pack(side=LEFT, fill=BOTH, expand=1)
scrollbar_2 = ttk.Scrollbar(frame_show_groups, orient="vertical", command=listbox_2.yview)
scrollbar_2.pack(side="right", fill='y')
listbox_2["yscrollcommand"]=scrollbar_2.set


frame_add_or_delet_currency = ttk.Frame()
ttk.Button(frame_add_or_delet_currency, text="Обратно", command=lambda:[show_frame(frame_show_groups), show_groups()]).pack(anchor='nw')
ttk.Label(frame_add_or_delet_currency, text="Введите группу", font=("", 12)).pack()
entry_3 = ttk.Entry(frame_add_or_delet_currency)
entry_3.pack(pady=10)
ttk.Label(frame_add_or_delet_currency, text="Введите номер валюты", font=("", 12)).pack()
entry_4 = ttk.Entry(frame_add_or_delet_currency)
entry_4.pack(pady=10)

frame_butt_3 = ttk.Frame(frame_add_or_delet_currency)
frame_butt_3.pack(fill="x", pady=10)
frame_butt_3.columnconfigure(0, weight=1)
frame_butt_3.columnconfigure(1, weight=1)

butt_1 = tk.Button(frame_butt_3, text="Добавить", bg="green", width=15, command=lambda: [butt_1.config(state="disabled"), group_operation(True)])
butt_1.grid(column=0, row=0)
butt_2 = tk.Button(frame_butt_3, text="Удалить", bg="red", width=15, command=lambda: [butt_2.config(state="disabled"), group_operation(False)])
butt_2.grid(column=1, row=0)
label_3 = ttk.Label(frame_add_or_delet_currency)
label_3.pack()


frame_create_group = ttk.Frame(root)
ttk.Button(frame_create_group, text="Обратно", command=lambda:[show_frame(frame_show_groups), show_groups()]).pack(anchor='nw')
ttk.Label(frame_create_group, text="Введите название группы", font=("", 12)).pack(pady=10)
entry_2 = ttk.Entry(frame_create_group)
entry_2.pack(pady=10)
butt_3 = ttk.Button(frame_create_group, text="Создать", command=lambda:[butt_3.config(state="disabled") ,create_group()])
butt_3.pack(pady=5)
label_2 = ttk.Label(frame_create_group)
label_2.pack(pady=10)


frames = [frame_menu,
           frame_show_all_currencies,
           frame_view_currency,
           frame_show_groups,
           frame_add_or_delet_currency,
           frame_create_group]
for frame in frames:
    frame.grid(row=0, column=0, sticky='nsew')

show_frame(frame_menu)
root.mainloop()