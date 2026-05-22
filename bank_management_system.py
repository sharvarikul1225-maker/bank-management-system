import tkinter as tk
from tkinter import messagebox
import random
import hashlib

# In-memory user database
users = {}
current_user = [None]

# Hash password using SHA-256
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Generate unique 10-digit account number
def generate_account_number():
    while True:
        acc = str(random.randint(1000000000, 9999999999))
        if acc not in users:
            return acc

# Account creation logic
def create_account(name, aadhaar, password):
    if len(password) < 8:
        return "Password must be at least 8 characters."
    for user in users.values():
        if user['aadhaar'] == aadhaar:
            return "Aadhaar already registered."
    acc = generate_account_number()
    users[acc] = {
        'name': name,
        'aadhaar': aadhaar,
        'password_hash': hash_password(password),
        'balance': 0
    }
    return f"Account created!\nYour Account Number: {acc}"

# Login logic
def login(account_number, password):
    if account_number not in users:
        return "Account not found."
    if users[account_number]['password_hash'] != hash_password(password):
        return "Incorrect password."
    current_user[0] = account_number
    return f"Welcome, {users[account_number]['name']}!"

# Other operations
def logout():
    current_user[0] = None
    return "Logged out."

def deposit(amount):
    if current_user[0]:
        users[current_user[0]]['balance'] += amount
        return f"Deposited ₹{amount}."
    return "Please log in."

def withdraw(amount):
    if current_user[0]:
        if users[current_user[0]]['balance'] >= amount:
            users[current_user[0]]['balance'] -= amount
            return f"Withdrew ₹{amount}."
        return "Insufficient funds."
    return "Please log in."

def transfer(to_acc, amount):
    if current_user[0]:
        if to_acc not in users:
            return "Recipient account not found."
        if users[current_user[0]]['balance'] >= amount:
            users[current_user[0]]['balance'] -= amount
            users[to_acc]['balance'] += amount
            return f"Transferred ₹{amount} to {to_acc}."
        return "Insufficient funds."
    return "Please log in."

def check_balance():
    if current_user[0]:
        return f"Balance: ₹{users[current_user[0]]['balance']}"
    return "Please log in."

