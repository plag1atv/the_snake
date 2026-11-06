"""Игра «Изгиб Питона»: змейка, собирающая яблоки."""

from random import choice

import pygame

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
DIRECTIONS = (UP, DOWN, LEFT, RIGHT)

BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)
SPEED = 20
CENTER_POSITION = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
ALL_CELLS = {
    (x * GRID_SIZE, y * GRID_SIZE)
    for x in range(GRID_WIDTH)
    for y in range(GRID_HEIGHT)
}

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption('Изгиб Питона')
clock = pygame.time.Clock()


class GameObject:
    """Базовый объект игрового поля."""

    def __init__(self):
        """Задать стандартную позицию и цвет объекта."""
        self.position = CENTER_POSITION
        self.body_color = None

    def draw(self):
        """Определить интерфейс отрисовки для подклассов."""
        pass


class Apple(GameObject):
    """Яблоко, появляющееся в свободной клетке поля."""

    def __init__(self):
        """Задать цвет яблока и его начальную позицию."""
        super().__init__()
        self.body_color = APPLE_COLOR
        self.randomize_position()

    def randomize_position(self, occupied=()):
        """Переместить яблоко в случайную незанятую клетку."""
        free_cells = ALL_CELLS - set(occupied)
        if not free_cells:
            return False
        self.position = choice(tuple(free_cells))
        return True

    def draw(self):
        """Нарисовать яблоко и рамку вокруг него."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Змейка, которая движется, растёт и может кусать себя."""

    def __init__(self):
        """Подготовить змейку к новой игре."""
        super().__init__()
        self.body_color = SNAKE_COLOR
        self.length = 1
        self.positions = [CENTER_POSITION]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def update_direction(self):
        """Применить направление, выбранное игроком."""
        if self.next_direction is not None:
            self.direction = self.next_direction
            self.next_direction = None

    def get_head_position(self):
        """Вернуть координаты головы."""
        return self.positions[0]

    def move(self):
        """Передвинуть голову на клетку и при необходимости убрать хвост."""
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction
        new_head = (
            (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT,
        )
        self.positions.insert(0, new_head)
        self.last = None
        if len(self.positions) > self.length:
            self.last = self.positions.pop()

    def draw(self):
        """Нарисовать тело змейки и стереть предыдущую клетку хвоста."""
        if self.last is not None:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)
        for position in self.positions:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    def reset(self):
        """Вернуть змейку в центр с длиной один сегмент."""
        self.length = 1
        self.position = CENTER_POSITION
        self.positions = [CENTER_POSITION]
        self.direction = choice(DIRECTIONS)
        self.next_direction = None
        self.last = None


def handle_keys(game_object):
    """Обработать выход из игры и изменение направления стрелками."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                raise SystemExit
            key_directions = {
                pygame.K_UP: UP,
                pygame.K_DOWN: DOWN,
                pygame.K_LEFT: LEFT,
                pygame.K_RIGHT: RIGHT,
            }
            new_direction = key_directions.get(event.key)
            if new_direction is None:
                continue
            old_x, old_y = game_object.direction
            if new_direction != (-old_x, -old_y):
                game_object.next_direction = new_direction


def main():
    """Запустить игровой цикл и обработку столкновений."""
    pygame.init()
    snake = Snake()
    apple = Apple()
    apple.randomize_position(snake.positions)

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            apple.randomize_position(snake.positions)

        if snake.get_head_position() == apple.position:
            snake.length += 1
            if snake.last is not None:
                snake.positions.append(snake.last)
                snake.last = None
            if not apple.randomize_position(snake.positions):
                snake.reset()
                apple.randomize_position(snake.positions)

        screen.fill(BOARD_BACKGROUND_COLOR)
        snake.draw()
        apple.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
