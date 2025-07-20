import pygame
import cv2
import sys
import random
import numpy as np
import os
import math
import json

pygame.init()

# --- DİL TƏRCÜMƏLƏRİ ---
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
        "new_game": "New Game",
        "pause": "Pause",
        "skip": "SKIP (ESC)"
    },
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
        "new_game": "Yeni Oyun",
        "pause": "Duraklat",
        "skip": "GEÇ (ESC)"
    },
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
        "new_game": "Новая Игра",
        "pause": "Пауза",
        "skip": "ПРОПУСТИТЬ (ESC)"
    }
}

# --- AYAR İDARƏETMƏSİ ---
def load_settings():
    settings = {
        "resolution": "1280x720",
        "language": "en",
        "sound": True,
        "music": True
    }
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
        "2560x1440": (2560, 1440)
    }
    return res_map.get(res_str, (1280, 720))

settings = load_settings()
WIDTH, HEIGHT = get_resolution(settings["resolution"])
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(translations[settings["language"]]["title"])

def tr(key):
    return translations[settings["language"]].get(key, key)

# --- RƏNGLƏR VƏ SABİTLƏR ---
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 150, 255)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
MENU_BG = (10, 20, 40, 200)
BUTTON_NORMAL = (70, 130, 180)
BUTTON_HOVER = (100, 180, 255)

font = pygame.font.SysFont("Arial", 24)
big = pygame.font.SysFont("Arial", 60)
clock = pygame.time.Clock()

# --- DÜYMƏ (BUTTON) SİNİFİ ---
class Button:
    def __init__(self, x, y, width, height, text, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.hovered = False

    def draw(self, surface, custom_font=None):
        f = custom_font if custom_font else font
        color = BUTTON_HOVER if self.hovered else BUTTON_NORMAL
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=10)
        text_surf = f.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)
        return self.hovered

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered and self.action:
                if settings["sound"]:
                    try: click_sound.play()
                    except: pass
                return self.action()
        return None

# --- VİDEO ARXA PLAN İDARƏETMƏSİ ---
video = None
def load_video():
    global video
    if video is not None:
        video.release()
    try:
        video = cv2.VideoCapture("assets/video.mp4")
        return int(video.get(cv2.CAP_PROP_FPS)) or 120
    except:
        return 120

fps = load_video()

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

# --- HEKAYƏ GİRİŞİ FUNKSİYASI ---
def story_intro():
    story_font = pygame.font.SysFont("Arial", max(32, int(HEIGHT / 25)))
    
    story_text = """
Bir zamanlar Samanyolu, insanlığın Altın Çağı'na şahitlik edirdi.
Yıldızlara uzanan koloniler, barış ve refah içinde parlıyordu.

Ancak bu barış, evrenin derinliklerinden gelen bir fısıltıyla son buldu.
Onlara Sürü adını verdiler.

Biyomekanik ve doymak bilmez bir iştahla hareket eden bu varlıklar,
karşılarına çıkan her şeyi tüketen bir felaketti.
Görkemli filolarımız, onların kaotik ve ezici sayısal üstünlüğü
karşısında bir bir eridi.

Umut, yerini sessiz bir korkuya bırakmıştı.
İnsanlığın son kaleleri, birer birer düşüyordu.

Sektör 7, iç bölgelere açılan son tahliye koridorunun bekçisiydi.
Milyonlarca insanın son kaçış umudu...

Sürü'nün devasa gücü bu sektöre yöneldiğinde,
tüm savunma hatları saniyeler içinde çöktü.

Geriye sadece tek bir gemi, tek bir sinyal kaldı.

"YILDIRIM"

Deneysel avcı gemisinin pilotu olarak sen,
filonun geri kalanından kopmuş, tek başına kalmıştın.

Geri çekilmek bir seçenekti. Ama bu, milyonlarca masum insanı
ölüme terk etmek demekti.

Görevin belli:

HATTI TUT. NE PAHASINA OLURSA OLSUN.

Sürü'nün sonsuz dalgalarına karşı dur.
Savaştıkça güçlen, liderlerini yok et ve insanlığa
ihtiyaç duyduğu o değerli zamanı kazandır.

Sen onların son umudusun...
"""
    lines = story_text.strip().split('\n')
    rendered_lines = [story_font.render(line, True, YELLOW) for line in lines]
    
    line_height = story_font.get_linesize()
    total_text_height = len(rendered_lines) * line_height
    scroll_y = HEIGHT
    scroll_speed = 1.2

    skip_font = pygame.font.SysFont("Arial", max(24, int(HEIGHT / 35)))
    skip_button = Button(WIDTH - 220, HEIGHT - 70, 200, 50, tr("skip"), lambda: "skip")
    
    state = "story"
    while state == "story":
        screen.blit(get_frame(), (0, 0))

        for i, line_surface in enumerate(rendered_lines):
            text_rect = line_surface.get_rect(centerx=WIDTH / 2, top=scroll_y + i * line_height)
            screen.blit(line_surface, text_rect)
        
        mouse_pos = pygame.mouse.get_pos()
        skip_button.check_hover(mouse_pos)
        skip_button.draw(screen, custom_font=skip_font)
        
        scroll_y -= scroll_speed
        
        if scroll_y + total_text_height < 0:
            state = "finished"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                state = "finished"
            if skip_button.handle_event(event) == "skip":
                state = "finished"

        pygame.display.update()
        clock.tick(60)

    return "main_menu"

