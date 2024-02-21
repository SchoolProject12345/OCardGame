import pygame
# Debug Settings
load_cards = True
load_menus = True


def ValueWatcher(surface, value):
    ft_helvetica = pygame.font.SysFont("Helvetica", 50)
    value_surface = ft_helvetica.render(str(value), True, (255, 255, 255))
    value_rect = value_surface.get_rect(topleft=(0, 0))
    surface.blit(value_surface, value_rect)
