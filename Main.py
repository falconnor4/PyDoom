import math

import pygame
import render

'''
Minimal DOOM WAD renderer
Based on Pythong implementation by shedskin:

https://github.com/shedskin/shedskin/tree/master/examples/doom
'''

WAD = 'DOOM1.WAD'
MAP = 'E1M1'

VELOCITY_LIMIT = 4
MIN_VELOCITY_LIMIT = -4

def move_player(accel, strafe, player, vx, vy, linear_accel):
    ax = accel * math.cos(player.angle + strafe)
    ay = accel * math.sin(player.angle + strafe)
    vx2 = vx + ax
    vy2 = vy + ay
    vx2 = min(max(vx2, MIN_VELOCITY_LIMIT), VELOCITY_LIMIT)
    vy2 = min(max(vy2, MIN_VELOCITY_LIMIT), VELOCITY_LIMIT)
    return vx2, vy2

def main():
    screen = (render.WIDTH, render.HEIGHT)
    pygame.init()
    surface = pygame.display.set_mode(screen)
    drawsurf = pygame.Surface(screen).convert()
    drawsurf.set_colorkey((0, 0, 0))

    map_ = render.Map(WAD, MAP)
    player = map_.player
    palette = map_.palette
    frame_count = 0

    vx = vy = vz = 0.0
    va = 0.0

    delta = 1 / 60
    angular_accel = 30
    linear_accel = 0.4
    strafe = math.radians(90)

    ANGULAR_LIMIT = 30
    FLOOR_HEIGHT_OFFSET = 48

    clock = pygame.time.Clock()

    ingame = True
    while ingame:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    ingame = False
            elif event.type == pygame.QUIT:
                ingame = False

        keys = pygame.key.get_pressed()

        # angular speed
        if not keys[pygame.K_LCTRL]:
            if keys[pygame.K_RIGHT]:
                va -= angular_accel * delta
            if keys[pygame.K_LEFT]:
                va += angular_accel * delta

            va = min(max(va, -ANGULAR_LIMIT), ANGULAR_LIMIT)

        player.angle += va * delta
        va = va * (1.0 - 8.0 * delta)

        # linear speeds
        if keys[pygame.K_LCTRL]:
            if keys[pygame.K_LEFT]:
                vx, vy = move_player(linear_accel, strafe, player, vx, vy, linear_accel)
            if keys[pygame.K_RIGHT]:
                vx, vy = move_player(linear_accel, -strafe, player, vx, vy, linear_accel)

        if keys[pygame.K_UP]:
            vx, vy = move_player(linear_accel, 0, player, vx, vy, linear_accel)

        if keys[pygame.K_DOWN]:
            vx, vy = move_player(-linear_accel, 0, player, vx, vy, linear_accel)

        # update player
        player.x += vx
        player.y += vy
        vx *= 0.95
        vy *= 0.95
        if player.z < player.floor_h + FLOOR_HEIGHT_OFFSET:
            player.z += 0.1 * (player.floor_h + FLOOR_HEIGHT_OFFSET - player.z)
            vz = 0
        else:
            vz -= 0.1
            player.z += max(-5.0, vz)
        player.update()

        # and now render!
        t0 = pygame.time.get_ticks()

        buf = render.render(map_, frame_count)
        img = pygame.image.frombuffer(buf, (render.WIDTH, render.HEIGHT), 'P')
        img.set_palette(palette)
        surface.blit(img, (0, 0))
        pygame.display.flip()

        clock.tick(60)

        delta = (pygame.time.get_ticks() - t0)
        if frame_count % 10 == 0: #doesn't work with updated get_ticks
            print('FPS %.2f' % (1/delta))
        frame_count += 1


if __name__ == '__main__':
    main()
