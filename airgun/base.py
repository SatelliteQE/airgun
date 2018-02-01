
NAVBAR_PATH = (
    '//div[contains(@class,"navbar-inner") and '
    'not(contains(@style, "display"))]')
MENU_CONTAINER_PATH = NAVBAR_PATH + '//ul[@id="menu"]'


def menu_click(tree, browser):
    for i, element in enumerate(tree, start=1):
        locator = MENU_CONTAINER_PATH + element
        browser.wait_for_element(locator, ensure_page_safe=True)
        browser.move_to_element(locator)
        browser.plugin.ensure_page_safe()
        if len(tree) == i:
            browser.wait_for_element(locator, ensure_page_safe=True)
            browser.click(locator)
            browser.plugin.ensure_page_safe()
