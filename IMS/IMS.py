import sqlite3
import tkinter as tk
from tkinter import Toplevel, messagebox, ttk
from PIL import Image, ImageTk


# Database management class
class IMS:
    def __init__(self, db_name):
        # Connect to SQLite database
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        # Create inventory table if it doesn't exist
        self.create_table()

    def create_table(self):
        # Create a table to store inventory items
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS inventory (
                item_name TEXT PRIMARY KEY,
                quantity INTEGER,
                price REAL,
                category TEXT
            )
            """
        )
        self.conn.commit()

    def add_item(self, item_name, quantity, price, category):
        # Add a new item to the inventory
        try:
            self.cursor.execute(
                "INSERT OR REPLACE INTO inventory VALUES (?, ?, ?, ?)",
                (item_name, quantity, price, category),
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error: {e}")
            return False

    def delete_item(self, item_name):
        # Delete an item from the inventory
        self.cursor.execute("DELETE FROM inventory WHERE item_name = ?", (item_name,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def search_item(self, search_term):
        # Search for items in the inventory based on name or category
        self.cursor.execute(
            "SELECT * FROM inventory WHERE item_name LIKE ? OR category LIKE ?",
            (f"%{search_term}%", f"%{search_term}%"),
        )
        return self.cursor.fetchall()

    def fetch_all_items(self):
        # Fetch all items from the inventory
        self.cursor.execute("SELECT * FROM inventory")
        return self.cursor.fetchall()

    def close_connection(self):
        # Close the database connection
        self.conn.close()


# GUI application class
class InventoryApp:
    def __init__(self, root):
        # Initialize database and main window
        self.db = IMS("inventory.db")
        self.root = root
        self.root.title("Inventory Management System")
        self.root.geometry("700x600")

        # Load logo image
        logo_path = "C:/Users/asus/Desktop/IMS/IMS - v2.1/My2Project/Logo.png"
        try:
            logo_image = Image.open(logo_path)
            logo_image = logo_image.resize((100, 100), Image.Resampling.LANCZOS)
            self.logo = ImageTk.PhotoImage(logo_image)

            # Display the logo
            logo_label = tk.Label(root, image=self.logo)
            logo_label.pack(pady=10)
        except FileNotFoundError:
            messagebox.showerror("Error", f"Logo file not found at {logo_path}")

        # Header text
        header = tk.Label(
            root, text="Inventory Management System", font=("Arial", 18, "bold")
        )
        header.pack(pady=10)

        # Frame for input fields and buttons
        self.control_frame = tk.Frame(root)
        self.control_frame.pack(pady=10)

        # Input fields for item details
        tk.Label(self.control_frame, text="Item Name:").grid(
            row=0, column=0, padx=5, pady=5
        )
        self.item_name_entry = tk.Entry(self.control_frame)
        self.item_name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.control_frame, text="Quantity:").grid(
            row=1, column=0, padx=5, pady=5
        )
        self.quantity_entry = tk.Entry(self.control_frame)
        self.quantity_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.control_frame, text="Price:").grid(
            row=2, column=0, padx=5, pady=5
        )
        self.price_entry = tk.Entry(self.control_frame)
        self.price_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(self.control_frame, text="Category:").grid(
            row=3, column=0, padx=5, pady=5
        )
        self.category_entry = tk.Entry(self.control_frame)
        self.category_entry.grid(row=3, column=1, padx=5, pady=5)

        # Buttons for CRUD operations
        tk.Button(self.control_frame, text="Add Item", command=self.add_item).grid(
            row=4, column=0, padx=5, pady=5
        )
        tk.Button(
            self.control_frame, text="Delete Item", command=self.delete_item
        ).grid(row=4, column=1, padx=5, pady=5)
        tk.Button(
            self.control_frame, text="Search Item", command=self.open_search_window
        ).grid(row=5, column=0, padx=5, pady=5)
        tk.Button(self.control_frame, text="Refresh", command=self.refresh_table).grid(
            row=5, column=1, padx=5, pady=5
        )

        # Table to display inventory items
        self.tree = ttk.Treeview(
            root, columns=("Name", "Quantity", "Price", "Category"), show="headings"
        )
        self.tree.heading("Name", text="Item Name")
        self.tree.heading("Quantity", text="Quantity")
        self.tree.heading("Price", text="Price")
        self.tree.heading("Category", text="Category")
        self.tree.pack(pady=10)

        # Populate the table with data
        self.refresh_table()

    def add_item(self):
        # Add an item to the database
        item_name = self.item_name_entry.get()
        try:
            quantity = int(self.quantity_entry.get())
            price = float(self.price_entry.get())
        except ValueError:
            messagebox.showerror("Input Error", "Quantity and Price must be numbers.")
            return
        category = self.category_entry.get()

        if item_name and quantity > 0 and price > 0:
            if self.db.add_item(item_name, quantity, price, category):
                messagebox.showinfo("Success", "Item added successfully.")
                self.refresh_table()
        else:
            messagebox.showerror("Input Error", "All fields must be valid.")

    def delete_item(self):
        # Delete the selected item from the table and database
        selected_item = self.tree.selection()
        if selected_item:
            item_name = self.tree.item(selected_item)["values"][0]
            if self.db.delete_item(item_name):
                messagebox.showinfo("Success", "Item deleted successfully.")
                self.refresh_table()
            else:
                messagebox.showerror("Error", "Failed to delete item.")
        else:
            messagebox.showerror("Error", "No item selected.")

    def open_search_window(self):
        # Open a new window to search for items
        search_window = Toplevel(self.root)
        search_window.title("Search Item")
        search_window.geometry("400x300")

        tk.Label(search_window, text="Enter search term:").pack(pady=10)
        search_entry = tk.Entry(search_window)
        search_entry.pack(pady=5)

        search_results = ttk.Treeview(
            search_window,
            columns=("Name", "Quantity", "Price", "Category"),
            show="headings",
        )
        search_results.heading("Name", text="Item Name")
        search_results.heading("Quantity", text="Quantity")
        search_results.heading("Price", text="Price")
        search_results.heading("Category", text="Category")
        search_results.pack(pady=10)

        def search_action():
            # Perform search based on user input
            search_term = search_entry.get()
            results = self.db.search_item(search_term)
            for row in search_results.get_children():
                search_results.delete(row)
            for item in results:
                search_results.insert("", "end", values=item)

        tk.Button(search_window, text="Search", command=search_action).pack(pady=10)

    def refresh_table(self):
        # Refresh the table with the latest data from the database
        items = self.db.fetch_all_items()
        for row in self.tree.get_children():
            self.tree.delete(row)
        for item in items:
            self.tree.insert("", "end", values=item)

    def close_app(self):
        # Close the application and database connection
        self.db.close_connection()
        self.root.destroy()


if __name__ == "__main__":
    # Start the application
    root = tk.Tk()
    app = InventoryApp(root)
    root.protocol("WM_DELETE_WINDOW", app.close_app)
    root.mainloop()
