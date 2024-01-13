import pygame
import inspect
from Assets.menu_assets import smoothscale_converter


def get_max_delta(image_idle, image_toggle):
    delta_width = abs(image_toggle.get_width() - image_idle.get_width())
    delta_height = abs(image_toggle.get_height() - image_idle.get_height())
    return (delta_width, delta_height)


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

    `revert_state`(self):
        Reverts the current state to the previous state if not an anchor state.

    `check_ownership`(self):
        Checks if the current global state is within the local state options and assigns it as the local state.

    `state_manager_hook`(self):
        Placeholder method to be overridden by subclasses.

    `state_manager`(self):
        Checks state ownership and runs the state_manager_hook.

    """

    state = "MainMenu"
    previous_state = []

    def __init__(
        self, screen: pygame.surface.Surface, is_anchor: bool, local_options: list
    ):
        self.screen = screen
        self.is_anchor = is_anchor
        self.local_options = local_options
        # Option on index 0 is always the default one.
        self.local_state = self.local_options[0]

    def change_state(self, new_state: str):
        """
        Changes the current state to a new state.

        Parameters:
            new_state : str
                The new state to change to

        """
        self.local_state = new_state
        State.previous_state.append(State.state)
        State.state = new_state

    def revert_state(self):
        """
        Reverts the current state to the previous state if not an anchor state.

        """
        if self.is_anchor == False:
            State.state = State.previous_state[-1]
            State.previous_state.pop()

    def check_ownership(self):
        """
        Checks if the current global state is within the local state options and assigns it as the local state.

        """
        if State.state in self.local_options:
            self.local_state = State.state

    def state_manager_hook(self):
        """
        Placeholder method to be overridden by subclasses.

        """
        pass

    def state_manager(self):
        """
        Checks state ownership and runs the state_manager_hook.

        """
        self.check_ownership()
        self.state_manager_hook()


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
            if inspect.isfunction(self.call_back):
                return self.call_back()
            elif type(self.call_back) == pygame.event.Event:
                pygame.event.post(self.call_back)
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
        self.toggle_image = kwargs.get("toggle_image", self.all_image[0])
        self.position_type = kwargs.get("position_type", "center")
        self.position = kwargs.get("position", (0, 0))

        # Core Attributes for toggled state
        self.toggle_image_T = kwargs.get("toggle_image_T", self.all_image[1])
        self.position_type_T = kwargs.get("position_type_T", self.position_type)
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
            if inspect.isfunction(self.call_back):
                return self.call_back()
            elif type(self.call_back) == pygame.event.Event:
                pygame.event.post(self.call_back)
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
            for i_2, image_type in enumerate(toggle):
                match i_2:
                    case 0:
                        local_factor = factor
                    case 1:
                        local_factor = factor_T
                self.all_images[i_1][i_2] = smoothscale_converter(
                    image_type, local_factor
                )
        self.card_width = self.all_images[0][0][0].get_width()
        self.card_height = self.all_images[0][0][0].get_height()
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


class DualBar:
    """
    Creates a dual bar to display two values.

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
        max_health: int,
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
        self.max_health = max_health
        self.health = self.max_health

    def update(self, health: int) -> None:
        self.health = health
        self.health_percent = self.health / self.max_health
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
            (self.position[0], self.position[1], self.health_width, self.height),
            border_radius=self.border_radius,
        )
