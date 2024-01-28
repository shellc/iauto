from typing import Any
from ._action import Action
from playwright.sync_api import sync_playwright, Browser, Page


class OpenBrowserAction(Action):
    def perform(self, *args, exec=None, **kwargs) -> Browser:
        pw = sync_playwright().start()
        browser = pw.chromium.launch(
            executable_path=exec,
            headless=False
        )

        return browser


class NewPageAction(Action):
    def perform(self, *args, browser: Browser = None, **kwargs) -> Page:
        page = browser.new_page()

        return page


class GotoAction(Action):
    def perform(self, *args, browser: Browser = None, page: Page = None, url: str = None, **kwargs) -> Page:
        if page is None and browser is None:
            raise ValueError("got action must specify browser or page.")

        if page is None:
            page = browser.new_page()
        page.goto(url=url)

        return page


class EvaluateJavascriptAction(Action):
    def perform(self, *args, page: Page = None, javascript: str = None, **kwargs) -> Any:
        result = page.evaluate(javascript)

        return result
