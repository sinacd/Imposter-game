import os
import pickle 
import pygame
import random
from os import listdir
from os.path import isfile,join

pygame.init()
pygame.display.set_caption("Imposter")
RED= (255,0,0)
GREEN= (0,255,0)
BLACK= (0,0,0)
WHITE = (255,255,255)
FONT = pygame.font.SysFont('Futura',60)
FONT2= pygame.font.SysFont('Futura',30)
FPS=60
WIDTH,HEIGHT = 800,450
WIDTH_COF = 3
LEVEL_WIDTH = WIDTH * WIDTH_COF
PLAYER_VEL=1
GRAVITY = 1
TILE_SIZE = 45
ROWS = HEIGHT // TILE_SIZE
COLS = LEVEL_WIDTH // TILE_SIZE
print('ROWS',ROWS)
print('COLS',COLS)
TILE_TYPES = 21
level = 1


world_data = []
pickle_in = open(f'level{level}_data', 'rb')
world_data = pickle.load(pickle_in)
# for i in range(ROWS):
#     x = [-1] * COLS
#     world_data.append(x)
# for i in range(COLS-1):
#     x = [1] * COLS
#     world_data[ROWS-1] = x
#     y =[0] * COLS
#     world_data[ROWS-2] = y
# print(world_data)


window = pygame.display.set_mode((WIDTH,HEIGHT))

# ======================clases start============================
def flip(sprites):
    return [pygame.transform.flip(sprite,True,False) for sprite in sprites]
def load_sprite_sheet(dir1,dir2,width,height,direction=False,sacleX=64,scaleY=64):
    path = join("assets",dir1,dir2)
    imagenames = [f for f in listdir(path) if isfile(join(path,f))]
    all_sprites = {}
    for imagename in imagenames:
        sprite_sheet = pygame.image.load(join(path,imagename))
        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface  = pygame.Surface((width,height),pygame.SRCALPHA,32)
            rect = pygame.Rect(i*width,0,width,height)
            surface.blit(sprite_sheet,(0,0),rect)
            # sprites.append(surface)
            # sprites.append(pygame.transform.smoothscale_by(surface,(1.4,1.7)))
            if sacleX == 64 and scaleY == 64:
                sprites.append(pygame.transform.scale2x(surface))
            else:
                sprites.append(pygame.transform.scale(surface,(sacleX,scaleY)))
        if direction:
            all_sprites[imagename.replace(".png","")+"_right"] = sprites
            all_sprites[imagename.replace(".png","")+"_left"] = flip(sprites)
        else:
            all_sprites[imagename.replace(".png","")] = sprites
    return all_sprites

def get_block(size,bitmapcode = 0):
    path = [join("assets","Terrain","0.png"),join("assets","Terrain","1.png"),join("assets","alien","Archer","Arrow.png")]
    image = pygame.image.load(path[bitmapcode]).convert_alpha()
    surface = pygame.Surface((size,size),pygame.SRCALPHA,32)
    rect = pygame.Rect(0,0,size,size)
    surface.blit(image,(0,0),rect)
    return pygame.transform.scale(surface, (TILE_SIZE, TILE_SIZE))




