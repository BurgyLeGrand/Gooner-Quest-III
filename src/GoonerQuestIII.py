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

missile_source = pygame.image.load("missile2.png").convert_alpha()
rona_source = pygame.image.load("rona.png").convert_alpha()

def scale_to_height(image, target_height):
    width, height = image.get_size()
    scaled_width = max(1, int(width * (target_height / height)))
    return pygame.transform.smoothscale(image, (scaled_width, target_height))

small_projectile_variants = [
    {"image": scale_to_height(missile_source, STAR_HEIGHT), "rotates": False},
    {"image": scale_to_height(rona_source, STAR_HEIGHT), "rotates": True}
]
big_projectile_variants = [
    {"image": scale_to_height(missile_source, 2 * STAR_HEIGHT), "rotates": False},
    {"image": scale_to_height(rona_source, 2 * STAR_HEIGHT), "rotates": True}
]

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
        rotated_star = pygame.transform.rotate(star["image"], star["angle"])
        rotated_star_rect = rotated_star.get_rect(center=star["rect"].center)
        WIN.blit(rotated_star, rotated_star_rect.topleft)
    for bstar in bstars:
        rotated_bstar = pygame.transform.rotate(bstar["image"], bstar["angle"])
        rotated_bstar_rect = rotated_bstar.get_rect(center=bstar["rect"].center)
        WIN.blit(rotated_bstar, rotated_bstar_rect.topleft)

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
        frame_time_ms = clock.tick(60)
        star_count += frame_time_ms
        delta_time = frame_time_ms / 1000
        elapsed_time = time.time() - start_time



        if star_count > star_add_increment:
            for _ in range(5+int(elapsed_time/10)):
                star_variant = random.choice(small_projectile_variants)
                star_sprite = star_variant["image"]
                star_width, star_height = star_sprite.get_size()
                star_x = random.randint(0, WIDTH - star_width)
                star = {
                    "rect": pygame.Rect(star_x, -star_height, star_width, star_height),
                    "image": star_sprite,
                    "angle": random.uniform(0, 360) if star_variant["rotates"] else 0,
                    "spin": random.uniform(55, 90) if star_variant["rotates"] else 0
                }
                stars.append(star)
            for _ in range(2*int(elapsed_time/30)):
                bstar_variant = random.choice(big_projectile_variants)
                bstar_sprite = bstar_variant["image"]
                bstar_width, bstar_height = bstar_sprite.get_size()
                bstar_x = random.randint(0, WIDTH - bstar_width)
                bstar = {
                    "rect": pygame.Rect(bstar_x, -bstar_height, bstar_width, bstar_height),
                    "image": bstar_sprite,
                    "angle": random.uniform(0, 360) if bstar_variant["rotates"] else 0,
                    "spin": random.uniform(35, 60) if bstar_variant["rotates"] else 0
                }
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
            star["rect"].y += STAR_VEL + int(elapsed_time/20)
            star["angle"] = (star["angle"] + star["spin"] * delta_time) % 360
            if star["rect"].y > HEIGHT:
                stars.remove(star)
            elif star["rect"].y + star["rect"].height -20 >= player.y and star["rect"].colliderect(player):
                stars.remove(star)
                hit = True
                break
        for bstar in bstars[:]:
            bstar["rect"].y += STAR_VEL + int(elapsed_time/20)
            bstar["angle"] = (bstar["angle"] + bstar["spin"] * delta_time) % 360
            if bstar["rect"].y > HEIGHT:
                bstars.remove(bstar)
            elif bstar["rect"].y + bstar["rect"].height -20 >= player.y and bstar["rect"].colliderect(player):
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