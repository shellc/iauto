import asyncio
import json
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Literal, Optional, Union

from playwright.async_api import (Browser, BrowserContext, Locator, Page,
                                  async_playwright)

from ..action import Action, ActionSpec
from ..loader import register

_event_loop = asyncio.new_event_loop()
_thread_executor = ThreadPoolExecutor()


class OpenBrowserAction(Action):
    def __init__(self) -> None:
        super().__init__()
        self.spec = ActionSpec.from_dict({
            "name": "browser.open",
            "description": "Opens a new browser instance.",
            "arguments": [
                {
                    "name": "exec",
                    "type": "string",
                    "description": "Path to the browser executable.",
                    "required": True
                },
                {
                    "name": "headless",
                    "type": "bool",
                    "description": "Indicates whether to launch the browser in headless mode.",
                    "required": False
                },
                {
                    "name": "timeout",
                    "type": "int",
                    "description": "The maximum time to wait for the browser instance to start.",
                    "required": False
                },
                {
                    "name": "entry",
                    "type": "string",
                    "description": "The URL to open upon launching the browser.",
                    "required": False
                },
                {
                    "name": "user_data_dir",
                    "type": "string",
                    "description": "The path to a directory where user data can be stored.",
                    "required": False
                },
                {
                    "name": "devtools",
                    "type": "bool",
                    "description": "Whether to open the devtools panel on start.",
                    "required": False
                }
            ]
        })

    def perform(self,
                *args,
                browser_type: Optional[str] = None,
                exec: Optional[str] = None,
                headless: Union[bool, str] = False,
                timeout=30000,
                entry=None,
                user_data_dir=None,
                devtools=False,
                extra_kwargs: Optional[Dict] = None,
                playbook,
                executor,
                **kwargs
                ) -> Union[Browser, BrowserContext]:

        if browser_type is None:
            browser_type = "chromium"

        if isinstance(headless, str):
            headless = headless.lower() == "true"

        if extra_kwargs is None:
            extra_kwargs = {}

        async def _func():
            b_args = [
                "--mute-audio",
                "--disable-features=AudioServiceOutOfProcess,VideoCapture",
                "--disable-notifications",
                '--disable-infobars',
            ]

            if headless:
                b_args.append("--disable-gpu")

            if entry:
                b_args.append(f"--app={entry}")

            if "size" in kwargs:
                b_args.append(f"--window-size={kwargs['size']}")

            _playwright = await async_playwright().start()

            browser_instance = None
            if browser_type == "chromium":
                browser_instance = _playwright.chromium
            elif browser_type == "firefox":
                browser_instance = _playwright.firefox
            elif browser_type == "webkit":
                browser_instance = _playwright.webkit
            else:
                raise IndexError(f"invalid browser_type: {browser_type}")

            if user_data_dir:
                browser = await browser_instance.launch_persistent_context(
                    user_data_dir=user_data_dir,
                    executable_path=exec,
                    headless=headless,
                    timeout=timeout,
                    args=b_args,
                    devtools=devtools,
                    **extra_kwargs
                )
            else:
                browser = await browser_instance.launch(
                    executable_path=exec,
                    headless=headless,
                    timeout=timeout,
                    args=b_args,
                    devtools=devtools,
                    **extra_kwargs
                )
            return browser
        return _event_loop.run_until_complete(_func())


class CloseBrowserAction(Action):
    def __init__(self) -> None:
        super().__init__()
        self.spec = ActionSpec.from_dict({
            "name": "browser.close",
            "description": "Closes the currently open browser instance.",
            "arguments": [
                {
                    "name": "browser",
                    "type": "Browser",
                    "description": "The browser instance to close.",
                    "required": True
                }
            ]
        })

    def perform(self, browser: Browser, *args, **kwargs) -> Any:
        async def _func():
            return await browser.close()
        return _event_loop.run_until_complete(_func())


