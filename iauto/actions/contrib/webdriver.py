import time
from typing import Any, Dict, List, Literal, Optional, Union

from appium.options.common.base import AppiumOptions
from appium.webdriver.appium_connection import AppiumConnection
from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webdriver import WebDriver as AppiumWebDriver
from appium.webdriver.webelement import WebElement
from selenium.common.exceptions import (ElementNotInteractableException,
                                        NoSuchElementException)

from ...log import get_logger
from ..action import Action, create

_log = get_logger("webdriver")


class Element(WebElement):
    def __init__(self, appium_element: Optional[WebElement] = None) -> None:
        super().__init__(
            parent=appium_element.parent if appium_element else None,
            id_=appium_element.id if appium_element else None
        )

        self._not_found = appium_element is None

        if self._not_found:
            self._execute = lambda *args, **kwargs: _log.warn(f"Element not found, ignore execute.{args} {kwargs}")

    def click(self, retries=0, delay=0.5, error_skip=False) -> None:
        for i in range(retries + 1):
            try:
                super().click()
                return
            except ElementNotInteractableException as e:
                _log.debug(f"Click error: {e.msg}")
                if i < retries - 1:
                    time.sleep(delay)
                    continue
                else:
                    if not error_skip:
                        raise e

    def get_element(
        self,
        by: str = AppiumBy.ID,
        value: Union[str, Dict, None] = None,
        not_found_ignore: bool = False,
        retries: int = 0,
        delay: float = 0.5
    ) -> Union['Element', None]:
        return Element._get_element(
            obj=self,
            by=by,
            value=value,
            not_found_ignore=not_found_ignore,
            retries=retries,
            delay=delay
        )

    def get_elements(
        self,
        by: str = AppiumBy.ID,
        value: Union[str, Dict, None] = None,
        not_found_ignore: bool = False,
        retries: int = 0,
        delay: float = 0.5
    ) -> Union[List['Element'], List]:
        return Element._get_elements(
            obj=self,
            by=by,
            value=value,
            not_found_ignore=not_found_ignore,
            retries=retries,
            delay=delay
        )

    def get_element_by_css(
        self,
        value: Union[str, Dict, None] = None,
        not_found_ignore: bool = False,
        retries: int = 0,
        delay: float = 0.5
    ):
        return self.get_element(
            by=AppiumBy.CSS_SELECTOR,
            value=value,
            not_found_ignore=not_found_ignore,
            retries=retries,
            delay=delay
        )

    def get_elements_by_css(
        self,
        value: Union[str, Dict, None] = None,
        not_found_ignore: bool = False,
        retries: int = 0,
        delay: float = 0.5
    ):
        return self.get_elements(
            by=AppiumBy.CSS_SELECTOR,
            value=value,
            not_found_ignore=not_found_ignore,
            retries=retries,
            delay=delay
        )

    def get_element_by_id(
        self,
        value: Union[str, Dict, None] = None,
        not_found_ignore: bool = False,
        retries: int = 0,
        delay: float = 0.5
    ):
        return self.get_element_by_css(
            value=f'[id="f{value}"]',
            not_found_ignore=not_found_ignore,
            retries=retries,
            delay=delay
        )

    @staticmethod
    def _get_element(
        obj,
        by: str = AppiumBy.ID,
        value: Union[str, Dict, None] = None,
        not_found_ignore: bool = False,
        retries: int = 0,
        delay: float = 0.5
    ) -> Union['Element', None]:
        e = None
        exc = None

        for i in range(retries + 1):
            try:
                e = obj.find_element(by=by, value=value)
                break
            except NoSuchElementException as exc_:
                exc = exc_
                _log.debug(f"Element not found: {value}")
                if i < retries - 1:
                    time.sleep(delay)
                continue

        if e is None:
            if not not_found_ignore:
                raise exc or NoSuchElementException(f"Element not found: {value}")
            else:
                return None

        return Element(appium_element=e)

    @staticmethod
    def _get_elements(
        obj,
        by: str = AppiumBy.ID,
        value: Union[str, Dict, None] = None,
        not_found_ignore: bool = True,
        retries: int = 0,
        delay: float = 0.5
    ) -> Union[List['Element'], List]:
        el = []
        for i in range(retries + 1):
            el = obj.find_elements(by=by, value=value)

            if len(el) > 0:
                break
            else:
                _log.debug(f"Elements not found: {value}")
                if i < retries - 1:
                    time.sleep(delay)
                continue

        if not not_found_ignore and len(el) == 0:
            raise NoSuchElementException(f"Element not found: {by} {value}")
        return [Element(appium_element=e) for e in el]


