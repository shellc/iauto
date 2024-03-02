from ..action import Action, ActionSpec


class ModAction(Action):
    def __init__(self) -> None:
        super().__init__()

        self.spec = ActionSpec.from_dict({
            "name": "math.mod",
            "description": "Calculates the remainder of the division of two numbers.",
            "arguments": [
                {
                    "name": "l",
                    "type": "int",
                    "description": "The dividend in the division operation.",
                    "required": True
                },
                {
                    "name": "r",
                    "type": "int",
                    "description": "The divisor in the division operation.",
                    "required": True
                }
            ],
        })

    def perform(
        self,
        l: int,
        r: int,
        **kwargs
    ) -> int:
        return l % r
