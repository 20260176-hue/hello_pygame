import pygame

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("Mouse Click Sound")
clock = pygame.time.Clock()

# ── ① 효과음 및 배경음악 로드 ──────────────────
shoot_sound = pygame.mixer.Sound(r"C:\Users\HOSEO\Desktop\viralaudio-descent-whoosh-long-cinematic-sound-effect-405921.mp3")
pygame.mixer.music.load(r"C:\Users\HOSEO\Desktop\alexgrohl-energetic-action-sport-500409bgm.gg")

# ── ② 볼륨 및 페이드인 설정 ────────────────────
shoot_sound.set_volume(0.5)
pygame.mixer.music.set_volume(0.6)
pygame.mixer.music.play(loops=-1, fade_ms=5000)

running = True
while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # ── ③ 마우스 클릭 감지 ────────────────────────
        if event.type == pygame.MOUSEBUTTONDOWN:
            # 마우스 왼쪽 버튼(1), 휠(2), 오른쪽 버튼(3) 중 아무거나 눌러도 재생
            # 특정 버튼만 지정하고 싶다면: if event.button == 1: (왼쪽 클릭)
            shoot_sound.stop()   # 기존 소리 중지
            shoot_sound.play()   # 처음부터 다시 재생

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    screen.fill((30, 30, 40))
    pygame.display.flip()

pygame.quit()