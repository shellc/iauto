import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Optional, Union

from playwright.async_api import (Browser, BrowserContext, Locator, Page,
                                  async_playwright)

from ._action import Action, ActionSpec

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
                **kwargs
                ) -> Union[Browser, BrowserContext]:
        async def _func():
            b_args = [
                "--mute-audio",
                "--disable-features=AudioServiceOutOfProcess,VideoCapture"
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
                    args=b_args
                )
            else:
                browser = await _playwright.chromium.launch(
                    executable_path=exec,
                    headless=headless,
                    timeout=timeout,
                    args=b_args
                )
            return browser
        return _event_loop.run_until_complete(_func())


class CloseBrowserAction(Action):
    def __init__(self) -> None:
        super().__init__()
        self.spec = ActionSpec.from_dict({
            "description": "Close the browser.",
        })

    def perform(self, browser: Union[Browser, BrowserContext], *args, **kwargs) -> Any:
        async def _func():
            return await browser.close()
        return _event_loop.run_until_complete(_func())


class NewPageAction(Action):
    def __init__(self) -> None:
        super().__init__()
        self.spec = ActionSpec.from_dict({
            "description": "Open a new tab in the browser.",
        })

    def perform(self, *args, browser: Union[Browser, BrowserContext], **kwargs) -> Page:
        async def _func(browser):
            if not isinstance(browser, BrowserContext):
                if len(browser.contexts) == 0:
                    await browser.new_context()
                context = browser.contexts[0]
            else:
                context = browser

            page = await context.new_page()
            return page

        return _event_loop.run_until_complete(_func(browser=browser))


class GotoAction(Action):
    def __init__(self) -> None:
        super().__init__()
        self.spec = ActionSpec.from_dict({
            "description": "Open URL in the browser.",
        })

    def perform(
        self,
        *args,
        browser: Union[Browser, BrowserContext, None] = None,
        page: Optional[Page] = None,
        url: str,
        timeout=30000,
        **kwargs
    ) -> Page:
        async def _func(browser, page):
            if page is None and browser is None:
                raise ValueError("got action must specify browser or page.")

            if not isinstance(browser, BrowserContext):
                if len(browser.contexts) == 0:
                    await browser.new_context()
                context = browser.contexts[0]
            else:
                context = browser

            if page is None:
                page = await context.new_page()

            await page.goto(url=url, timeout=timeout)
            await page.wait_for_load_state(state="domcontentloaded", timeout=timeout)
            return page
        return _event_loop.run_until_complete(_func(browser=browser, page=page))


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
        selector: str,
        **kwargs
    ) -> Locator:
        return page.locator(selector=selector)


class ClickAction(Action):
    def __init__(self) -> None:
        super().__init__()
        self.spec = ActionSpec.from_dict({
            "description": "Click a element.",
        })

    def perform(
        self,
        *args,
        locator: Locator,
        **kwargs
    ) -> Locator:
        return _event_loop.run_until_complete(locator.click())


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

    def perform(self, *args, page: Page, **kwargs) -> Any:
        async def _func(page):
            return await page.content()
        return _event_loop.run_until_complete(_func(page=page))


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
            return "" + soup.get_text()
        except ImportError:
            print("readability not found, readability-lxml and beautifulsoup4 required.")
