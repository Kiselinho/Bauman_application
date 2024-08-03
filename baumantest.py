import pygame
import sqlite3
import sys
import random

# Инициализация PyGame
pygame.init()

# Размеры окна
WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PyGame Game")

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Шрифт
font = pygame.font.Font(None, 36)

# Класс для главного персонажа
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 30
        self.vel = 5

    def draw(self, win):
        pygame.draw.polygon(win, BLUE, [
            (self.x, self.y - self.radius),
            (self.x - self.radius, self.y + self.radius),
            (self.x + self.radius, self.y + self.radius)
        ])

# Класс для монеты
class Coin:
    def __init__(self):
        self.x = random.randint(50, WIDTH - 50)
        self.y = random.randint(50, HEIGHT - 50)
        self.radius = 20
        self.color = (255, 215, 0)  # Цвет монеты

    def draw(self, win):
        pygame.draw.circle(win, self.color, (self.x, self.y), self.radius)

# Класс для препятствий
class Obstacle:
    def __init__(self):
        self.x = random.randint(50, WIDTH - 50)
        self.y = random.randint(50, HEIGHT - 50)
        self.radius = 20
        self.color = RED  # Цвет препятствия

    def draw(self, win):
        pygame.draw.circle(win, self.color, (self.x, self.y), self.radius)

# Класс для взаимодействия с базой данных
class Database:
    def __init__(self):
        self.conn = sqlite3.connect('scores2.db')
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS scores
                               (name TEXT, score INTEGER)''')
        self.conn.commit()

    def add_score(self, name, score):
        self.cursor.execute("SELECT score FROM scores WHERE name = ?", (name,))
        result = self.cursor.fetchone()
        if result:
            if score > result[0]:
                self.cursor.execute("UPDATE scores SET score = ? WHERE name = ?", (score, name))
        else:
            self.cursor.execute("INSERT INTO scores (name, score) VALUES (?, ?)", (name, score))
        self.conn.commit()

    def get_top_scores(self):
        self.cursor.execute("SELECT name, score FROM scores ORDER BY score DESC LIMIT 5")
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()

# Функция для запроса имени пользователя
def get_user_name():
    input_box = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 25, 200, 50)
    user_text = ''
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return user_text
                elif event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]
                else:
                    user_text += event.unicode

        win.fill(WHITE)
        prompt_text = font.render("Введите имя:", True, BLACK)
        win.blit(prompt_text, (input_box.x, input_box.y - 40))
        txt_surface = font.render(user_text, True, BLACK)
        win.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(win, BLACK, input_box, 2)
        pygame.display.flip()

# Основной игровой цикл
def game_loop(player_name):
    player = Player(WIDTH // 2, HEIGHT // 2)
    clock = pygame.time.Clock()
    score = 0
    coins = []  # Список для хранения монет
    obstacles = []  # Список для хранения препятствий

    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - player.radius > 0:
            player.x -= player.vel
        if keys[pygame.K_RIGHT] and player.x + player.radius < WIDTH:
            player.x += player.vel
        if keys[pygame.K_UP] and player.y - player.radius > 0:
            player.y -= player.vel
        if keys[pygame.K_DOWN] and player.y + player.radius < HEIGHT:
            player.y += player.vel

        # Создание новой монеты случайным образом
        if random.randint(0, 100) < 2:  # Вероятность создания монеты
            coins.append(Coin())

        # Создание нового препятствия случайным образом
        if random.randint(0, 100) < 1:  # Вероятность создания препятствия
            obstacles.append(Obstacle())

        # Рисуем персонажа, монеты и препятствия
        win.fill(WHITE)
        player.draw(win)
        
        for coin in coins:
            coin.draw(win)

            # Проверка столкновения персонажа с монетой
            if (coin.x - coin.radius < player.x + player.radius and
                coin.x + coin.radius > player.x - player.radius and
                coin.y - coin.radius < player.y + player.radius and
                coin.y + coin.radius > player.y - player.radius):
                coins.remove(coin)
                score += 10  # Например, за каждую монету начисляем 10 очков

        for obstacle in obstacles:
            obstacle.draw(win)

            # Проверка столкновения персонажа с препятствием
            if (obstacle.x - obstacle.radius < player.x + player.radius and
                obstacle.x + obstacle.radius > player.x - player.radius and
                obstacle.y - obstacle.radius < player.y + player.radius and
                obstacle.y + obstacle.radius > player.y - player.radius):
                obstacles.remove(obstacle)
                score -= 10  # За каждое препятствие вычитаем 10 очков

        score_text = font.render(f"Score: {score}", True, BLACK)
        instructions_text = font.render("Собирайте монеты, избегайте красных объектов", True, BLACK)
        win.blit(score_text, (10, 10))
        win.blit(instructions_text, (10, 50))
        pygame.display.flip()

        # Условие проигрыша
        if score < -100:  # Проигрыш при -100 очков
            run = False
            win.fill(WHITE)
            lose_text = font.render("You Lose!", True, BLACK)
            win.blit(lose_text, (WIDTH // 2 - lose_text.get_width() // 2, HEIGHT // 2 - lose_text.get_height() // 2))
            pygame.display.flip()
            pygame.time.delay(2000)

    return score

def main():
    db = Database()
    name = get_user_name()
    score = game_loop(name)
    db.add_score(name, score)
    top_scores = db.get_top_scores()

    # Отображение топ-5 игроков
    win.fill(WHITE)
    y_offset = 100
    for i, (name, score) in enumerate(top_scores):
        score_text = font.render(f"{i+1}. {name} - {score}", True, BLACK)
        win.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, y_offset))
        y_offset += 40

    pygame.display.flip()
    pygame.time.delay(5000)
    db.close()
    pygame.quit()

if __name__ == "__main__":
    main()



