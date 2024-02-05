import pygame
from UserInterface.ui_settings import SCREEN_CENTER
from UserInterface.OcgVision.vision_main import State, ImageButton
from UserInterface.OcgVision.vision_io import KeyRel
from Assets.menu_assets import MenuBackgrounds, MenuButtons, alpha_converter
from SfxEngine.SoundEngine import sound_handle

class TutorialMenu(State):
    def __init__(self, screen):
        self.screen = screen
        self.is_anchor = False
        self.local_options = ["TutorialMenu"]
        
        super().__init__(self.screen, self.is_anchor, self.local_options)
        self.escp_rel = KeyRel(pygame.K_ESCAPE)

        self.tutorial_index = 0

        self.bg_tutorial1_menu_image = MenuBackgrounds.bg_tutorial1_image.convert_alpha()
        self.bg_tutorial2_menu_image = MenuBackgrounds.bg_tutorial2_image.convert_alpha()
        self.bg_tutorial3_menu_image = MenuBackgrounds.bg_tutorial3_image.convert_alpha()
        self.bg_tutorial4_menu_image = MenuBackgrounds.bg_tutorial4_image.convert_alpha()
        self.bg_tutorial5_menu_image = MenuBackgrounds.bg_tutorial5_image.convert_alpha()
        self.bg_tutorial6_menu_image = MenuBackgrounds.bg_tutorial6_image.convert_alpha()
        self.bg_tutorial7_menu_image = MenuBackgrounds.bg_tutorial7_image.convert_alpha()
        self.bg_tutorial8_menu_image = MenuBackgrounds.bg_tutorial8_image.convert_alpha()
        self.bg_tutorial9_menu_image = MenuBackgrounds.bg_tutorial9_image.convert_alpha()
        self.bg_tutorial_menu_rect = self.bg_tutorial1_menu_image.get_rect()
        
        self.bg_tutorial_images = []
        self.bg_tutorial_images.append(self.bg_tutorial1_menu_image)
        self.bg_tutorial_images.append(self.bg_tutorial2_menu_image)
        self.bg_tutorial_images.append(self.bg_tutorial3_menu_image)
        self.bg_tutorial_images.append(self.bg_tutorial4_menu_image)
        self.bg_tutorial_images.append(self.bg_tutorial5_menu_image)
        self.bg_tutorial_images.append(self.bg_tutorial6_menu_image)
        self.bg_tutorial_images.append(self.bg_tutorial7_menu_image)
        self.bg_tutorial_images.append(self.bg_tutorial8_menu_image)
        self.bg_tutorial_images.append(self.bg_tutorial9_menu_image)
        
        # Buttons
        self.endtutorial_button = ImageButton(self.screen, True, image=alpha_converter(
            MenuButtons.endtutorial_button_image),position_type="topleft", position=(1105,632))
        self.nexttutorial_button = ImageButton(self.screen, True, image=alpha_converter(
            MenuButtons.nexttutorial_button_image),position_type="topleft",position=(1105,691))
        

    def tutorial_menu(self):
        self.screen.blit(self.bg_tutorial_images[self.tutorial_index], self.bg_tutorial_menu_rect)
        self.endtutorial_button.render()

        if self.tutorial_index < 8:
            self.nexttutorial_button.render()
            if self.nexttutorial_button.answer():
                self.tutorial_index += 1

                sound_handle(f"TutorialSpeech{self.tutorial_index + 1}", sfx_channel= 7)


        if self.endtutorial_button.answer() or self.escp_rel.update(pygame.event.get(pygame.KEYUP)):
            self.tutorial_index = 0
            self.revert_state()
            sound_handle(action_type="stop", sfx_channel=7)
        

    def state_manager_hook(self,app):
        if State.state_tree[1] == self.local_options[0]:
            self.tutorial_menu()