class Remote(AppiumWebDriver):
    def __init__(
        self,
        command_executor: Union[str, AppiumConnection] = 'http://127.0.0.1:4444/wd/hub',
        keep_alive: bool = True,
        direct_connection: bool = True,
        extensions: Optional[List['AppiumWebDriver']] = None,
        strict_ssl: bool = True,
        options: Union[AppiumOptions, List[AppiumOptions], None] = None,
    ):
        super().__init__(
            command_executor=command_executor,
            keep_alive=keep_alive,
            direct_connection=direct_connection,
            extensions=extensions,
            strict_ssl=strict_ssl,
            options=options
        )

    def get_element(
        self,
        by: str = AppiumBy.ID,
        value: Union[str, Dict, None] = None,
        not_found_ignore: bool = False,
        retries: int = 0,
        delay: float = 0.5
    ) -> Union['Element', None]:
        return Element._get_element(
            obj=self,
            by=by,
            value=value,
            not_found_ignore=not_found_ignore,
            retries=retries,
            delay=delay
        )

    def get_elements(
        self,
        by: str = AppiumBy.ID,
        value: Union[str, Dict, None] = None,
        not_found_ignore: bool = False,
        retries: int = 0,
        delay: float = 0.5
    ) -> Union[List['Element'], List]:
        return Element._get_elements(
            obj=self,
            by=by,
            value=value,
            not_found_ignore=not_found_ignore,
            retries=retries,
            delay=delay
        )

    def get_element_by_css(
        self,
        value: Union[str, Dict, None] = None,
        not_found_ignore: bool = False,
        retries: int = 0,
        delay: float = 0.5
    ):
        return self.get_element(
            by=AppiumBy.CSS_SELECTOR,
            value=value,
            not_found_ignore=not_found_ignore,
            retries=retries,
            delay=delay
        )

    def get_element_by_id(
        self,
        value: Union[str, Dict, None] = None,
        not_found_ignore: bool = False,
        retries: int = 0,
        delay: float = 0.5
    ):
        return self.get_element_by_css(
            value=f'[id="f{value}"]',
            not_found_ignore=not_found_ignore,
            retries=retries,
            delay=delay
        )

    def get_elements_by_css(
        self,
        value: Union[str, Dict, None] = None,
        not_found_ignore: bool = False,
        retries: int = 0,
        delay: float = 0.5
    ):
        return self.get_elements(
            by=AppiumBy.CSS_SELECTOR,
            value=value,
            not_found_ignore=not_found_ignore,
            retries=retries,
            delay=delay
        )

    def get_element_and_click(self, by, selector, retries=0, delay=0.5, error_skip=False):
        for i in range(retries + 1):
            try:
                e = self.get_element(by=by, value=selector, retries=0, delay=delay, not_found_ignore=error_skip)
                if e is not None:
                    e.click()
            except Exception as e:
                _log.debug(f"Get element and click error: {e}")
                if i < retries - 1:
                    time.sleep(delay)
                    continue
                else:
                    if not error_skip:
                        raise e


def connect(*args, server="http://127.0.0.1:4723", caps={}, **kwargs):
    options = AppiumOptions().load_capabilities(caps=caps)
    return Remote(command_executor=server, options=options, strict_ssl=False)


def get_webdriver_from_context(kwargs):
    if "executor" in kwargs:
        return kwargs["executor"].variables.get("$webdriver")


def execute_script(*args, webdriver: Remote, script: str, params=None, **kwargs) -> Any:
    return webdriver.execute_script(script=script, *params)


def get_element(
    *args,
    webdriver: Optional[Remote] = None,
    element: Optional[Element] = None,
    selector: str,
    by: str = "css",
    retries: int = 0,
    delay: float = 0.5,
    error_skip: bool = False,
    **kwargs
) -> Optional[Element]:
    if by == "tag":
        a_by = AppiumBy.TAG_NAME
    elif by == "css":
        a_by = AppiumBy.CSS_SELECTOR
    elif by == "class":
        a_by = AppiumBy.CLASS_NAME
    else:
        a_by = by

    if webdriver is None:
        webdriver = get_webdriver_from_context(kwargs)

    if element is not None:
        return element.get_element(by=a_by, value=selector, retries=retries, delay=delay, not_found_ignore=error_skip)
    elif webdriver is not None:
        return webdriver.get_element(by=a_by, value=selector, retries=retries, delay=delay, not_found_ignore=error_skip)
    else:
        raise ValueError("No element or webdriver specified.")


