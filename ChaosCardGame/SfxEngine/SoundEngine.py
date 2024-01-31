## Berda's Soung engine v0.1
from pygame import mixer, mixer_music
import pygame
from pygame.locals import *
import os
from random import randint

pygame.init()

devmode = True

def sound_handle(track:str , action_type:str = "play"):
    sfx_path = os.path.join(os.getcwd(), "ChaosCardGame", "SfxEngine", "SFX", str(track) + ".wav")
    sound = pygame.mixer.Sound(sfx_path)

    if action_type == "play":
        if randint(0,10) == 1:
            pygame.mixer.Sound.play(pygame.mixer.Sound(os.path.join(os.getcwd(), "ChaosCardGame", "SfxEngine", "SFX", "magictrack.wav")))
            print("HEHEHEHHEHEHEHAEHAEHAHEAHEHAEHAHEHAEHEAHEAHAEHAEHEEAHA")
        pygame.mixer.Sound.play(sound)

    if action_type == "pause":
        pygame.mixer.pause()






if devmode:
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