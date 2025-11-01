import customtkinter as ctk
from tkinter import messagebox
from database import get_products, add_product, sell_product, verify_login

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# ---------------------- LOGIN WINDOW ---------------------- #
def login_window():
    login = ctk.CTk()
    login.title("Login • POS System")
    login.geometry("350x300")

    ctk.CTkLabel(login, text="POS Login", font=("Arial", 20, "bold")).pack(pady=20)

    username_entry = ctk.CTkEntry(login, placeholder_text="Username")
    username_entry.pack(pady=5, padx=20, fill="x")

    password_entry = ctk.CTkEntry(login, placeholder_text="Password", show="*")
    password_entry.pack(pady=5, padx=20, fill="x")

    def try_login():
        u = username_entry.get().strip()
        p = password_entry.get().strip()
        ok, role = verify_login(u, p)
        if ok:
            messagebox.showinfo("Success", f"Welcome {u}! Role: {role}")
            login.destroy()
            main_window(role, u)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    ctk.CTkButton(login, text="Login", command=try_login).pack(pady=15)

    login.mainloop()

# ---------------------- MAIN POS WINDOW ---------------------- #
def main_window(role: str, username: str):
    app = ctk.CTk()
    app.title(f"POS Inventory — {username} ({role})")
    app.geometry("900x560")

    table = ctk.CTkFrame(app)
    table.pack(pady=10, padx=10, fill="x")

    def refresh_products():
        for w in table.winfo_children():
            w.destroy()
        headers = ["ID", "Name", "Category", "Qty", "Price"]
        for col, text in enumerate(headers):
            ctk.CTkLabel(table, text=text, font=("Arial", 14, "bold")).grid(row=0, column=col, padx=6, pady=4)

        for r, row in enumerate(get_products(), start=1):
            for c, val in enumerate(row):
                color = "red" if c == 3 and val < 5 else "black"
                ctk.CTkLabel(table, text=val, text_color=color).grid(row=r, column=c, padx=6, pady=2)

    refresh_products()

    def add_product_ui():
        if role != "admin":
            messagebox.showwarning("Access Denied", "Admins only")
            return
        win = ctk.CTkToplevel(app)
        win.title("Add Product")
        labels = ["Name", "Category", "Quantity", "Price"]
        entries = []
        for i, t in enumerate(labels):
            ctk.CTkLabel(win, text=t).grid(row=i, column=0, padx=6, pady=6, sticky="e")
            e = ctk.CTkEntry(win)
            e.grid(row=i, column=1, padx=6, pady=6)
            entries.append(e)

        def save():
            try:
                name = entries[0].get().strip()
                category = entries[1].get().strip()
                qty = int(entries[2].get())
                price = float(entries[3].get())
                add_product(name, category, qty, price)
                refresh_products()
                win.destroy()
                messagebox.showinfo("Success", "Product added!")
            except:
                messagebox.showerror("Error", "Invalid input")

        ctk.CTkButton(win, text="Save", command=save).grid(row=4, column=0, columnspan=2, pady=10)

    def sell_product_ui():
        win = ctk.CTkToplevel(app)
        win.title("Sell Product")

        ctk.CTkLabel(win, text="Product ID").grid(row=0, column=0, padx=6, pady=6, sticky="e")
        id_entry = ctk.CTkEntry(win)
        id_entry.grid(row=0, column=1, padx=6, pady=6)

        ctk.CTkLabel(win, text="Quantity").grid(row=1, column=0, padx=6, pady=6, sticky="e")
        qty_entry = ctk.CTkEntry(win)
        qty_entry.grid(row=1, column=1, padx=6, pady=6)

        def do_sell():
            try:
                pid = int(id_entry.get())
                qty = int(qty_entry.get())
                ok, msg = sell_product(pid, qty, username)
                refresh_products()
                if ok:
                    messagebox.showinfo("Sale", msg)
                    win.destroy()
                else:
                    messagebox.showwarning("Sale Failed", msg)
            except:
                messagebox.showerror("Error", "Invalid input")

        ctk.CTkButton(win, text="Sell", command=do_sell).grid(row=2, column=0, columnspan=2, pady=10)

    buttons = ctk.CTkFrame(app)
    buttons.pack(pady=10)

    ctk.CTkButton(buttons, text="Add Product (Admin)",
                  command=add_product_ui,
                  state=("normal" if role == "admin" else "disabled")).grid(row=0, column=0, padx=8)

    ctk.CTkButton(buttons, text="Sell Product", command=sell_product_ui).grid(row=0, column=1, padx=8)
    ctk.CTkButton(buttons, text="Refresh Products", command=refresh_products).grid(row=0, column=2, padx=8)

    app.mainloop()

# ----- start -----
if __name__ == "__main__":
    login_window()