class GotoAction(Action):
    def __init__(self) -> None:
        super().__init__()
        self.spec = ActionSpec.from_dict({
            "name": "browser.goto",
            "description": "Navigates to a specified URL in the browser.",
            "arguments": [
                {
                    "name": "browser",
                    "type": "Union[Browser, Page]",
                    "description": "The browser instance or page to navigate.",
                    "required": True
                },
                {
                    "name": "new_context",
                    "type": "Optional[bool]",
                    "description": "Whether to navigate in a new browser context.",
                    "required": False
                },
                {
                    "name": "url",
                    "type": "str",
                    "description": "The URL to navigate to.",
                    "required": True
                },
                {
                    "name": "timeout",
                    "type": "int",
                    "description": "Maximum time to wait for navigation to complete.",
                    "required": False
                }
            ]
        })

    def perform(
        self,
        *args,
        browser: Union[Browser, Page],
        new_context: Optional[bool] = False,
        url: str,
        timeout=30000,
        **kwargs
    ) -> Page:
        async def _func(browser):
            if browser is None:
                raise ValueError("got action must specify browser or page.")

            if isinstance(browser, Browser):
                if len(browser.contexts) == 0:
                    await browser.new_context()
                context = browser.contexts[0]
            else:
                context = browser

            page = None
            if not new_context and len(context.pages) > 0:
                page = context.pages[-1]

            if page is None:
                page = await context.new_page()

            await page.goto(url=url, timeout=timeout)
            await page.wait_for_load_state(state="domcontentloaded", timeout=timeout)
            return page
        return _event_loop.run_until_complete(_func(browser=browser))


class LocatorAction(Action):
    def __init__(self) -> None:
        super().__init__()
        self.spec = ActionSpec.from_dict({
            "name": "browser.locator",
            "description": "Finds elements in the page using a selector.",
            "arguments": [
                {
                    "name": "page",
                    "type": "Page",
                    "description": "The page object where the locator should be created.",
                    "required": True
                },
                {
                    "name": "selector",
                    "type": "Union[str, List[str]]",
                    "description": "The selector or list of selectors to locate the elements.",
                    "required": True
                },
                {
                    "name": "wait",
                    "type": "bool",
                    "description": "Whether to wait for the element to be present before returning the locator.",
                    "required": False,
                    "default": False
                },
                {
                    "name": "not_found",
                    "type": "Literal['fail', 'ignore']",
                    "description": "Action to take if no elements match the selector.",
                    "required": False,
                    "default": "fail"
                },
                {
                    "name": "timeout",
                    "type": "int",
                    "description": "Maximum time to wait for the element to be present, in milliseconds.",
                    "required": False,
                    "default": 3000
                }
            ]
        })

    def perform(
        self,
        *args,
        page: Page,
        selector: Union[str, List[str]],
        wait: bool = False,
        not_found: Literal["fail", "ignore"] = "fail",
        timeout: int = 3000,
        **kwargs
    ) -> Union[Locator, None]:
        async def _func():
            selectors = []
            if isinstance(selector, str):
                selectors.append(selector)
            elif isinstance(selector, List):
                for sel in selector:
                    if isinstance(sel, List):
                        selectors.extend(sel)
                    elif isinstance(sel, str):
                        selectors.append(sel)
            else:
                raise ValueError(f"invalid selector: {selector}")

            locator = None
            for sel in selectors:
                ignores = ["aria", "pierce", "xpath", "text"]
                ignore = False
                for i in ignores:
                    if sel.startswith(i):
                        ignore = True
                        break
                if ignore:
                    continue
                loc = page.locator(selector=sel)
                if wait:
                    try:
                        await loc.wait_for(timeout=timeout)
                    except Exception as e:
                        if not_found == "fail":
                            raise e
                        else:
                            return None
                    return loc
                else:
                    count = await loc.count()
                    if loc is not None and count > 0:
                        locator = loc
                        break
            if locator is None and not_found == "fail":
                raise RuntimeError(f"elements not found: {selector}")
            return locator
        return _event_loop.run_until_complete(_func())


