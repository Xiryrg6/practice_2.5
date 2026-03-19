import sqlite3
from tkinter import *
import tkinter as tk
from tkinter import ttk

con = sqlite3.connect("resource/base_1.db")
cursor = con.cursor()


def operation_on_student(flag):
    data = get_a_student(entry_1)
    result = data[0]

    if result != 0:
        first_name, last_name, middle_name, group_name, student_id = data[1], data[2], data[3], data[4], data[5]

        if flag:
            if result:
                label_1["text"]= "Такой студент уже есть"
            else:
                cursor.execute("INSERT INTO students (first_name, last_name, middle_name, group_name) VALUES (?, ?, ?, ?)",
                                (first_name, last_name, middle_name, group_name))
                con.commit()
                label_1["text"] = "Студент добавлен"
        else:
            if not result:
                label_1["text"] = "Такого студента нет"
            else:
                cursor.execute("DELETE FROM students WHERE first_name=? AND last_name=? AND middle_name=? AND group_name=?",
                                (first_name, last_name, middle_name, group_name))
                con.commit()
                cursor.execute("DELETE FROM grades WHERE student_id=?", (student_id))
                con.commit()
                label_1["text"] = "Студент удалён"
    else:
        label_1["text"] = "Неправильный ввод"


def edit_student(option):
    data = get_a_student(entry_2)
    result = data[0]

    if result != 0:
        first_name, last_name, middle_name, group_name = data[1], data[2], data[3], data[4]

        if not result:
            label_2["text"] = "Такого студента нет"
            return
        new_value = entry_3.get()
        if new_value != "":
            match option:
                case "first_name":
                    cursor.execute(
                        "UPDATE students SET first_name=? WHERE first_name=? AND last_name=? AND middle_name=? AND group_name=?",
                        (new_value, first_name, last_name, middle_name, group_name)
                    )
                case "last_name":
                    cursor.execute(
                        "UPDATE students SET last_name=? WHERE first_name=? AND last_name=? AND middle_name=? AND group_name=?",
                        (new_value, first_name, last_name, middle_name, group_name)
                    )
                case "middle_name":
                    cursor.execute(
                        "UPDATE students SET middle_name=? WHERE first_name=? AND last_name=? AND middle_name=? AND group_name=?",
                        (new_value, first_name, last_name, middle_name, group_name)
                    )
                case "group_name":
                    cursor.execute(
                        "UPDATE students SET group_name=? WHERE first_name=? AND last_name=? AND middle_name=? AND group_name=?",
                        (new_value, first_name, last_name, middle_name, group_name)
                    )
            con.commit()
            label_2["text"] = "Данные обновлены"
        else:
            label_2["text"] = "Замена не может быть пустой"
    else:
        label_2["text"] = "Неправильный ввод"


def show_all_students(flag):
    cursor.execute("SELECT * FROM students")
    result = cursor.fetchall()
    cursor.execute("SELECT \
                    AVG(grades.grade) AS average_grade \
                    FROM \
                        students \
                    LEFT JOIN \
                        grades ON students.id = grades.student_id \
                    GROUP BY \
                        students.id, students.first_name, students.last_name")
    list_data = []
    found = False

    for student in result:
        gpa = cursor.fetchmany(1)[0]
        person = f"{student[1]} {student[2]} {student[3]} {student[4]}"

        if flag:
            if person != entry_4.get(): continue
        found = True
        list_data.append(f"ФИО: {student[1]} {student[2]} {student[3]}; Группа: {student[4]}; Ср.Балл: {gpa}")
        if flag: break
    if not found:
        list_data.append("Ничего не найденно")

    var_data = StringVar(value=list_data)
    listbox_1["listvariable"] = var_data


