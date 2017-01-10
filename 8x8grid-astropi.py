# -*- coding: utf-8 -*-
# forked from astro-pi/RPi_8x8GridDraw
# traduction française framboise314.fr
import pygame
import sys
import math
from pygame.locals import *
from led import LED
from buttons import Button
import png # pypng
from sense_hat import SenseHat
import copy, time

saved = True
warning = False
pygame.init()
pygame.font.init()

ap=SenseHat()
screen = pygame.display.set_mode((520, 530), 0, 32)
pygame.display.set_caption('Editeur LED pour SenseHat')
pygame.mouse.set_visible(1)

background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill((0, 51, 25))
colour = (255,0,0) # Mettre le rouge comme couleur par défaut
rotation = 0
frame_number  = 1
fps = 4



def setColourRed():
	global colour 
	colour = (255,0,0)

def setColourBlue():
	global colour 
	colour = (0,0,255)

def setColourGreen():
	global colour 
	colour = (0,255,0)

def setColourPurple():
	global colour 
	colour = (102,0,204)

def setColourPink():
	global colour 
	colour = (255,0,255)

def setColourYellow():
	global colour 
	colour = (255,255,0)

def setColourOrange():
	global colour 
	colour = (255,128,0)

def setColourWhite():
	global colour 
	colour = (255,255,255)

def setColourCyan():
	global colour 
	colour = (0,255,255)

def clearGrid(): # Efface la grille de LED pygame et met tous les leds.lit sur False
	
	for led in leds:
		led.lit = False

def buildGrid(): # Capture une grille et prépare une version pour l'exporter (png and text)

	e = [0,0,0]
	e_png = (0,0,0)

	grid = [
	e,e,e,e,e,e,e,e,
	e,e,e,e,e,e,e,e,
	e,e,e,e,e,e,e,e,
	e,e,e,e,e,e,e,e,
	e,e,e,e,e,e,e,e,
	e,e,e,e,e,e,e,e,
	e,e,e,e,e,e,e,e,
	e,e,e,e,e,e,e,e
	]
	#png_grid =[]

	png_grid = ['blank','blank','blank','blank','blank','blank','blank','blank']
	for led in leds:
		if led.lit:
			val = led.pos[0] + (8 * led.pos[1])
			#print val
			grid[val] = [led.color[0], led.color[1], led.color[2]]
			if png_grid[led.pos[0]] == 'blank':
				png_grid[led.pos[0]] = (led.color[0], led.color[1], led.color[2])
			else:
				png_grid[led.pos[0]] = png_grid[led.pos[0]] + (led.color[0], led.color[1], led.color[2])
		else: 
			if png_grid[led.pos[0]] == 'blank':
				png_grid[led.pos[0]] = (0,0,0)
			else:
				png_grid[led.pos[0]] = png_grid[led.pos[0]] + (0,0,0)
	return (grid, png_grid)

def piLoad(): # Charge une image sur la matrice de la SenseHat
	grid, grid_png = buildGrid()
	ap.set_pixels(grid)

def exportGrid(): # Ecrit un png dans un fichier

	global saved
	grid, png_grid = buildGrid()
	FILE=open('image8x8.png','wb')
	w = png.Writer(8,8)
	w.write(FILE,png_grid)
	FILE.close()
	saved = True

def exportCons(): # Ecrit une liste brute sur la console

	grid, png_grid = buildGrid()
	print(grid)


def rotate(): # Tourne l'image sur la matrice de la SenseHat
	global rotation
	if rotation == 270:
		rotation = 0
	else:
		rotation = rotation + 90
	ap.set_rotation(rotation)



def handleClick():
   
	global saved
	global warning
	pos = pygame.mouse.get_pos()
	led = findLED(pos, leds)
	if led:
		#print 'led ' + str(led) + ' clicked'
		led.clicked(colour)
		saved = False
	for butt in buttons:
		if butt.rect.collidepoint(pos):
			butt.click()
			#print 'button clicked'
	if warning:
		for butt in buttons_warn:
			if butt.rect.collidepoint(pos):
				butt.click()
				
 
def findLED(clicked_pos, leds): # Lit les leds et vérifie si la position cliquée en fait partie
	
	x = clicked_pos[0]
	y = clicked_pos[1]
	for led in leds:
		if math.hypot(led.pos_x - x, led.pos_y - y) <= led.radius:
			return led
			#print 'led cliquée'
	return None


def drawEverything():
	
	global warning
	screen.blit(background, (0, 0))
	#draw the leds
	for led in leds:
		led.draw()
	for button in buttons:
		button.draw(screen)
	font = pygame.font.Font(None,16)
	
	frame_text = 'Trame ' + str(frame_number) 
	text = font.render(frame_text,1,(255,255,255))
	screen.blit(text, (445,370))
	fps_text = 'Freq. Trame= ' + str(fps) +' fps' 
	text = font.render(fps_text,1,(255,255,255))
	screen.blit(text, (343,440))
	font = pygame.font.Font(None,18)
	export_text = 'Animation'
	text = font.render(export_text,1,(255,255,255))
	screen.blit(text, (30,440))
	export_text = 'Trame unique'
	text = font.render(export_text,1,(255,255,255))
	screen.blit(text, (160,440))
	pygame.draw.circle(screen,colour,(470,345),20,0)
	#flip the screen
	if warning:
		for button in buttons_warn:
			button.draw(screen)
	pygame.display.flip()