def get_elements(
    *args,
    webdriver: Optional[Remote] = None,
    element: Optional[Element] = None,
    selector: str,
    by: str = "css",
    retries: int = 0,
    delay: float = 0.5,
    error_skip: bool = False,
    **kwargs
) -> List[Element]:
    if by == "tag":
        a_by = AppiumBy.TAG_NAME
    elif by == "css":
        a_by = AppiumBy.CSS_SELECTOR
    elif by == "class":
        a_by = AppiumBy.CLASS_NAME
    else:
        a_by = by

    if webdriver is None:
        webdriver = get_webdriver_from_context(kwargs)

    if element is not None:
        return element.get_elements(
            by=a_by,
            value=selector,
            retries=retries,
            delay=delay,
            not_found_ignore=error_skip
        )
    elif webdriver is not None:
        return webdriver.get_elements(
            by=a_by,
            value=selector,
            retries=retries,
            delay=delay,
            not_found_ignore=error_skip
        )
    else:
        raise ValueError("No element or webdriver specified.")


def send_keys(*args, element: Element, keys: str, **kwargs):
    element.send_keys(keys)


def click(
    element: Optional[Element] = None,
    webdriver: Optional[Remote] = None,
    by: Optional[AppiumBy] = None,
    selector: Optional[str] = None,
    retries: int = 0,
    error_skip: bool = False,
    *args,
    **kwargs
):
    if webdriver is None:
        webdriver = get_webdriver_from_context(kwargs)

    if element:
        return element.click()
    else:
        if webdriver is None:
            raise ValueError("webdirver is none")
        return webdriver.get_element_and_click(by=by, selector=selector, retries=retries, error_skip=error_skip)


def get_attr(*args, element: Element, name: str, **kwargs) -> Any:
    return element.get_attribute(name=name)


def text(element: Element, *args, **kwargs) -> Any:
    return element.text


def execute(*args, webdriver: Optional[Remote] = None, command: str, params: Optional[Dict] = None, **kwargs) -> Any:
    if webdriver is None:
        webdriver = get_webdriver_from_context(kwargs)

    if webdriver is None:
        raise ValueError("webdriver is none.")

    if params is None:
        params = {}
    return webdriver.execute(driver_command=command, params=params)


def win_click(
    element: Element,
    button: Literal["left", "right"] = "left",
    webdriver: Optional[Remote] = None,
    **kwargs
):
    if webdriver is None:
        webdriver = get_webdriver_from_context(kwargs)

    webdriver.execute_script("windows:click", {
        "elementId": element.id,
        "button": button
    })


def win_get_clipboard(type: Literal["plaintext", "image"] = "plaintext", webdriver: Optional[Remote] = None, **kwargs):
    if webdriver is None:
        webdriver = get_webdriver_from_context(kwargs)

    result = webdriver.execute_script("windows:getClipboard", {
        "contentType": type
    })

    return result


def win_set_clipboard(
    type: Literal["plaintext", "image"] = "plaintext",
    content: str = "",
    webdriver: Optional[Remote] = None,
    **kwargs
):
    if webdriver is None:
        webdriver = get_webdriver_from_context(kwargs)

    webdriver.execute_script("windows:setClipboard", {
        "contentType": type,
        "b64Content": content
    })


def win_scroll(element: Element, deltaX=None, deltaY=None, webdriver: Optional[Remote] = None, **kwargs):
    if webdriver is None:
        webdriver = get_webdriver_from_context(kwargs)

    params = {
        "elementId": element.id
    }

    if deltaX is not None:
        params["deltaX"] = deltaX
    if deltaY is not None:
        params["deltaY"] = deltaY

    webdriver.execute_script("windows:scroll", params)


