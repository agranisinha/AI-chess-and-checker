# battle_log.py
import os, json
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

# File paths for logs and stats
HISTORY_FILE = os.path.join(os.path.dirname(__file__), "battle_history.json")
STATS_FILE = os.path.join(os.path.dirname(__file__), "battle_stats.json")

# ✅ Add game entry to history log
def add_to_history(game_data):
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            try:
                history = json.load(f)
            except:
                history = []

    game_data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    history.append(game_data)

    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

# ✅ Get game history
def get_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return []

# ✅ Get current stats
def get_stats():
    if not os.path.exists(STATS_FILE):
        return {
            "chess": {"white_wins": 0, "black_wins": 0, "draws": 0},
            "checkers": {"white_wins": 0, "black_wins": 0, "draws": 0}
        }
    with open(STATS_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return {
                "chess": {"white_wins": 0, "black_wins": 0, "draws": 0},
                "checkers": {"white_wins": 0, "black_wins": 0, "draws": 0}
            }

# ✅ Update result stats
def update_stats(game_type, message):
    stats = get_stats()
    if game_type not in stats:
        stats[game_type] = {"white_wins": 0, "black_wins": 0, "draws": 0}

    msg = message.lower()
    if "draw" in msg:
        stats[game_type]["draws"] += 1
    elif "white wins" in msg or "player 1" in msg:
        stats[game_type]["white_wins"] += 1
    elif "black wins" in msg or "player 2" in msg:
        stats[game_type]["black_wins"] += 1

    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=2)

# 🔄 Reset all logs and stats
def reset_history_and_stats():
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)
    if os.path.exists(STATS_FILE):
        os.remove(STATS_FILE)

# 🖼️ Show full battle log UI
def show_battle_log(root, go_back_callback=None):
    for widget in root.winfo_children():
        widget.destroy()
    root.configure(bg="#2B2B2B")

    # Header
    tk.Label(root, text="📜 Battle Log & Stats", font=("Arial", 20, "bold"), bg="#2B2B2B", fg="white").pack(pady=15)

    # Stats summary
    stats = get_stats()
    summary = (
        f"♟ Chess - White: {stats['chess']['white_wins']} | Black: {stats['chess']['black_wins']} | Draws: {stats['chess']['draws']}\n"
        f"🪙 Checkers - White: {stats['checkers']['white_wins']} | Black: {stats['checkers']['black_wins']} | Draws: {stats['checkers']['draws']}"
    )
    tk.Label(root, text=summary, font=("Arial", 13), bg="#2B2B2B", fg="lightgreen").pack(pady=5)

    # History Table
    frame = tk.Frame(root, bg="#2B2B2B")
    frame.pack(padx=20, pady=10, fill="both", expand=True)

    columns = ("Game", "Type", "Result", "Moves", "Timestamp")
    tree = ttk.Treeview(frame, columns=columns, show="headings", height=12)

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview.Heading", font=("Arial", 12, "bold"))
    style.configure("Treeview", rowheight=28, font=("Arial", 11))

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=170 if col != "Result" else 250)

    for entry in reversed(get_history()):
        tree.insert("", "end", values=(
            entry.get("name", "N/A"),
            entry.get("type", "chess"),
            entry.get("result", "N/A"),
            entry.get("moves", 0),
            entry.get("timestamp", "N/A")
        ))
    tree.pack(fill="both", expand=True)

    # Footer Buttons
    button_frame = tk.Frame(root, bg="#2B2B2B")
    button_frame.pack(pady=15)

    def confirm_reset():
        if messagebox.askyesno("Reset", "Clear all game history and stats?"):
            reset_history_and_stats()
            show_battle_log(root, go_back_callback)

    tk.Button(button_frame, text="↩️ Back to Home", font=("Arial", 12), bg="white",
              command=go_back_callback).grid(row=0, column=0, padx=10)
    tk.Button(button_frame, text="🗑️ Reset All", font=("Arial", 12), bg="red", fg="white",
              command=confirm_reset).grid(row=0, column=1, padx=10)
