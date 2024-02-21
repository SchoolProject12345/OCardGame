import pygame
import inspect
from UserInterface.OcgVision.vision_coordadapter import coord_converter
from UserInterface.ui_settings import SCREEN_CENTER
from Assets.menu_assets import smoothscale_converter
from SfxEngine.SoundEngine import sound_handle


class State:
    """
    A class to represent a state.

    ...

    Parameters
    ----------
    `state` : `str`
        A string representing the current state
    `previous_state` : `list`
        A list to hold the previous state(s)
    screen : `pygame.Surface`
        The game screen to display the state on
    is_anchor : `bool`
        A flag indicating if the state is an anchor state
    local_options : `list`
        A list of state options valid in the local context

    Methods
    -------
    `__init__`(self, screen, is_anchor, local_options):
        Constructs all the necessary attributes for the state object.

    `change_state`(self, new_state):
        Changes the current state to a new state.

    `revert_state`(self,n_revert):
        Reverts the current state n_revert times if not an anchor state.

    `check_ownership`(self):
        Checks if the current global state is within the local state options and assigns it as the local state.

    `state_manager_hook`(self):
        Placeholder method to be overridden by subclasses.

    `state_manager`(self):
        Checks state ownership and runs the state_manager_hook.

    """

    state_tree = ["MainMenu"]
    events = []

    def __init__(
        self, screen: pygame.surface.Surface, is_anchor: bool, local_options: list
    ):
        self.screen = screen
        self.is_anchor = is_anchor
        self.local_options = local_options
        # Option on index 0 is always the default one.

    def change_state(self, new_state: str):
        """
        Changes the current state to a new state.

        Parameters:
            new_state : str
                The new state to change to

        """
        State.state_tree.append(new_state)

    def revert_state(self, n_revert: int = 1):
        """
        Reverts the current state n_revert times if not an anchor state.
        """
        for _ in range(n_revert):
            State.state_tree.pop()

        State.new_menu = True

    def state_manager_hook(self, app=0):
        """
        Placeholder method to be overridden by subclasses.

        """
        pass

    def state_manager(self, app):
        """
        Checks state ownership and runs the state_manager_hook.

        """
        self.state_manager_hook(app)


class ImageButton:
    """
    Creates an instance of a usable button with effects.

    Parameters
    ---------
    `screen` : `pygame.surface.Surface`
        Screen to draw the button to.
    `call_back` : `bool` or `function`
        Value to return when the button is triggered.
    `image` : `list [pygame.Surface]`
        Image to be displayed. Idle, Hover, Clicked.
    `position_type` : `str` (optional)
        Type of position for the coordinates.
    `position` : `tuple | list` (optional)
        Coordinates for displaying the button.
    `factor` : `int` (optional)
        Factor by which the button must be scaled.

    Methods
    --------
    `render` -> `None`
        Renders the button on the screen.
    `answer` -> `any`
        Returns the call_back if clicked.
    """

    all_states = ["idle", "hover", "click"]

    def __init__(self, screen, call_back, **kwargs):
        self.screen = screen
        self.state = self.all_states[0]
        self.call_back = call_back
        # Core Attributes
        self.button_image = kwargs.get("image", None)
        self.position_type = kwargs.get("position_type", "center")
        self.position = kwargs.get("position", (0, 0))
        self.factor = kwargs.get("factor", 1)
        self.previous_state = self.state

        while len(self.button_image) < 3:
            self.button_image.append(self.button_image[0])

        for image in self.button_image:
            image = pygame.transform.scale_by(image, self.factor)

        self.button_rect = self.button_rect = self.button_image[0].get_rect(
            **{self.position_type: self.position}
        )

    def render(self) -> None:
        """
        Checks the state of the button and blits the corresponding surface on the screen.

        """
        self.previous_state = self.state

        self.check_state()

        if self.state == self.all_states[0]:
            self.screen.blit(self.button_image[0], self.button_rect)
        elif self.state == self.all_states[1]:
            self.screen.blit(self.button_image[1], self.button_rect)
        elif self.state == self.all_states[2]:
            self.screen.blit(self.button_image[2], self.button_rect)

        if self.state == self.all_states[2] and self.previous_state == self.all_states[1]:
            # On click sound handler
            sound_handle("ClickSound1-2", "play", 40)

        if self.state == self.all_states[1] and self.previous_state == self.all_states[2]:
            # On click sound handler
            sound_handle("ClickSound2-1", "play", 40)

    def check_state(self) -> None:
        """
        Checks mouse position and click state to decide the state of the button.

        """
        self.mouse_pos = pygame.mouse.get_pos()
        self.mouse_click = pygame.mouse.get_pressed()

        if self.button_rect.collidepoint(self.mouse_pos):
            self.state = self.all_states[1]
            if self.mouse_click[0]:
                self.state = self.all_states[2]
        else:
            self.state = self.all_states[0]

    def answer(self) -> any:
        """
        Checks if the mouse is clicked on the button i.e button is in click state
        and if so execute the callback function or return the callback object.

        Returns
        -------
        `call_back` : `Any`
            Result of the `call_back` parameter.

        """
        if (
            self.previous_state == self.all_states[2]
            and self.state == self.all_states[1]
        ):
            if isinstance(self.call_back, pygame.event.Event):
                pygame.event.post(self.call_back)
            elif inspect.isfunction(self.call_back):
                return self.call_back()
            else:
                return self.call_back


