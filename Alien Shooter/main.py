import pygame
import cv2
import sys
import random
import numpy as np
import os
import math
import json
pygame.init()
translations = {
    "en": {
        "title": "Alien Shooter",
        "start": "Start Game",
        "settings": "Settings",
        "quit": "Quit",
        "resolution": "Resolution",
        "language": "Language",
        "back": "Back",
        "sound": "Sound",
        "music": "Music",
        "on": "On",
        "off": "Off",
        "apply": "Apply",
        "score": "Score",
        "high_score": "High Score",
        "lives": "Lives",
        "wave": "Wave",
        "weapon_level": "Weapon Level",
        "upgrade_weapon": "S: Upgrade Weapon (50)",
        "extra_life": "H: Extra Life (100)",
        "shield": "P: Energy Shield (150)",
        "game_over": "GAME OVER",
        "restart": "Press R to Restart",
        "final_score": "Final Score",
        "continue": "Continue",
        "new_game": "New Game"},
    "tr": {
        "title": "Uzaylı Avcısı",
        "start": "Oyunu Başlat",
        "settings": "Ayarlar",
        "quit": "Çıkış",
        "resolution": "Çözünürlük",
        "language": "Dil",
        "back": "Geri",
        "sound": "Ses Efektleri",
        "music": "Müzik",
        "on": "Açık",
        "off": "Kapalı",
        "apply": "Uygula",
        "score": "Skor",
        "high_score": "En Yüksek Skor",
        "lives": "Can",
        "wave": "Dalga",
        "weapon_level": "Silah Seviyesi",
        "upgrade_weapon": "S: Silah Geliştir (50)",
        "extra_life": "H: Ekstra Can (100)",
        "shield": "P: Enerji Kalkanı (150)",
        "game_over": "OYUN BİTTİ",
        "restart": "Yeniden Başlamak için R'ye basın",
        "final_score": "Son Skor",
        "continue": "Devam Et",
        "new_game": "Yeni Oyun"},
    "ru": {
        "title": "Охотник на Пришельцев",
        "start": "Начать Игру",
        "settings": "Настройки",
        "quit": "Выход",
        "resolution": "Разрешение",
        "language": "Язык",
        "back": "Назад",
        "sound": "Звуковые Эффекты",
        "music": "Музыка",
        "on": "Вкл",
        "off": "Выкл",
        "apply": "Применить",
        "score": "Счёт",
        "high_score": "Рекорд",
        "lives": "Жизни",
        "wave": "Волна",
        "weapon_level": "Уровень Оружия",
        "upgrade_weapon": "S: Улучшить Оружие (50)",
        "extra_life": "H: Доп. Жизнь (100)",
        "shield": "P: Энерг. Щит (150)",
        "game_over": "ИГРА ОКОНЧЕНА",
        "restart": "Нажмите R для перезапуска",
        "final_score": "Финальный Счёт",
        "continue": "Продолжить",
        "new_game": "Новая Игра"}}
def load_settings():
    settings = {
        "resolution": "1280x720",
        "language": "en",
        "sound": True,
        "music": True}
    try:
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as f:
                loaded_settings = json.load(f)
                for key in settings:
                    if key in loaded_settings:
                        settings[key] = loaded_settings[key]
    except:
        pass
    return settings
def save_settings(settings):
    try:
        with open("settings.json", "w") as f:
            json.dump(settings, f)
    except:
        pass
def get_resolution(res_str):
    res_map = {
        "1280x720": (1280, 720),
        "1920x1080": (1920, 1080),
        "2560x1440" : (2560, 1440)}
    return res_map.get(res_str, (1280, 720))
settings = load_settings()
WIDTH, HEIGHT = get_resolution(settings["resolution"])
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(translations[settings["language"]]["title"])
def tr(key):
    return translations[settings["language"]].get(key, key)
video = None
def load_video():
    global video
    if video is not None:
        video.release()
    try:
        video = cv2.VideoCapture("assets/video.mp4")
        return int(video.get(cv2.CAP_PROP_FPS)) or 30
    except:
        return 30
