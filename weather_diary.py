import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class WeatherDiary:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary - Дневник погоды")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        
        self.data_file = "weather_data.json"
        self.entries = []  # Список записей
        self.load_data()
        
        self.create_widgets()
        self.update_display()
    
    # ========== Работа с JSON ==========
    def save_data(self):
        """Сохраняет записи в JSON файл"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.entries, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")
    
    def load_data(self):
        """Загружает записи из JSON файла"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.entries = json.load(f)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")
                self.entries = []
        else:
            self.entries = []
    
    # ========== Валидация ввода ==========
    def validate_date(self, date_str):
        """Проверяет формат даты (ГГГГ-ММ-ДД)"""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    def validate_temperature(self, temp_str):
        """Проверяет, что температура — число"""
        try:
            float(temp_str)
            return True
        except ValueError:
            return False
    
    # ========== Добавление записи ==========
    def add_entry(self):
        date = self.date_entry.get().strip()
        temp = self.temp_entry.get().strip()
        description = self.desc_entry.get().strip()
        precipitation = self.precip_var.get()
        
        # Проверка корректности ввода
        if not date:
            messagebox.showwarning("Ошибка", "Введите дату!")
            return
        
        if not self.validate_date(date):
            messagebox.showwarning("Ошибка", "Неверный формат даты!\nИспользуйте ГГГГ-ММ-ДД (например, 2024-03-15)")
            return
        
        if not temp:
            messagebox.showwarning("Ошибка", "Введите температуру!")
            return
        
        if not self.validate_temperature(temp):
            messagebox.showwarning("Ошибка", "Температура должна быть числом!")
            return
        
        if not description:
            messagebox.showwarning("Ошибка", "Введите описание погоды!")
            return
        
        # Создаём запись
        new_entry = {
            "date": date,
            "temperature": float(temp),
            "description": description,
            "precipitation": precipitation
        }
        
        self.entries.append(new_entry)
        self.save_data()
        self.update_display()
        
        # Очищаем поля ввода
        self.date_entry.delete(0, tk.END)
        self.temp_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.precip_var.set("Нет")
        
        messagebox.showinfo("Успех", "Запись добавлена!")
    
    # ========== Отображение записей ==========
    def update_display(self, filtered_entries=None):
        """Обновляет таблицу с записями"""
        # Очищаем таблицу
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        entries_to_show = filtered_entries if filtered_entries is not None else self.entries
        
        # Сортируем по дате (новые сверху)
        entries_to_show.sort(key=lambda x: x["date"], reverse=True)
        
        for entry in entries_to_show:
            precip_text = "Да" if entry["precipitation"] else "Нет"
            self.tree.insert("", tk.END, values=(
                entry["date"],
                f"{entry['temperature']:.1f}°C",
                entry["description"],
                precip_text
            ))
    
    # ========== Фильтрация ==========
    def filter_by_date(self):
        date_filter = self.filter_date_entry.get().strip()
        
        if not date_filter:
            messagebox.showwarning("Ошибка", "Введите дату для фильтрации!")
            return
        
        if not self.validate_date(date_filter):
            messagebox.showwarning("Ошибка", "Неверный формат даты!\nИспользуйте ГГГГ-ММ-ДД")
            return
        
        filtered = [e for e in self.entries if e["date"] == date_filter]
        
        if not filtered:
            messagebox.showinfo("Результат", f"Записей за {date_filter} не найдено.")
        
        self.update_display(filtered)
    
    def filter_by_temperature(self):
        try:
            temp_threshold = float(self.filter_temp_entry.get().strip())
        except ValueError:
            messagebox.showwarning("Ошибка", "Введите корректное число для температуры!")
            return
        
        filtered = [e for e in self.entries if e["temperature"] > temp_threshold]
        
        if not filtered:
            messagebox.showinfo("Результат", f"Записей с температурой выше {temp_threshold}°C не найдено.")
        
        self.update_display(filtered)
    
    def reset_filter(self):
        """Сбрасывает фильтрацию и показывает все записи"""
        self.filter_date_entry.delete(0, tk.END)
        self.filter_temp_entry.delete(0, tk.END)
        self.update_display()
        messagebox.showinfo("Фильтр", "Фильтрация сброшена. Показаны все записи.")
    
    def delete_selected(self):
        """Удаляет выбранную запись"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите запись для удаления!")
            return
        
        if messagebox.askyesno("Подтверждение", "Удалить выбранную запись?"):
            # Получаем индекс выбранной записи
            for item in selected:
                values = self.tree.item(item, "values")
                # Ищем запись в self.entries
                for i, entry in enumerate(self.entries):
                    if (entry["date"] == values[0] and 
                        float(entry["temperature"]) == float(values[1].replace("°C", "")) and
                        entry["description"] == values[2]):
                        del self.entries[i]
                        break
            
            self.save_data()
            self.update_display()
            messagebox.showinfo("Успех", "Запись удалена!")
    
    # ========== Интерфейс ==========
    def create_widgets(self):
        # Основной контейнер
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # ===== Левая панель - Добавление записи =====
        left_frame = ttk.LabelFrame(main_frame, text="Добавить запись", padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        
        # Дата
        ttk.Label(left_frame, text="Дата (ГГГГ-ММ-ДД):").pack(anchor=tk.W, pady=(0, 5))
        self.date_entry = ttk.Entry(left_frame, width=25)
        self.date_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Температура
        ttk.Label(left_frame, text="Температура (°C):").pack(anchor=tk.W, pady=(0, 5))
        self.temp_entry = ttk.Entry(left_frame, width=25)
        self.temp_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Описание
        ttk.Label(left_frame, text="Описание погоды:").pack(anchor=tk.W, pady=(0, 5))
        self.desc_entry = ttk.Entry(left_frame, width=25)
        self.desc_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Осадки
        ttk.Label(left_frame, text="Осадки:").pack(anchor=tk.W, pady=(0, 5))
        self.precip_var = tk.StringVar(value="Нет")
        precip_frame = ttk.Frame(left_frame)
        precip_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Radiobutton(precip_frame, text="Да", variable=self.precip_var, value="Да").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(precip_frame, text="Нет", variable=self.precip_var, value="Нет").pack(side=tk.LEFT)
        
        # Кнопка добавления
        ttk.Button(left_frame, text="➕ Добавить запись", command=self.add_entry).pack(fill=tk.X, pady=10)
        
        # Кнопка удаления
        ttk.Button(left_frame, text="🗑 Удалить запись", command=self.delete_selected).pack(fill=tk.X, pady=5)
        
        # ===== Правая панель - Просмотр и фильтрация =====
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Фильтры
        filter_frame = ttk.LabelFrame(right_frame, text="Фильтрация", padding="10")
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Фильтр по дате
        date_filter_frame = ttk.Frame(filter_frame)
        date_filter_frame.pack(fill=tk.X, pady=5)
        ttk.Label(date_filter_frame, text="Дата:").pack(side=tk.LEFT, padx=(0, 5))
        self.filter_date_entry = ttk.Entry(date_filter_frame, width=15)
        self.filter_date_entry.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(date_filter_frame, text="Применить", command=self.filter_by_date, width=10).pack(side=tk.LEFT)
        
        # Фильтр по температуре
        temp_filter_frame = ttk.Frame(filter_frame)
        temp_filter_frame.pack(fill=tk.X, pady=5)
        ttk.Label(temp_filter_frame, text="Температура выше (°C):").pack(side=tk.LEFT, padx=(0, 5))
        self.filter_temp_entry = ttk.Entry(temp_filter_frame, width=10)
        self.filter_temp_entry.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(temp_filter_frame, text="Применить", command=self.filter_by_temperature, width=10).pack(side=tk.LEFT)
        
        # Кнопка сброса фильтра
        ttk.Button(filter_frame, text="🔄 Сбросить фильтр", command=self.reset_filter).pack(fill=tk.X, pady=5)
        
        # Таблица записей
        table_frame = ttk.LabelFrame(right_frame, text="Записи о погоде", padding="10")
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("Дата", "Температура", "Описание", "Осадки")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        self.tree.heading("Дата", text="Дата")
        self.tree.heading("Температура", text="Температура")
        self.tree.heading("Описание", text="Описание")
        self.tree.heading("Осадки", text="Осадки")
        
        self.tree.column("Дата", width=100)
        self.tree.column("Температура", width=80)
        self.tree.column("Описание", width=200)
        self.tree.column("Осадки", width=60)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Подсказка
        hint_label = ttk.Label(right_frame, text="💡 Подсказка: Формат даты ГГГГ-ММ-ДД (например, 2024-03-15)", 
                               font=("Arial", 9), foreground="gray")
        hint_label.pack(pady=(5, 0))

def main():
    root = tk.Tk()
    app = WeatherDiary(root)
    root.mainloop()

if __name__ == "__main__":
    main()