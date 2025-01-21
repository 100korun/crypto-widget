import tkinter as tk
import time
import requests
import random
import platform


API_URL = "https://api.coingecko.com/api/v3/simple/price"
DEFAULT_CRYPTO = [
    "bitcoin", "ethereum", "dogecoin", "ripple", "litecoin",
    "polkadot", "cardano", "solana", "tron", "monero", "XRP"
]

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
    "shiba-inu": {"usd": 1, "change": -4.46, "symbol": "XRP"}
}


class CryptoWidget:
    def __init__(self, root):
        self.root = root
        self.platform = platform.system()  # Detect OS
        self.root.title("Crypto Widget")
        self.root.configure(bg="#1e1e1e")

        # Remove title bar for Windows
        if self.platform == "Windows":
            self.root.overrideredirect(True)

        # Canvas for rendering
        self.canvas = tk.Canvas(root, bg="#1e1e1e", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Label for update timer
        self.timer_label = tk.Label(root, text="", bg="#1e1e1e", fg="white", font=("Arial", 12, "bold"))
        self.timer_label.pack(side="bottom", pady=5)

        # Version label
        self.version_label = tk.Label(
            root,
            text="v0.1",
            bg="#1e1e1e",
            fg="white",
            font=("Arial", 10, "bold"),
            anchor="w"
        )
        self.version_label.place(relx=0.01, rely=0.98, anchor="sw")  # Bottom-left corner

        # Data
        self.crypto_data = DEFAULT_DATA.copy()
        self.last_update = 0
        self.update_interval = 30  # Update interval (seconds)
        self.remaining_time = self.update_interval
        self.scale = 1.0

        self.update_prices()
        self.update_timer()

        self.root.bind("<Configure>", self.on_resize)
        self.canvas.bind("<MouseWheel>", self.zoom)

        # Create a context menu
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Close", command=self.root.quit)

        # Handle right-click for the platform
        right_click = "<Button-2>" if self.platform == "Darwin" else "<Button-3>"
        self.canvas.bind(right_click, self.show_context_menu)

        # Enable window dragging on both platforms
        self.canvas.bind("<ButtonPress-1>", self.start_move)
        self.canvas.bind("<B1-Motion>", self.move_window)

        # Initial movement coordinates
        self.x = 0
        self.y = 0

    def fetch_crypto_prices(self):
        """Fetch cryptocurrency data with error handling."""
        if time.time() - self.last_update < self.update_interval:
            print("Using cached data.")
            return self.crypto_data

        try:
            print("Fetching data from API...")
            response = requests.get(API_URL, params={"ids": ",".join(DEFAULT_CRYPTO), "vs_currencies": "usd"})
            response.raise_for_status()
            data = response.json()

            # Generate random changes
            for crypto in data:
                data[crypto]["change"] = random.uniform(-5, 5)
                data[crypto]["symbol"] = crypto[:3].upper()
            self.crypto_data = data
            self.last_update = time.time()
            self.remaining_time = self.update_interval
            print("Data fetched successfully:", data)
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error: {e}")
        except Exception as e:
            print(f"Error: {e}")

        return self.crypto_data

    def update_prices(self):
        """Update price data and redraw blocks."""
        self.fetch_crypto_prices()
        self.render_squares()
        self.root.after(self.update_interval * 1000, self.update_prices)

    def update_timer(self):
        """Update the countdown timer."""
        if self.remaining_time > 0:
            self.remaining_time -= 1
            self.timer_label.config(text=f"Next update in: {self.remaining_time} seconds")
        else:
            self.timer_label.config(text="Updating data...")
        self.root.after(1000, self.update_timer)

    def render_squares(self):
        """Display data as a grid of blocks."""
        self.canvas.delete("all")
        if not self.crypto_data:
            print("No data to display.")
            return

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        # Debugging canvas size
        print(f"Canvas size: width={width}, height={height}")

        if width == 1 or height == 1:
            print("Canvas not ready, skipping render.")
            return  # Skip rendering if dimensions are not ready

        num_crypto = len(self.crypto_data)
        grid_size = int(num_crypto ** 0.5) + (1 if (num_crypto ** 0.5) % 1 != 0 else 0)

        cell_width = width / grid_size
        cell_height = height / grid_size

        for i, (name, data) in enumerate(sorted(self.crypto_data.items(), key=lambda x: -x[1]["usd"])):
            price = data["usd"]
            change = data["change"]
            symbol = data["symbol"]

            row = i // grid_size
            col = i % grid_size

            x1 = col * cell_width
            y1 = row * cell_height
            x2 = x1 + cell_width
            y2 = y1 + cell_height

            color = "green" if change >= 0 else "red"

            self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#1e1e1e")

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
        """Handle window resizing."""
        self.render_squares()

    def zoom(self, event):
        """Handle zooming with mouse wheel."""
        if event.delta > 0:
            self.scale *= 1.1
        elif event.delta < 0:
            self.scale /= 1.1
        self.render_squares()

    def show_context_menu(self, event):
        """Show context menu on right-click."""
        self.context_menu.post(event.x_root, event.y_root)

    def start_move(self, event):
        """Start window movement."""
        self.x = event.x
        self.y = event.y

    def move_window(self, event):
        """Move the window."""
        delta_x = event.x - self.x
        delta_y = event.y - self.y
        new_x = self.root.winfo_x() + delta_x
        new_y = self.root.winfo_y() + delta_y
        self.root.geometry(f"+{new_x}+{new_y}")


if __name__ == "__main__":
    root = tk.Tk()
    widget = CryptoWidget(root)
    root.mainloop()

