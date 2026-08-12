import pygame
import time
import random
pygame.font.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1300, 1000
WIN =  pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gooner Quest III")

BG = pygame.transform.scale(pygame.image.load("room1.jpg"), (WIDTH, HEIGHT))
SD = pygame.mixer.music.load("For Whom The Bell Tolls (Remastered).mp3")

PLAYER_WIDTH = 60
PLAYER_HEIGHT = 120
PLAYER_VEL = 6
TRAIL_LIFETIME = 3.0
TRAIL_RADIUS = 7
TRAIL_COLOR = (120, 72, 36)

tommy_image = pygame.transform.scale(pygame.image.load("Tommy.png").convert_alpha(), (PLAYER_WIDTH, PLAYER_HEIGHT))
benito_image = pygame.transform.scale(pygame.image.load("benito.png").convert_alpha(), (PLAYER_WIDTH, PLAYER_HEIGHT))

STAR_WIDTH = 20
STAR_HEIGHT = 90
STAR_VEL = 4

star_image= pygame.transform.scale(pygame.image.load("missile2.png").convert_alpha(), (STAR_WIDTH, STAR_HEIGHT))
big_star = pygame.transform.scale(pygame.image.load("missile2.png").convert_alpha(), (2*STAR_WIDTH, 2*STAR_HEIGHT))

FONT = pygame.font.SysFont("comicsans", 30)

def draw(player, player_sprite, elapsed_time, stars, bstars, trail_points):
    WIN.blit(BG, (0, 0))

    time_text = FONT.render(f"Time: {round(elapsed_time)}s",1 , "red")
    WIN.blit(time_text, (10,10))

    trail_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for x, y, created_at in trail_points:
        age = elapsed_time - created_at
        if age < TRAIL_LIFETIME:
            alpha = int(255 * (1 - (age / TRAIL_LIFETIME)))
            pygame.draw.circle(trail_surface, (*TRAIL_COLOR, alpha), (x, y), TRAIL_RADIUS)
    WIN.blit(trail_surface, (0, 0))

    WIN.blit(player_sprite, (player.x-15, player.y))

    for star in stars:
        WIN.blit(star_image, star)
    for bstar in bstars:
        WIN.blit(big_star, bstar)

    pygame.display.update()

def main():
    run = True
    pygame.mixer.music.play(-1)

    player = pygame.Rect(500, HEIGHT - PLAYER_HEIGHT,
                        PLAYER_WIDTH*0.55, PLAYER_HEIGHT*0.8)

    clock = pygame.time.Clock()
    start_time = time.time()
    elapsed_time = 0

    star_add_increment = 1200
    star_count = 0

    stars = []
    bstars = []
    trail_points = []
    benito_mode = False
    hit = False


    while run:
        star_count += clock.tick(60)
        elapsed_time = time.time() - start_time



        if star_count > star_add_increment:
            for _ in range(5+int(elapsed_time/10)):
                star_x = random.randint(0, WIDTH - STAR_WIDTH)
                star = pygame.Rect(star_x, -STAR_HEIGHT, STAR_WIDTH, STAR_HEIGHT)
                stars.append(star)
            for _ in range(2*int(elapsed_time/30)):
                bstar_x = random.randint(0, WIDTH - 2*STAR_WIDTH)
                bstar = pygame.Rect(bstar_x, -2*STAR_HEIGHT, 2*STAR_WIDTH, 2*STAR_HEIGHT)
                bstars.append(bstar)

            star_add_increment = max(800, star_add_increment- 3)
            star_count = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        old_x, old_y = player.x, player.y

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LSHIFT]:
            PLAYER_VEL = 2
        else:
            PLAYER_VEL = 6
        if keys[pygame.K_LEFT]:
            player.x = max(0, player.x - PLAYER_VEL)
        if keys[pygame.K_RIGHT]:
            player.x = min(WIDTH - player.width, player.x + PLAYER_VEL)
        if keys[pygame.K_UP]:
            player.y = max(0, player.y - PLAYER_VEL)
        if keys[pygame.K_DOWN]:
            player.y = min(HEIGHT - player.height, player.y + PLAYER_VEL)

        if player.x != old_x or player.y != old_y:
            trail_points.append((player.x + player.width // 2, player.y + player.height // 2, elapsed_time))

        trail_points = [point for point in trail_points if elapsed_time - point[2] < TRAIL_LIFETIME]

        for star in stars[:]:
            star.y += STAR_VEL + int(elapsed_time/20)
            if star.y > HEIGHT:
                stars.remove(star)
            elif star.y + star.height -20 >= player.y and star.colliderect(player):
                stars.remove(star)
                hit = True
                break
        for bstar in bstars[:]:
            bstar.y += STAR_VEL + int(elapsed_time/20)
            if bstar.y > HEIGHT:
                bstars.remove(bstar)
            elif bstar.y + bstar.height -20 >= player.y and bstar.colliderect(player):
                bstars.remove(bstar)
                hit = True
                break

        if hit:
            lost_text = FONT.render("Tommy KABOOM!", 5, "red")
            WIN.blit(lost_text, (WIDTH/2 - lost_text.get_width()/2, HEIGHT/2 - lost_text.get_height()/2))
            pygame.display.update()
            pygame.time.delay(4000)
            break

        if player.y <= 0:
            benito_mode = True

        if benito_mode:
            current_player_sprite = benito_image
        else:
            current_player_sprite = tommy_image

        draw(player, current_player_sprite, elapsed_time, stars, bstars, trail_points)

    pygame.quit()

if __name__ == "__main__":
    main()