class ImageToggle:
    """
    Create a  image based toggle.

    Parameters
    -------
    `screen`: `pygame.Surface`
        The screen the toggle is displayed on.
    `call_back`: `Any`
        Action to execute when button is toggled.
    `is_toggled`: `bool`
        Default position of the toggle.
    `factor`: `int`
        The factor by which to scale the image.
    `image`: `list[list,list]`
        List containing all states for the toggle.
    `position_type`: `str`
        The default position type of the toggle. (center, midbottom, etc...)
    `position_type_T` = `position_type`: `str`
        The position while toggled.
    `position`: `tuple[x,y]`:
        The default position.
    `position_T` = `position`: `tuple[x,y]`
        The default toggle position.

    Methods
    ---------
    def render(self): -> None
        Renders the button on the screen.
    def answer(self): -> None
        Returns the call_back based on toggle state.

    """

    all_states = ["idle", "hover", "click"]

    def __init__(self, screen, call_back, **kwargs):
        self.screen = screen
        self.state = self.all_states[0]
        self.call_back = call_back

        # Combined toggles
        self.is_toggled = kwargs.get("is_toggled", False)
        self.previous_state = self.state
        self.factor = kwargs.get("factor", 1)
        self.all_image = kwargs.get("image", None)
        # Core Attributes for untoggled state
        self.toggle_image = kwargs.get("toggle_image", self.all_image[0:3])
        self.position_type = kwargs.get("position_type", "center")
        self.position = kwargs.get("position", (0, 0))

        # Core Attributes for toggled state
        self.toggle_image_T = kwargs.get("toggle_image_T", self.all_image[3:6])
        self.position_type_T = kwargs.get(
            "position_type_T", self.position_type)
        self.position_T = kwargs.get("position_T", self.position)

        # Image processing
        for image_group in [self.toggle_image, self.toggle_image_T]:
            while len(image_group) < 3:
                image_group.append(image_group[0])
            for image in image_group:
                image = pygame.transform.scale_by(image, self.factor)

        # Position processing
        self.toggle_rect = self.toggle_image[0].get_rect(
            **{self.position_type: self.position}
        )
        self.toggle_rect_T = self.toggle_image_T[0].get_rect(
            **{self.position_type_T: self.position_T}
        )

    def render(self):
        self.previous_state = self.state

        self.check_state()

        if self.state == self.all_states[0] and self.is_toggled:
            self.screen.blit(self.toggle_image_T[0], self.toggle_rect_T)
        elif self.state == self.all_states[0]:
            self.screen.blit(self.toggle_image[0], self.toggle_rect)
        elif self.state == self.all_states[1] and self.is_toggled:
            self.screen.blit(self.toggle_image_T[1], self.toggle_rect_T)
        elif self.state == self.all_states[1]:
            self.screen.blit(self.toggle_image[1], self.toggle_rect)
        elif self.state == self.all_states[2] and self.is_toggled:
            self.screen.blit(self.toggle_image_T[2], self.toggle_rect_T)
        elif self.state == self.all_states[2]:
            self.screen.blit(self.toggle_image[2], self.toggle_rect)

    def check_state(self):
        self.mouse_pos = pygame.mouse.get_pos()
        self.mouse_click = pygame.mouse.get_pressed()

        if self.is_toggled:
            if self.toggle_rect_T.collidepoint(self.mouse_pos):
                self.state = self.all_states[1]
                if self.mouse_click[0]:
                    self.state = self.all_states[2]
            else:
                self.state = self.all_states[0]
        else:
            if self.toggle_rect.collidepoint(self.mouse_pos):
                self.state = self.all_states[1]
                if self.mouse_click[0]:
                    self.state = self.all_states[2]
            else:
                self.state = self.all_states[0]

    def answer(self) -> any:
        if (
            self.previous_state == self.all_states[2]
            and self.state == self.all_states[1]
        ):
            self.change_toggle()
        if self.is_toggled:
            if isinstance(self.call_back, pygame.event.Event):
                pygame.event.post(self.call_back)
            elif inspect.isfunction(self.call_back):
                return self.call_back()
            else:
                return self.call_back

    def change_toggle(self):
        if self.is_toggled:
            self.is_toggled = False
        else:
            self.is_toggled = True


