import os
from typing import Any, Optional

from ..action import Action, ActionSpec
from ..executor import Executor
from ..playbook import Playbook
from ..playbook import load as playbook_load


class PlaybookAction(Action):
    def __init__(self) -> None:
        """
        Initializes a new instance of the PlaybookAction class.

        This action serves as the top-level Action used to execute other Actions by
        loading and performing them using the provided executor and playbook.
        """
        super().__init__()

        self.spec = ActionSpec.from_dict({
            "name": "playbook",
            "description": "Executes a series of actions defined within a playbook."
        })

    def perform(
        self,
        *args,
        execute: Optional[bool] = True,
        executor: Executor,
        playbook: Playbook,
        **kwargs
    ) -> Any:
        """
        Performs the action of executing a series of other actions defined within a playbook.

        This method takes a variable number of arguments and keyword arguments. It requires
        an executor and a playbook to be provided to perform the actions. The method sets
        variables in the executor from the provided keyword arguments and then loads and
        executes actions either from the provided playbook or from playbook paths specified
        in the args.

        Args:
            *args: Variable length argument list containing playbook paths as strings.
            exuecute (Optional[bool]) : Return actions if execute is False
            executor (Optional[Executor]): The executor to perform the actions. Must not be None.
            playbook (Optional[Playbook]): The playbook containing actions to be executed. Must not be None.
            **kwargs: Arbitrary keyword arguments which are set as variables in the executor.

        Raises:
            ValueError: If either executor or playbook is None, or if any of the args are not
                valid playbook paths as strings.

        Returns:
            Any: The result of the last action performed by the executor.
        """

        if executor is None or playbook is None:
            raise ValueError("Executor and playbook are required.")

        for k, v in kwargs.items():
            executor.set_variable(f"${k}", v)

        actions = []

        if len(args) > 0:
            fpath = playbook.metadata.get("__root__")
            # fname = executor.variables.get("__file__")
            # if fname is not None:
            #    fpath = os.path.dirname(fname)
            for p in args:
                if not isinstance(p, str):
                    raise ValueError(f"Invalid playbook path: {p}")
                if not os.path.isabs(p) and fpath is not None:
                    p = os.path.join(fpath, p)

                pb = playbook_load(p)
                actions.append(pb)

        actions.extend(playbook.actions or [])

        if execute:
            result = None
            for action in actions:
                result = executor.perform(playbook=action)

            return result
        else:
            pb_run_actions = []
            for action in actions:
                pb_run = PlaybookRunAction(executor=executor, playbook=action)
                pb_run_actions.append(pb_run)

            return pb_run_actions


class PlaybookRunAction(Action):
    def __init__(self, executor: Executor, playbook: Playbook) -> None:
        """
        Initialize a PlaybookRunAction with a specific executor and playbook.

        Args:
            executor (Executor): The executor that will perform the actions in the playbook.
            playbook (Playbook): The playbook containing the actions to be executed.
        """
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
        """
        Perform the actions defined in the playbook using the executor.

        This method sets any provided keyword arguments as variables in the executor and then
        performs the actions in the playbook.

        Args:
            *args: Variable length argument list, unused in this method.
            executor (Optional[Executor]): Unused in this method, as the executor is set during
                initialization.
            playbook (Optional[Playbook]): Unused in this method, as the playbook is set during
                initialization.
            **kwargs: Arbitrary keyword arguments which are set as variables in the executor.

        Returns:
            Any: The result of the last action performed by the executor.
        """
        for k, v in kwargs.items():
            self._executor.set_variable(f"${k}", v)
        return self._executor.perform(playbook=self._playbook)


class SetVarAction(Action):
    def __init__(self) -> None:
        super().__init__()
        self.spec = ActionSpec.from_dict({
            "name": "setvar",
            "description": "Sets a variable to a specified value. Usage: setvar: [variable_name, value]",
            "arguments": [
                {
                    "name": "name",
                    "type": "string",
                    "description": "The name of the variable to set.",
                    "required": True
                },
                {
                    "name": "value",
                    "type": "any",
                    "description": "The value to assign to the variable.",
                    "required": True
                }
            ]
        })

    def perform(
        self,
        name: str,
        value: Any,
        executor: Optional[Executor] = None,
        playbook: Optional[Playbook] = None,
        **kwargs
    ) -> Any:
        if executor is None:
            raise ValueError("executor is None")

        executor.set_variable(f"${name}", value)
