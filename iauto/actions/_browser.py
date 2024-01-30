from typing import Any, Optional

from playwright.sync_api import Browser, Page, sync_playwright

from ._action import Action, ActionSpec


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

    def perform(self, *args, exec=None, **kwargs) -> Browser:
        pw = sync_playwright().start()
        browser = pw.chromium.launch(
            executable_path=exec,
            headless=False
        )

        return browser


class NewPageAction(Action):
    def perform(self, *args, browser: Browser, **kwargs) -> Page:
        page = browser.new_page()

        return page


class GotoAction(Action):
    def perform(
        self,
        *args,
        browser: Optional[Browser] = None,
        page: Optional[Page] = None,
        url: str,
        **kwargs
    ) -> Page:
        if page is None and browser is None:
            raise ValueError("got action must specify browser or page.")

        if page is None:
            page = browser.new_page()
        page.goto(url=url)

        return page


class EvaluateJavascriptAction(Action):
    def perform(self, *args, page: Page, javascript: str, **kwargs) -> Any:
        result = page.evaluate(javascript)

        return result