def load_leds_to_animation():

	global frame_number
	global leds
	for saved_led in animation[frame_number]:
				if saved_led.lit:
					for led in leds:
						if led.pos == saved_led.pos:
							led.color = saved_led.color
							led.lit = True

def nextFrame():
	
	global frame_number
	global leds
	#print(frame_number)
	animation[frame_number] = copy.deepcopy(leds)
	#clearGrid()
	frame_number+=1
	if frame_number in animation:
		leds =[]
		for x in range(0, 8):
			for y in range(0, 8):
				led = LED(pos=(x, y))
				leds.append(led)
		load_leds_to_animation()
			
	

def prevFrame():

	global frame_number
	global leds
	#print(frame_number)
	animation[frame_number] = copy.deepcopy(leds)
	clearGrid()
	if frame_number != 1:
		frame_number-=1
	if frame_number in animation:
		leds =[]
		for x in range(0, 8):
			for y in range(0, 8):
				led = LED(pos=(x, y))
				leds.append(led)
		load_leds_to_animation()

def delFrame():
	global frame_number
	#print('ani length is ' + str(len(animation)) + ' frame is ' + str(frame_number))
	if len(animation) > 1:
		animation[frame_number] = copy.deepcopy(leds)
		del animation[frame_number]
		prevFrame()		
		for shuffle_frame in range(frame_number+1,len(animation)):
			animation[shuffle_frame] = animation[shuffle_frame+1]
		del animation[len(animation)]
		


def getLitLEDs():

	points = []
	for led in leds:
		if led.lit:
			points.append(led.pos)
	return points

# Programme principal - configure les leds et les boutons

leds = []
for x in range(0, 8):
	for y in range(0, 8):
		led = LED(pos=(x, y))
		leds.append(led)
buttons = []
buttons_warn = []
animation={}
#global frame_number

def play():
	
	global leds
	global frame_number
	animation[frame_number] = copy.deepcopy(leds)
	#print 'length of ani is ' + str(len(animation))
	for playframe in range(1,(len(animation)+1)):
		#print(playframe) 
		leds =[]
		for x in range(0, 8):
			for y in range(0, 8):
				led = LED(pos=(x, y))
				leds.append(led)
			for saved_led in animation[playframe]:
				if saved_led.lit:
					for led in leds:
						if led.pos == saved_led.pos:
							led.color = saved_led.color
							led.lit = True
		piLoad()
		time.sleep(1.0/fps)
		
def faster():
	global fps
	fps+=1

def slower():
	global fps
	if fps != 1:
		fps-=1

def exportAni():

	global saved
	FILE=open('animation8x8.py','wb')
	FILE.write('from sense_hat import SenseHat\n')
	FILE.write('import time\n')
	FILE.write('ap=SenseHat()\n')
	FILE.write('FRAMES = [\n')
	global leds
	global frame_number
	animation[frame_number] = copy.deepcopy(leds)
	#print 'length of ani is ' + str(len(animation))
	for playframe in range(1,(len(animation)+1)):
		#print(playframe) 
		leds =[]
		for x in range(0, 8):
			for y in range(0, 8):
				led = LED(pos=(x, y))
				leds.append(led)
			for saved_led in animation[playframe]:
				if saved_led.lit:
					for led in leds:
						if led.pos == saved_led.pos:
							led.color = saved_led.color
							led.lit = True
		grid, png_grid = buildGrid()
		
		FILE.write(str(grid))
		FILE.write(',\n')
	FILE.write(']\n')
	FILE.write('for x in FRAMES:\n')
	FILE.write('\t ap.set_pixels(x)\n')
	FILE.write('\t time.sleep('+ str(1.0/fps) + ')\n')
	FILE.close()
	saved = True

def prog_exit():
	print('exit clicked')
	global warning
	warning = False
	clearGrid()
	pygame.quit()
	sys.exit()

def save_it():
	print('save clicked')
	global warning
	exportAni()
	warning = False

def importAni():
        global leds
        global frame_number
	with open('animation8x8.py') as ll:
		line_count = sum(1 for _ in ll)
	ll.close()

	#animation = {}
	frame_number = 1
	file = open('animation8x8.py')
	for r in range(4):
		file.readline()

	for frame  in range(line_count-8):
		buff = file.readline()

		load_frame = buff.split('], [')
		counter = 1
		leds =[]
		for f in load_frame:
                        
			if counter == 1:
				f = f[2:]
			elif counter == 64:
                                
				f = f[:-4]
			
			y = int(counter-1)/8
			x = int(counter-1)%8
			
			#print(str(counter) + ' ' + f + ' x= ' + str(x) + ' y= ' + str(y))
			led = LED(pos=(x, y))
			if f == '0, 0, 0':
				led.lit = False
			
			else:
				led.lit = True
				f_colours = f.split(',')
				#print(f_colours)
				led.color = [int(f_colours[0]),int(f_colours[1]),int(f_colours[2])]
			leds.append(led)
			counter+=1
		animation[frame_number] = copy.deepcopy(leds)
		frame_number+=1
		counter+=1

	file.close()
	#drawEverything()

