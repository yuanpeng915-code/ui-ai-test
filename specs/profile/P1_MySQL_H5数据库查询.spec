# MySQL H5运维数据库查询验证
tags: p1, mysql, h5, profile

## P1-MySQL_H5_数据库查询
* 启动用户浏览器"TEST_USER1"密码"1qaz2wsx#EDC"
* 进入运维界面
* 选择运维界面左侧树节点"根目录"
* 填写运维界面资产搜索条件
|asset_name|
|MYSQL_129  |
* 点击运维界面资产查询
* 打开运维连接弹窗"MYSQL_129"
* 选择H5运维方式
* 发起运维连接
* 等待"3"秒
* 获取H5数据库运维页面
* 等待"3"秒
* H5数据库选择库"t1"执行查询"select txt from test;"
* H5数据库查看结果"1"验证查询结果"yes"
____
* 关闭用户浏览器
