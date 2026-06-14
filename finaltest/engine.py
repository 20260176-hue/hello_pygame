import pygame
import sys
import random
import math
import os

# --- 1. 글로벌 및 카메라 설정 ---
SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080  
VIRTUAL_WIDTH, VIRTUAL_HEIGHT = 960, 540  

GRID_SIZE = 40  
COLS, ROWS = 45, 35  

BG_COLOR = (15, 15, 20)      
GRID_COLOR = (30, 30, 35)
WALL_COLOR = (60, 60, 65)     
ENEMY_IDLE_COLOR = (220, 60, 60)   
ENEMY_CHASE_COLOR = (255, 120, 60) 

ENEMY_BURN_COLOR = (255, 100, 50)
ENEMY_SLOW_COLOR = (100, 180, 255)
ENEMY_SHOCK_COLOR = (130, 210, 255) 

FLOOR_DEFAULT = (35, 35, 40)   
FLOOR_TREASURE = (45, 40, 25)  
FLOOR_SHOP = (25, 35, 45)      
FLOOR_START = (30, 45, 35)     

STAIRS_COLOR = (160, 50, 250)
TEXT_COLOR = (255, 255, 255)
TITLE_COLOR = (255, 215, 0)

WEAPON_DATA = {
    "PUNCH": {"name": "기사의 검", "atk": 4, "range": 1, "type": "MELEE", "color": (255, 215, 0)}
}

# ⭐️ [EXE 빌드 경로 완치] PyInstaller 임시 압축 해제 폴더(_MEIPASS) 우선 참조 연산 주입
if hasattr(sys, '_MEIPASS'):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 기존 에셋 서브디렉토리 리스트는 그대로 유지합니다.
ASSET_SUBDIRS = [
    "boss", "artifact", "player", "chest", "map", "monster", "without_outline",
    "Free Effect Bullet Impact Explosion 32x32"
]

ASSET_CACHE_MAP = {}
ASSET_STORE = {} 

def build_asset_cache():
    global ASSET_CACHE_MAP
    ASSET_CACHE_MAP.clear()
    for subdir in ASSET_SUBDIRS:
        sub_dir_path = os.path.join(BASE_DIR, subdir)
        if os.path.exists(sub_dir_path) and os.path.isdir(sub_dir_path):
            for f in os.listdir(sub_dir_path):
                ASSET_CACHE_MAP[f.lower()] = os.path.join(sub_dir_path, f)
    for f in os.listdir(BASE_DIR):
        if os.path.isfile(os.path.join(BASE_DIR, f)) and f.lower() not in ASSET_CACHE_MAP:
            ASSET_CACHE_MAP[f.lower()] = os.path.join(BASE_DIR, f)

def find_asset_path(filename):
    fn_lower = filename.lower()
    if fn_lower in ASSET_CACHE_MAP: return ASSET_CACHE_MAP[fn_lower]
    keyword = fn_lower.split(".")[0][:4] 
    for cached_fn, cached_path in ASSET_CACHE_MAP.items():
        if keyword in cached_fn: return cached_path
    return None

