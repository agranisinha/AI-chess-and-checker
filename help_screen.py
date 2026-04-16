import tkinter as tk

class HelpScreen:
    def __init__(self, root, go_back_callback=None):
        self.root = root
        self.go_back_callback = go_back_callback  # Callback to return to the previous screen
        self.build_ui()  # Build the help screen UI upon initialization

    # Construct the UI layout and content
    def build_ui(self):
        self.clear_screen()
        self.root.configure(bg="#3B3B29")  # Set background color

        # 🆘 Title label
        tk.Label(
            self.root,
            text="🆘 HELP",
            font=("Papyrus", 26, "bold"),
            fg="white",
            bg="#3B3B29"
        ).pack(pady=20)

        # 📝 Help instructions and feature guide
        content = (
            "Welcome to the Real Wizards Arena!\n\n"
            "🎮 How to Play:\n"
            "- Select 'Chess' or 'Checkers' on the home screen.\n"
            "- Choose your Hogwarts House theme.\n"
            "- Pick game mode: You vs Player or You vs AI.\n"
            "- Enter names, colors, and timer in setup screen.\n\n"
            "📢 Voice Commands:\n"
            "- Press 🎙️ Voice Command in Chess to say moves (e.g., 'E2 to E4').\n"
            "- Checkers voice moves are coming soon!\n\n"
            "🛑 In-Game Controls:\n"
            "- Use 'Resign' to quit early.\n"
            "- 'Offer Draw' to propose a draw.\n"
            "- 'Return to Home' is only allowed after game ends.\n\n"
            "✨ Let the magic of strategy unfold!"
        )

        # Display the content in a styled label
        tk.Label(
            self.root,
            text=content,
            font=("Arial", 12),
            fg="lightyellow",
            bg="#3B3B29",
            justify="left",
            wraplength=700
        ).pack(padx=40, pady=10)

        # 🔙 Back button to return to the previous screen
        tk.Button(
            self.root,
            text="⬅ Back",
            font=("Arial", 12, "bold"),
            bg="orange",
            command=self.go_back
        ).pack(pady=20)

    # Callback trigger when back button is clicked
    def go_back(self):
        if self.go_back_callback:
            self.go_back_callback()

    # Clear all widgets from the window before redrawing
    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