class ToggleGridFour:
    """
    Aligns 4 toggles in a 2x2 grid.

    Parameters
    ----------
    `mother_surface`: `pygame.Surface`
        The surface to render the toggles on.
    `image`: `list`
        A list containg 4 lists containing all images for the toggles.
    `grid_width`: `int`
        The width of the grid.
    `grid_height`: `int`
        The height of the grid.
    `initial_pos`: `tuple`
        A tuple containing (x,y)
    `factor`: `int`
        The scaling factor for untoggled state.
    `factor_T`: `int`
        The scaling facor for toggled state.

    Methods
    -------
    def render(self): -> None
        Renders the grid.
    """

    def __init__(
        self,
        mother_surface,
        images,
        grid_width,
        grid_height,
        initial_pos,
        factor=1,
        factor_T=1,
    ):
        self.mother_surface = mother_surface
        self.width = grid_width
        self.height = grid_height
        self.all_images = images
        self.toggles = []
        for i_1, toggle in enumerate(self.all_images):
            if i_1 < 2:
                self.all_images[i_1] = smoothscale_converter(toggle, factor)
            else:
                self.all_images[i_1] = smoothscale_converter(toggle, factor_T)

        self.card_width = self.all_images[0][0].get_width()
        self.card_height = self.all_images[0][0].get_height()
        self.initial_pos = initial_pos
        self.top_left = self.initial_pos
        self.top_right = (
            self.initial_pos[0] + self.width / 2 + self.card_width,
            self.initial_pos[1],
        )
        self.bottom_left = (
            self.initial_pos[0],
            self.initial_pos[1] + self.height / 2 + self.card_height,
        )
        self.bottom_right = (
            self.initial_pos[0] + self.width / 2 + self.card_height,
            self.initial_pos[1] + self.height / 2 + self.card_height,
        )
        self.positions = [
            ["topleft", self.initial_pos],
            ["topright", self.top_right],
            ["bottomleft", self.bottom_left],
            ["bottomright", self.bottom_right],
        ]
        for index, image in enumerate(self.all_images):
            self.toggles.append(
                ImageToggle(
                    self.mother_surface,
                    True,
                    image=image,
                    position_type=self.positions[index][0],
                    position=self.positions[index][1],
                )
            )

    def render(self):
        self.priority = None
        for idx, toggle in enumerate(self.toggles):
            if toggle.state == "hover":
                self.priority = self.toggles[idx]
            else:
                toggle.render()
                toggle.answer()
        if self.priority != None:
            self.priority.render()
            self.priority.answer()


