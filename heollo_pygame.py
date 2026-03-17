import pygame
import sys
import random
import math

# 초기화
pygame.init()
WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("원 피하기 - 무한 재도전")

# 색상
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 50, 50)
BLACK = (0, 0, 0)

# 폰트 설정
font = pygame.font.SysFont("arial", 30)
large_font = pygame.font.SysFont("arial", 70)

# 전역 변수 초기화 함수 (재시작 시 사용)
def reset_game():
    global player_pos, obstacles, score, game_over
    player_pos = [WIDTH // 2, HEIGHT // 2]
    obstacles = []
    score = 0.0
    game_over = False

# 초기 실행 시 세팅
reset_game()
player_size = 15
speed = 6

SPAWN_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_EVENT, 600)

clock = pygame.time.Clock()
running = True

while running:
    screen.fill(WHITE)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # [수정] 게임 오버 상태에서 아무 키나 누르면 게임 리셋
        if game_over and event.type == pygame.KEYDOWN:
            reset_game()

        if not game_over and event.type == SPAWN_EVENT:
            new_x = random.randint(50, WIDTH - 50)
            new_y = random.randint(50, HEIGHT - 50)
            obstacles.append([new_x, new_y, 0])

    if not game_over:
        is_colliding = False
        
        # 1. 플레이어 이동
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_pos[0] > 0: player_pos[0] -= speed
        if keys[pygame.K_RIGHT] and player_pos[0] < WIDTH: player_pos[0] += speed
        if keys[pygame.K_UP] and player_pos[1] > 0: player_pos[1] -= speed
        if keys[pygame.K_DOWN] and player_pos[1] < HEIGHT: player_pos[1] += speed

        # 2. 장애물 업데이트 및 충돌 판정
        for obs in obstacles[:]:
            obs[2] += 2.0  
            dist = math.sqrt((obs[0] - player_pos[0])**2 + (obs[1] - player_pos[1])**2)
            
            if dist < obs[2]:
                is_colliding = True
                score -= 0.8
            
            if obs[2] > 130:
                obstacles.remove(obs)
                score += 1.0

        # 3. 점수 체크
        if score < 0:
            game_over = True

        # --- 그리기 로직 (게임 중) ---
        for obs in obstacles:
            pygame.draw.circle(screen, RED, (int(obs[0]), int(obs[1])), int(obs[2]), 2)

        player_color = RED if is_colliding else BLUE
        p1 = (player_pos[0], player_pos[1] - player_size)
        p2 = (player_pos[0] - player_size, player_pos[1] + player_size)
        p3 = (player_pos[0] + player_size, player_pos[1] + player_size)
        pygame.draw.polygon(screen, player_color, [p1, p2, p3])

    else:
        # --- 그리기 로직 (게임 오버 시) ---
        over_text = large_font.render("GAME OVER", True, RED)
        retry_text = font.render("Press Any Key to Restart", True, BLACK)
        
        screen.blit(over_text, (WIDTH//2 - over_text.get_width()//2, HEIGHT//2 - 50))
        screen.blit(retry_text, (WIDTH//2 - retry_text.get_width()//2, HEIGHT//2 + 40))

    # UI 표시
    score_display = max(0, int(score)) if not game_over else 0
    score_text = font.render(f"SCORE: {score_display}", True, BLACK)
    screen.blit(score_text, (20, 20))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()