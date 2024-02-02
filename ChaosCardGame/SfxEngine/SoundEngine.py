## Berda's Soung engine v0.1
from pygame import mixer, mixer_music
import pygame
from pygame.locals import *
import os
from random import randint

devmode = False

def sound_handle(track:str , action_type:str = "play", volume:int=100, sfx_channel:int=5, ambient_channel:int=6):
    
    sfx_path = os.path.join(os.getcwd(), "ChaosCardGame", "SfxEngine", "SFX", str(track) + ".wav")

    sfxchannel = pygame.mixer.Channel(sfx_channel)
    sound = pygame.mixer.Sound(sfx_path)
    sound.set_volume(volume/100)


    if action_type == "play":
        sfxchannel.play(sound)

    if action_type == "pause":
        sfxchannel.stop()

    if action_type == "ambient_play":
        pygame.mixer.music.load(sfx_path)
        pygame.mixer.music.set_volume(volume/100)
        pygame.mixer.music.play()

    #    ambientchannel = pygame.mixer.Channel(ambient_channel)
    #    ambient_sound = pygame.mixer.Sound(sfx_path)
    #    ambient_sound.set_volume(volume/100)
    #    ambientchannel.play(ambient_sound)





if devmode:
    print(pygame.__version__)
    pygame.init()
    #experimental window with a button to test if work or no
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

    sound_handle("ambientmenumusictest", "ambient_play",30)
# put this piece of crap NOT IN A WHILE LOOP, it will start the song repeatedly and not play
    
    while running:

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if button_rect.collidepoint(mouse_pos):
                    print("clicked")
                    sound_handle("ClickSound1-2", "play", 40)
            elif event.type == MOUSEBUTTONUP:
                mouse_pos = pygame.mouse.get_pos()
                if button_rect.collidepoint(mouse_pos):
                    print("released")                    
                    sound_handle("ClickSound2-1", "play", 40)


        window.fill((0, 0, 0)) # Fill the window with black color
        pygame.draw.rect(window, button_color, button_rect) # Draw the button
        pygame.display.flip() # Update the display

pygame.quit()