fps = load_video()
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 6)
        self.speed_x = random.uniform(-3, 3)
        self.speed_y = random.uniform(-3, 3)
        self.life = random.randint(20, 40)
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.life -= 1
        self.size = max(0, self.size - 0.1)
        return self.life > 0
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.size))
class PowerUp:
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type
        self.size = 20
        self.speed = 2
        self.colors = {"health": (255, 50, 50), "weapon": (50, 255, 50), "shield": (50, 150, 255)}
        self.pulse = 0
        self.pulse_dir = 1
    def update(self):
        self.y += self.speed
        self.pulse += 0.1 * self.pulse_dir
        if self.pulse > 1 or self.pulse < 0:
            self.pulse_dir *= -1
        return self.y < HEIGHT
    def draw(self, surface):
        pulse_size = self.size + 5 * math.sin(self.pulse * math.pi)
        pygame.draw.circle(surface, self.colors[self.type], (int(self.x), int(self.y)), int(pulse_size))
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x), int(self.y)), int(pulse_size), 2)
    def get_rect(self):
        return pygame.Rect(self.x - self.size, self.y - self.size, self.size*2, self.size*2)
pygame.mixer.init()
shoot_sound = pygame.mixer.Sound("assets/shoot.wav")
explosion_sound = pygame.mixer.Sound("assets/explosion.wav")
boss_sound = pygame.mixer.Sound("assets/boss.wav")
gameover_sound = pygame.mixer.Sound("assets/gameover.wav")
powerup_sound = pygame.mixer.Sound("assets/powerup.wav")
click_sound = pygame.mixer.Sound("assets/click.wav")
pygame.mixer.music.load("assets/ambient.wav")
if settings["music"]:
    pygame.mixer.music.play(-1)
player_right_imgs = []
player_left_imgs = []
try:
    player_right_imgs = [pygame.transform.scale(pygame.image.load(f"assets/player_walk{i}.png"), (60, 60)) for i in range(1, 3)]
    player_left_imgs = [pygame.transform.flip(img, True, False) for img in player_right_imgs]
except:
    player_right_imgs = [pygame.Surface((60, 60), pygame.SRCALPHA)]
    pygame.draw.rect(player_right_imgs[0], (0, 255, 0), (10, 10, 40, 40))
    player_left_imgs = [player_right_imgs[0]]
player_img = player_right_imgs[0]
direction = "right"
walk_index = 0
walk_delay = 0
enemy_imgs = []
try:
    enemy_imgs = [
        pygame.transform.scale(pygame.image.load("assets/enemy.png"), (50, 50)),
        pygame.transform.scale(pygame.image.load("assets/enemy2.png"), (50, 50))
    ]
except:
    img = pygame.Surface((50, 50), pygame.SRCALPHA)
    pygame.draw.rect(img, (255, 0, 0), (5, 5, 40, 40))
    enemy_imgs = [img]
boss_img = None
try:
    boss_img = pygame.transform.scale(pygame.image.load("assets/boss.png"), (200, 100))
except:
    boss_img = pygame.Surface((200, 100), pygame.SRCALPHA)
    pygame.draw.rect(boss_img, (255, 0, 255), (10, 10, 180, 80))
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 150, 255)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
MENU_BG = (10, 20, 40, 200)
BUTTON_NORMAL = (70, 130, 180)
BUTTON_HOVER = (100, 180, 255)
font = None
big = None
clock = pygame.time.Clock()
score_file = "highscore.txt"
upgrade_ready = True
shield_active = False
shield_timer = 0
game_paused = False
def load_score():
    if os.path.exists(score_file):
        with open(score_file, "r") as f:
            return int(f.read())
    return 0
def save_score(score):
    with open(score_file, "w") as f:
        f.write(str(score))
def get_frame():
    if video is None:
        return pygame.Surface((WIDTH, HEIGHT))
    ret, frame = video.read()
    if not ret or frame is None:
        video.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret, frame = video.read()
        if not ret or frame is None:
            return pygame.Surface((WIDTH, HEIGHT))
    frame = cv2.resize(frame, (WIDTH, HEIGHT))
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = np.rot90(frame)
    return pygame.surfarray.make_surface(frame)
