import tkinter as tk
import time  # Добавлено для использования time.time()
import requests
import random


API_URL = "https://api.coingecko.com/api/v3/simple/price"
DEFAULT_CRYPTO = [
    "bitcoin", "ethereum", "dogecoin", "ripple", "litecoin",
    "polkadot", "cardano", "solana", "tron", "monero", "shiba-inu"
]

# Примерные данные
DEFAULT_DATA = {
    "bitcoin": {"usd": 20000, "change": 2.87, "symbol": "BIT"},
    "ethereum": {"usd": 1500, "change": 0.57, "symbol": "ETH"},
    "dogecoin": {"usd": 0.06, "change": -2.33, "symbol": "DOG"},
    "ripple": {"usd": 0.3, "change": 0.77, "symbol": "RIP"},
    "litecoin": {"usd": 60, "change": -3.63, "symbol": "LIT"},
    "polkadot": {"usd": 5, "change": -2.04, "symbol": "POL"},
    "cardano": {"usd": 0.35, "change": 2.04, "symbol": "CAR"},
    "solana": {"usd": 20, "change": -2.62, "symbol": "SOL"},
    "tron": {"usd": 0.08, "change": 1.97, "symbol": "TRO"},
    "monero": {"usd": 150, "change": 3.06, "symbol": "MON"},
    "shiba-inu": {"usd": 0.00001, "change": -4.46, "symbol": "SHI"}
}


class CryptoWidget:
    def __init__(self, root):
        self.root = root
        self.root.title("Crypto Widget")
        self.root.configure(bg="#1e1e1e")

        # Убираем заголовок окна
        self.root.overrideredirect(True)

        # Холст для отрисовки
        self.canvas = tk.Canvas(root, bg="#1e1e1e", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Метка для таймера обновления
        self.timer_label = tk.Label(root, text="", bg="#1e1e1e", fg="white", font=("Arial", 12, "bold"))
        self.timer_label.pack(side="bottom", pady=5)

        # Данные
        self.crypto_data = DEFAULT_DATA.copy()
        self.last_update = 0
        self.update_interval = 30  # Интервал обновления данных (в секундах)
        self.remaining_time = self.update_interval
        self.scale = 1.0  # Масштаб блоков

        self.update_prices()
        self.update_timer()

        self.root.bind("<Configure>", self.on_resize)
        self.canvas.bind("<MouseWheel>", self.zoom)

        # Создание контекстного меню
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Закрыть", command=self.root.quit)

        # Обработчик правой кнопки мыши
        self.canvas.bind("<Button-3>", self.show_context_menu)

        # Перемещение окна
        self.canvas.bind("<ButtonPress-1>", self.start_move)
        self.canvas.bind("<B1-Motion>", self.move_window)

        # Начальные координаты для перемещения
        self.x = 0
        self.y = 0

    def fetch_crypto_prices(self):
        """Получить данные о криптовалютах с обработкой ошибок."""
        if time.time() - self.last_update < self.update_interval:
            print("Использование кэшированных данных.")
            return self.crypto_data

        try:
            print("Запрос данных из API...")
            response = requests.get(API_URL, params={"ids": ",".join(DEFAULT_CRYPTO), "vs_currencies": "usd"})
            response.raise_for_status()
            data = response.json()

            # Генерация случайных изменений
            for crypto in data:
                data[crypto]["change"] = random.uniform(-5, 5)
                data[crypto]["symbol"] = crypto[:3].upper()
            self.crypto_data = data
            self.last_update = time.time()
            self.remaining_time = self.update_interval  # Сброс таймера
            print("Данные успешно получены:", data)
        except requests.exceptions.HTTPError as e:
            print(f"HTTP ошибка: {e}")
        except Exception as e:
            print(f"Ошибка: {e}")

        return self.crypto_data

    def update_prices(self):
        """Обновить данные о ценах и перерисовать блоки."""
        self.fetch_crypto_prices()
        self.render_squares()
        self.root.after(self.update_interval * 1000, self.update_prices)

    def update_timer(self):
        """Обновить таймер обратного отсчёта."""
        if self.remaining_time > 0:
            self.remaining_time -= 1
            self.timer_label.config(text=f"Обновление через: {self.remaining_time} сек.")
        else:
            self.timer_label.config(text="Обновление данных...")
        self.root.after(1000, self.update_timer)

    def render_squares(self):
        """Отобразить блоки на основе данных в виде мозаики."""
        self.canvas.delete("all")
        if not self.crypto_data:
            print("Нет данных для отображения.")
            return

        # Размеры окна
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        # Количество криптовалют
        num_crypto = len(self.crypto_data)
        grid_size = int(num_crypto ** 0.5) + (1 if (num_crypto ** 0.5) % 1 != 0 else 0)

        # Размер ячейки
        cell_width = width / grid_size
        cell_height = height / grid_size

        for i, (name, data) in enumerate(sorted(self.crypto_data.items(), key=lambda x: -x[1]["usd"])):
            price = data["usd"]
            change = data["change"]
            symbol = data["symbol"]

            # Позиция в сетке
            row = i // grid_size
            col = i % grid_size

            # Координаты ячейки
            x1 = col * cell_width
            y1 = row * cell_height
            x2 = x1 + cell_width
            y2 = y1 + cell_height

            # Цвет на основе изменения
            color = "green" if change >= 0 else "red"

            # Рисование блока
            self.canvas.create_rectangle(
                x1, y1, x2, y2, fill=color, outline="#1e1e1e"
            )

            # Адаптивный текст
            text_size = int(min(cell_height / 5, cell_width / len(symbol), 20))
            self.canvas.create_text(
                (x1 + x2) / 2, y1 + cell_height / 4,
                text=symbol,
                fill="white",
                font=("Arial", text_size, "bold")
            )
            self.canvas.create_text(
                (x1 + x2) / 2, y1 + cell_height / 2,
                text=f"{change:+.2f}%",
                fill="white",
                font=("Arial", text_size, "bold")
            )
            self.canvas.create_text(
                (x1 + x2) / 2, y1 + 3 * cell_height / 4,
                text=f"${price:,.2f}",
                fill="white",
                font=("Arial", text_size - 2, "bold")
            )

    def on_resize(self, event):
        """Обработать изменение размеров окна."""
        self.render_squares()

    def zoom(self, event):
        """Обработать приближение/отдаление через колесико мыши."""
        if event.delta > 0:
            self.scale *= 1.1  # Увеличение масштаба
        elif event.delta < 0:
            self.scale /= 1.1  # Уменьшение масштаба
        self.render_squares()

    def show_context_menu(self, event):
        """Показать контекстное меню при правом клике мыши."""
        self.context_menu.post(event.x_root, event.y_root)

    def start_move(self, event):
        """Запомнить начальную позицию для перемещения окна."""
        self.x = event.x
        self.y = event.y

    def move_window(self, event):
        """Переместить окно при движении мыши."""
        delta_x = event.x - self.x
        delta_y = event.y - self.y
        new_x = self.root.winfo_x() + delta_x
        new_y = self.root.winfo_y() + delta_y
        self.root.geometry(f"+{new_x}+{new_y}")


# Запуск программы
if __name__ == "__main__":
    root = tk.Tk()
    widget = CryptoWidget(root)
    root.mainloop()
