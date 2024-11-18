import math
import time
from cmu_graphics import *

app.stepsPerSecond = 60
CurrentScreen = Group()
app.setMaxShapeCount(69000000)

Hud = Image('assets/DOOM_HUD.png',0,360, width=400,height=40)
Background = Image('assets/Loopedskies.png',0,0, width=1600, height=200,align='top')
Background.toBack()

#Face = Image('cmu://746728/28903928/doomguyGIF.gif',185,380,align='center',width=68,height=39)

Frame0 = Image('assets/SS0.png', 200, 360,align='bottom',width=74,height=69, visible = True)
Frame1 = Image('assets/SS1.png', 200, 360,align='bottom',width=102,height=100, visible = False)
Frame2 = Image('assets/SS2.png', 200, 360,align='bottom',width=252,height=79, visible = False)
Frame3 = Image('assets/SS3.png', 200, 360,align='bottom',width=110,height=64, visible = False)
Frame4 = Image('assets/SS4.png', 200, 360,align='bottom',width=102,height=100, visible = False)

app.playerX,app.playerY = 1.5, 1.5
app.playerAngle = 0
speed = 0.9
health = 89
screenWidth = 400
screenHeight = 360
Resolution = 3

app.wallHeightMod = 2
app.playerHeightMod = 2
animBuffer = 0.1

worldMap = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 0, 1, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 0, 0, 1, 1, 0, 0, 0, 1],
    [1, 0, 0, 0, 1, 1, 0, 0, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 1, 0, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ]
    
worldColours = [
    ['gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray', 'gray'],
    ['dimGray', 'fireBrick', 'fireBrick', 'fireBrick', 'fireBrick', 'fireBrick', 'fireBrick', 'fireBrick', 'fireBrick', 'gray'],
    ['dimGray', 'fireBrick', 'dimGray', 'dimGray', 'fireBrick', 'fireBrick', 'gray', 'gray', 'fireBrick', 'gray'],
    ['dimGray', 'fireBrick', 'dimGray', 'fireBrick', 'fireBrick', 'fireBrick', 'fireBrick', 'gray', 'fireBrick', 'gray'],
    ['dimGray', 'fireBrick', 'fireBrick', 'fireBrick', 'lime', 'lime', 'fireBrick', 'fireBrick', 'fireBrick', 'gray'],
    ['dimGray', 'fireBrick', 'fireBrick', 'fireBrick', 'lime', 'lime', 'fireBrick', 'fireBrick', 'fireBrick', 'gray'],
    ['dimGray', 'fireBrick', 'dimGray', 'fireBrick', 'fireBrick', 'fireBrick', 'fireBrick', 'dimGray', 'fireBrick', 'gray'],
    ['dimGray', 'fireBrick', 'dimGray', 'dimGray', 'fireBrick', 'fireBrick', 'dimGray', 'dimGray', 'fireBrick', 'gray'],
    ['dimGray', 'fireBrick', 'fireBrick', 'fireBrick', 'fireBrick', 'fireBrick', 'fireBrick', 'fireBrick', 'fireBrick', 'gray'],
    ['dimGray', 'dimGray', 'dimGray', 'dimGray', 'dimGray', 'dimGray', 'dimGray', 'dimGray', 'dimGray', 'gray']
    ]

def shoot():
    #TODO: for some reason the .visible meathod is not working, will look into later.
    fire = Sound('assets/firing.mp3')
    fire.play()
    time.sleep(animBuffer)
    open = Sound('assets/opening.mp3')
    open.play()   
    Frame0.visible = False
    Frame1.visible = True 
    time.sleep(animBuffer)
    Frame1.visible = False
    Frame2.visible = True
    time.sleep(animBuffer)
    reloading = Sound('assets/reloading.mp3')
    reloading.play()
    Frame2.visible = False
    Frame3.visible = True
    time.sleep(animBuffer)
    Frame3.visible = False
    Frame4.visible = True
    time.sleep(animBuffer)
    close = Sound('assets/closing.mp3')
    close.play() 
    Frame4.visible = False
    Frame0.visible = True     

def renderTri(locX1, locY1, locX2, locY2, LocX3, LocY3, color):
    RenderedTri = Polygon(locX1, locY1, locX2, locY2, LocX3, LocY3, fill=color)
    CurrentScreen.add(RenderedTri)
    
def renderQuad(locX1, locY1, locX2, locY2, LocX3, LocY3, LocX4, LocY4,color):
    RenderedQuad = Polygon(locX1, locY1, locX2, locY2, LocX3, LocY3, LocX4, LocY4, fill=color)
    CurrentScreen.add(RenderedQuad)


