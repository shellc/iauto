# iauto Python API Reference

* [iauto](#iauto)
  * [VERSION](#iauto.VERSION)
* [iauto.agents](#iauto.agents)
* [iauto.agents.\_executor](#iauto.agents._executor)
  * [AgentExecutor](#iauto.agents._executor.AgentExecutor)
* [iauto.actions.\_playbook](#iauto.actions._playbook)
  * [PlaybookAction](#iauto.actions._playbook.PlaybookAction)
  * [PlaybookRunAction](#iauto.actions._playbook.PlaybookRunAction)
* [iauto.actions.\_loader](#iauto.actions._loader)
  * [ActionLoader](#iauto.actions._loader.ActionLoader)
  * [register\_action](#iauto.actions._loader.register_action)
* [iauto.actions](#iauto.actions)
* [iauto.actions.\_action](#iauto.actions._action)
  * [Playbook](#iauto.actions._action.Playbook)
  * [Executor](#iauto.actions._action.Executor)
  * [ActionArg](#iauto.actions._action.ActionArg)
  * [ActionSpec](#iauto.actions._action.ActionSpec)
  * [Action](#iauto.actions._action.Action)
  * [FunctionAction](#iauto.actions._action.FunctionAction)
  * [create\_action](#iauto.actions._action.create_action)
* [iauto.actions.\_flow](#iauto.actions._flow)
  * [eval\_operator](#iauto.actions._flow.eval_operator)
* [iauto.actions.\_executor](#iauto.actions._executor)
  * [PlaybookExecutor](#iauto.actions._executor.PlaybookExecutor)
* [iauto.llms.\_chatglm](#iauto.llms._chatglm)
  * [ChatGLM](#iauto.llms._chatglm.ChatGLM)
* [iauto.llms.\_openai](#iauto.llms._openai)
  * [OpenAI](#iauto.llms._openai.OpenAI)
* [iauto.llms.\_session](#iauto.llms._session)
  * [Session](#iauto.llms._session.Session)
* [iauto.llms.\_llm](#iauto.llms._llm)
  * [Function](#iauto.llms._llm.Function)
  * [ToolCall](#iauto.llms._llm.ToolCall)
  * [ChatMessage](#iauto.llms._llm.ChatMessage)
  * [LLM](#iauto.llms._llm.LLM)
* [iauto.llms.llama.\_llama](#iauto.llms.llama._llama)
  * [LLaMA](#iauto.llms.llama._llama.LLaMA)
* [iauto.llms.\_llm\_factory](#iauto.llms._llm_factory)
  * [create\_llm](#iauto.llms._llm_factory.create_llm)

<a id="iauto"></a>

# iauto

`iauto` is a Low-Code intelligent automation tool that integrates LLM and RPA.

Classes:
* Playbook
* PlaybookExecutor

<a id="iauto.VERSION"></a>

#### VERSION

The current version.

<a id="iauto.agents"></a>

# iauto.agents

This module provides the `AgentExecutor` class which is responsible for executing actions on behalf of agents.
It acts as an intermediary layer between the agent's instructions and the actual execution of those instructions.

Classes:
* AgentExecutor

<a id="iauto.agents._executor"></a>

# iauto.agents.\_executor

<a id="iauto.agents._executor.AgentExecutor"></a>

## AgentExecutor Objects

```python
class AgentExecutor()
```

<a id="iauto.agents._executor.AgentExecutor.run"></a>

#### run

```python
def run(message: ChatMessage,
        clear_history: Optional[bool] = True,
        silent: Optional[bool] = False,
        **kwargs) -> Dict
```

Runs the chat session with the given message and configuration.

This method initiates a chat with the recipient (either a single agent or a group chat manager) using
the UserProxyAgent. It processes the message, manages the chat history, and generates a summary
of the conversation.

**Arguments**:

- `message` _ChatMessage_ - The message to start the chat with.
- `clear_history` _Optional[bool]_ - Determines whether to clear the chat history before starting
  the new chat session. Defaults to True.
- `silent` _Optional[bool]_ - If set to True, the agents will not output any messages. Defaults to False.
- `**kwargs` - Additional keyword arguments that might be needed for extended functionality.
  

**Returns**:

- `Dict` - A dictionary containing the chat history, summary of the conversation, and the cost of the session.

<a id="iauto.agents._executor.AgentExecutor.reset"></a>

#### reset

```python
def reset()
```

Resets the state of all agents and the UserProxyAgent.

This method clears any stored state or history in the agents to prepare for a new task.

<a id="iauto.agents._executor.AgentExecutor.set_human_input_mode"></a>

#### set\_human\_input\_mode

```python
def set_human_input_mode(mode)
```

Sets the human input mode for the UserProxyAgent and the recipient.

**Arguments**:

- `mode` _str_ - The mode of human input to set. Can be 'NEVER', 'TERMINATE', or 'ALWAYS'.

<a id="iauto.agents._executor.AgentExecutor.register_human_input_func"></a>

#### register\_human\_input\_func

```python
def register_human_input_func(func)
```

Registers a function to handle human input across all agents.

**Arguments**:

- `func` _Callable_ - The function to be called when human input is needed.

<a id="iauto.agents._executor.AgentExecutor.register_print_received"></a>

#### register\_print\_received

```python
def register_print_received(func)
```

Registers a function to print messages received by agents.

The function will be called each time an agent receives a message, unless the silent
flag is set to True.

**Arguments**:

- `func` _Callable_ - The function to be called with the message, sender, and receiver
  information when a message is received.

<a id="iauto.actions._playbook"></a>

# iauto.actions.\_playbook

<a id="iauto.actions._playbook.PlaybookAction"></a>

## PlaybookAction Objects

```python
class PlaybookAction(Action)
```

<a id="iauto.actions._playbook.PlaybookAction.perform"></a>

#### perform

```python
def perform(*args,
            executor: Optional[Executor] = None,
            playbook: Optional[Playbook] = None,
            **kwargs) -> Any
```

Performs the action of executing a series of other actions defined within a playbook.

This method takes a variable number of arguments and keyword arguments. It requires
an executor and a playbook to be provided to perform the actions. The method sets
variables in the executor from the provided keyword arguments and then loads and
executes actions either from the provided playbook or from playbook paths specified
in the args.

**Arguments**:

- `*args` - Variable length argument list containing playbook paths as strings.
- `executor` _Optional[Executor]_ - The executor to perform the actions. Must not be None.
- `playbook` _Optional[Playbook]_ - The playbook containing actions to be executed. Must not be None.
- `**kwargs` - Arbitrary keyword arguments which are set as variables in the executor.
  

**Raises**:

- `ValueError` - If either executor or playbook is None, or if any of the args are not
  valid playbook paths as strings.
  

**Returns**:

- `Any` - The result of the last action performed by the executor.

<a id="iauto.actions._playbook.PlaybookRunAction"></a>

## PlaybookRunAction Objects

```python
class PlaybookRunAction(Action)
```

<a id="iauto.actions._playbook.PlaybookRunAction.perform"></a>

#### perform

```python
def perform(*args,
            executor: Optional[Executor] = None,
            playbook: Optional[Playbook] = None,
            **kwargs) -> Any
```

Perform the actions defined in the playbook using the executor.

This method sets any provided keyword arguments as variables in the executor and then
performs the actions in the playbook.

**Arguments**:

- `*args` - Variable length argument list, unused in this method.
- `executor` _Optional[Executor]_ - Unused in this method, as the executor is set during
  initialization.
- `playbook` _Optional[Playbook]_ - Unused in this method, as the playbook is set during
  initialization.
- `**kwargs` - Arbitrary keyword arguments which are set as variables in the executor.
  

**Returns**:

- `Any` - The result of the last action performed by the executor.

<a id="iauto.actions._loader"></a>

# iauto.actions.\_loader

<a id="iauto.actions._loader.ActionLoader"></a>

## ActionLoader Objects

```python
class ActionLoader()
```

Manages the registration and retrieval of action instances.

This class provides a mechanism to register actions by name and retrieve them.
It keeps an internal dictionary that maps action names to action instances.

<a id="iauto.actions._loader.ActionLoader.register"></a>

#### register

```python
def register(actions: Dict[str, Action])
```

Registers a set of actions.

**Arguments**:

- `actions` _Dict[str, Action]_ - A dictionary with action names as keys and
  Action instances as values to be registered.

<a id="iauto.actions._loader.ActionLoader.get"></a>

#### get

```python
def get(name) -> Union[Action, None]
```

Retrieves an action instance by its name.

**Arguments**:

- `name` _str_ - The name of the action to retrieve.
  

**Returns**:

  Action or None: The action instance if found, otherwise None.

<a id="iauto.actions._loader.ActionLoader.actions"></a>

#### actions

```python
@property
def actions()
```

Gets a list of all registered action instances.

**Returns**:

- `list` - A list of Action instances.

<a id="iauto.actions._loader.ActionLoader.load"></a>

#### load

```python
def load(identifier)
```

Loads an action from a given identifier.

The identifier is expected to be a string in the format 'package.module.ClassName', where 'package.module'
is the full path to the module containing the class 'ClassName' that is the action to be loaded.

**Arguments**:

- `identifier` _str_ - A dot-separated path representing the action to be loaded.
  

**Raises**:

- `ValueError` - If the action name conflicts with an already registered action.
- `ImportError` - If the module cannot be imported.
- `AttributeError` - If the class cannot be found in the module.
  

**Returns**:

  None

<a id="iauto.actions._loader.register_action"></a>

#### register\_action

```python
def register_action(name: str, spec: Dict)
```

Registers a new action with the provided name and specification.

**Arguments**:

- `name` _str_ - The unique name of the action to register.
- `spec` _Dict_ - A dictionary containing the action specification.
  

**Returns**:

  The created action instance.
  
  Decorates:
- `func` - The function to be transformed into an action.
  

**Raises**:

- `ValueError` - If an action with the given name already exists.

<a id="iauto.actions"></a>

# iauto.actions

This module defines the core components of the action system.

It provides the necessary classes and functions to create, manage, and execute actions
within the context of the playbook execution environment. It includes
definitions for actions, action arguments, action specifications, executors, and playbooks.

Classes:
* Action: Represents a single action to be executed.
* ActionArg: Defines an argument that can be passed to an action.
* ActionSpec: Contains the specification details of an action.
* Executor: The base class for action executors.
* Playbook: Represents a sequence of actions to be executed as a unit.
* PlaybookExecutor: Responsible for executing the actions defined in a playbook.
* PlaybookRunAction: A special action that represents the execution of a playbook.

Functions:
* create_action: A factory function to create instances of actions.
* loader: A function to load actions and their specifications.
* register_action: A function to register new actions into the system.

The module also handles the registration and discovery of built-in actions.

<a id="iauto.actions._action"></a>

# iauto.actions.\_action

<a id="iauto.actions._action.Playbook"></a>

## Playbook Objects

```python
class Playbook(BaseModel)
```

A class representing a playbook which includes a series of actions to be executed.

**Attributes**:

- `name` _Optional[str]_ - The name of the playbook.
- `description` _Optional[str]_ - A brief description of what the playbook does.
- `args` _Union[str, List, Dict, None]_ - Arguments that can be passed to the actions in the playbook.
- `actions` _Optional[List['Playbook']]_ - A list of actions (playbooks) to be executed.
- `result` _Union[str, List, Dict, None]_ - The result of the playbook execution.
- `spec` _Optional['ActionSpec']_ - The specification of the action that this playbook represents.

<a id="iauto.actions._action.Executor"></a>

## Executor Objects

```python
class Executor(ABC)
```

Abstract base class for an executor that can run playbooks.

**Attributes**:

- `variables` _Dict_ - A dictionary to hold variables that can be used in the execution context.

<a id="iauto.actions._action.Executor.perform"></a>

#### perform

```python
@abstractmethod
def perform(playbook: Playbook) -> Any
```

Execute the given playbook.

**Arguments**:

- `playbook` _Playbook_ - The playbook to execute.
  

**Returns**:

- `Any` - The result of the playbook execution.

<a id="iauto.actions._action.Executor.get_action"></a>

#### get\_action

```python
@abstractmethod
def get_action(playbook: Playbook) -> Union['Action', None]
```

Retrieve the action associated with the given playbook.

**Arguments**:

- `playbook` _Playbook_ - The playbook containing the action to retrieve.
  

**Returns**:

  Union[Action, None]: The action to perform, or None if not found.

<a id="iauto.actions._action.Executor.eval_args"></a>

#### eval\_args

```python
@abstractmethod
def eval_args(args: Union[str, List, Dict, None] = None) -> Tuple[List, Dict]
```

Evaluate the arguments passed to the playbook or action.

**Arguments**:

- `args` _Union[str, List, Dict, None], optional_ - The arguments to evaluate.
  

**Returns**:

  Tuple[List, Dict]: A tuple containing the evaluated arguments as a list or a dictionary.

<a id="iauto.actions._action.Executor.extract_vars"></a>

#### extract\_vars

```python
@abstractmethod
def extract_vars(data, vars)
```

Extract variables from the given data based on the vars specification.

**Arguments**:

- `data` - The data from which to extract variables.
- `vars` - The specification of variables to extract from the data.

<a id="iauto.actions._action.Executor.set_variable"></a>

#### set\_variable

```python
def set_variable(name: str, value: Any)
```

Set a variable in the executor's context.

**Arguments**:

- `name` _str_ - The name of the variable to set.
- `value` _Any_ - The value to assign to the variable.

<a id="iauto.actions._action.Executor.variables"></a>

#### variables

```python
@property
def variables() -> Dict
```

Get the current variables in the executor's context.

**Returns**:

- `Dict` - A dictionary of the current variables.

<a id="iauto.actions._action.ActionArg"></a>

## ActionArg Objects

```python
class ActionArg(BaseModel)
```

A class representing an argument for an action.

**Attributes**:

- `name` _str_ - The name of the argument.
- `type` _str_ - The type of the argument, default is "string".
- `description` _str_ - A description of what the argument is for.
- `required` _bool_ - Whether the argument is required or optional, default is False.

<a id="iauto.actions._action.ActionSpec"></a>

## ActionSpec Objects

```python
class ActionSpec(BaseModel)
```

A class representing the specification of an action.

**Attributes**:

- `name` _str_ - The name of the action.
- `description` _str_ - A brief description of what the action does.
- `arguments` _Optional[List[ActionArg]]_ - A list of arguments that the action accepts.

<a id="iauto.actions._action.ActionSpec.from_dict"></a>

#### from\_dict

```python
@staticmethod
def from_dict(d: Dict = {}) -> 'ActionSpec'
```

Create an ActionSpec instance from a dictionary representation.

**Arguments**:

- `d` _Dict, optional_ - The dictionary containing action specification data.
  

**Returns**:

- `ActionSpec` - An instance of ActionSpec created from the provided dictionary.
  

**Raises**:

- `ValueError` - If the dictionary contains invalid data for creating an ActionSpec.

<a id="iauto.actions._action.ActionSpec.from_oai_dict"></a>

#### from\_oai\_dict

```python
@staticmethod
def from_oai_dict(d: Dict = {}) -> 'ActionSpec'
```

Create an ActionSpec instance from a dictionary following the OpenAPI Specification.

**Arguments**:

- `d` _Dict, optional_ - The dictionary containing OpenAPI Specification data.
  

**Returns**:

- `ActionSpec` - An instance of ActionSpec created from the provided OpenAPI dictionary.
  

**Raises**:

- `ValueError` - If the dictionary does not conform to the expected OpenAPI Specification format.

<a id="iauto.actions._action.ActionSpec.oai_spec"></a>

#### oai\_spec

```python
def oai_spec() -> Dict
```

Generate an OpenAPI Specification dictionary for this action.

**Returns**:

- `Dict` - A dictionary representing the action in OpenAPI Specification format.

<a id="iauto.actions._action.Action"></a>

## Action Objects

```python
class Action(ABC)
```

Abstract base class for an action.

An action defines a single operation that can be performed. Actions are typically
executed by an Executor within the context of a Playbook.

**Attributes**:

- `spec` _ActionSpec_ - The specification of the action.

<a id="iauto.actions._action.Action.perform"></a>

#### perform

```python
@abstractmethod
def perform(*args,
            executor: Optional[Executor] = None,
            playbook: Optional[Playbook] = None,
            **kwargs) -> Any
```

Execute the action with the given arguments.

**Arguments**:

- `*args` - Positional arguments for the action.
- `executor` _Optional[Executor]_ - The executor running this action.
- `playbook` _Optional[Playbook]_ - The playbook that this action is part of.
- `**kwargs` - Keyword arguments for the action.
  

**Returns**:

- `Any` - The result of the action execution.
  

**Raises**:

- `NotImplementedError` - If the method is not implemented by the subclass.

<a id="iauto.actions._action.Action.copy"></a>

#### copy

```python
def copy()
```

Create a copy of the Action instance.

**Returns**:

- `Action` - A new instance of the Action with the same specification.

<a id="iauto.actions._action.FunctionAction"></a>

## FunctionAction Objects

```python
class FunctionAction(Action)
```

A concrete implementation of Action that wraps a Python callable.

**Attributes**:

- `_func` _Callable_ - The Python callable to wrap.
- `spec` _ActionSpec_ - The specification of the action.

<a id="iauto.actions._action.FunctionAction.perform"></a>

#### perform

```python
def perform(*args,
            executor: Optional[Executor] = None,
            playbook: Optional[Playbook] = None,
            **kwargs) -> Any
```

Execute the wrapped Python callable with the given arguments.

**Arguments**:

- `*args` - Positional arguments for the callable.
- `executor` _Optional[Executor]_ - The executor running this action.
- `playbook` _Optional[Playbook]_ - The playbook that this action is part of.
- `**kwargs` - Keyword arguments for the callable.
  

**Returns**:

- `Any` - The result of the callable execution.

<a id="iauto.actions._action.create_action"></a>

#### create\_action

```python
def create_action(func, spec: Dict) -> Action
```

Factory function to create a FunctionAction.

**Arguments**:

- `func` _Callable_ - The Python callable that the action will execute.
- `spec` _Dict_ - A dictionary representing the action's specification.
  

**Returns**:

- `Action` - A FunctionAction instance with the given callable and specification.

<a id="iauto.actions._flow"></a>

# iauto.actions.\_flow

<a id="iauto.actions._flow.eval_operator"></a>

#### eval\_operator

```python
def eval_operator(operator, vars={}) -> bool
```

not: not true
all: all true
any: any is true
lt: less than
le: less than or equal to
eq: equal to
ne: not equal to
ge: greater than or equal to
gt: greater than

<a id="iauto.actions._executor"></a>

# iauto.actions.\_executor

<a id="iauto.actions._executor.PlaybookExecutor"></a>

## PlaybookExecutor Objects

```python
class PlaybookExecutor(Executor)
```

Executes playbooks containing a sequence of actions.

This executor handles the running of actions defined in a playbook, managing
the necessary thread execution for asynchronous actions and the extraction
and evaluation of variables from the results.

<a id="iauto.actions._executor.PlaybookExecutor.perform"></a>

#### perform

```python
def perform(playbook: Playbook) -> Any
```

Executes the given playbook.

This method takes a Playbook object, retrieves the corresponding action,
evaluates the arguments, and then performs the action. If the action's result
is an asyncio coroutine, it is run in a separate thread. After the action is
performed, any variables specified in the playbook's 'result' section are
extracted and stored.

**Arguments**:

  - playbook (Playbook): The playbook object containing the action to be executed.
  

**Returns**:

  - Any: The result of executing the action in the playbook.
  

**Raises**:

  - ValueError: If the action is not found or the playbook is invalid.

<a id="iauto.actions._executor.PlaybookExecutor.eval_vars"></a>

#### eval\_vars

```python
def eval_vars(vars)
```

Evaluate the variables in the context of the current executor's state.

This method takes a variable or a structure containing variables and
evaluates them using the current state of variables stored within the
executor. It supports strings, lists, and dictionaries. If a string
variable starts with '$', it is treated as a reference to a variable
which is then resolved. If the variable is not found, the string is
returned as is. For lists and dictionaries, each element or key-value
pair is recursively processed.

**Arguments**:

  - vars (Union[str, List, Dict, None]): The variable or structure containing
  variables to be evaluated.
  

**Returns**:

  - The evaluated variable, or the original structure with all contained
  variables evaluated.

<a id="iauto.actions._executor.PlaybookExecutor.eval_args"></a>

#### eval\_args

```python
def eval_args(args: Union[str, List, Dict, None] = None) -> Tuple[List, Dict]
```

Evaluates and separates arguments into positional and keyword arguments.

This method processes the input arguments, evaluating any variables within
them using the current state of the executor. It then separates the evaluated
arguments into positional (list) and keyword (dictionary) arguments.

**Arguments**:

  - args (Union[str, List, Dict, None], optional): The arguments to evaluate and
  separate. Can be a string, list, dictionary, or None.
  

**Returns**:

  - Tuple[List, Dict]: A tuple containing a list of positional arguments and a
  dictionary of keyword arguments.

<a id="iauto.actions._executor.PlaybookExecutor.extract_vars"></a>

#### extract\_vars

```python
def extract_vars(data, vars)
```

Extracts variables from the result data and stores them in the executor's state.

This method takes the result data and the variables defined in the playbook's 'result'
section, then stores these variables in the executor's state for later use. The method
supports extracting variables from strings, lists, and dictionaries.

**Arguments**:

  - data (Any): The result data from which variables will be extracted.
  - vars (Union[str, List, Dict, None]): The structure defining which variables to extract
  from the result data. It can be a string, a list, a dictionary, or None.
  
  If `vars` is a string that starts with '$', it is assumed to be a variable name, and the
  entire `data` is stored with that variable name. If `vars` is a list, each element in
  `vars` that starts with '$' is treated as a variable name, and the corresponding element
  in `data` is stored with that variable name, provided `data` is also a list and the indices
  match. If `vars` is a dictionary, each key that starts with '$' is treated as a variable
  name, and the value from `data` corresponding to the dictionary's value is stored with the
  variable name, provided `data` is also a dictionary and contains the keys.
  
  No action is taken if `vars` is None or if the data types of `vars` and `data` do not
  correspond as expected.

<a id="iauto.actions._executor.PlaybookExecutor.resolve_path"></a>

#### resolve\_path

```python
def resolve_path(path: str) -> str
```

Resolves a given file path to an absolute path.

If the given path is already an absolute path, it is returned unchanged.
Otherwise, the path is resolved relative to the directory of the current
playbook file, which is stored in the executor's variables under the key
"__file__".

**Arguments**:

- `path` _str_ - The file path to resolve.
  

**Returns**:

- `str` - The resolved absolute file path.

<a id="iauto.actions._executor.PlaybookExecutor.execute"></a>

#### execute

```python
@staticmethod
def execute(playbook_file, variables={}) -> Any
```

Executes a playbook from a given file with optional initial variables.

This static method loads a playbook from the specified file, creates a new
PlaybookExecutor instance, sets any initial variables, and then performs the
playbook.

**Arguments**:

- `playbook_file` _str_ - The path to the playbook file to be executed.
- `variables` _dict, optional_ - A dictionary of initial variables to set in
  the executor's context before executing the playbook. Defaults to an
  empty dictionary.
  

**Returns**:

- `Any` - The result of executing the playbook, which could be of any type
  depending on the actions performed within the playbook.

<a id="iauto.llms._chatglm"></a>

# iauto.llms.\_chatglm

<a id="iauto.llms._chatglm.ChatGLM"></a>

## ChatGLM Objects

```python
class ChatGLM(LLM)
```

<a id="iauto.llms._chatglm.ChatGLM.generate"></a>

#### generate

```python
def generate(instructions: str, **kwargs) -> Message
```



<a id="iauto.llms._openai"></a>

# iauto.llms.\_openai

<a id="iauto.llms._openai.OpenAI"></a>

## OpenAI Objects

```python
class OpenAI(LLM)
```



<a id="iauto.llms._session"></a>

# iauto.llms.\_session

<a id="iauto.llms._session.Session"></a>

## Session Objects

```python
class Session()
```

The Session class is responsible for managing a conversation with a language model (LLM).
It handles the state of the conversation, including the messages exchanged and the actions
that can be performed based on those messages.

The Session class provides high-level methods to interact with a language model, allowing for
complex conversation flows, tool integration, and message management.

<a id="iauto.llms._session.Session.add"></a>

#### add

```python
def add(message: ChatMessage) -> None
```

Add a new ChatMessage to the session's message history.

**Arguments**:

- `message` _ChatMessage_ - The message to add to the history.
  

**Returns**:

  None

<a id="iauto.llms._session.Session.llm"></a>

#### llm

```python
@property
def llm() -> LLM
```

Get the language model (LLM) instance associated with the session.

**Returns**:

- `LLM` - The language model instance used for processing messages.

<a id="iauto.llms._session.Session.messages"></a>

#### messages

```python
@property
def messages() -> List[ChatMessage]
```

Get the list of ChatMessage instances that represent the message history of the session.

**Returns**:

- `List[ChatMessage]` - The list of messages exchanged during the session.

<a id="iauto.llms._session.Session.actions"></a>

#### actions

```python
@property
def actions() -> Optional[List[Action]]
```

Get the list of Action instances that can be performed within the session.

**Returns**:

- `Optional[List[Action]]` - The list of actions available in the session, or an empty list if none are set.

<a id="iauto.llms._session.Session.run"></a>

#### run

```python
def run(instructions: Optional[str] = None,
        messages: Optional[List[ChatMessage]] = None,
        history: int = 5,
        rewrite: bool = False,
        expect_json: int = 0,
        tools: Optional[List[Action]] = None,
        use_tools: bool = True,
        auto_exec_tools: bool = True,
        **kwargs) -> Union[ChatMessage, Dict]
```

Run a conversation flow based on provided instructions and messages, with the option to rewrite the input,
expect a JSON response, and execute tools.

**Arguments**:

- `instructions` _Optional[str]_ - Instructions to prepend to the messages before sending to the LLM as a system role message.
- `messages` _Optional[List[ChatMessage]]_ - A list of ChatMessage instances to include in the conversation.
  If not provided, the last 'history' number of messages from the session will be used.
- `history` _int_ - The number of recent messages from the session to consider in the conversation. Defaults to 5.
- `rewrite` _bool_ - Whether to rewrite the last user message to be clearer before running the session.
- `expect_json` _int_ - The number of times to attempt parsing the LLM's response as JSON before giving up.
- `tools` _Optional[List[Action]]_ - A list of Action instances representing tools that can be used in the session.
- `use_tools` _bool_ - Whether to include tool specifications when sending messages to the LLM.
- `auto_exec_tools` _bool_ - Automatically execute tools if they are called in the LLM's response.
  

**Returns**:

  Union[ChatMessage, Dict]: The final ChatMessage from the LLM, or a dictionary if a JSON response is expected and successfully parsed.
  

**Raises**:

- `json.JSONDecodeError` - If 'expect_json' is greater than 0 and the LLM's response cannot be parsed as JSON.

<a id="iauto.llms._session.Session.react"></a>

#### react

```python
def react(instructions: Optional[str] = None,
          messages: Optional[List[ChatMessage]] = None,
          history: int = 5,
          rewrite: bool = False,
          log: bool = False,
          max_steps: int = 3,
          tools: Optional[List[Action]] = None,
          use_tools: bool = True,
          auto_exec_tools: bool = True,
          **kwargs) -> ChatMessage
```

Perform a series of Thought, Action, and Observation steps to react to the user's last question and generate an answer.

This method simulates a cognitive process by interleaving Thought (reasoning about the situation),
Action (using tools to generate an observation or concluding the task), and Observation (result of the action).

**Arguments**:

- `instructions` _Optional[str]_ - Additional instructions to provide context for the language model.
- `messages` _Optional[List[ChatMessage]]_ - The list of ChatMessage instances to include in the conversation.
  Defaults to the last 'history' messages if not provided.
- `history` _int_ - The number of recent messages from the session to consider. Defaults to 5.
- `rewrite` _bool_ - Whether to rewrite the last user message for clarity before processing. Defaults to False.
- `log` _bool_ - Whether to log the steps of the process. Defaults to False.
- `max_steps` _int_ - The maximum number of Thought/Action/Observation cycles to perform. Defaults to 3.
- `tools` _Optional[List[Action]]_ - A list of Action instances representing tools that can be used in the session.
- `use_tools` _bool_ - Whether to include tool specifications when sending messages to the LLM. Defaults to True.
- `auto_exec_tools` _bool_ - Whether to automatically execute tools if they are called in the LLM's response. Defaults to True.
  

**Returns**:

- `ChatMessage` - The final ChatMessage containing the answer to the user's question or indicating that more information is needed.
  

**Raises**:

- `ValueError` - If the provided messages list is empty or the last message is not from the user.

<a id="iauto.llms._session.Session.rewrite"></a>

#### rewrite

```python
def rewrite(history: int = 5, **kwargs) -> None
```

Rewrite the last user message in the session's message history to be clearer and more complete based on the context of the conversation.

This method utilizes the language model to reformulate the user's question, considering the conversation history to provide a clearer version of the question.

**Arguments**:

- `history` _int_ - The number of recent messages from the session to consider for context. Defaults to 5.
  

**Returns**:

- `None` - The method updates the last user message in the session's message history in place.
  

**Raises**:

- `ValueError` - If there are no messages or the last message is not from the user.

<a id="iauto.llms._session.Session.plain_messages"></a>

#### plain\_messages

```python
def plain_messages(messages: List[ChatMessage],
                   norole: bool = False,
                   nowrap: bool = False) -> str
```

Convert a list of ChatMessage instances into a plain string representation.

**Arguments**:

- `messages` _List[ChatMessage]_ - The list of ChatMessage instances to convert.
- `norole` _bool, optional_ - If True, the role of the message sender is omitted. Defaults to False.
- `nowrap` _bool, optional_ - If True, newlines in the message content are replaced with '\n'. Defaults to False.
  

**Returns**:

- `str` - A string representation of the messages, each message on a new line.

<a id="iauto.llms._llm"></a>

# iauto.llms.\_llm

<a id="iauto.llms._llm.Function"></a>

## Function Objects

```python
class Function(BaseModel)
```

Represents a function call with optional arguments.

**Attributes**:

- `name` _str_ - The name of the function being called.
- `arguments` _Optional[str]_ - The arguments to be passed to the function, if any.

<a id="iauto.llms._llm.ToolCall"></a>

## ToolCall Objects

```python
class ToolCall(BaseModel)
```

Represents a call to a specific tool with an optional function call.

**Attributes**:

- `id` _str_ - The unique identifier for the tool call.
- `type` _str_ - The type of the tool.
- `function` _Optional[Function]_ - An optional Function instance representing the function call associated with         the tool, if any.

<a id="iauto.llms._llm.ChatMessage"></a>

## ChatMessage Objects

```python
class ChatMessage(Message)
```

Represents a chat message with additional metadata and optional tool call information.

**Attributes**:

- `role` _str_ - The role of the entity sending the message (e.g., "user", "system", "assistant").
- `tool_calls` _Optional[List[ToolCall]]_ - A list of ToolCall instances representing the tool calls associated         with this message, if any.
- `tool_call_id` _Optional[str]_ - The identifier of the tool call associated with this message, if any.
- `name` _Optional[str]_ - The name of the tool or function called.

<a id="iauto.llms._llm.ChatMessage.from_dict"></a>

#### from\_dict

```python
@staticmethod
def from_dict(d: Dict) -> "ChatMessage"
```

Create a ChatMessage instance from a dictionary.

Parses the dictionary to populate the ChatMessage fields. If certain keys
are not present in the dictionary, default values are used. For 'tool_calls',
it creates a list of ToolCall instances from the sub-dictionaries.

**Arguments**:

- `d` _Dict_ - The dictionary containing the ChatMessage data.
  

**Returns**:

- `ChatMessage` - An instance of ChatMessage with properties populated from the dictionary.

<a id="iauto.llms._llm.LLM"></a>

## LLM Objects

```python
class LLM(ABC)
```

Abstract base class for a Language Model (LLM) that defines the interface for generating messages and handling     chat interactions.

<a id="iauto.llms._llm.LLM.generate"></a>

#### generate

```python
@abstractmethod
def generate(instructions: str, **kwargs) -> Message
```

Generate a message based on the given instructions.

**Arguments**:

- `instructions` _str_ - The instructions or prompt to generate the message from.
- `**kwargs` - Additional keyword arguments that the concrete implementation may use.
  

**Returns**:

- `Message` - The generated message as a Message instance.

<a id="iauto.llms._llm.LLM.chat"></a>

#### chat

```python
@abstractmethod
def chat(messages: List[ChatMessage],
         tools: Optional[List[ActionSpec]] = None,
         **kwargs) -> ChatMessage
```

Conduct a chat interaction by processing a list of ChatMessage instances and optionally using tools.

**Arguments**:

- `messages` _List[ChatMessage]_ - A list of ChatMessage instances representing the conversation history.
- `tools` _Optional[List[ActionSpec]]_ - An optional list of ActionSpec instances representing tools that can be used in the chat.
- `**kwargs` - Additional keyword arguments that the concrete implementation may use.
  

**Returns**:

- `ChatMessage` - The response as a ChatMessage instance after processing the interaction.

<a id="iauto.llms._llm.LLM.model"></a>

#### model

```python
@property
@abstractmethod
def model() -> str
```

Abstract property that should return the model identifier for the LLM instance.

**Returns**:

- `str` - The model identifier.

<a id="iauto.llms.llama._llama"></a>

# iauto.llms.llama.\_llama

<a id="iauto.llms.llama._llama.LLaMA"></a>

## LLaMA Objects

```python
class LLaMA(LLM)
```

llamap.cpp: https://github.com/ggerganov/llama.cpp
llama-cpp-python: https://github.com/abetlen/llama-cpp-python

<a id="iauto.llms.llama._llama.LLaMA.generate"></a>

#### generate

```python
def generate(instructions: str, **kwargs) -> Message
```



<a id="iauto.llms._llm_factory"></a>

# iauto.llms.\_llm\_factory

<a id="iauto.llms._llm_factory.create_llm"></a>

#### create\_llm

```python
def create_llm(provider: str = "openai", **kwargs) -> LLM
```

Create a language model instance based on the specified provider.

This factory function supports creating instances of different language
models by specifying a provider. Currently supported providers are 'openai',
'llama', and 'chatglm'. Depending on the provider, additional keyword
arguments may be required or optional.

**Arguments**:

  - provider (str): The name of the provider for the LLM. Defaults to 'openai'.
  - **kwargs: Additional keyword arguments specific to the chosen LLM provider.
  

**Returns**:

  - LLM: An instance of the specified language model.
  

**Raises**:

  - ImportError: If the required module for the specified provider is not installed.
  - ValueError: If an invalid provider name is given.

