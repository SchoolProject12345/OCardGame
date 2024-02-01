## Berda's Soung engine v0.1
from pygame import mixer
import pygame
import os





def sound_handle(track:str , action_type:str = "play", volume:int=100, sfx_channel:int=5):
    # a terminer

    sfx_path = os.path.join(os.getcwd(), "ChaosCardGame", "Assets", "SFX", str(track) + ".wav")
    
    sfxchannel = pygame.mixer.Channel(sfx_channel)
    sound = pygame.mixer.Sound(sfx_path)
    sound.set_volume(volume/100)

    pygame.mixer.music.load(sfx_path)
    pygame.mixer.music.set_volume(volume/100)

    if action_type == "play":
        sfxchannel.play(sound)

    if action_type == "ambient_pause":
        pygame.mixer.music.pause()

    if action_type == "ambient_play":
        pygame.mixer.music.play()

    #    ambientchannel = pygame.mixer.Channel(ambient_channel)
    #    ambient_sound = pygame.mixer.Sound(sfx_path)
    #    ambient_sound.set_volume(volume/100)
    #    ambientchannel.play(ambient_sound)