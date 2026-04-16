import tkinter as tk
import time, threading, random, re
import speech_recognition as sr
import pyttsx3
from tkinter import messagebox, simpledialog
from battle_log import add_to_history, update_stats, get_stats

# Define piece values for AI evaluation and scoring
PIECE_VALUES = {
    "♙": 1, "♟": 1,
    "♘": 3, "♞": 3,
    "♗": 3, "♝": 3,
    "♖": 5, "♜": 5,
    "♕": 9, "♛": 9,
    "♔": 100, "♚": 100
}

# Define board colors by theme
THEME_COLORS = {
    "Gryffindor": ["#740001", "#D3A625"],
    "Slytherin": ["#1A472A", "#AAAAAA"],
    "Ravenclaw": ["#0E1A40", "#946B2D"],
    "Hufflepuff": ["#D7C755", "#3C3C3C"]
}

class ChessGame:
    def __init__(self, root, player1, player2, player1_color, time_minutes, mode="human", game_name="My Match", on_exit=None, theme="Gryffindor"):
        # Game and player setup
        self.root = root
        self.player1 = player1
        self.player2 = player2
        self.player1_color = player1_color
        self.time_left = {player1: time_minutes * 60, player2: time_minutes * 60}
        self.mode = mode
        self.game_name = game_name
        self.on_exit = on_exit
        self.theme = theme
        self.move_counter = {player1: 0, player2: 0}
        self.current_player = self.player1 if player1_color == "white" else self.player2
        self.voice_enabled = True
        self.running = True
        self.selected = None
        self.board_state = self.setup_initial_board()
        self.engine = pyttsx3.init()
        self.white_captures = 0
        self.black_captures = 0
        self.buttons = {}
        self.last_move = None  # Format: ((sr, sc), (dr, dc), moved_piece)


        # Setup UI and start the game
        self.build_ui()
        self.start_timer()
        if self.is_ai_turn():
            self.root.after(1000, self.make_ai_move)

    # Initialize chess pieces in standard starting positions
    def setup_initial_board(self):
        return [
            ["♜", "♞", "♝", "♛", "♚", "♝", "♞", "♜"],
            ["♟"] * 8,
            [""] * 8, [""] * 8, [""] * 8, [""] * 8,
            ["♙"] * 8,
            ["♖", "♘", "♗", "♕", "♔", "♗", "♘", "♖"],
        ]

    # Setup UI layout: board, info, controls
    def build_ui(self):
        self.clear_screen()
        self.root.configure(bg="#3B3B29")

        tk.Label(self.root, text=f"Game: {self.game_name}", font=("Arial", 18, "bold"),
                 bg="#3B3B29", fg="white").pack(pady=(10, 5))

        main_frame = tk.Frame(self.root, bg="#3B3B29")
        main_frame.pack(pady=10)

        board_frame = tk.Frame(main_frame)
        board_frame.pack(side="left")
        self.canvas = tk.Canvas(board_frame, width=480, height=480, bg="#3B3B29", highlightthickness=0)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_board_click)

        info_frame = tk.Frame(main_frame, bg="#3B3B29")
        info_frame.pack(side="right", padx=20)

        self.info_label = tk.Label(info_frame, text="", font=("Arial", 12), bg="#3B3B29", fg="lightgreen", justify="left")
        self.info_label.pack(pady=10)

        self.status_label = tk.Label(info_frame, text=f"Turn: {self.current_player}", font=("Arial", 14),
                                     bg="#3B3B29", fg="yellow")
        self.status_label.pack(pady=10)

        # Control Buttons: Speak, Resign, Return, Draw
        tk.Button(info_frame, text="🎙️ Speak Move", font=("Arial", 12), bg="orange", command=self.listen_for_move).pack(pady=5)
        tk.Button(info_frame, text="Resign", font=("Arial", 12), bg="white", command=self.resign).pack(pady=5)
        tk.Button(info_frame, text="Return to Home", font=("Arial", 12), bg="white", command=self.exit_game).pack(pady=5)
        tk.Button(info_frame, text="Offer Draw", font=("Arial", 12), bg="lightblue", command=self.offer_draw).pack(pady=5)

        self.update_info()
        self.draw_board_with_coordinates()

    def get_piece_color(self, piece):
        if piece in "♙♖♘♗♕♔":
            return "white"
        elif piece in "♟♜♞♝♛♚":
            return "black"
        return None

    def get_piece_owner(self, piece):
        if piece in "♙♖♘♗♕♔":
            return self.player1
        elif piece in "♟♜♞♝♛♚":
            return self.player2
        return None

    # Updates game info (time, moves, captures) per player
    def update_info(self):
        p1_time = self.format_time(self.time_left[self.player1])
        p2_time = self.format_time(self.time_left[self.player2])
        p1_moves = self.move_counter[self.player1]
        p2_moves = self.move_counter[self.player2]

        if self.player1_color == "white":
            p1_score = self.black_captures
            p2_score = self.white_captures
            p1_icon, p2_icon = "⚪", "⚫"
        else:
            p1_score = self.white_captures
            p2_score = self.black_captures
            p1_icon, p2_icon = "⚫", "⚪"

        self.info_label.config(
            text=f"{p1_icon} {self.player1}\n⏱ {p1_time} | 🧮 Moves: {p1_moves} | 🏁 Score: {p1_score}\n\n"
                 f"{p2_icon} {self.player2}\n⏱ {p2_time} | 🧮 Moves: {p2_moves} | 🏁 Score: {p2_score}"
        )
        self.status_label.config(text=f"Turn: {self.current_player}")

    # Renders chess board and pieces with A-H and 1-8 labels
    def draw_board_with_coordinates(self):
        square_size = 60
        files = "ABCDEFGH"
        colors = THEME_COLORS.get(self.theme, ["#EEEED2", "#769656"])
        self.canvas.delete("all")
    
        kr, kc = (-1, -1)
        if self.is_king_in_check():
            kr, kc = self.get_king_position()
    
        for row in range(8):
            for col in range(8):
                x1, y1 = col * square_size, row * square_size
                x2, y2 = x1 + square_size, y1 + square_size
    
                if (row, col) == (kr, kc):
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="red", outline="red")
                else:
                    color = colors[(row + col) % 2]
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=color)
    
                piece = self.board_state[row][col]
                if piece:
                    self.canvas.create_text(x1 + 30, y1 + 30, text=piece, font=("Arial", 24))
    
        # File and rank labels
        for i in range(8):
            self.canvas.create_text(i * square_size + 30, 8 * square_size + 10, text=files[i], fill="white", font=("Arial", 10))
            self.canvas.create_text(i * square_size + 30, 10, text=files[i], fill="white", font=("Arial", 10))
            self.canvas.create_text(10, i * square_size + 30, text=str(8 - i), fill="white", font=("Arial", 10))
            self.canvas.create_text(480 - 10, i * square_size + 30, text=str(8 - i), fill="white", font=("Arial", 10))


    def get_king_position(self):
        king = "♔" if self.current_player == self.player1 else "♚"
        for r in range(8):
            for c in range(8):
                if self.board_state[r][c] == king:
                    return r, c
        return None, None

    # Uses speech recognition to accept a move in voice format like "E2 to E4"
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
            self.speak("Could not understand. Try again.")

    # Parses the spoken move and executes it on the board
    def process_voice_move(self, command):
        match = re.findall(r"[a-hA-H][1-8]", command)
        if len(match) >= 2:
            sr, sc = 8 - int(match[0][1]), ord(match[0][0].lower()) - ord('a')
            dr, dc = 8 - int(match[1][1]), ord(match[1][0].lower()) - ord('a')
            if self.valid_move(sr, sc, dr, dc) and not self.would_cause_check(sr, sc, dr, dc):
                self.move_piece(sr, sc, dr, dc)
                return
        self.speak("Invalid move.")

    # Offer draw dialog logic
    def offer_draw(self):
        if messagebox.askyesno("Draw Offer", "Do both players agree to a draw?"):
            self.running = False
            messagebox.showinfo("Draw", "Game ended in a draw.")
            add_to_history({
                        "name": self.game_name,
                        "type": "chess",
                        "result": "Draw",
                        "moves": self.move_counter[self.player1] + self.move_counter[self.player2]
                    })
            update_stats("chess", "Draw")
            if self.on_exit:
                self.on_exit()
    # Handle mouse clicks to select and move pieces
    def on_board_click(self, event):
        if self.is_ai_turn() or not self.running:
            return
    
        row, col = event.y // 60, event.x // 60
    
        if self.selected:
            sr, sc = self.selected
            if self.valid_move(sr, sc, row, col) and not self.would_cause_check(sr, sc, row, col):
                self.move_piece(sr, sc, row, col)
            else:
                self.speak("Invalid move.")
            self.selected = None
            self.legal_moves = []
            self.draw_board_with_coordinates()
        elif self.is_own_piece(row, col):
            self.selected = (row, col)
            self.legal_moves = []
            for r in range(8):
                for c in range(8):
                    if self.valid_move(row, col, r, c) and not self.would_cause_check(row, col, r, c):
                        # 👇 NEW check: only allow moves that resolve check
                        if not self.is_king_in_check() or not self.move_causes_king_remain_in_check(row, col, r, c):
                            self.legal_moves.append((r, c))
            self.speak(f"{self.board_state[row][col]} selected.")
            self.draw_board_with_coordinates()

    def is_king_in_check(self):
        return self.king_in_check(self.current_player, self.board_state)


    def move_causes_king_remain_in_check(self, sr, sc, dr, dc):
        backup = [row.copy() for row in self.board_state]
        piece = self.board_state[sr][sc]
        captured = self.board_state[dr][dc]
    
        # Make the hypothetical move
        self.board_state[dr][dc] = piece
        self.board_state[sr][sc] = ""
    
        in_check = self.is_king_in_check()
    
        # Revert the board
        self.board_state = backup
        return in_check

    # AI checks if it's its turn to move
    def is_ai_turn(self):
        return self.mode == "ai" and self.current_player == self.player2

    # Executes the AI move based on best capture
    def make_ai_move(self):
        if not self.running:
            return

        best_score = -float("inf")
        best_moves = []

        for sr in range(8):
            for sc in range(8):
                if self.is_own_piece(sr, sc):
                    for dr in range(8):
                        for dc in range(8):
                            if self.valid_move(sr, sc, dr, dc) and not self.would_cause_check(sr, sc, dr, dc):
                                target = self.board_state[dr][dc]
                                score = PIECE_VALUES.get(target, 0)

                                if score > best_score:
                                    best_score = score
                                    best_moves = [(sr, sc, dr, dc)]
                                elif score == best_score:
                                    best_moves.append((sr, sc, dr, dc))

        if best_moves:
            move = random.choice(best_moves)
            self.move_piece(*move)
            self.update_info()

    # Executes the piece move and updates the board
    def move_piece(self, sr, sc, dr, dc):
        piece = self.board_state[sr][sc]
        target = self.board_state[dr][dc]
    
        # Handle en passant
        if piece in ["♙", "♟"] and abs(sc - dc) == 1 and not target:
            if piece == "♙" and sr == 3:
                target = self.board_state[dr + 1][dc]
                self.board_state[dr + 1][dc] = ""
            elif piece == "♟" and sr == 4:
                target = self.board_state[dr - 1][dc]
                self.board_state[dr - 1][dc] = ""
    
        # Save last move
        self.last_move = (sr, sc, dr, dc, piece)
    
        # Execute move
        self.board_state[dr][dc] = piece
        self.board_state[sr][sc] = ""
    
        # Captures
        if target:
            if target in "♙♖♘♗♕♔":
                self.black_captures += 1
            else:
                self.white_captures += 1
    
        # Pawn promotion
        if piece == "♙" and dr == 0:
            self.board_state[dr][dc] = "♕"
        elif piece == "♟" and dr == 7:
            self.board_state[dr][dc] = "♛"
    
        # Castling move rook
        if piece == "♔":
            if (sr, sc, dr, dc) == (7, 4, 7, 6):  # White kingside
                self.board_state[7][7] = ""
                self.board_state[7][5] = "♖"
            elif (sr, sc, dr, dc) == (7, 4, 7, 2):  # White queenside
                self.board_state[7][0] = ""
                self.board_state[7][3] = "♖"
        elif piece == "♚":
            if (sr, sc, dr, dc) == (0, 4, 0, 6):  # Black kingside
                self.board_state[0][7] = ""
                self.board_state[0][5] = "♜"
            elif (sr, sc, dr, dc) == (0, 4, 0, 2):  # Black queenside
                self.board_state[0][0] = ""
                self.board_state[0][3] = "♜"
    
        # Update castling rights
        if piece == "♔":
            self.castling_rights["white_kingside"] = False
            self.castling_rights["white_queenside"] = False
        elif piece == "♚":
            self.castling_rights["black_kingside"] = False
            self.castling_rights["black_queenside"] = False
        elif piece == "♖" and sr == 7:
            if sc == 0:
                self.castling_rights["white_queenside"] = False
            elif sc == 7:
                self.castling_rights["white_kingside"] = False
        elif piece == "♜" and sr == 0:
            if sc == 0:
                self.castling_rights["black_queenside"] = False
            elif sc == 7:
                self.castling_rights["black_kingside"] = False
    
        self.move_counter[self.current_player] += 1
        self.update_info()
        self.draw_board_with_coordinates()
    
        if not self.has_legal_moves():
            if self.is_king_in_check():
                winner = self.get_opponent()
                messagebox.showinfo("Checkmate!", f"{winner} wins.")
                add_to_history({
                    "name": self.game_name,
                    "type": "chess",
                    "result": f"{winner} wins by checkmate",
                    "moves": self.move_counter[self.player1] + self.move_counter[self.player2]
                })
                update_stats("chess", f"{winner} wins by checkmate")
            else:
                messagebox.showinfo("Stalemate", "The game is a draw by stalemate.")
                add_to_history({
                    "name": self.game_name,
                    "type": "chess",
                    "result": "Draw by stalemate",
                    "moves": self.move_counter[self.player1] + self.move_counter[self.player2]
                })
                update_stats("chess", "Draw by stalemate")
            self.running = False
            if self.on_exit:
                self.on_exit()
            return
    
        self.switch_turn()


    # Checks if current player's king is in check
    def king_in_check(self, player, board):
        king_symbol = "♔" if player == self.player1 else "♚"
        enemy_color = self.player2 if player == self.player1 else self.player1
    
        # Find king position
        for r in range(8):
            for c in range(8):
                if board[r][c] == king_symbol:
                    king_pos = (r, c)
                    break
    
        # Check all opponent's pieces if they can move to king_pos
        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece != "" and self.get_piece_color(piece) != self.get_piece_color(king_symbol):
                    if self.simulated_valid_move(r, c, king_pos[0], king_pos[1], board):
                        return True
        return False

    def simulated_valid_move(self, sr, sc, dr, dc, board):
        piece = board[sr][sc]
        delta_r, delta_c = dr - sr, dc - sc
        abs_r, abs_c = abs(delta_r), abs(delta_c)
    
        def clear_path():
            step_r = (delta_r > 0) - (delta_r < 0)
            step_c = (delta_c > 0) - (delta_c < 0)
            r, c = sr + step_r, sc + step_c
            while (r, c) != (dr, dc):
                if board[r][c] != "":
                    return False
                r += step_r
                c += step_c
            return True
    
        if piece in ["♙", "♟"]:
            direction = -1 if piece == "♙" else 1
            if dr == sr + direction and abs(sc - dc) == 1:
                return True
    
        elif piece in ["♖", "♜"] and (sr == dr or sc == dc):
            return clear_path()
    
        elif piece in ["♗", "♝"] and abs_r == abs_c:
            return clear_path()
    
        elif piece in ["♕", "♛"] and (sr == dr or sc == dc or abs_r == abs_c):
            return clear_path()
    
        elif piece in ["♘", "♞"]:
            return (abs_r, abs_c) in [(2, 1), (1, 2)]
    
        elif piece in ["♔", "♚"]:
            return max(abs_r, abs_c) == 1
    
        return False


    # Determines whether player has any valid legal move left
    def has_legal_moves(self):
        for sr in range(8):
            for sc in range(8):
                piece = self.board_state[sr][sc]
                if piece and self.get_piece_owner(piece) == self.current_player:
                    for dr in range(8):
                        for dc in range(8):
                            if self.valid_move(sr, sc, dr, dc):
                                return True
        return False


    # Resign from the game
    def resign(self):
        if not self.running:
            return
        loser = self.current_player
        winner = self.get_opponent()
        self.running = False
        messagebox.showinfo("Resignation", f"{loser} resigned. {winner} wins!")
        add_to_history({
                "name": self.game_name,
                "type": "chess",
                "result": f"{winner} wins by resignation",
                "moves": self.move_counter[self.player1] + self.move_counter[self.player2]
            })

        update_stats("chess", f"{winner} wins by resignation")
        if self.on_exit:
            self.on_exit()

    # Switch player turn after a move
    def switch_turn(self):
        self.current_player = self.get_opponent()
        self.update_info()
        if self.is_ai_turn():
            self.root.after(1000, self.make_ai_move)

    # Checks if a piece is owned by current player
    def is_own_piece(self, r, c):
        piece = self.board_state[r][c]
        if not piece:
            return False
        if self.current_player == self.player1:
            return (self.player1_color == "white" and piece in "♙♖♘♗♕♔") or (self.player1_color == "black" and piece in "♟♜♞♝♛♚")
        else:
            return (self.player1_color == "black" and piece in "♙♖♘♗♕♔") or (self.player1_color == "white" and piece in "♟♜♞♝♛♚")

    # Prevents moving into check
    def would_cause_check(self, sr, sc, dr, dc):
        temp_board = [row[:] for row in self.board_state]
        moving_piece = temp_board[sr][sc]
        temp_board[dr][dc] = moving_piece
        temp_board[sr][sc] = ""
    
        # Simulate en passant target cleanup
        if moving_piece in ["♙", "♟"] and abs(sc - dc) == 1 and self.board_state[dr][dc] == "":
            direction = -1 if moving_piece == "♙" else 1
            temp_board[dr + direction][dc] = ""
    
        return self.king_in_check(self.current_player, temp_board)


    # Format seconds to MM:SS
    def format_time(self, s):
        return f"{s//60:02}:{s%60:02}"

    # Speak message aloud
    def speak(self, text):
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except:
            pass

    # Exit the game properly
    def exit_game(self):
        if self.running:
            messagebox.showwarning("Cannot Exit", "Please finish or resign the game first.")
            return
        if self.on_exit:
            self.on_exit()

    # Get opponent of current player
    def get_opponent(self):
        return self.player2 if self.current_player == self.player1 else self.player1

    # Clear all widgets in the window
    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # Starts countdown timer thread
    def start_timer(self):
        def tick():
            while self.running:
                time.sleep(1)
                self.time_left[self.current_player] -= 1
    
                if self.time_left[self.current_player] <= 0:
                    self.running = False
                    winner = self.get_opponent()
                    messagebox.showinfo("Timeout", f"{winner} wins by timeout.")
    
                    # ✅ Corrected: Pass dictionary to add_to_history
                    add_to_history({
                        "name": self.game_name,
                        "type": "chess",
                        "result": f"{winner} wins by timeout",
                        "moves": self.move_counter[self.player1] + self.move_counter[self.player2]
                    })
    
                    # ✅ Corrected: Pass both game type and message
                    update_stats("chess", f"{winner} wins by timeout")
    
                    if self.on_exit:
                        self.on_exit()
                    break
    
                try:
                    self.update_info()
                except:
                    break  # widget might be destroyed
    
        threading.Thread(target=tick, daemon=True).start()

    def valid_move(self, sr, sc, dr, dc):
        piece = self.board_state[sr][sc]
        target = self.board_state[dr][dc]
    
        if sr == dr and sc == dc or (target and self.is_own_piece(dr, dc)):
            return False
    
        delta_r, delta_c = dr - sr, dc - sc
        abs_r, abs_c = abs(delta_r), abs(delta_c)
    
        def clear_path():
            step_r = (delta_r > 0) - (delta_r < 0)
            step_c = (delta_c > 0) - (delta_c < 0)
            r, c = sr + step_r, sc + step_c
            while (r, c) != (dr, dc):
                if self.board_state[r][c] != "":
                    return False
                r += step_r
                c += step_c
            return True
    
        # ♙♟ Pawn logic (with en passant)
        if piece in ["♙", "♟"]:
            direction = -1 if piece == "♙" else 1
            start_row = 6 if piece == "♙" else 1
            if sc == dc:
                if dr == sr + direction and not target:
                    return True
                if sr == start_row and dr == sr + 2 * direction and not target and not self.board_state[sr + direction][sc]:
                    return True
            if abs_c == 1 and dr == sr + direction:
                if target:
                    return True
                # En passant
                if self.last_move:
                    last_sr, last_sc, last_dr, last_dc, last_piece = self.last_move
                    if last_piece in ["♙", "♟"] and abs(last_dr - last_sr) == 2:
                        if last_dr == sr and last_dc == dc and self.board_state[last_dr][last_dc] == last_piece:
                            return True
    
        # ♖♜ Rook
        elif piece in ["♖", "♜"] and (sr == dr or sc == dc):
            return clear_path()
    
        # ♗♝ Bishop
        elif piece in ["♗", "♝"] and abs_r == abs_c:
            return clear_path()
    
        # ♕♛ Queen
        elif piece in ["♕", "♛"] and (sr == dr or sc == dc or abs_r == abs_c):
            return clear_path()
    
        # ♘♞ Knight
        elif piece in ["♘", "♞"]:
            return (abs_r, abs_c) in [(2, 1), (1, 2)]
    
        # ♔♚ King + Castling
        elif piece in ["♔", "♚"]:
            if max(abs_r, abs_c) == 1:
                if self.would_cause_check(sr, sc, dr, dc):
                    return False
                return True
    
            # White castling
            if piece == "♔" and sr == 7 and sc == 4:
                if dr == 7 and dc == 6 and self.castling_rights["white_kingside"]:
                    if self.board_state[7][5] == "" and self.board_state[7][6] == "":
                        if not self.would_cause_check(7, 4, 7, 5) and not self.would_cause_check(7, 4, 7, 6):
                            return True
                if dr == 7 and dc == 2 and self.castling_rights["white_queenside"]:
                    if self.board_state[7][1] == "" and self.board_state[7][2] == "" and self.board_state[7][3] == "":
                        if not self.would_cause_check(7, 4, 7, 3) and not self.would_cause_check(7, 4, 7, 2):
                            return True
    
            # Black castling
            if piece == "♚" and sr == 0 and sc == 4:
                if dr == 0 and dc == 6 and self.castling_rights["black_kingside"]:
                    if self.board_state[0][5] == "" and self.board_state[0][6] == "":
                        if not self.would_cause_check(0, 4, 0, 5) and not self.would_cause_check(0, 4, 0, 6):
                            return True
                if dr == 0 and dc == 2 and self.castling_rights["black_queenside"]:
                    if self.board_state[0][1] == "" and self.board_state[0][2] == "" and self.board_state[0][3] == "":
                        if not self.would_cause_check(0, 4, 0, 3) and not self.would_cause_check(0, 4, 0, 2):
                            return True
    
        return False

    def square_under_attack(self, row, col):
        opponent = self.get_opponent()
        saved = self.current_player
        self.current_player = opponent
        for r in range(8):
            for c in range(8):
                if self.is_own_piece(r, c):
                    if self.valid_move(r, c, row, col):
                        self.current_player = saved
                        return True
        self.current_player = saved
        return False

    def adjacent_to_enemy_king(self, row, col):
        enemy_king = "♚" if self.current_player == self.player1 else "♔"
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = row + dr, col + dc
                if 0 <= nr < 8 and 0 <= nc < 8:
                    if self.board_state[nr][nc] == enemy_king:
                        return True
        return False
