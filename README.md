# ASCII Eye → Space

A real-time animation of a human eye drawn entirely with text characters. The eye blinks, looks around, and after a while the inside of the eye slowly turns into a twinkling night sky full of stars, then returns to normal. Built with Python, NumPy and Pygame.

![Screenshot](screenshot.png)

## Features

- Eye rendered as colored ASCII characters (120 × 54 character grid)
- Natural blinking and moving gaze, with a changing pupil size
- Eyebrow, eyelashes, iris fibers and highlights drawn procedurally
- Seamless transition from the eye into a star field (space) and back
- Characters are picked by brightness using a font atlas, with a small flicker effect
- Save screenshots with a single key

## Requirements

- Python 3.9 or newer
- [pygame-ce](https://pyga.me/)
- [NumPy](https://numpy.org/)

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/ascii-eye.git
cd ascii-eye
pip install -r requirements.txt
```

> **Note:** On very new Python versions (such as 3.14) the original `pygame` package may fail to install on Windows. This project uses `pygame-ce`, which works with the same `import pygame` and installs without problems.

## Usage

```bash
python EYES.py
```

### Controls

| Key     | Action                                      |
| ------- | ------------------------------------------- |
| `SPACE` | Turn space mode on or off permanently       |
| `S`     | Save a screenshot (`eye_000.png`, `eye_001.png`, ...) |
| `ESC`   | Quit                                        |

## How it works

1. Every frame, a small color image (one pixel per character cell) is computed with NumPy: skin, eyelids, iris, pupil, lashes, and the star field.
2. The brightness of each cell decides which character is used, from light ones like `.` and `:` to dense ones like `@` and `$`.
3. The colors are applied as a tint to the characters, and the result is drawn to the Pygame window.
4. The animation runs on a 24 second loop. Space appears between roughly 13 s and 21 s, with smooth fades in and out.

## Customization

Settings are at the top of `EYES.py`:

| Variable      | Meaning                                         |
| ------------- | ----------------------------------------------- |
| `COLS, ROWS`  | Size of the character grid (lower = faster)     |
| `CW, CH`      | Size of one character cell in pixels            |
| `FPS`         | Frames per second                               |
| `LOOP`        | Length of the full loop in seconds              |
| `CHARS`       | Characters used for shading                     |
| `EYE_W`       | Width of the eye                                |

If the animation is slow on your computer, reduce `FPS` or `COLS, ROWS`.

## License

Created by Uzair Zafar
