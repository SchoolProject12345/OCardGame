## Berda's Soung engine v0.1
from pygame import mixer, mixer_music
import pygame
from pygame.locals import *
import os
from random import randint
print(pygame.__version__)

pygame.init()

devmode = True

def sound_handle(track:str , action_type:str = "play", volume:int=100, channel:int=1):
    sfx_path = os.path.join(os.getcwd(), "ChaosCardGame", "SfxEngine", "SFX", str(track) + ".wav")
    channel = pygame.mixer.Channel(channel)
    sound = pygame.mixer.Sound(sfx_path)

    sound.set_volume(volume/100)

    if action_type == "play":
        channel.play(pygame.mixer.Sound(sound))

    if action_type == "pause":
        pygame.mixer.stop()

    if action_type == "ambient_play":
        pygame.mixer.music.load(sfx_path)
        pygame.mixer.music.set_volume(volume/100)
        pygame.mixer.music.play(-1)
        
#channel crap is tricke, you cant play 2 things at the same time on the same channel so you have to number these correctly
# music shall be on the default channel, dont need to put an int for the channel, but sfx will have to be numbered





if devmode:
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

    while running:
        sound_handle("ambientmenumusictest", "play",30)
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
