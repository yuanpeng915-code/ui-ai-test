"""
标题:堡垒机登录
路由:/index/#/index/index/login
功能:在明御运维安全管理系统登录页输入账号密码完成登录,进入个人工作台。
      其它需要登录态的功能调用前,先执行本功能。
"""
from getgauge.python import step, data_store


@step("登录堡垒机账号<username>密码<password>")
def login_bastion(username, password):
    """
    name:堡垒机登录
    description:在登录页输入账号密码并登录,进入运维系统需先调用。用户未给凭据时,可参考 assets.json 的 bastion_admin
    params:
        - username:文本输入|无|任意文本
        - password:文本输入|无|任意文本
    """
    page = data_store.suite["page"]
    page.locator("#username").fill(username)
    page.locator("#password").fill(password)
    page.get_by_role("button").filter(has_text="登").first.click()

    page.wait_for_url("**/workbench**", timeout=15000)
    assert "/login" not in page.url
    assert "workbench" in page.url
    return page.url
