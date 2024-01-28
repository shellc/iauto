from ._action import Action


class ModAction(Action):
    def perform(self, executor=None, playbook=None, *args, **kwargs) -> int:
        if len(args) != 2:
            raise ValueError("mod requires 2 numbers, like: [10, 2]")

        return args[0] % args[1]
