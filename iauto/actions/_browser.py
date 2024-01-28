from typing import Any, Dict
from ._action import Action
from playwright.sync_api import sync_playwright, Browser, Page


class OpenBrowserAction(Action):
    def perform(self, **args: Any) -> Browser:
        # browser_type = args.get("browser") or "chromium"
        exec_path = args.get("exec_path")

        pw = sync_playwright().start()
        browser = pw.chromium.launch(
            executable_path=exec_path,
            headless=False
        )

        return browser


class NewPageAction(Action):
    def perform(self, **args: Any) -> Page:
        browser: Browser = args.get("browser")

        page = browser.new_page()

        return page


class GotoAction(Action):
    def perform(self, **args: Any) -> Page:
        page: Page = args.get("page")
        url = args.get("url")

        page.goto(url=url)

        return page


class EvaluateJavascriptAction(Action):
    def perform(self, **args: Any) -> Any:
        page: Page = args.get("page")
        javascript = args.get("javascript")
        result = page.evaluate(javascript)

        return result
