import pygame
from pygame.locals import *
import random
import time

#Universal Variables
SIZE = (1000, 700)
BLACK = (0,0,0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BROWN = (75, 54, 33)
LIGHT_BROWN  = (244,164,96)

# Text wrapping function
def wrapText(text, font, maxWidth, x, y, screen):
    # Split the text into words
    words = text.split(' ')
    lines = []
    currentLine = ''

    for word in words:
        # Create a test line by adding the current word
        testLine = currentLine +" " + word
        textWidth, textHeight = font.size(testLine)

        # If the line is too wide, start a new line
        if textWidth > maxWidth:
            lines.append(currentLine)
            currentLine = word
        else:
            currentLine = testLine

    # Add the last line
    lines.append(currentLine)

    yOffset = 0
    for line in lines:
        fw, fh = font.size(line)

        # (tx, ty) is the top-left of the font surface
        tx = x - fw / 2
        ty = y + yOffset
        
        fontSurface = font.render(line, True, BLACK)
        screen.blit(fontSurface, (tx, ty))

        yOffset += fh

pygame.init()
screen = pygame.display.set_mode(SIZE)
pygame.display.set_caption("Deck the Darkness")
cardTemplate = pygame.image.load("dist/assets/card-template.png").convert_alpha()
cardWid = 170
cardHei = 250
cardTemplate = pygame.transform.scale(cardTemplate, (cardWid, cardHei))

crossOut = pygame.image.load("dist/assets/cross-out.png")

castleBG = pygame.image.load("dist/assets/castle-background.jpg").convert_alpha()
castleBG = pygame.transform.scale(castleBG, (1000, 700))
forestBG = pygame.image.load("dist/assets/forest-background.jpg").convert_alpha()
forestBG = pygame.transform.scale(forestBG, (1000, 700))

hero1Img = pygame.image.load("dist/assets/RegularHero.png").convert_alpha()
hero2Img = pygame.image.load("dist/assets/ToughHero.png").convert_alpha()
hero3Img = pygame.image.load("dist/assets/ManaHero.png").convert_alpha()
heroWid = 150
heroHei = 218
hero1Img = pygame.transform.scale(hero1Img, (heroWid, heroHei))

#icons
poisonIcon = pygame.image.load("dist/assets/poison_icon.png").convert_alpha()
poisonIcon = pygame.transform.scale(poisonIcon, (30, 30))



cardList = [] # a master list of all the cards
globalMana = 0 # universal mana max depends on hero, replenishes each turn

def addIcon(iconImg, enemyX, enemyY, iconNum, power):
    textFont = pygame.font.SysFont(None, 18)
    iconPower = textFont.render(str(power), True, BLACK)
    screen.blit(iconPower, (enemyX+iconNum*60+13, enemyY+170))
    screen.blit(iconImg, (enemyX+iconNum*60, enemyY+140))

class Hero():
    def __init__(self, name, img, desc, health, defense, manaPower):
        self.name = name # name of hero, str
        self.img = img #image of the hero
        self.desc = desc # A brief description of hero
        self.health = health # How much health they have
        self.defense = defense # how much shield they have
        self.manaPower = manaPower # how much mana can use for per turn, default is 4, some is 5

        self.maxHealth = self.health
        self.startDefense = self.defense
        self.startMana = self.manaPower
        self.isDead = False
        self.isSelected = False

    def draw(self, x, y):
        self.x = x
        self.y = y

        descFont = pygame.font.SysFont(None, 18)
        titleFont = pygame.font.SysFont(None, 24)

        # if dead
        if self.isDead:
            screen.blit(self.img, (self.x, self.y))
            crossDisplay = pygame.transform.scale(crossOut, (heroWid, heroHei))
            screen.blit(crossDisplay, (self.x, self.y))

        else:
            #name Text
            nameText = titleFont.render(self.name, True, WHITE)
            nameRect = nameText.get_rect(center=(self.x + 140, self.y + 60))

            #Health text
            healthText = descFont.render("Health: %i / %i" %(self.health, self.maxHealth), True, WHITE)
            healthRect = healthText.get_rect(center=(self.x + 170, self.y + 100))

            #defense  text
            defenseText = descFont.render("Defense: %i" %self.defense, True, WHITE)
            defenseRect = defenseText.get_rect(center=(self.x + 170, self.y + 115))

            

            # create everything
            screen.blit(self.img, (self.x, self.y))
            screen.blit(nameText, nameRect)
            screen.blit(healthText, healthRect)
            screen.blit(defenseText, defenseRect)

    def drawSelect(self, x, y):
        self.x = x
        self.y = y

        descFont = pygame.font.SysFont(None, 24)
        titleFont = pygame.font.SysFont(None, 52)

        heroName = titleFont.render(self.name, True, BLACK)
        healthText = descFont.render("Health: %i" %self.health, True, BLACK)
        defenseText = descFont.render("Defense: %i" %self.defense, True, BLACK)
        manaText = descFont.render("Mana: %i" %self.manaPower, True, BLACK)

        #draw border if selected
        if self.isSelected == True:
            pygame.draw.rect(screen, BLACK, (self.x-10, self.y-10, 620, 220))
    
        pygame.draw.rect(screen, LIGHT_BROWN, (self.x, self.y, 600,200))

        # Draw everything
        screen.blit(self.img, (self.x+30, self.y))
        screen.blit(heroName, (self.x+300, self.y+10))
        wrapText(self.desc, descFont, 250, self.x+340, self.y+60, screen)

        #Draw stats
        screen.blit(healthText, (self.x + 200, self.y + 150))
        screen.blit(defenseText, (self.x + 300, self.y + 150))
        screen.blit(manaText, (self.x + 400, self.y + 150))


    def getHealth(self, health):
        if self.health + health > self.maxHealth:
            self.health = self.maxHealth #so it doesnt go over limit
        else:
            self.health += health

    def getShield(self, shield):
        self.defense += shield # get shielded more

    def getDamaged(self, damage):
        netDamage = damage - self.defense #accounting for shields

        self.health -= netDamage 

    def dead(self):
        self.isDead = True

class Enemy():
    def __init__(self, name, x, y, wid, hei, img, health, shield, attack):
        self.name = name #str displayed on top of img
        self.x = x
        self.y = y
        self.wid = wid
        self.hei = hei
        self.img = img #image variable, render it
        self.health = health #integer, healh of creature, displayed under wolf
        self.shield = shield #how much block they have, integer, below health
        self.attack = attack #integer, how much damage they will do, top of enemy

        self.maxHealth = self.health # their full health and full defeense and full attack
        self.startDef = shield
        self.startAttack = attack
        self.isPoisoned = False # if poinsoned, becomes true, in game loop, lose some damage every turn
        self.poisonPower = 0

        self.status = "alive" # alive or dead

    def draw(self):

        if self.status == "alive":
            titleFont = pygame.font.SysFont(None, 24)
            descFont = pygame.font.SysFont(None, 18)
            # Title text
            titleText = titleFont.render(self.name, True, WHITE)
            titleRect = titleText.get_rect(center=(self.x + self.wid/2, self.y - 10))

            #health text
            healthText = descFont.render("Health: %i / %i" % (self.health, self.maxHealth), True, WHITE)
            healthRect = healthText.get_rect(center=(self.x + self.wid/2, self.y + self.hei + 10))

            #shield text
            shieldText = descFont.render("Shield: %i" % self.shield, True, WHITE)
            shieldRect = shieldText.get_rect(center=(self.x + self.wid/2, self.y + self.hei + 22))

            #damage text
            damageText = descFont.render("Damage: %i" % self.attack, True, WHITE)
            damageRect = damageText.get_rect(center=(self.x + self.wid/2, self.y + self.hei + 34))

            #icons
            if self.isPoisoned:
                addIcon(poisonIcon, self.x, self.y, 0, self.poisonPower)

            screen.blit(self.img, (self.x, self.y))
            screen.blit(titleText, titleRect)
            screen.blit(healthText, healthRect)
            screen.blit(shieldText, shieldRect)
            screen.blit(damageText, damageRect)
        
        elif self.status == "dead":
            screen.blit(self.img, (self.x, self.y))
            crossDisplay = pygame.transform.scale(crossOut, (self.wid, self.hei))
            screen.blit(crossDisplay, (self.x, self.y))

    def getDamaged(self, damage):
        netDamage = damage - self.shield # damage not blocked by shield
        if netDamage < 0:
            netDamage = 0 #incase shield bigger than damage
        
        self.health -= netDamage #dealt by health

        if self.health <= 0: # if dead
            self.dead()

    def dead(self):
        self.status = "dead"

    def attackHero(self, hero):
        if hero.health > 0:
            netDamage = self.attack - hero.defense # minus the shield blocks
            hero.health -= netDamage

class Card():
    def __init__(self, name, x, y, img, desc, manaCost, power, type, effect, effectPower):
        self.name = name # name of card, str
        self.x = x
        self.y = y
        self.img = img # display image of card, image name
        self.desc = desc # Description of card, str
        self.manaCost = manaCost # how much it costs to play, int
        self.power = power # the number of damage, block, heal, etc, int
        self.type = type # what type of card it is (for now, damage, block, heal), str
        self.effect = effect # any additional things it does (poison, etc) lambda
        self.effectPower = effectPower # how strong the effect is (poison how much)

        self.ifClicked = False #if clicked, thenclicked on enemy it triggers the card
        self.isUsed = False #If the card has been used
        self.cardOutline = cardTemplate

    def draw(self):

        #render fonts
        titleFont = pygame.font.SysFont(None, 24)
        descFont = pygame.font.SysFont(None, 18)

        #name center
        nameText = titleFont.render(self.name, True, BLACK)
        nameRect = nameText.get_rect(center=(self.x + cardWid/2, self.y + cardHei/18))

        #mana cost center
        manaText = titleFont.render(str(self.manaCost), True, BLACK)
        manaRect = manaText.get_rect(center=(self.x + cardWid - 23, self.y + cardHei - 10))
    
        #render everything
        screen.blit(self.cardOutline, (self.x, self.y))
        if self.ifClicked == True:
            pygame.draw.rect(screen, BLACK, (self.x-5, self.y-5, cardWid+10, cardHei+10), 5)
        screen.blit(nameText, nameRect)
        screen.blit(manaText, manaRect)
        #desc render
        wrapText(self.desc, descFont, cardWid - 10, self.x + cardWid / 2, self.y + cardHei/1.4, screen)

        #render img
        screen.blit(self.img, (self.x + 30, self.y + 30))

    def onClicked(self):
        self.ifClicked = True

    def useCard(self, target):
        if self.type == "damage": # attack enemy
            target.getDamaged(self.power)
            if self.effect == "poison":
                target.isPoisoned = True
                target.poisonPower += self.effectPower # poisoned by effect
        
        if self.type == "defend":
            target.getShield(self.power)

        if self.type == "heal":
            target.getHealth(self.power)

        self.isUsed = True



def resetScreen():
    titleFont = pygame.font.SysFont(None, 64)
    descFont = pygame.font.SysFont(None, 48)

    diedText = titleFont.render("You have died!", True, BLACK)
    
    #Reset or quit
    resetText = descFont.render("Restart", True, BLACK)
    quitText = descFont.render("Quit", True, BLACK)

    # Draw everything
    pygame.draw.rect(screen, BROWN, (200, 100, 600, 500))
    if isHoverReset == False:
        resetText = descFont.render("Restart", True, BLACK) # default
    else:
        resetText = descFont.render("Restart", True, WHITE) # if mouse on it
        
    if isHoverQuit == False:
        quitText = descFont.render("Quit", True, BLACK)
    else:
        quitText = descFont.render("Quit", True, WHITE)

    
    screen.blit(quitText, (550, 450))
    screen.blit(resetText, (250, 450))
    screen.blit(diedText, (350, 200))

#reset screen
isHoverReset = False
isHoverQuit = False

#select screen
isHoverStart = False

# won screen
isHoverNewGame = False
isHoverWonQuit = False

# next fight screen
isHoverContinue = False

#Heroes
regularHero = Hero("Anissa", hero1Img, "A warrior who never turns her head in the face of adversity", 20, 1, 4)
toughHero = Hero("Cecil", hero2Img, "A guard who uses his strength and toughness to conquer any opponents", 25, 2, 3)
manaHero = Hero("Eve", hero3Img, "A mage who enchants and dazzles her enemies to death", 15, 0, 5)
currentHero = regularHero
heroList = [regularHero, toughHero, manaHero]


def selectScreen():
    pygame.draw.rect(screen, BROWN, (0,0,1000,700))

    text = pygame.font.SysFont(None, 48)

    selectText = text.render("Choose your Fighter!", True, BLACK)
    startTextB = text.render("Start Game!", True, BLACK)
    startTextW = text.render("Start Game!", True, WHITE)

    
    #Draw everything
    screen.blit(selectText, (350, 10))

    if isHoverStart: #not select
        screen.blit(startTextB, (800, 640))
    else:
        screen.blit(startTextW, (800, 640))

    #Three select screens, rect width is 600, height 200
    regularHero.drawSelect(50, 50)
    toughHero.drawSelect(50, 270)
    manaHero.drawSelect(50, 490)

def winScreen():
    titleFont = pygame.font.SysFont(None, 64)
    descFont = pygame.font.SysFont(None, 48)

    wonText = titleFont.render("You Won!", True, (0, 255, 255))
    
    #Reset or quit
    newGameText = descFont.render("New Game", True, BLACK)
    quitText = descFont.render("Quit", True, BLACK)

    # Draw everything
    pygame.draw.rect(screen, BROWN, (200, 100, 600, 500))
    if isHoverNewGame == False:
        newGameText = descFont.render("New Game", True, BLACK)
    else:
        newGameText = descFont.render("New Game", True, WHITE)
        
    if isHoverWonQuit == False:
        quitText = descFont.render("Quit", True, BLACK)
    else:
        quitText = descFont.render("Quit", True, WHITE)

    
    screen.blit(quitText, (550, 450))
    screen.blit(newGameText, (250, 450))
    screen.blit(wonText, (350, 200))

def nextFightScreen(fight):
    titleFont = pygame.font.SysFont(None, 64)
    descFont = pygame.font.SysFont(None, 48)

    nextFightText = titleFont.render("You Won Fight %i!" %fight, True, BLACK)
    
    #Reset or quit
    continueText = descFont.render("Continue", True, BLACK)

    # Draw everything
    pygame.draw.rect(screen, BROWN, (200, 100, 600, 500))
    if isHoverContinue == False:
        continueText = descFont.render("Continue", True, BLACK)
    else:
        continueText = descFont.render("Continue", True, WHITE)
    
    screen.blit(continueText, (400, 450))
    screen.blit(nextFightText, (250, 200))

woodBG = pygame.image.load("dist/assets/wood-background.jpg")
woodBG = pygame.transform.scale(woodBG, (1000, 700))
isHoverStartGame = False
isHoverHTP = False

def startScreen():
    titleFont = pygame.font.SysFont(None, 86)
    descFont = pygame.font.SysFont(None, 48)
    screen.blit(woodBG, (0,0))

    #Title text
    titleText = titleFont.render("Deck the Darkness", True, (210, 43, 43))
    titleRect = titleText.get_rect(center=(510, 70))

    # Start button
    if isHoverStartGame == False:
        startText = descFont.render("Start", True, BLACK)
    else:
        startText = descFont.render("Start", True, WHITE)
    pygame.draw.rect(screen, BROWN, (400, 300, 200, 70))

    # how to play button
    if isHoverHTP == False:
        htpText = descFont.render("How to Play", True, BLACK)
    else:
        htpText = descFont.render("How to Play", True, WHITE)
    pygame.draw.rect(screen, BROWN, (400, 450, 200, 70))


    
    # have title text top middle, surrond by the characters and cards, two options of start game and how to play
    screen.blit(titleText, titleRect)
    screen.blit(startText, (460, 317))
    screen.blit(htpText, (405, 467))

isHoverBack = False

def htpScreen():
    titleFont = pygame.font.SysFont(None, 86)
    descFont = pygame.font.SysFont(None, 32)
    screen.blit(woodBG, (0,0))

    howToPlayText = "Your goal is to defeat the enemies. During your turn, you can cast cards that use up your mana. To use a card, click on it, then click on either one of the enemies you wish to target or your hero if the card is a heal or defend card. Once you ran out of mana or are satified with your turn, you can click end turn. Then, enemies will attack you. Try not to die! There are two rounds in total!"

    #Title text
    titleText = titleFont.render("How to Play", True, (210, 43, 43))
    titleRect = titleText.get_rect(center=(510, 70))

    screen.blit(titleText, titleRect)
    wrapText(howToPlayText, descFont, 600, 500, 200, screen)

    #back button
    if isHoverBack == False:
        backText = titleFont.render("Back", True, BLACK)
    else:
        backText = titleFont.render("Back", True, WHITE)

    pygame.draw.rect(screen, BROWN, (200, 500, 200, 70))

    screen.blit(backText, (230, 505))



# Card image dist/assets
knifeImg = pygame.image.load("dist/assets/knife-art.png").convert_alpha()
knifeImg = pygame.transform.scale(knifeImg, (100, 100))
blastImg = pygame.image.load("dist/assets/punch-art.png")
blastImg = pygame.transform.scale(blastImg, (100, 100))
strikeImg = pygame.image.load("dist/assets/strike-art.png")
strikeImg = pygame.transform.scale(strikeImg, (100, 100))
fireballImg = pygame.image.load("dist/assets/fireball-art.png")
fireballImg = pygame.transform.scale(fireballImg, (100, 100))
shieldImg = pygame.image.load("dist/assets/shield-art.png")
shieldImg = pygame.transform.scale(shieldImg, (100, 100))
armourImg = pygame.image.load("dist/assets/armour-art.png")
armourImg = pygame.transform.scale(armourImg, (100, 100))
rejuvenateImg = pygame.image.load("dist/assets/rejuvenate-art.png")
rejuvenateImg = pygame.transform.scale(rejuvenateImg, (100, 100))
littlehealImg = pygame.image.load("dist/assets/littleheal-art.png")
littlehealImg = pygame.transform.scale(littlehealImg, (100, 100))
poisonswordImg = pygame.image.load("dist/assets/poisonsword-art.png")
poisonswordImg = pygame.transform.scale(poisonswordImg, (100, 100))
poisonpotionImg = pygame.image.load("dist/assets/poison_potion.jpeg")
poisonpotionImg = pygame.transform.scale(poisonpotionImg, (100, 100))

# Enemy image dist/assets
wolfImg = pygame.image.load("dist/assets/wolf.png").convert_alpha()
wolfWid = 150
wolfHei = 100
wolfImg = pygame.transform.scale(wolfImg, (wolfWid, wolfHei))

goblinImg = pygame.image.load("dist/assets/goblin-art.png")
goblinImg = pygame.transform.scale(goblinImg, (150, 100))
witch1Img = pygame.image.load("dist/assets/witch1-art.png")
witch2Img = pygame.image.load("dist/assets/witch2-art.png")
witch1Img = pygame.transform.scale(witch1Img, (150, 100))
witch2Img = pygame.transform.scale(witch2Img, (150, 100))


stabCard = Card("Stab", 10000, 10000, knifeImg, "deals 5 damage to an enemy", 1, 5, "damage",  "none", 0)
stabCard2 = Card("Stab", 10000, 10000, knifeImg, "deals 5 damage to an enemy", 1, 5,  "damage",  "none", 0)
blastCard = Card("Blast", 100000, 100000, blastImg, "deals 9 damage to an enemy", 2, 9,  "damage",  "none", 0)
strikeCard = Card("Strike", 10000, 10000, strikeImg, "deals 14 damage to an enemy", 3, 14,  "damage",  "none", 0)
fireballCard = Card("Fireball", 1000000,1000000, fireballImg, "deals 20 damage to an enemy", 4, 20,  "damage",  "none", 0)
shieldCard = Card("Shield", 1000000, 1000000, shieldImg, "Shields the hero by 1", 1, 1,  "defend",  "none", 0)
armourCard = Card("Armour Up", 10000, 10000, armourImg, "gain 2 shields", 3, 2,  "defend",  "none", 0)
healthCard = Card("Rejuvenate", 1000000, 1000000, rejuvenateImg, "Heals the hero by 7", 2, 7,  "heal",  "none", 0)
littlehealCard = Card("Little Heal", 1000000,1000000, littlehealImg, "Heals the hero by 3", 1, 3,  "heal",  "None", 0)
#Special Cards, add new parameter called "effect Power"
poisonCard = Card("Poison Blade", 10000, 10000, poisonswordImg, "deals 4 damage and poison enemy by 3 (enemy takes 3 damage per turn)", 2, 4, "damage", "poison", 3)
bigpoisonCard = Card("Crippling Poison", 10000, 10000, poisonpotionImg, "gives 6 poison to an enemy (enemy takes 6 damage per turn)", 3, 0, "damage", "poison", 6)

#Fight 1
wolfEnemy = Enemy("Wolf", 150, 100, 150, 100, wolfImg, 20, 2, 5)
goblinEnemy = Enemy("Goblin", 0, 0, 150, 100, goblinImg, 15, 0, 7)

# Fight 2
witchEnemy = Enemy("Beatrice", 0, 0, 150, 100, witch1Img, 25, 1, 7)
witchEnemy2 = Enemy("Bruneau", 0, 0, 150, 100, witch2Img, 10, 7, 7)

widBetween = 25

cardList = [stabCard, stabCard2, blastCard, strikeCard, fireballCard, shieldCard, armourCard, healthCard, littlehealCard, poisonCard, bigpoisonCard]
random.shuffle(cardList) # randomly shuffle cards

# current five cards on the thing, cards on left, coordinates on right
cardField = [cardList[0], cardList[1], cardList[2], cardList[3], cardList[4]] 
cardFieldCoord = [(widBetween, 400), (widBetween*2+cardWid, 400), (widBetween*3+cardWid*2, 400), (widBetween*4+cardWid*3, 400), (widBetween*5+cardWid*4, 400)] 
#coordinates of the 5 cards on the field at a time



#each list based on which fight
enemyList = [
    [wolfEnemy, goblinEnemy],
    [witchEnemy, witchEnemy2]
]
fightNum = 1

titleFont = pygame.font.SysFont(None, 32)
descFont = pygame.font.SysFont(None, 28)

#things that show up when you can't do something
noManaText = descFont.render("Not Enough Mana", True, RED)
noHeroSelect = descFont.render("Please select a hero first", True, RED)

# End turn text
endTurnText = descFont.render("End Turn", True, BLACK)
endTurnButX = 650
endTurnButY = 350

# define each screen as function
myClock = pygame.time.Clock()
noManaTime=0
noHeroSelectTime = 0
enemyAttackTime = 0
frameCount=0
turn = 0
dead = 0
enemyPhase=False

# start screen, how to play, select screen, then fight screen, then reset screen if lost, then won screen if won
currentScreen = "start screen"


for j in range(len(enemyList[fightNum-1])):
    enemyList[fightNum-1][j].x, enemyList[fightNum-1][j].y = (200*j+100, 30)
isRunning = True
while isRunning:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isRunning = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            
            if currentScreen == "fight screen": # if still alive
                for card in cardField:
                    # check if they hit enemy
                    if card.type == "damage": # target enemy
                        for enemy in enemyList[fightNum-1]: # depend on which fight
                            if enemy.x <= mx <= enemy.x + enemy.wid and enemy.y <= my <= enemy.y + enemy.hei:
                                if card.ifClicked == True and enemyPhase == False:
                                    if globalMana >= card.manaCost: # Check if theres enough mana
                                        card.useCard(enemy)
                                        globalMana -= card.manaCost
                                        # Part where you move card to back
                                        currCardIndex = cardField.index(card)
                                        cardList.pop(currCardIndex)
                                        cardList.append(card)
                                    else:
                                        noManaTime=frameCount+120
                                    

                    #check if hit hero
                    elif card.type != "damage":
                        if currentHero.x <= mx <= currentHero.x + heroWid and currentHero.y <= my <= currentHero.y + heroHei:
                            if card.ifClicked == True and enemyPhase == False:
                                if globalMana >= card.manaCost: # Check if theres enough mana
                                    card.useCard(currentHero)
                                    globalMana -= card.manaCost
                                    # Part where you move card to back
                                    currCardIndex = cardField.index(card)
                                    cardList.pop(currCardIndex)
                                    cardList.append(card)
                                else:
                                    noManaTime=frameCount+120 # two seconds display
                                    

                    if card.x <= mx <= card.x + cardWid and card.y <= my <= card.y + cardHei and enemyPhase == False: # if clicked on card in a cardlist
                        card.onClicked()
                    else:
                        card.ifClicked = False
                
                # if end turn pressed
                if endTurnButX <= mx <= endTurnButX + 100 and endTurnButY <= my <= endTurnButY + 30 and enemyPhase == False:
                    enemyPhase=True
                    currentEnemy=0
                    enemyAttackTime = frameCount + 30 # 1 sec of attack
                    random.shuffle(cardList) # shuffle cards again
                    globalMana = maxMana # reload all mana used
                    turn+=1 
                    

                # Reset and Quit buttons
            elif currentScreen == "reset screen":
                if 250 <= mx <= 370 and 450 <= my <= 500:
                    # Everything needed to reset the game
                    currentHero.isDead = False
                    # reset all hero stats
                    for hero in heroList:
                        hero.health = hero.maxHealth
                        hero.defense = hero.startDefense
                        hero.manaPower = hero.startMana
                    
                    # reset all enemy stats
                    for enemies in enemyList:
                        for enemy in enemies:
                            enemy.status = "alive"
                            enemy.health = enemy.maxHealth
                            enemy.shield = enemy.startDef
                            enemy.attack = enemy.startAttack
                            enemy.isPoisoned = False
                            enemy.poisonPower = 0
                    
                    fightNum = 1
                    enemyPhase = False

                    currentScreen = "start screen"

                #Quit screen
                if 550 <= mx <= 630 and 450 <= my <= 500:
                    isRunning = False
            
            elif currentScreen == "start screen":
                # go to select screen
                if 400 <= mx <= 600 and 300 <= my <= 370:
                    currentScreen = "select screen"
                if 400 <= mx <= 600 and 450 <= my <= 520:
                    currentScreen = "HTP screen"

            elif currentScreen == "HTP screen":
                # go back to start screen
                if 200 <= mx <= 400 and 500 <= my <= 570:
                    currentScreen = "start screen"

            # Select screen buttons
            elif currentScreen == "select screen":
                # start game clicked
                if 800 <= mx <= 1000 and 640 <= my <= 700:
                    # find which selected hero and go to fight
                    if regularHero.isSelected:
                        currentHero = regularHero
                        globalMana = currentHero.manaPower # how much mana
                        maxMana = currentHero.manaPower
                        currentScreen = "fight screen"
                    elif toughHero.isSelected:
                        currentHero = toughHero
                        globalMana = currentHero.manaPower # how much mana
                        maxMana = currentHero.manaPower
                        currentScreen = "fight screen"
                    elif manaHero.isSelected:
                        currentHero = manaHero
                        globalMana = currentHero.manaPower # how much mana
                        maxMana = currentHero.manaPower
                        currentScreen = "fight screen"
                    else: # not select anything
                        noHeroSelectTime = frameCount + 120
                # hero 1 select
                if 50 <= mx <= 650 and 50 <= my <= 250:
                    regularHero.isSelected = True
                else:
                    regularHero.isSelected = False
                # hero 2 select
                if 50 <= mx <= 650 and 270 <= my <= 470:
                    toughHero.isSelected = True
                else:
                    toughHero.isSelected = False
                # hero 3 select
                if 50 <= mx <= 650 and 490 <= my <= 690:
                    manaHero.isSelected = True
                else:
                    manaHero.isSelected = False

            elif currentScreen == "won screen":
                if 250 <= mx <= 430 and 450 <= my <= 500:
                    # Everything needed to reset the game after winning
                    currentHero.isDead = False
                    # reset all hero stats
                    for hero in heroList:
                        hero.health = hero.maxHealth
                        hero.defense = hero.startDefense
                        hero.manaPower = hero.startMana
                    
                    # reset all enemy stats, every enemy in every fight
                    for enemies in enemyList:
                        for enemy in enemies:
                            enemy.status = "alive"
                            enemy.health = enemy.maxHealth
                            enemy.shield = enemy.startDef
                            enemy.attack = enemy.startAttack
                            enemy.isPoisoned = False
                            enemy.poisonPower = 0
                    
                    fightNum = 1
                    enemyPhase = False

                    currentScreen = "start screen"
                    
                #hit quit button
                if 550 <= mx <= 630 and 450 <= my <= 500:
                    isRunning = False

            elif currentScreen == "next fight screen":
                # click continue button
                if 400 <= mx <= 550 and 450 <= my <= 500:
                    # ready for next fight
                    fightNum += 1
                    currentHero.health = currentHero.maxHealth
                    currentHero.defense = currentHero.startDefense
                    globalMana = maxMana

                    #reset enemy coords
                    for j in range(len(enemyList[fightNum-1])):
                        enemyList[fightNum-1][j].x, enemyList[fightNum-1][j].y = (200*j+100, 30)
    
                    currentScreen = "fight screen"

        if event.type == pygame.MOUSEMOTION:
            mx, my = pygame.mouse.get_pos()
            
            # start game how to play and start options
            if currentScreen == "start screen":
                if 400 <= mx <= 600 and 300 <= my <= 370:
                    isHoverStartGame = True
                else:
                    isHoverStartGame = False

                if 400 <= mx <= 600 and 450 <= my <= 520:
                    isHoverHTP = True
                else:
                    isHoverHTP = False

            if currentScreen == "HTP screen":
                if 200 <= mx <= 400 and 500 <= my <= 570:
                    isHoverBack = True
                else:
                    isHoverBack = False

            #reset screen options
            elif currentScreen == "reset screen":
                # hover over mouse
                if 250 <= mx <= 370 and 450 <= my <= 500:
                    isHoverReset = True
                else:
                    isHoverReset = False

                if 550 <= mx <= 630 and 450 <= my <= 500:
                    isHoverQuit = True
                else:
                    isHoverQuit = False
            
            # select screen
            elif currentScreen == "select screen":
                # hover over mouse
                if 800 <= mx <= 1000 and 640 <= my <= 700:
                    isHoverStart = True
                else:
                    isHoverStart = False

            elif currentScreen == "won screen":
                # hover over mouse
                if 250 <= mx <= 430 and 450 <= my <= 500:
                    isHoverNewGame = True
                else:
                    isHoverNewGame = False

                if 550 <= mx <= 630 and 450 <= my <= 500:
                    isHoverWonQuit = True
                else:
                    isHoverWonQuit = False

            elif currentScreen == "next fight screen":
                # hover over mouse
                if 400 <= mx <= 550 and 450 <= my <= 500:
                    isHoverContinue = True
                else:
                    isHoverContinue = False


    if currentScreen == "select screen":
        selectScreen()

        # display no hero selected error for two seconds
        if noHeroSelectTime > frameCount:
            screen.blit(noHeroSelect, (700, 400))

    #if still fighting
    if currentScreen == "fight screen":
        #enemy turn
        if enemyPhase:  
            enemy = enemyList[fightNum-1][currentEnemy]
            if enemy.status == "alive":
                if enemyAttackTime<frameCount+15:
                    enemy.y -= 3
                else:
                    enemy.y += 3
            
            if currentEnemy < len(enemyList[fightNum-1]) and enemyAttackTime < frameCount:
                enemy.y = 30
                currentEnemy += 1
                enemyAttackTime = frameCount+30
                if enemy.status == "alive" and currentHero.health > 0:
                    enemy.attackHero(currentHero)
            if currentEnemy == len(enemyList[fightNum-1]): # animation finsihed
                #check poison
                for enemy in enemyList[fightNum-1]:
                    if enemy.isPoisoned:
                        enemy.getDamaged(enemy.poisonPower + enemy.shield) # it bypasses shields
                enemyPhase = False
            if currentHero.health <= 0: # if killed
                currentHero.dead()
            
        if fightNum == 1:
            screen.blit(forestBG, (0,0))
        if fightNum == 2:
            screen.blit(castleBG, (0,0))
        manaText = titleFont.render("Mana: %i/%i" %(globalMana, maxMana), True, WHITE)
        
        #Display no mana error for 2 seconds
        if noManaTime>frameCount:
            screen.blit(noManaText, (450, 350))

        #make end turn button
        endTurnButton = pygame.draw.rect(screen, (205,133,63), (endTurnButX, endTurnButY, 100, 30))
        screen.blit(endTurnText, (660, 355))

        for i in range(len(cardField)):
            cardField[i].draw() #Each card is drawn with the coordinates depending on what position it is on
            cardField[i].x, cardField[i].y = cardFieldCoord[i]
        
        for j in range(len(enemyList[fightNum-1])):
            enemyList[fightNum-1][j].draw()

        currentHero.draw(50,200)

        #mana
        screen.blit(manaText, (800, 350))

    # Won a fight
    allDead = all(enemy.status == "dead" for enemy in enemyList[fightNum-1]) # should be True in all enemies dead
    if allDead:
        if fightNum == 1:
            currentScreen = "next fight screen"
        elif fightNum == 2:
            currentScreen = "won screen"

    # start screen
    if currentScreen == "start screen":
        startScreen()

    # How to play screen
    if currentScreen == "HTP screen":
        htpScreen()

    # Reset screen
    if currentHero.isDead:
        currentScreen = "reset screen"

    if currentScreen == "reset screen":
        resetScreen()
    
    # Won Screen
    if currentScreen == "won screen":
        winScreen()
    
    #Next fight screen
    if currentScreen == "next fight screen":
        nextFightScreen(fightNum)
    
    frameCount+=1
    cardField = [cardList[0], cardList[1], cardList[2], cardList[3], cardList[4]] 
    pygame.display.flip()
    myClock.tick(60)

pygame.quit()