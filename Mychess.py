import pygame
import sys

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
WIDTH, HEIGHT = 800, 800
SQUARE_SIZE = WIDTH // 8
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_BROWN = (240, 217, 181)
DARK_BROWN = (181, 136, 99)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
OVERLAY_COLOR = (50, 50, 50, 220)

# Setup display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess Game")
clock = pygame.time.Clock()

# Load sounds with error handling
def load_sound(path):
    try:
        return pygame.mixer.Sound(path)
    except pygame.error:
        print(f"Warning: Could not load sound {path}")
        return None

move_sound = load_sound("sounds/move-sound.mp3")
capture_sound = load_sound("sounds/sounds_capture.mp3")
promote_sound = load_sound("sounds/sounds_promote.mp3")

# Load images
def load_pieces():
    pieces = {}
    piece_names = ['bp', 'br', 'bn', 'bb', 'bq', 'bk', 'wp', 'wr', 'wn', 'wb', 'wq', 'wk']
    for name in piece_names:
        try:
            img = pygame.image.load(f"images/{name}.png")
            pieces[name] = pygame.transform.scale(img, (SQUARE_SIZE, SQUARE_SIZE))
        except pygame.error:
            print(f"Warning: Could not load image images/{name}.png")
            pieces[name] = None
    return pieces

pieces = load_pieces()

