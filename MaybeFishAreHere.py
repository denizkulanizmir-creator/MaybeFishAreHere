import pygame
import random
import sys
import datetime
import threading

pygame.init()
pygame.font.init()

try:
    import pyttsx3
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
TOP_PANEL_HEIGHT = 100
MAP_WIDTH = WINDOW_WIDTH
MAP_HEIGHT = WINDOW_HEIGHT - TOP_PANEL_HEIGHT

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("MaybeFishAreHere")

font_big = pygame.font.SysFont("Segoe UI", 18)
font_small = pygame.font.SysFont("Segoe UI", 14)
font_status = pygame.font.SysFont("Segoe UI", 16)

WHITE = (255, 255, 255)
PANEL_BG = (30, 41, 59)
PANEL_BORDER = (51, 65, 85)
BACKGROUND_DARK = (15, 23, 42)
WATER_DARK = (2, 132, 199)
WATER_GLOW = (56, 189, 248)
FISH_FILL = (254, 240, 138)
FISH_OUTLINE = (234, 179, 8)
FLOAT_WHITE = (255, 255, 255)
FLOAT_RED = (239, 68, 68)
STATUS_COLOR = (56, 189, 248)

wind_direction = 0
fishing_hour = 6
fishing_minute = 30
fish_schools = []
mouse_held = False
last_sound_time = 0
voice_engine = None

if VOICE_AVAILABLE:
    try:
        voice_engine = pyttsx3.init()
        voice_engine.setProperty('rate', 130)
        voice_engine.setProperty('volume', 1.0)
        voices = voice_engine.getProperty('voices')
        for v in voices:
            if 'tr' in v.id.lower() or 'turkish' in v.name.lower():
                voice_engine.setProperty('voice', v.id)
                break
    except Exception:
        voice_engine = None

def speak_async(text):
    if voice_engine is None:
        return
    def run():
        try:
            voice_engine.say(text)
            voice_engine.runAndWait()
        except Exception:
            pass
    threading.Thread(target=run, daemon=True).start()

def get_wind_label(direction):
    labels = [
        "Kuzey (Poyraz)",
        "Güney (Lodos)",
        "Doğu (Gündoğusu)",
        "Batı (Günbatısı)"
    ]
    return labels[direction % 4]

def place_fish_schools():
    global fish_schools
    fish_schools = []

    is_golden = (5 <= fishing_hour <= 8) or (18 <= fishing_hour <= 21)
    total_fish = 7 if is_golden else 3

    min_x, max_x = 0.10, 0.90
    min_y, max_y = 0.10, 0.90

    if wind_direction == 0:
        min_y, max_y = 0.55, 0.92
    elif wind_direction == 1:
        min_y, max_y = 0.08, 0.45
    elif wind_direction == 2:
        min_x, max_x = 0.08, 0.45
    elif wind_direction == 3:
        min_x, max_x = 0.55, 0.92

    for _ in range(total_fish):
        nx = random.uniform(min_x, max_x)
        ny = random.uniform(min_y, max_y)

        if not is_golden:
            nx = (nx + 0.5) / 2
            ny = (ny + 0.5) / 2

        x = nx * MAP_WIDTH
        y = TOP_PANEL_HEIGHT + ny * MAP_HEIGHT
        fish_schools.append([x, y])

def draw_fish(surface, x, y):
    pygame.draw.circle(surface, FISH_FILL, (int(x), int(y)), 18)
    pygame.draw.circle(surface, FISH_OUTLINE, (int(x), int(y)), 18, 2)

    pygame.draw.circle(surface, (30, 30, 30), (int(x - 6), int(y - 5)), 3)
    pygame.draw.circle(surface, (30, 30, 30), (int(x + 3), int(y - 5)), 3)

    tail_points = [
        (x + 18, y),
        (x + 28, y - 8),
        (x + 28, y + 8)
    ]
    pygame.draw.polygon(surface, FISH_OUTLINE, tail_points)

def draw_fishing_float(surface, x, y):
    pygame.draw.circle(surface, FLOAT_WHITE, (int(x), int(y)), 22)
    pygame.draw.circle(surface, FLOAT_RED, (int(x), int(y)), 22, 3)
    pygame.draw.circle(surface, FLOAT_RED, (int(x), int(y)), 12)

def check_proximity():
    for fx, fy in fish_schools:
        distance = ((fx - float_x) ** 2 + (fy - float_y) ** 2) ** 0.5
        if distance < 45:
            return True
    return False

