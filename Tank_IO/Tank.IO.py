'''
   Project Title: Tank.IO - A 2D Top-Down Tank Battle Game
   Description: A 2D top-down tank battle game where players navigate a maze-like arena, strategically maneuvering their tanks to outwit and outshoot their opponents.                 
   Players can choose between keyboard controls or gamepad input, adding versatility to the gameplay experience.                                                                                                                                #
   
   Developed by: JCMIrish                                                                                   
   GitHub: https://github.com/JCMIrish        
   License: MIT                                                                                                    
   Credits:                                                                                                     
   - Shooting & Hit SFX by: Muncheybobo // https://opengameart.org/content/retro-shooter-sound-effects          
   - Music OSTs & Jingles by: SketchyLogic // https://opengameart.org/content/nes-shooter-music-5-tracks-3-jingles 
   - PYGAME pip used for development: pygame team // https://www.pygame.org                                        
   - Guides used along development: Coding With Russ // https://www.youtube.com/@CodingWithRuss                    
'''


import pygame as pg
from pygame import mixer
import os
import csv
import button

#initalize
pg.init()
mixer.init()
pg.joystick.init()

joy = False # player one joystick
joy_two = False # player two joystick

#joystick Counter
joysticks = [pg.joystick.Joystick(x) for x in range (pg.joystick.get_count())]
for joystick in joysticks:
    #print(joystick.get_id())
    if pg.joystick.get_count() == 1: #if count met enable joystick
        joy = True
    if pg.joystick.get_count() == 2:
        joy_two = True
if joy == False and joy_two == False: # if neither joystick inputted
    print("Keyboard enabled") #prints into terminal

#clock
clock = pg.time.Clock()

#screen sizes
SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

#display
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption('Tank.IO') #Adds window caption


#define game variables
ROWS = 16 #total rows
COLS = 20 #total cols 
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 11 #total tiles
level = 1 #level start
start_game = False #main menu
run = True #main game loop
play_win_sound = True #sets win sound to play

#actions
player_one_shoot = False
player_two_shoot = False

#keyboard inputs
#player one
player_left = False
player_right = False
player_up = False
player_down = False
#player two
player_two_left = False
player_two_right = False
player_two_up = False
player_two_down = False

#audio
#gameplay sfx
shot_sfx = pg.mixer.Sound('audio/shoot.mp3')
shot_sfx.set_volume(0.15)
hit_sfx = pg.mixer.Sound('audio/hit.mp3')
hit_sfx.set_volume(0.17)
#jingles
start_jingle = pg.mixer.Sound('audio/Intro_Jingle.wav')
start_jingle.set_volume(0.20) 
start_jingle.play() # plays on startup
button_jingle = pg.mixer.Sound('audio/confirmbeep.wav')
button_jingle.set_volume(0.35)
win_jingle = pg.mixer.Sound('audio/Win_Jingle.wav')
win_jingle.set_volume(0.25)
#Menu Soundtrack function
def menu_ost():
        pg.mixer.music.load('audio/soundtrack/8BitMetal.wav')
        pg.mixer.music.set_volume(0.08)
        pg.mixer.music.play(-1, 0.0, 1000)
menu_ost()
#soundtrack function
def soundtrack(): 
        pg.mixer.music.load('audio/soundtrack/OST.ogg')
        pg.mixer.music.set_volume(0.08)
        pg.mixer.music.play(-1, 0.0, 1000)

#load Images
#button images
start_img = pg.image.load('img/start_btn.png').convert_alpha()
exit_img = pg.image.load('img/exit_btn.png').convert_alpha()
restart_img = pg.image.load('img/restart_btn.png').convert_alpha()
#background image
bg_img = pg.image.load('img/bg/tank_io_bg.png').convert_alpha()
#stored level tiles
img_list = []
for x in range(TILE_TYPES):
    img = pg.image.load(f'img/Tile/{x}.png')
    img = pg.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)
#bullet
bullet_img = pg.image.load('img/bullet.png')


#define colors
BG = (50, 50, 50)
Black = (0,0,0)
White = (255, 255, 255)
Red = (255, 20, 20)
Green = (20, 255, 20)

#define font
Win_text = pg.font.SysFont('Futura', 90)
title_text = pg.font.SysFont('Futura', 180)
caption_text = pg.font.SysFont('Futura', 40)
reg_text = pg.font.SysFont('Futura', 25)
credits_text = pg.font.SysFont('Futura', 18)

