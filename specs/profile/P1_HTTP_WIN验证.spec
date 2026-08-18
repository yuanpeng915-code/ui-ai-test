# HTTP_WIN_137 Ping连通性验证
tags: p1, http, win, profile

## P1-HTTP_WIN_137_Ping验证
* 清除Ping服务时间戳
* 启动用户浏览器"TEST_USER1"密码"1qaz2wsx#EDC"
* 进入运维界面
* 选择运维界面左侧树节点"根目录"
* 填写运维界面资产搜索条件
|asset_name    |
|HTTP_WIN_137  |
* 点击运维界面资产查询
* 打开运维连接弹窗"HTTP_WIN_137"
* 选择H5运维方式
* 发起运维连接
* 等待"3"秒
* 获取H5运维页面
* 验证Ping服务已被调用
____
* 关闭用户浏览器