class DualBarHori:
    """
    Creates a horizontal dual bar to display two values.

    Args:
        screen: `pygame.Surface`
            The screen to render the bar on.
        position: `tuple`
            The position of the bar.
        position_type: `str`
            The position type of the bar.
        width: `int`
            The width of the bar.
        height: `int`
            The height of the bar.
        color_bg: `pygame.Color`
            The background color of the bar.
        color_fg: `pygame.Color`
            The foreground color of the bar.
        max_value: `int`
            The maximum value of the bar.
    """

    def __init__(
        self,
        screen: pygame.Surface,
        position: tuple,
        position_type: str,
        width: int,
        height: int,
        color_bg: pygame.Color | tuple,
        color_fg: pygame.Color | tuple,
        max_value: int,
        **kwargs,
    ) -> None:
        self.screen = screen
        self.position = position
        self.position_type = position_type
        self.width = width
        self.height = height
        self.color_bg = color_bg
        self.color_fg = color_fg
        self.border_radius = kwargs.get("border_radius", 0)
        self.max_value = max_value
        self.health = self.max_value

    def update(self, health: int) -> None:
        self.health = health
        self.health_percent = self.health / self.max_value
        self.health_width = self.health_percent * self.width

    def render(self, health: int):
        """Renders and maintains the bar.

        Args:
            health (int): The current health of the bar.
        """
        self.update(health)
        pygame.draw.rect(
            self.screen,
            self.color_bg,
            (self.position[0], self.position[1], self.width, self.height),
            border_radius=self.border_radius,
        )
        pygame.draw.rect(
            self.screen,
            self.color_fg,
            (self.position[0], self.position[1],
             self.health_width, self.height),
            border_radius=self.border_radius,
        )


class DualBarVerti:
    """
    Creates a vertical dual bar to display two values.

    Args:
        screen: `pygame.Surface`
            The screen to render the bar on.
        position: `tuple`
            The position of the bar.
        position_type: `str`
            The position type of the bar.
        width: `int`
            The width of the bar.
        height: `int`
            The height of the bar.
        color_bg: `pygame.Color`
            The background color of the bar.
        color_fg: `pygame.Color`
            The foreground color of the bar.
        max_value: `int`
            The maximum value of the bar.
    """

    def __init__(
        self,
        screen: pygame.Surface,
        position: tuple,
        position_type: str,
        width: int,
        height: int,
        color_bg: pygame.Color | tuple,
        color_fg: pygame.Color | tuple,
        max_value: int,
        **kwargs,
    ) -> None:
        self.screen = screen
        self.position = position
        self.position_type = position_type
        self.width = width
        self.height = height
        self.color_bg = color_bg
        self.color_fg = color_fg
        self.border_radius = kwargs.get("border_radius", 0)
        self.max_value = max_value
        self.health = self.max_value

    def update(self, health: int) -> None:
        self.health = health
        self.health_percent = self.health / self.max_value
        self.health_height = int(self.health_percent * self.height)

    def render(self, health: int, rotate: bool = False):
        """Renders and maintains the bar, optionally rotated by 180 degrees.

        Args:
            health (int): The current health of the bar.
            rotate (bool, optional): Whether to rotate the bar by 180 degrees. Defaults to False.
        """
        self.update(health)

        temp_surface = pygame.Surface(
            (self.width, self.height), pygame.SRCALPHA)

        pygame.draw.rect(
            temp_surface,
            self.color_bg,
            (0, 0, self.width, self.height),
            border_radius=self.border_radius,
        )

        pygame.draw.rect(
            temp_surface,
            self.color_fg,
            (0, self.height-self.health_height, self.width, self.health_height),
            border_radius=self.border_radius,
        )

        if rotate:
            temp_surface = pygame.transform.rotate(temp_surface, 180)
            new_position = self.position[0] - (temp_surface.get_width() - self.width) // 2, \
                self.position[1] - \
                (temp_surface.get_height() - self.height) // 2
        else:
            new_position = self.position

        self.screen.blit(temp_surface, new_position)


