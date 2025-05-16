# My-chess-game-project

A classic 2D chess game built using Python and Pygame. This project provides a playable chess board with basic rules.

## Features
- 8x8 interactive chess board
- Full set of chess pieces with images
- Turn-based play for white and black
- Move highlighting and capture detection
- Sound effects for move, capture, and promotion
- Check and checkmate detection
- King highlighting when in check
- Promotion system (choose from queen, rook, bishop, knight)
- Title screen before game start

## Requirements

- Python 3.x
- Pygame (`pip install pygame`)

## How to Run

1. Clone or download this repository.
2. Ensure you have the following directory structure:

```
chess_game/
├── images/
│   ├── bp.png
│   ├── br.png
│   └── ... (all 12 piece images)
├── sounds/
│   ├── move-sound.mp3
│   ├── sounds_capture.mp3
│   └── sounds_promote.mp3
├── main.py
└── README.md
```

3. Run the game:

```bash
python main.py
```

## File Structure

- `MyChess.py`: The main game logic (board, pieces, UI, rules).
- `images/`: Folder containing piece images.
- `sounds/`: Folder containing MP3 sound files for moves and events.
- `README.md`: Project documentation.

## License
This project is open-source and free to use.

---

## Credits

- Piece images inspired by classic chess sets.
- Sounds from free game sound libraries.

Enjoy playing chess!