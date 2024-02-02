import pygame
from UserInterface.ui_settings import SCREEN_CENTER
from UserInterface.OcgVision.vision_main import State, ImageButton
from UserInterface.OcgVision.vision_io import KeyRel
from Assets.menu_assets import MenuBackgrounds, MenuButtons, alpha_converter

class LoreMenu(State):
    def __init__(self, screen):
        self.screen = screen
        self.is_anchor = False
        self.local_options = ["LoreMenu"]
        
        super().__init__(self.screen, self.is_anchor, self.local_options)
        self.escp_rel = KeyRel(pygame.K_ESCAPE)
        self.space_rel = KeyRel(pygame.K_SPACE)

        self.lore_index = 0

        self.bg_lore1_menu_image = MenuBackgrounds.bg_lore1_image.convert_alpha()
        self.bg_lore2_menu_image = MenuBackgrounds.bg_lore2_image.convert_alpha()
        self.bg_lore3_menu_image = MenuBackgrounds.bg_lore3_image.convert_alpha()
        self.bg_lore4_menu_image = MenuBackgrounds.bg_lore4_image.convert_alpha()
        self.bg_lore5_menu_image = MenuBackgrounds.bg_lore5_image.convert_alpha()
        self.bg_lore6_menu_image = MenuBackgrounds.bg_lore6_image.convert_alpha()
        self.bg_lore7_menu_image = MenuBackgrounds.bg_lore7_image.convert_alpha()
        self.bg_lore8_menu_image = MenuBackgrounds.bg_lore8_image.convert_alpha()
        self.bg_lore9_menu_image = MenuBackgrounds.bg_lore9_image.convert_alpha()
        self.bg_lore10_menu_image = MenuBackgrounds.bg_lore10_image.convert_alpha()
        self.bg_lore11_menu_image = MenuBackgrounds.bg_lore11_image.convert_alpha()
        self.bg_lore12_menu_image = MenuBackgrounds.bg_lore12_image.convert_alpha()
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

    def lore_menu(self):
        self.screen.blit(self.bg_lore_images[self.lore_index],self.bg_lore_menu_rect)
        events = pygame.event.get()
        if self.escp_rel.update([e for e in events if e.type == pygame.KEYUP]):
            self.lore_index = 0
            self.revert_state()
        elif self.space_rel.update([e for e in events if e.type == pygame.KEYUP]):
            if self.lore_index == 11:
                self.lore_index = 0
                self.revert_state()
            elif self.lore_index < 11:
                self.lore_index += 1

        

    def state_manager_hook(self):
        if State.state_tree[1] == self.local_options[0]:
            self.lore_menu()