# GUI
def main_window():
    root = tk.Tk()
    root.title("Cosmos Bank")
    root.configure(bg='#ADD8E6')
    root.attributes('-fullscreen', True)

    default_font = ("Arial", 16)
    status_label = [None]  # To hold reference across nested functions

    def clear_frame():
        for widget in root.winfo_children():
            widget.destroy()

        # Header on top of every screen
        tk.Label(root, text="Welcome to Cosmos Bank",
                 font=("Arial", 24, "bold"),
                 bg='#ADD8E6').pack(pady=20)

    def label(text):
        return tk.Label(root, text=text, font=default_font, bg='#ADD8E6')

    def show_login():
        clear_frame()
        label("Login").pack(pady=10)
        label("Account Number").pack(pady=5)
        acc_entry = tk.Entry(root, font=default_font)
        acc_entry.pack(pady=5)
        label("Password").pack(pady=5)
        pass_entry = tk.Entry(root, show="*", font=default_font)
        pass_entry.pack(pady=5)
        tk.Button(root, text="Login", font=default_font,
                  command=lambda: try_login(acc_entry.get(), pass_entry.get())).pack(pady=10)
        tk.Button(root, text="Create Account",
                  font=default_font, command=show_create_account).pack(pady=10)

    def try_login(acc, pwd):
        msg = login(acc, pwd)
        messagebox.showinfo("Login", msg)
        if "Welcome" in msg:
            show_dashboard()

    def show_create_account():
        clear_frame()
        label("Create Account").pack(pady=10)
        label("Full Name").pack(pady=5)
        name_entry = tk.Entry(root, font=default_font)
        name_entry.pack(pady=5)
        label("Aadhaar Number").pack(pady=5)
        aadhaar_entry = tk.Entry(root, font=default_font)
        aadhaar_entry.pack(pady=5)
        label("Password (min 8 chars)").pack(pady=5)
        pass_entry = tk.Entry(root, show="*", font=default_font)
        pass_entry.pack(pady=5)

        def do_create():
            msg = create_account(name_entry.get(), aadhaar_entry.get(), pass_entry.get())
            if "Account created" in msg:
                clear_frame()
                acc_number = msg.split(":")[-1].strip()
                label("Account successfully created!").pack(pady=10)
                label("Your Account Number:").pack(pady=5)
                acc_entry = tk.Entry(root, font=default_font, justify="center")
                acc_entry.insert(0, acc_number)
                acc_entry.configure(state="readonly")
                acc_entry.pack(pady=5)

                def copy_to_clipboard():
                    root.clipboard_clear()
                    root.clipboard_append(acc_number)
                    messagebox.showinfo("Copied", "Account number copied to clipboard!")

                tk.Button(root, text="Copy Account Number",
                          font=default_font, command=copy_to_clipboard).pack(pady=10)
                tk.Button(root, text="Back to Login",
                          font=default_font, command=show_login).pack(pady=20)
            else:
                messagebox.showinfo("Account Creation", msg)

        tk.Button(root, text="Create Account",
                  font=default_font, command=do_create).pack(pady=10)
        tk.Button(root, text="Back to Login",
                  font=default_font, command=show_login).pack(pady=10)

    def show_dashboard():
        clear_frame()
        user_data = users[current_user[0]]

        # Left-side frame (main actions)
        main_frame = tk.Frame(root, bg='#ADD8E6')
        main_frame.pack(side='left', expand=True, fill='both')

        label_widget = lambda text: tk.Label(main_frame, text=text, font=default_font, bg='#ADD8E6')
        label_widget(f"Welcome, {user_data['name']}").pack(pady=5)
        label_widget(f"Account No: {current_user[0]}").pack(pady=5)

        label_widget("Deposit Amount").pack(pady=5)
        deposit_entry = tk.Entry(main_frame, font=default_font)
        deposit_entry.pack(pady=5)
        tk.Button(main_frame, text="Deposit", font=default_font,
                  command=lambda: try_deposit(deposit_entry.get())).pack(pady=10)

        label_widget("Withdraw Amount").pack(pady=5)
        withdraw_entry = tk.Entry(main_frame, font=default_font)
        withdraw_entry.pack(pady=5)
        tk.Button(main_frame, text="Withdraw", font=default_font,
                  command=lambda: try_withdraw(withdraw_entry.get())).pack(pady=10)

        label_widget("Transfer To (Account Number)").pack(pady=5)
        transfer_acc = tk.Entry(main_frame, font=default_font)
        transfer_acc.pack(pady=5)
        label_widget("Amount to Transfer").pack(pady=5)
        transfer_amt = tk.Entry(main_frame, font=default_font)
        transfer_amt.pack(pady=5)
        tk.Button(main_frame, text="Transfer", font=default_font,
                  command=lambda: try_transfer(transfer_acc.get(), transfer_amt.get())).pack(pady=10)

        tk.Button(main_frame, text="Check Balance", font=default_font,
                  command=lambda: status_label[0].config(text=check_balance())).pack(pady=10)
        tk.Button(main_frame, text="Logout", font=default_font,
                  command=lambda: [messagebox.showinfo("Logout", logout()), show_login()]).pack(pady=10)
        tk.Button(main_frame, text="Exit", font=default_font,
                  command=root.destroy).pack(pady=30)

        # Right-side frame for transaction output
        right_frame = tk.Frame(root, bg='#E0FFFF', width=300, height=300)
        right_frame.pack(side='right', fill='both', padx=20, pady=50)

        status = tk.Label(right_frame, text="Transaction Info", font=default_font,
                          bg='#E0FFFF', wraplength=250, justify="left")
        status.pack(pady=20, padx=20)
        status_label[0] = status

        def try_deposit(val):
            try:
                amt = float(val)
                result = deposit(amt)
                status_label[0].config(text=result + "\n" + check_balance())
            except:
                status_label[0].config(text="Invalid amount.")

        def try_withdraw(val):
            try:
                amt = float(val)
                result = withdraw(amt)
                status_label[0].config(text=result + "\n" + check_balance())
            except:
                status_label[0].config(text="Invalid amount.")

        def try_transfer(to, val):
            try:
                amt = float(val)
                result = transfer(to, amt)
                status_label[0].config(text=result + "\n" + check_balance())
            except:
                status_label[0].config(text="Invalid amount.")

    show_login()
    root.mainloop()

main_window()