def reset_game():
    global px, py, bullets, enemies, bt, bl, score, lives, game_over
    global wave, boss_on, boss_hp, bx, by, player_img, direction, high_score
    global walk_index, walk_delay, upgrade_ready, particles, powerups
    global enemy_anim_delay, shield_active, shield_timer, game_paused
    px, py = WIDTH // 2, HEIGHT - 100
    bullets = []
    enemies = []
    bt = 0
    bl = 1
    score = 0
    lives = 3
    game_over = False
    wave = 0
    boss_on = False
    boss_hp = 0
    bx, by = WIDTH // 2 - 100, 50
    player_img = player_right_imgs[0]
    direction = "right"
    high_score = load_score()
    walk_index = 0
    walk_delay = 0
    upgrade_ready = True
    particles = []
    powerups = []
    enemy_anim_delay = 0
    shield_active = False
    shield_timer = 0
    game_paused = False
reset_game()
ps, bs, bc, es = 6, 10, 10, 2
spawn_rate = 30
class Button:
    def __init__(self, x, y, width, height, text, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.hovered = False
    def draw(self, surface):
        color = BUTTON_HOVER if self.hovered else BUTTON_NORMAL
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=10)
        text_surf = font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)
        return self.hovered
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered and self.action:
                if settings["sound"]:
                    click_sound.play()
                return self.action()
        return None