# --- ZƏRRƏCİK (PARTICLE) SİNİFİ ---
class Particle:
    def __init__(self, x, y, color):
        self.x, self.y, self.color = x, y, color
        self.size = random.randint(2, 6)
        self.speed_x, self.speed_y = random.uniform(-3, 3), random.uniform(-3, 3)
        self.life = random.randint(20, 40)

    def update(self):
        self.x += self.speed_x; self.y += self.speed_y
        self.life -= 1; self.size = max(0, self.size - 0.1)
        return self.life > 0

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.size))

# --- GÜCLƏNDİRMƏ (POWERUP) SİNİFİ ---
class PowerUp:
    def __init__(self, x, y, type):
        self.x, self.y, self.type = x, y, type
        self.size, self.speed = 20, 2
        self.colors = {"health": (255, 50, 50), "weapon": (50, 255, 50), "shield": (50, 150, 255)}
        self.pulse, self.pulse_dir = 0, 1

    def update(self):
        self.y += self.speed
        self.pulse += 0.1 * self.pulse_dir
        if self.pulse > 1 or self.pulse < 0: self.pulse_dir *= -1
        return self.y < HEIGHT

    def draw(self, surface):
        pulse_size = self.size + 5 * math.sin(self.pulse * math.pi)
        pygame.draw.circle(surface, self.colors[self.type], (int(self.x), int(self.y)), int(pulse_size))
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), int(pulse_size), 2)

    def get_rect(self):
        return pygame.Rect(self.x - self.size, self.y - self.size, self.size * 2, self.size * 2)

# --- SƏS VƏ MUSİQİ YÜKLƏNMƏSİ ---
pygame.mixer.init()
try:
    shoot_sound = pygame.mixer.Sound("assets/shoot.wav")
    explosion_sound = pygame.mixer.Sound("assets/explosion.wav")
    boss_sound = pygame.mixer.Sound("assets/boss.wav")
    gameover_sound = pygame.mixer.Sound("assets/gameover.wav")
    powerup_sound = pygame.mixer.Sound("assets/powerup.wav")
    click_sound = pygame.mixer.Sound("assets/click.wav")
    pygame.mixer.music.load("assets/ambient.wav")
except pygame.error as e:
    print(f"Səs faylları yüklənə bilmədi: {e}")
    class NullSound:
        def play(self): pass
    shoot_sound = explosion_sound = boss_sound = gameover_sound = powerup_sound = click_sound = NullSound()

# --- GÖRÜNTÜ YÜKLƏNMƏSİ ---
player_base_img, player_img_rotated = None, None
try:
    player_base_img = pygame.transform.scale(pygame.image.load("assets/player_walk1.png").convert_alpha(), (60, 60))
except:
    player_base_img = pygame.Surface((60, 60), pygame.SRCALPHA)
    pygame.draw.polygon(player_base_img, (0, 255, 0), [(30, 0), (0, 50), (60, 50)])
