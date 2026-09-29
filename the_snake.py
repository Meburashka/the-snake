from random import randint

from typing import Optional

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 5

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс всех игровых объектов."""

    def __init__(self, position: Optional[tuple[int, int]] = None, body_color: Optional[tuple[int, int, int]] = None):
        """Инициализирует объект: задаёт позицию и цвет."""
        self.position = position
        self.body_color = body_color

    def draw(self) -> None:
        """Абстрактный метод отрисовки. Переопределяется в дочерних классах."""
        raise NotImplementedError


class Apple(GameObject):
    """Класс яблока — цели для змейки."""

    def __init__(self, position: tuple[int, int] | None = None):
        """Инициализирует яблоко с фиксированным цветом APPLE_COLOR."""
        if position is None:
            position = self.randomize_position()
        super().__init__(position, APPLE_COLOR)

    def randomize_position(self) -> tuple[int, int]:
        """Задаёт яблоку случайную позицию на сетке и возвращает её."""
        x = randint(0, GRID_WIDTH - 1)
        y = randint(0, GRID_HEIGHT - 1)
        self.position = (x, y)
        return self.position

    def draw(self) -> None:
        """Отрисовывает яблоко на игровом поле.
        Преобразует координаты сетки в пиксельные и рисует ячейку
        цветом APPLE_COLOR с рамкой BORDER_COLOR.
        """
        
        assert self.body_color is not None, "У яблока должен быть цвет!"
        if self.position is None:
            return 
        
        x, y = self.position
        pixel_x = x * GRID_SIZE
        pixel_y = y * GRID_SIZE
        topleft = (pixel_x, pixel_y)
        rect = pygame.Rect(topleft, (GRID_SIZE, GRID_SIZE))

        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Класс змейки — управляемого игроком объекта."""
    
    positions: list[tuple[int, int]]
    last: tuple[int, int] | None
    next_direction: tuple[int, int] | None
    def __init__(self, position: tuple[int, int] | None = None):
        """Инициализирует змейку.

        Атрибуты:
            positions — список, содержащий позиции всех сегментов тела змейки.
            length — длина змейки, изначально 1.
            direction — текущее направление, по умолчанию RIGHT.
            next_direction — следующее направление движения,
            которое будет применено после обработки нажатия клавиши.
            По умолчанию — None.
            body_color — цвет змейки, по умолчанию SNAKE_COLOR.
            last — координаты последнего сегмента перед его удалением;
            изначально None.
        """
        if position is None:
            position = (GRID_WIDTH // 2, GRID_HEIGHT // 2)
        final_position: tuple[int, int] = position
        
        super().__init__(final_position, SNAKE_COLOR)
        self.positions = [final_position]
        self.length = 1
        self.direction = RIGHT
        self.next_direction = None
        self.last = None 

    def get_head_position(self) -> tuple[int, int]:
        """Возвращает позицию головы змейки."""
        if not self.positions:
            return (0, 0)
        assert self.positions[0] is not None, "Голова змейки не может быть None!"

        return self.positions[0]

    def move(self) -> None:
        """Обновляет положение змейки на игровом поле.

        Рассчитывает новую позицию головы с учётом направления и
        зацикливания границ поля. Добавляет голову в начало списка
        positions и удаляет последний сегмент, если длина змейки
        не увеличилась (сохраняя удалённый сегмент в self.last).
        """
        
        assert self.body_color is not None, "У змейки должен быть цвет!"
        if not self.positions:
            return
        assert self.positions[0] is not None, "Голова змейки не может быть None!"

        head_x, head_y = self.positions[0]
        dx, dy = self.direction
        new_head = ((head_x + dx) % GRID_WIDTH, (head_y + dy) % GRID_HEIGHT)

        self.positions.insert(0, new_head)

        if len(self.positions) > self.length:
            assert self.positions[-1] is not None, "Последний сегмент не может быть None!"
            self.last = self.positions[-1]
            self.positions.pop()
        else:
            self.last = None

    def update_direction(self) -> None:
        """Метод обновления направления после нажатия на кнопку."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def draw(self) -> None:
        """
        Отрисовывает змейку на экране.
        Переводит координаты сетки в пиксельные.
        Если self.last не равен None, закрашивает эту ячейку цветом фона
        BOARD_BACKGROUND_COLOR и сбрасывает self.last в None.
        """
        
        assert self.body_color is not None, "У змейки должен быть цвет!"
        if self.position is None:
            return

        for pos in self.positions: 
            x, y = pos
            pixel_x = x * GRID_SIZE
            pixel_y = y * GRID_SIZE
            rect = pygame.Rect((pixel_x, pixel_y), (GRID_SIZE, GRID_SIZE))
            
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        if self.last is not None:
            x, y = self.last
            pixel_x = x * GRID_SIZE
            pixel_y = y * GRID_SIZE
            last_rect = pygame.Rect((pixel_x, pixel_y), (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)
            self.last = None

    def reset(self) -> None:
        """Сбрасывает змейку в начальное состояние."""
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = (0, -1)
        self.length = 1


def handle_keys(game_object: Snake) -> None:
    """
    Функция обработки действий пользователя.
    Обрабатывает события клавиатуры: меняет направление змейки.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main() -> None:
    """Главный игровой цикл.

    Создаёт змейку в центре поля и яблоко со случайной позицией.
    В каждом кадре:
        - обрабатывает нажатия клавиш;
        - обновляет направление и сдвигает змейку;
        - проверяет столкновение головы с телом — если да, игра
          заканчивается;
        - проверяет совпадение головы с яблоком — если да, увеличивает
          длину и перемещает яблоко;
        - отрисовывает змейку и яблоко, обновляет экран.

    Цикл повторяется с частотой SPEED кадров в секунду.
    """
    pygame.init()
    snake = Snake((GRID_WIDTH // 2, GRID_HEIGHT // 2))
    apple = Apple((0, 0))
    apple.randomize_position()

    while True:
        clock.tick(SPEED)
        screen.fill(BOARD_BACKGROUND_COLOR)
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        head_position = snake.get_head_position()

        if head_position in snake.positions[1:]:
            snake.reset()

        if head_position == apple.position:
            snake.length += 1
            apple.randomize_position()

        snake.draw()
        apple.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