def main_menu():
    global font, big, screen, WIDTH, HEIGHT, settings
    font = pygame.font.SysFont("Arial", max(24, int(HEIGHT/30)))
    big = pygame.font.SysFont("Arial", max(60, int(HEIGHT/12)))
    buttons = [
        Button(WIDTH//2-150, HEIGHT//2-100, 300, 60, tr("start"), lambda: "playing"),
        Button(WIDTH//2-150, HEIGHT//2, 300, 60, tr("settings"), lambda: "settings"),
        Button(WIDTH//2-150, HEIGHT//2+100, 300, 60, tr("quit"), lambda: "quit")
    ]
    state = "main_menu"
    while state == "main_menu":
        screen.blit(get_frame(), (0, 0))
        menu_bg = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(menu_bg, MENU_BG, (0, 0, WIDTH, HEIGHT))
        screen.blit(menu_bg, (0, 0))
        title = big.render(tr("title"), True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//6))
        mouse_pos = pygame.mouse.get_pos()
        for button in buttons:
            button.check_hover(mouse_pos)
            button.draw(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            
            for button in buttons:
                result = button.handle_event(event)
                if result:
                    if result == "quit":
                        return "quit"
                    state = result
        pygame.display.update()
        clock.tick(30)
    return state
def settings_menu():
    global font, big, screen, WIDTH, HEIGHT, settings
    resolutions = ["1280x720", "1920x1080", "2560x1440"]
    languages = ["en", "tr", "ru"]
    buttons = [
        Button(WIDTH//2-150, HEIGHT-100, 300, 60, tr("back"), lambda: "back"),
        Button(WIDTH//2-150, HEIGHT//2+180, 300, 60, tr("apply"), lambda: "apply")
    ]
    res_buttons = []
    for i, res in enumerate(resolutions):
        res_buttons.append(Button(WIDTH//2-300, HEIGHT//4 + i*70, 200, 50, res, lambda r=res: r))
    lang_buttons = []
    for i, lang in enumerate(languages):
        lang_name = "English" if lang == "en" else "Türkçe" if lang == "tr" else "Русский"
        lang_buttons.append(Button(WIDTH//2+50, HEIGHT//4 + i*70, 200, 50, lang_name, lambda l=lang: l))
    sound_buttons = [
        Button(WIDTH//2-300, HEIGHT//2+80, 200, 50, tr("on" if settings["sound"] else "off"), lambda: "sound"),
        Button(WIDTH//2+50, HEIGHT//2+80, 200, 50, tr("on" if settings["music"] else "off"), lambda: "music")]
    state = "settings"
    while state == "settings":
        screen.blit(get_frame(), (0, 0))
        menu_bg = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(menu_bg, MENU_BG, (0, 0, WIDTH, HEIGHT))
        screen.blit(menu_bg, (0, 0))
        title = big.render(tr("settings"), True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//10))
        screen.blit(font.render(tr("resolution"), True, WHITE), (WIDTH//2-300, HEIGHT//4-40))
        screen.blit(font.render(tr("language"), True, WHITE), (WIDTH//2+50, HEIGHT//4-40))
        screen.blit(font.render(tr("sound"), True, WHITE), (WIDTH//2-300, HEIGHT//2+40))
        screen.blit(font.render(tr("music"), True, WHITE), (WIDTH//2+50, HEIGHT//2+40))
        mouse_pos = pygame.mouse.get_pos()
        for button in res_buttons:
            button.check_hover(mouse_pos)
            if button.action() == settings["resolution"]:
                pygame.draw.rect(screen, BUTTON_HOVER, button.rect, border_radius=10)
            button.draw(screen)
        for button in lang_buttons:
            button.check_hover(mouse_pos)
            if button.action() == settings["language"]:
                pygame.draw.rect(screen, BUTTON_HOVER, button.rect, border_radius=10)
            button.draw(screen)
        for button in sound_buttons:
            button.check_hover(mouse_pos)
            button.text = tr("on" if (button.action() == "sound" and settings["sound"]) or 
                             (button.action() == "music" and settings["music"]) else "off")
            button.draw(screen)
        for button in buttons:
            button.check_hover(mouse_pos)
            button.draw(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            for button in res_buttons:
                result = button.handle_event(event)
                if result:
                    settings["resolution"] = result
            for button in lang_buttons:
                result = button.handle_event(event)
                if result:
                    settings["language"] = result
            for button in sound_buttons:
                result = button.handle_event(event)
                if result == "sound":
                    settings["sound"] = not settings["sound"]
                elif result == "music":
                    settings["music"] = not settings["music"]
                    if settings["music"]:
                        pygame.mixer.music.play(-1)
                    else:
                        pygame.mixer.music.stop()
            for button in buttons:
                result = button.handle_event(event)
                if result == "back":
                    return "main_menu"
                elif result == "apply":
                    new_width, new_height = get_resolution(settings["resolution"])
                    if new_width != WIDTH or new_height != HEIGHT:
                        WIDTH, HEIGHT = new_width, new_height
                        screen = pygame.display.set_mode((WIDTH, HEIGHT))
                        pygame.display.set_caption(tr("title"))
                        fps = load_video()
                    save_settings(settings)
                    return "main_menu"
        pygame.display.update()
        clock.tick(30)
    return "main_menu"
def in_game_menu():
    global font, big, screen, game_paused
    buttons = [
        Button(WIDTH//2-150, HEIGHT//2-80, 300, 60, tr("continue"), lambda: "continue"),
        Button(WIDTH//2-150, HEIGHT//2, 300, 60, tr("settings"), lambda: "settings"),
        Button(WIDTH//2-150, HEIGHT//2+80, 300, 60, tr("quit"), lambda: "quit")
    ]
    state = "paused"
    while state == "paused":
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        title = big.render(tr("title"), True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//4))
        mouse_pos = pygame.mouse.get_pos()
        for button in buttons:
            button.check_hover(mouse_pos)
            button.draw(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "continue"
            for button in buttons:
                result = button.handle_event(event)
                if result:
                    if result == "quit":
                        return "quit"
                    state = result
        pygame.display.update()
        clock.tick(30)
    return state
def game_loop():
    global px, py, bullets, enemies, bt, bl, score, lives, game_over
    global wave, boss_on, boss_hp, bx, by, player_img, direction, high_score
    global walk_index, walk_delay, upgrade_ready, particles, powerups
    global enemy_anim_delay, shield_active, shield_timer, game_paused
    global font, big
    global screen
    font = pygame.font.SysFont("Arial", max(24, int(HEIGHT/40)))
    big = pygame.font.SysFont("Arial", max(60, int(HEIGHT/12)))
    continue_button = Button(WIDTH//2-150, HEIGHT//2+100, 300, 60, tr("continue"), lambda: None)
    state = "playing"
    while state == "playing":
        screen.blit(get_frame(), (0, 0))
        for _ in range(2):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            size = random.uniform(0.5, 2)
            brightness = random.randint(150, 255)
            pygame.draw.circle(screen, (brightness, brightness, brightness), (x, y), size)
        if game_over:
            screen.blit(player_img, (px, py))
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            screen.blit(big.render(tr("game_over"), True, RED), (WIDTH // 2 - 180, HEIGHT // 2 - 100))
            screen.blit(font.render(f"{tr('final_score')}: {score}", True, WHITE), (WIDTH // 2 - 100, HEIGHT // 2 - 20))
            screen.blit(font.render(tr("restart"), True, WHITE), (WIDTH // 2 - 150, HEIGHT // 2 + 40))
            mouse_pos = pygame.mouse.get_pos()
            continue_button.text = tr("new_game")
            continue_button.check_hover(mouse_pos)
            continue_button.draw(screen)
            pygame.display.update()
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return "quit"
                if e.type == pygame.KEYDOWN and e.key == pygame.K_r:
                    if score > high_score:
                        save_score(score)
                    gameover_sound.play()
                    reset_game()
                    return "playing"
                if continue_button.handle_event(e):
                    if score > high_score:
                        save_score(score)
                    reset_game()
                    return "playing"
            continue
        if game_paused:
            result = in_game_menu()
            if result == "continue":
                game_paused = False
            elif result == "settings":
                settings_result = settings_menu()
                if settings_result == "main_menu":
                    return "main_menu"
                else:
                    game_paused = False
            elif result == "quit":
                return "main_menu"
            font = pygame.font.SysFont("Arial", max(24, int(HEIGHT/40)))
            big = pygame.font.SysFont("Arial", max(60, int(HEIGHT/12)))
            continue
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "quit"
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                game_paused = True
                continue
            if e.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                dx, dy = mx - (px + 30), my - (py + 30)
                angle = np.arctan2(dy, dx)
                for i in range(bl):
                    bullets.append([px + 30, py + 30, np.cos(angle), np.sin(angle)])
                direction = "right" if dx >= 0 else "left"
                if settings["sound"]:
                    shoot_sound.play()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_s and score >= 50 and bl < 5 and upgrade_ready:
                    bl += 1
                    score -= 50
                    upgrade_ready = False
                if e.key == pygame.K_h and score >= 100 and lives < 5:
                    lives += 1
                    score -= 100
                if e.key == pygame.K_p and score >= 150 and not shield_active:
                    shield_active = True
                    shield_timer = 300
                    score -= 150
            
            if e.type == pygame.KEYUP:
                if e.key == pygame.K_s:
                    upgrade_ready = True
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and px > 0:
            px -= ps
            direction = "left"
        if keys[pygame.K_RIGHT] and px < WIDTH - 60:
            px += ps
            direction = "right"
        if keys[pygame.K_UP] and py > 0:
            py -= ps
        if keys[pygame.K_DOWN] and py < HEIGHT - 60:
            py += ps
        if keys[pygame.K_SPACE] and bt == 0:
            mx, my = pygame.mouse.get_pos()
            dx, dy = mx - (px + 30), my - (py + 30)
            angle = np.arctan2(dy, dx)
            for i in range(bl):
                bullets.append([px + 30, py + 30, np.cos(angle), np.sin(angle)])
            bt = bc
            direction = "right" if dx >= 0 else "left"
            if settings["sound"]:
                shoot_sound.play()
        if bt > 0:
            bt -= 1
        if shield_active:
            shield_timer -= 1
            if shield_timer <= 0:
                shield_active = False
        walk_delay += 1
        if walk_delay >= 10:
            walk_index = (walk_index + 1) % len(player_right_imgs)
            walk_delay = 0
        player_img = player_right_imgs[walk_index] if direction == "right" else player_left_imgs[walk_index]
        for b in bullets:
            b[0] += bs * b[2]
            b[1] += bs * b[3]
        bullets = [b for b in bullets if 0 < b[0] < WIDTH and 0 < b[1] < HEIGHT]
        enemy_anim_delay = (enemy_anim_delay + 1) % 10
        if not enemies and not boss_on:
            wave += 1
            spawn_rate = max(5, 30 - wave * 2)
            if wave % 5 == 0:
                boss_on = True
                boss_hp = 100 + wave * 20
                bx, by = WIDTH // 2 - 100, 50
                if settings["sound"]:
                    boss_sound.play()
            else:
                for _ in range(wave * 2):
                    enemies.append([random.randint(0, WIDTH - 50), random.randint(-100, 0), 
                                  random.uniform(-1, 1)])
        for e in enemies:
            e[1] += es
            e[0] += e[2]
            if e[0] <= 0 or e[0] >= WIDTH - 50:
                e[2] *= -1
        for b in bullets[:]:
            hit = False
            for e in enemies[:]:
                if e[0] < b[0] < e[0] + 50 and e[1] < b[1] < e[1] + 50:
                    enemies.remove(e)
                    bullets.remove(b)
                    score += 10
                    if settings["sound"]:
                        explosion_sound.play()
                    for _ in range(20):
                        particles.append(Particle(e[0] + 25, e[1] + 25, 
                                              (random.randint(200, 255), random.randint(100, 150), 50)))
                    if random.random() < 0.2:
                        power_type = random.choice(["health", "weapon", "shield"])
                        powerups.append(PowerUp(e[0] + 25, e[1] + 25, power_type))
                    hit = True
                    break
            if not hit and boss_on:
                if bx < b[0] < bx + 200 and by < b[1] < by + 100:
                    bullets.remove(b)
                    boss_hp -= 5
                    if settings["sound"]:
                        explosion_sound.play()
                    for _ in range(5):
                        particles.append(Particle(b[0], b[1], 
                                              (random.randint(200, 255), random.randint(100, 150), 50)))
                    if boss_hp <= 0:
                        boss_on = False
                        score += 100
                        for _ in range(100):
                            particles.append(Particle(bx + 100, by + 50, 
                                                  (random.randint(200, 255), random.randint(100, 150), 50)))
        if boss_on:
            bx += random.choice([-1, 0, 1]) * 3
            bx = max(0, min(WIDTH - 200, bx))
            if random.random() < 0.02:
                angle = math.atan2(py + 30 - (by + 50), px + 30 - (bx + 100))
                bullets.append([bx + 100, by + 100, math.cos(angle), math.sin(angle)])
        for e in enemies[:]:
            if e[1] > HEIGHT:
                enemies.remove(e)
                if not shield_active:
                    lives -= 1
                    screen_shake = 10
                    for _ in range(screen_shake):
                        offset_x = random.randint(-5, 5)
                        offset_y = random.randint(-5, 5)
                        screen.blit(get_frame(), (offset_x, offset_y))
                        pygame.display.flip()
                        pygame.time.delay(30)
                    if lives <= 0:
                        game_over = True
        particles = [p for p in particles if p.update()]
        powerups = [p for p in powerups if p.update()]
        for p in powerups[:]:
            player_rect = pygame.Rect(px, py, 60, 60)
            if player_rect.colliderect(p.get_rect()):
                powerups.remove(p)
                if settings["sound"]:
                    powerup_sound.play()
                
                if p.type == "health" and lives < 5:
                    lives += 1
                elif p.type == "weapon" and bl < 5:
                    bl += 1
                elif p.type == "shield":
                    shield_active = True
                    shield_timer = 300
        for p in particles:
            p.draw(screen)
        for p in powerups:
            p.draw(screen)
        if boss_on:
            screen.blit(boss_img, (bx, by))
            bar_width = 200
            health_width = max(0, int(bar_width * (boss_hp / (100 + wave * 20))))
            pygame.draw.rect(screen, RED, (bx, by - 20, bar_width, 10))
            pygame.draw.rect(screen, GREEN, (bx, by - 20, health_width, 10))
            pygame.draw.rect(screen, WHITE, (bx, by - 20, bar_width, 10), 2)
        screen.blit(player_img, (px, py))
        if shield_active:
            shield_alpha = min(255, shield_timer // 2)
            shield_surface = pygame.Surface((80, 80), pygame.SRCALPHA)
            pygame.draw.circle(shield_surface, (50, 150, 255, shield_alpha), (40, 40), 40)
            pygame.draw.circle(shield_surface, (200, 200, 255, shield_alpha), (40, 40), 40, 2)
            screen.blit(shield_surface, (px - 10, py - 10))
        for b in bullets:
            glow_surface = pygame.Surface((15, 25), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (255, 255, 200, 100), (0, 0, 15, 25))
            pygame.draw.rect(glow_surface, WHITE, (5, 5, 5, 15))
            screen.blit(glow_surface, (b[0] - 5, b[1] - 5))
            pygame.draw.rect(screen, WHITE, (b[0], b[1], 5, 15))
        for e in enemies:
            enemy_img = enemy_imgs[0] if enemy_anim_delay < 5 else enemy_imgs[1] if len(enemy_imgs) > 1 else enemy_imgs[0]
            screen.blit(enemy_img, (e[0], e[1]))
        screen.blit(font.render(f"{tr('score')}:{score}", True, WHITE), (10, 10))
        screen.blit(font.render(f"{tr('high_score')}:{high_score}", True, WHITE), (10, 40))
        for i in range(lives):
            pygame.draw.circle(screen, RED, (WIDTH - 40 - i*30, 25), 12)
            pygame.draw.circle(screen, WHITE, (WIDTH - 40 - i*30, 25), 12, 2)
        screen.blit(font.render(f"{tr('wave')}:{wave}", True, WHITE), (WIDTH // 2 - 60, 10))
        screen.blit(font.render(tr("upgrade_weapon"), True, WHITE), (WIDTH // 2 - 160, HEIGHT - 80))
        screen.blit(font.render(tr("extra_life"), True, WHITE), (WIDTH // 2 - 160, HEIGHT - 50))
        screen.blit(font.render(tr("shield"), True, WHITE), (WIDTH // 2 - 160, HEIGHT - 20))
        for i in range(bl):
            glow_surface = pygame.Surface((15, 25), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (255, 255, 200, 100), (0, 0, 15, 25))
            pygame.draw.rect(glow_surface, YELLOW, (5, 5, 5, 15))
            screen.blit(glow_surface, (10 + i * 20 - 5, 100 - 5))
            pygame.draw.rect(screen, YELLOW, (10 + i * 20, 100, 5, 15))
        screen.blit(font.render(f"{tr('weapon_level')}: {bl}", True, YELLOW), (10, 135))
        if shield_active:
            shield_percent = shield_timer / 300
            bar_width = 100
            pygame.draw.rect(screen, BLUE, (WIDTH - 120, 50, bar_width * shield_percent, 10))
            pygame.draw.rect(screen, WHITE, (WIDTH - 120, 50, bar_width, 10), 2)
            screen.blit(font.render("SHIELD", True, BLUE), (WIDTH - 120, 30))
        screen.blit(font.render("ESC: " + tr("pause"), True, WHITE), (WIDTH - 200, HEIGHT - 30))
        pygame.display.update()
        clock.tick(fps)
    return "main_menu"
def main():
    pygame.display.set_caption(tr("title"))
    state = "main_menu"
    while True:
        if state == "main_menu":
            state = main_menu()
        elif state == "settings":
            state = settings_menu()
        elif state == "playing":
            state = game_loop()
        elif state == "quit":
            if video is not None:
                video.release()
            pygame.quit()
            sys.exit()
if __name__ == "__main__":
    main()