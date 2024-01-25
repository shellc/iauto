from .._action import Action


class BrowserFunction(Action):
    def __init__(self) -> None:
        super().__init__()
        self._browser = None

    @property
    def browser(self):
        return self._browser