class ClickAction(Action):
    def __init__(self) -> None:
        super().__init__()
        self.spec = ActionSpec.from_dict({
            "name": "browser.click",
            "description": "Performs a click on the specified element.",
            "arguments": [
                {
                    "name": "locator",
                    "type": "Optional[Locator]",
                    "description": "The locator object representing the element to click on.",
                    "required": False
                },
                {
                    "name": "page",
                    "type": "Optional[Page]",
                    "description": "The page object where the click should occur.",
                    "required": False
                },
                {
                    "name": "selector",
                    "type": "Optional[List[str]]",
                    "description": "A list of selectors to locate the element to click on.",
                    "required": False
                },
                {
                    "name": "on_fail",
                    "type": "Literal['ignore', 'fail']",
                    "description": "Action to take if the click fails.",
                    "required": False,
                    "default": "fail"
                }
            ]
        })

    def perform(
        self,
        *args,
        locator: Optional[Locator] = None,
        page: Optional[Page] = None,
        selector: Optional[List[str]] = None,
        on_fail: Literal["ignore", "fail"] = "fail",
        **kwargs
    ):
        try:
            if locator is not None:
                return _event_loop.run_until_complete(locator.click())
            elif selector:
                if page is None:
                    raise ValueError("arument `page` required")

                loc_action = LocatorAction()
                loc = loc_action.perform(page=page, selector=selector)
                if loc is not None:
                    return _event_loop.run_until_complete(loc.click())
            else:
                ...
        except Exception as e:
            if on_fail == "fail":
                raise e


class ScrollAction(Action):
    def __init__(self) -> None:
        super().__init__()
        self.spec = ActionSpec.from_dict({
            "name": "browser.scroll",
            "description": "Scrolls the page both horizontally and vertically.",
            "arguments": [
                {
                    "name": "page",
                    "type": "Page",
                    "description": "The page object to scroll.",
                    "required": True
                },
                {
                    "name": "x",
                    "type": "int",
                    "description": "The number of pixels to scroll horizontally.",
                    "required": False,
                    "default": 0
                },
                {
                    "name": "y",
                    "type": "int",
                    "description": "The number of pixels to scroll vertically.",
                    "required": False,
                    "default": 0
                }
            ]
        })

    def perform(
        self,
        *args,
        page: Page,
        x: int = 0,
        y: int = 0,
        **kwargs
    ) -> Locator:
        return _event_loop.run_until_complete(page.mouse.wheel(x, y))


