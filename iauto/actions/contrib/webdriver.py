import time
from typing import Any, Dict, List, Optional, Union

from appium.options.common.base import AppiumOptions
from appium.webdriver.appium_connection import AppiumConnection
from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webdriver import WebDriver as AppiumWebDriver
from appium.webdriver.webelement import WebElement
from selenium.common.exceptions import (ElementNotInteractableException,
                                        NoSuchElementException)

from ...log import get_logger
from ..action import Action, create_action

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
            raise NoSuchElementException(f"Element not found: {value}")
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

    def get_element_and_click(self, css_selector, retries=0, delay=0.5, error_skip=False):
        for i in range(retries + 1):
            try:
                e = self.get_element_by_css(value=css_selector, retries=0, delay=0.5, error_skip=error_skip)
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


def execute_script(*args, webdriver: Remote, javascript: str, **kwargs) -> Any:
    return webdriver.execute_script(javascript)


def get_element(
    *args,
    webdriver: Optional[Remote] = None,
    element: Optional[Element] = None,
    selector: str,
    by: str = "css",
    **kwargs
) -> Optional[Element]:
    a_by = AppiumBy.CSS_SELECTOR
    if by == "xpath":
        a_by = AppiumBy.XPATH

    if element is not None:
        return element.get_element(by=a_by, value=selector)
    elif webdriver is not None:
        return webdriver.get_element(by=a_by, value=selector)
    else:
        raise ValueError("No element or webdriver specified.")


def get_elements(
    *args,
    webdriver: Optional[Remote] = None,
    element: Optional[Element] = None,
    selector: str,
    by: str = "css",
    **kwargs
) -> List[Element]:
    a_by = AppiumBy.CSS_SELECTOR
    if by == "xpath":
        a_by = AppiumBy.XPATH

    if element is not None:
        return element.get_elements(by=a_by, value=selector)
    elif webdriver is not None:
        return webdriver.get_elements(by=a_by, value=selector)
    else:
        raise ValueError("No element or webdriver specified.")


def send_keys(*args, element: Element, content, **kwargs):
    element.send_keys(content)


def click(element: Element, *args, **kwargs):
    element.click()


def get_attr(*args, element: Element, name: str, **kwargs) -> Any:
    return element.get_attribute(name=name)


def text(element: Element, *args, **kwargs) -> Any:
    return element.text


def execute(*args, webdriver: Remote, command: str, params, **kwargs) -> Any:
    return webdriver.execute(driver_command=command, params=params)


def create_actions() -> Dict[str, Action]:
    actions = {}
    actions["wd.connect"] = create_action(func=connect, spec={
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
    actions["wd.execute_script"] = create_action(func=execute_script, spec={
        "name": "wd.execute_script",
        "description": "Execute a given JavaScript script on the current page.",
        "arguments": [
            {
                "name": "webdriver",
                "type": "Remote",
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
    actions["wd.get_element"] = create_action(func=get_element, spec={
        "name": "wd.get_element",
        "description": "Retrieve a single web element based on the specified selector and search method.",
        "arguments": [
            {
                "name": "webdriver",
                "type": "Optional[Remote]",
                "description": "The WebDriver instance to use for finding the element.",
                "required": False
            },
            {
                "name": "element",
                "type": "Optional[Element]",
                "description": "The Element instance to use as the starting point for the search.",
                "required": False
            },
            {
                "name": "selector",
                "type": "str",
                "description": "The selector string used to find the element.",
                "required": True
            },
            {
                "name": "by",
                "type": "str",
                "description": "The method to use for the search (e.g., 'css' for CSS Selector, 'xpath' for XPath).",
                "default": "css",
                "required": False
            }
        ]
    })
    actions["wd.get_elements"] = create_action(func=get_elements, spec={
        "name": "wd.get_elements",
        "description": "Retrieve all web elements that match the specified selector and search method.",
        "arguments": [
            {
                "name": "webdriver",
                "type": "Optional[Remote]",
                "description": "The WebDriver instance to use for finding the elements.",
                "required": False
            },
            {
                "name": "element",
                "type": "Optional[Element]",
                "description": "The Element instance to use as the starting point for the search.",
                "required": False
            },
            {
                "name": "selector",
                "type": "str",
                "description": "The selector string used to find the elements.",
                "required": True
            },
            {
                "name": "by",
                "type": "str",
                "description": "The method to use for the search (e.g., 'css' for CSS Selector, 'xpath' for XPath).",
                "default": "css",
                "required": False
            }
        ]
    })
    actions["wd.get_attr"] = create_action(func=get_attr, spec={
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
                "type": "str",
                "description": "The name of the attribute to retrieve.",
                "required": True
            }
        ]
    })
    actions["wd.text"] = create_action(func=text, spec={
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
    actions["wd.send_keys"] = create_action(func=send_keys, spec={
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
                "name": "content",
                "type": "str",
                "description": "The string of keystrokes to send to the element.",
                "required": True
            }
        ]
    })
    actions["wd.click"] = create_action(func=click, spec={
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

    return actions