exportAniButton = Button('Export vers py', action=exportAni, size=(115,30), pos=(10, 460), color=(153,0,0))
buttons.append(exportAniButton)
importAniButton = Button('Import de fichier', action=importAni, size=(115,30), pos=(10, 495), color=(153,0,0))
buttons.append(importAniButton)

exportConsButton = Button('Export vers console', action=exportCons, size=(135,30), pos=(130, 460), color=(160,160,160))
buttons.append(exportConsButton)
exportPngButton = Button('Export vers PNG', action=exportGrid, size=(135,30), pos=(130, 495), color=(160,160,160))
buttons.append(exportPngButton)

RotateButton = Button('Rotation LEDs', action=rotate,  size=(110,30), pos=(275, 460), color=(205,255,255))
buttons.append(RotateButton)
clearButton = Button('Efface tout', action=clearGrid,  size=(110,30), pos=(275, 495), color=(204,255,255))
buttons.append(clearButton)

FasterButton = Button('+', action=faster, size=(45,25), pos=(395, 460), color=(184,138,0))
buttons.append(FasterButton)
SlowerButton = Button('-', action=slower, size=(45,25), pos=(450, 460), color=(184,138,0))
buttons.append(SlowerButton)

PlayButton = Button('Joue sur LED', action=play,  pos=(395, 495), color=(184,138,0))
buttons.append(PlayButton)

RedButton = Button('Rouge', action=setColourRed, size=(60,30), pos=(445, 10),hilight=(0, 200, 200),color=(255,0,0))
buttons.append(RedButton)
BlueButton = Button('Bleu', action=setColourBlue, size=(60,30), pos=(445, 45),hilight=(0, 200, 200),color=(0,0,255))
buttons.append(BlueButton)
GreenButton = Button('vert', action=setColourGreen, size=(60,30), pos=(445, 80),hilight=(0, 200, 200),color=(0,255,0))
buttons.append(GreenButton)
PurpleButton = Button('Pourpre', action=setColourPurple, size=(60,30), pos=(445, 115),hilight=(0, 200, 200),color=(102,0,204))
buttons.append(PurpleButton)
PinkButton = Button('Rose', action=setColourPink, size=(60,30), pos=(445, 150),hilight=(0, 200, 200),color=(255,0,255))
buttons.append(PinkButton)
OrangeButton = Button('Orange', action=setColourOrange, size=(60,30), pos=(445, 185),hilight=(0, 200, 200),color=(255,128,0))
buttons.append(OrangeButton)
YellowButton = Button('Jaune', action=setColourYellow, size=(60,30), pos=(445, 220),hilight=(0, 200, 200),color=(255,255,0))
buttons.append(YellowButton)
WhiteButton = Button('Blanc', action=setColourWhite, size=(60,30), pos=(445, 255),hilight=(0, 200, 200),color=(255,255,255))
buttons.append(WhiteButton)
CyanButton = Button('Cyan', action=setColourCyan, size=(60,30), pos=(445, 290),hilight=(0, 200, 200),color=(0,255,255))
buttons.append(CyanButton)

PrevFrameButton = Button('<-', action=prevFrame, size=(25,25), pos=(445, 385), color=(184,138,0))
buttons.append(PrevFrameButton)
NextFrameButton = Button('->', action=nextFrame, size=(25,25), pos=(475, 385), color=(184,138,0))
buttons.append(NextFrameButton)

DelFrame = Button('Supprime', action=delFrame, size=(55,25), pos=(445, 415), color=(184,138,0))
buttons.append(DelFrame)

saveButton = Button('Sauve', action=save_it, size=(60,50), pos=(150, 180),hilight=(200, 0, 0),color=(255,255,0))
buttons_warn.append(saveButton)
QuitButton = Button('Quitte', action=prog_exit, size=(60,50), pos=(260, 180),hilight=(200, 0, 0),color=(255,255,0))
buttons_warn.append(QuitButton)


def nosave_warn():
	global warning
	warning = True
	font = pygame.font.Font(None,48)
	frame_text = 'Images non sauvegardées ' 
	
	for d in range(5):
		text = font.render(frame_text,1,(255,0,0))
		screen.blit(text, (100,100))
		pygame.display.flip()
		time.sleep(0.1)
		text = font.render(frame_text,1,(0,255,0))
		screen.blit(text, (100,100))
		pygame.display.flip()
		time.sleep(0.1)
	drawEverything()
# Main prog loop


while True:

	for event in pygame.event.get():
		if event.type == QUIT:
			if saved == False:
				nosave_warn()
			else:
				prog_exit()
		
		if event.type == MOUSEBUTTONDOWN:
			handleClick()

	#update the display
	drawEverything()

