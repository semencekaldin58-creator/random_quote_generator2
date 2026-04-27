import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os
from datetime import datetime

class RandomQuoteGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор случайных цитат")
        self.root.geometry("750x650")

        self.history_file = "quotes_history.json"
        self.quotes_file = "quotes_pool.json"
        
        # Загрузка или создание базового пула цитат
        self.quotes_pool = self.load_data(self.quotes_file, [
            {"text": "Оставайтесь голодными. Оставайтесь безрассудными.", "author": "Стив Джобс", "topic": "Мотивация"},
            {"text": "Я мыслю, следовательно, я существую.", "author": "Рене Декарт", "topic": "Философия"},
            {"text": "Успех — это способность шагать от одной неудачи к другой, не теряя энтузиазма.", "author": "Уинстон Черчилль", "topic": "Успех"},
            {"text": "Сложнее всего начать действовать, все остальное зависит только от упорства.", "author": "Амелия Эрхарт", "topic": "Мотивация"},
            {"text": "Жизнь — это то, что с тобой происходит, пока ты строишь планы.", "author": "Джон Леннон", "topic": "Жизнь"}
        ])
        
        self.history = self.load_data(self.history_file, [])

        self.create_widgets()
        self.update_filters()
        self.update_history_table()

    def create_widgets(self):
        # --- Фрейм добавления новой цитаты ---
        add_frame = ttk.LabelFrame(self.root, text="Добавить новую цитату", padding=10)
        add_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(add_frame, text="Текст:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.new_text_entry = ttk.Entry(add_frame, width=50)
        self.new_text_entry.grid(row=0, column=1, columnspan=3, padx=5, pady=5, sticky="w")

        ttk.Label(add_frame, text="Автор:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.new_author_entry = ttk.Entry(add_frame, width=20)
        self.new_author_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(add_frame, text="Тема:").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.new_topic_entry = ttk.Entry(add_frame, width=20)
        self.new_topic_entry.grid(row=1, column=3, padx=5, pady=5, sticky="w")

        ttk.Button(add_frame, text="Добавить", command=self.add_quote).grid(row=1, column=4, padx=10, pady=5)

        # --- Фрейм генерации и фильтрации ---
        gen_frame = ttk.LabelFrame(self.root, text="Генерация и Фильтры", padding=10)
        gen_frame.pack(fill=tk.X, padx=10, pady=5)

        filter_frame = ttk.Frame(gen_frame)
        filter_frame.pack(fill=tk.X, pady=5)

        ttk.Label(filter_frame, text="Фильтр по автору:").pack(side=tk.LEFT, padx=5)
        self.author_var = tk.StringVar(value="Все")
        self.author_combo = ttk.Combobox(filter_frame, textvariable=self.author_var, state="readonly", width=15)
        self.author_combo.pack(side=tk.LEFT, padx=5)
        self.author_combo.bind("<<ComboboxSelected>>", self.on_filter_change)

        ttk.Label(filter_frame, text="Фильтр по теме:").pack(side=tk.LEFT, padx=5)
        self.topic_var = tk.StringVar(value="Все")
        self.topic_combo = ttk.Combobox(filter_frame, textvariable=self.topic_var, state="readonly", width=15)
        self.topic_combo.pack(side=tk.LEFT, padx=5)
        self.topic_combo.bind("<<ComboboxSelected>>", self.on_filter_change)

        ttk.Button(gen_frame, text="Сгенерировать цитату", command=self.generate_quote).pack(pady=10)

        self.result_text = tk.Text(gen_frame, height=4, width=80, wrap=tk.WORD, font=("Arial", 11, "italic"), bg="#f0f0f0", relief=tk.FLAT)
        self.result_text.pack(pady=5)
        self.result_text.insert(tk.END, "Нажмите кнопку, чтобы получить цитату...")
        self.result_text.config(state=tk.DISABLED)

        # --- Фрейм истории ---
        history_frame = ttk.LabelFrame(self.root, text="История сгенерированных цитат", padding=10)
        history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.tree = ttk.Treeview(history_frame, columns=("date", "author", "topic", "text"), show="headings")
        self.tree.heading("date", text="Дата и время")
        self.tree.heading("author", text="Автор")
        self.tree.heading("topic", text="Тема")
        self.tree.heading("text", text="Текст цитаты")

        self.tree.column("date", width=130, anchor=tk.CENTER)
        self.tree.column("author", width=120, anchor=tk.W)
        self.tree.column("topic", width=100, anchor=tk.CENTER)
        self.tree.column("text", width=350, anchor=tk.W)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def update_filters(self):
        authors = sorted(list(set(q["author"] for q in self.quotes_pool)))
        topics = sorted(list(set(q["topic"] for q in self.quotes_pool)))
        
        self.author_combo["values"] = ["Все"] + authors
        self.topic_combo["values"] = ["Все"] + topics

    def add_quote(self):
        text = self.new_text_entry.get().strip()
        author = self.new_author_entry.get().strip()
        topic = self.new_topic_entry.get().strip()

        # Валидация
        if not text or not author or not topic:
            messagebox.showerror("Ошибка", "Все поля (Текст, Автор, Тема) должны быть заполнены!")
            return

        new_quote = {"text": text, "author": author, "topic": topic}
        self.quotes_pool.append(new_quote)
        self.save_data(self.quotes_file, self.quotes_pool)
        
        self.new_text_entry.delete(0, tk.END)
        self.new_author_entry.delete(0, tk.END)
        self.new_topic_entry.delete(0, tk.END)
        
        self.update_filters()
        messagebox.showinfo("Успех", "Цитата успешно добавлена!")

    def generate_quote(self):
        selected_author = self.author_var.get()
        selected_topic = self.topic_var.get()
        
        # Фильтрация пула
        available_quotes = self.quotes_pool
        if selected_author != "Все":
            available_quotes = [q for q in available_quotes if q["author"] == selected_author]
        if selected_topic != "Все":
            available_quotes = [q for q in available_quotes if q["topic"] == selected_topic]

        if not available_quotes:
            messagebox.showinfo("Пусто", "Нет цитат, соответствующих выбранным фильтрам.")
            return

        # Генерация
        selected = random.choice(available_quotes)
        
        display_text = f"«{selected['text']}»\n— {selected['author']} ({selected['topic']})"
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, display_text)
        self.result_text.config(state=tk.DISABLED)

        # Сохранение в историю
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        history_record = {
            "date": timestamp,
            "author": selected["author"],
            "topic": selected["topic"],
            "text": selected["text"]
        }
        
        self.history.insert(0, history_record)
        self.save_data(self.history_file, self.history)
        self.update_history_table()

    def on_filter_change(self, event=None):
        self.update_history_table()

    def update_history_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        selected_author = self.author_var.get()
        selected_topic = self.topic_var.get()

        for item in self.history:
            match_author = (selected_author == "Все" or item["author"] == selected_author)
            match_topic = (selected_topic == "Все" or item["topic"] == selected_topic)
            
            if match_author and match_topic:
                self.tree.insert("", tk.END, values=(item["date"], item["author"], item["topic"], item["text"]))

    def load_data(self, filename, default_data):
        if not os.path.exists(filename):
            return default_data
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return default_data

    def save_data(self, filename, data):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    root = tk.Tk()
    app = RandomQuoteGenerator(root)
    root.mainloop()