class Player(pygame.sprite.Sprite):   # chanage to see difference later
    COLOR = (255,0,0)
    ANIMATION_DELAY = 5
    # SPRITES = load_sprite_sheet('MainCharacters','NinjaFrog',32,32,True)
    SPRITES = load_sprite_sheet('MainCharacters','VirtualGuy',32,32,True)
    def __init__(self,x,y,width,height):
        super().__init__()
        self.name = "Player"
        self.rect = pygame.Rect(x,y,width,height)
        self.x_vel = 0
        self.y_vel = 0
        self.direction = "right"
        self.fall_count = 0
        self.animation_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        self.health = 100
        self.max_health = self.health
        self.alive = True
    
    def make_hit(self):
        self.hit = True
        self.hit_count = 0
        
    def jump(self):
        self.y_vel = - 7
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count >= 1: # help to reset gravity after 2 jump
            self.fall_count = 0

    def draw(self,win,xOffset):
        # self.sprite = self.SPRITES['idle_'+self.direction][0]
        # self.sprite = self.SPRITES['amoung_'+self.direction][0]
        win.blit(self.sprite,(self.rect.x -xOffset ,self.rect.y))
        pygame.draw.rect(win,BLACK,(10-2 ,10-2 ,150 + 4 ,20+4))
        pygame.draw.rect(win,RED,(10 ,10 ,150,20))
        ratio = self.health / self.max_health
        pygame.draw.rect(win,GREEN,(10 ,10 ,150 * ratio ,20))
    def move(self,dx,dy,collision = True):
        self.rect.x += dx
        self.rect.y += dy
    def antimove(self,dx,dy,collision = True):
        self.rect.x -= dx
        self.rect.y -= dy
    
    def loop(self,FPS): # constant moving with a calling move in a loop even if vel is 0
        self.y_vel+= min(1,(self.fall_count / FPS)*GRAVITY)
        self.move(self.x_vel,self.y_vel)
        if self.hit:
            self.hit_count +=1
        if self.hit_count > FPS * 2 :
            self.hit = False
            self.hit_count = 0
            self.health -= 25
        if self.health <= 0:
                self.health = 0
                self.alive = False
        if self.rect.y > HEIGHT:
            print(self.rect.x,self.rect.y)
            self.rect.y = 0


        self.fall_count += 1
        self.update_sprite()
        
        
    def update_sprite(self):
        sprite_sheet = 'idle'
        if self.hit:
            sprite_sheet = 'hit'
        elif self.y_vel < 0:
            if self.jump_count == 1:
               sprite_sheet = 'jump'
            elif self.jump_count == 2:
                sprite_sheet = 'double_jump'
        elif self.y_vel > GRAVITY:
           sprite_sheet = 'fall'
        elif self.x_vel != 0 and not (self.rect.right + self.x_vel > LEVEL_WIDTH or self.rect.left < abs(self.x_vel)):
           sprite_sheet = 'run'
        # if self.rect.right + self.x_vel > LEVEL_WIDTH:
        #     sprite_sheet = ''
        # if self.rect.left + self.x_vel < 0 or self.rect.right + self.x_vel > WIDTH:
        #     sprite_sheet = 'idle'
        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = ((self.animation_count // self.ANIMATION_DELAY) % len(sprites))
        self.sprite = sprites[sprite_index]
        self.animation_count +=1
        self.update()
    
    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x,self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)


   
   
    def moveRight(self,vel): # sets the speed
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
    def moveLeft(self,vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0
    def hit_head(self):
        self.count = 0
        self.y_vel *= -1


class Enemy(Player):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.ANIMATION_DELAY = 5
        self.SPRITES = load_sprite_sheet('alien','Archer',128,128,True,128,128)
        self.name = "Enemy"
        self.last_sprite_sheet = "run"
        self.move_counter = 0
        self.move_pause = False
        self.move_pause_counter = 0
        self.vision = pygame.Rect(0,0,150,20)
        self.shoot = False
        self.shoot_count = 70
        self.first_shot = True
        self.collided_left = False
        self.collided_right = False

    def shooting(self):
        if self.shoot_count == 0:
            self.shoot_count = 70
            if self.direction == "right":
                return Bullet(self.rect.centerx+(0.6*self.rect.size[0]*(1)),self.rect.centery,1)
            else:
                return Bullet(self.rect.centerx+(0.6*self.rect.size[0]*(-1)),self.rect.centery,-1)
        else:
            self.shoot_count -= 1
            return -1
    
    def draw(self,win,xOffset):
        # self.sprite = self.SPRITES['idle_'+self.direction][0]
        # self.sprite = self.SPRITES['amoung_'+self.direction][0]
        win.blit(self.sprite,(self.rect.x -xOffset ,self.rect.y))
        # pygame.draw.rect(win,RED,self.vision)
    def ai(self):
        if self.alive :
            # if self.vision.colliderect

                if not self.move_pause:
                    if  random.randint(0,400) == 69:
                        self.move_pause = True
                        self.move_pause_counter = 120
                    if self.direction == "right" :
                        self.moveRight(PLAYER_VEL)
                        self.vision.center = (self.rect.centerx + 75   ,self.rect.centery+20)
                    elif self.direction == "left":
                        self.moveLeft(PLAYER_VEL)
                        self.vision.center = (self.rect.centerx - 75   ,self.rect.centery+20)
                    self.ai_incrementer()
                else:
                    self.move_pause_counter -= 1
                    if self.move_pause_counter <= 0:
                        self.move_pause = False
                
    def ai_wall_bang(self):
        if self.direction == "right":
            self.direction = "left"
            self.move_counter = 0
        elif self.direction == "left":
            self.direction = "right"
            self.move_counter = 0
    def ai_incrementer(self):
        self.move_counter += 1
        if self.move_counter > FPS * 3 :
            self.ai_wall_bang()





    def update_sprite(self):
        sprite_sheet = 'run'
        if self.shoot:
            sprite_sheet = 'shoot'
        elif self.move_pause:
            sprite_sheet = 'idle'
        elif self.hit:
            sprite_sheet = 'run'
        elif self.y_vel < 0:
            if self.jump_count == 1:
               sprite_sheet = 'jump'
            elif self.jump_count == 2:
                sprite_sheet = 'jump'
        elif self.y_vel >= GRAVITY:
           sprite_sheet = 'jump'
        elif self.x_vel != 0 and not (self.rect.right + self.x_vel > LEVEL_WIDTH or self.rect.left < abs(self.x_vel)):
           sprite_sheet = 'run'
        if sprite_sheet != self.last_sprite_sheet:
            self.animation_count = 0
        self.last_sprite_sheet = sprite_sheet
        # if self.rect.right + self.x_vel > LEVEL_WIDTH:
        #     sprite_sheet = ''
        # if self.rect.left + self.x_vel < 0 or self.rect.right + self.x_vel > WIDTH:
        #     sprite_sheet = 'idle'
        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = ((self.animation_count // self.ANIMATION_DELAY) % len(sprites))
        self.sprite = sprites[sprite_index]
        self.animation_count +=1
        self.update()
    
    def loop(self,FPS,offset_x): # constant moving with a calling move in a loop even if vel is 0
        self.y_vel+= min(1,(self.fall_count / FPS)*GRAVITY)
        self.move(self.x_vel,self.y_vel)
        if self.hit:
            self.hit_count +=1
        if self.hit_count > FPS * 2 :
            self.hit = False
            self.hit_count = 0
            self.health -= 25
        # if self.shoot_count > 0 and not self.first_shot :
        #     self.shoot_count -= 1
        if self.health <= 0:
            self.health = 0
            self.alive = False
        self.fall_count += 1
        self.update_sprite()
    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x,self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    
    
class Bullet(pygame.sprite.Sprite):
    def __init__(self,x,y,direction):
        super().__init__() 
        self.speed = 10
        self.direction = direction
        self.rect = pygame.Rect(x,y,TILE_SIZE,TILE_SIZE)
        self.image = pygame.Surface((TILE_SIZE,TILE_SIZE),pygame.SRCALPHA)
        self.width=TILE_SIZE
        self.height=TILE_SIZE
        self.name = "aa"
        block = get_block(48,2)
        self.image.blit(block,(0,0))
        self.mask = pygame.mask.from_surface(self.image)
    def draw(self,win,xOffset=10):
        win.blit(self.image,(self.rect.x - xOffset ,self.rect.y))
    def update(self):
        self.rect.x += self.speed * self.direction
        # if self.rect.right < 0 or self.rect.left > WIDTH:
        #     self.kill()
  
#=========================================        
class Object(pygame.sprite.Sprite):
    def __init__(self,x,y,width,height,name=None):
        super().__init__()
        self.rect = pygame.Rect(x,y,width,height)
        self.image = pygame.Surface((width,height),pygame.SRCALPHA)
        self.width=width
        self.height=height
        self.name = name
        
    def draw(self,win,xOffset):
        win.blit(self.image,(self.rect.x - xOffset ,self.rect.y))


class Block(Object):
    def __init__(self, x, y, size,code= 0):
        super().__init__(x, y, size,size)
        block = get_block(size,code)
        self.image.blit(block,(0,0))
        self.mask = pygame.mask.from_surface(self.image)
class Fire(Object):
    ANIMATION_DELAY= 5
    def __init__(self, x, y, width, height, name=None):
        super().__init__(x, y, width, height, "Fire")
        self.fireSprite = load_sprite_sheet("Traps","Fire",width,height,False)
        self.image = self.fireSprite["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"
    def off(self):
        self.animation_name = "off"
    def loop(self):
        sprites = self.fireSprite[self.animation_name]
        sprite_index = ((self.animation_count // self.ANIMATION_DELAY) % len(sprites))
        self.image = sprites[sprite_index]
        self.animation_count +=1
        self.rect = self.image.get_rect(topleft=(self.rect.x,self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)
        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count=0




# ======================clases end============================
# ======================funcs start============================
def getBackground(name):
    bgImage = pygame.image.load(join("assets","Background","Ocean_6",name))
    _,_,bgImageWidth,bgImageHeight  = bgImage.get_rect()
    tiles =[]
    for i in range(LEVEL_WIDTH//bgImageWidth+1):
        for j in range(1):
            pos = (i*bgImageWidth,j*bgImageHeight)
            tiles.append(pos)
    
    return tiles,bgImage

def draw(window,tilesBackground,bgImage,yOffset=0,fromTop=True,player=None,repetition = 1,proxco = 1,objects =None, xOffset = 0):
    if fromTop:
        # window.blit(bgImage,(tilesBackground[0][0]-bg_scroll,tilesBackground[0][1]+yOffset))
        for x in range(repetition):
            window.blit(bgImage,(tilesBackground[x][0]- xOffset *proxco  ,tilesBackground[x][1]+yOffset))
    else:
        for tile in tilesBackground:
            window.blit(bgImage,(tile[0]- xOffset *proxco ,HEIGHT-bgImage.get_height()+yOffset))
    if player is not None:
        for obj in player:
            if type(obj) == type(pygame.sprite.Group()):
                for obj2 in obj:
                    obj2.draw(window,xOffset)
            else:
                obj.draw(window,xOffset)
    if objects is not None:
        for obj in objects:
            obj.draw(window , xOffset)
def handle_vertical_collision(player,objects,dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player,obj):
            if dy > 0 :
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0 :
                player.rect.top = obj.rect.bottom
                player.hit_head()
            collided_objects.append(obj)
    return collided_objects
def collide(player, objects, dx):
    player.move(dx, 0,False)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break

    player.move(-dx, 0,False)
    player.update()
    return collided_object


def vision_collide(player, enemies):
    bullets = []
    for obj in enemies:
        # print( obj.vision.colliderect(player.rect))
        if obj.vision.colliderect(player.rect) and player.alive:
            obj.shoot = True

            obj.move_pause = True
            # player.health -= 1
            bullet_temp = obj.shooting()
            if bullet_temp != -1:
                bullets.append(bullet_temp)
        else:
            obj.first_shot = True
            obj.shoot = False
    if bullets != []:
        print(bullets)
        return bullets
    else:
        return -1
    
def bullet_collide(player,bullets):
    list_collided_bullets = pygame.sprite.spritecollide(player,bullets,False)
    if list_collided_bullets != [] :
        for obj in list_collided_bullets:
            obj.kill()
            player.health -= 5

def handleMove(player,objects):
    keys = pygame.key.get_pressed()
    player.x_vel=0
    collide_left = collide(player, objects, -PLAYER_VEL * 8 * 3) 
    collide_right = collide(player, objects, PLAYER_VEL * 8 * 3)
    # print(collide_right)
    if  player.name == "Player" and keys[pygame.K_LEFT] and not collide_left and player.alive :
        player.moveLeft(PLAYER_VEL*3)
    elif  player.name == "Player" and keys[pygame.K_RIGHT] and not collide_right and player.alive :
        player.moveRight(PLAYER_VEL*3)
    elif  player.name == "Enemy"  and not collide_left and player.direction == 'left'  :
        player.ai()
    elif  player.name == "Enemy"  and not collide_right and player.direction == 'right' :
        player.ai()
    elif  player.name == "Enemy" and player.shoot == False:
        player.ai_incrementer()
    vertical_collide = handle_vertical_collision(player,objects,player.y_vel)
    to_check = [collide_left,collide_right,*vertical_collide]
    for obj in to_check:
        if obj and obj.name == "Fire":
            player.make_hit()

def text_show(window,text,font,text_color,x,y):
    img = font.render(text,True,text_color)
    window.blit(img,(x,y))



    


# ======================funcs end============================
def main(window):
    clock = pygame.time.Clock()
    tiles1,bgImage1 = getBackground("1.png")
    tiles2,bgImage2 = getBackground("12.png")
    tiles3,bgImage3 = getBackground("13.png")
    tiles4,bgImage4 = getBackground("14.png")
    player = Player(100,200,50,50)
    # enemy = Enemy(120, 100,50,50)
    enemy_group = pygame.sprite.Group()
    bullet_group = pygame.sprite.Group()
    blockSize = TILE_SIZE
    # blocks = [Block(i*blockSize,HEIGHT-blockSize,blockSize) for i in range(-WIDTH // blockSize ,WIDTH * 3 // blockSize)]
    # blocks = [Block(i*blockSize,HEIGHT-blockSize,blockSize) for i in range(-WIDTH // blockSize ,(LEVEL_WIDTH // blockSize)+1)]
    blocks2 = []
    for y, row in enumerate(world_data):
        for x , tile in enumerate(row):
            if tile == 0:
                blocks2.append(Block(x*TILE_SIZE,y*TILE_SIZE,blockSize,tile))
            elif tile == 1:
                blocks2.append(Block(x*TILE_SIZE,y*TILE_SIZE,blockSize,tile))
            elif tile == 2:
                enemy_group.add(Enemy(x*TILE_SIZE, y*TILE_SIZE-10,50,50))
    fire = Fire(350,HEIGHT - blockSize - 64,16,32)
    fire.on()
    objects = [*blocks2, Block(blockSize * 3, HEIGHT - blockSize * 2, blockSize),
               Block(blockSize * 5, HEIGHT - blockSize * 4, blockSize),fire]
    scroll_area_width = 300
    offset_x = 0
    run = True
    while run :
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2 and player.alive:
                    player.jump()



        player.loop(FPS)
        handleMove(player,objects)
        for enemy in enemy_group:
            enemy.loop(FPS,offset_x)
            handleMove(enemy,objects)
        vision_collide_temp = vision_collide(player,enemy_group)
        # ali =  Bullet(150,100,1)
        # bullet_group.add(ali)
        # print(vision_collide_temp)
        # print("yes")
        if vision_collide_temp != -1:
             for x in vision_collide_temp:
                 bullet_group.add(x)
       
        fire.loop()
        # handleMove(enemy,objects)
        draw(window,tiles1,bgImage1,0,False,repetition=WIDTH_COF,xOffset=offset_x)
        draw(window,tiles2,bgImage2,proxco=0.09,xOffset=offset_x)
        draw(window,tiles3,bgImage3,repetition=WIDTH_COF,proxco=0.2,xOffset=offset_x)
        draw(window,tiles4,bgImage4,-93,False,[player,enemy_group],repetition=WIDTH_COF,proxco=0.5,objects=objects,xOffset=offset_x)
        for bullet in bullet_group:
            bullet.update()
            bullet.draw(window,offset_x)
            bullet_collide(player,bullet_group)
   
        # pygame.display.update()
        
        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width and offset_x < LEVEL_WIDTH - WIDTH ) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width and offset_x >  abs(player.x_vel)) and player.x_vel < 0):
            offset_x += player.x_vel
            # print(offset_x)
        elif player.rect.left < PLAYER_VEL:
            player.antimove(-PLAYER_VEL,0)
        elif player.rect.right + PLAYER_VEL > LEVEL_WIDTH:
            # player.antimove(PLAYER_VEL ,0)
            player.alive = False
            text_show(window,f'Congrats!',FONT,WHITE,300,160)
            text_show(window,f'You have completed the game! Thanks for playing!',FONT2,WHITE,150,250)
        elif player.alive == False :
            text_show(window,f'You Lose!',FONT,WHITE,300,160)
        pygame.display.update()
        


            
        
    pygame.quit()
    quit()





if __name__== "__main__":
    main(window)
