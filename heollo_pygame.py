import pygame
import sys
import math
from sprites import load_sprite

# 1. 초기화 및 설정
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Triple Collision: Circle, AABB, OBB")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 24)

# 색상 정의
BLUE = (50, 50, 255)   # Circle
RED = (255, 50, 50)    # AABB
GREEN = (50, 255, 50)  # OBB
WHITE = (255, 255, 255)
BG_COLOR = (30, 30, 30)

# 2. SAT(OBB) 충돌 함수들
def get_obb_vertices(center, size, angle):
    w, h = size[0] / 2, size[1] / 2
    rad = math.radians(-angle)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    vertices = []
    for px, py in [(-w, -h), (w, -h), (w, h), (-w, h)]:
        rx = px * cos_a - py * sin_a + center[0]
        ry = px * sin_a + py * cos_a + center[1]
        vertices.append(pygame.Vector2(rx, ry))
    return vertices

def check_sat_collision(v1, v2):
    def get_axes(v):
        axes = []
        for i in range(len(v)):
            edge = v[(i+1)%len(v)] - v[i]
            axes.append(pygame.Vector2(-edge.y, edge.x).normalize())
        return axes
    for axis in get_axes(v1) + get_axes(v2):
        dots1 = [v.dot(axis) for v in v1]
        dots2 = [v.dot(axis) for v in v2]
        if max(dots1) < min(dots2) or max(dots2) < min(dots1):
            return False
    return True

# 3. 스프라이트 준비
# "rocket" (플레이어 - OBB/AABB 비교용)
p_img_orig = load_sprite("rocket", (80, 200))
p_pos = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
p_angle = 0

# "stone" (고정 장애물 - Circle용)
s_img_orig = load_sprite("stone", (120, 120))
s_pos = pygame.Vector2(200, 200)
s_angle = 0

# 4. 메인 루프
while True:
    screen.fill(BG_COLOR)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # --- 조작 및 업데이트 ---
    keys = pygame.key.get_pressed()
    move_speed = 5
    rot_speed = 5 if keys[pygame.K_z] else 2
    
    p_angle += rot_speed
    if keys[pygame.K_LEFT]:  p_pos.x -= move_speed
    if keys[pygame.K_RIGHT]: p_pos.x += move_speed
    if keys[pygame.K_UP]:    p_pos.y -= move_speed
    if keys[pygame.K_DOWN]:  p_pos.y += move_speed
    
    s_angle += 0.5 # 장애물도 천천히 회전

    # --- 충돌 데이터 계산 ---
    # 1. OBB (정점 계산)
    p_verts = get_obb_vertices(p_pos, (80, 200), p_angle)
    s_verts = get_obb_vertices(s_pos, (120, 120), s_angle)
    hit_obb = check_sat_collision(p_verts, s_verts)

    # 2. AABB (회전된 이미지의 Rect 활용)
    p_img_rot = pygame.transform.rotate(p_img_orig, p_angle)
    s_img_rot = pygame.transform.rotate(s_img_orig, s_angle)
    p_aabb = p_img_rot.get_rect(center=p_pos)
    s_aabb = s_img_rot.get_rect(center=s_pos)
    hit_aabb = p_aabb.colliderect(s_aabb)

    # 3. Circle (중심 거리 계산)
    p_radius = 40  # 로켓 너비의 절반
    s_radius = 60  # 돌 너비의 절반
    dist = p_pos.distance_to(s_pos)
    hit_circle = dist < (p_radius + s_radius)

    # --- 그리기 ---
    # 이미지 출력
    screen.blit(p_img_rot, p_aabb)
    screen.blit(s_img_rot, s_aabb)

    # 시각화 박스 그리기
    pygame.draw.circle(screen, BLUE, p_pos, p_radius, 2)     # Circle
    pygame.draw.circle(screen, BLUE, s_pos, s_radius, 2)
    pygame.draw.rect(screen, RED, p_aabb, 2)                 # AABB
    pygame.draw.rect(screen, RED, s_aabb, 2)
    pygame.draw.polygon(screen, GREEN, p_verts, 3)           # OBB
    pygame.draw.polygon(screen, GREEN, s_verts, 3)

    # 결과 메시지 표시 (상단 중앙)
    y_off = 20
    for label, hit, color in [("Circle", hit_circle, BLUE), 
                             ("AABB", hit_aabb, RED), 
                             ("OBB", hit_obb, GREEN)]:
        text = font.render(f"{label}: {'HIT!' if hit else 'OK'}", True, color)
        screen.blit(text, (WIDTH//2 - 50, y_off))
        # 왼쪽 상단에도 고정 표시
        screen.blit(text, (20, y_off))
        y_off += 30

    pygame.display.flip()
    clock.tick(60)