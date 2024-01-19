import pygame
import utility
import os
from UserInterface.ui_settings import SCREEN_WIDTH, SCREEN_HEIGHT
from UserInterface.OCG_Vision.vision_main import State, ImageToggle, ToggleGridFour, ImageButton
from Assets.menu_assets import MenuBackgrounds, CardsMenuToggles, MenuButtons, alpha_converter


class EarthCards():
    def __init__(self, screen):
        self.screen = screen
        self.image = pygame.image.load(
            os.path.join(utility.cwd_path, "Assets/Group 50.png")).convert_alpha()
        self.image_2 = pygame.image.load(
            os.path.join(utility.cwd_path, "Assets/Group 53.png")).convert_alpha()
        self.total = [[self.image], [self.image_2]]
        self.total_2 = [[self.image], [self.image_2]]
        self.left_side = ToggleGridFour(
            self.screen, [self.total, self.total, self.total, self.total], 475, 450, (25, 145), 0.78, 0.8)
        self.right_side = ToggleGridFour(
            self.screen, [self.total_2, self.total_2, self.total_2, self.total_2], 475, 450, (SCREEN_WIDTH-475-10, 145), 0.78, 0.8)

    def render(self):
        self.left_side.render()
        self.right_side.render()


class CardsMenu(State):
    def __init__(self, screen):
        self.screen = screen
        self.is_anchor = False
        self.local_options = ["CardsMenu"]
        super().__init__(self.screen, self.is_anchor, self.local_options)
        self.bg_cards_menu_image = MenuBackgrounds.bg_cards_menu_image.convert_alpha()
        self.bg_cards_menu_rect = self.bg_cards_menu_image.get_rect()
        # Exit Button
        self.exit_button = ImageButton(
            self.screen, True, image=MenuButtons.exit_arrow_button_image, position_type="topleft", position=(25, 25))
        # Toggle Grids
        padding = 25
        object_width = CardsMenuToggles.air_toggle_image[0][0].get_width()
        number_of_toggles = 5
        total_width = SCREEN_WIDTH - 2 * padding - object_width * number_of_toggles
        gap_width = total_width / (number_of_toggles-1)
        toggle_xpos = [padding + object_width/2 +
                       (gap_width + object_width) * i for i in range(number_of_toggles)]
        # Toggles
        self.element_toggles = [
            ImageToggle(
                self.screen, "AirToggle", image=alpha_converter(CardsMenuToggles.air_toggle_image), position=(toggle_xpos[0], SCREEN_HEIGHT-20), position_type="midbottom"),
            ImageToggle(
                self.screen, "ChaosToggle", image=alpha_converter(CardsMenuToggles.chaos_toggle_image), position=(toggle_xpos[1], SCREEN_HEIGHT-20), position_type="midbottom"),
            ImageToggle(
                self.screen, "EarthToggle", is_toggled=True, image=alpha_converter(CardsMenuToggles.earth_toggle_image), position=(toggle_xpos[2], SCREEN_HEIGHT-20), position_type="midbottom"),
            ImageToggle(
                self.screen, "WaterToggle", image=alpha_converter(CardsMenuToggles.water_toggle_image), position=(toggle_xpos[3], SCREEN_HEIGHT-20), position_type="midbottom"),
            ImageToggle(
                self.screen, "FireToggle", image=alpha_converter(CardsMenuToggles.fire_toggle_image), position=(toggle_xpos[4], SCREEN_HEIGHT-20), position_type="midbottom")
        ]
        self.active_toggle = -1
        self.new_toggle = None
        # Init all cards and grids here
        self.earth_grid = EarthCards(self.screen)

    def cards_menu(self):
        self.screen.blit(self.bg_cards_menu_image, self.bg_cards_menu_rect)
        self.exit_button.render()
        if self.exit_button.answer() or pygame.key.get_pressed()[pygame.K_ESCAPE]:
            self.revert_state()
        # Toggle selector
        for index, toggle in enumerate(self.element_toggles):
            if toggle.is_toggled:
                if index != self.active_toggle:
                    self.new_toggle = index
                else:
                    continue
            else:
                toggle.is_toggled = False
        if self.new_toggle != None:
            self.element_toggles[self.active_toggle].is_toggled = False
            self.active_toggle = self.new_toggle
            self.new_toggle = None
        for toggle in self.element_toggles:
            toggle.render()
            toggle.answer()
        # Cards
        if self.active_toggle == 2:
            self.earth_grid.render()

    def state_manager_hook(self):
        if self.local_state == self.local_options[0]:
            self.cards_menu()
