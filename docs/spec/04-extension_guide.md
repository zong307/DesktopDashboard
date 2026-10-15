# DesktopDashboard 扩展开发指南

## 概述

DesktopDashboard 采用**插件化内容块**架构，允许开发者轻松添加新的内容类型（图片、视频、LVGL 控件等）。

## 内容块架构

### 核心概念

所有可显示内容都必须继承 `ContentBlock` 基类：

```python
class ContentBlock:
    """内容块基类"""
    
    def __init__(self, parent: QWidget):
        self.parent = parent
        self.widget: Optional[QWidget] = None
    
    def render(self) -> QWidget:
        """渲染内容。"""
        raise NotImplementedError
    
    def update(self, data: NetworkInfo) -> None:
        """更新数据。"""
        raise NotImplementedError
```

### 内容块生命周期

```
创建 → 渲染 → 显示 → 更新 → 隐藏
```

## 添加新内容块

### 步骤 1：创建内容块类

在 `src/app/` 或 `src/ext/` 中创建新类：

```python
# src/app/image_block.py
from typing import Optional
from PySide6.QtWidgets import QLabel, QWidget
from src.app.fetcher import NetworkInfo


class ImageBlock:
    """图片内容块"""
    
    def __init__(self, parent: QWidget, *, image_url: str = ""):
        self.parent = parent
        self.widget = QLabel(parent)
        self.image_url = image_url
        
    def update(self, data: NetworkInfo) -> None:
        """根据数据更新图片"""
        if self.image_url:
            # 加载图片逻辑
            pass
    
    def hide(self) -> None:
        self.widget.hide()
    
    def show_widget(self) -> None:
        self.widget.show()
```

### 步骤 2：注册内容块

在 `StickyNoteWindow._init_blocks()` 中注册：

```python
def _init_blocks(self) -> None:
    acfg = self.settings.appearance

    # 现有块
    if acfg.show_lan_ip:
        self._blocks.append(TextBlock(...))
    
    # 新增块
    if acfg.show_image:
        self._blocks.append(ImageBlock(
            self._blocks_container,
            image_url="..."
        ))

    # 添加所有块到布局
    for block in self._blocks:
        if block.show:
            self._blocks_layout.addWidget(block.widget)
```

### 步骤 3：添加配置项

在 `config/settings.yaml` 中添加：

```yaml
appearance:
  show_image: true  # 显示图片
  image_url: "..."  # 图片 URL
```

在 `src/app/config.py` 中添加对应配置类：

```python
@dataclass
class AppearanceSettings:
    show_image: bool = True
    image_url: str = ""
```

## 示例：图片内容块

### 完整实现

```python
# src/app/image_block.py
from pathlib import Path
from typing import Optional
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QWidget

from src.app.fetcher import NetworkInfo


class ImageFetchThread(QThread):
    """图片下载线程"""
    finished = Signal(QPixmap)
    
    def __init__(self, url: str):
        super().__init__()
        self.url = url
    
    def run(self):
        try:
            import urllib.request
            import ssl
            ctx = ssl.create_default_context()
            req = urllib.request.Request(self.url)
            with urllib.request.urlopen(req, timeout=5, context=ctx) as resp:
                data = resp.read()
                pixmap = QPixmap()
                pixmap.loadFromData(data)
                self.finished.emit(pixmap)
        except Exception as e:
            print(f"Image fetch error: {e}")


class ImageBlock:
    """图片内容块"""
    
    def __init__(self, parent: QWidget, *, show: bool = True):
        self.show = show
        self.parent = parent
        self.widget = QWidget(parent)
        
        # 创建图片标签
        self.image_label = QLabel(self.widget)
        self.image_label.setAlignment(__import__("PySide6.QtCore").Qt.AlignmentFlag.AlignCenter)
        self.image_label.setFixedSize(240, 120)
        self.image_label.setStyleSheet("""
            QLabel {
                background: rgba(0, 0, 0, 0.05);
                border-radius: 8px;
            }
        """)
    
    def update(self, data: NetworkInfo) -> None:
        """更新图片（可自定义逻辑）"""
        # 示例：根据 IP 生成图片
        # 或从 URL 加载
        pass
    
    def hide(self) -> None:
        if self.widget:
            self.widget.hide()
    
    def show_widget(self) -> None:
        if self.widget:
            self.widget.show()
```

## 示例：视频内容块

```python
# src/app/video_block.py
from PySide6.QtMultimedia import QMediaPlayer, QVideoWidget
from PySide6.QtWidgets import QWidget
from src.app.fetcher import NetworkInfo


class VideoBlock:
    """视频内容块"""
    
    def __init__(self, parent: QWidget, *, video_url: str = ""):
        self.parent = parent
        self.video_url = video_url
        
        # 创建视频播放器
        self.player = QMediaPlayer()
        self.video_widget = QVideoWidget(parent)
        self.player.setVideoOutput(self.video_widget)
        
    def update(self, data: NetworkInfo) -> None:
        """更新视频源"""
        if self.video_url:
            self.player.setSource(QUrl(self.video_url))
            self.player.play()
    
    def hide(self) -> None:
        self.player.stop()
        self.video_widget.hide()
    
    def show_widget(self) -> None:
        self.video_widget.show()
```

