import pygame
import sys
import random
import math
import os
from engine import *
# ⭐️ [강제 안착] 만약 * 로 안 불러와졌을 경우를 대비해 확실하게 직접 지정하여 불러옵니다.
from engine import VisualEffect

# ★ [참조 스코프 완치] engine 모듈의 VisualEffect 클래스를 전역 공간에 확실하게 안착시킵니다.
try:
    from engine import VisualEffect
except ImportError:
    # 만약 engine 모듈에서 VisualEffect를 찾을 수 없다면 백업용 클래스 작동
    class VisualEffect:
        def __init__(self, r, c, frames):
            self.r = r
            self.c = c
            self.frames = frames
            self.anim_frame = 0
            self.tick = 0
            self.is_finished = False
        def update(self):
            self.tick += 1
            if self.tick >= 4:
                self.tick = 0
                self.anim_frame += 1
                if self.frames and self.anim_frame >= len(self.frames):
                    self.is_finished = True
        def draw(self, surface, camera):
            if self.is_finished or not self.frames: return
            rect = pygame.Rect(self.c * GRID_SIZE, self.r * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            screen_rect = camera.apply(rect)
            surface.blit(self.frames[min(self.anim_frame, len(self.frames)-1)], screen_rect)

# 여기서부터 기존 Stairs 클래스가 시작됩니다.
class Stairs(Entity):
    def __init__(self, r, c):
        super().__init__(r, c, (160, 50, 250))
        self.anim_frame = 0
        self.fps_tick_accumulator = 0
        self.portal_frames = []
        
        target_path = find_asset_path("portal.jpg")
        if target_path and os.path.exists(target_path):
            try:
                sheet = pygame.image.load(target_path).convert_alpha()
                sheet_w, sheet_h = sheet.get_width(), sheet.get_height()
                cell_w = sheet_w // 6
                
                for i in range(6):
                    sub_rect = pygame.Rect(i * cell_w, 0, cell_w, sheet_h)
                    cell_surf = sheet.subsurface(sub_rect)
                    final_frame = pygame.transform.scale(cell_surf, (int(GRID_SIZE * 1.8), int(GRID_SIZE * 1.8)))
                    self.portal_frames.append(final_frame)
            except Exception as e:
                print(f"⚠️ 포탈 시트 디코딩 오류 백업 가동: {e}")
                
    def update_animation(self):
        self.fps_tick_accumulator += 1
        if self.fps_tick_accumulator >= 5:
            self.fps_tick_accumulator = 0
            if self.portal_frames:
                self.anim_frame = (self.anim_frame + 1) % len(self.portal_frames)
                
    def draw(self, surface, camera):
        rect = pygame.Rect(self.c * GRID_SIZE, self.r * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        screen_rect = camera.apply(rect)
        if self.portal_frames:
            # 삐져나가지 않고 타일 정중앙에 오도록 X, Y 축 오프셋 마이너스 정렬
            surface.blit(self.portal_frames[self.anim_frame], (screen_rect.x - 16, screen_rect.y - 16))
        else:
            center_x = screen_rect.x + GRID_SIZE // 2
            center_y = screen_rect.y + GRID_SIZE // 2
            pygame.draw.circle(surface, (50, 200, 100), (center_x, center_y), GRID_SIZE // 2)
            pygame.draw.circle(surface, (200, 255, 200), (center_x, center_y), GRID_SIZE // 3, 2)

class GameMap:
    def __init__(self):
        self.grid = [[1 for _ in range(COLS)] for _ in range(ROWS)]
        self.room_types = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.start_pos = (0, 0)
        self.battle_rooms_rects = []
        self.tile_img = None
        
        target_floor_file = find_asset_path("floor1.jpg")
        if not target_floor_file: target_floor_file = find_asset_path("Tilemap_color1.png")
            
        if target_floor_file and os.path.exists(target_floor_file):
            try:
                raw_tile = pygame.image.load(target_floor_file).convert_alpha()
                pure_grass_surf = raw_tile.subsurface(pygame.Rect(58, 52, raw_tile.get_width() - 114, raw_tile.get_height() - 110))
                self.tile_img = pygame.transform.scale(pure_grass_surf, (GRID_SIZE + 2, GRID_SIZE + 2))
                self.tile_img.set_colorkey((0, 0, 0))
                darken_filter = pygame.Surface((GRID_SIZE + 2, GRID_SIZE + 2), pygame.SRCALPHA); darken_filter.fill((160, 160, 160, 255))
                self.tile_img.blit(darken_filter, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            except Exception as e: print(f"⚠️ 바닥 로드 오류: {e}")

        self.long_wall_img = self.short_wall_img = self.vertical_wall_img = None
        long_wall_path = find_asset_path("long wall.jpg")
        if long_wall_path:
            try:
                w_tile = pygame.image.load(long_wall_path).convert_alpha()
                core_wall = w_tile.subsurface(pygame.Rect(207, 116, 190, 124))
                self.long_wall_img = pygame.transform.scale(core_wall, (GRID_SIZE + 2, GRID_SIZE + 2))
                self.long_wall_img.set_colorkey((0, 0, 0))
            except Exception as e: print(f"⚠️ 가로 긴 벽 로드 오류: {e}")
            
        short_wall_path = find_asset_path("short wall.jpg")
        if short_wall_path:
            try:
                sw = pygame.image.load(short_wall_path).convert_alpha()
                core_swall = sw.subsurface(pygame.Rect(260, 125, 64, 124))
                self.short_wall_img = pygame.transform.scale(core_swall, (GRID_SIZE + 2, GRID_SIZE + 2))
                self.short_wall_img.set_colorkey((0, 0, 0))
            except Exception as e: print(f"⚠️ 모서리 짧은 벽 로드 오류: {e}")

        vertical_wall_path = find_asset_path("vertical_wall.jpg")
        if vertical_wall_path:
            try:
                vw = pygame.image.load(vertical_wall_path).convert_alpha()
                core_vwall = vw.subsurface(pygame.Rect(257, 85, 64, 212))
                self.vertical_wall_img = pygame.transform.scale(core_vwall, (GRID_SIZE + 2, GRID_SIZE + 2))
                self.vertical_wall_img.set_colorkey((0, 0, 0))
            except Exception as e: print(f"⚠️ 세로 벽 로드 오류: {e}")

        self.generate_structured_map()

    def generate_structured_map(self):
        self.grid = [[1 for _ in range(COLS)] for _ in range(ROWS)]
        self.room_types = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.battle_rooms_rects = []
        sector_w, sector_h = COLS // 3, ROWS // 3
        room_w, room_h = 11, 8
        role_pool = ["TREASURE", "SHOP"] + ["BATTLE"] * random.randint(3, 5)
        random.shuffle(role_pool)
        final_roles = ["START"] + role_pool
        rooms_centers, role_idx = [], 0
        
        for s_r in range(3):
            for s_c in range(3):
                if role_idx >= len(final_roles): break
                start_x, start_y = s_c * sector_w + (sector_w - room_w) // 2, s_r * sector_h + (sector_h - room_h) // 2
                for r in range(start_y, start_y + room_h):
                    for c in range(start_x, start_x + room_w): self.grid[r][c] = 0
                curr_rect, role = pygame.Rect(start_x, start_y, room_w, room_h), final_roles[role_idx]
                if role == "START":
                    for r in range(start_y, start_y + room_h):
                        for c in range(start_x, start_x + room_w): self.room_types[r][c] = 3
                    self.start_pos = (start_y + room_h // 2, start_x + room_w // 2); self.start_room_rect = curr_rect
                elif role == "TREASURE":
                    for r in range(start_y, start_y + room_h):
                        for c in range(start_x, start_x + room_w): self.room_types[r][c] = 1
                    self.treasure_room_rect = curr_rect
                elif role == "SHOP":
                    for r in range(start_y, start_y + room_h):
                        for c in range(start_x, start_x + room_w): self.room_types[r][c] = 2
                    self.shop_room_rect = curr_rect
                elif role == "BATTLE": self.battle_rooms_rects.append(curr_rect)
                rooms_centers.append((start_x + room_w // 2, start_y + room_h // 2)); role_idx += 1
        for i in range(len(rooms_centers) - 1):
            x1, y1 = rooms_centers[i]; x2, y2 = rooms_centers[i+1]
            for c in range(min(x1, x2), max(x1, x2) + 1): self.grid[y1][c] = self.grid[y1+1][c] = 0
            for r in range(min(y1, y2), max(y1, y2) + 1): self.grid[r][x2] = self.grid[r][x2+1] = 0

    def generate_test_room_grid(self, p_r, p_c):
        self.grid = [[1 for _ in range(COLS)] for _ in range(ROWS)]
        self.room_types = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.battle_rooms_rects = []
        for r in range(p_r - 4, p_r + 5):
            for c in range(p_c - 4, p_c + 5):
                if 0 <= r < ROWS and 0 <= c < COLS: self.grid[r][c] = 0; self.room_types[r][c] = 0

    def get_room_random_pos(self, rect): return random.randint(rect.y + 1, rect.y + rect.height - 2), random.randint(rect.x + 1, rect.x + rect.width - 2)

    def is_walkable(self, r, c, active_items_list=None, enemies=None, player=None, merchant=None): 
        if not (0 <= r < ROWS and 0 <= c < COLS): return False
        if self.grid[r][c] != 0: return False 
        if active_items_list:
            for item in active_items_list:
                if item.item_type == "CHEST" and item.r == r and item.c == c:
                    if item.chest_state in ["IDLE", "OPENING"]: return False
        if enemies:
            for enemy in enemies:
                if enemy.enemy_state != "DEATH" and enemy.r == r and enemy.c == c: return False
        if player and player.r == r and player.c == c: return False
        if merchant and merchant.r == r and merchant.c == c: return False
        return True

    def get_room_at(self, r, c):
        for room in [self.start_room_rect, self.treasure_room_rect, self.shop_room_rect] + self.battle_rooms_rects:
            if room and room.x <= c < room.x + room.width and room.y <= r < room.y + room.height: return room
        return None

    def draw(self, surface, camera):
        for r in range(ROWS):
            for c in range(COLS):
                rect = pygame.Rect(c * GRID_SIZE - 1, r * GRID_SIZE - 1, GRID_SIZE + 2, GRID_SIZE + 2)
                screen_rect = camera.apply(rect)
                if -GRID_SIZE <= screen_rect.x <= VIRTUAL_WIDTH and -GRID_SIZE <= screen_rect.y <= VIRTUAL_HEIGHT:
                    if self.grid[r][c] == 0:
                        if self.tile_img:
                            surface.blit(self.tile_img, screen_rect)
                            if self.room_types[r][c] == 1:
                                s = pygame.Surface((GRID_SIZE + 2, GRID_SIZE + 2), pygame.SRCALPHA); s.fill((218, 165, 32, 40)); surface.blit(s, screen_rect)
                            elif self.room_types[r][c] == 2:
                                s = pygame.Surface((GRID_SIZE + 2, GRID_SIZE + 2), pygame.SRCALPHA); s.fill((0, 100, 255, 40)); surface.blit(s, screen_rect)
                            elif self.room_types[r][c] == 3:
                                s = pygame.Surface((GRID_SIZE + 2, GRID_SIZE + 2), pygame.SRCALPHA); s.fill((0, 255, 100, 30)); surface.blit(s, screen_rect)
                        else:
                            if self.room_types[r][c] == 1: pygame.draw.rect(surface, FLOOR_TREASURE, screen_rect)
                            elif self.room_types[r][c] == 2: pygame.draw.rect(surface, FLOOR_SHOP, screen_rect)
                            elif self.room_types[r][c] == 3: pygame.draw.rect(surface, FLOOR_START, screen_rect)
                            else: pygame.draw.rect(surface, FLOOR_DEFAULT, screen_rect)
                    elif self.grid[r][c] == 1:
                        is_n_floor = r - 1 >= 0 and self.grid[r-1][c] == 0
                        is_s_floor = r + 1 < ROWS and self.grid[r+1][c] == 0
                        is_w_floor = c - 1 >= 0 and self.grid[r][c-1] == 0
                        is_e_floor = c + 1 < COLS and self.grid[r][c+1] == 0
                        has_floor_around = False
                        for dr in [-1, 0, 1]:
                            for dc in [-1, 0, 1]:
                                if 0 <= r+dr < ROWS and 0 <= c+dc < COLS and self.grid[r+dr][c+dc] == 0: has_floor_around = True
                        if has_floor_around:
                            if (is_n_floor and is_w_floor) or (is_n_floor and is_e_floor) or (is_s_floor and is_w_floor) or (is_s_floor and is_e_floor):
                                if self.short_wall_img: surface.blit(self.short_wall_img, screen_rect)
                                else: pygame.draw.rect(surface, (120, 100, 80), screen_rect)
                            elif is_w_floor or is_e_floor:
                                if self.vertical_wall_img: surface.blit(self.vertical_wall_img, screen_rect)
                                else: pygame.draw.rect(surface, (90, 110, 120), screen_rect)
                            elif is_n_floor or is_s_floor:
                                if self.long_wall_img: surface.blit(self.long_wall_img, screen_rect)
                                else: pygame.draw.rect(surface, (100, 110, 90), screen_rect)
                            else:
                                if self.short_wall_img: surface.blit(self.short_wall_img, screen_rect)
                                else: pygame.draw.rect(surface, WALL_COLOR, screen_rect)

class Item(Entity):
    def __init__(self, r, c, item_type, price=0):
        super().__init__(r, c, (0,0,0))
        self.item_type, self.price = item_type, price
        color = (255, 165, 0) if item_type == "FOOD" else (192, 192, 192) if item_type == "SHIELD" else (218, 165, 32)
        self.color = color; self.chest_state = "IDLE"; self.anim_frame = self.tick_accumulator = 0
        self.img_idle = self.img_opened = self.shop_icon = None; self.opening_frames = []; self.trigger_ui_after_open = False 
        
        if item_type == "FOOD":
            target_path = find_asset_path("Food.jpg")
            if target_path and os.path.exists(target_path): self.shop_icon = pygame.transform.scale(pygame.image.load(target_path).convert_alpha(), (GRID_SIZE, GRID_SIZE))
        elif item_type == "SHIELD":
            target_path = find_asset_path("Sheid.jpg")
            if target_path and os.path.exists(target_path): self.shop_icon = pygame.transform.scale(pygame.image.load(target_path).convert_alpha(), (GRID_SIZE, GRID_SIZE))
        elif item_type in ["FIRE_ART", "ICE_ART", "LIGHTNING_ART", "EXPLOSION_ART"]:
            icon_file = "fire_icon.jpg" if item_type == "FIRE_ART" else "ice_icon.jpg" if item_type == "ICE_ART" else "lightning_icon.jpg" if item_type == "LIGHTNING_ART" else "explosion_icon.jpg"
            target_path = find_asset_path(icon_file)
            if target_path and os.path.exists(target_path):
                try: self.shop_icon = pygame.transform.scale(pygame.image.load(target_path).convert_alpha(), (GRID_SIZE, GRID_SIZE))
                except: pass

        if item_type == "CHEST":
            CHEST_SIZE = (GRID_SIZE, GRID_SIZE)
            chest_path, chest_open_path, chest_opening_path = find_asset_path("chest.jpg"), find_asset_path("chest_open.jpg"), find_asset_path("chest_opening.jpg")
            try:
                if chest_path and os.path.exists(chest_path): self.img_idle = pygame.transform.scale(pygame.image.load(chest_path).convert_alpha(), CHEST_SIZE)
                if chest_open_path and os.path.exists(chest_open_path): self.img_opened = pygame.transform.scale(pygame.image.load(chest_open_path).convert_alpha(), CHEST_SIZE)
                if chest_opening_path and os.path.exists(chest_opening_path):
                    sheet = pygame.image.load(chest_opening_path).convert_alpha(); lw = sheet.get_width() // 5
                    content_offsets = [pygame.Rect(79, 73, 56, 31), pygame.Rect(80, 73, 56, 31), pygame.Rect(80, 71, 57, 33), pygame.Rect(81, 68, 57, 36), pygame.Rect(82, 66, 56, 38)]
                    for i_idx in range(5):
                        box_rect = content_offsets[i_idx]; sub_surf = sheet.subsurface(pygame.Rect((i_idx * lw) + box_rect.x, box_rect.y, box_rect.width, box_rect.height))
                        temp_canvas = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA); temp_canvas.blit(sub_surf, (0, 0))
                        self.opening_frames.append(pygame.transform.scale(temp_canvas, CHEST_SIZE))
            except: pass

    def update_animation(self, state_holder_ref):
        if self.chest_state == "OPENING" and self.opening_frames:
            self.tick_accumulator += 1
            if self.tick_accumulator >= 6:  
                self.tick_accumulator = 0; self.anim_frame += 1
                if self.anim_frame >= len(self.opening_frames):
                    self.chest_state = "OPENED"; self.anim_frame = 0
                    if self.trigger_ui_after_open:
                        self.trigger_ui_after_open = False
                        return "ARTIFACT_CHOICE" if state_holder_ref.get("reward_mode") == "ARTIFACT" else "GOLD_REWARD"
        return None

    def draw(self, surface, camera):
        rect = pygame.Rect(self.c * GRID_SIZE, self.r * GRID_SIZE, GRID_SIZE, GRID_SIZE); screen_rect = camera.apply(rect)
        if self.shop_icon: surface.blit(self.shop_icon, screen_rect)
        elif self.item_type == "CHEST":
            if self.chest_state == "IDLE" and self.img_idle: surface.blit(self.img_idle, screen_rect)
            elif self.chest_state == "OPENING" and self.opening_frames: surface.blit(self.opening_frames[min(self.anim_frame, len(self.opening_frames)-1)], screen_rect)
            elif self.chest_state == "OPENED" and self.img_opened: surface.blit(self.img_opened, screen_rect)
            else: pygame.draw.rect(surface, self.color, screen_rect)
        else: pygame.draw.circle(surface, self.color, (screen_rect.x + screen_rect.width // 2, screen_rect.y + screen_rect.height // 2), GRID_SIZE // 4)

class Merchant(Entity):
    def __init__(self, r, c):
        super().__init__(r, c, (0, 255, 120)); self.anim_frame = self.fps_tick_accumulator = 0
        self.merchant_frames = get_cached_frames("merchant.jpg", 8, False, dummy_color=(0, 255, 120))

    def update_animation(self):
        self.fps_tick_accumulator += 1
        if self.fps_tick_accumulator >= 6:
            self.fps_tick_accumulator = 0
            if self.merchant_frames: self.anim_frame = (self.anim_frame + 1) % len(self.merchant_frames)

    def draw(self, surface, camera):
        rect = pygame.Rect(self.c * GRID_SIZE, self.r * GRID_SIZE, GRID_SIZE, GRID_SIZE); screen_rect = camera.apply(rect)
        if self.merchant_frames:
            current_img = self.merchant_frames[self.anim_frame]; img_w, img_h = current_img.get_width(), current_img.get_height()
            surface.blit(current_img, pygame.Rect(screen_rect.x - (img_w - GRID_SIZE)//2, screen_rect.y - (img_h - GRID_SIZE), img_w, img_h))
        else: pygame.draw.rect(surface, self.color, camera.apply(pygame.Rect(self.c * GRID_SIZE + 4, self.r * GRID_SIZE + 4, GRID_SIZE - 8, GRID_SIZE - 8)))

class Player(Entity):
    def __init__(self, r, c):
        super().__init__(r, c, (0,0,0))
        self.max_hp, self.hp, self.defense, self.gold = 20, 20, 0, 15
        self.shield_durability = 0
        self.hunger, self.max_hunger = 120, 120
        self.level, self.exp, self.max_exp = 1, 0, 10
        self.ability_levels = {"ATK": 1, "DEF": 0, "MAX_HP": 1, "THORNS": 0, "VAMPIRISM": 0, "BERSERK": 0, "HASTE": 0, "MIDAS": 0, "REGEN": 0}
        self.equipped_artifact = None 

        self.idle_frames = get_cached_frames("IDLE .jpg", 7, False, dummy_color=(0, 200, 100))
        self.attack_frames = get_cached_frames("ATTACK 1.jpg", 6, True, dummy_color=(255, 200, 0))
        self.death_frames = get_cached_frames("DEATH.jpg", 11, False, dummy_color=(80, 80, 90))
        
        self.fire_effect_frames = get_cached_frames("fire.jpg", 3, False, False, True, dummy_color=(255, 120, 30))
        self.ice_effect_frames = get_cached_frames("ice.jpg", 12, False, False, True, dummy_color=(100, 200, 255))
        self.lightning_effect_frames = get_cached_frames("lightning.jpg", 7, False, False, True, dummy_color=(120, 220, 255))
        self.explosion_effect_frames = get_cached_frames("explosion.jpg", 12, False, False, True, dummy_color=(255, 80, 0))
        
        self.player_state, self.anim_frame, self.flip_x = "IDLE", 0, False
        self.r, self.c = r, c; self.visual_r, self.visual_c = float(r), float(c)
        self.bounce_time, self.is_bouncing = 0.0, False
        self.attack_offset_x = self.attack_offset_y = self.attack_timer = 0.0
        self.is_attacking_anim = False; self.damage_flash_timer = self.fps_tick_accumulator = 0
        self.death_animation_complete = False

    def gain_exp(self, amount, state_holder):
        if self.player_state == "DEATH": return
        self.exp += amount
        if self.exp >= self.max_exp:
            self.exp -= self.max_exp; self.level += 1; self.max_exp = int(self.max_exp * 1.4); state_holder["pending_level_ups"] += 1
            
            # ⭐️ [요청 사양 반영] 패시브 스킬 트리거와는 완전 별개로 기초 순수 보너스 스탯 누적 가산
            self.max_hp += 1
            self.hp = min(self.max_hp, self.hp + 1)
            print(f"🎉 [기초 성장] 기사의 레벨이 {self.level}로 올랐습니다! (기초 HP/공격력/방어력 +1 보너스 동시 획득)")

    def trigger_attack_state(self, dr, dc):
        if self.player_state == "DEATH": return
        self.player_state = "ATTACK"; self.anim_frame = 0; self.is_attacking_anim = True; self.attack_timer = 0.0
        self.attack_offset_x = dc * GRID_SIZE * 0.4; self.attack_offset_y = dr * GRID_SIZE * 0.4

    def take_damage(self, amount, camera, attacker=None, effect_list=None):
        if attacker and attacker.enemy_state == "DEATH": return
        
        # ⭐️ 기사의 방어력이 적용되도록 조정
        final_damage = max(1, amount - self.defense)
        if attacker and attacker.enemy_type != "SANDBAG": self.hp -= final_damage
        if camera: camera.start_shake(8, 4) # 피격 시 화면 진동 효과 연결
        
        # [수정] 흡혈 특성 제어 (player -> self)
        if self.ability_levels["VAMPIRISM"] > 0 and self.player_state != "DEATH":
            hit_vamp_chance = self.ability_levels["VAMPIRISM"] * 0.20
            if random.random() < hit_vamp_chance:
                self.hp = min(self.max_hp, self.hp + 1)
                print(f"🩸 [흡혈 특성] 적을 베어 생명력을 +1 탈취했습니다! (현재 HP: {self.hp}/{self.max_hp})")
                
        # [수정] 유물 트리거 장소 제어 (player -> self)
        if hasattr(self, "equipped_artifact") and self.equipped_artifact is not None and effect_list is not None:
            trigger_success = random.random() < 0.36 or (attacker and attacker.enemy_type == "SANDBAG")
            
            if self.equipped_artifact == "FIRE" and trigger_success:
                effect_list.append(VisualEffect(self.r, self.c, self.fire_effect_frames))
                self.debuff_type = "BURN"; self.debuff_duration = 3  
            elif self.equipped_artifact == "ICE" and trigger_success:
                effect_list.append(VisualEffect(self.r, self.c, self.ice_effect_frames))
                self.debuff_type = "SLOW"; self.debuff_duration = 4  
            elif self.equipped_artifact == "LIGHTNING" and trigger_success:
                effect_list.append(VisualEffect(self.r, self.c, self.lightning_effect_frames))
                self.debuff_type = "SHOCK"; self.debuff_duration = 5
            elif self.equipped_artifact == "EXPLOSION" and trigger_success:
                effect_list.append(VisualEffect(self.r, self.c, self.explosion_effect_frames))

        # ⭐️ 플레이어(기사)가 대미지를 받아 사망했을 때의 올바른 처리
        if self.hp <= 0: 
            self.hp = 0
            self.player_state = "DEATH"  # 기사의 상태를 DEATH로 변경
            self.anim_frame = 0
            self.fps_tick_accumulator = 0
            print("💀 [게임 오버] 기사가 치명상을 입고 쓰러졌습니다...")

    def update_physics_and_animation(self):
        self.visual_r += (self.r - self.visual_r) * 0.25; self.visual_c += (self.c - self.visual_c) * 0.25
        if self.is_bouncing:
            self.bounce_time += 0.25
            if self.bounce_time >= math.pi: self.is_bouncing = False; self.bounce_time = 0.0
        if self.is_attacking_anim:
            self.attack_timer += 0.25  
            if self.attack_timer >= math.pi: self.is_attacking_anim = False; self.attack_offset_x = self.attack_offset_y = 0.0
        self.fps_tick_accumulator += 1
        if self.fps_tick_accumulator >= 5:  
            self.fps_tick_accumulator = 0
            if self.player_state == "IDLE": self.anim_frame = (self.anim_frame + 1) % len(self.idle_frames)
            elif self.player_state == "ATTACK":
                self.anim_frame += 1
                if self.anim_frame >= len(self.attack_frames): self.player_state = "IDLE"; self.anim_frame = 0
            elif self.player_state == "DEATH":
                if self.anim_frame < len(self.death_frames) - 1: self.anim_frame += 1
                else: self.death_animation_complete = True  

    def draw(self, surface, camera):
        rect = pygame.Rect(self.visual_c * GRID_SIZE, self.visual_r * GRID_SIZE, GRID_SIZE, GRID_SIZE); screen_rect = camera.apply(rect)
        if self.is_bouncing: screen_rect.y -= int(math.sin(self.bounce_time) * 16)
        if self.is_attacking_anim:
            sf = math.sin(self.attack_timer); screen_rect.x += int(self.attack_offset_x * sf); screen_rect.y += int(self.attack_offset_y * sf)
        current_img = self.death_frames[self.anim_frame] if self.player_state == "DEATH" else self.attack_frames[min(self.anim_frame, len(self.attack_frames) - 1)] if self.player_state == "ATTACK" else self.idle_frames[self.anim_frame % len(self.idle_frames)]
        img_w, img_h = current_img.get_width(), current_img.get_height()
        render_rect = pygame.Rect(screen_rect.x - 10, screen_rect.y - (img_h - GRID_SIZE), img_w, img_h) if self.player_state == "ATTACK" and not self.flip_x else pygame.Rect(screen_rect.x - (img_w - GRID_SIZE) + 10, screen_rect.y - (img_h - GRID_SIZE), img_w, img_h) if self.player_state == "ATTACK" else pygame.Rect(screen_rect.x - (img_w - GRID_SIZE) // 2, screen_rect.y - (img_h - GRID_SIZE), img_w, img_h)
        if self.flip_x: current_img = pygame.transform.flip(current_img, True, False)
        
        if self.shield_durability > 0 and self.player_state != "DEATH":
            s_aura = pygame.Surface((img_w, img_h), pygame.SRCALPHA)
            s_aura.blit(current_img, (0, 0))
            s_aura.fill((0, 150, 255, 60), special_flags=pygame.BLEND_RGBA_ADD)
            surface.blit(s_aura, render_rect)
        
        if self.damage_flash_timer > 0 and self.player_state != "DEATH":
            self.damage_flash_timer -= 1; f_surf = current_img.copy(); f_surf.fill((255, 60, 60, 255), special_flags=pygame.BLEND_RGBA_MULT); surface.blit(f_surf, render_rect)
        elif self.shield_durability <= 0 or self.player_state == "DEATH" or self.damage_flash_timer <= 0: 
            surface.blit(current_img, render_rect)

    def move(self, dr, dc, game_map, enemies, state_holder, active_items_list, effect_list, merchant):
        if self.player_state == "DEATH": return False
        if dc < 0: self.flip_x = True
        elif dc > 0: self.flip_x = False
        target_r, target_c = self.r + dr, self.c + dc
        is_berserk_triggered = self.ability_levels["BERSERK"] > 0 and (self.hp <= self.max_hp // 2)
        berserk_multiplier = 1.0 + (self.ability_levels["BERSERK"] * 0.24 + 0.12) if is_berserk_triggered else 1.0
        
        # ⭐️ [요청 사양 반영] 패시브 데미지 계산식 외에 순수 기본 레벨업 증가분 (self.level - 1) 보너스를 더합니다!
        base_atk = (5 + (self.ability_levels["ATK"] - 1) * 3) + (self.level - 1)
        final_atk = int(base_atk * berserk_multiplier)
        
        if not game_map.is_walkable(target_r, target_c, active_items_list, enemies, merchant=merchant): 
            for enemy in enemies:
                if enemy.r == target_r and enemy.c == target_c and enemy.enemy_state != "DEATH":
                    self.trigger_attack_state(dr, dc); enemy.take_damage(final_atk, self, state_holder, effect_list, enemies) 
                    return True
            return False
        self.r, self.c = target_r, target_c; self.is_bouncing = True; return True

class Enemy(Entity):
    def __init__(self, r, c, enemy_type="GOBLIN", stage_level=1):
        super().__init__(r, c, ENEMY_IDLE_COLOR)
        self.enemy_type = enemy_type 
        self.state = "IDLE"; self.detection_range = 6; self.hit_flash_timer = 0
        self.debuff_type = "NONE"; self.debuff_duration = 0
        self.enemy_state = "IDLE"; self.anim_frame = self.fps_tick_accumulator = 0
        self.flip_x = self.death_animation_complete = False
        
        stage_bonus_hp = (stage_level - 1) * 2
        self.enemy_atk = 2 + (stage_level - 1)
        
        if self.enemy_type == "SANDBAG":
            self.hp = 9999
            self.idle_pool = get_cached_frames("M_Idle.jpg", 4, False, dummy_color=(140, 140, 150))
            self.attack_pool = []; self.death_pool = get_cached_frames("M_Death.jpg", 4, False, dummy_color=(70, 70, 70))
        elif self.enemy_type == "BOSS":
            self.hp = 60
            self.enemy_atk = 10
            self.idle_pool = get_cached_frames("boss_idle.jpg", total_frames=6, dummy_color=(255, 0, 0))
            self.attack_pool = get_cached_frames("boss_attack.jpg", total_frames=15, is_effect=False, dummy_color=(255, 50, 50))
            self.death_pool = get_cached_frames("boss_death.jpg", total_frames=18, is_death=True, dummy_color=(50, 50, 50))
        elif self.enemy_type == "GOBLIN":
            self.hp = 8 + stage_bonus_hp
            self.idle_pool = get_cached_frames("G_Idle.jpg", 4, False, dummy_color=(230, 70, 70))
            self.attack_pool = get_cached_frames("G_Attack.jpg", 8, is_effect=False, dummy_color=(255, 50, 50))
            self.death_pool = get_cached_frames("G_Death.jpg", 4, False, dummy_color=(100, 100, 100))
        else: 
            self.hp = 10 + stage_bonus_hp
            self.idle_pool = get_cached_frames("M_Idle.jpg", 4, False, dummy_color=(200, 80, 150))
            self.attack_pool = get_cached_frames("M_Attack.jpg", 8, is_effect=False, dummy_color=(220, 60, 120))
            self.death_pool = get_cached_frames("M_Death.jpg", 4, False, dummy_color=(90, 80, 90))

    def take_damage(self, amount, player, state_holder, effect_list, all_enemies_list=None):
        if self.enemy_state == "DEATH": return
        self.hit_flash_timer = 8
        if self.enemy_type != "SANDBAG": self.hp -= amount
        
        if player.ability_levels["VAMPIRISM"] > 0 and player.player_state != "DEATH":
            hit_vamp_chance = player.ability_levels["VAMPIRISM"] * 0.20
            if random.random() < hit_vamp_chance:
                player.hp = min(player.max_hp, player.hp + 1)
                print(f"🩸 [흡혈 특성] 적을 베어 생명력을 +1 탈취했습니다! (현재 HP: {player.hp}/{player.max_hp})")
            
        if hasattr(player, "equipped_artifact") and player.equipped_artifact is not None and effect_list is not None:
            trigger_success = random.random() < 0.36 or self.enemy_type == "SANDBAG"
            
            if player.equipped_artifact == "FIRE" and trigger_success:
                effect_list.append(VisualEffect(self.r, self.c, player.fire_effect_frames))
                self.debuff_type = "BURN"; self.debuff_duration = 3  
            elif player.equipped_artifact == "ICE" and trigger_success:
                effect_list.append(VisualEffect(self.r, self.c, player.ice_effect_frames))
                self.debuff_type = "SLOW"; self.debuff_duration = 4  
            elif player.equipped_artifact == "LIGHTNING" and trigger_success:
                effect_list.append(VisualEffect(self.r, self.c, player.lightning_effect_frames))
                self.debuff_type = "SHOCK"; self.debuff_duration = 5
            elif player.equipped_artifact == "EXPLOSION" and trigger_success:
                effect_list.append(VisualEffect(self.r, self.c, player.explosion_effect_frames))
                if all_enemies_list:
                    for target_enemy in all_enemies_list:
                        if target_enemy != self and target_enemy.enemy_state != "DEATH":
                            if abs(target_enemy.r - self.r) <= 1 and abs(target_enemy.c - self.c) <= 1:
                                splash_damage = max(1, amount // 2)
                                if target_enemy.enemy_type != "SANDBAG": target_enemy.hp -= splash_damage
                                target_enemy.hit_flash_timer = 6
                                effect_list.append(VisualEffect(target_enemy.r, target_enemy.c, player.fire_effect_frames))

        if self.hp <= 0: 
            self.hp = 0; self.enemy_state = "DEATH"; self.anim_frame = self.fps_tick_accumulator = 0
            if hasattr(player, "gain_exp"):
                player.gain_exp(4, state_holder) 
                
                current_stage_ref = state_holder.get("current_stage_level", 1)
                kill_gold_reward = 5 + (current_stage_ref - 1) * 2
                player.gold += kill_gold_reward
                print(f"💰 [전리품 정산] 몬스터를 격파하여 ${kill_gold_reward}를 루팅했습니다! (현재 골드: ${player.gold})") 

    def update_turn(self, player, game_map, camera, all_enemies, merchant):
        if player.player_state == "DEATH" or self.enemy_state == "DEATH": return
        if self.enemy_type == "SANDBAG": return

        if self.debuff_duration > 0:
            if self.debuff_type == "BURN":
                self.hp -= 3; self.hit_flash_timer = 6
                if self.hp <= 0: self.hp = 0; self.enemy_state = "DEATH"; self.anim_frame = 0; return
            elif self.debuff_type == "SLOW":
                if self.debuff_duration % 2 == 1: self.debuff_duration -= 1; return 
            elif self.debuff_type == "SHOCK":
                if random.random() < 0.50:
                    self.hit_flash_timer = 4
                    self.debuff_duration -= 1
                    if self.debuff_duration <= 0: self.debuff_type = "NONE"
                    return 
            self.debuff_duration -= 1
            if self.debuff_duration <= 0: self.debuff_type = "NONE"

        distance = abs(self.r - player.r) + abs(self.c - player.c)
        current_range = 10 if self.enemy_type == "BOSS" else self.detection_range
        self.state = "CHASE" if distance <= current_range else "IDLE"

        if self.state == "CHASE":
            dr = dc = 0
            if self.r < player.r: dr = 1
            elif self.r > player.r: dr = -1
            elif self.c < player.c: dc = 1
            elif self.c > player.c: dc = -1
            
            if self.r + dr == player.r and self.c + dc == player.c:
                self.enemy_state = "ATTACK"; self.anim_frame = 0
                player.take_damage(self.enemy_atk, camera, self, effect_list=[])
            else:
                other_enemies = [e for e in all_enemies if e != self]
                if game_map.is_walkable(self.r + dr, self.c + dc, enemies=other_enemies, player=player, merchant=merchant): self.r += dr; self.c += dc

    def update_animation(self):
        self.fps_tick_accumulator += 1
        if self.fps_tick_accumulator >= 4: 
            self.fps_tick_accumulator = 0
            frames_pool = self.death_pool if self.enemy_state == "DEATH" else self.attack_pool if self.enemy_state == "ATTACK" else self.idle_pool
            if frames_pool:
                if self.enemy_state == "IDLE": self.anim_frame = (self.anim_frame + 1) % len(frames_pool)
                elif self.enemy_state == "ATTACK":
                    self.anim_frame += 1
                    if self.anim_frame >= len(frames_pool): self.enemy_state = "IDLE"; self.anim_frame = 0
                elif self.enemy_state == "DEATH":
                    if self.anim_frame < len(frames_pool) - 1: self.anim_frame += 1
                    else: self.death_animation_complete = True

    def draw(self, surface, camera, player_ref=None):
        if self.enemy_state == "DEATH" and self.death_animation_complete: return 
        rect = pygame.Rect(self.c * GRID_SIZE, self.r * GRID_SIZE, GRID_SIZE, GRID_SIZE); screen_rect = camera.apply(rect)
        
        if player_ref:
            if self.enemy_type == "BOSS":
                if player_ref.c < self.c: self.flip_x = False
                elif player_ref.c > self.c: self.flip_x = True
            else:
                if player_ref.c < self.c: self.flip_x = True  
                elif player_ref.c > self.c: self.flip_x = False 

        if self.debuff_type == "BURN": self.color = ENEMY_BURN_COLOR
        elif self.debuff_type == "SLOW": self.color = ENEMY_SLOW_COLOR
        elif self.debuff_type == "SHOCK": self.color = ENEMY_SHOCK_COLOR
        else: self.color = ENEMY_CHASE_COLOR if self.state == "CHASE" else ENEMY_IDLE_COLOR
        
        frames_pool = self.death_pool if self.enemy_state == "DEATH" else self.attack_pool if self.enemy_state == "ATTACK" else self.idle_pool
        if frames_pool:
            current_img = frames_pool[min(self.anim_frame, len(frames_pool) - 1)]
            if self.flip_x: current_img = pygame.transform.flip(current_img, True, False)
            img_w, img_h = current_img.get_width(), current_img.get_height()
            
            if self.enemy_type == "BOSS":
                render_rect = pygame.Rect(screen_rect.x - (img_w - GRID_SIZE)//2, screen_rect.y - (img_h - GRID_SIZE) + 28, img_w, img_h)
            else:
                offset_y = (img_h - GRID_SIZE) if self.enemy_state != "ATTACK" else (img_h - GRID_SIZE) - 10
                render_rect = pygame.Rect(screen_rect.x - (img_w - GRID_SIZE)//2, screen_rect.y - offset_y, img_w, img_h)
                
            if self.hit_flash_timer > 0:
                self.hit_flash_timer -= 1; f_surf = current_img.copy(); f_surf.fill((255, 100, 100, 255), special_flags=pygame.BLEND_RGBA_MULT); surface.blit(f_surf, render_rect)
            else: surface.blit(current_img, render_rect)
        else:
            sub_rect = pygame.Rect(screen_rect.x + 4, screen_rect.y + 4, GRID_SIZE - 8, GRID_SIZE - 8)
            if self.hit_flash_timer > 0: self.hit_flash_timer -= 1; pygame.draw.rect(surface, (255, 255, 255), sub_rect)
            else: pygame.draw.rect(surface, self.color, sub_rect)

global main_map_grid_ref

def main():
    pygame.init(); screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Rogue Knight - Fix Portal Spawning"); clock = pygame.time.Clock()
    
    # ⭐️ [배경음악 주입] 던전 오디오 오실레이터 믹서 장치 초기화 연산 가동
    try:
        pygame.mixer.init()
        if os.path.exists("dungeon_bgm.wav"):
            pygame.mixer.music.load("dungeon_bgm.wav")
            pygame.mixer.music.set_volume(0.6)  # 볼륨 60% 조절
            pygame.mixer.music.play(-1)          # -1 입력으로 무한 루프 반복 설정 완치
            print("🎵 [BGM 가동] 던전 배경음악이 안전하게 무한 반복 구동됩니다.")
        else:
            print("⚠️ [BGM 경고] dungeon_bgm.wav 파일을 찾을 수 없어 사운드가 무음 처리됩니다.")
    except Exception as audio_err:
        print(f"⚠️ [오디오 시스템 예외 가동]: {audio_err}")

    screen.fill((10, 10, 15)); boot_font = pygame.font.SysFont("malgungothic", 40, bold=True)
    load_text = boot_font.render("NOW LOADING...", True, (255, 215, 0)); screen.blit(load_text, (SCREEN_WIDTH // 2 - load_text.get_width() // 2, SCREEN_HEIGHT // 2 - 20)); pygame.display.flip()
    
    build_asset_cache(); virtual_screen = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
    title_font = pygame.font.SysFont("malgungothic", 54); sub_font = pygame.font.SysFont("malgungothic", 32)
    ui_font = pygame.font.SysFont("malgungothic", 24); ui_font_bold = pygame.font.SysFont("malgungothic", 26, bold=True)

    game_map = GameMap(); camera = Camera(); player = Player(game_map.start_pos[0], game_map.start_pos[1])
    stage_level = 1; merchant_npc = stairs = None; previous_enemy_count = 0 
    active_effects = []; state_holder = {"pending_level_ups": 0, "current_choices": [], "current_stage_level": 1}; saved_merchant_r = saved_merchant_c = 0

    # ★ 플레이어의 실시간 스탯을 기사 레벨 기반으로 상시 동기화해 주는 안전 함수
    def sync_player_stats():
        player.defense = (player.ability_levels["DEF"] // 2) + (player.level - 1)

    def setup_new_stage():
        nonlocal game_map, merchant_npc, previous_enemy_count, active_effects, stairs, saved_merchant_r, saved_merchant_c
        state_holder["current_stage_level"] = stage_level
        if stage_level == 5:
            game_map.grid = [[1 for _ in range(COLS)] for _ in range(ROWS)]; game_map.room_types = [[0 for _ in range(COLS)] for _ in range(ROWS)]
            for r in range(5, ROWS - 5):
                for c in range(5, COLS - 5): game_map.grid[r][c] = 0
            game_map.start_pos = (ROWS // 2, 8); player.r, player.c = game_map.start_pos
            player.visual_r, player.visual_c = float(player.r), float(player.c); player.death_animation_complete = False
            active_effects = []; stairs = None; merchant_npc = None; boss = Enemy(ROWS // 2, COLS - 10, "BOSS", stage_level)
            previous_enemy_count = 1
            return [boss], [], None

        game_map.generate_structured_map(); player.r, player.c = game_map.start_pos
        player.visual_r, player.visual_c = float(player.r), float(player.c); player.death_animation_complete = False; active_effects = []; stairs = None 
        
        if player.ability_levels["REGEN"] > 0 and player.hp < player.max_hp:
            player.hp += int((player.max_hp - player.hp) * (player.ability_levels["REGEN"] * 0.12))

        new_items = [Item(game_map.treasure_room_rect.y + game_map.treasure_room_rect.height // 2, game_map.treasure_room_rect.x + game_map.treasure_room_rect.width // 2, "CHEST")]
        mr, mc = game_map.shop_room_rect.y + game_map.shop_room_rect.height // 2, game_map.shop_room_rect.x + game_map.shop_room_rect.width // 2
        merchant_npc = Merchant(mr, mc); saved_merchant_r, saved_merchant_c = mr, mc
        
        goods_blueprint = [("FOOD", 25, -2), ("SHIELD", 25, -1)]
        for g_type, g_price, offset in goods_blueprint: new_items.append(Item(mr + 1, mc + offset, g_type, price=g_price))
        
        artifact_pool = ["FIRE_ART", "ICE_ART", "LIGHTNING_ART", "EXPLOSION_ART"]; chosen_shop_art = random.choice(artifact_pool)
        new_items.append(Item(mr + 1, mc + 1, chosen_shop_art, price=300)); new_enemies = []
        
        for b_room in game_map.battle_rooms_rects:
            for _ in range(random.randint(2, 3)):
                er, ec = game_map.get_room_random_pos(b_room)
                monster = Enemy(er, ec, "MUSHROOM" if random.random() < 0.50 else "GOBLIN", stage_level)
                monster.enemy_state = "IDLE"; monster.anim_frame = 0; new_enemies.append(monster)
        previous_enemy_count = len(new_enemies)
        return new_enemies, new_items, None

    enemies, items, _ = setup_new_stage(); main_map_grid_ref = game_map.grid
    current_scene = "TITLE"; game_state = "PLAYER_TURN"

    running = True
    while running:
        sync_player_stats()  # 루프 시작 시 항상 레벨업 능력치 가산 상태 동기화
        mx, my = pygame.mouse.get_pos(); player_acted = False; on_item_node = None  
        if current_scene == "PLAY":
            main_map_grid_ref = game_map.grid; camera.update_shake(); player.update_physics_and_animation()
            for fx in active_effects[:]:
                fx.update()
                if fx.is_finished: active_effects.remove(fx)
            for item in items:
                next_ui_trigger = item.update_animation(state_holder)
                if next_ui_trigger: game_state = next_ui_trigger
            for enemy in enemies: enemy.update_animation() 
            if merchant_npc: merchant_npc.update_animation()
            
            if stairs:
                stairs.update_animation()
                
            camera.target_on(player)
            
            if state_holder["pending_level_ups"] > 0 and game_state not in ["GAME_OVER_SCENE", "LEVEL_UP_CHOICE", "ARTIFACT_CHOICE", "GOLD_REWARD"]:
                game_state = "LEVEL_UP_CHOICE"; pool = ["ATK", "DEF", "MAX_HP", "THORNS", "VAMPIRISM", "BERSERK", "HASTE", "MIDAS", "REGEN"]
                available_pool = [p for p in pool if player.ability_levels[p] < 3]
                if len(available_pool) < 3: available_pool = pool[:3]
                state_holder["current_choices"] = random.sample(available_pool, 3)
                
            if player.player_state == "DEATH" and player.death_animation_complete: game_state = "GAME_OVER_SCENE"
            for item in items:
                if item.item_type != "CHEST" and item.r == player.r and item.c == player.c: on_item_node = item; break
                elif item.item_type == "CHEST" and abs(item.r - player.r) + abs(item.c - player.c) == 1: on_item_node = item; break

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if current_scene == "TITLE" and event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN: current_scene = "PLAY"
            elif current_scene == "PLAY" and game_state == "PLAYER_TURN" and player.player_state != "DEATH":
                if event.type == pygame.KEYDOWN:
                    dr = dc = 0
                    if event.key == pygame.K_w: dr = -1
                    elif event.key == pygame.K_s: dr = 1
                    elif event.key == pygame.K_a: dc = -1
                    elif event.key == pygame.K_d: dc = 1
                    elif event.key == pygame.K_b:
                        print("⚡ [CHEAT] 최종 5층 보스룸 시공간으로 강제 도약합니다."); stage_level = 5; enemies, items, _ = setup_new_stage(); game_state = "PLAYER_TURN"; continue
                    elif event.key == pygame.K_m:
                        print("🛠️ [SYSTEM] 개발자 테스트용 샌드박스 광장이 오픈되었습니다."); game_map.generate_test_room_grid(player.r, player.c); enemies.clear()
                        enemies.append(Enemy(player.r, player.c + 2, "SANDBAG")); enemies.append(Enemy(player.r + 1, player.c + 2, "GOBLIN")); enemies.append(Enemy(player.r - 1, player.c + 3, "MUSHROOM"))
                        items.clear(); items.append(Item(player.r - 2, player.c - 2, "CHEST")); merchant_npc = stairs = None; game_state = "PLAYER_TURN"; continue
                    elif event.key == pygame.K_SPACE:
                        current_room = game_map.get_room_at(player.r, player.c)
                        
                        if current_room:
                            room_enemies = [
                                e for e in enemies 
                                if e.enemy_state != "DEATH" and 
                                current_room.x <= e.c < current_room.x + current_room.width and 
                                current_room.y <= e.r < current_room.y + current_room.height
                            ]
                            
                            if len(room_enemies) == 0:
                                if player.hp < player.max_hp:
                                    if player.hunger > 0:
                                        player.hp = min(player.max_hp, player.hp + 4) 
                                        player.hunger = max(0, player.hunger - 8)     
                                        player_acted = True
                                        print(f"💖 [회복 성공] 체력이 회복되었습니다. (현재 HP: {player.hp}/{player.max_hp})")
                                    else:
                                        print("⚠️ [배고픔] 포만감이 부족하여 휴식할 수 없습니다!")
                                else:
                                    print("🛠️ [SYSTEM] 이미 체력이 가득 차 있어 포만감을 소모하지 않고 보호합니다.")
                                    
                    elif event.key == pygame.K_f:
                        chest_triggered = False
                        for item in items:
                            if item.item_type == "CHEST" and abs(item.r - player.r) + abs(item.c - player.c) == 1:
                                if item.chest_state == "OPENED": item.chest_state = "IDLE"
                                if item.chest_state == "IDLE":
                                    item.chest_state = "OPENING"
                                    if random.random() < 0.40: state_holder["found_artifact"] = random.choice(["FIRE", "ICE", "LIGHTNING", "EXPLOSION"]); item.trigger_ui_after_open = True; state_holder["reward_mode"] = "ARTIFACT"
                                    else:
                                        base_gold = 50 - max(random.randint(0, 49), random.randint(0, 49))
                                        if player.ability_levels["MIDAS"] > 0: 
                                            base_gold = int(base_gold * (1.0 + player.ability_levels["MIDAS"] * 0.24))
                                        state_holder["found_gold"] = base_gold; state_holder["found_artifact"] = None; item.trigger_ui_after_open = True; state_holder["reward_mode"] = "GOLD"
                                    player_acted = chest_triggered = True; break
                        if not chest_triggered:
                            for item in items[:]:
                                if item.item_type != "CHEST" and item.r == player.r and item.c == player.c:
                                    if player.gold >= item.price:
                                        player.gold -= item.price
                                        if item.item_type == "FOOD": player.hunger = min(player.max_hunger, player.hunger + 50)
                                        elif item.item_type == "SHIELD": 
                                            player.ability_levels["DEF"] = min(3, player.ability_levels["DEF"] + 1)
                                            sync_player_stats()
                                            player.shield_durability += 5
                                            print(f"🛡️ [방패 구입] 방어력 레벨업 및 실시간 방어막 내구도가 +5 충전되었습니다! (현재 방어막: {player.shield_durability})")
                                        elif item.item_type in ["FIRE_ART", "ICE_ART", "LIGHTNING_ART", "EXPLOSION_ART"]: pure_type = item.item_type.split("_")[0]; player.equipped_artifact = pure_type
                                        items.remove(item); player_acted = True
                                    
                    if dr != 0 or dc != 0: player_acted = player.move(dr, dc, game_map, enemies, state_holder, items, active_effects, merchant=merchant_npc)
                    if player_acted:
                        if len([e for e in enemies if e.enemy_state != "DEATH"]) == 0 and stairs is None:
                            if stage_level == 5: stairs = Stairs(ROWS // 2, COLS // 2)
                            else: stairs = Stairs(saved_merchant_r - 1, saved_merchant_c); player.hp = min(player.max_hp, player.hp + 4)
                        if stairs and player.r == stairs.r and player.c == stairs.c:
                            if stage_level == 5: current_scene = "CLEAR"; continue
                            stage_level += 1; enemies, items, _ = setup_new_stage(); game_state = "PLAYER_TURN"; continue
                        game_state = "PLAYER_TURN" if (player.ability_levels["HASTE"] * 0.06 > 0 and random.random() < player.ability_levels["HASTE"] * 0.06) else "ENEMY_TURN"

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game_state == "LEVEL_UP_CHOICE" and len(state_holder["current_choices"]) == 3:
                    card_w, card_h = 320, 380; card_y = SCREEN_HEIGHT // 2 - card_h // 2
                    rects = [pygame.Rect(SCREEN_WIDTH // 2 - 500, card_y, card_w, card_h), pygame.Rect(SCREEN_WIDTH // 2 - 160, card_y, card_w, card_h), pygame.Rect(SCREEN_WIDTH // 2 + 180, card_y, card_w, card_h)]
                    sel_idx = -1
                    for idx, r in enumerate(rects):
                        if r.collidepoint(mx, my): sel_idx = idx; break
                    if sel_idx != -1:
                        ability = state_holder["current_choices"][sel_idx]; player.ability_levels[ability] = min(3, player.ability_levels[ability] + 1)
                        if ability == "MAX_HP": 
                            player.max_hp += 3; player.hp = player.max_hp
                        
                        state_holder["pending_level_ups"] -= 1; state_holder["current_choices"] = []
                        sync_player_stats()  # 특성 카드를 고른 후 다시 한번 동기화 보장
                        if state_holder["pending_level_ups"] <= 0: game_state = "PLAYER_TURN"
                elif game_state == "ARTIFACT_CHOICE":
                    btn_w, btn_h, btn_y = 240, 60, SCREEN_HEIGHT // 2 + 100
                    if pygame.Rect(SCREEN_WIDTH // 2 - 380, btn_y, btn_w, btn_h).collidepoint(mx, my): player.equipped_artifact = state_holder.get("found_artifact"); state_holder["reward_mode"] = None; game_state = "PLAYER_TURN"
                    elif pygame.Rect(SCREEN_WIDTH // 2 - 120, btn_y, btn_w, btn_h).collidepoint(mx, my): state_holder["reward_mode"] = None; game_state = "PLAYER_TURN"
                    elif pygame.Rect(SCREEN_WIDTH // 2 + 140, btn_y, btn_w, btn_h).collidepoint(mx, my): player.equipped_artifact = state_holder.get("found_artifact"); state_holder["reward_mode"] = None; game_state = "PLAYER_TURN"
                elif game_state == "GOLD_REWARD":
                    if pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 80, 300, 60).collidepoint(mx, my): player.gold += state_holder.get("found_gold", 0); state_holder["found_gold"] = 0; state_holder["reward_mode"] = None; game_state = "PLAYER_TURN"
                elif game_state == "GAME_OVER_SCENE":
                    if pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 60, 300, 60).collidepoint(mx, my):
                        stage_level = 1; player.level = 1; player.exp = 0; player.max_exp = 10
                        player.ability_levels = {"ATK": 1, "DEF": 0, "MAX_HP": 1, "THORNS": 0, "VAMPIRISM": 0, "BERSERK": 0, "HASTE": 0, "MIDAS": 0, "REGEN": 0}
                        player.player_state = "IDLE"; player.anim_frame = 0; player.max_hp = 20; player.hp = player.max_hp; player.hunger = player.max_hunger; player.shield_durability = 0; player.death_animation_complete = False; player.equipped_artifact = None
                        enemies, items, _ = setup_new_stage(); current_scene = "PLAY"; game_state = "PLAYER_TURN"

        if current_scene == "PLAY" and game_state == "ENEMY_TURN" and player.player_state != "DEATH":
            for enemy in [e for e in enemies if e.enemy_state != "DEATH"]: 
                enemy.update_turn(player, game_map, camera, enemies, merchant=merchant_npc)
            game_state = "PLAYER_TURN"

        if current_scene == "TITLE":
            screen.fill(BG_COLOR); t_text = title_font.render("ROGUE KNIGHT", True, TITLE_COLOR); s_text = sub_font.render("Press [ ENTER ] to Play", True, TEXT_COLOR)
            screen.blit(t_text, (SCREEN_WIDTH // 2 - t_text.get_width() // 2, SCREEN_HEIGHT // 2 - 80)); screen.blit(s_text, (SCREEN_WIDTH // 2 - s_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
        elif current_scene == "PLAY":
            virtual_screen.fill((0, 0, 0)); game_map.draw(virtual_screen, camera)
            if stairs: stairs.draw(virtual_screen, camera)
            for item in items: item.draw(virtual_screen, camera)
            if merchant_npc: merchant_npc.draw(virtual_screen, camera)
            
            for enemy in enemies: enemy.draw(virtual_screen, camera, player_ref=player)
            
            player.draw(virtual_screen, camera)
            for fx in active_effects: fx.draw(virtual_screen, camera)
            screen.blit(pygame.transform.scale(virtual_screen, (SCREEN_WIDTH, SCREEN_HEIGHT)), (0, 0))
            
            if game_state not in ["GAME_OVER_SCENE", "LEVEL_UP_CHOICE", "ARTIFACT_CHOICE", "GOLD_REWARD"]:
                stage_str = "STAGE: 5/5 (FINAL BOSS)" if stage_level == 5 else f"STAGE: {stage_level}/5"
                
                # ★ 보너스가 누적된 위력을 UI 수치에서 더 직관적으로 보기 위해 보정 연동
                display_atk = (5 + (player.ability_levels["ATK"] - 1) * 3) + (player.level - 1)
                
                hp_txt = ui_font.render(f"{stage_str}  |  HP: {player.hp}/{player.max_hp}  [방어막 보호 수치: {player.shield_durability}]  |  DEF: {player.defense}", True, TEXT_COLOR)
                lv_txt = ui_font.render(f"기사 LEVEL: {player.level}  |  검의 총 공격력: {display_atk} (특성 포함)", True, (0, 255, 255))
                ex_txt = ui_font.render(f"EXP: {player.exp}/{player.max_exp}  |  보유 골드: ${player.gold}", True, (150, 255, 150))
                num_enemies_left = len([e for e in enemies if e.enemy_state != "DEATH"])
                hun_txt = ui_font.render(f"포만감: {player.hunger}/{player.max_hunger}  |  남은 적의 수: {num_enemies_left}마리", True, (255, 165, 0) if player.hunger > 0 else (255, 50, 50))
                
                art_owned_string = "[화염] 마석 장착 (36% 확률 점화 대미지)" if player.equipped_artifact == "FIRE" else "[얼음] 비석 장착 (36% 확률 동결 디버프)" if player.equipped_artifact == "ICE" else "[뇌전] 보주 장착 (36% 확률 감전 마비)" if player.equipped_artifact == "LIGHTNING" else "[폭발] 니트로 핵심 장착 (36% 확률 광역 스플래시)" if player.equipped_artifact == "EXPLOSION" else "장착 없음"
                p_str = ", ".join([f"{k}(Lv.{v})" for k, v in player.ability_levels.items() if v > 0 and k not in ["ATK", "MAX_HP"]])
                pas_txt = ui_font.render(f"보유 패시브 리스트: {p_str if p_str else '없음'}", True, (255, 130, 255)); art_txt = ui_font.render(f"장착 유물 슬롯: {art_owned_string}", True, (255, 215, 0))
                screen.blit(hp_txt, (40, 30)); screen.blit(lv_txt, (40, 70)); screen.blit(ex_txt, (40, 110)); screen.blit(hun_txt, (40, 150)); screen.blit(pas_txt, (40, 190)); screen.blit(art_txt, (40, 230))
                
                if on_item_node:
                    if on_item_node.item_type == "CHEST": help_msg = "  이미 개봉된 상자입니다  " if on_item_node.chest_state == "OPENED" else "  상자가 열리는 중입니다...  " if on_item_node.chest_state == "OPENING" else "  [ F ] 보물상자 정면 개봉하기  "
                    elif on_item_node.item_type == "FOOD": help_msg = f"  [ F ] ${on_item_node.price}에 [비상 식량 (포만감 +50)] 구매하기  "
                    elif on_item_node.item_type == "SHIELD": help_msg = f"  [ F ] ${on_item_node.price}에 [간이 방어막 방패 (쉴드내구도 +5 충전)] 강화하기  "
                    elif on_item_node.item_type in ["FIRE_ART", "ICE_ART", "LIGHTNING_ART", "EXPLOSION_ART"]:
                        p_name = "화염의 마석" if on_item_node.item_type == "FIRE_ART" else "얼음의 비석" if on_item_node.item_type == "ICE_ART" else "뇌전의 보주" if on_item_node.item_type == "LIGHTNING_ART" else "니트로 융합핵"
                        help_msg = f"  소지 자금 정산 구매: [ F ] ${on_item_node.price}에 고대 유물 [{p_name}] 다이렉트 영입  "
                    screen.blit(ui_font_bold.render(help_msg, True, (255, 215, 0) if on_item_node.item_type in ["CHEST", "FIRE_ART", "ICE_ART", "LIGHTNING_ART", "EXPLOSION_ART"] else (0, 255, 150)), (40, 400))
            
            if game_state == "LEVEL_UP_CHOICE" and len(state_holder["current_choices"]) == 3:
                card_w, card_h = 320, 380; card_y = SCREEN_HEIGHT // 2 - card_h // 2
                dim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); dim.fill((10, 10, 15, 220)); screen.blit(dim, (0, 0))
                title = title_font.render("  [ LEVEL UP ] 강화할 특성 카드를 선택하세요  ", True, TITLE_COLOR); screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 120))
                
                ability_details = {
                    "ATK": {
                        "title": "▶ 영혼의 참격술", 
                        "lines": ["- 효과: 공격력 +3 증가", "", "- 성격: 영구적 물리 화력", "        패시브 강화"]
                    },
                    "DEF": {
                        "title": "▶ 강철 신체훈련", 
                        "lines": ["- 효과: 피격 대미지", "        절대 상쇄 경감", "", "- 성격: 생존 방어 수치", "        안정적 밸런싱"]
                    },
                    "MAX_HP": {
                        "title": "▶ 생명 통확장", 
                        "lines": ["- 효과: 최대체력 +3 확장", "        및 체력 완전 치유", "", "- 성격: 즉시형 생존", "        리커버리 시스템"]
                    },
                    "THORNS": {
                        "title": "▶ 가시 갑옷 스파이크", 
                        "lines": ["- 효과: 피격 시 적에게", "        고정 반사피해", "", "- 성격: 인과응보형", "        반격 제어 장치"]
                    },
                    "VAMPIRISM": {
                        "title": "▶ 흡혈귀의 생명 추출", 
                        "lines": ["- 효과: 적 타격 성공 시", "        확률적 생명 +1 피흡", "", "- 성격: On-Hit 메커니즘", "        공격 시 즉시 피흡"]
                    },
                    "BERSERK": {
                        "title": "▶ 광전사 위기 폭발", 
                        "lines": ["- 효과: HP 50% 이하 시", "        가해량 비율 대폭 증가", "", "- 성격: 위기를 기회로", "        바꾸는 배수 공격"]
                    },
                    "HASTE": {
                        "title": "▶ 신속의 가속 장화", 
                        "lines": ["- 효과: 행동 후 확률적", "        추가 턴 획득 기동", "", "- 성격: 턴 소모가 없는", "        연속 포지셔닝"]
                    },
                    "MIDAS": {
                        "title": "▶ 황금의 연금 축복", 
                        "lines": ["- 효과: 상자 리워드 골드", "        자금 획득률 보스팅", "", "- 성격: 던전 상점 방", "        아이템 세팅 가속"]
                    },
                    "REGEN": {
                        "title": "▶ 나노 재생 아머", 
                        "lines": ["- 효과: 다음 층 진입 시", "        체력 자동 복구", "", "- 성격: 던전 장기 탐험", "        지속 유지력 확보"]
                    }
                }
                
                for idx, r in enumerate([pygame.Rect(SCREEN_WIDTH // 2 - 500, card_y, card_w, card_h), pygame.Rect(SCREEN_WIDTH // 2 - 160, card_y, card_w, card_h), pygame.Rect(SCREEN_WIDTH // 2 + 180, card_y, card_w, card_h)]):
                    key = state_holder["current_choices"][idx]; det = ability_details.get(key, {"title":"공백", "lines":[]}); curr_level = player.ability_levels[key]
                    pygame.draw.rect(screen, (45, 45, 60) if r.collidepoint(mx, my) else (25, 25, 35), r, 0, 16); pygame.draw.rect(screen, (0, 255, 200) if r.collidepoint(mx, my) else (200, 50, 250) if key in ["THORNS", "VAMPIRISM", "BERSERK", "HASTE", "MIDAS", "REGEN"] else (100, 100, 120), r, 3, 16)
                    
                    t_s = ui_font_bold.render(det["title"], True, TITLE_COLOR if r.collidepoint(mx, my) else (255, 100, 255) if key in ["THORNS", "VAMPIRISM", "BERSERK", "HASTE", "MIDAS", "REGEN"] else TEXT_COLOR)
                    l_s = ui_font.render(f" [ 레벨 수치: {curr_level} / 3 ]", True, (255, 215, 0))
                    
                    screen.blit(t_s, (r.x + 20, r.y + 40))
                    screen.blit(l_s, (r.x + 20, r.y + 80))
                    
                    start_y_offset = r.y + 150
                    for line_idx, text_line in enumerate(det["lines"]):
                        rendered_line = ui_font.render(text_line, True, (200, 255, 200) if "- 효과:" in text_line or "절대" in text_line else (170, 170, 180))
                        screen.blit(rendered_line, (r.x + 20, start_y_offset + (line_idx * 30)))
            
            if game_state == "ARTIFACT_CHOICE":
                dim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); dim.fill((10, 10, 15, 220)); screen.blit(dim, (0, 0))
                art_name = state_holder.get("found_artifact"); art_title = " 화염의 마석 " if art_name == "FIRE" else " 얼음의 비석 " if art_name == "ICE" else " 뇌전의 보주 " if art_name == "LIGHTNING" else " 니트로 융합핵 "
                art_desc = "공격 성공 시 36% 확률로 적에게 3턴간 화염 지속 피해 가산" if art_name == "FIRE" else "공격 성공 시 36% 확률로 적의 기동 속도를 4턴간 무력화 제어" if art_name == "ICE" else "공격 성공 시 36% 확률로 적을 감전(5턴간 50% 확률로 마비 스킵 유도)" if art_name == "LIGHTNING" else "공격 성공 시 36% 확률로 주변 3x3 범위 방사형 스플래시 연쇄 연타 피해" if art_name == "EXPLOSION" else ""
                screen.blit(title_font.render("  고대 유물 아티팩트 발견   ", True, TITLE_COLOR), (SCREEN_WIDTH // 2 - 450, SCREEN_HEIGHT // 2 - 200))
                name_surf = ui_font_bold.render(f"유물 종류: {art_title}", True, (255, 100, 255)); desc_surf = ui_font.render(art_desc, True, TEXT_COLOR);
                screen.blit(name_surf, (SCREEN_WIDTH // 2 - name_surf.get_width() // 2, SCREEN_HEIGHT // 2 - 80)); desc_surf = ui_font.render(art_desc, True, TEXT_COLOR);
                screen.blit(desc_surf, (SCREEN_WIDTH // 2 - desc_surf.get_width() // 2, SCREEN_HEIGHT // 2 - 20))
                curr_surf = ui_font.render(f"(기사 슬롯 장착 무기 장착 상태: {player.equipped_artifact if player.equipped_artifact else '장착 없음'})", True, (150, 150, 150));
                screen.blit(curr_surf, (SCREEN_WIDTH // 2 - max(10, curr_surf.get_width() // 2), SCREEN_HEIGHT // 2 + 30))
                btn_w, btn_h, btn_y = 240, 60, SCREEN_HEIGHT // 2 + 100
                for b in [{"rect": pygame.Rect(SCREEN_WIDTH // 2 - 380, btn_y, btn_w, btn_h), "text": " 유물 장착하기 ", "color": (40, 140, 80)}, {"rect": pygame.Rect(SCREEN_WIDTH // 2 - 120, btn_y, btn_w, btn_h), "text": " 유물 버리기 ", "color": (140, 40, 40)}, {"rect": pygame.Rect(SCREEN_WIDTH // 2 + 140, btn_y, btn_w, btn_h), "text": " 기존 유물 교체 ", "color": (40, 80, 140)}]:
                    pygame.draw.rect(screen, [min(255, c + 40) for c in b["color"]] if b["rect"].collidepoint(mx, my) else b["color"], b["rect"], 0, 12); pygame.draw.rect(screen, TEXT_COLOR if b["rect"].collidepoint(mx, my) else (200, 200, 200), b["rect"], 2, 12)
                    txt_surf = ui_font_bold.render(b["text"], True, TEXT_COLOR); screen.blit(txt_surf, (b["rect"].x + btn_w // 2 - txt_surf.get_width() // 2, b["rect"].y + btn_h // 2 - txt_surf.get_height() // 2))
            
            if game_state == "GOLD_REWARD":
                dim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); dim.fill((10, 10, 15, 220)); screen.blit(dim, (0, 0)); screen.blit(title_font.render(" TREASURE REWARD ", True, TITLE_COLOR), (SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 - 200))
                card_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 100, 400, 220); confirm_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 80, 300, 60); pygame.draw.rect(screen, (25, 25, 35), card_rect, 0, 16); pygame.draw.rect(screen, (218, 165, 32), card_rect, 3, 16) 
                gold_surf = sub_font.render(f"+ {state_holder.get('found_gold', 0)} GOLD", True, (255, 215, 0)); sub_msg = ui_font.render("던전 보물상자 리워드 자금 정산", True, (170, 170, 180)); screen.blit(gold_surf, (card_rect.x + 200 - gold_surf.get_width() // 2, card_rect.y + 50)); screen.blit(sub_msg, (card_rect.x + 200 - sub_msg.get_width() // 2, card_rect.y + 130))
                pygame.draw.rect(screen, (180, 130, 20) if confirm_rect.collidepoint(mx, my) else (120, 90, 15), confirm_rect, 0, 8); pygame.draw.rect(screen, TEXT_COLOR if confirm_rect.collidepoint(mx, my) else (200, 200, 200), confirm_rect, 2, 8); btn_txt = ui_font_bold.render(" 자금 수령하기 ", True, TEXT_COLOR); screen.blit(btn_txt, (confirm_rect.x + 150 - btn_txt.get_width() // 2, confirm_rect.y + 30 - btn_txt.get_height() // 2))
            
            if game_state == "GAME_OVER_SCENE":
                ov_ol = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); ov_ol.fill((0, 0, 0, 180)); screen.blit(ov_ol, (0, 0)); o_txt = title_font.render("GAME OVER", True, (255, 50, 50)); screen.blit(o_txt, (SCREEN_WIDTH // 2 - o_txt.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
                b_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 60, 300, 60); pygame.draw.rect(screen, (80, 20, 20) if b_rect.collidepoint(mx, my) else (40, 15, 15), b_rect, 0, 8); pygame.draw.rect(screen, (255, 50, 50), b_rect, 2, 8); b_txt = ui_font_bold.render("RESTART GAME", True, TEXT_COLOR); screen.blit(b_txt, (SCREEN_WIDTH // 2 - b_txt.get_width() // 2, SCREEN_HEIGHT // 2 + 75))
        
        # ⭐️ [문구 변경 완료] 보스를 처치하고 완전히 탈출했을 때의 메인 문구 수정 영역
        elif current_scene == "CLEAR":
            screen.fill((10, 25, 15))
            screen.blit(title_font.render("  VICTORY - DUNGEON CLEAR!  ", True, TITLE_COLOR), (SCREEN_WIDTH // 2 - 400, SCREEN_HEIGHT // 2 - 80))
            screen.blit(sub_font.render("던전에 보스를 죽이고 클리어 했습니다", True, TEXT_COLOR), (SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 + 20))
            
        pygame.display.flip(); clock.tick(60)
    pygame.quit(); sys.exit()

if __name__ == "__main__": main()