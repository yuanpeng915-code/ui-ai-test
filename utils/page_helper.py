"""页面操作助手:统一管理 Playwright page 上下文 + Ant Design Vue 表单操作。

所有 acceptance/step_impl 方法通过 PageHelper 共享同一个 page 实例:
- Gauge 模式: step_impl/hooks.py before_suite 注入
- 单文件调试: __main__ 里 page_helper = PageHelper(page)
"""
from playwright.sync_api import Page

from utils.data_loader import ROUTERS


class PageHelper:
    """页面操作助手 — 类级单例,所有方法共享 _page。"""

    def __init__(self, page: Page):
        self._page = page

    # ---- page 生命周期 ----
    def set_page(self, page):
        # 保留page切换入口
        self._page = page

    # ---- goto route ----
    def goto_route(self, page_name):
        """按页面名(data_loader.ROUTERS 里的 name,支持子串匹配)跳转。SPA hash 路由,直接改 URL 最稳。"""
        hit = next((r for r in ROUTERS if page_name in r["name"]), None)
        assert hit, f"router.json 里找不到页面 '{page_name}'"
        base = self._page.url.split("/index/")[0]
        self._page.goto(base + hit["path"], wait_until="domcontentloaded")
        self._page.wait_for_timeout(1500)  # 等 SPA 渲染
        return hit["path"]

    # ---- Ant Design Vue 表单助手 ----
    def drawer(self):
        """定位当前抽屉作用域,避开列表页同名控件(如 #username 重复)。"""
        return self._page.locator(".ant-drawer-content").last


    def antd_select(self, item_label, value):
        """按 form-item 标签定位 antd 下拉,展开并选中 value。value 为空则保留默认。"""
        if not value:
            return
        page = self._page
        item = self.drawer().locator(".ant-form-item").filter(has_text=item_label).first
        item.locator(".ant-select").first.click()
        page.wait_for_timeout(500)
        page.locator(".ant-select-dropdown:not(.ant-select-dropdown-hidden) "
                     ".ant-select-item-option").filter(has_text=value).first.click()
        page.wait_for_timeout(300)

    def antd_checkbox(self, label, want):
        """把某 antd 勾选框设成 want(True勾/False不勾),已是目标态则不动。"""
        cb = self.drawer().locator(".ant-checkbox-wrapper").filter(has_text=label).first
        checked = "ant-checkbox-checked" in (cb.locator(".ant-checkbox").first.get_attribute("class") or "")
        if checked != want:
            cb.click()

    def antd_radio(self, item_label, option):
        """按 form-item 标签定位 antd 单选组,点选 option。option 为空则保留默认。"""
        if not option:
            return
        self.drawer().locator(".ant-form-item").filter(has_text=item_label).first \
            .locator(".ant-radio-wrapper").filter(has_text=option).first.click()

    def antd_multi_select(self, item_label, select_id, desired):
        """多选框 diff 模式:读当前已选 → 与 desired 对比 → 只增删差额。desired 为 None/空则跳过。
        item_label: form-item 标签文本(如 "认证源"); select_id: select 内层 input 的 id(如 "authSourceIds")。
        desired: set 如 {"本地认证"} 或 str 逗号分隔如 "本地认证,LDAP"。"""
        if desired is None:
            return
        if isinstance(desired, str):
            desired = set(s.strip() for s in desired.split(",") if s.strip())
        if not desired:
            return
        page = self._page
        item = self.drawer().locator(".ant-form-item").filter(has_text=item_label).first
        # 定位 form-item 内的 .ant-select (不用固定层数父级, 兼容 #select_id 不同嵌套深度)
        sel = item.locator(".ant-select").first
        # 读当前已选
        current = set()
        for j in range(sel.locator(".ant-select-selection-item").count()):
            try:
                current.add(sel.locator(".ant-select-selection-item").nth(j).inner_text().strip())
            except:
                pass
        to_add = desired - current
        to_remove = current - desired
        if not to_add and not to_remove:
            return
        sel.click()
        page.wait_for_timeout(600)
        dropdown = page.locator(".ant-select-dropdown:not(.ant-select-dropdown-hidden)").first
        for s in to_add:
            dropdown.locator(".ant-select-item-option").filter(has_text=s).first.click()
            page.wait_for_timeout(250)
        for s in to_remove:
            dropdown.locator(".ant-select-item-option").filter(has_text=s).first.click()
            page.wait_for_timeout(250)
        page.keyboard.press("Escape")
        page.wait_for_timeout(300)

    def main_select(self, select_id, value):
        """主页面(非抽屉)操作 antd select: 点父级 .ant-select → 下拉选值。value 为空则跳过。"""
        if not value:
            return
        page = self._page
        sel = page.locator(f"#{select_id}").locator("..").locator("..")
        sel.click()
        page.wait_for_timeout(800)
        page.locator(".ant-select-dropdown:not(.ant-select-dropdown-hidden) "
                     ".ant-select-item-option").filter(has_text=value).first.click()
        page.wait_for_timeout(500)


# ---- 截图工具（模块级函数，hooks.py / common.py 共用）----
def save_screenshot(page, label, screenshots_dir):
    """截取 page 当前画面，保存到 screenshots_dir，返回文件名。"""
    import os
    from uuid import uuid1

    os.makedirs(screenshots_dir, exist_ok=True)
    img = page.screenshot(full_page=False)
    fname = f"screenshot-{label}-{uuid1().int}.png"
    path = os.path.join(screenshots_dir, fname)
    with open(path, "wb") as f:
        f.write(img)
    return fname


def save_screenshots_merged(pages, label, screenshots_dir):
    """截取多个 page 并横向拼接为一张图。pages: [(label, page), ...]，page 为 None 则跳过。
    返回合并后的文件名（无 PIL 时返回最后一张的文件名），无有效截图返回 ""。
    """
    import os
    from uuid import uuid1

    os.makedirs(screenshots_dir, exist_ok=True)
    saved = []
    for pg_label, pg in pages:
        if pg is None:
            continue
        try:
            fname = save_screenshot(pg, f"{label}-{pg_label}", screenshots_dir)
            saved.append(os.path.join(screenshots_dir, fname))
        except Exception:
            pass

    if not saved:
        return ""

    # ponytail: 用 PIL 横向拼接；无 PIL 则返回最后一张
    try:
        from PIL import Image
        imgs = [Image.open(p) for p in saved]
        h = max(i.height for i in imgs)
        total_w = sum(i.width for i in imgs)
        stitched = Image.new("RGB", (total_w, h))
        x = 0
        for i in imgs:
            stitched.paste(i, (x, 0))
            x += i.width
        merged = os.path.join(screenshots_dir, f"screenshot-{label}-merged-{uuid1().int}.png")
        stitched.save(merged)
        return os.path.basename(merged)
    except ImportError:
        return os.path.basename(saved[-1])
