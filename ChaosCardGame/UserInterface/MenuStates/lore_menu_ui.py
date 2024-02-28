import pygame
from SfxEngine.SoundEngine import sound_handle
from UserInterface.ui_settings import SCREEN_CENTER
from UserInterface.OcgVision.vision_main import State, ImageButton
from UserInterface.OcgVision.vision_io import KeyRel
from Assets.menu_assets import MenuBackgrounds, MenuButtons, alpha_converter
from utility import search_event


class LoreMenu(State):
    def __init__(self, screen):
        self.screen = screen
        self.is_anchor = False
        self.local_options = ["LoreMenu"]

        super().__init__(self.screen, self.is_anchor, self.local_options)
        self.escp_rel = KeyRel(pygame.K_ESCAPE)
        self.space_rel = KeyRel(pygame.K_SPACE)

        self.lore_index = 0
        self.bg_lore1_menu_image = MenuBackgrounds.bg_assets["lore_1_empty"]["img"].convert_alpha(
        )
        self.bg_lore2_menu_image = MenuBackgrounds.bg_assets["lore_2_empty"]["img"].convert_alpha(
        )
        self.bg_lore3_menu_image = MenuBackgrounds.bg_assets["lore_3_empty"]["img"].convert_alpha(
        )
        self.bg_lore4_menu_image = MenuBackgrounds.bg_assets["lore_4_empty"]["img"].convert_alpha(
        )
        self.bg_lore5_menu_image = MenuBackgrounds.bg_assets["lore_5_empty"]["img"].convert_alpha(
        )
        self.bg_lore6_menu_image = MenuBackgrounds.bg_assets["lore_6_empty"]["img"].convert_alpha(
        )
        self.bg_lore7_menu_image = MenuBackgrounds.bg_assets["lore_7_empty"]["img"].convert_alpha(
        )
        self.bg_lore8_menu_image = MenuBackgrounds.bg_assets["lore_8_empty"]["img"].convert_alpha(
        )
        self.bg_lore9_menu_image = MenuBackgrounds.bg_assets["lore_9_empty"]["img"].convert_alpha(
        )
        self.bg_lore10_menu_image = MenuBackgrounds.bg_assets["lore_10_empty"]["img"].convert_alpha(
        )
        self.bg_lore11_menu_image = MenuBackgrounds.bg_assets["lore_11_empty"]["img"].convert_alpha(
        )
        self.bg_lore12_menu_image = MenuBackgrounds.bg_assets["lore_12_empty"]["img"].convert_alpha(
        )
        self.bg_lore_menu_rect = self.bg_lore1_menu_image.get_rect()

        self.bg_lore_images = []
        self.bg_lore_images.append(self.bg_lore1_menu_image)
        self.bg_lore_images.append(self.bg_lore2_menu_image)
        self.bg_lore_images.append(self.bg_lore3_menu_image)
        self.bg_lore_images.append(self.bg_lore4_menu_image)
        self.bg_lore_images.append(self.bg_lore5_menu_image)
        self.bg_lore_images.append(self.bg_lore6_menu_image)
        self.bg_lore_images.append(self.bg_lore7_menu_image)
        self.bg_lore_images.append(self.bg_lore8_menu_image)
        self.bg_lore_images.append(self.bg_lore9_menu_image)
        self.bg_lore_images.append(self.bg_lore10_menu_image)
        self.bg_lore_images.append(self.bg_lore11_menu_image)
        self.bg_lore_images.append(self.bg_lore12_menu_image)

        # Buttons
        self.skiplore_button = ImageButton(
            self.screen,
            True,
            image=alpha_converter(
                MenuButtons.button_assets["Skip"]["img"]
            ),
            position_type="topleft",
            position=(1105, 632),
        )

        self.nextlore_button = ImageButton(
            self.screen,
            True,
            image=alpha_converter(
                MenuButtons.button_assets["Next"]["img"]
            ),
            position_type="topleft",
            position=(1105, 691),
        )

    def lore_menu(self):
        self.screen.blit(
            self.bg_lore_images[self.lore_index], self.bg_lore_menu_rect)
        events = search_event(super().events, pygame.KEYDOWN)


        if self.lore_index < 6:
            self.skiplore_button.render()
            self.nextlore_button.render()
            if self.nextlore_button.answer():
                if self.lore_index == 11:
                    self.lore_index = 0
                    self.revert_state()
                    sound_handle(action_type="stop", channel=7)
                elif self.lore_index < 11:
                    self.lore_index += 1
                    sound_handle(f"LoreSpeech{self.lore_index + 1}", channel= 7)

        if self.space_rel.update(search_event(super().events, pygame.KEYUP)):
            if self.lore_index == 11:
                self.lore_index = 0
                self.revert_state()
                sound_handle(action_type="stop", channel=7)
            elif self.lore_index < 11:
                self.lore_index += 1
                sound_handle(f"LoreSpeech{self.lore_index + 1}", channel= 7)

        if self.escp_rel.update(search_event(super().events, pygame.KEYUP)):
            self.lore_index = 0
            self.revert_state()
            sound_handle(action_type="stop", channel=7)

    def state_manager_hook(self, app):
        if State.state_tree[1] == self.local_options[0]:
            self.lore_menu()
