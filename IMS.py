import sqlite3


def get_positive_number(prompt):
    while True:
        try:
            value = float(input(prompt))
            if value > 0:
                return value
            print("Value must be positive.")
        except ValueError:
            print("Invalid input. Please enter a number.")


class InventoryManagementSystem:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
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

    def add_item(self):
        item_name = input("Enter item name: ")
        quantity = get_positive_number("Enter quantity: ")
        price = get_positive_number("Enter price: ")
        category = input("Enter item category (optional): ")
        self.cursor.execute(
            "INSERT OR REPLACE INTO inventory VALUES (?, ?, ?, ?)",
            (item_name, quantity, price, category),
        )
        self.conn.commit()
        print(f"{item_name} added to inventory.")

    def delete_item(self):
        item_name = input("Enter item name to delete: ")
        self.cursor.execute("DELETE FROM inventory WHERE item_name = ?", (item_name,))
        self.conn.commit()
        if not self.cursor.rowcount:
            print(f"{item_name} not found in inventory.")
        else:
            print(f"{item_name} deleted from inventory.")

    def search_item(self):
        search_term = input("Enter item name or category to search: ")
        self.cursor.execute(
            "SELECT * FROM inventory WHERE item_name LIKE ? OR category LIKE ?",
            (f"%{search_term}%", f"%{search_term}%"),
        )
        found_items = self.cursor.fetchall()
        if found_items:
            print("Search results:")
            for item in found_items:
                print(
                    f"- {item[0]} (Category: {item[3]}): Quantity {item[1]}, Price {item[2]}"
                )
        else:
            print("Item not found.")

    def edit_item(self):
        item_name = input("Enter item name to edit: ")
        self.cursor.execute("SELECT * FROM inventory WHERE item_name = ?", (item_name,))
        item = self.cursor.fetchone()
        if item:
            new_quantity = get_positive_number("Enter new quantity: ")
            new_price = get_positive_number("Enter new price: ")
            self.cursor.execute(
                "UPDATE inventory SET quantity = ?, price = ? WHERE item_name = ?",
                (new_quantity, new_price, item_name),
            )
            self.conn.commit()
            print(f"{item_name} updated.")
        else:
            print(f"{item_name} not found in inventory.")

    def display_inventory(self):
        self.cursor.execute("SELECT * FROM inventory")
        inventory = self.cursor.fetchall()
        if not inventory:
            print("Inventory is empty.")
            return

        print("Inventory:")
        total_value = sum(item[1] * item[2] for item in inventory)
        for item in inventory:
            print(
                f"- {item[0]} (Category: {item[3]}): Quantity {item[1]}, Price {item[2]}"
            )
        print(f"Total inventory value: ${total_value:.2f}")

    def close_connection(self):
        self.conn.close()


def main():
    db_name = "inventory.db"
    inventory_system = InventoryManagementSystem(db_name)

    while True:
        print("\nInventory Management System")
        print("1. Add item")
        print("2. Delete item")
        print("3. Search item")
        print("4. Edit item")
        print("5. Display inventory")
        print("6. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            inventory_system.add_item()
        elif choice == "2":
            inventory_system.delete_item()
        elif choice == "3":
            inventory_system.search_item()
        elif choice == "4":
            inventory_system.edit_item()
        elif choice == "5":
            inventory_system.display_inventory()
        elif choice == "6":
            inventory_system.close_connection()
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