## 示例：LVGL 控件

```python
# src/app/lvgl_block.py
from typing import Optional
from PySide6.QtWidgets import QWidget
from src.app.fetcher import NetworkInfo


class LVGLBlock:
    """LVGL 控件块"""
    
    def __init__(self, parent: QWidget, *, lvgl_id: str = ""):
        self.parent = parent
        self.lvgl_id = lvgl_id
        self.widget = None  # LVGL 窗口
        
    def update(self, data: NetworkInfo) -> None:
        """更新 LVGL 控件数据"""
        # 与 LVGL 引擎交互
        pass
    
    def hide(self) -> None:
        if self.widget:
            self.widget.hide()
    
    def show_widget(self) -> None:
        if self.widget:
            self.widget.show()
```

## 数据传递

### NetworkInfo 数据

所有内容块通过 `NetworkInfo` 接收数据：

```python
@dataclass
class NetworkInfo:
    lan_ip: str = ""
    public_ip: str = ""
    hostname: str = ""
    error: str = ""
```

### 扩展数据

如需传递更多数据，扩展 `NetworkInfo`：

```python
@dataclass
class NetworkInfo:
    lan_ip: str = ""
    public_ip: str = ""
    hostname: str = ""
    error: str = ""
    
    # 新增字段
    weather: str = ""
    battery: float = 0.0
```

## 异步操作

### 网络请求

使用 `QThread` 避免阻塞 UI：

```python
class DataFetchThread(QThread):
    finished = Signal(Data)
    
    def run(self):
        data = self._fetch_data()
        self.finished.emit(data)
```

### 文件操作

```python
import asyncio
from PySide6.QtCore import QThread

class FileOperationThread(QThread):
    def run(self):
        # 文件操作
        self._process_file()
```

## 样式定制

### 自定义样式表

在内容块中设置 QSS：

```python
class CustomBlock:
    def __init__(self, parent):
        self.widget = QWidget(parent)
        self.widget.setStyleSheet("""
            QWidget {
                background: rgba(0, 122, 255, 0.1);
                border-radius: 8px;
            }
            QLabel {
                color: #007AFF;
                font-size: 14px;
            }
        """)
```

### 主题支持

读取主题配置：

```python
theme = settings.appearance.theme
if theme == "dark":
    bg_color = "rgba(30, 30, 34, 0.85)"
else:
    bg_color = "rgba(255, 255, 255, 0.85)"
```

## 测试内容块

### 单元测试

```python
# tests/test_image_block.py
import pytest
from src.app.image_block import ImageBlock


def test_image_block_creation():
    block = ImageBlock(None)
    assert block.widget is not None


def test_image_block_update():
    block = ImageBlock(None)
    data = NetworkInfo(lan_ip="192.168.1.1")
    block.update(data)  # 不应抛出异常
```

### 集成测试

```python
def test_image_block_in_widget(qtbot):
    window = StickyNoteWindow(load_settings())
    window._blocks.append(ImageBlock(...))
    # 验证窗口正常创建
```

## 最佳实践

### 1. 保持内容块轻量

- 只做必要的数据渲染
- 避免复杂逻辑
- 使用异步操作

### 2. 错误处理

```python
def update(self, data: NetworkInfo):
    try:
        # 渲染逻辑
        pass
    except Exception as e:
        print(f"Block update error: {e}")
        # 显示错误状态
```

### 3. 内存管理

```python
def hide(self):
    # 清理资源
    self.player.stop()
    self.timer.stop()
```

### 4. 主题适配

```python
def _get_theme_color(self, light: str, dark: str) -> str:
    theme = self.settings.appearance.theme
    return light if theme == "light" else dark
```

## 发布新内容块

### 1. 文档

编写内容块文档：

```markdown
## 图片内容块 (ImageBlock)

支持显示网络图片。

### 配置
```yaml
appearance:
  show_image: true
  image_url: "https://example.com/image.jpg"
```

### 示例
```python
from src.app.image_block import ImageBlock

block = ImageBlock(parent)
```
```

### 2. 测试

确保测试覆盖：
- 创建测试
- 更新测试
- 错误处理测试

### 3. 提交

遵循 [Development Conventions](02-development_conventions.md)：

```
feat(blocks): 添加图片内容块支持

- 实现 ImageBlock 类
- 支持网络图片加载
- 添加异步下载线程

Closes #23
```

## 常见问题

### Q: 内容块不显示？

A: 检查：
1. `show` 属性是否为 True
2. 是否正确添加到布局
3. 是否调用 `show_widget()`

### Q: 数据更新不生效？

A: 检查：
1. `update()` 方法是否正确实现
2. 信号连接是否正确
3. 数据是否传递正确

### Q: 主题切换后样式不对？

A: 检查：
1. 是否读取主题配置
2. 是否使用主题色
3. 样式表是否正确应用

## 更多资源

- [Technical Architecture](01-technical_architecture.md) - 系统架构详情
- [API Reference](03-api_reference.md) - 完整 API 文档
- [Development Conventions](02-development_conventions.md) - 代码规范
