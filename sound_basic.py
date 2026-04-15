import pygame
import os
import sys

# ── ① 오디오 초기화 (노이즈 및 재생 속도 해결) ──────────────
try:
    # 8비트 음원은 주파수를 22050으로 설정할 때 가장 안정적으로 재생됩니다.
    pygame.mixer.pre_init(22050, -16, 2, 4096)
    pygame.init()
    pygame.mixer.init()
except Exception as e:
    print(f"믹서 초기화 오류: {e}")

screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("Quantum Slither Sound Test")
clock = pygame.time.Clock()

# ── ② 상대 경로 설정 ────────────────────────────────────────
# 실행 중인 .py 파일의 폴더 위치를 기준으로 파일을 찾습니다.
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

# 파일명 설정 (사용자가 제공한 파일명으로 교체)
#BGM_FILE = "653804__josefpres__8-bit-game-loop-004-only-organ-short-120-bpm.mp3"
# 효과음 파일이 있다면 아래 이름을 수정하세요. 현재는 BGM 파일을 효과음처럼 테스트하도록 설정했습니다.
EFFECT_FILE = "653804__josefpres__8-bit-game-loop-004-only-organ-short-120-bpm.mp3" 

BGM_PATH = os.path.join(BASE_PATH, BGM_FILE)
EFFECT_PATH = os.path.join(BASE_PATH, EFFECT_FILE)

# ── ③ 사운드 로드 및 재생 ────────────────────────────────────
try:
    # 배경음악 로드 (상대 경로)
    if os.path.exists(BGM_PATH):
        pygame.mixer.music.load(BGM_PATH)
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(loops=-1) # 무한 반복
    else:
        print(f"BGM 파일을 찾을 수 없습니다: {BGM_FILE}")

    # 효과음 로드 (상대 경로)
    if os.path.exists(EFFECT_PATH):
        click_sound = pygame.mixer.Sound(EFFECT_PATH)
        click_sound.set_volume(0.6)
    else:
        click_sound = None
        print(f"효과음 파일을 찾을 수 없습니다: {EFFECT_FILE}")

except Exception as e:
    print(f"사운드 로드 오류: {e}")

# ── ④ 메인 루프 ──────────────────────────────────────────────
running = True
while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # 마우스 클릭 시 효과음 재생
        if event.type == pygame.MOUSEBUTTONDOWN:
            if click_sound:
                click_sound.stop()  # 중복 재생 방지를 위해 정지 후 재생
                click_sound.play()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    screen.fill((40, 40, 60)) # 배경색 변경
    pygame.display.flip()

pygame.quit()