# Initial board setup
initial_board = [
    ["br", "bn", "bb", "bk", "bq", "bb", "bn", "br"],
    ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
    ["", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", ""],
    ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
    ["wr", "wn", "wb", "wk", "wq", "wb", "wn", "wr"]
]

white_king_position = (7, 3)
black_king_position = (0, 3)

# Draw chessboard squares
def draw_board():
    for row in range(8):
        for col in range(8):
            color = LIGHT_BROWN if (row + col) % 2 == 0 else DARK_BROWN
            pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    # Highlight kings in check
    if is_in_check(initial_board, white_king_position, "white"):
        pygame.draw.rect(screen, RED, (white_king_position[1] * SQUARE_SIZE, white_king_position[0] * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    if is_in_check(initial_board, black_king_position, "black"):
        pygame.draw.rect(screen, RED, (black_king_position[1] * SQUARE_SIZE, black_king_position[0] * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

# Draw all pieces on board
def draw_pieces(board):
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece and pieces.get(piece):
                screen.blit(pieces[piece], (col * SQUARE_SIZE, row * SQUARE_SIZE))

# Highlight valid moves on the board
def highlight_squares(squares, color):
    for (row, col) in squares:
        surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        surface.fill((*color, 100))  # Transparent fill
        screen.blit(surface, (col * SQUARE_SIZE, row * SQUARE_SIZE))

# Convert mouse position to board coordinates
def get_square_from_mouse(pos):
    x, y = pos
    return y // SQUARE_SIZE, x // SQUARE_SIZE

# Get valid moves for pieces (simplified for clarity, original logic preserved)
def get_valid_moves(row, col, piece, board):
    moves = []
    if not piece:
        return moves
    # Pawn moves
    if piece == "bp":
        if row < 7 and board[row + 1][col] == "":
            moves.append((row + 1, col))
        if row == 1 and board[row + 2][col] == "":
            moves.append((row + 2, col))
        if row < 7 and col > 0 and board[row + 1][col - 1].startswith("w"):
            moves.append((row + 1, col - 1))
        if row < 7 and col < 7 and board[row + 1][col + 1].startswith("w"):
            moves.append((row + 1, col + 1))
    elif piece == "wp":
        if row > 0 and board[row - 1][col] == "":
            moves.append((row - 1, col))
        if row == 6 and board[row - 2][col] == "":
            moves.append((row - 2, col))
        if row > 0 and col > 0 and board[row - 1][col - 1].startswith("b"):
            moves.append((row - 1, col - 1))
        if row > 0 and col < 7 and board[row - 1][col + 1].startswith("b"):
            moves.append((row - 1, col + 1))
    # Knight moves
    elif piece[1] == "n":
        knight_moves = [(-2, -1), (-1, -2), (1, -2), (2, -1), (2, 1), (1, 2), (-1, 2), (-2, 1)]
        for dr, dc in knight_moves:
            nr, nc = row + dr, col + dc
            if 0 <= nr < 8 and 0 <= nc < 8:
                target = board[nr][nc]
                if target == "" or (target.startswith("b") and piece.startswith("w")) or (target.startswith("w") and piece.startswith("b")):
                    moves.append((nr, nc))
    # Bishop moves
    elif piece[1] == "b":
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in directions:
            nr, nc = row, col
            while True:
                nr += dr
                nc += dc
                if 0 <= nr < 8 and 0 <= nc < 8:
                    target = board[nr][nc]
                    if target == "":
                        moves.append((nr, nc))
                    elif (target.startswith("b") and piece.startswith("w")) or (target.startswith("w") and piece.startswith("b")):
                        moves.append((nr, nc))
                        break
                    else:
                        break
                else:
                    break
    # Rook moves
    elif piece[1] == "r":
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            nr, nc = row, col
            while True:
                nr += dr
                nc += dc
                if 0 <= nr < 8 and 0 <= nc < 8:
                    target = board[nr][nc]
                    if target == "":
                        moves.append((nr, nc))
                    elif (target.startswith("b") and piece.startswith("w")) or (target.startswith("w") and piece.startswith("b")):
                        moves.append((nr, nc))
                        break
                    else:
                        break
                else:
                    break
    # Queen moves
    elif piece[1] == "q":
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in directions:
            nr, nc = row, col
            while True:
                nr += dr
                nc += dc
                if 0 <= nr < 8 and 0 <= nc < 8:
                    target = board[nr][nc]
                    if target == "":
                        moves.append((nr, nc))
                    elif (target.startswith("b") and piece.startswith("w")) or (target.startswith("w") and piece.startswith("b")):
                        moves.append((nr, nc))
                        break
                    else:
                        break
                else:
                    break
    # King moves
    elif piece[1] == "k":
        king_moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in king_moves:
            nr, nc = row + dr, col + dc
            if 0 <= nr < 8 and 0 <= nc < 8:
                target = board[nr][nc]
                if target == "" or (target.startswith("b") and piece.startswith("w")) or (target.startswith("w") and piece.startswith("b")):
                    moves.append((nr, nc))
    return moves

# Check if king is in check
def is_in_check(board, king_pos, color):
    enemy_prefix = "b" if color == "white" else "w"
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece and piece.startswith(enemy_prefix):
                if king_pos in get_valid_moves(r, c, piece, board):
                    return True
    return False

# Get escape moves to get out of check
def get_escape_moves(board, king_pos, color):
    escape_moves = {}
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece and ((color == "white" and piece.startswith("w")) or (color == "black" and piece.startswith("b"))):
                moves = get_valid_moves(r, c, piece, board)
                legal_moves = []
                for move in moves:
                    temp_board = [row[:] for row in board]
                    temp_board[move[0]][move[1]] = temp_board[r][c]
                    temp_board[r][c] = ""
                    new_king_pos = move if piece[1] == "k" else king_pos
                    if not is_in_check(temp_board, new_king_pos, color):
                        legal_moves.append(move)
                if legal_moves:
                    escape_moves[(r, c)] = legal_moves
    return escape_moves

# Checkmate detection
def is_checkmate(board, king_pos, color):
    if not is_in_check(board, king_pos, color):
        return False
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece and ((color == "white" and piece.startswith("w")) or (color == "black" and piece.startswith("b"))):
                moves = get_valid_moves(r, c, piece, board)
                for move in moves:
                    temp_board = [row[:] for row in board]
                    temp_board[move[0]][move[1]] = temp_board[r][c]
                    temp_board[r][c] = ""
                    new_king_pos = move if piece[1] == "k" else king_pos
                    if not is_in_check(temp_board, new_king_pos, color):
                        return False
    return True

# Display on-screen message
def display_message(text, color=RED):
    font = pygame.font.SysFont(None, 72)
    msg = font.render(text, True, color)
    screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - msg.get_height() // 2))
    pygame.display.flip()
    pygame.time.wait(3000)

# Title screen function
def display_title_screen():
    font = pygame.font.SysFont(None, 72)
    title = font.render("Chess Game", True, BLACK)
    start_text = font.render("Press Enter to Start", True, BLACK)
    screen.fill(WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - title.get_height() // 2 - 50))
    screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT // 2 + 20))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    waiting = False

# Pawn promotion choice UI
def promotion_choice(color):
    choices = ['q', 'r', 'b', 'n']  # queen, rook, bishop, knight
    font = pygame.font.SysFont(None, 48)
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill(OVERLAY_COLOR)

    # Draw choice boxes centered horizontally
    box_size = 100
    start_x = (WIDTH - (box_size * len(choices))) // 2
    y = (HEIGHT - box_size) // 2
    rects = []

    # Draw background overlay and text
    screen.blit(overlay, (0,0))
    title_text = font.render("Choose promotion:", True, WHITE)
    screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, y - 60))

    # Draw piece choices
    for i, piece_code in enumerate(choices):
        rect = pygame.Rect(start_x + i*box_size, y, box_size, box_size)
        rects.append(rect)
        pygame.draw.rect(screen, BLUE, rect)
        piece_key = ('w' if color == "white" else 'b') + piece_code
        piece_img = pieces.get(piece_key)
        if piece_img:
            # center image in box
            img_rect = piece_img.get_rect(center=rect.center)
            screen.blit(piece_img, img_rect)

    pygame.display.flip()

    # Wait for user choice
    choosing = True
    while choosing:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                for i, rect in enumerate(rects):
                    if rect.collidepoint(pos):
                        choosing = False
                        return ('w' if color == "white" else 'b') + choices[i]
            elif event.type == pygame.KEYDOWN:
                # Optional: allow keyboard keys 1-4 to select
                if event.key in [pygame.K_1, pygame.K_KP1]:
                    choosing = False
                    return ('w' if color == "white" else 'b') + choices[0]
                elif event.key in [pygame.K_2, pygame.K_KP2]:
                    choosing = False
                    return ('w' if color == "white" else 'b') + choices[1]
                elif event.key in [pygame.K_3, pygame.K_KP3]:
                    choosing = False
                    return ('w' if color == "white" else 'b') + choices[2]
                elif event.key in [pygame.K_4, pygame.K_KP4]:
                    choosing = False
                    return ('w' if color == "white" else 'b') + choices[3]

# Main game loop variables
selected_piece = None
valid_moves = []
current_turn = "white"
white_king_position = (7, 3)
black_king_position = (0, 3)

# Handle user clicks for moves with promotion choice
def handle_click(pos):
    global selected_piece, valid_moves, current_turn, white_king_position, black_king_position
    row, col = get_square_from_mouse(pos)
    king_pos = white_king_position if current_turn == "white" else black_king_position

    if selected_piece:
        old_r, old_c = selected_piece
        if (row, col) in valid_moves:
            captured = initial_board[row][col] != ""
            piece_moved = initial_board[old_r][old_c]

            initial_board[row][col] = piece_moved
            initial_board[old_r][old_c] = ""

            # Check for pawn promotion condition
            if piece_moved == "wp" and row == 0:
                promoted_piece = promotion_choice("white")
                initial_board[row][col] = promoted_piece
                if promote_sound:
                    promote_sound.play()
            elif piece_moved == "bp" and row == 7:
                promoted_piece = promotion_choice("black")
                initial_board[row][col] = promoted_piece
                if promote_sound:
                    promote_sound.play()

            # Update king positions if changed
            final_piece = initial_board[row][col]
            if final_piece == "wk":
                white_king_position = (row, col)
            elif final_piece == "bk":
                black_king_position = (row, col)

            # Play sounds
            if captured and capture_sound:
                capture_sound.play()
            elif move_sound:
                move_sound.play()

            current_turn = "black" if current_turn == "white" else "white"

            king_pos = white_king_position if current_turn == "white" else black_king_position

            # Check for checkmate
            if is_checkmate(initial_board, king_pos, current_turn):
                winner = "White" if current_turn == "black" else "Black"
                display_message(f"Checkmate! {winner} wins", BLUE)
                pygame.quit()
                sys.exit()

        selected_piece = None
        valid_moves = []
    else:
        piece = initial_board[row][col]
        if piece and ((current_turn == "white" and piece.startswith("w")) or (current_turn == "black" and piece.startswith("b"))):
            selected_piece = (row, col)
            all_moves = get_valid_moves(row, col, piece, initial_board)
            if is_in_check(initial_board, king_pos, current_turn):
                escape_moves = get_escape_moves(initial_board, king_pos, current_turn)
                valid_moves = escape_moves.get((row, col), [])
            else:
                valid_moves = all_moves

# Display whose turn it is
def display_turn(turn):
    font = pygame.font.SysFont(None, 32)
    text = font.render(f"Turn: {turn.capitalize()}", True, BLACK)
    screen.blit(text, (10, 10))

# Main function
def main():
    display_title_screen()
    global selected_piece, valid_moves

    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                handle_click(event.pos)

        draw_board()
        draw_pieces(initial_board)

        if selected_piece:
            # Highlight selected piece square
            highlight_squares([selected_piece], GREEN)
            # Highlight valid moves
            highlight_squares(valid_moves, BLUE)

        display_turn(current_turn)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()