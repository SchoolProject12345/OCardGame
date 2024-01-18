from UserInterface.OCG_Vision.vision_main import State, ImageButton
from Assets.menu_assets import MenuBackgrounds, MenuButtons, alpha_converter
from UserInterface.ui_settings import SCREEN_CENTER

class GameMenu(State):
    def __init__(self,screen):
        self.screen = screen
        self.is_anchor = True
        self.local_options = ["GameMenu"]
        super().__init__(self.screen, self.is_anchor, self.local_options)

        self.bg_game_menu_image = MenuBackgrounds.bg_game_menu_image.convert_alpha()
        self.bg_game_menu_rect = self.bg_game_menu_image.get_rect()

    def game_menu(self):
        self.screen.blit(self.bg_game_menu_image, self.bg_game_menu_rect)

    def state_manager_hook(self):
        if self.local_state == self.local_options[0]:
            self.game_menu()