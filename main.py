import pygame
import sys
import math
import random

from src.core.settings import (SCREEN_W, SCREEN_H, FPS, ROOM_W, ROOM_H,
                                PADDING, ROOMS_MAP, SAFE_ROOM)
from src.core.camera import Camera
from src.core.world import RoomWorld
from src.entities.soldier import Soldier
from src.entities.enemy import EnemySoldier
from src.entities.dummy import TacticalDummy
from src.ui.manager import GameUI
from src.ui.screens.profile import ProfileScreen
from src.core.paths import get_asset_path, get_data_path, get_safe_font


def main():
    pygame.init()
    # Low-latency mixer — 512-sample buffer eliminates perceptible sync lag
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.mixer.init(44100, -16, 2, 512)
    is_fullscreen = False
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.SCALED)
    # English Title
    pygame.display.set_caption("PROJECT SOLDIER")
    clock = pygame.time.Clock()

    # ── SOUND EFFECTS ─────────────────────────────────────────────────────────────────
    try:
        snd_shot   = pygame.mixer.Sound(get_asset_path("shot1.mp3"))
        snd_reload = pygame.mixer.Sound(get_asset_path("reload1.mp3"))
        snd_shot.set_volume(1.0)
        snd_reload.set_volume(1.0)
    except Exception as e:
        print(f"[AUDIO] Could not load SFX: {e}")
        snd_shot = snd_reload = None

    try:
        snd_btn = pygame.mixer.Sound(get_asset_path("button_sound.mp3"))
        snd_btn.set_volume(0.75)
    except Exception as e:
        print(f"[AUDIO] Could not load button_sound: {e}")
        snd_btn = None

    def play_btn():
        if snd_btn: snd_btn.play()

    # Real walking footstep from file (fallback to procedural if missing)
    try:
        snd_step = pygame.mixer.Sound(get_asset_path("walking1.mp3"))
        snd_step.set_volume(0.55)
    except:
        import array, math as _math
        def _make_step(sample_rate=44100, freq=90, dur=0.07):
            n = int(sample_rate * dur)
            buf = array.array('h')
            for i in range(n):
                t = i / sample_rate
                decay = _math.exp(-t * 40)
                val = int(32767 * decay * (
                    0.6 * _math.sin(2 * _math.pi * freq * t) +
                    0.4 * _math.sin(2 * _math.pi * freq * 2.5 * t)
                ))
                buf.append(max(-32767, min(32767, val)))
                buf.append(max(-32767, min(32767, val)))
            return pygame.mixer.Sound(buffer=buf)
        snd_step = _make_step()
        snd_step.set_volume(0.55)

    # ── BACKGROUND MUSIC SYSTEM ─────────────────────────────────────────────────
    # Menu alternates between two tracks via MUSIC_END event
    MUSIC_END = pygame.USEREVENT + 1
    pygame.mixer.music.set_endevent(MUSIC_END)
    _menu_tracks   = [get_asset_path("menu_audio_1.mp3"), get_asset_path("menu_audio2.mp3")]
    _menu_idx      = 0
    _current_music = None   # Track what's currently loaded

    def play_music(track, volume=0.55, loops=-1):
        """Load and start a background music track, no-op if already playing it."""
        nonlocal _current_music
        if track == _current_music:
            return
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(track)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(loops)
            _current_music = track
        except Exception as e:
            print(f"[MUSIC] Could not load {track}: {e}")
            _current_music = None

    def stop_music():
        nonlocal _current_music
        pygame.mixer.music.fadeout(800)
        _current_music = None

    # Dedicated mixer channels for SFX
    player_shot_ch = pygame.mixer.Channel(0)
    enemy_shot_ch  = pygame.mixer.Channel(1)
    step_ch        = pygame.mixer.Channel(2)

    # Walk-sound frame tracking
    _prev_walk_frame = -1
    _step_interval = 2       # play every N walk-animation frames

    world = RoomWorld()
    camera = Camera()

    # Start in the SAFE_ROOM (Room 0)
    sp_x = PADDING + ROOM_W // 2
    sp_y = PADDING + ROOM_H // 2
    soldier = Soldier(sp_x, sp_y)

    # Dummy in a later room
    dummy_room = ROOMS_MAP[2]
    dummy = TacticalDummy(PADDING + dummy_room[0]*ROOM_W + ROOM_W//2, 
                          PADDING + dummy_room[1]*ROOM_H + ROOM_H//2)

    ui = GameUI(soldier)
    enemies = []
    spawn_timer = 0
    state = "LOGIN"
    paused = False

    from src.ui.elements.mobile import VirtualJoystick
    joystick = VirtualJoystick(200, SCREEN_H - 200, radius=110, stick_radius=40)
    game_over_timer = 0
    sprint_toggle = False
    _space_was_pressed = False   # Rising-edge tracker for semi-auto fire
    
    running = True
    while running:
        clock.tick(FPS)
        sw, sh = screen.get_size()
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    is_fullscreen = not is_fullscreen
                    flags = pygame.FULLSCREEN if is_fullscreen else pygame.RESIZABLE
                    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), flags)
                if event.key == pygame.K_ESCAPE and state == "PLAYING":
                    paused = not paused
                    play_btn()  # ESC = pause toggle
            # ── Menu track alternation: when one menu track ends, cue the next ──
            if event.type == MUSIC_END and state in ("LOGIN", "MENU", "LAN_MENU", "PROFILE", "AVATAR_SELECT"):
                _menu_idx = (_menu_idx + 1) % len(_menu_tracks)
                _current_music = None   # Force reload
                play_music(_menu_tracks[_menu_idx], volume=0.50, loops=0)

        # ── MUSIC STATE MACHINE — sync music to game state ─────────────────────────────
        if state == "LOGIN":
            play_music(_menu_tracks[_menu_idx], volume=0.45, loops=0)
        elif state in ("MENU", "LAN_MENU", "PROFILE", "AVATAR_SELECT"):
            play_music(_menu_tracks[_menu_idx], volume=0.50, loops=0)
        elif state == "PLAYING":
            if not paused:
                play_music(get_asset_path("gameplay_bg1.mp3"), volume=0.42, loops=-1)
                pygame.mixer.music.set_volume(0.42)
            else:
                # Quiet the music during pause
                if _current_music == get_asset_path("gameplay_bg1.mp3"):
                    pygame.mixer.music.set_volume(0.12)
        elif state == "GAME_OVER":
            if _current_music is not None:
                stop_music()

        # ─── STATE MANAGER ────────────────────────────────────────────────────
        if state == "LOGIN":
            if ui.update_login(events) == "login":
                name = ui.login_menu.name_in.text.strip()
                if name:
                    play_btn()  # Login submit
                    img_file = ui.avatar_sel.profiles[ui.avatar_sel.selected]["file"]
                    ui.prof_screen = ProfileScreen(name, img_file)
                    ui.hud.profile_name = name.upper()
                    ui.hud.profile_img_file = img_file
                    state = "MENU"
            ui.draw_login(screen)

        elif state == "MENU":
            actions = ui.update_main()
            if actions: play_btn()   # Any menu button press
            if "solo"  in actions: state = "PLAYING"
            if "lan"   in actions: state = "LAN_MENU"
            if "prof"  in actions: state = "PROFILE"
            if "exit"  in actions: running = False
            ui.draw_main(screen)

        elif state == "LAN_MENU":
            _lan_res = ui.update_lan()
            if _lan_res: play_btn()
            if "back" in _lan_res: state = "MENU"
            ui.draw_lan(screen)

        elif state == "PROFILE":
            res = ui.update_prof()
            if res: play_btn()
            if res == "back": state = "MENU"
            if res == "edit": state = "AVATAR_SELECT"
            ui.draw_prof(screen)

        elif state == "AVATAR_SELECT":
            res = ui.update_avatar()
            if res:
                play_btn()
                ui.prof_screen.ins = res
                ui.hud.profile_img_file = res
                state = "PROFILE"
            ui.draw_avatar(screen)

        elif state == "PLAYING":
            # ── PAUSE ──
            ui_res = ui.update(paused)
            if paused:
                if ui_res == "resume": paused = False; play_btn()
                if ui_res == "quit":
                    play_btn()
                    state = "MENU"; paused = False
                    enemies.clear(); ui.hud.kill_count = 0
            else:
                if "pause" in ui_res: play_btn()  # Mobile pause button in gameplay
                joystick.process_events(events)
                keys = pygame.key.get_pressed()

                # Soldier Actions — semi-auto: one shot per click, blocked while shot sound plays
                keys = pygame.key.get_pressed()
                _space_now = keys[pygame.K_SPACE]
                _space_edge = _space_now and not _space_was_pressed   # Rising edge only
                _space_was_pressed = _space_now

                # Block shooting while the previous shot sound is still playing
                _can_fire = not player_shot_ch.get_busy()
                trigger_shoot = _can_fire and (_space_edge or ui.buttons["shoot"].pressed)
                if "run" in ui_res: sprint_toggle = not sprint_toggle
                if trigger_shoot: sprint_toggle = False
                
                soldier.shoot(trigger_shoot)
                _wants_reload = "reload" in ui_res or keys[pygame.K_r]
                if _wants_reload:
                    if not soldier.is_reloading and soldier.ammo < getattr(soldier, 'max_ammo', 30):
                        if snd_reload: snd_reload.play()  # Play at START of reload
                    soldier.reload()
                if "grenade" in ui_res or keys[pygame.K_g]: soldier.throw_grenade()
                if "pause"   in ui_res: paused = True

                # Collision Obstacles
                obstacles = list(world.walls)
                if not dummy.is_dead:
                    obstacles.append(dummy.hitbox)

                prev_ammo = soldier.ammo
                is_sprint_active = sprint_toggle or ui.buttons["run"].pressed or keys[pygame.K_LSHIFT]
                ui.buttons["run"].is_toggled = sprint_toggle
                soldier.update(keys, obstacles, jx=joystick.dx, jy=joystick.dy, pad_sprint=is_sprint_active)

                # ── SHOT SOUND: play exactly when a bullet was spawned this frame ──
                if soldier.ammo < prev_ammo:
                    camera.add_shake(2.5)
                    if snd_shot: player_shot_ch.play(snd_shot)

                # ── RELOAD SOUND: remove the old end-of-anim trigger (now fires on initiation) ──
                if hasattr(soldier, '_reload_done') and soldier._reload_done:
                    soldier._reload_done = False  # Just consume the flag, sound already played

                # ── FOOTSTEP SOUND: play at frame 0 and mid-cycle only (2x per walk cycle) ──
                if soldier.current_anim in ("Walk", "Run") and not soldier.is_dead:
                    cur_frame = soldier.frame_index
                    frames_total = max(1, len(soldier.anims.get(soldier.current_anim, [])))
                    half = frames_total // 2
                    # Trigger on frame 0 and the mid-point frame
                    is_step_frame = cur_frame in (0, half)
                    if is_step_frame and cur_frame != _prev_walk_frame:
                        if not step_ch.get_busy():
                            step_ch.play(snd_step)
                    _prev_walk_frame = cur_frame
                else:
                    _prev_walk_frame = -1

                if soldier.is_dead:
                    camera.add_shake(3.0) # Epic death shake
                    if getattr(soldier, 'frame_index', 0) == len(soldier.anims.get("Dead", [])) - 1:
                        state = "GAME_OVER"
                        game_over_timer = 0
                        paused = False
                        import os
                        current_hs = 0
                        hs_file = get_data_path("highscore.txt")
                        if os.path.exists(hs_file):
                            try:
                                with open(hs_file, "r") as f: current_hs = int(f.read())
                            except: pass
                        if ui.hud.kill_count > current_hs:
                            current_hs = ui.hud.kill_count
                            with open(hs_file, "w") as f: f.write(str(current_hs))
                        ui.hud.high_score = current_hs
                        continue

                dummy.update()

                # ── SPAWN ENEMIES (Skip Safe Room) ──
                spawn_timer += 1
                if spawn_timer > 360 and len(enemies) < 8:
                    spawn_timer = 0
                    # Pick a room that is NOT the safe room
                    spawnable_rooms = [r for idx, r in enumerate(ROOMS_MAP) if idx != SAFE_ROOM]
                    room = random.choice(spawnable_rooms)
                    ex = PADDING + room[0]*ROOM_W + random.randint(100, ROOM_W - 250)
                    ey = PADDING + room[1]*ROOM_H + random.randint(100, ROOM_H - 250)
                    enemies.append(EnemySoldier(ex, ey, soldier.anims))

                # ── HITBOX & COMBAT ──
                p_foot = soldier.foot_rect()
                # Full body hitbox for receiving bullets
                p_hitbox = pygame.Rect(soldier.x - 20, soldier.y - 70, 40, 70)

                for en in enemies[:]:
                    prev_en_bullets = len(en.bullets)
                    en.update(soldier.x, soldier.y, obstacles)

                    # Enemy shot sound (low volume = feels distant)
                    if snd_shot and len(en.bullets) > prev_en_bullets:
                        if not enemy_shot_ch.get_busy():
                            snd_shot.set_volume(0.35)
                            enemy_shot_ch.play(snd_shot)
                            snd_shot.set_volume(1.0)

                    if en.health <= 0 and not getattr(en, "kill_counted", False):
                        en.kill_counted = True
                        ui.hud.kill_count += 1
                        camera.add_shake(6.0)

                    # Player bullets → enemy
                    en_hitbox = pygame.Rect(en.x - 25, en.y - 80, 50, 80)
                    for b in soldier.bullets[:]:
                        if not en.is_dead and pygame.Rect(b.x-5, b.y-5, 10, 10).colliderect(en_hitbox):
                            en.take_damage(16)
                            b.alive = False

                    # Enemy bullets → soldier
                    for eb in en.bullets[:]:
                        if pygame.Rect(eb.x-5, eb.y-5, 10, 10).colliderect(p_hitbox):
                            soldier.health -= 6
                            eb.alive = False
                            camera.add_shake(4.5)

                # Player bullets → dummy
                d_rect = dummy.hitbox
                for b in soldier.bullets[:]:
                    if not dummy.is_dead and pygame.Rect(b.x-5, b.y-5, 10, 10).colliderect(d_rect):
                        dummy.take_damage(12)
                        camera.add_shake(1.5)
                        b.alive = False

                # Area Damage
                for p in soldier.projectiles:
                    if hasattr(p, "has_exploded") and p.has_exploded:
                        camera.add_shake(18.0)
                        for en in enemies:
                            de = math.hypot(p.x - en.x, p.y - en.y)
                            if de < 260:
                                en.take_damage(int(max(10, 110 - de / 2)))
                        if math.hypot(p.x - soldier.x, p.y - soldier.y) < 200:
                            soldier.health -= 25

                # Update HUD with enemy list
                ui.hud.enemies_ref = enemies

                camera.update(soldier.x, soldier.y)

            # ── RENDER ──────────────────────────────────────────────────────
            screen.fill((5, 7, 13))
            world.draw(screen, camera)

            ents = [soldier, dummy] + enemies
            ents.sort(key=lambda e: e.y)
            for e in ents:
                e.draw(screen, camera)
                if hasattr(e, "bullets"):
                    for eb in e.bullets:
                        eb.draw(screen, camera)

            ui.draw(screen, paused)
            
            # Draw Mobile Joystick overlay if alive
            if state == "PLAYING" and not paused and not soldier.is_dead:
                joystick.draw(screen)

        elif state == "GAME_OVER":
            game_over_timer += 1
            screen.fill((5, 7, 13))
            world.draw(screen, camera)
            ents = [soldier, dummy] + enemies
            ents.sort(key=lambda e: e.y)
            for e in ents:
                e.draw(screen, camera)
                
            # Epic Blood Heartbeat Red Pulse Overlay
            pulse = math.sin(game_over_timer * 0.1) * 30 + 150
            ov = pygame.Surface((sw, sh), pygame.SRCALPHA)
            ov.fill((100, 5, 5, int(pulse)))
            for y in range(0, sh, 4): pygame.draw.line(ov, (0, 0, 0, 80), (0, y), (sw, y))
            screen.blit(ov, (0,0))
            
            f_go = get_safe_font("Consolas", 100, bold=True)
            f_st = get_safe_font("Consolas", 40, bold=True)
            
            # Dark Overlay for premium feel
            overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            t = f_go.render("K. I. A.", True, (255, 30, 30))
            screen.blit(t, (sw//2 - t.get_width()//2, sh//3 - 80))
            
            tk = f_st.render(f"HOSTILES KIA : {ui.hud.kill_count}", True, (240, 240, 240))
            tr = f_st.render(f"SERVICE RECORD : {getattr(ui.hud, 'high_score', 0)}", True, (150, 200, 120))
            screen.blit(tk, (sw//2 - tk.get_width()//2, sh//2 - 40))
            screen.blit(tr, (sw//2 - tr.get_width()//2, sh//2 + 10))
            
            if not hasattr(ui, "btn_retry"):
                from src.ui.elements.base import MenuButton
                ui.btn_retry = MenuButton(0, 100, 400, 60, "REDEPLOY", is_right=False)
                ui.btn_tomenu = MenuButton(0, 180, 400, 60, "MAIN MENU", is_right=False)
                ui.btn_quit_game = MenuButton(0, 260, 400, 60, "EXIT GAME", is_right=False)
            
            ui.btn_retry.update(sw, sh)
            ui.btn_tomenu.update(sw, sh)
            ui.btn_quit_game.update(sw, sh)
            
            ui.btn_retry.draw(screen)
            ui.btn_tomenu.draw(screen)
            ui.btn_quit_game.draw(screen)
            
            if ui.btn_retry.pressed:
                if 'play_btn' in locals() or 'play_btn' in globals(): play_btn()
                soldier.health = 100.0
                soldier.is_dead = False
                soldier.x, soldier.y = PADDING + ROOM_W // 2, PADDING + ROOM_H // 2
                enemies.clear()
                ui.hud.kill_count = 0
                state = "PLAYING"
                pygame.event.clear()
            elif ui.btn_tomenu.pressed:
                if 'play_btn' in locals() or 'play_btn' in globals(): play_btn()
                soldier.health = 100.0
                soldier.is_dead = False
                soldier.x, soldier.y = PADDING + ROOM_W // 2, PADDING + ROOM_H // 2
                enemies.clear()
                ui.hud.kill_count = 0
                state = "MENU"
                pygame.event.clear()
            elif ui.btn_quit_game.pressed:
                if 'play_btn' in locals() or 'play_btn' in globals(): play_btn()
                running = False

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    import traceback
    try:
        main()
    except Exception:
        err = traceback.format_exc()
        print(err)
        
        pygame.init()
        # Fallback screen for errors
        try:
            from src.core.settings import SCREEN_W, SCREEN_H
        except:
            SCREEN_W, SCREEN_H = 400, 600
            
        screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.SCALED)
        pygame.display.set_caption("Error Log")
        font = get_safe_font("Consolas", 18)
        if not font: font = pygame.font.SysFont(None, 24)
        
        while True:
            screen.fill((120, 0, 0))
            y = 10
            for line in err.splitlines():
                if y > SCREEN_H - 20: break
                txt = font.render(line[:80], True, (255, 255, 255))
                screen.blit(txt, (10, y))
                y += 22
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    import sys; sys.exit()
            
            pygame.display.flip()
            pygame.time.Clock().tick(10)