class EvaluateJavascriptAction(Action):
    def __init__(self) -> None:
        super().__init__()
        self.spec = ActionSpec.from_dict({
            "name": "browser.eval",
            "description": "Executes JavaScript code in the current page context.",
            "arguments": [
                {
                    "name": "page",
                    "type": "Page",
                    "description": "The page object where the JavaScript will be executed.",
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

    def perform(
        self,
        *args,
        browser: Optional[Browser] = None,
        page: Optional[Page] = None,
        javascript: str,
        **kwargs
    ) -> Any:
        if page is None:
            page = get_default_page(browser=browser)
        if page is None:
            raise ValueError("page not found")

        async def _func(page):
            return await page.evaluate(javascript)

        return _event_loop.run_until_complete(_func(page=page))


class GetContentAction(Action):
    def __init__(self) -> None:
        super().__init__()
        self.spec = ActionSpec.from_dict({
            "name": "browser.content",
            "description": "Retrieves the HTML content of the current page or of the elements matching the specified selector.",  # noqa: E501
            "arguments": [
                {
                    "name": "browser",
                    "type": "Optional[Browser]",
                    "description": "The browser instance to retrieve content from.",
                    "required": False
                },
                {
                    "name": "page",
                    "type": "Optional[Page]",
                    "description": "The page object to retrieve content from.",
                    "required": False
                },
                {
                    "name": "selector",
                    "type": "Optional[List[str]]",
                    "description": "A list of selectors to locate the elements to retrieve content from.",
                    "required": False
                }
            ]
        })

    def perform(
        self,
        *args,
        browser: Optional[Browser] = None,
        page: Optional[Page] = None,
        selector: Optional[List[str]] = None,
        **kwargs
    ) -> Any:
        if page is None and browser is None:
            raise ValueError("missing args")

        if page is None:
            page = get_default_page(browser=browser)
        if page is None:
            raise ValueError("page not found")

        if selector:
            loc = LocatorAction()
            locator = loc.perform(page=page, selector=selector)
            if locator:
                async def _extract_texts():
                    texts = []
                    locs = await locator.all()
                    for loc_ in locs:
                        text = await loc_.inner_text()
                        if text == "":
                            text = await loc_.get_attribute("aria-label")
                        if text:
                            texts.append(text)
                    return texts
                return _event_loop.run_until_complete(_extract_texts())

        async def _func(page, browser):
            return await page.content()
        return _event_loop.run_until_complete(_func(page=page, browser=browser))


class ReadabilityAction(Action):
    def __init__(self) -> None:
        super().__init__()
        self.spec = ActionSpec.from_dict({
            "name": "browser.readability",
            "description": "Extracts the main content from the HTML, providing a clean and readable text.",
            "arguments": [
                {
                    "name": "content",
                    "type": "str",
                    "description": "The HTML content to process for readability.",
                    "required": True
                }
            ]
        })

    def perform(self, content: str, *args, **kwargs) -> Any:
        try:
            from bs4 import BeautifulSoup
            from readability import Document

            doc = Document(content)
            soup = BeautifulSoup(doc.summary(), 'html.parser')
            return "" + soup.get_text(separator="\n", strip=True)
        except ImportError:
            print("readability not found, readability-lxml and beautifulsoup4 required.")


def fill(
    *args,
    locator: Optional[Locator] = None,
    page: Optional[Page] = None,
    selector: Optional[List[str]] = None,
    value: str,
    **kwargs
):
    if locator is not None:
        return _event_loop.run_until_complete(locator.fill(value=value))
    elif selector:
        if page is None:
            raise ValueError("arument `page` required")
        loc_action = LocatorAction()
        loc = loc_action.perform(page=page, selector=selector)
        if loc is not None:
            return _event_loop.run_until_complete(loc.fill(value=value))


def key_down(*args, page: Page, key: str, **kwargs):
    return _event_loop.run_until_complete(page.keyboard.down(key))


def key_up(*args, page: Page, key: str, **kwargs):
    return _event_loop.run_until_complete(page.keyboard.up(key))


def wait_for(*args, page: Page, selector: str, **kwargs):
    return _event_loop.run_until_complete(page.locator(selector=selector).wait_for())


def get_default_page(*args, browser: Browser, **kwargs):
    if len(browser.contexts) > 0 and len(browser.contexts[0].pages) > 0:
        return browser.contexts[0].pages[0]


def replay(*args, browser: Browser, script: str, playbook, executor, **kwargs):
    if not script.startswith("{"):
        with open(playbook.resolve_path(script), "r") as f:
            script = f.read()
    try:
        data = json.loads(script)
        data = executor.eval_vars(data)
        steps = data["steps"]
    except Exception as e:
        raise ValueError(
            "Invalid replay script"
        ) from e

    result = None
    page = None
    for step in steps:
        tp = step["type"]
        if tp == "navigate" or tp == "goto":
            goto = GotoAction()
            page = goto.perform(browser=browser, url=step["url"])
            result = page
        elif tp == "click":
            clk = ClickAction()
            result = clk.perform(page=page, selector=step["selectors"])
        elif tp == "change":
            result = fill(page=page, selector=step["selectors"], value=step["value"])
        elif tp == "keyDown":
            result = key_down(page=page, key=step["key"])
        elif tp == "keyUp":
            result = key_up(page=page, key=step["key"])
        elif tp == "waitForElement":
            loc = LocatorAction()
            result = loc.perform(page=page, selector=step["selectors"], wait=True)
        elif tp == "setViewport":
            ...
        else:
            raise ValueError(f"Browser replay is an experimental feature that is currently not supported: {tp}")
    return result


register(name="browser.replay", spec={
    "description": "Replays a sequence of browser actions from a script.",
    "arguments": [
        {
            "name": "browser",
            "type": "Browser",
            "description": "The browser instance to replay the script with.",
            "required": True
        },
        {
            "name": "script",
            "type": "str",
            "description": "The path to the script file or the script content as a JSON string.",
            "required": True
        }
    ]
})(replay)
