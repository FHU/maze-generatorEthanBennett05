"""
maze_generator.py — Generate maze images of any size.

Usage:
    python maze_generator.py                          # 20×20, default output
    python maze_generator.py -cols 40 -rows 30       # 40 columns × 30 rows
    python maze_generator.py -cols 15 -rows 15 -cell 40 -wall 3 -out my_maze.png
    python maze_generator.py --help
"""

import argparse
import random
from PIL import Image, ImageDraw


# ---------------------------------------------------------------------------
# Maze generation — recursive back-tracker (depth-first search)
# ---------------------------------------------------------------------------

def generate_maze(cols: int, rows: int, seed: int | None = None) -> set[tuple]:
    """
    Return the set of walls to REMOVE (i.e. open passages).
    Each wall is represented as a frozenset of two adjacent (col, row) cells.
    """
    rng = random.Random(seed)

    visited = set()
    passages = set()

    def neighbors(c, r):
        for dc, dr in ((0, -1), (1, 0), (0, 1), (-1, 0)):
            nc, nr = c + dc, r + dr
            if 0 <= nc < cols and 0 <= nr < rows:
                yield nc, nr

    def dfs(c, r):
        visited.add((c, r))
        dirs = list(neighbors(c, r))
        rng.shuffle(dirs)
        for nc, nr in dirs:
            if (nc, nr) not in visited:
                passages.add(frozenset(((c, r), (nc, nr))))
                dfs(nc, nr)

    dfs(0, 0)
    return passages


# ---------------------------------------------------------------------------
# Image rendering
# ---------------------------------------------------------------------------

def draw_maze(
    cols: int,
    rows: int,
    passages: set,
    cell_size: int = 20,
    wall_width: int = 2,
    bg_color: str = "#ffffff",
    wall_color: str = "#1a1a2e",
    entry_color: str = "#4caf50",
    exit_color: str = "#f44336",
) -> Image.Image:
    """Render the maze to a PIL Image."""

    W = cols * cell_size + wall_width
    H = rows * cell_size + wall_width

    img = Image.new("RGB", (W, H), bg_color)
    draw = ImageDraw.Draw(img)

    def cell_rect(c, r):
        x0 = c * cell_size + wall_width
        y0 = r * cell_size + wall_width
        x1 = x0 + cell_size - wall_width
        y1 = y0 + cell_size - wall_width
        return x0, y0, x1, y1

    # Fill background cells
    for r in range(rows):
        for c in range(cols):
            x0, y0, x1, y1 = cell_rect(c, r)
            draw.rectangle([x0, y0, x1, y1], fill=bg_color)

    # Draw walls — for each cell check the right and bottom neighbour;
    # if no passage exists between them, draw the dividing wall.
    w = wall_width

    # Top border
    draw.rectangle([0, 0, W - 1, w - 1], fill=wall_color)
    # Left border
    draw.rectangle([0, 0, w - 1, H - 1], fill=wall_color)
    # Bottom border
    draw.rectangle([0, H - w, W - 1, H - 1], fill=wall_color)
    # Right border
    draw.rectangle([W - w, 0, W - 1, H - 1], fill=wall_color)

    for r in range(rows):
        for c in range(cols):
            x0, y0, x1, y1 = cell_rect(c, r)

            # Right wall
            if c + 1 < cols:
                if frozenset(((c, r), (c + 1, r))) not in passages:
                    draw.rectangle([x1, y0, x1 + w - 1, y1], fill=wall_color)
                else:
                    draw.rectangle([x1, y0, x1 + w - 1, y1], fill=bg_color)
            # Bottom wall
            if r + 1 < rows:
                if frozenset(((c, r), (c, r + 1))) not in passages:
                    draw.rectangle([x0, y1, x1, y1 + w - 1], fill=wall_color)
                else:
                    draw.rectangle([x0, y1, x1, y1 + w - 1], fill=bg_color)

    # Entry opening (top of top-left cell)
    ex0, ey0, ex1, ey1 = cell_rect(0, 0)
    draw.rectangle([ex0, 0, ex1, w - 1], fill=entry_color)

    # Exit opening (bottom of bottom-right cell)
    xx0, xy0, xx1, xy1 = cell_rect(cols - 1, rows - 1)
    draw.rectangle([xx0, H - w, xx1, H - 1], fill=exit_color)

    # Small entry/exit indicator squares inside the cells
    indicator = max(4, cell_size // 4)
    draw.rectangle(
        [ex0, ey0, ex0 + indicator, ey0 + indicator], fill=entry_color
    )
    draw.rectangle(
        [xx1 - indicator, xy1 - indicator, xx1, xy1], fill=exit_color
    )

    return img


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate a maze image.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-cols",  type=int, default=20,          help="Number of columns (width in cells)")
    parser.add_argument("-rows",  type=int, default=20,          help="Number of rows (height in cells)")
    parser.add_argument("-cell",  type=int, default=20,          help="Pixel size of each cell")
    parser.add_argument("-wall",  type=int, default=2,           help="Pixel thickness of walls")
    parser.add_argument("-seed",  type=int, default=None,        help="Random seed for reproducibility")
    parser.add_argument("-out",   type=str, default="maze.png",  help="Output filename")
    parser.add_argument("-bg",    type=str, default="#ffffff",   help="Background / path colour")
    parser.add_argument("-fg",    type=str, default="#1a1a2e",   help="Wall colour")
    args = parser.parse_args()

    if args.cols < 2 or args.rows < 2:
        parser.error("cols and rows must each be at least 2.")

    print(f"Generating {args.cols}×{args.rows} maze …")
    passages = generate_maze(args.cols, args.rows, seed=args.seed)

    img = draw_maze(
        cols=args.cols,
        rows=args.rows,
        passages=passages,
        cell_size=args.cell,
        wall_width=args.wall,
        bg_color=args.bg,
        wall_color=args.fg,
    )

    img.save(args.out)
    print(f"Saved → {args.out}  ({img.width}×{img.height} px)")


if __name__ == "__main__":
    main()
