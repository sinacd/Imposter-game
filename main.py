import os 
import pygame
import math
from os import listdir
from os.path import isfile,join

pygame.init()
pygame.display.set_caption("Imposter")

FPS=60
WIDTH,HEIGHT = 800,450
WIDTH_COF = 3
LEVEL_WIDTH = WIDTH * WIDTH_COF
PLAYER_VEL=3
GRAVITY = 1
window = pygame.display.set_mode((WIDTH,HEIGHT))

# ======================clases start============================
def flip(sprites):
    return [pygame.transform.flip(sprite,True,False) for sprite in sprites]
def load_sprite_sheet(dir1,dir2,width,height,direction=False):
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
            sprites.append(pygame.transform.scale2x(surface))
        if direction:
            all_sprites[imagename.replace(".png","")+"_right"] = sprites
            all_sprites[imagename.replace(".png","")+"_left"] = flip(sprites)
        else:
            all_sprites[imagename.replace(".png","")] = sprites
    return all_sprites

def get_block(size):
    path = join("assets","Terrain","Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size,size),pygame.SRCALPHA,32)
    rect = pygame.Rect(96,130,size,size)
    surface.blit(image,(0,0),rect)
    return pygame.transform.scale2x(surface)




class Player(pygame.sprite.Sprite):   # chanage to see difference later
    COLOR = (255,0,0)
    ANIMATION_DELAY = 5
    # SPRITES = load_sprite_sheet('MainCharacters','NinjaFrog',32,32,True)
    SPRITES = load_sprite_sheet('MainCharacters','VirtualGuy',32,32,True)
    def __init__(self,x,y,width,height):
        super().__init__()
        self.rect = pygame.Rect(x,y,width,height)
        self.x_vel = 0
        self.y_vel = 0
        self.direction = "right"
        self.fall_count = 0
        self.animation_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
    
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
        elif self.x_vel != 0:
           sprite_sheet = 'run'
        # if self.rect.left + self.x_vel < 0 or self.rect.right + self.x_vel > WIDTH:
        #     sprite_sheet = 'idle'
        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = ((self.animation_count // self.ANIMATION_DELAY) % len(sprites))
        self.sprite = sprites[sprite_index]
        self.animation_count +=1
        self.update()
    
    def update(self):
        pass
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
    def __init__(self, x, y, size):
        super().__init__(x, y, size,size)
        block = get_block(size)
        self.image.blit(block,(0,0))
        self.mask = pygame.mask.from_surface(self.image)
class Fire(Object):
    ANIMATION_DELAY= 5
    def __init__(self, x, y, width, height, name=None):
        super().__init__(x, y, width, height, "Fire")
        self.fireSprite = load_sprite_sheet("Traps","Fire",width,height)
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
        player.draw(window,xOffset)
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



def handleMove(player,objects):
    keys = pygame.key.get_pressed()
    player.x_vel=0
    collide_left = collide(player, objects, -PLAYER_VEL * 4)
    collide_right = collide(player, objects, PLAYER_VEL * 4)
    if keys[pygame.K_LEFT] and not collide_left:
        player.moveLeft(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.moveRight(PLAYER_VEL)
    vertical_collide = handle_vertical_collision(player,objects,player.y_vel)
    to_check = [collide_left,collide_right,*vertical_collide]
    for obj in to_check:
        if obj and obj.name == "Fire":
            player.make_hit()


# ======================funcs end============================
def main(window):
    clock = pygame.time.Clock()
    tiles1,bgImage1 = getBackground("1.png")
    tiles2,bgImage2 = getBackground("12.png")
    tiles3,bgImage3 = getBackground("13.png")
    tiles4,bgImage4 = getBackground("14.png")
    player = Player(100, 100,50,50)
    blockSize = 96
    # blocks = [Block(i*blockSize,HEIGHT-blockSize,blockSize) for i in range(-WIDTH // blockSize ,WIDTH * 3 // blockSize)]
    blocks = [Block(i*blockSize,HEIGHT-blockSize,blockSize) for i in range(-WIDTH // blockSize ,WIDTH * 3 // blockSize)]
    fire = Fire(250,HEIGHT - blockSize - 64,16,32)
    fire.on()
    objects = [*blocks, Block(blockSize * 3, HEIGHT - blockSize * 2, blockSize),
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
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()



        player.loop(FPS)
        fire.loop()
        handleMove(player,objects)
        draw(window,tiles1,bgImage1,0,False,repetition=WIDTH_COF,xOffset=offset_x)
        draw(window,tiles2,bgImage2,proxco=0.09,xOffset=offset_x)
        draw(window,tiles3,bgImage3,repetition=WIDTH_COF,proxco=0.2,xOffset=offset_x)
        draw(window,tiles4,bgImage4,-93,False,player,repetition=WIDTH_COF,proxco=0.5,objects=objects,xOffset=offset_x)
   
        pygame.display.update()
        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width and offset_x < LEVEL_WIDTH - WIDTH ) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width and offset_x >  abs(player.x_vel)) and player.x_vel < 0):
            offset_x += player.x_vel
            print(offset_x)
        elif player.rect.left < PLAYER_VEL:
            player.antimove(-PLAYER_VEL,0)
        elif player.rect.right + PLAYER_VEL > LEVEL_WIDTH:
            player.antimove(PLAYER_VEL,0)

            
        
    pygame.quit()
    quit()





if __name__== "__main__":
    main(window)
