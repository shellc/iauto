import os
from typing import Any, Optional

from ._action import Action, ActionSpec, Executor, Playbook


class PlaybookAction(Action):
    def __init__(self) -> None:
        super().__init__()

        self.spec = ActionSpec.from_dict({
            "name": "playbook",
            "description": "Playbook is used to execute Actions"
        })

    def perform(
        self,
        *args,
        executor: Optional[Executor] = None,
        playbook: Optional[Playbook] = None,
        **kwargs
    ) -> Any:
        if executor is None or playbook is None:
            raise ValueError("Executor and playbook are required.")

        for k, v in kwargs:
            executor.set_variable(f"${k}", v)

        actions = []

        if len(args) > 0:
            fpath = None
            fname = executor.variables.get("__file__")
            if fname is not None:
                if fname is not None:
                    fpath = os.path.dirname(fname)

            for p in args:
                if not isinstance(p, str):
                    raise ValueError(f"Invalid playbook path: {p}")
                if not os.path.isabs(p) and fpath is not None:
                    p = os.path.join(fpath, p)

                pb = Playbook.load(p)
                actions.append(pb)

        actions.extend(playbook.actions or [])

        result = None
        for action in actions:
            result = executor.perform(playbook=action)

        return result


class PlaybookRunAction(Action):
    def __init__(self, executor: Executor, playbook: Playbook) -> None:
        super().__init__()
        self._executor = executor
        self._playbook = playbook
        self.spec = playbook.spec

    def perform(
        self,
        *args,
        executor: Optional[Executor] = None,
        playbook: Optional[Playbook] = None,
        **kwargs
    ) -> Any:
        for k, v in kwargs.items():
            self._executor.set_variable(f"${k}", v)
        return self._executor.perform(playbook=self._playbook)
