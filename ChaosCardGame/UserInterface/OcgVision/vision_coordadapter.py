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


def coordconverter(position_type, coord, width=0, height=0):
    match position_type:
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
