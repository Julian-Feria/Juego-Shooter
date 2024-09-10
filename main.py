import pygame, random, os

# Constantes de juego
WIDTH = 800
HEIGHT = 600
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
FPS = 60
HIGHSCORE_FILE = "highscore.txt"

# Inicialización de Pygame
pygame.init()
pygame.mixer.init()

class Game:
    def __init__(self):
        # Inicializar la pantalla, puntajes y estado del juego
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Shooter")
        self.clock = pygame.time.Clock()
        self.running = True
        self.highscore = self.get_highscore()
        self.difficulty = 10  # Controla la velocidad de los meteoros
        self.score = 0
        self.all_sprites = None
        self.meteor_list = None
        self.bullets = None
        self.player = None
        self.game_over = True

        # Cargar assets
        self.background = pygame.image.load("assets/background.png").convert()
        self.player_img = pygame.image.load("assets/Nave.png").convert()
        self.bullet_img = pygame.image.load("assets/B1.png").convert_alpha()
        self.meteor_images = [pygame.image.load(img).convert() for img in [
            "assets/meteorGrey_big1.png", "assets/meteorGrey_big2.png", "assets/meteorGrey_big3.png", "assets/meteorGrey_big4.png",
            "assets/meteorGrey_med1.png", "assets/meteorGrey_med2.png", "assets/meteorGrey_small1.png", "assets/meteorGrey_small2.png",
            "assets/meteorGrey_tiny1.png", "assets/meteorGrey_tiny2.png"
        ]]
        self.explosion_anim = [pygame.transform.scale(pygame.image.load(f"assets/regularExplosion0{i}.png").convert(), (70, 70)) for i in range(9)]
        self.laser_sound = pygame.mixer.Sound("assets/laser5.ogg")
        self.explosion_sound = pygame.mixer.Sound("assets/explosion.wav")
        pygame.mixer.music.load("assets/music.ogg")
        pygame.mixer.music.set_volume(0.2)
        pygame.mixer.music.play(loops=-1)

    def get_highscore(self):
        if os.path.exists(HIGHSCORE_FILE):
            with open(HIGHSCORE_FILE, "r") as file:
                try:
                    return int(file.read())
                except:
                    return 0
        return 0

    def save_highscore(self, score):
        with open(HIGHSCORE_FILE, "w") as file:
            file.write(str(score))

    def draw_text(self, surface, text, size, x, y, selected=False):
        font = pygame.font.SysFont("serif", size)
        color = GREEN if selected else WHITE
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        surface.blit(text_surface, text_rect)

    def draw_shield_bar(self, surface, x, y, percentage):
        BAR_LENGHT = 100
        BAR_HEIGHT = 10
        fill = (percentage / 100) * BAR_LENGHT
        border = pygame.Rect(x, y, BAR_LENGHT, BAR_HEIGHT)
        fill = pygame.Rect(x, y, fill, BAR_HEIGHT)
        pygame.draw.rect(surface, GREEN, fill)
        pygame.draw.rect(surface, WHITE, border, 2)

    def show_menu(self):
        """Mostrar el menú principal donde se seleccionan opciones como iniciar juego o cambiar la velocidad"""
        selected_index = 0  # Index de la opción seleccionada
        running = True
        while running:
            self.draw_menu(selected_index)
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        selected_index = (selected_index + 1) % 3  # Mover selección hacia abajo
                    elif event.key == pygame.K_UP:
                        selected_index = (selected_index - 1) % 3  # Mover selección hacia arriba
                    elif event.key == pygame.K_RETURN:  # Seleccionar con Enter
                        if selected_index == 0:  # Start Game
                            return 'start'
                        elif selected_index == 1:  # Change Difficulty
                            self.change_difficulty()  # Cambia la dificultad y vuelve al menú
                        elif selected_index == 2:  # Exit
                            pygame.quit()
                            quit()

    def change_difficulty(self):
        self.difficulty += 5  # Aumentar la velocidad de los meteoros
        self.screen.blit(self.background, [0, 0])
        self.draw_text(self.screen, f"Dificultad Incrementada a {self.difficulty}", 30, WIDTH // 2, HEIGHT // 2)
        pygame.display.flip()
        pygame.time.wait(1000)  # Espera 1 segundo y vuelve al menú

    def draw_menu(self, selected_index):
        self.screen.blit(self.background, [0, 0])
        menu_items = ["Iniciar", f"Cambiar Dificultad ({self.difficulty} %)", "Salir"]
        
        for index, item in enumerate(menu_items):
            selected = index == selected_index
            self.draw_text(self.screen, item, 27, WIDTH // 2, HEIGHT // 2 + index * 50, selected)
        
        self.draw_text(self.screen, f"Puntaje maximo: {self.highscore}", 20, WIDTH // 2, HEIGHT * 3/4)
        pygame.display.flip()

    def show_go_screen(self, final_score=None):
        self.screen.blit(self.background, [0, 0])
        self.draw_text(self.screen, "SHOOTER", 65, WIDTH // 2, HEIGHT // 4)
        self.draw_text(self.screen, "Presione alguna tecla para comenzar", 20, WIDTH // 2, HEIGHT * 3/4)
        if final_score is not None:
            self.draw_text(self.screen, f"Final Score: {final_score}", 27, WIDTH // 2, HEIGHT // 2)
        pygame.display.flip()
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.KEYUP:
                    waiting = False

    def new_game(self):
        """Inicializa los sprites y listas"""
        self.all_sprites = pygame.sprite.Group()
        self.meteor_list = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()

        self.player = Player(self)
        self.all_sprites.add(self.player)

        # Añadir meteoritos
        for i in range(8):
            meteor = Meteor(self)
            self.all_sprites.add(meteor)
            self.meteor_list.add(meteor)

        self.score = 0

    def run(self):
        """Loop principal del juego"""
        while self.running:
            if self.game_over:
                menu_choice = self.show_menu()
                if menu_choice == 'change_difficulty':
                    self.change_difficulty()
                    continue  # Volver al menú
                self.new_game()  # Inicializa el nuevo juego
                self.game_over = False

            # Control del juego
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.player.shoot()

            self.all_sprites.update()

            # Detectar colisiones entre meteoros y balas
            hits = pygame.sprite.groupcollide(self.meteor_list, self.bullets, True, True)
            for hit in hits:
                self.score += 10
                explosion = Explosion(self, hit.rect.center)
                self.all_sprites.add(explosion)
                meteor = Meteor(self)
                self.all_sprites.add(meteor)
                self.meteor_list.add(meteor)

            # Detectar colisiones entre jugador y meteoros
            hits = pygame.sprite.spritecollide(self.player, self.meteor_list, True)
            for hit in hits:
                self.player.shield -= 25
                meteor = Meteor(self)
                self.all_sprites.add(meteor)
                self.meteor_list.add(meteor)
                if self.player.shield <= 0:
                    if self.score > self.highscore:
                        self.save_highscore(self.score)
                        self.highscore = self.score
                    self.game_over = True

            # Dibujar todo en la pantalla
            self.screen.blit(self.background, [0, 0])
            self.all_sprites.draw(self.screen)
            self.draw_text(self.screen, f"Puntaje actual: {self.score}", 20, WIDTH // 2, 10)
            self.draw_shield_bar(self.screen, 5, 5, self.player.shield)
            self.draw_text(self.screen, f"Puntahe maximo: {self.highscore}", 20, WIDTH - 120, 10)

            pygame.display.flip()

class Player(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.image = self.game.player_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10
        self.speed_x = 0
        self.shield = 100

    def update(self):
        self.speed_x = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speed_x = -5
        if keystate[pygame.K_RIGHT]:
            self.speed_x = 5
        self.rect.x += self.speed_x
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def shoot(self):
        bullet = Bullet(self.game, self.rect.centerx, self.rect.top)
        self.game.all_sprites.add(bullet)
        self.game.bullets.add(bullet)
        self.game.laser_sound.play()

class Meteor(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.image = random.choice(self.game.meteor_images)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-140, -100)
        self.speedy = random.randrange(1, self.game.difficulty)
        self.speedx = random.randrange(-5, 5)

    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top > HEIGHT + 10 or self.rect.left < -40 or self.rect.right > WIDTH + 40:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-140, - 100)
            self.speedy = random.randrange(1, self.game.difficulty)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__()
        self.game = game
        self.image = self.game.bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.y = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, game, center):
        super().__init__()
        self.game = game
        self.image = self.game.explosion_anim[0]
        self.rect = self.image.get_rect()
        self.rect.center = center 
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50 

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(self.game.explosion_anim):
                self.kill()
            else:
                center = self.rect.center
                self.image = self.game.explosion_anim[self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()