player_img_rotated = player_base_img

enemy_imgs = []
try:
    enemy_imgs = [pygame.transform.scale(pygame.image.load(f"assets/enemy{i}.png").convert_alpha(), (50, 50)) for i in ["", "2"]]
except:
    img = pygame.Surface((50, 50), pygame.SRCALPHA); pygame.draw.rect(img, (255, 0, 0), (5, 5, 40, 40)); enemy_imgs = [img]

boss_img = None
try:
    boss_img = pygame.transform.scale(pygame.image.load("assets/boss.png").convert_alpha(), (200, 100))
except:
    boss_img = pygame.Surface((200, 100), pygame.SRCALPHA); pygame.draw.rect(boss_img, (255, 0, 255), (10, 10, 180, 80))

# --- OYUN VƏZİYYƏTİ VƏ DƏYİŞƏNLƏR ---
score_file = "highscore.txt"
upgrade_ready, shield_active, game_paused = True, False, False
shield_timer = 0
px, py, bullets, boss_bullets, enemies, powerups, particles = 0, 0, [], [], [], [], []
bt, bl, score, lives, wave, boss_hp, bx, by, invincibility_timer = 0, 0, 0, 0, 0, 0, 0, 0, 0
game_over, boss_on = False, False
boss_speed_x, high_score = 3.0, 0
ps, bs, bc, es = 6, 10, 10, 2

def load_score():
    if os.path.exists(score_file):
        with open(score_file, "r") as f: return int(f.read())
    return 0

def save_score(s):
    with open(score_file, "w") as f: f.write(str(s))

def reset_game():
    global px, py, bullets, enemies, bt, bl, score, lives, game_over, wave, boss_on, boss_hp
    global bx, by, high_score, upgrade_ready, particles, powerups, shield_active, shield_timer
    global game_paused, boss_speed_x, invincibility_timer, boss_bullets
    
    px, py = WIDTH // 2 - 30, HEIGHT - 100
    bullets, boss_bullets, enemies, particles, powerups = [], [], [], [], []
    bt, bl, score, lives, game_over, wave, boss_on = 0, 1, 0, 3, False, 0, False
    boss_hp, bx, by, boss_speed_x = 0, WIDTH // 2 - 100, 50, 3.0
    high_score = load_score()
    upgrade_ready, shield_active, game_paused = True, False, False
    shield_timer, invincibility_timer = 0, 0

def fire_bullets(angle, level):
    if level <= 1:
        bullets.append([px + 30, py + 30, math.cos(angle), math.sin(angle)]); return
    spread_rad = math.radians((level - 1) * 15)
    angle_step = spread_rad / (level - 1) if level > 1 else 0
    start_angle = angle - spread_rad / 2
    for i in range(level):
        bullets.append([px + 30, py + 30, math.cos(start_angle + i * angle_step), math.sin(start_angle + i * angle_step)])

