## Berda's Soung engine v0.1
from pygame import mixer, mixer_music
import pygame
from pygame.locals import *
import os
from random import randint
print(pygame.__version__)

pygame.init()

devmode = False

def sound_handle(track:str , action_type:str = "play", volume:int=100):

    sfx_path = os.path.join(os.getcwd(), "ChaosCardGame", "SfxEngine", "SFX", str(track) + ".wav")
    #get path of the sound used

    sound = pygame.mixer.Sound(sfx_path)
    #define what is the damn sound$

    sound.set_volume(volume/100)
    #set the volume (garageband wav is gringe and loud so set a low volume like 30-50 if its too loud)

    if action_type == "play":
#       if randint(0,10000) == 1:
#           pygame.mixer.Sound.play(pygame.mixer.Sound(os.path.join(os.getcwd(), "ChaosCardGame", "SfxEngine", "SFX", "magictrack.wav")))
        pygame.mixer.Sound.play(sound)
        #play the damn sound

    if action_type == "pause":
        pygame.mixer.stop()
        #self explainatory

    if action_type == "ambient_play":
        music = pygame.mixer.music(sfx_path)
        pygame.mixer.music.set_volume(volume/100)
        pygame.mixer.music.play(music)
        #use for ambient music only as it is treated differently than other sfx






if devmode:
    #experimental window with a button to test if work or no
    sound_played = False
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.mixer.init()
    button_color = (255, 0, 0) # Red color
    button_width = 100
    button_height = 50
    button_x = (WINDOW_WIDTH - button_width) // 2
    button_y = (WINDOW_HEIGHT - button_height) // 2
    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if button_rect.collidepoint(mouse_pos):
                    print("clicked")
                    sound_handle("ClickSound1-2", "play")
            elif event.type == MOUSEBUTTONUP:
                mouse_pos = pygame.mouse.get_pos()
                if button_rect.collidepoint(mouse_pos):
                    print("released")                    
                    sound_handle("ClickSound2-1", "play")


        window.fill((0, 0, 0)) # Fill the window with black color
        pygame.draw.rect(window, button_color, button_rect) # Draw the button
        pygame.display.flip() # Update the display

pygame.quit()