class SelectTextBox:
    def __init__(self, screen: pygame.Surface,
                 position: tuple,
                 width: int, height: int,
                 font: pygame.font.Font,
                 default_color: tuple,
                 color: tuple,
                 position_type: str = "topleft",
                 text_center="left",
                 border_width=-1,
                 default_text=""):
        self.screen = screen
        self.position = position
        self.width = width
        self.height = height
        self.font = font
        self.default_color = default_color
        self.color = color
        self.position_type = position_type
        self.text_center = text_center
        self.border_width = border_width
        self.default_text = default_text

        self.text = self.default_text
        self.active = False
        self.input_rect = pygame.Rect(coord_converter(
            self.position_type, self.position, self.width, self.height), (self.width, self.height))

    def calc_left(self):
        self.text_rect = self.text_surf.get_rect(
            midleft=(self.input_rect.x, self.input_rect.y+(self.height//2)))

    def calc_center(self):
        self.text_rect = self.text_surf.get_rect(
            center=(self.input_rect.x+(self.width//2), self.input_rect.y+(self.height//2)))

    def calc_right(self):
        self.text_rect = self.text_surf.get_rect(
            midright=(self.input_rect.x+self.width,
                      self.input_rect.y+(self.height//2))
        )

    def update(self, key_events):
        if self.input_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            self.active = True
        elif not self.input_rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            self.active = False
        if self.active:
            for event in key_events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        self.text = self.text[:-1]
                    elif event.key == pygame.K_RETURN:
                        self.active = False
                    elif self.text_rect.width < self.input_rect.width:
                        self.text += event.unicode

        if self.active == False and self.text == "":
            self.text = self.default_text
        elif self.active and self.text == self.default_text:
            self.text = ""

        if self.active == False and self.text == self.default_text:
            self.active_color = self.default_color
        else:
            self.active_color = self.color

    def render(self, key_events: pygame.event.Event):
        # Event handler
        self.update(key_events)

        # Rendering
        pygame.draw.rect(self.screen, (255, 255, 255),
                         self.input_rect, width=self.border_width)
        self.text_surf = self.font.render(self.text, True, self.active_color)
        match self.text_center:
            case "left": self.calc_left()
            case "center": self.calc_center()
            case "right": self.calc_right()
            case _: raise ValueError(f"Wrong argument {self.text_center}")
        self.screen.blit(
            self.text_surf, (self.text_rect.x + 4, self.text_rect.y))
        return self.text


class TextBox:
    def __init__(self, screen: pygame.surface.Surface,
                 position: tuple,
                 width: int, height: int,
                 font: pygame.font.Font,
                 color: tuple,
                 position_type: str = "topleft",
                 text_center: str = "left",
                 text: str = ""):
        self.screen = screen
        self.position = position
        self.width = width
        self.height = height
        self.font = font
        self.color = color
        self.position_type = position_type
        self.text_center = text_center
        self.text = text

        self.input_rect = pygame.Rect(coord_converter(
            self.position_type, self.position, self.width, self.height), (self.width, self.height))

    def calc_left(self):
        self.text_rect = self.text_surface.get_rect(
            midleft=(self.input_rect.x, self.input_rect.y+(self.height//2)))

    def calc_center(self):
        self.text_rect = self.text_surface.get_rect(
            center=(self.input_rect.x+(self.width//2), self.input_rect.y+(self.height//2)))

    def calc_right(self):
        self.text_rect = self.text_surface.get_rect(
            midright=(self.input_rect.x+self.width,
                      self.input_rect.y+(self.height//2))
        )

    def render(self, new_text: str = None):
        if new_text != None:
            self.text = new_text
        self.text_surface = self.font.render(self.text, True, self.color)
        self.text_rect = self.text_surface.get_rect(
            **{self.position_type: self.position})
        match self.text_center:
            case "left": self.calc_left()
            case "center": self.calc_center()
            case "right": self.calc_right()
            case _: raise ValueError(f"Wrong argument {self.text_center}")
        self.screen.blit(self.text_surface, self.text_rect)
