import pygame
import random
import sys
import base64
import io
import os

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  1. 설정 및 초기화
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
try:
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    pygame.mixer.set_num_channels(16)
except Exception as e:
    print(f"믹서 초기화 중 오류 발생: {e}")

WIDTH, HEIGHT = 1400, 1200
CELL = 20           
ITEM_SIZE = 35      
TARGET_FPS = 120 

WHITE, BLACK, GRAY = (255, 255, 255), (0, 0, 0), (30, 30, 30)
RED, GOLD, PURPLE, YELLOW = (255, 50, 50), (255, 215, 0), (200, 50, 255), (255, 255, 0)
WALL_COLOR = (120, 100, 100)
GHOST_OVERLAY = (150, 200, 255, 120)

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF | pygame.HWSURFACE)
pygame.display.set_caption("Quantum Slither: Enhanced UI")
clock = pygame.time.Clock()

# 폰트 설정 개선
font_ui = pygame.font.SysFont("arial", 30, bold=True)
font_big = pygame.font.SysFont("arial", 70, bold=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  2. 사운드 자산 로드
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BGM_FILENAME = "653804__josefpres__8-bit-game-loop-004-only-organ-short-120-bpm.wav"
EAT_SOUND_FILENAME = "Video Project.wav"
eat_sound = None

def load_assets():
    global eat_sound
    current_dir = os.path.dirname(os.path.abspath(__file__))
    bgm_path = os.path.join(current_dir, BGM_FILENAME)
    if os.path.exists(bgm_path):
        try:
            pygame.mixer.music.load(bgm_path)
            pygame.mixer.music.set_volume(0.4)
            pygame.mixer.music.play(-1)
        except: pass
    eat_path = os.path.join(current_dir, EAT_SOUND_FILENAME)
    if os.path.exists(eat_path):
        try:
            eat_sound = pygame.mixer.Sound(eat_path)
            eat_sound.set_volume(0.8)
        except: pass

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  3. 스프라이트 추출
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SHEET_B64 = "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"

def load_all_sprites(b64_data):
    if not b64_data: return None
    try:
        sheet_bytes = base64.b64decode(b64_data)
        sheet = pygame.image.load(io.BytesIO(sheet_bytes)).convert()
        sheet.set_colorkey(BLACK)
        sprites = {}
        
        def extract_and_scale(rect, scale_size):
            sub = sheet.subsurface(rect)
            return pygame.transform.scale(sub, scale_size)

        fw1, fh1, cols1 = 21, 14, 7
        r1, c1 = divmod(68, cols1)
        sprites['NORMAL'] = extract_and_scale(pygame.Rect(c1 * fw1, r1 * fh1, fw1, fh1), (ITEM_SIZE, ITEM_SIZE))
        
        fw2, fh2, cols2 = 24, 17, 6
        r2, c2 = divmod(21, cols2)
        sprites['NANO'] = extract_and_scale(pygame.Rect(c2 * fw2, r2 * fh2, fw2, fh2), (ITEM_SIZE, ITEM_SIZE))
        
        fw3, fh3, cols3 = 8, 17, 20
        r3, c3 = divmod(65, cols3)
        sprites['GHOST'] = extract_and_scale(pygame.Rect(c3 * fw3, r3 * fh3, fw3, fh3), (ITEM_SIZE, ITEM_SIZE))
        
        fw_t, fh_t, cols_t = 8, 12, 20
        rt, ct = divmod(64, cols_t)
        sprites['THUNDER'] = extract_and_scale(pygame.Rect(ct * fw_t, rt * fh_t, fw_t, fh_t), (ITEM_SIZE, ITEM_SIZE))

        fw4, fh4, cols4 = 13, 14, 12
        def get_snake_part(idx):
            r, c = divmod(idx, cols4)
            return extract_and_scale(pygame.Rect(c * fw4, r * fh4, fw4, fh4), (CELL, CELL))
        sprites['HEAD'] = get_snake_part(79)
        sprites['BODY'] = get_snake_part(78)
        return sprites
    except Exception as e:
        print(f"이미지 로드 실패: {e}")
        return None

SPRITES = load_all_sprites(SHEET_B64)
if not SPRITES:
    SPRITES = {k: pygame.Surface((ITEM_SIZE, ITEM_SIZE)) for k in ['NORMAL', 'NANO', 'GHOST', 'THUNDER']}
    SPRITES.update({k: pygame.Surface((CELL, CELL)) for k in ['HEAD', 'BODY']})
    for k, c in zip(SPRITES.keys(), [RED, GOLD, PURPLE, YELLOW, (0, 255, 0), (0, 200, 0)]): SPRITES[k].fill(c)

head_angles, body_angles = {}, {}
def pre_rotate_sprites():
    angles = {(CELL, 0): 0, (-CELL, 0): 180, (0, -CELL): 90, (0, CELL): 270}
    for dir_tuple, angle in angles.items():
        h_rot = pygame.transform.rotate(SPRITES['HEAD'], angle)
        b_rot = pygame.transform.rotate(SPRITES['BODY'], angle)
        h_rot.set_colorkey(BLACK); b_rot.set_colorkey(BLACK)
        head_angles[dir_tuple], body_angles[dir_tuple] = h_rot, b_rot

load_assets()
pre_rotate_sprites()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  4. 보조 함수들
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def create_stars(count):
    return [{'pos': [random.randint(0, WIDTH), random.randint(0, HEIGHT)], 
             'size': random.randint(1, 3),
             'color': random.choice([(100, 100, 100), (150, 150, 150), (200, 200, 200)])} 
            for _ in range(count)]

stars_far = create_stars(120)
stars_mid = create_stars(80)

def get_hardcore_pos(snake_coords, exclude_list, head_coords, score):
    hx, hy = head_coords
    spawn_range = max(10, 40 - (score // 50))
    for _ in range(50):
        rx, ry = random.randint(-spawn_range, spawn_range) * CELL, random.randint(-spawn_range, spawn_range) * CELL
        pos = (hx + rx, hy + ry)
        if pos not in snake_coords and pos not in exclude_list:
            if abs(rx) > CELL*3 or abs(ry) > CELL*3: return pos
    return None

def spawn_hardcore_walls(snake_coords, walls, items_pos, head_coords, score):
    start_pos = get_hardcore_pos(snake_coords, walls + items_pos, head_coords, score)
    if not start_pos: return []
    cluster, curr = [start_pos], start_pos
    for _ in range(random.randint(3, 8)):
        d = random.choice([(0, CELL), (0, -CELL), (CELL, 0), (-CELL, 0)])
        nxt = (curr[0] + d[0], curr[1] + d[1])
        if nxt not in snake_coords and nxt not in walls: cluster.append(nxt); curr = nxt
    return cluster

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  5. 게임 오버 화면 (R: 재시작, Q: 종료)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def show_game_over(score):
    pygame.mixer.music.stop()
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((20, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    
    txt_gameover = font_big.render("GAME OVER", True, RED)
    txt_score = font_ui.render(f"FINAL SCORE: {score}", True, GOLD)
    txt_retry = font_ui.render("Press 'R' to Restart or 'Q' to Quit", True, WHITE)
    
    screen.blit(txt_gameover, (WIDTH//2 - txt_gameover.get_width()//2, HEIGHT//2 - 100))
    screen.blit(txt_score, (WIDTH//2 - txt_score.get_width()//2, HEIGHT//2))
    screen.blit(txt_retry, (WIDTH//2 - txt_retry.get_width()//2, HEIGHT//2 + 80))
    
    pygame.display.flip()
    
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r: 
                    try: pygame.mixer.music.play(-1)
                    except: pass
                    return True
                if e.key == pygame.K_q: pygame.quit(); sys.exit()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  6. 메인 게임 루프
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def main():
    snake = [(0, 0, CELL, 0), (-CELL, 0, CELL, 0), (-CELL*2, 0, CELL, 0)]
    direction, next_dir = (CELL, 0), (CELL, 0)
    items, walls, score, move_acc = [], [], 0, 0.0
    base_delay, ghost_timer, thunder_timer = 90, 0, 0

    while True:
        dt = clock.tick(TARGET_FPS)
        now = pygame.time.get_ticks()
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP and direction != (0, CELL): next_dir = (0, -CELL)
                elif e.key == pygame.K_DOWN and direction != (0, -CELL): next_dir = (0, CELL)
                elif e.key == pygame.K_LEFT and direction != (CELL, 0): next_dir = (-CELL, 0)
                elif e.key == pygame.K_RIGHT and direction != (-CELL, 0): next_dir = (CELL, 0)

        is_ghost, is_thunder = now < ghost_timer, now < thunder_timer
        delay = base_delay * 0.6 if is_thunder else base_delay
        move_acc += dt
        
        if move_acc >= delay:
            move_acc -= delay
            direction = next_dir
            hx, hy = snake[0][0] + direction[0], snake[0][1] + direction[1]
            head_coords, s_coords = (hx, hy), [(s[0], s[1]) for s in snake]
            
            if not is_ghost and (head_coords in walls or head_coords in s_coords): return score
            
            snake.insert(0, (hx, hy, direction[0], direction[1]))
            ate = False
            for it in items[:]:
                if abs(hx - it['pos'][0]) < CELL and abs(hy - it['pos'][1]) < CELL:
                    ate, score = True, score + (20 if is_thunder else 10)
                    if eat_sound: eat_sound.play()
                    if it['type'] == 'NANO': snake = snake[:max(3, len(snake)//2)]
                    elif it['type'] == 'GHOST': ghost_timer = now + 5000
                    elif it['type'] == 'THUNDER': thunder_timer = now + 5000
                    items.remove(it)
            if not ate: snake.pop()
            
            items = [i for i in items if abs(i['pos'][0]-hx) < 1500 and abs(i['pos'][1]-hy) < 1500]
            walls = [w for w in walls if abs(w[0]-hx) < 2000 and abs(w[1]-hy) < 2000]
            while len(items) < 8:
                p = get_hardcore_pos(s_coords, [i['pos'] for i in items] + walls, (hx, hy), score)
                if p: items.append({'pos': p, 'type': random.choice(["NORMAL"]*5 + ["GHOST", "THUNDER", "NANO"])})
            if len(walls) < min(600, 40 + (score // 2)):
                walls.extend(spawn_hardcore_walls(s_coords, walls, [i['pos'] for i in items], (hx, hy), score))

        cam_x, cam_y = WIDTH//2 - snake[0][0], HEIGHT//2 - snake[0][1]
        screen.fill(GRAY)

        # 배경 렌더링
        for s in stars_far:
            sx, sy = (s['pos'][0] + cam_x * 0.2) % WIDTH, (s['pos'][1] + cam_y * 0.2) % HEIGHT
            pygame.draw.circle(screen, s['color'], (int(sx), int(sy)), s['size'])
        for s in stars_mid:
            sx, sy = (s['pos'][0] + cam_x * 0.4) % WIDTH, (s['pos'][1] + cam_y * 0.4) % HEIGHT
            pygame.draw.circle(screen, s['color'], (int(sx), int(sy)), s['size'])

        # 게임 월드 오브젝트
        for w in walls: pygame.draw.rect(screen, WALL_COLOR, (w[0]+cam_x, w[1]+cam_y, CELL, CELL))
        offset = (ITEM_SIZE - CELL) // 2
        for it in items: 
            screen.blit(SPRITES[it['type']], (it['pos'][0]+cam_x-offset, it['pos'][1]+cam_y-offset))
        for i, (sx, sy, sdx, sdy) in enumerate(snake):
            img = head_angles.get((sdx, sdy), SPRITES['HEAD']) if i == 0 else body_angles.get((sdx, sdy), SPRITES['BODY'])
            screen.blit(img, (sx+cam_x, sy+cam_y))
            if is_ghost:
                g = pygame.Surface((CELL, CELL), pygame.SRCALPHA); g.fill(GHOST_OVERLAY)
                screen.blit(g, (sx+cam_x, sy+cam_y))

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        #  실시간 점수판 (In-Game UI)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 1. 점수판 배경 상자 (반투명 블랙)
        score_bg = pygame.Surface((220, 60), pygame.SRCALPHA)
        score_bg.fill((0, 0, 0, 150))
        screen.blit(score_bg, (15, 15))
        
        # 2. 테두리
        pygame.draw.rect(screen, GOLD, (15, 15, 220, 60), 2)
        
        # 3. 점수 텍스트
        score_surf = font_ui.render(f"SCORE: {score}", True, WHITE)
        screen.blit(score_surf, (30, 25))

        pygame.display.flip()

if __name__ == "__main__":
    while True:
        final_score = main()
        if not show_game_over(final_score): 
            break