# 郝志强主页 Pages CMS 试验

本仓库用于验证在线编辑新闻、成员、论文、图片、附件和短视频。沿用现有 v16 版式，不是第二版设计成品。

- 管理入口：https://app.pagescms.org/
- 所有者先使用 GitHub 登录，安装 Pages CMS GitHub App，并仅授权本试验仓库。
- 需要时，通过 Pages CMS 邮箱邀请交付人为协作者；协作者无需学习 Git。
- GitHub 仓库 Settings → Pages → Source 选择 GitHub Actions。
- 保存内容会产生提交；Actions 验证成功并完成部署后，网站才更新，保存不等于立即上线。

## 表单与发布约定

在中文栏目中填写资料。新增记录先取消“在网站显示”可保存未发布内容；确认后勾选再保存。排列序号越小越靠前，新闻支持置顶。同序号按新闻日期倒序。

未发布内容不输出到公开网页，但本仓库若为公开仓库，原始 JSON 仍公开，不应填写保密内容。

图片使用 JPG、PNG、WebP，生成页面时会优化尺寸；资料支持 PDF、Word、PPT、Excel 和 ZIP；视频支持 MP4、WebM 或视频播放链接。试验约定：图片/附件单文件不超过10 MB，视频单文件不超过20 MB，超过时构建失败，已上线的版本保持原状。CMS 上传速度和实际可传大小仍需授权后实测。长视频建议使用外部播放地址。

视频不自动播放、不预先下载视频文件。图片延后加载。列表默认每页10条，可选择20或50条。每次翻页只创建当前页的条目，不会同时摆出全部图片和播放器。

## 文件结构

- `.pages.yml`：Pages CMS 中文表单配置。
- `data/profile.json`：简介和网站设置。
- `content/`：一条记录一个 JSON 文件，避免每次修改整份大资料。
- `media/`：上传的图片、资料、视频。
- `templates/v16.html`：现有设计模板。
- `scripts/build.py`：生成完整静态页面；未来第二版可复用同一套 content/data。
- `.github/workflows/pages.yml`：验证、构建和发布。

## 本地验证

安装 Python 3.12，然后执行：

```
pip install -r requirements.txt
python scripts/test_build.py
python scripts/build.py
```

输出在 `_site/index.html`，可直接双击检查。配置中使用相对路径，仓库更名或迁移时不需要在每条资料中改网址。

## 当前验收边界

本地生成、展示与测试不能代替 Pages CMS 真实登录、上传和线上发布验收。首次授权和 Pages 开通仍需仓库所有者完成。不得宣称在任何网络和设备下都绝不卡顿；应记录真实网络、文件大小、加载和操作耗时。

当前只生成现有版式这一版；第二版尚未制作，数据结构已可共用。管理员入口不放在访客页面上。