def show_group_average(flag):
    cursor.execute("SELECT \
                        students.group_name, \
                        AVG(grades.grade) AS average_group_grade \
                    FROM \
                        students \
                    JOIN \
                        grades ON students.id = grades.student_id \
                    GROUP BY \
                        students.group_name")

    rows = cursor.fetchall()
    list_data = []
    found = False
    for group_name, avg_grade in rows:
        if flag:
            if group_name != entry_5.get(): continue
        found = True
        list_data.append(f"Группа: {group_name}; Средний балл: {avg_grade:.2f}")
        if flag: break
    if not found:
        list_data.append("Ничего не найденно")
    var_data = StringVar(value=list_data)
    listbox_2["listvariable"] = var_data
    


def get_a_student(entry):
    person = entry.get().split()
    if len(person) == 4:
        first_name, last_name, middle_name, group_name = person
        cursor.execute("SELECT * FROM students WHERE first_name=? AND last_name=? AND middle_name=? AND group_name=?",
                        (first_name, last_name, middle_name, group_name))
        student = cursor.fetchone()
        cursor.execute("SELECT id FROM students WHERE first_name=? AND last_name=? AND group_name=?",
                        (first_name, last_name, group_name))
        student_id = cursor.fetchone()
        result = [student, first_name, last_name, middle_name, group_name, student_id]
        return result
    else:
        return [0]

def show_frame(frame):
    frame.tkraise()


root = tk.Tk()
root.title("Студенты")
root.geometry("420x255")
root.resizable(False, False)
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)


frame_menu = ttk.Frame(root)
ttk.Label(frame_menu, text="Выберите действие", font=("", 12)).pack(pady=10)
ttk.Button(frame_menu, text="Добавить/удалить студента", width=30, command=lambda: show_frame(frame_operation_on_student)).pack(pady=3)
ttk.Button(frame_menu, text="Изменить студента", width=30, command=lambda: show_frame(frame_edit_student)).pack(pady=3)
ttk.Button(frame_menu, text="Просмотр студентов", width=30, command=lambda: [show_frame(frame_show_all_students), show_all_students(False), entry_4.delete(0, last="end")]).pack(pady=3)
ttk.Button(frame_menu, text="Просмотр групп", width=30, command=lambda: [show_frame(frame_show_group_average), show_group_average(False), entry_5.delete(0, last="end")]).pack(pady=3)
ttk.Button(frame_menu, text="Выход", width=30, command=lambda: root.destroy()).pack(pady=3)


frame_operation_on_student = ttk.Frame(root)
ttk.Button(frame_operation_on_student, text="Обратно", command=lambda:show_frame(frame_menu)).pack(anchor='nw')
ttk.Label(frame_operation_on_student, text="Введите ФИО и номер группы", font=("", 12)).pack(pady=10)
ttk.Label(frame_operation_on_student, text="В случае отсутствия отчества напишите тире", font=("", 9)).pack()
entry_1 = tk.Entry(frame_operation_on_student, width=40)
entry_1.pack(pady=10)

frame_butt_1 = ttk.Frame(frame_operation_on_student)
frame_butt_1.pack(fill="x", pady=10)
frame_butt_1.columnconfigure(0, weight=1)
frame_butt_1.columnconfigure(1, weight=1)

tk.Button(frame_butt_1, text="Добавить", bg="green", width=15, command=lambda: [operation_on_student(True), entry_1.delete(0, last="end")]).grid(column=0, row=0)
tk.Button(frame_butt_1, text="Удалить", bg="red", width=15, command=lambda: [operation_on_student(False), entry_1.delete(0, last="end")]).grid(column=1, row=0)
label_1 = ttk.Label(frame_operation_on_student)
label_1.pack(pady=10)


frame_edit_student = ttk.Frame(root)
ttk.Button(frame_edit_student, text="Обратно", command=lambda:show_frame(frame_menu)).pack(anchor='nw')
ttk.Label(frame_edit_student, text="Введите ФИО и группу", font=("", 10)).pack()
ttk.Label(frame_edit_student, text="В случае отсутствия отчества напишите тире", font=("", 9)).pack()
entry_2 = tk.Entry(frame_edit_student, width=40)
entry_2.pack(pady=10)
ttk.Label(frame_edit_student, text="Введите замену", font=("", 10)).pack()
entry_3 = tk.Entry(frame_edit_student, width=30)
entry_3.pack(pady=10)

