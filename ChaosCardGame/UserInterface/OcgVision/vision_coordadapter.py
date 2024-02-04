import pygame


def midleft2topleft(coord: tuple, height: int):
    return (coord[0], coord[1]-(height/2))


def bottomleft2topleft(coord, height):
    return (coord[0], coord[1]-height)


def midtop2topleft(coord, width):
    return (coord[0]-(width/2), coord[1])


def center2topleft(coord, width, height):
    return (coord[0]-(width/2), coord[1]-(height/2))


def midbottom2topleft(coord, width, height):
    return (coord[0]-(width/2), coord[1]-(height/2))


def topright2topleft(coord, width):
    return (coord[0]-width, coord[1])


def midright2topleft(coord, width, height):
    return (coord[0]-width, coord[1]-(height/2))


def bottomright2topleft(coord, width, height):
    return (coord[0]-width, coord[1]-height)


def coord_converter(position_type, coord, width=0, height=0):
    """
    Converts a given position from various types to top-left coordinates.

    This function accepts a position and its type (e.g., center, midbottom, topright) and,
    depending on the type, utilizes different helper functions to convert it into top-left
    coordinates. The conversion can optionally consider the dimensions of the object being
    positioned, specified by width and height, which default to 0.

    Attributes:
    - position_type (str): The type description of the given position. It determines how the
      conversion to top-left coordinates is performed. Supported types include "topleft",
      "midleft", "bottomleft", "midtop", "center", "midbottom", "topright", "midright",
      and "bottomright".
    - coord (tuple): The starting position specified as a tuple (x, y) to be converted.
    - width (int, optional): The width of the object at the given position, required for some
      position types. Defaults to 0.
    - height (int, optional): The height of the object at the given position, required for some
      position types. Defaults to 0.

    Returns:
    - tuple: The converted position as top-left coordinates (x, y).

    Raises:
    - Exception: If an unknown position_type is specified.
    """
    match position_type:
        case "topleft":
            return coord
        case "midleft":
            return midleft2topleft(coord, height)
        case "bottomleft":
            return bottomleft2topleft(coord, height)
        case "midtop":
            return midtop2topleft(coord, width)
        case "center":
            return center2topleft(coord, width, height)
        case "midbottom":
            return midbottom2topleft(coord, width, height)
        case "topright":
            return topright2topleft(coord, width)
        case "midright":
            return midright2topleft(coord, width)
        case "bottomright":
            return bottomright2topleft(coord, width, height)
        case _:
            raise "Unknown pos_type."


def coord_grid(position: tuple, position_type: str, dimensions: tuple, alignement: tuple) -> None:
    x_div_factor = dimensions[0] / alignement[0]
    y_div_factor = dimensions[1] / alignement[1]
    adapted_position = coord_converter(
        position_type, position, dimensions[0], dimensions[1])

    x_grid_coord = [(x_div_factor * factor) + (x_div_factor / 2) +
                    adapted_position[0] for factor in range(alignement[0])]
    y_grid_coord = [(y_div_factor * factor) + (y_div_factor / 2) +
                    adapted_position[1] for factor in range(alignement[1])]

    assembled_grid_coord = [[x_layer, y_layer]
                            for y_layer in y_grid_coord for x_layer in x_grid_coord]

    return assembled_grid_coord


def rect_grid(position: tuple, position_type: str, dimensions: tuple, alignement: tuple,
              x_inter_padding: int = 0, y_inter_padding: int = 0, return_rect_values: bool = True):
    """
    Generates a grid of rectangles with or without pygame Rect objects.

    This function creates a grid of rectangle positions based on the specified
    dimensions, alignment, padding between rectangles, and the conversion of the initial
    position to top left according to the specified position type.

    Attributes:
    - position (tuple): The starting position of the grid.
    - position_type (str): The type of the provided position. Used for conversion.
    - dimensions (tuple): The dimensions (width, height) for the grid area.
    - alignement (tuple): The layout (columns, rows) of the grid.
    - x_inter_padding (int, optional): The horizontal padding between rectangles. Defaults to 0.
    - y_inter_padding (int, optional): The vertical padding between rectangles. Defaults to 0.
    - return_rect_values (bool, optional): Determines if the returned grid contains pygame.Rect
      objects (True) or just the rectangle coordinates and dimensions (False). Defaults to True.

    Returns:
    - list: A list containing the rectangles of the grid, either as pygame.Rect objects or as
      tuples with rectangle coordinates and dimensions, depending on the return_rect_values flag.
    """
    x_div_factor = (dimensions[0]-((alignement[0]-1) *
                    x_inter_padding)) / alignement[0]
    y_div_factor = (dimensions[1]-((alignement[1]-1) *
                    y_inter_padding)) / alignement[1]
    adapted_pos = coord_converter(
        position_type, position, dimensions[0], dimensions[1])

    x_grid_points = [(x_div_factor*factor)+(x_inter_padding*factor)+(adapted_pos[0])
                     for factor in range(alignement[0])]
    y_grid_points = [(y_div_factor*factor)+(x_inter_padding*factor)+(adapted_pos[1])
                     for factor in range(alignement[1])]

    curated_grid_rects = [[(x_layer, y_layer), (x_div_factor, y_div_factor)]
                          for x_layer in x_grid_points for y_layer in y_grid_points]

    if return_rect_values:
        curated_grid_rects = [pygame.Rect(values[0], values[1])
                              for values in curated_grid_rects]
        return curated_grid_rects
    else:
        return curated_grid_rects

# print(rect_grid((0, 0), "topleft", (500, 303),
#                 (6, 1), 12, return_rect_values=False))
