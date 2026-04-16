import tkinter as tk
from player_setup import PlayerSetup
from help_screen import HelpScreen
from rules_screen import RulesScreen
from tutorials_screen import TutorialsScreen
from battle_log import show_battle_log
from ai_player_setup import AIPlayerSetup

class GameLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("🧙‍♂️ Real Wizards Arena")           # Set window title
        self.root.geometry("1280x720")                      # Set fixed window size
        self.root.configure(bg="#3B3B29")                   # Background color
        self.selected_game = "chess"                        # Default game
        self.selected_theme = "Gryffindor"                  # Default theme
        self.setup_ui()                                     # Build UI on launch

    # Build the main launcher screen
    def setup_ui(self):
        self.clear_screen()
        # App title
        tk.Label(self.root, text="🧙‍♂️ Real Wizards Arena", font=("Papyrus", 28, "bold"),
                 fg="white", bg="#3B3B29").pack(pady=20)

        # Center preview canvas (shows sample board)
        self.board_canvas = tk.Canvas(self.root, width=480, height=480, bg="#3B3B29", highlightthickness=0)
        self.board_canvas.place(relx=0.5, rely=0.52, anchor=tk.CENTER)
        self.draw_game_preview()  # Draw default preview board

        # 🎮 Left panel for game settings
        left_frame = tk.Frame(self.root, bg="#3B3B29")
        left_frame.place(relx=0.07, rely=0.5, anchor="center")

        # Game type buttons
        tk.Label(left_frame, text="🎮 Game Mode", font=("Arial", 14, "bold"), bg="#3B3B29", fg="lightblue").pack(pady=5)
        self.bubble_button(left_frame, "♟️ Chess", lambda: self.select_game("chess")).pack(pady=10)
        self.bubble_button(left_frame, "🪙 Checkers", lambda: self.select_game("checkers")).pack(pady=10)

        # House theme selector
        tk.Label(left_frame, text="🧙 House Theme", font=("Arial", 14, "bold"), bg="#3B3B29", fg="lightblue").pack(pady=5)
        for house in ["Gryffindor", "Slytherin", "Ravenclaw", "Hufflepuff"]:
            self.bubble_button(left_frame, house, lambda h=house: self.select_theme(h)).pack(pady=2)

        # Play mode (vs Player or vs AI)
        tk.Label(left_frame, text="🎯 Play Mode", font=("Arial", 14, "bold"), bg="#3B3B29", fg="lightblue").pack(pady=5)
        self.bubble_button(left_frame, "YOU VS 👨", lambda: self.launch_setup("human")).pack(pady=10)
        self.bubble_button(left_frame, "YOU VS 🤖", lambda: self.launch_setup("ai")).pack(pady=10)

        # 📜 Right panel for info/help screens
        right_frame = tk.Frame(self.root, bg="#3B3B29")
        right_frame.place(relx=0.93, rely=0.5, anchor="center")

        self.bubble_button(right_frame, "HELP ❓", self.open_help).pack(pady=10)
        self.bubble_button(right_frame, "RULES 📜", self.open_rules).pack(pady=10)
        self.bubble_button(right_frame, "TUTORIALS 🎓", self.open_tutorials).pack(pady=10)
        self.bubble_button(right_frame, "BATTLE LOG 🗒️", lambda: show_battle_log(self.root, go_back_callback=self.setup_ui)).pack(pady=10)

    # Create a stylized button used for all menus
    def bubble_button(self, parent, text, command):
        return tk.Button(parent, text=text, font=("Helvetica", 14, "bold"), width=15, height=2,
                         bg="#D5D8DC", fg="black", relief="groove", bd=3, command=command)

    # Set the selected game type (chess or checkers)
    def select_game(self, game_type):
        self.selected_game = game_type
        self.draw_game_preview()

    # Set the selected house theme
    def select_theme(self, house):
        self.selected_theme = house
        self.draw_game_preview()

    # Draw preview of the selected game (chess or checkers) with selected theme
    def draw_game_preview(self):
        self.board_canvas.delete("all")
        square_size = 60

        theme_colors = {
            "Gryffindor": ["#740001", "#D3A625"],
            "Slytherin": ["#1A472A", "#AAAAAA"],
            "Ravenclaw": ["#0E1A40", "#946B2D"],
            "Hufflepuff": ["#D7C755", "#3C3C3C"]
        }

        colors = theme_colors.get(self.selected_theme, ["#EEEED2", "#769656"])

        # Draw the 8x8 board with squares and pieces
        for row in range(8):
            for col in range(8):
                x1, y1 = col * square_size, row * square_size
                x2, y2 = x1 + square_size, y1 + square_size
                color = colors[(row + col) % 2]
                self.board_canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=color)

                if self.selected_game == "chess":
                    piece = ""
                    if row == 0:
                        piece = ["♜", "♞", "♝", "♛", "♚", "♝", "♞", "♜"][col]
                    elif row == 1:
                        piece = "♟"
                    elif row == 6:
                        piece = "♙"
                    elif row == 7:
                        piece = ["♖", "♘", "♗", "♕", "♔", "♗", "♘", "♖"][col]
                    if piece:
                        self.board_canvas.create_text(x1 + 30, y1 + 30, text=piece, font=("Arial", 22))
                elif self.selected_game == "checkers":
                    if (row + col) % 2 == 1:
                        if row < 3:
                            self.board_canvas.create_oval(x1 + 10, y1 + 10, x2 - 10, y2 - 10, fill="black")
                        elif row > 4:
                            self.board_canvas.create_oval(x1 + 10, y1 + 10, x2 - 10, y2 - 10, fill="white")

    # Launch player setup screen for selected mode (AI or human)
    def launch_setup(self, mode):
        self.clear_screen()
        PlayerSetup(
            root=self.root,
            game_type=self.selected_game,
            theme=self.selected_theme,
            mode=mode,  # "ai" or "human"
            return_home=self.setup_ui
        )

    # Open help screen
    def open_help(self):
        self.clear_screen()
        HelpScreen(self.root, go_back_callback=self.setup_ui)

    # Open rules screen for selected game
    def open_rules(self):
        self.clear_screen()
        RulesScreen(self.root, go_back_callback=self.setup_ui, game_type=self.selected_game)
    
    # Open tutorials screen for selected game
    def open_tutorials(self):
        self.clear_screen()
        TutorialsScreen(self.root, go_back_callback=self.setup_ui, game_type=self.selected_game)
    
    # Show the battle log screen
    def show_log(self):
        show_battle_log(self.root, go_back_callback=self.setup_ui)

    # Clear all widgets from the current screen
    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

# 🔁 Launch the game if this file is run directly
if __name__ == "__main__":
    root = tk.Tk()
    app = GameLauncher(root)
    root.mainloop()
