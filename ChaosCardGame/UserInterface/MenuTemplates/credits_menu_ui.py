import pygame
from UserInterface.OcgVision.vision_main import State, ImageButton
from Assets.menu_assets import MenuBackgrounds, MenuButtons, alpha_converter
from UserInterface.ui_settings import SCREEN_CENTER
 

class CreditsMenu(State):
    def __init__(self, screen):
        super().__init__(screen, False, ["CreditsMenu"])

        self.bg_credits_menu_image = MenuBackgrounds.bg_credits_menu_image.convert_alpha()
        self.bg_credits_menu_rect = self.bg_credits_menu_image.get_rect(
            topleft=(0, 0))

        self.button = ImageButton(self.screen, True, image=alpha_converter(MenuButtons.exit_button_image),
                                  position_type="center", position=(SCREEN_CENTER[0], SCREEN_CENTER[1]+302))

    def credits_menu(self):
        self.screen.blit(self.bg_credits_menu_image, self.bg_credits_menu_rect)
        self.button.render()

        if self.button.answer() or pygame.key.get_pressed()[pygame.K_ESCAPE]:
            self.revert_state(1)

    def state_manager_hook(self):
        if self.local_state == self.local_options[0]:
            self.credits_menu()
