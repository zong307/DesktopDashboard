# DesktopDashboard 使用说明

## 安装

### 环境要求
- Python 3.10+
- Windows 10/11、macOS 10.15+、Ubuntu 20.04+

### 使用 Conda（推荐）

```powershell
# 创建环境
conda create -n py312 python=3.12 -y

# 激活环境
conda activate py312

# 安装依赖
pip install PySide6 PySide6-Addons
```

### 使用 venv

```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

pip install -r requirements.txt
```

## 运行程序

### 开发模式

```powershell
conda activate py312
cd DesktopDashboard
python src/main.py
```

### 打包模式

```powershell
# 运行构建脚本
scripts\build.bat

# 启动程序
dist\DesktopDashboard\DesktopDashboard.exe
```

## 配置

编辑 `config/settings.yaml`：

```yaml
display:
  width: 280            # 窗口宽度
  height: 180           # 窗口高度
  opacity: 0.85         # 透明度 0.0~1.0
  corner_radius: 16     # 圆角半径
  padding: 20           # 内边距
  font_size: 13         # 字体大小
  font_weight: 500      # 字体粗细

appearance:
  theme: "light"        # light / dark
  show_lan_ip: true     # 显示局域网 IP
  show_public_ip: true  # 显示公网 IP
  show_hostname: false  # 显示主机名
  show_timestamp: true  # 显示时间戳

refresh:
  interval_seconds: 60  # 刷新间隔
  public_ip_url: "https://api.ipify.org"  # 公网 IP API
```

## 交互操作

### 窗口操作
- **拖拽移动** — 左键按住拖动（解锁状态）
- **右键菜单** — 打开操作菜单

### 右键菜单
| 选项 | 说明 |
|------|------|
| 刷新 IP | 立即刷新网络信息 |
| 显示方式 → 置顶 | 窗口始终在最前 |
| 显示方式 → 不置顶 | 窗口可被遮挡 |
| 固定 | 锁定位置，显示复制按钮 |
| 退出 | 关闭程序 |

### 固定模式
- 窗口位置锁定
- 鼠标悬停时显示 IP 复制按钮
- 点击复制按钮 → 复制到剪贴板
- 显示"已复制"提示（2 秒后消失）

### 退出程序
1. 右键菜单 → 退出
2. 键盘 `Ctrl + C`
3. 终端中 `Ctrl + C`
4. 系统托盘右键 → 退出

## 系统托盘

程序启动后在系统托盘显示图标：
- **左键单击** — 显示/隐藏窗口
- **右键菜单** — 显示/退出
