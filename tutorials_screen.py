import tkinter as tk

class TutorialsScreen:
    def __init__(self, root, go_back_callback=None, game_type="chess"):
        self.root = root
        self.go_back_callback = go_back_callback  # Function to go back to previous menu
        self.game_type = game_type  # "chess" or "checkers"
        self.build_ui()  # Build the tutorials interface on initialization

    # Build the full UI for the tutorial screen
    def build_ui(self):
        self.clear_screen()
        self.root.configure(bg="#3B3B29")  # Set background color

        # Title Label showing "Chess Tutorials" or "Checkers Tutorials"
        tk.Label(
            self.root,
            text=f"{self.game_type.capitalize()} Tutorials",
            font=("Papyrus", 26, "bold"),
            fg="white",
            bg="#3B3B29"
        ).pack(pady=20)

        # Tutorial instructions text (pulled from get_tutorial_text)
        text = self.get_tutorial_text()
        tk.Label(
            self.root,
            text=text,
            font=("Arial", 13),
            wraplength=700,
            fg="lightyellow",
            bg="#3B3B29",
            justify="left"
        ).pack(padx=30, pady=10)

        # Back button to return to previous screen
        tk.Button(
            self.root,
            text="⬅ Back",
            font=("Arial", 12),
            bg="orange",
            command=self.go_back_callback
        ).pack(pady=15)

    # Return a tutorial string based on the selected game type
    def get_tutorial_text(self):
        if self.game_type == "checkers":
            return (
                "🪙 CHECKERS TUTORIAL:\n"
                "- Click to select a piece.\n"
                "- Click again to move to a valid square.\n"
                "- Capture opponents by jumping over them.\n"
                "- If you can jump, you must jump.\n"
                "- Reach the opposite end to get a King.\n"
                "- Kings move forward and backward."
            )
        else:
            return (
                "♟ CHESS TUTORIAL:\n"
                "- Click a piece to select.\n"
                "- Click another square to move.\n"
                "- Use legal rules: pawns forward, knights L-shape, etc.\n"
                "- Promote pawns on the last row.\n"
                "- Use 'Speak Move' button to say 'E2 to E4'."
            )

    # Clears all widgets from the root window (used before redrawing)
    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
