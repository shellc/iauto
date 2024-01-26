from typing import Any, Dict
from ia.actions._action import ActionDef
from ._action import Action
from playwright.sync_api import sync_playwright, Browser, Page


class OpenBrowserAction(Action):
    def definition(self) -> ActionDef:
        return super().definition()

    def perform(self, **args: Any) -> Dict:
        # browser_type = args.get("browser") or "chromium"
        exec_path = args.get("exec_path")

        pw = sync_playwright().start()
        browser = pw.chromium.launch(
            executable_path=exec_path,
            headless=False
        )

        return {"browser": browser}


class NewPageAction(Action):
    def definition(self) -> ActionDef:
        return super().definition()

    def perform(self, **args: Any) -> Dict:
        browser: Browser = args.get("browser")

        page = browser.new_page()

        return {"page": page}


class GotoAction(Action):
    def definition(self) -> ActionDef:
        return super().definition()

    def perform(self, **args: Any) -> Dict:
        page: Page = args.get("page")
        url = args.get("url")

        page.goto(url=url)

        return {"page": page}


class EvaluateJavascriptAction(Action):
    def definition(self) -> ActionDef:
        return super().definition()

    def perform(self, **args: Any) -> Dict:
        page: Page = args.get("page")
        javascript = args.get("javascript")
        result = page.evaluate(javascript)

        return {"result": result}
