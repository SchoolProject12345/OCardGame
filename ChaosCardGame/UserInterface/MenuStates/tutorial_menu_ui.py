import pygame
from UserInterface.ui_settings import SCREEN_CENTER
from UserInterface.OcgVision.vision_main import State, ImageButton
from UserInterface.OcgVision.vision_io import KeyRel
from Assets.menu_assets import MenuBackgrounds, MenuButtons, alpha_converter
from SfxEngine.SoundEngine import sound_handle
from utility import search_event


class TutorialMenu(State):
    def __init__(self, screen):
        self.screen = screen
        self.is_anchor = False
        self.local_options = ["TutorialMenu"]

        super().__init__(self.screen, self.is_anchor, self.local_options)
        self.escp_rel = KeyRel(pygame.K_ESCAPE)
        self.tutorial_index = 0
        self.bg_tutorial1_menu_image = MenuBackgrounds.bg_assets["tutorial1_empty"][
            "processed_img"
        ].convert_alpha()
        self.bg_tutorial2_menu_image = MenuBackgrounds.bg_assets["tutorial2_empty"][
            "processed_img"
        ].convert_alpha()
        self.bg_tutorial3_menu_image = MenuBackgrounds.bg_assets["tutorial3_empty"][
            "processed_img"
        ].convert_alpha()
        self.bg_tutorial4_menu_image = MenuBackgrounds.bg_assets["tutorial4_empty"][
            "processed_img"
        ].convert_alpha()
        self.bg_tutorial5_menu_image = MenuBackgrounds.bg_assets["tutorial5_empty"][
            "processed_img"
        ].convert_alpha()
        self.bg_tutorial6_menu_image = MenuBackgrounds.bg_assets["tutorial6_empty"][
            "processed_img"
        ].convert_alpha()
        self.bg_tutorial7_menu_image = MenuBackgrounds.bg_assets["tutorial7_empty"][
            "processed_img"
        ].convert_alpha()
        self.bg_tutorial8_menu_image = MenuBackgrounds.bg_assets["tutorial8_empty"][
            "processed_img"
        ].convert_alpha()
        self.bg_tutorial9_menu_image = MenuBackgrounds.bg_assets["tutorial9_empty"][
            "processed_img"
        ].convert_alpha()
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
        self.skiptutorial_button = ImageButton(
            self.screen,
            True,
            image=alpha_converter(
                MenuButtons.button_assets["SkipTutorial"]["processed_img"]
            ),
            position_type="topleft",
            position=(1105, 632),
        )

        self.nexttutorial_button = ImageButton(
            self.screen,
            True,
            image=alpha_converter(
                MenuButtons.button_assets["NextTutorial"]["processed_img"]
            ),
            position_type="topleft",
            position=(1105, 691),
        )

    def tutorial_menu(self):
        self.screen.blit(
            self.bg_tutorial_images[self.tutorial_index], self.bg_tutorial_menu_rect
        )
        self.skiptutorial_button.render()

        if self.tutorial_index < 8:
            self.nexttutorial_button.render()
            if self.nexttutorial_button.answer():
                self.tutorial_index += 1
                # Play the corresponding TutorialSpeech sound
                sound_handle(f"TutorialSpeech{self.tutorial_index + 1}", sfx_channel=7)

        if self.skiptutorial_button.answer() or self.escp_rel.update(
            search_event(super().events, pygame.KEYUP)
        ):
            self.tutorial_index = 0
            self.revert_state()
            sound_handle(action_type="stop", sfx_channel=7)

    def state_manager_hook(self, app):
        if State.state_tree[1] == self.local_options[0]:
            self.tutorial_menu()
