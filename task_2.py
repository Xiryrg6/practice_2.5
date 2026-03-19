import sqlite3
import time
import threading
from tkinter import *
import tkinter as tk
from tkinter import ttk

con = sqlite3.connect("resource/base_2.db")
cursor = con.cursor()


def sell():
    cocktail = combobox_1.get()
    for data_1 in cocktails:
        if data_1[1] == cocktail:
            cursor.execute("SELECT * FROM cocktail_ingredients WHERE cocktail_id = ?", (data_1[0],))
            cocktail_ingredients = cursor.fetchall()
            for data_2 in cocktail_ingredients:
                ingredient_id = data_2[1]
                required_qty = data_2[2]

                cursor.execute("SELECT * FROM ingredients WHERE id = ?", (ingredient_id,))
                result = cursor.fetchone()
                ingredient_name = result[1]
                stock_qty = result[3]

                if stock_qty < required_qty:
                    label_3["text"] = f"Недостаточно ингредиента: {ingredient_name}: {int(required_qty - stock_qty)} шт."
                    break
                else:
                    cursor.execute("UPDATE ingredients SET stock_quantity = stock_quantity - ? WHERE id = ?",
                                    (required_qty, ingredient_id))
                    label_3["text"] = "Продажа совершена успешно"
            break
    con.commit()

    def task():
        time.sleep(2)
        label_3["text"] = ''
        butt_1.config(state="normal")
    threading.Thread(target=task).start()


def update_listbox():
    cursor.execute("SELECT * FROM ingredients")
    result = cursor.fetchall()
    list_ingredient = []
    found = False
    for ingredient in result:
        found = True
        list_ingredient.append(f"{ingredient[1]}; Креп-ть: {ingredient[2]}; Кол-во: {ingredient[3]}")
    if not found:
        list_ingredient.append("Ничего не найденно")
    
    var_ingredients = StringVar(value=list_ingredient)
    listbox_1["listvariable"] = var_ingredients


def replenishment():
    name = combobox_2.get()
    quantity = spinbox_1.get()
    cursor.execute("UPDATE ingredients SET stock_quantity = stock_quantity + ? WHERE name=?;", (quantity, name))
    con.commit()

    label_4["text"] = f"{name} пополнен на {quantity}"
    def task():
        time.sleep(1.5)
        label_4["text"] = ''
        butt_2.config(state="normal")
    threading.Thread(target=task).start()


def selected(event):
    selection = combobox_1.get()
    for data in average_strength:
        if data[0] == selection:
            label_1["text"] = f"Крепость: {data[1]:.1f}"
            break
    for data in cocktails:
        if data[1] == selection:
            label_2["text"] = f"Цена: {data[2]}р"
            break


def show_frame(frame):
    frame.tkraise()


root = tk.Tk()
root.title("I love drink")
root.geometry("500x200")
root.resizable(False, False)
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)


cursor.execute("SELECT name FROM ingredients")
ingredients_name = []
for name in cursor:
    ingredients_name.append(name[0])
var_ingredients_name = StringVar(value=ingredients_name[0])

cursor.execute("SELECT * FROM cocktails")
cocktails = cursor.fetchall()
cocktail_name = []
for name in cocktails:
    cocktail_name.append(f"{name[1]}")
var_cocktail_name = StringVar(value=cocktail_name[0])

cursor.execute(
    "SELECT \
        c.name, \
        SUM(i.alcohol_strength * ci.quantity) / SUM(ci.quantity) AS average_strength \
    FROM \
        cocktails c \
    JOIN \
        cocktail_ingredients ci ON c.id = ci.cocktail_id \
    JOIN \
        ingredients i ON ci.ingredient_id = i.id \
    GROUP BY \
        c.id, c.name;")
average_strength = cursor.fetchall()

spinbox_var = StringVar(value=10)

frame_menu = ttk.Frame(root)
ttk.Label(frame_menu, text="Выберите действие", font=("", 12)).pack(pady=10)
ttk.Button(frame_menu, text="Продажа", width=30, command=lambda: show_frame(frame_sell)).pack(pady=3)
ttk.Button(frame_menu, text="Склад", width=30, command=lambda: [show_frame(frame_warehouse), update_listbox()]).pack(pady=3)
ttk.Button(frame_menu, text="Выход", width=30, command=lambda: root.destroy()).pack(pady=3)


