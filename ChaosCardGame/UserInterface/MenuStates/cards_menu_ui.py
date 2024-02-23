import pygame
import utility
import os
from UserInterface.ui_settings import SCREEN_WIDTH, SCREEN_HEIGHT
from UserInterface.OcgVision.vision_main import State, ImageToggle, ToggleGridFour, ImageButton
from Assets.menu_assets import MenuBackgrounds, MenuToggles, MenuButtons, alpha_converter


class CardCollection:
    placeholder = (
        pygame.image.load(os.path.join(
            utility.cwd_path,
            "Assets/Graphics/Cards/Misc/card_not_found/s_card_not_found.png"
        )),
        pygame.image.load(os.path.join(
            utility.cwd_path,
            "Assets/Graphics/Cards/Misc/card_not_found/b_card_not_found.png"
        )),
    )
    def __init__(self, screen, element: str):
        self.screen = screen
        self.total = [
            (
            pygame.image.load(
                os.path.join(utility.cwd_path, dirpath, filenames[1])
            ),
            pygame.image.load(
                os.path.join(utility.cwd_path, dirpath, filenames[0])
            )
            )
            for (dirpath, _, filenames) in os.walk(os.path.join(utility.cwd_path, f"Assets/Graphics/Cards/{element.strip().title()}"))
            if len(filenames) > 1
        ]
        # 4 + 4 = 8
        if len(self.total) < 8:
            self.total += [self.placeholder] * (8 - len(self.total))
        self.left_side = ToggleGridFour(
            self.screen,
            self.total,
            475, 450,
            (50, 145),
            1.6, 1.0
        )
        self.right_side = ToggleGridFour(
            self.screen,
            self.total,
            475, 450,
            (SCREEN_WIDTH-475-10, 145),
            1.6, 1.0,
            start=4
        )
    def render(self):
        self.left_side.render()
        self.right_side.render()


class CardsMenu(State):
    def __init__(self, screen):
        self.screen = screen
        self.is_anchor = False
        self.local_options = ["CardsMenu"]
        super().__init__(self.screen, self.is_anchor, self.local_options)
        self.bg_cards_menu_image = MenuBackgrounds.bg_assets["cards_menu_empty"]["img"].convert_alpha(
        )
        self.bg_cards_menu_rect = self.bg_cards_menu_image.get_rect()

        self.exit_button = ImageButton(
            self.screen,
            True,
            image=alpha_converter(
                MenuButtons.button_assets["ExitArrow"]["img"]),
            position_type="topleft",
            position=(25, 25)
        )

        # Toggle Grids
        padding = 25
        object_width = MenuToggles.toggle_assets["AirToggle"]["img"][0].get_width(
        )
        number_of_toggles = 5
        total_width = SCREEN_WIDTH - 2 * padding - object_width * number_of_toggles
        gap_width = total_width / (number_of_toggles-1)
        toggle_xpos = [padding + object_width/2 +
                       (gap_width + object_width) * i for i in range(number_of_toggles)]
        # Toggles
        self.element_toggles = [
            ImageToggle(
                self.screen, "AirToggle", image=alpha_converter(MenuToggles.toggle_assets["AirToggle"]["img"]), position=(toggle_xpos[0], SCREEN_HEIGHT-20), position_type="midbottom"),
            ImageToggle(
                self.screen, "ChaosToggle", image=alpha_converter(MenuToggles.toggle_assets["ChaosToggle"]["img"]), position=(toggle_xpos[1], SCREEN_HEIGHT-20), position_type="midbottom"),
            ImageToggle(
                self.screen, "EarthToggle", is_toggled=True, image=alpha_converter(MenuToggles.toggle_assets["EarthToggle"]["img"]), position=(toggle_xpos[2], SCREEN_HEIGHT-20), position_type="midbottom"),
            ImageToggle(
                self.screen, "WaterToggle", image=alpha_converter(MenuToggles.toggle_assets["WaterToggle"]["img"]), position=(toggle_xpos[3], SCREEN_HEIGHT-20), position_type="midbottom"),
            ImageToggle(
                self.screen, "FireToggle", image=alpha_converter(MenuToggles.toggle_assets["FireToggle"]["img"]), position=(toggle_xpos[4], SCREEN_HEIGHT-20), position_type="midbottom")
        ]
        self.active_toggle = 2
        self.new_toggle = None

        # Init all cards and grids here
        # Tuple so immutable hence less memory
        self.grids: tuple[CardCollection, ...] = (
            CardCollection(self.screen, "air"),
            CardCollection(self.screen, "chaos"),
            CardCollection(self.screen, "earth"),
            CardCollection(self.screen, "water"),
            CardCollection(self.screen, "fire")
        )
    def cards_menu(self):
        self.screen.blit(self.bg_cards_menu_image, self.bg_cards_menu_rect)
        self.exit_button.render()
        if self.exit_button.answer() or pygame.key.get_pressed()[pygame.K_ESCAPE]:
            self.revert_state(1)
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
        self.grids[self.active_toggle].render()

    def state_manager_hook(self, app):
        if State.state_tree[1] == self.local_options[0]:
            self.cards_menu()
