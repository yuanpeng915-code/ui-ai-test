"""
标题:公共步骤
功能:跨模块使用的通用 Gauge step。包括用户端浏览器管理。
      step1 启动用户浏览器<username>密码<password>  【必须】懒创建 user context + 登录指定用户
      step2 关闭用户浏览器                       【必须】清理用户端 session
注意: 用户端通过 driver.new_user_context() 共享同一 browser 的不同 context，首次调用时懒创建。
"""
from getgauge.python import step, data_store
from utils.page_helper import PageHelper
from utils.data_loader import ACCOUNTS


def _ensure_user_browser():
    """懒创建用户端 browser context，已存在则跳过。"""
    if "user_page" in data_store.suite:
        return
    driver = data_store.suite["driver"]
    user_ctx, user_page = driver.new_user_context()
    data_store.suite["user_context"] = user_ctx
    data_store.suite["user_page"] = user_page
    data_store.suite["user_page_helper"] = PageHelper(user_page)


@step("启动用户浏览器<username>密码<password>")
def start_user_browser(username, password):
    """
    name:启动用户浏览器
    description:懒创建用户端 browser context（首次）并以指定用户登录，进入工作台
    params:
        - username:文本输入|无|测试用户名(如 yptest)
        - password:文本输入|无|该用户密码
    """
    _ensure_user_browser()
    page = data_store.suite["user_page"]
    account = ACCOUNTS["bastion_admin"]
    page.goto(account["url"], wait_until="domcontentloaded")
    page.wait_for_timeout(2000)

    page.locator("#username").fill(username)
    page.locator("#password").fill(password)
    page.get_by_role("button").filter(has_text="登").first.click()
    page.wait_for_timeout(3000)
    assert "/login" not in page.url, f"用户 {username} 登录失败"
    assert "workbench" in page.url, f"用户 {username} 登录后未进入工作台"

    # ponytail: 首次登录可能有"修改本地密码"弹窗，Escape 关掉
    page.keyboard.press("Escape")
    page.wait_for_timeout(500)


@step("关闭用户浏览器")
def stop_user_browser():
    """
    name:关闭用户浏览器
    description:关闭用户端 browser context，释放会话
    params: 无
    """
    for k in ["user_page", "user_page_helper"]:
        data_store.suite.pop(k, None)
    user_ctx = data_store.suite.pop("user_context", None)
    if user_ctx:
        user_ctx.close()
