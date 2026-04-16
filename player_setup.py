import tkinter as tk
from chess_game import ChessGame
from checkers_game import CheckersGame
from tkinter import messagebox

class PlayerSetup:
    def __init__(self, root, game_type="chess", theme="Gryffindor", mode="human", return_home=None):
        self.root = root
        self.game_type = game_type
        self.theme = theme
        self.mode = mode
        self.return_home = return_home or self.default_home  # fallback to main menu
        self.root.configure(bg="#3B3B29")
        self.build_ui()

    # Fallback method to return to GameLauncher if no callback is provided
    def default_home(self):
        from main import GameLauncher
        GameLauncher(self.root).setup_ui()

    # Build the player setup UI form
    def build_ui(self):
        self.clear_screen()
        tk.Label(self.root, text=f"{self.game_type.upper()} SETUP", font=("Papyrus", 26, "bold"),
                 fg="white", bg="#3B3B29").pack(pady=20)

        form_frame = tk.Frame(self.root, bg="#3B3B29")
        form_frame.pack(pady=10)

        # Game name field
        tk.Label(form_frame, text="Game Name:", font=("Arial", 14), bg="#3B3B29", fg="white").grid(row=0, column=0, sticky="e", pady=10)
        self.game_name_entry = self.entry_box(form_frame)
        self.game_name_entry.grid(row=0, column=1, pady=10)

        # Player 1 fields
        tk.Label(form_frame, text="Player 1 Name:", font=("Arial", 14), bg="#3B3B29", fg="white").grid(row=1, column=0, sticky="e", pady=10)
        self.p1_name_entry = self.entry_box(form_frame)
        self.p1_name_entry.grid(row=1, column=1, pady=10)

        tk.Label(form_frame, text="Player 1 Color:", font=("Arial", 14), bg="#3B3B29", fg="white").grid(row=2, column=0, sticky="e", pady=10)
        self.p1_color = tk.StringVar(value="white")
        tk.OptionMenu(form_frame, self.p1_color, "white", "black").grid(row=2, column=1, pady=10)

        if self.mode == "human":
            # Player 2 fields (only if not playing vs AI)
            tk.Label(form_frame, text="Player 2 Name:", font=("Arial", 14), bg="#3B3B29", fg="white").grid(row=3, column=0, sticky="e", pady=10)
            self.p2_name_entry = self.entry_box(form_frame)
            self.p2_name_entry.grid(row=3, column=1, pady=10)

            tk.Label(form_frame, text="Player 2 Color:", font=("Arial", 14), bg="#3B3B29", fg="white").grid(row=4, column=0, sticky="e", pady=10)
            self.p2_color = tk.StringVar(value="black")
            tk.OptionMenu(form_frame, self.p2_color, "white", "black").grid(row=4, column=1, pady=10)

        # Timer dropdown
        tk.Label(form_frame, text="Timer (minutes):", font=("Arial", 14), bg="#3B3B29", fg="white").grid(row=5, column=0, sticky="e", pady=10)
        self.timer_choice = tk.StringVar(value="5")
        tk.OptionMenu(form_frame, self.timer_choice, "1", "3", "5", "10", "15", "30").grid(row=5, column=1, pady=10)

        # Start Game button
        tk.Button(self.root, text="Start Game", font=("Arial", 14, "bold"),
                  bg="orange", fg="black", command=self.start_game).pack(pady=(20, 10))

        # ✅ Return to Home button added
        tk.Button(self.root, text="Return to Home", font=("Arial", 12),
                  bg="white", fg="black", command=self.return_home).pack(pady=(0, 20))

    # Helper method to create styled entry fields
    def entry_box(self, parent):
        return tk.Entry(parent, font=("Arial", 14))

    # Handle logic when "Start Game" is pressed
    def start_game(self):
        game_name = self.game_name_entry.get().strip() or "My Match"
        p1 = self.p1_name_entry.get().strip() or "Player 1"
        p1_color = self.p1_color.get()
        minutes = int(self.timer_choice.get())

        if self.mode == "human":
            p2 = self.p2_name_entry.get().strip() or "Player 2"
            p2_color = self.p2_color.get()

            # Prevent both players from selecting the same color
            if p1_color == p2_color:
                messagebox.showerror("Color Conflict", "Player 1 and Player 2 cannot have the same color.")
                return
        else:
            p2 = "AI Bot"
            p2_color = "black" if p1_color == "white" else "white"

        # Launch the game
        game_class = ChessGame if self.game_type == "chess" else CheckersGame
        game_class(
            self.root,
            player1=p1,
            player2=p2,
            player1_color=p1_color,
            time_minutes=minutes,
            mode=self.mode,
            game_name=game_name,
            on_exit=self.return_home,
            theme=self.theme
        )

    # Clear the entire screen (destroy all widgets)
    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
