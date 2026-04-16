import tkinter as tk

class RulesScreen:
    def __init__(self, root, go_back_callback=None, game_type="chess"):
        self.root = root
        self.go_back_callback = go_back_callback  # Function to return to the previous screen
        self.game_type = game_type  # 'chess' or 'checkers'
        self.build_ui()  # Build the rules UI when initialized

    # Build the visual interface for the rules screen
    def build_ui(self):
        self.clear_screen()
        self.root.configure(bg="#3B3B29")

        # Title Label: Shows "Chess Rules" or "Checkers Rules"
        tk.Label(
            self.root,
            text=f"{self.game_type.capitalize()} Rules",
            font=("Papyrus", 26, "bold"),
            fg="white", bg="#3B3B29"
        ).pack(pady=20)

        # Display the rules text depending on game type
        rules = self.get_rules()
        tk.Label(
            self.root,
            text=rules,
            font=("Arial", 13),
            wraplength=700,
            fg="lightyellow",
            bg="#3B3B29",
            justify="left"
        ).pack(padx=30, pady=10)

        # Back Button to return to previous screen
        tk.Button(
            self.root,
            text="⬅ Back",
            font=("Arial", 12),
            bg="orange",
            command=self.go_back_callback
        ).pack(pady=15)

    # Return a rules string based on the selected game type
    def get_rules(self):
        if self.game_type == "checkers":
            return (
                "🪙 CHECKERS RULES:\n"
                "- Each player has 12 pieces.\n"
                "- Move diagonally forward on dark squares.\n"
                "- Jump opponent to capture.\n"
                "- Reach the last row to become a King.\n"
                "- Only Kings can move backward.\n"
                "- Game ends when opponent has no valid pieces or moves."
            )
        else:
            return (
                "♟ CHESS RULES:\n"
                "- Each player starts with 16 pieces.\n"
                "- Capture the opponent’s King via checkmate.\n"
                "- Special rules: Castling, En Passant, Promotion.\n"
                "- Kings cannot move into check.\n"
                "- Voice moves supported (e.g., 'E2 to E4')."
            )

    # Remove all widgets from the screen (used when redrawing)
    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()