frame_butt_2 = ttk.Frame(frame_edit_student)
frame_butt_2.pack(fill="x", pady=10)
frame_butt_2.columnconfigure(0, weight=1)
frame_butt_2.columnconfigure(1, weight=1)
frame_butt_2.columnconfigure(2, weight=1)
frame_butt_2.columnconfigure(3, weight=1)

ttk.Button(frame_butt_2, text="Замена\nфамилии", command=lambda: [edit_student("first_name"), entry_3.delete(0, last="end")]).grid(column=0, row=0)
ttk.Button(frame_butt_2, text="Замена\nимени", command=lambda: [edit_student("last_name"), entry_3.delete(0, last="end")]).grid(column=1, row=0)
ttk.Button(frame_butt_2, text="Замена\nотчества", command=lambda: [edit_student("middle_name"), entry_3.delete(0, last="end")]).grid(column=2, row=0)
ttk.Button(frame_butt_2, text="Замена\nгруппы", command=lambda: [edit_student("group_name"), entry_3.delete(0, last="end")]).grid(column=3, row=0)
label_2 = ttk.Label(frame_edit_student)
label_2.pack(pady=10)


frame_show_all_students = ttk.Frame(root)
frame_butt_3 = tk.Frame(frame_show_all_students)
frame_butt_3.pack(fill=X)

frame_butt_3.columnconfigure(0, weight=1)
frame_butt_3.columnconfigure(1, weight=1)
frame_butt_3.columnconfigure(2, weight=0)

ttk.Button(frame_butt_3, text="Обратно", command=lambda:show_frame(frame_menu)).grid(row=0, column=0, sticky='w')
ttk.Button(frame_butt_3, text="Поиск", command=lambda: show_all_students(True)).grid(row=0, column=2, sticky='e')
entry_4 = ttk.Entry(frame_butt_3, width=40)
entry_4.grid(pady=2, row=0, column=1)

ttk.Label(frame_show_all_students, text="Студенты", font=("", 14)).pack()
listbox_1 = Listbox(frame_show_all_students)
listbox_1.pack(side=LEFT, fill=BOTH, expand=1)
scrollbar_1 = ttk.Scrollbar(frame_show_all_students, orient="vertical", command=listbox_1.yview)
scrollbar_1.pack(side="right", fill='y')
listbox_1["yscrollcommand"]=scrollbar_1.set


frame_show_group_average = ttk.Frame(root)
frame_butt_4 = tk.Frame(frame_show_group_average)
frame_butt_4.pack(fill=X)

frame_butt_4.columnconfigure(0, weight=1)
frame_butt_4.columnconfigure(1, weight=1)
frame_butt_4.columnconfigure(2, weight=0)

ttk.Button(frame_butt_4, text="Обратно", command=lambda:show_frame(frame_menu)).grid(row=0, column=0, sticky='w')
ttk.Button(frame_butt_4, text="Поиск", command=lambda: show_group_average(True)).grid(row=0, column=2, sticky='e')
entry_5 = ttk.Entry(frame_butt_4, width=40)
entry_5.grid(pady=2, row=0, column=1)

ttk.Label(frame_show_group_average, text="Группы", font=("", 14)).pack()
listbox_2 = Listbox(frame_show_group_average)
listbox_2.pack(side=LEFT, fill=BOTH, expand=1)
scrollbar_2 = ttk.Scrollbar(frame_show_group_average, orient="vertical", command=listbox_2.yview)
scrollbar_2.pack(side="right", fill='y')
listbox_2["yscrollcommand"]=scrollbar_2.set


frames = [frame_menu,
          frame_operation_on_student,
          frame_edit_student,
          frame_show_all_students,
          frame_show_group_average]
for frame in frames:
    frame.grid(row=0, column=0, sticky='nsew')

show_frame(frame_menu)
root.mainloop()