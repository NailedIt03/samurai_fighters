import pygame
import sys
import os
import math  


pygame.init()
pygame.mixer.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BG_COLOR = (0, 0, 0)  
FIGHTER_WIDTH = 400
FIGHTER_HEIGHT = 400
HITBOX_WIDTH = 200  
HITBOX_HEIGHT = 200  
GRAVITY = 0.7
JUMP_STRENGTH = 12
ANIMATION_SPEED = 0.1 
TITLE_SHAKE_AMPLITUDE = 5
FADE_SPEED = 2 
GAME_OVER_DELAY = 3



pygame.mixer.music.load('assets/music/theme.ogg')
pygame.mixer.music.set_volume(0.5)

pygame.mixer.music.play(-1) 

player1_win_sound = pygame.mixer.Sound('assets/music/player1_win.mp3')
player1_win_sound.set_volume(1)
player2_win_sound = pygame.mixer.Sound('assets/music/player2_win.mp3')
player2_win_sound.set_volume(1)

fighter1_hit_sound = pygame.mixer.Sound('assets/music/hit1.mp3')
fighter2_hit_sound = pygame.mixer.Sound('assets/music/hit2.mp3')


def load_images_from_folder(folder, flip=False):
    images = []
    for filename in os.listdir(folder):
        try:
            img = pygame.image.load(os.path.join(folder, filename))
            if img is not None:
                if flip:
                    img = pygame.transform.flip(img, True, False)  
                images.append(img)
        except pygame.error:
            print(f"Warning: Failed to load image file '{filename}'")
            continue
    return images


fighter1_idle = load_images_from_folder('assets/fighter1/idle')
fighter1_punch = load_images_from_folder('assets/fighter1/punch')
fighter1_walk = load_images_from_folder('assets/fighter1/walk')
fighter1_jump = load_images_from_folder('assets/fighter1/jump')
fighter1_dead = load_images_from_folder('assets/fighter1/dead')

fighter2_idle = load_images_from_folder('assets/fighter2/idle', flip=True)
fighter2_punch = load_images_from_folder('assets/fighter2/punch', flip=True)
fighter2_walk = load_images_from_folder('assets/fighter2/walk', flip=True)
fighter2_jump = load_images_from_folder('assets/fighter2/jump', flip=True)
fighter2_dead = load_images_from_folder('assets/fighter2/dead', flip=True)


fighter1_idle = [pygame.transform.scale(image, (FIGHTER_WIDTH, FIGHTER_HEIGHT)) for image in fighter1_idle]
fighter1_punch = [pygame.transform.scale(image, (FIGHTER_WIDTH, FIGHTER_HEIGHT)) for image in fighter1_punch]
fighter1_walk = [pygame.transform.scale(image, (FIGHTER_WIDTH, FIGHTER_HEIGHT)) for image in fighter1_walk]
fighter1_jump = [pygame.transform.scale(image, (FIGHTER_WIDTH, FIGHTER_HEIGHT)) for image in fighter1_jump]
fighter1_dead = [pygame.transform.scale(image, (FIGHTER_WIDTH, FIGHTER_HEIGHT)) for image in fighter1_dead]

fighter2_idle = [pygame.transform.scale(image, (FIGHTER_WIDTH, FIGHTER_HEIGHT)) for image in fighter2_idle]
fighter2_punch = [pygame.transform.scale(image, (FIGHTER_WIDTH, FIGHTER_HEIGHT)) for image in fighter2_punch]
fighter2_walk = [pygame.transform.scale(image, (FIGHTER_WIDTH, FIGHTER_HEIGHT)) for image in fighter2_walk]
fighter2_jump = [pygame.transform.scale(image, (FIGHTER_WIDTH, FIGHTER_HEIGHT)) for image in fighter2_jump]
fighter2_dead = [pygame.transform.scale(image, (FIGHTER_WIDTH, FIGHTER_HEIGHT)) for image in fighter2_dead]


background_images = load_images_from_folder('assets/background')
background_images = [pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT)) for img in background_images]

main_screen_background_images = load_images_from_folder('assets/menubg')
main_screen_background_images = [pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT)) for img in main_screen_background_images]


font_large = pygame.font.Font('assets/PressStart2P-Regular.ttf', 32)
font_small = pygame.font.Font('assets/PressStart2P-Regular.ttf', 16)


