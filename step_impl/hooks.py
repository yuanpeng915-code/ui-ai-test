import os
from pathlib import Path

from getgauge.python import before_suite, after_suite, data_store
from playwright.sync_api import Page

from utils.dirver import ChromeDriver
from utils.data_loader import ACCOUNTS, ROUTERS
from utils.page_helper import PageHelper

ROOT = Path(__file__).resolve().parent.parent

# ---------------
# Custom Screenshot Writer (browser-level instead of desktop)
# ---------------

try:
    from getgauge.python import custom_screenshot_writer
    from utils.page_helper import save_screenshots_merged

    @custom_screenshot_writer
    def take_screenshot():
        screenshots_dir = os.getenv("gauge_screenshots_dir")
        if not screenshots_dir:
            return ""

        driver: ChromeDriver | None = data_store.suite.get("driver")
        browser = driver.browser if driver else None
        if browser is None:
            return ""

        # 识别各 context 身份：admin(管理端) / user(用户端) / ctxN(其它)
        admin_page: Page | None = data_store.suite.get("page")
        admin_ctx = admin_page.context if admin_page else None
        user_ctx = data_store.suite.get("user_context")

        pages: list[tuple[str, Page]] = []
        for ctx_idx, ctx in enumerate(browser.contexts):
            if ctx is admin_ctx:
                ctx_label = "admin"
            elif ctx is user_ctx:
                ctx_label = "user"
            else:
                ctx_label = f"ctx{ctx_idx}"
            ctx_pages = ctx.pages
            for pg_idx, pg in enumerate(ctx_pages):
                # 单 context 只有一页时沿用 ctx_label，多页时带页号
                pg_label = ctx_label if len(ctx_pages) == 1 else f"{ctx_label}-p{pg_idx}"
                pages.append((pg_label, pg))

        return save_screenshots_merged(pages, "failure", screenshots_dir)

except ImportError:
    pass  # old Gauge-python does not support custom_screenshot_writer

# ---------------
# Execution Hooks
# ---------------

@before_suite
def init_test_env():
    # ----test driver----
    driver = ChromeDriver()
    data_store.suite["driver"] = driver
    data_store.suite["page"] = driver.page
    data_store.suite["page_helper"] = PageHelper(driver.page)

    # default auto login admin
    page = data_store.suite["page"]
    page.goto(ACCOUNTS["bastion_admin"]["url"], wait_until="domcontentloaded")
    page.wait_for_timeout(2000)
    page.locator("#username").fill("admin")
    page.locator("#password").fill("1qaz2wsx#EDC")
    page.get_by_role("button").filter(has_text="登").first.click()

    page.wait_for_url("**/workbench**", timeout=15000)
    assert "/login" not in page.url

    # ---store test data----
    data_store.suite["accounts"] = ACCOUNTS
    data_store.suite["routers"] = ROUTERS


@after_suite
def quit_driver():
    driver = data_store.suite.get("driver")
    driver.close()
    # 兜底关用户 context
    user_ctx = data_store.suite.get("user_context")
    if user_ctx:
        user_ctx.close()


if __name__ == '__main__':
    init_test_env()
    print(data_store.suite.get("page"))
    input("12313123")
    quit_driver()