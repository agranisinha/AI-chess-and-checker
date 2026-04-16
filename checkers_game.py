import tkinter as tk
import time, threading, re, speech_recognition as sr, pyttsx3
from tkinter import messagebox
from battle_log import add_to_history, update_stats, get_stats

# Theme color definitions for each house
THEME_COLORS = {
    "Gryffindor": ["#740001", "#D3A625"],
    "Slytherin": ["#1A472A", "#AAAAAA"],
    "Ravenclaw": ["#0E1A40", "#946B2D"],
    "Hufflepuff": ["#D7C755", "#3C3C3C"]
}

class CheckersGame:
    def __init__(self, root, player1, player2, player1_color="white", time_minutes=5, mode="human", game_name="My Match", on_exit=None, theme="Gryffindor"):
        # Initialize game state variables
        self.root = root
        self.player1 = player1
        self.player2 = player2
        self.player1_color = player1_color
        self.time_left = {player1: time_minutes * 60, player2: time_minutes * 60}
        self.mode = mode
        self.game_name = game_name
        self.on_exit = on_exit
        self.theme = theme
        self.current_player = player1
        self.voice_enabled = True
        self.running = True
        self.selected = None  # Track selected piece
        self.board_state = [[""] * 8 for _ in range(8)]  # 8x8 board
        self.engine = pyttsx3.init()  # Text-to-speech engine
        self.white_captures = 0
        self.black_captures = 0

        # Setup initial board, UI, and timer
        self.setup_board()
        self.build_ui()
        self.start_timer()
        if self.is_ai_turn():
            self.root.after(1000, self.make_ai_move)

    def setup_board(self):
        # Place initial black and white pieces on the board
        for r in range(3):
            for c in range(8):
                if (r + c) % 2 == 1:
                    self.board_state[r][c] = "B" if self.player1_color == "white" else "W"
        for r in range(5, 8):
            for c in range(8):
                if (r + c) % 2 == 1:
                    self.board_state[r][c] = "W" if self.player1_color == "white" else "B"

    def get_player_symbol(self):
        # Return "W" or "B" depending on current player's assigned color
        return "W" if self.current_player == self.player1 else "B"

    def build_ui(self):
        # Build the game screen layout
        self.clear_screen()
        self.root.configure(bg="#3B3B29")

        # Display game name
        tk.Label(self.root, text=f"Game: {self.game_name}", font=("Arial", 18, "bold"),
                 bg="#3B3B29", fg="white").pack(pady=(10, 5))

        # Create frame for board and side panel
        main_frame = tk.Frame(self.root, bg="#3B3B29")
        main_frame.pack(pady=10)

        # Create board canvas
        board_frame = tk.Frame(main_frame)
        board_frame.pack(side="left")
        self.canvas = tk.Canvas(board_frame, width=480, height=480, bg="#3B3B29", highlightthickness=0)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_board_click)

        # Info panel (right side)
        info_frame = tk.Frame(main_frame, bg="#3B3B29")
        info_frame.pack(side="right", padx=20)

        # Player info, timers, score display
        self.info_label = tk.Label(info_frame, text="", font=("Arial", 12), bg="#3B3B29", fg="lightgreen", justify="left")
        self.info_label.pack(pady=10)

        # Show whose turn it is
        self.status_label = tk.Label(info_frame, text=f"Turn: {self.current_player}", font=("Arial", 14),
                                     bg="#3B3B29", fg="yellow")
        self.status_label.pack(pady=10)

        # Buttons for speaking move, resigning, exiting
        tk.Button(info_frame, text="🎙️ Speak Move", font=("Arial", 12), bg="orange", command=self.listen_for_move).pack(pady=5)
        tk.Button(info_frame, text="Resign", font=("Arial", 12), bg="white", command=self.resign).pack(pady=5)
        tk.Button(info_frame, text="Offer Draw", font=("Arial", 12), bg="white", command=self.offer_draw).pack(pady=5)  
        tk.Button(info_frame, text="Return to Home", font=("Arial", 12), bg="white", command=self.exit_game).pack(pady=5)

        # Draw board and update info
        self.draw_board()
        self.update_info_display()

    def update_info_display(self):
        try:
            # Format remaining time for each player
            p1_time = self.format_time(self.time_left[self.player1])
            p2_time = self.format_time(self.time_left[self.player2])
            p1_score = self.white_captures
            p2_score = self.black_captures
    
            # Determine display symbols based on color
            p1_symbol = "⚪" if self.player1_color == "white" else "⚫"
            p2_symbol = "⚫" if self.player1_color == "white" else "⚪"
    
            # Update the label text safely
            self.info_label.config(
                text=f"{p1_symbol} {self.player1}\n⏱ {p1_time} | 🏁 Score: {p1_score}\n\n"
                     f"{p2_symbol} {self.player2}\n⏱ {p2_time} | 🏁 Score: {p2_score}"
            )
        except tk.TclError:
            # Widget was destroyed (e.g., during screen change), ignore safely
            pass

    def offer_draw(self):
        if not self.running:
            return
        accepted = messagebox.askyesno("Offer Draw", "Do both players agree to a draw?")
        if accepted:
            self.running = False
            messagebox.showinfo("Draw", "Game ended in a draw.")
            add_to_history({
                "name": self.game_name,
                "type": "checkers",
                "result": "Draw",
                "moves": self.white_captures + self.black_captures
            })
            update_stats("checkers", "Draw")
            if self.on_exit:
                self.on_exit()


    def draw_board(self):
        # Draw the checkers board with pieces and coordinates
        square_size = 60
        files = "ABCDEFGH"
        colors = THEME_COLORS.get(self.theme, ["#EEEED2", "#769656"])
        self.canvas.delete("all")

        for row in range(8):
            for col in range(8):
                x1, y1 = col * square_size, row * square_size
                x2, y2 = x1 + square_size, y1 + square_size
                color = colors[(row + col) % 2]
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=color)
                piece = self.board_state[row][col]
                if piece:
                    fill = "white" if piece.startswith("W") else "black"
                    king = "👑" if piece.endswith("K") else ""
                    self.canvas.create_oval(x1+10, y1+10, x2-10, y2-10, fill=fill)
                    self.canvas.create_text(x1+30, y1+30, text=king, fill="gold", font=("Arial", 14))

        # Label rows and columns
        for i in range(8):
            self.canvas.create_text(i * square_size + 30, 8 * square_size + 10, text=files[i], fill="white", font=("Arial", 10))
            self.canvas.create_text(i * square_size + 30, 10, text=files[i], fill="white", font=("Arial", 10))
            self.canvas.create_text(10, i * square_size + 30, text=str(8 - i), fill="white", font=("Arial", 10))
            self.canvas.create_text(480 - 10, i * square_size + 30, text=str(8 - i), fill="white", font=("Arial", 10))

    def format_time(self, seconds):
        # Convert seconds to MM:SS format
        return f"{seconds // 60:02}:{seconds % 60:02}"

    def on_board_click(self, event):
        # Handle mouse clicks to select and move pieces
        if self.is_ai_turn() or not self.running:
            return
        row, col = event.y // 60, event.x // 60
        if self.selected:
            sr, sc = self.selected
            if self.valid_move(sr, sc, row, col):
                self.move_piece(sr, sc, row, col)
                self.selected = None
            else:
                self.speak("Invalid move.")
                self.selected = None
        elif self.board_state[row][col].startswith(self.get_player_symbol()):
            self.selected = (row, col)
            self.speak("Piece selected.")

    def valid_move(self, sr, sc, dr, dc):
        # Validate if a move is legal (basic + capture)
        piece = self.board_state[sr][sc]
        if self.board_state[dr][dc] != "":
            return False
        dr_step = dr - sr
        dc_step = abs(dc - sc)
        if dc_step != 1 and dc_step != 2:
            return False
        direction = -1 if piece.startswith("W") else 1
        is_king = piece.endswith("K")

        if dc_step == 1 and (dr_step == direction or (is_king and abs(dr_step) == 1)):
            return True

        if dc_step == 2:
            mid_r = (sr + dr) // 2
            mid_c = (sc + dc) // 2
            mid_piece = self.board_state[mid_r][mid_c]
            if mid_piece and not mid_piece.startswith(self.get_player_symbol()):
                if dr_step == 2 * direction or (is_king and abs(dr_step) == 2):
                    return True

        return False

    def move_piece(self, sr, sc, dr, dc):
        # Move a piece and handle capture/promotion
        piece = self.board_state[sr][sc]
        self.board_state[dr][dc] = piece
        self.board_state[sr][sc] = ""

        if abs(dr - sr) == 2:
            mid_r = (sr + dr) // 2
            mid_c = (sc + dc) // 2
            captured = self.board_state[mid_r][mid_c]
            self.board_state[mid_r][mid_c] = ""
            if captured.startswith("W"):
                self.white_captures += 1
            else:
                self.black_captures += 1

        self.update_info_display()

        if piece == "W" and dr == 0:
            self.board_state[dr][dc] = "WK"
        elif piece == "B" and dr == 7:
            self.board_state[dr][dc] = "BK"

        self.draw_board()
        if self.check_win_condition():
            return
        self.switch_turn()

    def switch_turn(self):
        # Change current player and update status
        self.current_player = self.player2 if self.current_player == self.player1 else self.player1
        self.status_label.config(text=f"Turn: {self.current_player}")
        if self.is_ai_turn():
            self.root.after(1000, self.make_ai_move)

    def is_ai_turn(self):
        return self.mode == "ai" and self.current_player == "AI Bot"

    def make_ai_move(self):
        # Simple AI: prioritize captures, then any move
        for sr in range(8):
            for sc in range(8):
                if self.board_state[sr][sc].startswith("B"):
                    for dr in range(8):
                        for dc in range(8):
                            if self.valid_move(sr, sc, dr, dc) and abs(dr - sr) == 2:
                                self.move_piece(sr, sc, dr, dc)
                                return
        for sr in range(8):
            for sc in range(8):
                if self.board_state[sr][sc].startswith("B"):
                    for dr in range(8):
                        for dc in range(8):
                            if self.valid_move(sr, sc, dr, dc):
                                self.move_piece(sr, sc, dr, dc)
                                return
        self.speak("AI has no valid moves.")

    def check_win_condition(self):
        # Check for win (no remaining opponent pieces)
        pieces = [p for row in self.board_state for p in row if p]
        w_pieces = [p for p in pieces if p.startswith("W")]
        b_pieces = [p for p in pieces if p.startswith("B")]

        if not w_pieces:
            self.end_game(f"{self.player2} wins!")
            return True
        elif not b_pieces:
            self.end_game(f"{self.player1} wins!")
            return True
        return False

    def end_game(self, msg):
        # Finalize the game and log result
        self.running = False
        messagebox.showinfo("Game Over", msg)
        add_to_history({
            "name": self.game_name,
            "type": "checkers",
            "result": msg,
            "moves": self.white_captures + self.black_captures
        })
        update_stats("checkers", msg)
        if self.on_exit:
            self.on_exit()

    def resign(self):
        # Resign and declare opponent as winner
        if not self.running:
            return
        loser = self.current_player
        winner = self.player2 if loser == self.player1 else self.player1
        self.end_game(f"{winner} wins by resignation")

    def listen_for_move(self):
        if not self.voice_enabled or not self.running:
            return
        try:
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                self.speak("Listening...")
                audio = recognizer.listen(source, timeout=5)
                command = recognizer.recognize_google(audio)
                self.speak(f"You said: {command}")
                self.process_voice_move(command)
        except:
            self.speak("Could not understand. Please try again.")
    
    def process_voice_move(self, command):
        import re
        match = re.findall(r"[a-hA-H][1-8]", command)
        if len(match) >= 2:
            sr, sc = 8 - int(match[0][1]), ord(match[0][0].lower()) - ord('a')
            dr, dc = 8 - int(match[1][1]), ord(match[1][0].lower()) - ord('a')
            if self.valid_move(sr, sc, dr, dc):
                self.move_piece(sr, sc, dr, dc)
                return
        self.speak("Invalid move.")


    def speak(self, text):
        # Speak out text using TTS
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except:
            pass

    def start_timer(self):
        def update():
            while self.running:
                time.sleep(1)
                self.time_left[self.current_player] -= 1
                if self.time_left[self.current_player] <= 0:
                    self.running = False
                    winner = self.player2 if self.current_player == self.player1 else self.player1
                    msg = f"{winner} wins by timeout!"
                    try:
                        messagebox.showinfo("Time Out", msg)
                    except:
                        pass
                    add_to_history({
                        "name": self.game_name,
                        "type": "checkers",
                        "result": msg,
                        "moves": self.white_captures + self.black_captures
                    })
                    update_stats("checkers", msg)
                    if self.on_exit:
                        self.on_exit()
                    return
                try:
                    self.update_info_display()
                except:
                    break
        threading.Thread(target=update, daemon=True).start()

    def exit_game(self):
        # Exit to main menu only after game ends
        if self.running:
            messagebox.showwarning("Warning", "Finish or resign the game before exiting.")
            return
        if self.on_exit:
            self.on_exit()

    def clear_screen(self):
        # Remove all UI widgets
        for widget in self.root.winfo_children():
            widget.destroy()
