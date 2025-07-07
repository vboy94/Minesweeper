import pygame
import sys
import random

# --- Налаштування гри ---
WIDTH, HEIGHT = 15, 15  # Розміри сітки
TILE_SIZE = 50
MINES_COUNT = 15
WINDOW_SIZE = WIDTH * TILE_SIZE, HEIGHT * TILE_SIZE

# --- Кольори ---
GRAY = (200, 200, 200)
DARK_GRAY = (150, 150, 150)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 150, 0)

# --- Ініціалізація Pygame ---
pygame.init()
# --- Завантаження звуків ---
pygame.mixer.init()
click_sound = pygame.mixer.Sound("sounds/click.wav")
flag_sound = pygame.mixer.Sound("sounds/flag.wav")
boom_sound = pygame.mixer.Sound("sounds/boom.wav")
icon = pygame.image.load("icon.png")
pygame.display.set_icon(icon)
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Сапер")
font = pygame.font.SysFont(None, 28)
clock = pygame.time.Clock()

# --- Клас клітинки ---
class Cell:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.is_mine = False
        self.is_revealed = False
        self.is_flagged = False
        self.adjacent_mines = 0

    def draw(self):
        rect = pygame.Rect(self.x * TILE_SIZE, self.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        if self.is_revealed:
            pygame.draw.rect(screen, GRAY, rect)
            pygame.draw.rect(screen, DARK_GRAY, rect, 1)
            if self.is_mine:
                pygame.draw.circle(screen, RED, rect.center, TILE_SIZE // 4)
            elif self.adjacent_mines > 0:
                text = font.render(str(self.adjacent_mines), True, BLACK)
                screen.blit(text, text.get_rect(center=rect.center))
        else:
            pygame.draw.rect(screen, DARK_GRAY, rect)
            pygame.draw.rect(screen, BLACK, rect, 2)
            if self.is_flagged:
                text = font.render("🚩", True, RED)
                screen.blit(text, text.get_rect(center=rect.center))

# --- Створення поля ---
def create_grid():
    grid = [[Cell(x, y) for x in range(WIDTH)] for y in range(HEIGHT)]
    # Розставити міни
    mines = random.sample([(x, y) for x in range(WIDTH) for y in range(HEIGHT)], MINES_COUNT)
    for (x, y) in mines:
        grid[y][x].is_mine = True

    # Обчислити кількість мін навколо
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if not grid[y][x].is_mine:
                count = 0
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < WIDTH and 0 <= ny < HEIGHT:
                            if grid[ny][nx].is_mine:
                                count += 1
                grid[y][x].adjacent_mines = count
    return grid

# --- Рекурсивне відкриття ---
def reveal(grid, x, y):
    cell = grid[y][x]
    if cell.is_revealed or cell.is_flagged:
        return
    cell.is_revealed = True
    if cell.adjacent_mines == 0 and not cell.is_mine:
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < WIDTH and 0 <= ny < HEIGHT:
                    reveal(grid, nx, ny)

# --- Головна гра ---
def main():
    grid = create_grid()
    game_over = False
    win = False

    while True:
        screen.fill(WHITE)
        for row in grid:
            for cell in row:
                cell.draw()

        # Перевірка на перемогу
        if not game_over:
            unrevealed = [cell for row in grid for cell in row if not cell.is_revealed]
            if len(unrevealed) == MINES_COUNT:
                win = True
                game_over = True

        if game_over:
            msg = "🎉 Перемога!" if win else "💥 Ви програли!"
            text = font.render(msg, True, GREEN if win else RED)
            screen.blit(text, text.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2)))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if not game_over and event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                x, y = mx // TILE_SIZE, my // TILE_SIZE
                cell = grid[y][x]

                if event.button == 1:  # ЛКМ — відкрити
                    if cell.is_mine:
                        cell.is_revealed = True
                        boom_sound.play()
                        game_over = True
                    else:
                        click_sound.play()
                        reveal(grid, x, y)

                elif event.button == 3:  # ПКМ — прапорець
                    if not cell.is_revealed:
                        cell.is_flagged = not cell.is_flagged
                        flag_sound.play()

        clock.tick(30)

if __name__ == "__main__":
    main()