class Fighter:
    def __init__(self, x, y, idle_images, punch_images, walk_images, jump_images, dead_images, health_bar_pos):
        self.idle_images = idle_images
        self.punch_images = punch_images
        self.walk_images = walk_images
        self.jump_images = jump_images
        self.dead_images = dead_images
        self.images = idle_images
        self.image_index = 0
        self.image = self.images[self.image_index]
        self.rect = pygame.Rect(x, y, HITBOX_WIDTH, HITBOX_HEIGHT)  
        self.is_punching = False
        self.is_walking = False
        self.is_jumping = False
        self.is_dead = False
        self.health = 100
        self.speed = 5
        self.jump_speed = 0
        self.animation_speed = 0.1
        self.current_animation_time = 0
        self.health_bar_pos = health_bar_pos

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x - (FIGHTER_WIDTH - HITBOX_WIDTH) // 2, 
                                 self.rect.y - (FIGHTER_HEIGHT - HITBOX_HEIGHT) // 2))
        self.draw_health_bar(screen)

        

    def draw_health_bar(self, screen):
        health_bar_width = 200
        health_bar_height = 20
        fill = (self.health / 100) * health_bar_width
        if self.health_bar_pos == "left":
            outline_rect = pygame.Rect(20, 20, health_bar_width, health_bar_height)
            fill_rect = pygame.Rect(20, 20, fill, health_bar_height)
        else:
            outline_rect = pygame.Rect(SCREEN_WIDTH - health_bar_width - 20, 20, health_bar_width, health_bar_height)
            fill_rect = pygame.Rect(SCREEN_WIDTH - health_bar_width - 20, 20, fill, health_bar_height)
        pygame.draw.rect(screen, (255, 0, 0), fill_rect)
        pygame.draw.rect(screen, (255, 255, 255), outline_rect, 2)

    def update_animation(self, dt):
        if self.is_dead:
            if self.image_index < len(self.dead_images) - 1:
                self.current_animation_time += dt
                if self.current_animation_time >= self.animation_speed:
                    self.current_animation_time = 0
                    self.image_index += 1
                    self.image = self.dead_images[self.image_index]
        else:
            self.current_animation_time += dt
            if self.current_animation_time >= self.animation_speed:
                self.current_animation_time = 0
                self.image_index = (self.image_index + 1) % len(self.images)
                self.image = self.images[self.image_index]
                if self.is_punching and self.image_index == 0:
                    self.idle()

    def punch(self):
        if not self.is_dead:
            self.images = self.punch_images
            self.is_punching = True
            self.image_index = 0

    def idle(self):
        if not self.is_dead:
            self.images = self.idle_images
            self.is_punching = False
            self.is_walking = False
            self.is_jumping = False
            self.image_index = 0

    def walk(self, direction):
        if not self.is_punching and not self.is_dead: 
            self.images = self.walk_images
            self.rect.x += direction * self.speed
            self.is_walking = True

    def jump(self):
        if not self.is_jumping and not self.is_dead:
            self.images = self.jump_images
            self.is_jumping = True
            self.jump_speed = -JUMP_STRENGTH
            self.image_index = 0

    def apply_gravity(self):
        if self.is_jumping and not self.is_dead:
            self.jump_speed += GRAVITY
            self.rect.y += self.jump_speed

         
            if self.rect.y >= SCREEN_HEIGHT - FIGHTER_HEIGHT + 160:
                self.rect.y = SCREEN_HEIGHT - FIGHTER_HEIGHT + 160
                self.is_jumping = False  
                self.jump_speed = 0
                self.idle()

    def get_hit(self):
        if not self.is_dead:
            self.health -= 10
            if self.health <= 0:
                self.die()

    def die(self):
        self.is_dead = True
        self.images = self.dead_images
        self.image_index = 0


def show_main_screen(screen, background_images, animation_time, shake_offset, instruction_alpha):
    
    current_frame = int(animation_time / ANIMATION_SPEED) % len(background_images)
    screen.blit(background_images[current_frame], (0, 0))
    
    
    title_text = font_large.render("Samurai Fighters", True, (255, 255, 255))
    instruction_text = font_small.render("Press Space to start", True, (155, 155, 155))
    

    title_x = SCREEN_WIDTH // 2 - title_text.get_width() // 2
    title_y = SCREEN_HEIGHT // 2 - title_text.get_height() // 2 + shake_offset
    
    
    instruction_surface = instruction_text.copy()
    instruction_surface.set_alpha(instruction_alpha)
    
    instruction_x = SCREEN_WIDTH // 2 - instruction_surface.get_width() // 2
    instruction_y = SCREEN_HEIGHT - instruction_surface.get_height() - 50 
    
    
    screen.blit(title_text, (title_x, title_y))
    screen.blit(instruction_surface, (instruction_x, instruction_y))
    
    pygame.display.flip()


def update_background(screen, background_images, animation_time):
    current_frame = int(animation_time / ANIMATION_SPEED) % len(background_images)
    screen.blit(background_images[current_frame], (0, 0))


def show_end_screen(screen, winner_text):
    if winner_text == "Player 1 Wins!":
        player1_win_sound.play()
    elif winner_text == "Player 2 Wins!":
        player2_win_sound.play()
    screen.fill(BG_COLOR)

  
    winner_text_surface = font_large.render(winner_text, True, (255, 255, 255))
    winner_text_x = SCREEN_WIDTH // 2 - winner_text_surface.get_width() // 2
    winner_text_y = SCREEN_HEIGHT // 2 - winner_text_surface.get_height() // 2 - 100
    screen.blit(winner_text_surface, (winner_text_x, winner_text_y))


    main_menu_text = font_small.render("Main Menu", True, (255, 255, 255))
    quit_text = font_small.render("Quit", True, (255, 255, 255))

    main_menu_rect = main_menu_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))

    pygame.draw.rect(screen, (255, 255, 255), main_menu_rect.inflate(20, 10), 2)
    pygame.draw.rect(screen, (255, 255, 255), quit_rect.inflate(20, 10), 2)

    screen.blit(main_menu_text, main_menu_rect)
    screen.blit(quit_text, quit_rect)

    pygame.display.flip()

    return main_menu_rect, quit_rect

