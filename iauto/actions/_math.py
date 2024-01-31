from ._action import Action, ActionSpec


class ModAction(Action):
    def __init__(self) -> None:
        super().__init__()

        self.spec = ActionSpec.from_dict({
            "description": "Calculate the modulus and return the result.",
        })

    def perform(
        self,
        *args,
        **kwargs
    ) -> int:
        if len(args) != 2:
            raise ValueError("mod requires 2 numbers, like: [10, 2]")

        return args[0] % args[1]