def main_menu():
    global font, big
    font = pygame.font.SysFont("Arial", max(24, int(HEIGHT / 30)))
    big = pygame.font.SysFont("Arial", max(60, int(HEIGHT / 12)))
    buttons = [
        Button(WIDTH // 2 - 150, HEIGHT // 2 - 100, 300, 60, tr("start"), lambda: "playing"),
        Button(WIDTH // 2 - 150, HEIGHT // 2, 300, 60, tr("settings"), lambda: "settings"),
        Button(WIDTH // 2 - 150, HEIGHT // 2 + 100, 300, 60, tr("quit"), lambda: "quit")
    ]
    state = "main_menu"
    while state == "main_menu":
        screen.blit(get_frame(), (0, 0))
        menu_bg = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); pygame.draw.rect(menu_bg, MENU_BG, (0, 0, WIDTH, HEIGHT)); screen.blit(menu_bg, (0, 0))
        title = big.render(tr("title"), True, WHITE); screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 6))
        mouse_pos = pygame.mouse.get_pos()
        for button in buttons: 
            button.check_hover(mouse_pos)
            button.draw(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "quit"
            for button in buttons:
                result = button.handle_event(event)
                if result: return result
        pygame.display.update(); clock.tick(30)
    return state

def settings_menu():
    global font, big, screen, WIDTH, HEIGHT, settings, fps
    font = pygame.font.SysFont("Arial", max(24, int(HEIGHT / 30)))
    big = pygame.font.SysFont("Arial", max(60, int(HEIGHT / 12)))
    resolutions = ["1280x720", "1920x1080", "2560x1440"]
    languages = ["en", "tr", "ru"]
    buttons = [
        Button(WIDTH // 2 - 150, HEIGHT - 100, 300, 60, tr("back"), lambda: "back"),
        Button(WIDTH // 2 - 150, HEIGHT // 2 + 180, 300, 60, tr("apply"), lambda: "apply")
    ]
    res_buttons = [Button(WIDTH // 2 - 300, HEIGHT // 4 + i * 70, 200, 50, res, lambda r=res: r) for i, res in enumerate(resolutions)]
    lang_buttons = [Button(WIDTH // 2 + 50, HEIGHT // 4 + i * 70, 200, 50, "English" if lang=="en" else "Türkçe" if lang=="tr" else "Русский", lambda l=lang: l) for i, lang in enumerate(languages)]
    sound_buttons = [
        Button(WIDTH // 2 - 300, HEIGHT // 2 + 80, 200, 50, "", lambda: "sound"),
        Button(WIDTH // 2 + 50, HEIGHT // 2 + 80, 200, 50, "", lambda: "music")]
    
    state = "settings"
    while state == "settings":
        screen.blit(get_frame(), (0, 0))
        menu_bg = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); pygame.draw.rect(menu_bg, MENU_BG, (0,0,WIDTH,HEIGHT)); screen.blit(menu_bg, (0,0))
        title = big.render(tr("settings"), True, WHITE); screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 10))
        screen.blit(font.render(tr("resolution"), True, WHITE), (WIDTH // 2 - 300, HEIGHT // 4 - 40))
        screen.blit(font.render(tr("language"), True, WHITE), (WIDTH // 2 + 50, HEIGHT // 4 - 40))
        screen.blit(font.render(tr("sound"), True, WHITE), (WIDTH // 2 - 300, HEIGHT // 2 + 40))
        screen.blit(font.render(tr("music"), True, WHITE), (WIDTH // 2 + 50, HEIGHT // 2 + 40))
        
        mouse_pos = pygame.mouse.get_pos()
        all_buttons = buttons + res_buttons + lang_buttons + sound_buttons

        for button in res_buttons:
            button.check_hover(mouse_pos)
            if button.text == settings["resolution"]: pygame.draw.rect(screen, BUTTON_HOVER, button.rect, border_radius=10)
            button.draw(screen)
        for button in lang_buttons:
            lang_code = "en" if "English" in button.text else "tr" if "Türkçe" in button.text else "ru"
            button.check_hover(mouse_pos)
            if lang_code == settings["language"]: pygame.draw.rect(screen, BUTTON_HOVER, button.rect, border_radius=10)
            button.draw(screen)
        for button in sound_buttons:
            button.check_hover(mouse_pos)
            button.text = tr("on") if (button.action() == "sound" and settings["sound"]) or (button.action() == "music" and settings["music"]) else tr("off")
            button.draw(screen)
        for button in buttons:
            button.check_hover(mouse_pos); button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "quit"
            for button in res_buttons:
                if button.handle_event(event): settings["resolution"] = button.text
            for button in lang_buttons:
                if button.handle_event(event):
                     lang_code = "en" if "English" in button.text else "tr" if "Türkçe" in button.text else "ru"
                     settings["language"] = lang_code
            for button in sound_buttons:
                if button.handle_event(event) == "sound": settings["sound"] = not settings["sound"]
                elif button.handle_event(event) == "music":
                    settings["music"] = not settings["music"]
                    if settings["music"]: pygame.mixer.music.play(-1)
                    else: pygame.mixer.music.stop()
            for button in buttons:
                result = button.handle_event(event)
                if result == "back": return "main_menu"
                elif result == "apply":
                    new_w, new_h = get_resolution(settings["resolution"])
                    if new_w != WIDTH or new_h != HEIGHT:
                        WIDTH, HEIGHT = new_w, new_h
                        screen = pygame.display.set_mode((WIDTH, HEIGHT))
                    pygame.display.set_caption(tr("title"))
                    fps = load_video()
                    save_settings(settings); return "main_menu"
        pygame.display.update(); clock.tick(30)
    return "main_menu"

def in_game_menu():
    global game_paused
    buttons = [
        Button(WIDTH // 2 - 150, HEIGHT // 2 - 80, 300, 60, tr("continue"), lambda: "continue"),
        Button(WIDTH // 2 - 150, HEIGHT // 2, 300, 60, tr("settings"), lambda: "settings"),
        Button(WIDTH // 2 - 150, HEIGHT // 2 + 80, 300, 60, tr("quit"), lambda: "quit_to_menu")
    ]
    state = "paused"
    while state == "paused":
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); overlay.fill((0, 0, 0, 150)); screen.blit(overlay, (0, 0))
        title = big.render(tr("title"), True, WHITE); screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 4))
        mouse_pos = pygame.mouse.get_pos()
        for button in buttons: button.check_hover(mouse_pos); button.draw(screen)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "quit_to_desktop"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: return "continue"
            for button in buttons:
                result = button.handle_event(event)
                if result: return result
        pygame.display.update(); clock.tick(30)
    return state

def game_loop():
    global px, py, bullets, enemies, bt, bl, score, lives, game_over, wave, boss_on, boss_hp, bx, by, player_img_rotated, high_score, upgrade_ready, particles, powerups, shield_active, shield_timer, game_paused, boss_speed_x, invincibility_timer, boss_bullets
    font = pygame.font.SysFont("Arial", max(24, int(HEIGHT / 40)))
    big = pygame.font.SysFont("Arial", max(60, int(HEIGHT / 12)))
    continue_button = Button(WIDTH // 2 - 150, HEIGHT // 2 + 100, 300, 60, "", lambda: "restart")
    
    enemy_anim_delay = 0

    state = "playing"
    while state == "playing":
        screen.blit(get_frame(), (0, 0))
        
        if game_over:
            player_rect = player_img_rotated.get_rect(center=(px + 30, py + 30)); screen.blit(player_img_rotated, player_rect)
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); overlay.fill((0, 0, 0, 150)); screen.blit(overlay, (0, 0))
            game_over_text = big.render(tr("game_over"), True, RED)
            screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width()//2, HEIGHT // 2 - 100))
            final_score_text = font.render(f"{tr('final_score')}: {score}", True, WHITE)
            screen.blit(final_score_text, (WIDTH // 2 - final_score_text.get_width()//2, HEIGHT // 2 - 20))
            restart_text = font.render(tr("restart"), True, WHITE)
            screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width()//2, HEIGHT // 2 + 40))
            
            continue_button.text = tr("new_game")
            continue_button.check_hover(pygame.mouse.get_pos())
            continue_button.draw(screen)

            pygame.display.update()
            
            for e in pygame.event.get():
                if e.type == pygame.QUIT: return "quit"
                if e.type == pygame.KEYDOWN and e.key == pygame.K_r: state = "restart"
                if continue_button.handle_event(e): state = "restart"
            if state == "restart":
                if score > high_score: save_score(score)
                if settings["sound"]: gameover_sound.play()
                return "playing"
            continue

        if game_paused:
            result = in_game_menu()
            if result == "continue": game_paused = False
            elif result == "settings": settings_menu()
            elif result == "quit_to_menu": return "main_menu"
            elif result == "quit_to_desktop": return "quit"
            font = pygame.font.SysFont("Arial", max(24, int(HEIGHT/40))); big = pygame.font.SysFont("Arial", max(60, int(HEIGHT/12)))
            continue
        
        if invincibility_timer > 0: invincibility_timer -= 1
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT: return "quit"
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE: game_paused = True; continue
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                mx, my = pygame.mouse.get_pos(); dx, dy = mx - (px + 30), my - (py + 30)
                angle = math.atan2(dy, dx); fire_bullets(angle, bl); shoot_sound.play()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_s and score >= 50 and bl < 5 and upgrade_ready: bl += 1; score -= 50; upgrade_ready = False
                if e.key == pygame.K_h and score >= 100 and lives < 5: lives += 1; score -= 100
                if e.key == pygame.K_p and score >= 150 and not shield_active: shield_active = True; shield_timer = 300; score -= 150
            if e.type == pygame.KEYUP and e.key == pygame.K_s: upgrade_ready = True

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: px = max(0, px - ps)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: px = min(WIDTH - 60, px + ps)
        if keys[pygame.K_UP] or keys[pygame.K_w]: py = max(0, py - ps)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: py = min(HEIGHT - 60, py + ps)
        
        if keys[pygame.K_SPACE] and bt == 0:
            mx, my = pygame.mouse.get_pos(); dx, dy = mx - (px + 30), my - (py + 30)
            angle = math.atan2(dy, dx); fire_bullets(angle, bl); bt = bc; shoot_sound.play()
        if bt > 0: bt -= 1

        if shield_active:
            shield_timer -= 1
            if shield_timer <= 0: shield_active = False
        
        mx, my = pygame.mouse.get_pos(); angle = math.degrees(math.atan2(-(my - (py + 30)), mx - (px + 30))) - 90
        player_img_rotated = pygame.transform.rotate(player_base_img, angle)
        player_rect = player_img_rotated.get_rect(center=(px + 30, py + 30))

        for b in bullets: b[0] += bs * b[2]; b[1] += bs * b[3]
        bullets = [b for b in bullets if 0 < b[0] < WIDTH and 0 < b[1] < HEIGHT]

        for b in boss_bullets[:]:
            b[0] += bs * b[2]; b[1] += bs * b[3]
            if not (0 < b[0] < WIDTH and 0 < b[1] < HEIGHT): boss_bullets.remove(b); continue
            if player_rect.collidepoint(b[0], b[1]) and not shield_active and invincibility_timer <= 0:
                boss_bullets.remove(b); lives -= 1; invincibility_timer = fps * 1.5; explosion_sound.play()
                if lives <= 0: game_over = True; break
        
        enemy_anim_delay = (pygame.time.get_ticks() // 200) % len(enemy_imgs)
        
        if not enemies and not boss_on:
            wave += 1
            if wave > 0 and wave % 5 == 0:
                boss_on = True; boss_speed_x = (3.0 + (wave // 5 - 1) * 0.5) * (1 if random.random() > 0.5 else -1)
                boss_hp = 100 + wave * 20; bx, by = WIDTH // 2 - 100, 50; boss_sound.play()
            else:
                for _ in range(min(30, wave * 2)): enemies.append([random.randint(0, WIDTH - 50), random.randint(-150, -50), random.uniform(-1.5, 1.5)])

        for e in enemies:
            e[1] += es
            e[0] += e[2]
            if e[0] <= 0 or e[0] >= WIDTH - 50:
                e[2] *= -1

        for b in bullets[:]:
            hit = False
            for e in enemies[:]:
                if e[0] < b[0] < e[0] + 50 and e[1] < b[1] < e[1] + 50:
                    enemies.remove(e); bullets.remove(b); score += 10; explosion_sound.play()
                    for _ in range(20): particles.append(Particle(e[0] + 25, e[1] + 25, (random.randint(200, 255), random.randint(100, 150), 50)))
                    hit = True; break
            if hit: continue
            
            if not hit and boss_on and bx < b[0] < bx + 200 and by < b[1] < by + 100:
                bullets.remove(b); boss_hp -= 5; explosion_sound.play()
                for _ in range(5): particles.append(Particle(b[0], b[1], (random.randint(200, 255), 50, 50)))
                if boss_hp <= 0:
                    boss_on = False; score += 100
                    for _ in range(100): particles.append(Particle(bx + 100, by + 50, (random.randint(200, 255), random.randint(100, 150), 50)))
                    for _ in range(3): powerups.append(PowerUp(bx + 100 + random.randint(-40, 40), by + 50 + random.randint(-40, 40), random.choice(["health", "weapon", "shield"])))

        if boss_on:
            bx += boss_speed_x
            if bx <= 0 or bx >= WIDTH - 200: boss_speed_x *= -1
            if random.random() < 0.03:
                angle = math.atan2((py + 30) - (by + 50), (px + 30) - (bx + 100))
                boss_bullets.append([bx + 100, by + 50, math.cos(angle), math.sin(angle)])
            if player_rect.colliderect(pygame.Rect(bx, by, 200, 100)) and not shield_active and invincibility_timer <= 0:
                lives -= 1; invincibility_timer = fps * 2; explosion_sound.play();
                if lives <= 0: game_over = True
        
        for e in enemies[:]:
            enemy_rect = pygame.Rect(e[0], e[1], 50, 50)
            if player_rect.colliderect(enemy_rect) and not shield_active and invincibility_timer <= 0:
                enemies.remove(e); lives -= 1; invincibility_timer = fps * 1.5; explosion_sound.play()
                if lives <= 0: game_over = True; break
            elif e[1] > HEIGHT:
                enemies.remove(e); lives -= 1; explosion_sound.play()
                if lives <= 0: game_over = True; break
        
        particles = [p for p in particles if p.update()]
        powerups = [p for p in powerups if p.update()]

        for p in powerups[:]:
            if player_rect.colliderect(p.get_rect()):
                powerups.remove(p); powerup_sound.play()
                if p.type == "health" and lives < 5: lives += 1
                elif p.type == "weapon" and bl < 5: bl += 1
                elif p.type == "shield": shield_active = True; shield_timer = 300

        for p in particles: p.draw(screen)
        for p in powerups: p.draw(screen)
        if boss_on:
            screen.blit(boss_img, (bx, by))
            bar_w = 200; health_w = max(0, int(bar_w * (boss_hp / (100 + wave * 20)))) if (100+wave*20)>0 else 0
            pygame.draw.rect(screen, RED, (bx, by - 20, bar_w, 10)); pygame.draw.rect(screen, GREEN, (bx, by - 20, health_w, 10)); pygame.draw.rect(screen, WHITE, (bx, by - 20, bar_w, 10), 2)

        if invincibility_timer > 0 and invincibility_timer % 10 < 5: pass
        else: screen.blit(player_img_rotated, player_rect)
        if shield_active:
            s_surf = pygame.Surface((player_rect.width + 20, player_rect.height + 20), pygame.SRCALPHA)
            pygame.draw.circle(s_surf, (50, 150, 255, min(255, int(shield_timer*0.8))), s_surf.get_rect().center, s_surf.get_width()//2)
            screen.blit(s_surf, (player_rect.left - 10, player_rect.top - 10))

        for b in bullets: pygame.draw.rect(screen, WHITE, (b[0], b[1], 5, 15))
        for b in boss_bullets: pygame.draw.circle(screen, RED, (int(b[0]), int(b[1])), 7)
        for e in enemies: screen.blit(enemy_imgs[enemy_anim_delay], (e[0], e[1]))

        screen.blit(font.render(f"{tr('score')}: {score}", True, WHITE), (10, 10))
        screen.blit(font.render(f"{tr('high_score')}: {high_score}", True, WHITE), (10, 40))
        for i in range(lives): pygame.draw.circle(screen, RED, (WIDTH - 40 - i * 30, 25), 12)
        wave_text = font.render(f"{tr('wave')}: {wave}", True, WHITE)
        screen.blit(wave_text, (WIDTH // 2 - wave_text.get_width()//2, 10))
        
        y_offset = HEIGHT - 80
        screen.blit(font.render(tr("upgrade_weapon"), True, WHITE if score >= 50 and bl < 5 else (100,100,100)), (10, y_offset))
        screen.blit(font.render(tr("extra_life"), True, WHITE if score >= 100 and lives < 5 else (100,100,100)), (10, y_offset + 30))
        screen.blit(font.render(tr("shield"), True, WHITE if score >= 150 and not shield_active else (100,100,100)), (10, y_offset + 60))
        
        pygame.display.update()
        clock.tick(fps)
    return "main_menu"

def main():
    if settings["music"]:
        try: pygame.mixer.music.play(-1)
        except: pass
        
    state = "story_intro"
    while True:
        if state == "story_intro":
            state = story_intro()
        elif state == "main_menu":
            state = main_menu()
        elif state == "settings":
            state = settings_menu()
        elif state == "playing":
            reset_game()
            state = game_loop()
        elif state == "quit":
            if video is not None: video.release()
            pygame.quit()
            sys.exit()

if __name__ == "__main__":
    main()