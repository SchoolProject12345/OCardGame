## Berda's Soung engine v0.5
from pygame import mixer
import pygame
import os
from utility import cwd_path


def sound_handle(track:str="ClickSound12" , action_type:str = "play", volume:int=100, channel:int=5, loop:bool=False):
    # a terminer


    sfx_path = os.path.join(cwd_path, "Assets", "Sfx", str(track) + ".wav")
    
    sfxchannel = pygame.mixer.Channel(channel)
    sound = pygame.mixer.Sound(sfx_path)
    sound.set_volume(volume/100)

    previous_volume = volume


    if action_type == "play" and loop == False:
        sfxchannel.play(sound)
    elif action_type == "play" and loop == True:
        sfxchannel.play(sound, loops=-1 if loop else 0)

    if action_type == "stop":
        pygame.mixer.Channel(channel).stop()

    if action_type == "break":
        sound.stop()

# faut test
    if action_type == "mute_all":
        sound.set_volume(0)

    if action_type == "unmute_all":
        sound.set_volume(previous_volume)