# ★ [보스 크기 강제 고정 사양 정밀 디코더 완치]
class FixedFrameDecoder:
    def __init__(self, filename, total_frames, is_attack=False, is_death=False, is_effect=False, dummy_color=(200, 50, 50)):
        target = find_asset_path(filename)
        self.frames = []
        
        is_boss_file = "boss" in filename.lower()
        
        if target and os.path.exists(target):
            try: 
                self.sheet = pygame.image.load(target).convert_alpha()
                self.sheet.set_colorkey((0, 0, 0))
                sheet_w, sheet_h = self.sheet.get_width(), self.sheet.get_height()
                cell_w = sheet_w // total_frames 
                
                for i in range(total_frames):
                    sub_rect = pygame.Rect(i * cell_w, 0, cell_w, sheet_h)
                    cell_surf = self.sheet.subsurface(sub_rect)
                    
                    if is_boss_file:
                        # ★ [크기 널뛰기 버그 원천 진압] 가로/세로를 억지로 맞추지 않고, 원본 비율을 완벽히 보존한 채 세로 기준 3.5칸 크기(GRID_SIZE * 3.5)로 비례 스케일링합니다!
                        target_h = int(GRID_SIZE * 3.5)
                        aspect_ratio = cell_w / sheet_h
                        target_w = int(target_h * aspect_ratio)
                        
                        # 상단 공백으로 인해 도트가 작아지는 현상을 방지하기 위해 상하좌우 빈 여백 자동 트리밍 연산 가동
                        sub_rect_bound = cell_surf.get_bounding_rect()
                        if sub_rect_bound.width > 0 and sub_rect_bound.height > 0:
                            trimmed_surf = cell_surf.subsurface(sub_rect_bound)
                            # 트리밍된 순수 도트만 타일 크기에 맞게 업스케일
                            aspect_ratio = sub_rect_bound.width / sub_rect_bound.height
                            target_w = int(target_h * aspect_ratio)
                            final_frame = pygame.transform.scale(trimmed_surf, (target_w, target_h))
                        else:
                            final_frame = pygame.transform.scale(cell_surf, (target_w, target_h))
                    else:
                        scale = int(GRID_SIZE * 2.2) if is_effect else int(GRID_SIZE * 1.5)
                        final_frame = pygame.transform.scale(cell_surf, (scale, scale))
                        
                    self.frames.append(final_frame)
                return
            except Exception as e: print(f"⚠️ 파일 파싱 오류 백업 가동 ({filename}): {e}")
            
        # 백업용 수치 세팅
        scale = int(GRID_SIZE * 3.5) if is_boss_file else (int(GRID_SIZE * 2.2) if is_effect else int(GRID_SIZE * 1.5))
        for i in range(total_frames):
            dummy_surf = pygame.Surface((scale, scale), pygame.SRCALPHA)
            progress_ratio = (i + 1) / total_frames
            radius = int((scale // 2) * (progress_ratio if is_effect or is_death else 1.0))
            alpha = int(255 * (1.0 - progress_ratio if is_death else 1.0))
            pygame.draw.circle(dummy_surf, list(dummy_color) + [alpha], (scale//2, scale//2), max(4, radius))
            self.frames.append(dummy_surf)

def get_cached_frames(filename, total_frames, is_attack=False, is_death=False, is_effect=False, dummy_color=(200, 50, 50)):
    cache_key = f"{filename.lower()}_{total_frames}_{is_effect}"
    if cache_key not in ASSET_STORE:
        decoder = FixedFrameDecoder(filename, total_frames, is_attack, is_death, is_effect, dummy_color)
        ASSET_STORE[cache_key] = decoder.frames
    return ASSET_STORE[cache_key]

class Camera:
    def __init__(self):
        self.x, self.y = 0, 0
        self.shake_timer = self.shake_intensity = self.shake_offset_x = self.shake_offset_y = 0

    def start_shake(self, duration, intensity):
        self.shake_timer = duration; self.shake_intensity = intensity

    def update_shake(self):
        if self.shake_timer > 0:
            self.shake_timer -= 1
            self.shake_offset_x = random.randint(-self.shake_intensity, self.shake_intensity)
            self.shake_offset_y = random.randint(-self.shake_intensity, self.shake_intensity)
        else: self.shake_offset_x = self.shake_offset_y = 0

    def target_on(self, player):
        p_center_x = player.visual_c * GRID_SIZE + GRID_SIZE // 2
        p_center_y = player.visual_r * GRID_SIZE + GRID_SIZE // 2
        self.x = max(0, min(p_center_x - VIRTUAL_WIDTH // 2, COLS * GRID_SIZE - VIRTUAL_WIDTH))
        self.y = max(0, min(p_center_y - VIRTUAL_HEIGHT // 2, ROWS * GRID_SIZE - VIRTUAL_HEIGHT))

    def apply(self, rect): return rect.move(-int(self.x) + self.shake_offset_x, -int(self.y) + self.shake_offset_y)
    def apply_pos(self, pos): return (pos[0] - int(self.x) + self.shake_offset_x, pos[1] - int(self.y) + self.shake_offset_y)
    def to_world_pos(self, pos): return (pos[0] * VIRTUAL_WIDTH // SCREEN_WIDTH + self.x, pos[1] * VIRTUAL_HEIGHT // SCREEN_HEIGHT + self.y)

class Entity:
    def __init__(self, r, c, color): self.r, self.c, self.color = r, c, color
    def draw(self, surface, camera): pygame.draw.rect(surface, self.color, camera.apply(pygame.Rect(self.c * GRID_SIZE + 4, self.r * GRID_SIZE + 4, GRID_SIZE - 8, GRID_SIZE - 8)))
    
# === engine.py 파일 맨 아래에 추가할 코드 ===

class VisualEffect:
    def __init__(self, r, c, frames):
        self.r = r
        self.c = c
        self.frames = frames
        self.anim_frame = 0
        self.tick_accumulator = 0
        self.is_finished = False

    def update(self):
        self.tick_accumulator += 1
        if self.tick_accumulator >= 4:  # 애니메이션 속도 제어
            self.tick_accumulator = 0
            self.anim_frame += 1
            if self.frames and self.anim_frame >= len(self.frames):
                self.is_finished = True

    def draw(self, surface, camera):
        if self.is_finished or not self.frames: 
            return
        
        # 타일 위치에 맞춰 사각형 영역 계산
        rect = pygame.Rect(self.c * GRID_SIZE, self.r * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        screen_rect = camera.apply(rect)
        
        # 프레임 범위를 벗어나지 않도록 최댓값 제한 안전장치
        current_frame = self.frames[min(self.anim_frame, len(self.frames) - 1)]
        
        # 이펙트가 타일 중앙에 오도록 오프셋 정렬 렌더링
        img_w, img_h = current_frame.get_width(), current_frame.get_height()
        render_pos = (screen_rect.x - (img_w - GRID_SIZE) // 2, screen_rect.y - (img_h - GRID_SIZE) // 2)
        
        surface.blit(current_frame, render_pos)