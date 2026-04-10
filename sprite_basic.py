import pygame

pygame.init()
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("Screen Wrap Example")
clock = pygame.time.Clock()

# 이미지 로드 및 설정
img_path = r"C:\Users\HOSEO\Desktop\v8yNjB16ijFF3ZhPgBhsBHfvcXIXvzz-C-Zi3d1UZM657ALY1seeeUrfhqS_qMEWGdS6WJbPDFtGa0KhvbKEsg (1).png"
img = pygame.image.load(img_path).convert_alpha()
img = pygame.transform.scale(img, (100, 100))

rect = img.get_rect()
rect.topleft = (0, 0)

running = True
while running:
    clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 1. 이동
    rect.x += 2
    rect.y += 2

    # 2. 화면 경계 체크 (Screen Wrapping)
    # 오른쪽 끝으로 완전히 사라지면 왼쪽 끝에서 나타남
    if rect.left > 400:
        rect.right = 0
    
    # 아래쪽 끝으로 완전히 사라지면 위쪽 끝에서 나타남
    if rect.top > 300:
        rect.bottom = 0

    # 3. 그리기
    screen.fill((30, 30, 40))
    screen.blit(img, rect)
    pygame.display.flip()

pygame.quit()