def RenderWorld(playerX, playerY, playerAngle, screenWidth, screenHeight):
    for column in range(0, screenWidth, Resolution):
        columnAngle = playerAngle - (math.atan(0.5 - (column + 0.5) / (screenWidth / 2)))
        distanceToWall = 0
        hitWall = False
        wallX, wallY = playerX, playerY
                
        while not hitWall and distanceToWall < 20:
            distanceToWall += Resolution * 0.00625
            
            testX = int(playerX + distanceToWall * math.cos(columnAngle))
            testY = int(playerY + distanceToWall * math.sin(columnAngle))
            if testX < 0 or testX >= len(worldMap[0]) or testY < 0 or testY >= len(worldMap):
                hitWall = True
                distanceToWall = 20
            
            else:
                if worldMap[testY][testX] == 1:
                    hitWall = True
                    wallX, wallY = testX, testY
                    app.currentColour = worldColours[testY][testX]
                    
                elif worldMap[testY][testX] == 0:
                    hitWall = False
                    app.floorColour = worldColours[testY][testX]
                    
        distanceToWall *= math.cos(playerAngle - columnAngle)
        wallHeight = min(screenHeight, int(screenHeight / distanceToWall))
        
        wallTop = max(0, screenHeight // 2 - wallHeight // app.wallHeightMod)
        wallBottom = min(screenHeight, screenHeight // 2 + wallHeight // app.playerHeightMod)
        
        renderQuad(column, wallBottom, column + Resolution, wallBottom, column + Resolution, screenHeight, column, screenHeight, app.floorColour)
        renderQuad(column-1, wallTop, column + Resolution, wallTop, column + Resolution, wallBottom,column, wallBottom, app.currentColour)

    for y in range(len(worldMap)):
            for x in range(len(worldMap[y])):
                Colour = worldColours[y][x]
                renderQuad(x * 12 / 4, y * 12 / 4, (x + 1) * 12 / 4, y * 12 / 4, (x + 1) * 12 / 4, (y + 1) * 12 / 4,x * 12 / 4, (y + 1) * 12 / 4, Colour)

def IsCollision(x, y):
    gridX = int(x)
    gridY = int(y)
    if gridY < 0 or gridY >= len(worldMap) or gridX < 0 or gridX >= len(worldMap[0]):
        return True
    if worldMap[gridY][gridX] == 1:
        return True
        
    return False

def onStep():
    CurrentScreen.clear()
    RenderWorld(app.playerX, app.playerY, app.playerAngle, screenWidth, screenHeight)

def onKeyHold(keys):
    if "w" in keys:
        newPlayerX = app.playerX + speed * math.cos(app.playerAngle)*0.1
        newPlayerY = app.playerY + speed * math.sin(app.playerAngle)*0.1
    elif "s" in keys:
        newPlayerX = app.playerX - speed * math.cos(app.playerAngle)*0.1
        newPlayerY = app.playerY - speed * math.sin(app.playerAngle)*0.1
    elif "a" in keys:
        newPlayerX = app.playerX + speed * math.sin(app.playerAngle)*0.1
        newPlayerY = app.playerY - speed * math.cos(app.playerAngle)*0.1
    elif "d" in keys:
        newPlayerX = app.playerX - speed * math.sin(app.playerAngle)*0.1
        newPlayerY = app.playerY + speed * math.cos(app.playerAngle)*0.1
        
    elif "left" in keys:
        app.playerAngle -= math.pi/16
        if app.playerAngle <= math.pi*-2:
            app.playerAngle = 0
        newPlayerX = app.playerX
        newPlayerY = app.playerY
        Background.centerX = app.playerAngle*-63.661+200
        
    elif "right" in keys:
        app.playerAngle += math.pi/16
        if app.playerAngle >= math.pi*2:
            app.playerAngle = 0
        newPlayerX = app.playerX
        newPlayerY = app.playerY
        Background.centerX = app.playerAngle*-63.661+200
        
    elif "space" in keys:
        shoot()
        newPlayerX = app.playerX
        newPlayerY = app.playerY
    else:
        newPlayerX = app.playerX
        newPlayerY = app.playerY
        
    if IsCollision(newPlayerX, newPlayerY):
        pass
    else:
        app.playerX = newPlayerX
        app.playerY = newPlayerY


class Imp:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.speed = 0.1
        self.health = 100
        self.visible = False
        self.sprite = Image('assets/imp1.png', self.x, self.y, align='bottom', width=100, height=100, visible = False)
        
    def move(self):
        self.x += self.speed * math.cos(self.angle)
        self.y += self.speed * math.sin(self.angle)
        self.sprite.x = self.x
        self.sprite.y = self.y
        
    def render(self):
        self.sprite.visible = self.visible

    #TODO: Implement occlusion culling based on depth
    #I believe the best way to implement this is to do a depth prepass before rendering
    #then, render walls in order, therfor occlusing the Imp's position.

cmu_graphics.run()