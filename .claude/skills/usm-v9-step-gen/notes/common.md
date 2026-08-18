## 堡垒机（明御运维安全管理系统 / USM V9）框架事实

- **前端框架是 Ant Design Vue(`.ant-*` 类名)**,不是 Element-Plus。表单用 `.ant-form-item`、抽屉 `.ant-drawer-content`、单选 `.ant-radio-wrapper`、勾选 `.ant-checkbox-wrapper`、下拉 `.ant-select`。弹窗遮罩 `.ant-drawer-mask` / `.ant-modal` 会拦截点击。
- 全站路由表见 `data/router.json`,按页面名跳转(`goto_route`),别点侧边栏折叠菜单。
- `#username` 在列表页搜索框和新建表单里**各有一个**,操作表单必须限定在 `.ant-drawer-content` 作用域,否则 strict 模式报 2 elements。