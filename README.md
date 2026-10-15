# DesktopDashboard

跨平台桌面便签小部件，以苹果风格展示网络信息。

## 特性

- **跨平台** — 支持 Windows 10/11、macOS 10.15+、Ubuntu 20.04+
- **苹果风格 UI** — 毛玻璃效果、简洁排版、圆角阴影
- **实时 IP 显示** — 自动获取并刷新局域网 IP 与公网 IP
- **右键交互** — 置顶模式、窗口固定、一键复制
- **系统托盘** — 托盘图标快捷管理
- **插件化架构** — 未来可扩展图片、视频、LVGL 等内容块

## 快速开始

### 环境准备

```powershell
# 创建 conda 环境
conda create -n py312 python=3.12 -y
conda activate py312

# 安装依赖
pip install PySide6 PyYAML requests
```

### 运行程序

```powershell
conda activate py312
python src/main.py
```

### 构建可执行文件

```powershell
# Windows
scripts\build.bat

# macOS / Linux
chmod +x scripts/build.sh
./scripts/build.sh
```

构建产物位于 `dist/` 目录。

## 配置

编辑 `config/settings.yaml`：

```yaml
display:
  width: 280
  height: 180
  opacity: 0.85
  corner_radius: 16
  padding: 20

appearance:
  theme: light
  show_lan_ip: true
  show_public_ip: true

refresh:
  interval_seconds: 60
```

## 交互操作

| 操作 | 说明 |
|------|------|
| 拖拽移动 | 左键按住拖动（未固定状态） |
| 右键菜单 | 置顶/固定/刷新/退出 |
| 复制 IP | 固定后鼠标悬停显示复制按钮 |
| 系统托盘 | 右键托盘图标可退出 |
| 退出 | 右键菜单 → 退出，或终端 Ctrl+C |

## 文档索引

### 用户文档

- [使用说明](docs/01-user_guidance.md) — 安装、运行、配置、交互说明
- [UI 设计规范](docs/02-ui_design.md) — 色彩、字体、间距、动效规范

### 开发者文档

- [技术架构](docs/spec/01-technical_architecture.md) — 分层架构、模块设计、数据流
- [开发规范](docs/spec/02-development_conventions.md) — 代码风格、Git 工作流、测试
- [API 参考](docs/spec/03-api_reference.md) — 模块 API 文档
- [扩展指南](docs/spec/04-extension_guide.md) — 插件化内容块开发指南
