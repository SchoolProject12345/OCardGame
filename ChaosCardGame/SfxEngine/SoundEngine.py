## Berda's Soung engine v0.5
from pygame import mixer
import pygame
import os
from utility import cwd_path


def sound_handle(track:str="ClickSound12" , action_type:str = "play", volume:int=100, sfx_channel:int=5):
    # a terminer


    sfx_path = os.path.join(cwd_path, "Assets", "Sfx", str(track) + ".wav")
    
    sfxchannel = pygame.mixer.Channel(sfx_channel)
    sound = pygame.mixer.Sound(sfx_path)
    sound.set_volume(volume/100)

    pygame.mixer.music.load(sfx_path)
    pygame.mixer.music.set_volume(volume/100)
    previous_volume = volume

    if action_type == "play":
        sfxchannel.play(sound)

    if action_type == "stop":
        pygame.mixer.Channel(sfx_channel).stop()

    if action_type == "ambient_play":
        pygame.mixer.music.play()

    if action_type == "ambient_pause":
        pygame.mixer.music.pause()


    if action_type == "break":
        pygame.mixer.music.stop()
        sound.stop()

# faut test
    if action_type == "mute_all":
        sound.set_volume(0)
        pygame.mixer.music.set_volume(0)

    if action_type == "unmute_all":
        sound.set_volume(previous_volume)
        pygame.mixer.music.set_volume(previous_volume)

