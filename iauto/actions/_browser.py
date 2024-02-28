import asyncio
import json
from concurrent.futures import ThreadPoolExecutor
from typing import Any, List, Optional, Union

from playwright.async_api import (Browser, BrowserContext, Locator, Page,
                                  async_playwright)

from ._action import Action, ActionSpec
from ._loader import register_action

_event_loop = asyncio.new_event_loop()
_thread_executor = ThreadPoolExecutor()


class OpenBrowserAction(Action):
    def __init__(self) -> None:
        super().__init__()
        self.spec = ActionSpec.from_dict({
            "name": "browser.open",
            "description": "Use Playwright to open a browser.",
            "arguments": [
                {
                    "name": "exec",
                    "type": "string",
                    "description": "Browser executable path.",
                    "required": True
                },
                {
                    "name": "headless",
                    "type": "bool",
                    "description": "Is the headless mode used.",
                    "required": False
                }
            ]
        })

    def perform(self,
                *args,
                exec=None,
                headless=False,
                timeout=30000,
                entry=None,
                user_data_dir=None,
                devtools=False,
                playbook,
                executor,
                **kwargs
                ) -> Union[Browser, BrowserContext]:
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
            if user_data_dir:
                browser = await _playwright.chromium.launch_persistent_context(
                    user_data_dir=user_data_dir,
                    executable_path=exec,
                    headless=headless,
                    timeout=timeout,
                    args=b_args,
                    devtools=devtools,
                    **kwargs
                )
            else:
                browser = await _playwright.chromium.launch(
                    executable_path=exec,
                    headless=headless,
                    timeout=timeout,
                    args=b_args,
                    devtools=devtools,
                    **kwargs
                )
            return browser
        return _event_loop.run_until_complete(_func())


class CloseBrowserAction(Action):
    def __init__(self) -> None:
        super().__init__()
        self.spec = ActionSpec.from_dict({
            "description": "Close the browser.",
        })

    def perform(self, browser: Browser, *args, **kwargs) -> Any:
        async def _func():
            return await browser.close()
        return _event_loop.run_until_complete(_func())


class GotoAction(Action):
    def __init__(self) -> None:
        super().__init__()
        self.spec = ActionSpec.from_dict({
            "description": "Open URL in the browser.",
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
            "description": "Locate elements in the page.",
        })

    def perform(
        self,
        *args,
        page: Page,
        selector: Union[str, List[str]],
        wait: bool = False,
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
                    await loc.wait_for()
                else:
                    count = await loc.count()
                    if loc is not None and count > 0:
                        return loc
        return _event_loop.run_until_complete(_func())


class ClickAction(Action):
    def __init__(self) -> None:
        super().__init__()
        self.spec = ActionSpec.from_dict({
            "description": "Click a element.",
        })

    def perform(
        self,
        *args,
        locator: Optional[Locator] = None,
        page: Optional[Page] = None,
        selector: Optional[List[str]] = None,
        **kwargs
    ):
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


class ScrollAction(Action):
    def __init__(self) -> None:
        super().__init__()
        self.spec = ActionSpec.from_dict({
            "description": "Scroll the mouse wheel.",
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
            "description": "Execute JavaScript in the browser page.",
        })

    def perform(self, *args, page: Page, javascript: str, **kwargs) -> Any:
        async def _func(page):
            return await page.evaluate(javascript)

        return _event_loop.run_until_complete(_func(page=page))


class GetContentAction(Action):
    def __init__(self) -> None:
        super().__init__()
        self.spec = ActionSpec.from_dict({
            "description": "Get the HTML content of the page.",
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
            "description": "Convert the HTML content to easy-to-read pure text content.",
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


def replay(*args, browser: Browser, script: str, executor, **kwargs):
    if not script.startswith("{"):
        with open(executor.resolve_path(script), "r") as f:
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


register_action(name="browser.replay", spec={})(replay)
