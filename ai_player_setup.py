import tkinter as tk
from chess_game import ChessGame
from checkers_game import CheckersGame

class AIPlayerSetup:
    def __init__(self, root, game_type="chess"):
        self.root = root
        self.game_type = game_type  # "chess" or "checkers"
        self.root.configure(bg="#3B3B29")  # Set background color
        self.build_ui()  # Build UI on initialization

    # Build the UI layout for setting up an AI game
    def build_ui(self):
        self.clear_screen()

        # Title label
        tk.Label(self.root, text="AI GAME SETUP", font=("Papyrus", 26, "bold"),
                 fg="white", bg="#3B3B29").pack(pady=20)

        # Frame to hold the form inputs
        form_frame = tk.Frame(self.root, bg="#3B3B29")
        form_frame.pack(pady=10)

        # Game name input
        tk.Label(form_frame, text="Game Name:", font=("Arial", 14), bg="#3B3B29", fg="white").grid(row=0, column=0, sticky="e", pady=10)
        self.game_name = self.entry_box(form_frame)
        self.game_name.grid(row=0, column=1, pady=10)

        # Player name input
        tk.Label(form_frame, text="Player Name:", font=("Arial", 14), bg="#3B3B29", fg="white").grid(row=1, column=0, sticky="e", pady=10)
        self.player_name = self.entry_box(form_frame)
        self.player_name.grid(row=1, column=1, pady=10)

        # Color choice dropdown
        tk.Label(form_frame, text="Choose Color:", font=("Arial", 14), bg="#3B3B29", fg="white").grid(row=2, column=0, sticky="e", pady=10)
        self.player_color = tk.StringVar(value="white")
        tk.OptionMenu(form_frame, self.player_color, "white", "black").grid(row=2, column=1, pady=10)

        # Timer dropdown
        tk.Label(form_frame, text="Timer (minutes):", font=("Arial", 14), bg="#3B3B29", fg="white").grid(row=3, column=0, sticky="e", pady=10)
        self.timer_choice = tk.StringVar(value="5")
        tk.OptionMenu(form_frame, self.timer_choice, "1", "3", "5", "10", "15", "30").grid(row=3, column=1, pady=10)

        # Start game button
        tk.Button(self.root, text="Start Game vs AI", font=("Arial", 14, "bold"),
                  bg="white", fg="black", width=20, height=2,
                  command=self.start_game).pack(pady=25)

    # Utility function to create styled entry boxes
    def entry_box(self, parent):
        return tk.Entry(parent, font=("Arial", 14), width=20, bg="white", bd=2, relief="sunken")

    # Logic to start the game when the button is clicked
    def start_game(self):
        player_name = self.player_name.get() or "Player"
        ai_name = "AI Bot"
        color = self.player_color.get()
        game_name = self.game_name.get() or "My Match"
        time_minutes = int(self.timer_choice.get())

        # Chess logic: assign white to determine who starts
        if self.game_type == "chess":
            if color == "white":
                ChessGame(self.root, player_name, ai_name, "white", time_minutes,
                          mode="ai", game_name=game_name, on_exit=self.return_home)
            else:
                ChessGame(self.root, ai_name, player_name, "white", time_minutes,
                          mode="ai", game_name=game_name, on_exit=self.return_home)
        # Checkers logic
        else:
            CheckersGame(self.root, player_name, ai_name, time_minutes,
                         mode="ai", game_name=game_name)

    # Remove all widgets from the screen
    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # Return to the main launcher
    def return_home(self):
        from main import GameLauncher
        GameLauncher(self.root)