#text drawing function
def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))

#rectangle drawing function
def draw_rect(length, height, rect_col, x, y, outline_col):
    surface = pg.Surface([length, height])
    surface_outline = pg.Surface([length + 20, height + 20])
    surface_outline.fill(outline_col)
    screen.blit(surface_outline, (x - 10, y - 10))
    surface.fill(rect_col)
    screen.blit(surface, (x, y))

#background function
def draw_bg():
    screen.fill(BG)
    screen.blit(bg_img, (0, 0))

#restarts level function
def reset_level():
    bullet_group.empty() #empties group

    #resets tiles
    data = []
    for row in range(ROWS):
        r = [-1] * COLS
        data.append(r)

    return data


#player class
class Player(pg.sprite.Sprite):

    def __init__(self, char_type, x, y, scale):
        pg.sprite.Sprite.__init__(self)
        self.char_type = char_type 
        self.shoot_cooldown = 0
        self.speed = 2 #player speed
        #Health
        self.health = 100 #max health
        self.max_health = self.health 
        #image manipulation
        self.flip = False #flips player horizontally
        self.direction = 1 # direction check
        self.vertical = False #flips player vertically
        #animations
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pg.time.get_ticks()
        #Load all images
        animation_types = ['x_move', 'UP', 'DOWN', 'death'] 
        for animation in animation_types:
            #reset temp list
            temp_list = []
            #count files
            num_of_frames = len(os.listdir(f'img/tank/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pg.image.load(f'img/tank/{self.char_type}/{animation}/{i}.png')
                img = pg.transform.scale(img, (int(img.get_width() * scale), img.get_height() * scale))
                temp_list.append(img)
            self.animation_list.append(temp_list)
        
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()


    def update(self): #updates player
        self.update_animation()
        self.check_alive()
        #update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1


    def move(self, x_speed, y_speed): #player movement
        dx = 0
        dy = 0

        if x_speed > 0:
            #RIGHT
            dx = self.speed 
            self.flip = False # keeps sprite right
            self.direction = 1 # bullet direction
            self.vertical = False # checks vertical movement
            
        elif x_speed < 0:
            #LEFT
            dx = -self.speed 
            self.flip = True # flip tank sprite
            self.direction = -1 # inverts bullet direction
            self.vertical = False

        if y_speed > 0:
            #DOWN
            dy = self.speed 
            self.direction = 1 
            self.vertical = True 

        elif y_speed < 0:
            #UP
            dy = -self.speed
            self.direction = -1
            self.vertical = True
        
        
        #check tile collision
        for tile in world.obstacle_list:
            #check x collision
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
            #check y collision
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                dy = 0

        #check if player hit screen boundaries and stops them
        if self.char_type == 'P1' or self.char_type == "P2":
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0
            if self.rect.top + dy < 0 or self.rect.bottom + dy > SCREEN_HEIGHT:
                dy = 0


        #Update rectangle position
        self.rect.x += dx
        self.rect.y += dy


    def shoot(self):
        if self.shoot_cooldown == 0:
            self.shoot_cooldown = 60 #interval between shots
            shot_sfx.play()
            if self.vertical == False: #horizontal shooting
                bullet = Bullet(self.rect.centerx + (0.74 * self.rect.size[0] * self.direction), self.rect.centery, self.direction, False)
                bullet_group.add(bullet)
            if self.vertical == True: #vertical shooting
                bullet = Bullet(self.rect.centerx, self.rect.centery + (0.74 * self.rect.size[0] * self.direction), self.direction, True)
                bullet_group.add(bullet) 
  

    def update_animation(self):
        #update animation
        ANIMATION_COOLDOWN = 30
        #Update image depending on frame
        self.image = self.animation_list[self.action][self.frame_index]
        #check if enough time has passed
        if pg.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pg.time.get_ticks()
            self.frame_index += 1
        #if animation run out reset
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0


    def update_action(self, new_action):
        #check if action different
        if new_action != self.action:
            self.action = new_action
            #update animation settings
            self.frame_index = 0
            self.update_time = pg.time.get_ticks()
  

    #Ensuring player is alive
    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.update_action(3)

    #Draws player
    def draw(self):
        screen.blit(pg.transform.flip(self.image, self.flip, False), self.rect) 


#World Class
class World():
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        #iterate through level values
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 8: #identifies tiles
                        self.obstacle_list.append(tile_data)
                    elif tile == 9: # Create Player One
                        player = Player('P1', x * TILE_SIZE, y * TILE_SIZE, 1.20)
                    elif tile == 10: # Create Player Two
                        player_two = Player('P2', x * TILE_SIZE, y * TILE_SIZE, 1.20)
        
        return player, player_two

    def draw(self):
        for tile in self.obstacle_list:
            screen.blit(tile[0], tile[1])



#Bullet Class
class Bullet(pg.sprite.Sprite):
    def __init__(self, x, y, direction, vertical):
        pg.sprite.Sprite.__init__(self)
        self.speed = 6 #bullet speed
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        #directional shooting
        self.direction = direction
        #Checks for vertical movement
        self.vertical = vertical


    def update(self):
        #Bullet movement
        #Horizontal shooting
        if self.vertical == False:
            self.rect.x += (self.direction * self.speed)
        #vertical shooting    
        if self.vertical == True:
            self.rect.y += (self.direction * self.speed)

        #check if bullet off screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()
        if self.rect.top < 0 or self.rect.bottom > SCREEN_HEIGHT:
            self.kill()


        #Check level collision
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        #Check bullet collision with player
        if pg.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 20
                hit_sfx.play()
                print('Player 1 HP:' , player.health)
                self.kill()
        if pg.sprite.spritecollide(player_two, bullet_group, False):
            if player_two.alive:
                player_two.health -= 20
                hit_sfx.play()
                print('Player 2 HP:' , player_two.health)
                self.kill()



#create buttons
start_button = button.Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 - 100, start_img, 1)
exit_button = button.Button(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT //2 + 50, exit_img, 1)
restart_button = button.Button(SCREEN_WIDTH // 2 - 170, SCREEN_HEIGHT // 2 - 90, restart_img, 3)
#sprite group
bullet_group = pg.sprite.Group()



#create empty tile list
world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)
#Load level data to create world
with open(f'level{level}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)
world = World()
player, player_two = world.process_data(world_data)


#game loop
while run:

    clock.tick(60) #runs at 60FPS

    if start_game == False:
        #draw main menu
        screen.fill(BG)
        draw_rect(SCREEN_WIDTH - 300, 110,(Black), SCREEN_WIDTH // 2 - 240, SCREEN_HEIGHT // 2 - 250, (White)) #title background
        draw_text("Tank.IO", title_text, (White), SCREEN_WIDTH // 2 - 220, SCREEN_HEIGHT // 2 - 250) #title text

        #controls text
        draw_rect(200, 400,(Black), SCREEN_WIDTH // 2 - 380, SCREEN_HEIGHT // 2 - 100, (White))
        draw_text("Controls", caption_text, (White), SCREEN_WIDTH // 2 - 375, SCREEN_HEIGHT // 2 - 95)
        draw_text("Mouse = Select", reg_text, (White), SCREEN_WIDTH // 2 - 375, SCREEN_HEIGHT // 2 - 65)
        draw_text("'ESC' key = Exit", reg_text, (White), SCREEN_WIDTH // 2 - 375, SCREEN_HEIGHT // 2 - 40)
        #joystick controls
        draw_text("Left Stick = Move", reg_text, (White), SCREEN_WIDTH // 2 - 375, SCREEN_HEIGHT // 2 - 15) 
        draw_text("'A' button = Shoot", reg_text, (White), SCREEN_WIDTH // 2 - 375, SCREEN_HEIGHT // 2 + 10)
        #player one controls
        draw_text("Player One:", reg_text, (Green), SCREEN_WIDTH // 2 - 375, SCREEN_HEIGHT // 2 + 33) 
        draw_text("'W,A,S,D' keys = Move", reg_text, (White), SCREEN_WIDTH // 2 - 370, SCREEN_HEIGHT // 2 + 55)
        draw_text("'X' key = Shoot", reg_text, (White), SCREEN_WIDTH // 2 - 370, SCREEN_HEIGHT // 2 + 77)
        #player two controls
        draw_text("Player Two:", reg_text, (Red), SCREEN_WIDTH // 2 - 375, SCREEN_HEIGHT // 2 + 103)
        draw_text("'I,J,K,L' keys = Move", reg_text, (White), SCREEN_WIDTH // 2 - 370, SCREEN_HEIGHT // 2 + 123)
        draw_text("'M' key = Shoot", reg_text, (White), SCREEN_WIDTH // 2 - 370, SCREEN_HEIGHT // 2 + 147)

        #credits text
        draw_rect(650, 130,(Black), SCREEN_WIDTH // 2 - 380, SCREEN_HEIGHT // 2 + 180, (White))
        draw_text("Credits", caption_text, (White), SCREEN_WIDTH // 2 - 375, SCREEN_HEIGHT // 2 + 185)
        draw_text("Shooting & Hit SFX by: Muncheybobo // https://opengameart.org/content/retro-shooter-sound-effects", credits_text, (White), SCREEN_WIDTH // 2 - 375, SCREEN_HEIGHT // 2 + 220)
        draw_text("Music OSTs & Jingles by: SketchyLogic // https://opengameart.org/content/nes-shooter-music-5-tracks-3-jingles", credits_text, (White), SCREEN_WIDTH // 2 - 375, SCREEN_HEIGHT // 2 + 240)
        draw_text("PYGAME pip used for development: pygame team // https://www.pygame.org", credits_text, (White), SCREEN_WIDTH // 2 - 375, SCREEN_HEIGHT // 2 + 260)
        draw_text("Guides used along development: Coding With Russ // https://www.youtube.com/@CodingWithRuss", credits_text, (White), SCREEN_WIDTH // 2 - 375, SCREEN_HEIGHT // 2 + 280)
        
        #buttons  
        if start_button.draw(screen): 
            button_jingle.play()
            start_game = True # initialize game
            pg.mixer.music.stop()
            soundtrack() #start game soundtrack
        if exit_button.draw(screen):               
            run = False #close game

    else:
     
        #Update Background
        draw_bg()
        #draws map
        world.draw()

        #Updates players
        player.update()
        player_two.update()

        #draw players
        player.draw()
        player_two.draw()


        #update and draw groups
        bullet_group.update()
        bullet_group.draw(screen)
    
        if player.alive:
            #shooting
            if player_one_shoot:
                player.shoot()

            if joy == False: #Check for controller input
                x_speed = 0
                y_speed = 0

                if player_right:
                    x_speed = 1
                if player_left:
                    x_speed = -1
                if player_up:
                    y_speed = -1
                if player_down:
                    y_speed = 1

            if joy == True: #if joystick detected enable
                x_speed = round(pg.joystick.Joystick(0).get_axis(0)) 
                y_speed = round(pg.joystick.Joystick(0).get_axis(1))
            elif joy == False:
                pass

            player.move(x_speed, y_speed) #updates move function
     
            #Actions
            if x_speed > 0 or x_speed < 0:
                player.update_action(0) # Horizontal
            if y_speed < 0:
                player.update_action(1) # UP
            if y_speed > 0:
                player.update_action(2) # DOWN

        else:
            pg.mixer.music.fadeout(5) #fades soundtrack
            draw_rect(SCREEN_WIDTH - 280, 65,(Black), SCREEN_WIDTH // 2 - 235, SCREEN_HEIGHT // 2 - 200, (White)) #win text background
            draw_text("Player Two Wins!", Win_text, (Red), SCREEN_WIDTH // 2 - 235, SCREEN_HEIGHT // 2 - 200) # win text background

            if play_win_sound: #plays win jingle
                play_win_sound = False
                win_jingle.play(0)

            if restart_button.draw(screen):
                play_win_sound = True #resets win sound
                win_jingle.fadeout(10) #fades jingle if restarted quickly
                button_jingle.play() #button jingle
                soundtrack() #restart music
                world_data = reset_level() #resets all data
                #Load level data to create world
                with open(f'level{level}_data.csv', newline='') as csvfile:
                    reader = csv.reader(csvfile, delimiter=',')
                    for x, row in enumerate(reader):
                        for y, tile in enumerate(row):
                            world_data[x][y] = int(tile)
                world = World()
                player, player_two = world.process_data(world_data)
            
            if exit_button.draw(screen):               
                run = False #closes game if exit pressed

        if player_two.alive:
            #shooting
            if player_two_shoot:
                player_two.shoot()

            if joy_two == False: #Check for controller input
                x_speed = 0
                y_speed = 0

                if player_two_right:
                    x_speed = 1
                if player_two_left:
                    x_speed = -1
                if player_two_up:
                    y_speed = -1
                if player_two_down:
                    y_speed = 1

            if joy_two == True: #if joystick detected enable
                x_speed = round(pg.joystick.Joystick(1).get_axis(0)) 
                y_speed = round(pg.joystick.Joystick(1).get_axis(1))
            elif joy_two == False:
                pass

            player_two.move(x_speed, y_speed) #updates move function

            #Actions
            if x_speed > 0 or x_speed < 0:
                player_two.update_action(0) # Horizontal
            if y_speed < 0:
                player_two.update_action(1) # UP
            if y_speed > 0:
                player_two.update_action(2) # DOWN

        else:
            pg.mixer.music.fadeout(5) #fades soundtrack
            draw_rect(SCREEN_WIDTH - 280, 65,(Black), SCREEN_WIDTH // 2 - 235, SCREEN_HEIGHT // 2 - 200, (White)) # win text background
            draw_text("Player One Wins!", Win_text, (Green), SCREEN_WIDTH // 2 - 235, SCREEN_HEIGHT // 2 - 200) #win text
            
            if play_win_sound: #plays win jingle
                play_win_sound = False
                win_jingle.play(0)

            if restart_button.draw(screen):
                play_win_sound = True #resets win sound
                win_jingle.fadeout(10) #fades jingle if restarted quickly
                button_jingle.play() #button press jingle
                soundtrack() # restart music
                world_data = reset_level() #resets all data
                #Load level data to create world
                with open(f'level{level}_data.csv', newline='') as csvfile:
                    reader = csv.reader(csvfile, delimiter=',')
                    for x, row in enumerate(reader):
                        for y, tile in enumerate(row):
                            world_data[x][y] = int(tile)
                world = World()
                player, player_two = world.process_data(world_data)
            
            if exit_button.draw(screen):               
                run = False #closes game if exit pressed



    #event handler
    for event in pg.event.get():
        if event.type == pg.QUIT: #Closes game if the 'X' is clicked
            run = False
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE: #Closes game is 'ESC" pressed
                run = False
        #Joystick button down
        if event.type == pg.JOYBUTTONDOWN:
            if joy == True: #Check controller instance
                if pg.joystick.Joystick(0).get_button(0): #checks for button input
                    player_one_shoot = True
            if joy_two == True:
                if pg.joystick.Joystick(1).get_button(0):
                    player_two_shoot = True
        #Joystick button released
        if event.type == pg.JOYBUTTONUP:
            if joy == True:
                player_one_shoot = False
            if joy_two == True:
                player_two_shoot = False

        #Player One keyboard inputs
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_w: #'W' Up
                player_up = True
            if event.key == pg.K_a: #'A' LEFT
                player_left = True
            if event.key == pg.K_s: #'S' DOWN
                player_down = True
            if event.key == pg.K_d: #'D' RIGHT
                player_right = True
            if event.key == pg.K_x: #'X' SHOOT
                player_one_shoot = True

        if event.type == pg.KEYUP:
            if event.key == pg.K_w:
                player_up = False
            if event.key == pg.K_a:
                player_left = False
            if event.key == pg.K_s:
                player_down = False
            if event.key == pg.K_d:
                player_right = False
            if event.key == pg.K_x:
                player_one_shoot = False
        
        #Player Two keyboard inputs
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_i: #'I' UP
                player_two_up = True
            if event.key == pg.K_j: #'J' LEFT
                player_two_left = True
            if event.key == pg.K_k: #'K' DOWN
                player_two_down = True
            if event.key == pg.K_l: #'L" RIGHT
                player_two_right = True
            if event.key == pg.K_m: #'M' SHOOT
                player_two_shoot = True

        if event.type == pg.KEYUP:
            if event.key == pg.K_i:
                player_two_up = False
            if event.key == pg.K_j:
                player_two_left = False
            if event.key == pg.K_k:
                player_two_down = False
            if event.key == pg.K_l:
                player_two_right = False
            if event.key == pg.K_m:
                player_two_shoot = False
            

        if event.type == pg.JOYDEVICEADDED: # Allows device hotplugging
            joysticks = [pg.joystick.Joystick(x) for x in range (pg.joystick.get_count())]
            #print(pg.joystick.get_count())
            print("Joystick Connected")
            if pg.joystick.get_count() == 1 or pg.joystick.get_count() == 2:
                joy = True
            if pg.joystick.get_count() == 2:
                joy_two = True
        if event.type == pg.JOYDEVICEREMOVED: # Removes device
            joysticks = [pg.joystick.Joystick(x) for x in range (pg.joystick.get_count())]
            print("Joystick Disconnected")
            if pg.joystick.get_count() != 1:
                joy = False
            if pg.joystick.get_count() != 2:
                joy_two = False
        

    pg.display.update()

pg.quit()
