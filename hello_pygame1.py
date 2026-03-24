import pygame
import sys
import random

pygame.init()

# --- 설정 ---
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("커지는 원 피하기!")

WHITE = (255, 255, 255)
BLUE = (50, 50, 255)
RED = (255, 50, 50)
BLACK = (0, 0, 0)

clock = pygame.time.Clock()

# 플레이어 설정
p_x, p_y = WIDTH // 2, HEIGHT // 2
p_size = 20
p_speed = 7

# 적(원) 리스트
enemies = []
SPAWN_DELAY = 40  # 적 생성 간격
spawn_timer = 0

def spawn_enemy():
    # 처음엔 아주 작은 크기(r=5)에서 시작
    x = random.randint(50, WIDTH - 50)
    y = random.randint(50, HEIGHT - 50)
    grow_speed = random.uniform(0.5, 2.0) # 커지는 속도 랜덤
    max_r = random.randint(50, 100)      # 사라질 최대 크기 랜덤
    enemies.append({'x': x, 'y': y, 'r': 5, 'grow': grow_speed, 'max_r': max_r})

def get_triangle_points(cx, cy, size):
    return [(cx, cy - size), (cx + size, cy + size // 2), (cx - size, cy + size // 2)]

game_over = False
score = 0
start_ticks = pygame.time.get_ticks()

# --- 메인 루프 ---
while True:
    screen.fill(WHITE)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if game_over and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE: # 재시작
                game_over = False
                enemies = []
                p_x, p_y = WIDTH // 2, HEIGHT // 2
                start_ticks = pygame.time.get_ticks()

    if not game_over:
        # 1. 플레이어 이동
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:  p_x -= p_speed
        if keys[pygame.K_RIGHT]: p_x += p_speed
        if keys[pygame.K_UP]:    p_y -= p_speed
        if keys[pygame.K_DOWN]:  p_y += p_speed
        
        # 화면 제한
        p_x = max(p_size, min(p_x, WIDTH - p_size))
        p_y = max(p_size, min(p_y, HEIGHT - p_size))

        # 2. 적 생성
        spawn_timer += 1
        if spawn_timer > SPAWN_DELAY:
            spawn_enemy()
            spawn_timer = 0

        # 3. 적 업데이트 (커지기 & 충돌 검사)
        kept_enemies = []
        for e in enemies:
            e['r'] += e['grow']  # 반지름을 매 프레임 증가시킴
            
            # 충돌 계산
            dist = ((p_x - e['x'])**2 + (p_y - e['y'])**2)**0.5
            if dist < (e['r'] + p_size - 5): # 약간의 판정 자비
                game_over = True

            # 최대 크기에 도달하지 않은 원만 유지
            if e['r'] < e['max_r']:
                kept_enemies.append(e)
        enemies = kept_enemies
        
        score = (pygame.time.get_ticks() - start_ticks) // 1000

        # 4. 그리기
        for e in enemies:
            # 사라지기 직전에 깜빡이는 효과 (선택)
            if e['max_r'] - e['r'] < 15 and (int(e['r']) % 4 < 2):
                continue
            pygame.draw.circle(screen, RED, (int(e['x']), int(e['y'])), int(e['r']), 2) # 테두리만 그리기 (안이 보임)
            # pygame.draw.circle(screen, RED, (int(e['x']), int(e['y'])), int(e['r'])) # 꽉 찬 원

        pygame.draw.polygon(screen, BLUE, get_triangle_points(p_x, p_y, p_size))
        
        font = pygame.font.SysFont("malgungothic", 30)
        screen.blit(font.render(f"Time: {score}s", True, BLACK), (10, 10))

    else:
        font = pygame.font.SysFont("malgungothic", 50)
        msg = font.render("GAME OVER! Space to Restart", True, RED)
        screen.blit(msg, (WIDTH//2 - 250, HEIGHT//2 - 25))

    pygame.display.flip()
    clock.tick(60)