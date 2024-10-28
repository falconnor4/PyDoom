import pygame as pg

# Constants
SCREENRECT = pg.Rect(0, 0, 640, 480)

# Variables
tick = 0

def main():
    print("start")

    pg.init()

    fullscreen = True
    winstyle = 0
    bestdepth = pg.display.mode_ok(SCREENRECT.size, winstyle, 32)
    screen = pg.display.set_mode(SCREENRECT.size, winstyle, bestdepth)

    background = pg.Surface(SCREENRECT.size)
    screen.blit(background, (0, 0))

    clock = pg.time.clock()

    while True:
        loop(clock)

main()

def loop(clock):
    print("loop")

    clock.tick(60)

    tick += 1