def create_actions() -> Dict[str, Action]:
    actions = {}
    actions["wd.connect"] = create(func=connect, spec={
        "name": "wd.connect",
        "description": "Establish a connection to the Appium server with the specified server address and capabilities.",  # noqa: E501
        "arguments": [
                {
                    "name": "server",
                    "type": "string",
                    "description": "The URL of the Appium server to connect to.",
                    "default": "http://127.0.0.1:4723"
                },
            {
                    "name": "caps",
                    "type": "object",
                    "description": "A dictionary of capabilities to be passed to the Appium server.",
                    "default": {}
                    }
        ]
    })
    actions["wd.execute_script"] = create(func=execute_script, spec={
        "name": "wd.execute_script",
        "description": "Execute a given JavaScript script on the current page.",
        "arguments": [
            {
                "name": "webdriver",
                "type": "WebDriver",
                "description": "The WebDriver instance to execute the script on.",
                "required": True
            },
            {
                "name": "javascript",
                "type": "string",
                "description": "The JavaScript code to execute.",
                "required": True
            }
        ]
    })
    actions["wd.get_element"] = create(func=get_element, spec={
        "name": "wd.get_element",
        "description": "Retrieve a single web element based on the specified selector and search method.",
        "arguments": [
            {
                "name": "webdriver",
                "type": "WebDriver",
                "description": "The WebDriver instance to use for finding the element.",
                "required": False
            },
            {
                "name": "element",
                "type": "Element",
                "description": "The Element instance to use as the starting point for the search.",
                "required": False
            },
            {
                "name": "selector",
                "type": "string",
                "description": "The selector string used to find the element.",
                "required": True
            },
            {
                "name": "by",
                "type": "string",
                "description": "The method to use for the search (e.g., 'css' for CSS Selector, 'xpath' for XPath).",
                "default": "css",
                "required": False
            }
        ]
    })
    actions["wd.get_elements"] = create(func=get_elements, spec={
        "name": "wd.get_elements",
        "description": "Retrieve all web elements that match the specified selector and search method.",
        "arguments": [
            {
                "name": "webdriver",
                "type": "WebDriver",
                "description": "The WebDriver instance to use for finding the elements.",
                "required": False
            },
            {
                "name": "element",
                "type": "Element",
                "description": "The Element instance to use as the starting point for the search.",
                "required": False
            },
            {
                "name": "selector",
                "type": "string",
                "description": "The selector string used to find the elements.",
                "required": True
            },
            {
                "name": "by",
                "type": "string",
                "description": "The method to use for the search (e.g., 'css' for CSS Selector, 'xpath' for XPath).",
                "default": "css",
                "required": False
            }
        ]
    })
    actions["wd.get_attr"] = create(func=get_attr, spec={
        "name": "wd.get_attr",
        "description": "Retrieve the value of a specified attribute from the element.",
        "arguments": [
            {
                "name": "element",
                "type": "Element",
                "description": "The Element instance to retrieve the attribute from.",
                "required": True
            },
            {
                "name": "name",
                "type": "string",
                "description": "The name of the attribute to retrieve.",
                "required": True
            }
        ]
    })
    actions["wd.text"] = create(func=text, spec={
        "name": "wd.text",
        "description": "Retrieve the text content of the element.",
        "arguments": [
            {
                "name": "element",
                "type": "Element",
                "description": "The Element instance to retrieve the text from.",
                "required": True
            }
        ]
    })
    actions["wd.send_keys"] = create(func=send_keys, spec={
        "name": "wd.send_keys",
        "description": "Send keystrokes to the specified element.",
        "arguments": [
            {
                "name": "element",
                "type": "Element",
                "description": "The Element instance to send the keystrokes to.",
                "required": True
            },
            {
                "name": "keys",
                "type": "str",
                "description": "The string of keystrokes to send to the element.",
                "required": True
            }
        ]
    })
    actions["wd.click"] = create(func=click, spec={
        "name": "wd.click",
        "description": "Simulate a mouse click on the specified element.",
        "arguments": [
            {
                "name": "element",
                "type": "Element",
                "description": "The Element instance to perform the click action on.",
                "required": True
            }
        ]
    })

    actions["wd.execute"] = create(func=execute, spec={
        "name": "wd.execute",
        "description": "Execute a command"
    })

    actions["wd.win.click"] = create(func=win_click, spec={
        "name": "wd.win.click",
        "description": "Windows click"
    })

    actions["wd.win.get_clipboard"] = create(func=win_get_clipboard, spec={
        "name": "wd.win.get_clipboard",
        "description": "Windows get clipboard"
    })

    actions["wd.win.set_clipboard"] = create(func=win_set_clipboard, spec={
        "name": "wd.win.get_clipboard",
        "description": "Windows set clipboard"
    })

    actions["wd.win.scroll"] = create(func=win_scroll, spec={
        "name": "wd.win.scroll",
        "description": "Windows scroll"
    })

    return actions