#game loop
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Samurai Fighters')

fighter1 = Fighter(50, SCREEN_HEIGHT - FIGHTER_HEIGHT + 160, fighter1_idle, fighter1_punch, fighter1_walk, fighter1_jump, fighter1_dead, "left")
fighter2 = Fighter(SCREEN_WIDTH - 300, SCREEN_HEIGHT - FIGHTER_HEIGHT + 160, fighter2_idle, fighter2_punch, fighter2_walk, fighter2_jump, fighter2_dead, "right")

running = True
clock = pygame.time.Clock()
game_started = False
game_over = False
background_animation_time = 0
title_shake_time = 0
instruction_fade_direction = 1
instruction_alpha = 255
game_over_time = None

while running:
    dt = clock.tick(60) / 1000  
    background_animation_time += dt
    title_shake_time += dt
    
    shake_offset = int(TITLE_SHAKE_AMPLITUDE * math.sin(2 * math.pi * title_shake_time)) 
    
    
    instruction_alpha += instruction_fade_direction * FADE_SPEED
    if instruction_alpha >= 255 or instruction_alpha <= 0:
        instruction_fade_direction *= -1
        instruction_alpha = max(0, min(255, instruction_alpha))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if not game_started:
                if event.key == pygame.K_SPACE:
                    game_started = True
            elif game_started and not game_over:
                if not fighter1.is_dead and not fighter2.is_dead:
                    if event.key == pygame.K_a:  # Fighter 1 Punch
                        fighter1.punch()
                        fighter2_hit_sound.play()
                        if fighter1.rect.colliderect(fighter2.rect):
                            fighter2.get_hit()
                    elif event.key == pygame.K_l:  # Fighter 2 Punch
                        fighter2.punch()
                        if fighter2.rect.colliderect(fighter1.rect):
                            fighter1.get_hit()
                            fighter1_hit_sound.play()
                    elif event.key == pygame.K_w:  # Fighter 1 Jump
                        fighter1.jump()
                    elif event.key == pygame.K_i:  # Fighter 2 Jump
                        fighter2.jump()
        elif event.type == pygame.KEYUP:
            if game_started and not game_over:
                if not fighter1.is_dead and not fighter2.is_dead:
                    if event.key == pygame.K_a and not (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]):  # Fighter 1 Idle
                        fighter1.idle()
                    elif event.key == pygame.K_l and not (keys[pygame.K_j] or keys[pygame.K_k]):  # Fighter 2 Idle
                        fighter2.idle()
        elif event.type == pygame.MOUSEBUTTONDOWN and game_over:
            mouse_pos = event.pos
            if main_menu_rect.collidepoint(mouse_pos):
               
                game_started = False
                game_over = False
                fighter1.health = 100
                fighter2.health = 100
                fighter1.is_dead = False
                fighter2.is_dead = False
                fighter1.idle()
                fighter2.idle()
            elif quit_rect.collidepoint(mouse_pos):
                running = False

    if not game_started:
        show_main_screen(screen, main_screen_background_images, background_animation_time, shake_offset, instruction_alpha)
    elif game_started and not game_over:

        keys = pygame.key.get_pressed()
        if not fighter1.is_dead:
            if keys[pygame.K_LEFT]:
                fighter1.walk(-1)
            elif keys[pygame.K_RIGHT]:
                fighter1.walk(1)
            else:
                if not fighter1.is_punching and fighter1.is_walking:
                    fighter1.idle()

        if not fighter2.is_dead:
            if keys[pygame.K_j]:
                fighter2.walk(-1)
            elif keys[pygame.K_k]:
                fighter2.walk(1)
            else:
                if not fighter2.is_punching and fighter2.is_walking:
                    fighter2.idle()
                    
      
        fighter1.apply_gravity()
        fighter2.apply_gravity()
        fighter1.update_animation(dt)
        fighter2.update_animation(dt)
        update_background(screen, background_images, background_animation_time)
        fighter1.draw(screen)
        fighter2.draw(screen)
      
       
             
        if fighter1.is_dead or fighter2.is_dead:
            if game_over_time is None:
                game_over_time = pygame.time.get_ticks()
            elif pygame.time.get_ticks() - game_over_time >= GAME_OVER_DELAY * 800:
                winner_text = "Player 1 Wins!" if fighter2.is_dead else "Player 2 Wins!"
                show_end_screen(screen, winner_text)
                game_state = "game_over"
                continue

       
        pygame.display.flip()
    elif game_over:
        main_menu_rect, quit_rect = show_end_screen(screen, winner_text)


pygame.quit()
sys.exit()  