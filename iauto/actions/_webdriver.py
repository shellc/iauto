import time
from typing import Dict, List, Optional, Union

from appium.options.common.base import AppiumOptions
from appium.webdriver.appium_connection import AppiumConnection
from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webdriver import WebDriver as AppiumWebDriver
from appium.webdriver.webelement import WebElement
from selenium.common.exceptions import (ElementNotInteractableException,
                                        NoSuchElementException)

from .._logging import get_logger
from ._action import create_action

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
    ) -> 'Element':
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
    ) -> 'Element':
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
    ) -> 'Element':
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


def create_webdriver(*args, server="http://127.0.0.1:4723", caps={}, **kwargs):
    options = AppiumOptions().load_capabilities(caps=caps)
    return Remote(command_executor=server, options=options, strict_ssl=False)


def create_actions():
    actions = {}
    actions["wd.create"] = create_action(func=create_webdriver, spec={})