frame_sell = ttk.Frame(root)
ttk.Button(frame_sell, text="Обратно", command=lambda:show_frame(frame_menu)).pack(anchor='nw')
ttk.Label(frame_sell, text="Продажа", font=("", 12)).pack(pady=10)

frame_butt_1 = ttk.Frame(frame_sell)
frame_butt_1.pack(fill='x', padx=30)
frame_butt_1.columnconfigure(0, weight=1)
frame_butt_1.columnconfigure(1, weight=1)
frame_butt_1.columnconfigure(2, weight=1)
frame_butt_1.columnconfigure(3, weight=1)

label_1 = ttk.Label(frame_butt_1)
label_1.grid(column=0, row=0)
combobox_1 = ttk.Combobox(frame_butt_1, width=30, textvariable=var_cocktail_name, values=cocktail_name, state="readonly")
combobox_1.grid(column=1, row=0)
combobox_1.bind("<<ComboboxSelected>>", selected)
label_2 = ttk.Label(frame_butt_1)
label_2.grid(column=2, row=0)
butt_1 = ttk.Button(frame_butt_1, text="Продать", command=lambda: [butt_1.config(state="disabled"), sell()])
butt_1.grid(column=3, row=0)
selected(0)

label_3 = ttk.Label(frame_sell)
label_3.pack(pady=10)


frame_warehouse = ttk.Frame(root)
frame_butt_2 = tk.Frame(frame_warehouse)
frame_butt_2.pack(fill="x")
frame_butt_2.columnconfigure(0, weight=1)
frame_butt_2.columnconfigure(1, weight=1)

ttk.Button(frame_butt_2, text="Обратно", command=lambda:show_frame(frame_menu)).grid(column=0, row=0, sticky='nw')
ttk.Button(frame_butt_2, text="Пополнение запасов", command=lambda:show_frame(frame_replenishment)).grid(column=1, row=0, sticky='ne')

ttk.Label(frame_warehouse, text="Склад", font=("", 12)).pack(pady=10)
listbox_1 = Listbox(frame_warehouse)
listbox_1.pack(side="left", fill=BOTH, expand=1)
scrollbar_1 = ttk.Scrollbar(frame_warehouse, orient="vertical", command=listbox_1.yview)
scrollbar_1.pack(side="right", fill='y')
listbox_1["yscrollcommand"]=scrollbar_1.set


frame_replenishment = ttk.Frame(root)
ttk.Button(frame_replenishment, text="Обратно", command=lambda:[show_frame(frame_warehouse), update_listbox()]).pack(anchor='nw')
ttk.Label(frame_replenishment, text="Пополнение запасов", font=("", 12)).pack(pady=10)

frame_butt_3 = ttk.Frame(frame_replenishment)
frame_butt_3.pack(fill='x', padx=80)
frame_butt_3.columnconfigure(0, weight=1)
frame_butt_3.columnconfigure(1, weight=1)
frame_butt_3.columnconfigure(2, weight=1)

combobox_2 = ttk.Combobox(frame_butt_3, width=30, textvariable=var_ingredients_name, values=ingredients_name, state="readonly")
combobox_2.grid(column=0, row=0)
spinbox_1 = ttk.Spinbox(frame_butt_3, width=5, from_=10.0, to=1000.0, increment=10, textvariable=spinbox_var, state="readonly")
spinbox_1.grid(column=1, row=0)
butt_2 = ttk.Button(frame_butt_3, text="Добавить", command=lambda: [butt_2.config(state="disabled"), replenishment()])
butt_2.grid(column=2, row=0)
label_4 = ttk.Label(frame_replenishment)
label_4.pack(pady=10)


frames = [frame_menu,
          frame_sell,
          frame_warehouse,
          frame_replenishment]
for frame in frames:
    frame.grid(row=0, column=0, sticky='nsew')

show_frame(frame_menu)
root.mainloop()