from ..loader import loader
from . import browser
from .webdriver import create_actions as create_wd_actions

actions = {}

actions["browser.open"] = browser.OpenBrowserAction()
actions["browser.close"] = browser.CloseBrowserAction()
actions["browser.goto"] = browser.GotoAction()
actions["browser.locator"] = browser.LocatorAction()
actions["browser.click"] = browser.ClickAction()
actions["browser.scroll"] = browser.ScrollAction()
actions["browser.eval"] = browser.EvaluateJavascriptAction()
actions["browser.content"] = browser.GetContentAction()
actions["browser.readability"] = browser.ReadabilityAction()

wd_actions = create_wd_actions()

actions.update(wd_actions)

loader.register(actions)