place_fish_schools()
float_x = 600
float_y = TOP_PANEL_HEIGHT + 350

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mx, my = event.pos
                distance = ((mx - float_x) ** 2 + (my - float_y) ** 2) ** 0.5
                if distance < 30:
                    mouse_held = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                mouse_held = False

        elif event.type == pygame.MOUSEMOTION:
            if mouse_held:
                mx, my = event.pos
                float_x = max(22, min(MAP_WIDTH - 22, mx))
                float_y = max(TOP_PANEL_HEIGHT + 22, min(TOP_PANEL_HEIGHT + MAP_HEIGHT - 22, my))

        elif event.type == pygame.KEYDOWN:
            changed = False

            if event.key == pygame.K_UP:
                wind_direction = (wind_direction + 3) % 4
                changed = True
            elif event.key == pygame.K_DOWN:
                wind_direction = (wind_direction + 1) % 4
                changed = True
            elif event.key == pygame.K_LEFT:
                fishing_hour = (fishing_hour + 23) % 24
                changed = True
            elif event.key == pygame.K_RIGHT:
                fishing_hour = (fishing_hour + 1) % 24
                changed = True
            elif event.key == pygame.K_q:
                fishing_minute = (fishing_minute + 45) % 60
                changed = True
            elif event.key == pygame.K_e:
                fishing_minute = (fishing_minute + 15) % 60
                changed = True

            if changed:
                place_fish_schools()

    if check_proximity():
        now = pygame.time.get_ticks()
        if now - last_sound_time > 1500:
            last_sound_time = now
            speak_async("balık balık balık balık balık")

    screen.fill(BACKGROUND_DARK)

    pygame.draw.rect(screen, PANEL_BG, (0, 0, WINDOW_WIDTH, TOP_PANEL_HEIGHT))
    pygame.draw.rect(screen, PANEL_BORDER, (0, TOP_PANEL_HEIGHT - 3, WINDOW_WIDTH, 3))

    pygame.draw.rect(screen, WATER_DARK, (0, TOP_PANEL_HEIGHT, MAP_WIDTH, MAP_HEIGHT))

    glow_surface = pygame.Surface((600, 600), pygame.SRCALPHA)
    pygame.draw.circle(glow_surface, (56, 189, 248, 60), (300, 300), 300)
    screen.blit(glow_surface, (WINDOW_WIDTH // 2 - 300, TOP_PANEL_HEIGHT + MAP_HEIGHT // 2 - 300))

    wind_text = f"Rüzgarın Esiş Yönü: {get_wind_label(wind_direction)}   (Yukarı/Aşağı ile değiştir)"
    wind_surface = font_big.render(wind_text, True, WHITE)
    screen.blit(wind_surface, (20, 20))

    time_text = f"Av Saati: {fishing_hour:02d}:{fishing_minute:02d}   (Sol/Sağ: saat, Q/E: dakika)"
    time_surface = font_big.render(time_text, True, WHITE)
    screen.blit(time_surface, (20, 50))

    is_golden = (5 <= fishing_hour <= 8) or (18 <= fishing_hour <= 21)
    if is_golden:
        status_text = "Eşhor/Altın Saat! Balıklar kıyıda agresif besleniyor."
    else:
        status_text = "Öğlen/Gece durağanlığı. Balık az ve derinde."

    status_surface = font_status.render(status_text, True, STATUS_COLOR)
    screen.blit(status_surface, (700, 30))

    coast_north = font_small.render("KUZEY KIYISI", True, (255, 255, 255, 90))
    coast_south = font_small.render("GÜNEY KIYISI", True, (255, 255, 255, 90))
    coast_west = font_small.render("BATI KIYISI", True, (255, 255, 255, 90))
    coast_east = font_small.render("DOĞU KIYISI", True, (255, 255, 255, 90))

    screen.blit(coast_north, (560, TOP_PANEL_HEIGHT + 10))
    screen.blit(coast_south, (560, TOP_PANEL_HEIGHT + MAP_HEIGHT - 30))
    screen.blit(coast_west, (15, TOP_PANEL_HEIGHT + MAP_HEIGHT // 2))
    screen.blit(coast_east, (MAP_WIDTH - 110, TOP_PANEL_HEIGHT + MAP_HEIGHT // 2))

    for fx, fy in fish_schools:
        draw_fish(screen, fx, fy)

    draw_fishing_float(screen, float_x, float_y)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()