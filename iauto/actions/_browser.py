import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Optional

from playwright.async_api import Browser, Page, async_playwright

from ._action import Action, ActionSpec

_event_loop = asyncio.new_event_loop()
_thread_executor = ThreadPoolExecutor()


class OpenBrowserAction(Action):
    def __init__(self) -> None:
        super().__init__()
        self.spec = ActionSpec.from_dict({
            "name": "browser.open",
            "description": "Use this tool to open browser.",
            "arguments": [
                {
                    "name": "exec",
                    "type": "string",
                    "description": "Browser executable path.",
                    "required": True
                }
            ]
        })

    def perform(self, *args, exec=None, headless=False, timeout=30000, **kwargs) -> Browser:
        async def _func():
            _playwright = await async_playwright().start()
            browser = await _playwright.chromium.launch(
                executable_path=exec,
                headless=headless,
                timeout=timeout
            )
            return browser
        return _event_loop.run_until_complete(_func())


class CloseBrowserAction(Action):
    def perform(self, browser: Browser, *args, **kwargs) -> Any:
        async def _func():
            return await browser.close()
        return _event_loop.run_until_complete(_func())


class NewPageAction(Action):
    def perform(self, *args, browser: Browser, **kwargs) -> Page:
        async def _func(browser):
            if len(browser.contexts) == 0:
                await browser.new_context()
            context = browser.contexts[0]

            page = await context.new_page()
            return page

        return _event_loop.run_until_complete(_func(browser=browser))


class GotoAction(Action):
    def perform(
        self,
        *args,
        browser: Optional[Browser] = None,
        page: Optional[Page] = None,
        url: str,
        timeout=30000,
        **kwargs
    ) -> Page:
        async def _func(browser, page):
            if page is None and browser is None:
                raise ValueError("got action must specify browser or page.")

            if len(browser.contexts) == 0:
                await browser.new_context()
            context = browser.contexts[0]

            if page is None:
                page = await context.new_page()

            await page.goto(url=url, timeout=timeout)
            await page.wait_for_load_state(state="domcontentloaded", timeout=timeout)
            return page
        return _event_loop.run_until_complete(_func(browser=browser, page=page))


class EvaluateJavascriptAction(Action):
    def perform(self, *args, page: Page, javascript: str, **kwargs) -> Any:
        async def _func(page):
            return await page.evaluate(javascript)

        return _event_loop.run_until_complete(_func(page=page))


class GetContentAction(Action):
    def perform(self, *args, page: Page, **kwargs) -> Any:
        async def _func(page):
            return await page.content()
        return _event_loop.run_until_complete(_func(page=page))


class ReadabilityAction(Action):
    def perform(self, content: str, *args, **kwargs) -> Any:
        try:
            from bs4 import BeautifulSoup
            from readability import Document

            doc = Document(content)
            soup = BeautifulSoup(doc.summary(), 'html.parser')
            return "" + soup.get_text()
        except ImportError:
            print("readability not found, readability-lxml and beautifulsoup4 required.")
