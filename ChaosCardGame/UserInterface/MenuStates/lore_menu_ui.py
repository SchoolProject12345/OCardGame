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
        self.bg_lore1_menu_image = MenuBackgrounds.bg_assets["lore_1_empty"]["processed_img"].convert_alpha()
        self.bg_lore2_menu_image = MenuBackgrounds.bg_assets["lore_2_empty"]["processed_img"].convert_alpha()
        self.bg_lore3_menu_image = MenuBackgrounds.bg_assets["lore_3_empty"]["processed_img"].convert_alpha()
        self.bg_lore4_menu_image = MenuBackgrounds.bg_assets["lore_4_empty"]["processed_img"].convert_alpha()
        self.bg_lore5_menu_image = MenuBackgrounds.bg_assets["lore_5_empty"]["processed_img"].convert_alpha()
        self.bg_lore6_menu_image = MenuBackgrounds.bg_assets["lore_6_empty"]["processed_img"].convert_alpha()
        self.bg_lore7_menu_image = MenuBackgrounds.bg_assets["lore_7_empty"]["processed_img"].convert_alpha()
        self.bg_lore8_menu_image = MenuBackgrounds.bg_assets["lore_8_empty"]["processed_img"].convert_alpha()
        self.bg_lore9_menu_image = MenuBackgrounds.bg_assets["lore_9_empty"]["processed_img"].convert_alpha()
        self.bg_lore10_menu_image = MenuBackgrounds.bg_assets["lore_10_empty"]["processed_img"].convert_alpha()
        self.bg_lore11_menu_image = MenuBackgrounds.bg_assets["lore_11_empty"]["processed_img"].convert_alpha()
        self.bg_lore12_menu_image = MenuBackgrounds.bg_assets["lore_12_empty"]["processed_img"].convert_alpha()
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
        events = pygame.event.get(pygame.KEYUP)
        if self.escp_rel.update([e for e in events if e.type == pygame.KEYUP]):
            self.lore_index = 0
            self.revert_state()
        elif self.space_rel.update([e for e in events if e.type == pygame.KEYUP]):
            if self.lore_index == 11:
                self.lore_index = 0
                self.revert_state()
            elif self.lore_index < 11:
                self.lore_index += 1

        

    def state_manager_hook(self,app):
        if State.state_tree[1] == self.local_options[0]:
            self.lore_menu()