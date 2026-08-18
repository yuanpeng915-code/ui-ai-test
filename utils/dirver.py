from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
from utils.data_loader import CONFIG, ROOT_PATH


class ChromeDriver:

    def __init__(self, user: str = "admin", headless: bool | None = None):
        self._user = user
        self._headless = headless if headless is not None else CONFIG.get("headless", False)
        self._state_file = ROOT_PATH / "acceptance" / f"{self._user}.json"
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self.__page: Page | None = None
        self.base_url = None
        self._init()

    def _init(self) -> None:
        playwright = sync_playwright().start()
        self._browser = playwright.chromium.launch(
            headless=self._headless,
            args=CONFIG.get("args", []),
            timeout=CONFIG.get("timeout", 30000),
            slow_mo=CONFIG.get("slow_mo", 0),
        )
        self._context = self._browser.new_context(
            viewport=CONFIG.get("viewport", None),
        )
        self.__page = self._context.new_page()

    @property
    def page(self) -> Page:
        return self.__page

    @page.setter
    def page(self, p: Page) -> None:
        self.__page = p

    @property
    def browser(self) -> Browser | None:
        """底层 Browser 实例，用于遍历所有 context/pages（失败截图用）。"""
        return self._browser

    def close(self) -> None:
        self._context.close()
        self._browser.close()

    def new_user_context(self) -> tuple[BrowserContext, Page]:
        """在同一浏览器中创建独立的第二 context + page，用于双用户场景。
        返回 (context, page)，调用方自行管理生命周期。"""
        ctx = self._browser.new_context(
            viewport=CONFIG.get("viewport", None),
        )
        pg = ctx.new_page()
        return ctx, pg
