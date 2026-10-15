# API 参考

## 模块索引

| 模块 | 说明 |
|------|------|
| config | 配置管理 |
| fetcher | 网络信息获取 |
| style | 样式管理 |
| widget | 窗口核心 |

## config 模块

### load_settings(path=None) -> Settings

加载配置。

**参数：**
- path (Optional[Path]): 配置文件路径

**返回：**
- Settings: 配置对象

**示例：**
```python
from src.app.config import load_settings

settings = load_settings()
print(settings.display.width)  # 280
```

### class Settings

配置数据类。

**属性：**
| 属性 | 类型 | 说明 |
|------|------|------|
| display | DisplaySettings | 显示配置 |
| refresh | RefreshSettings | 刷新配置 |
| appearance | AppearanceSettings | 外观配置 |
| window | WindowSettings | 窗口行为配置 |

### class DisplaySettings

显示配置。

**属性：**
| 属性 | 类型 | 默认值 |
|------|------|--------|
| width | int | 280 |
| height | int | 180 |
| opacity | float | 0.85 |
| corner_radius | int | 16 |
| padding | int | 20 |

### class RefreshSettings

刷新配置。

**属性：**
| 属性 | 类型 | 默认值 |
|------|------|--------|
| interval_seconds | int | 60 |
| public_ip_url | str | "https://api.ipify.org" |

### class AppearanceSettings

外观配置。

**属性：**
| 属性 | 类型 | 默认值 |
|------|------|--------|
| theme | str | "light" |
| show_lan_ip | bool | True |
| show_public_ip | bool | True |

## fetcher 模块

### get_lan_ip() -> str

获取局域网 IP。

**返回：**
- str: 局域网 IP 地址

**示例：**
```python
from src.app.fetcher import get_lan_ip

ip = get_lan_ip()
print(ip)  # "192.168.1.100"
```

### get_public_ip(url) -> str

获取公网 IP。

**参数：**
- url (str): API 地址

**返回：**
- str: 公网 IP 地址

**示例：**
```python
ip = get_public_ip("https://api.ipify.org")
```

### class FetchThread(QThread)

后台网络请求线程。

**信号：**
| 信号 | 参数 | 说明 |
|------|------|------|
| finished | NetworkInfo | 数据获取完成 |

**属性：**
| 属性 | 类型 | 说明 |
|------|------|------|
| public_ip_url | str | 公网 IP API |

**示例：**
```python
thread = FetchThread("https://api.ipify.org")
thread.finished.connect(on_data)
thread.start()
```

### class NetworkInfo

网络数据容器。

**属性：**
| 属性 | 类型 | 默认值 |
|------|------|--------|
| lan_ip | str | "" |
| public_ip | str | "" |
| hostname | str | "" |
| error | str | "" |

## style 模块

### get_stylesheet(theme) -> str

获取 QSS 样式表。

**参数：**
- theme (str): 主题名称 ("light" 或 "dark")

**返回：**
- str: QSS 样式表字符串

**示例：**
```python
from src.app.style import get_stylesheet

qss = get_stylesheet("light")
widget.setStyleSheet(qss)
```

## widget 模块

### class StickyNoteWindow(QMainWindow)

主窗口类。

**构造：**
```python
window = StickyNoteWindow(settings)
```

**参数：**
- settings (Settings): 配置对象

**属性：**
| 属性 | 类型 | 说明 |
|------|------|------|
| settings | Settings | 配置对象 |
| _blocks | list[ContentBlock] | 内容块列表 |

**方法：**

#### set_window_mode(mode) -> None

设置显示模式。

**参数：**
- mode (str): "topmost" 或 "normal"

**示例：**
```python
window.set_window_mode("topmost")
```

#### set_locked(locked) -> None

设置锁定状态。

**参数：**
- locked (bool): True=锁定，False=解锁

**示例：**
```python
window.set_locked(True)
```

#### _copy_ip(block) -> None

复制 IP 到剪贴板。

**参数：**
- block (TextBlock): 内容块

**示例：**
```python
window._copy_ip(block)
```

### class TextBlock(ContentBlock)

文本内容块。

**构造：**
```python
block = TextBlock(parent, title="LAN IP", data_key="lan_ip")
```

**参数：**
- parent (QWidget): 父组件
- title (str): 标签文本
- data_key (str): 数据字段名
- show (bool): 是否显示
- is_value (bool): 是否为值类型

**方法：**

#### update(data) -> None

更新显示数据。

**参数：**
- data (NetworkInfo): 网络数据

#### set_copy_visible(visible) -> None

设置复制按钮可见性。

**参数：**
- visible (bool): 是否可见

### class ToastLabel(QLabel)

Toast 提示标签。

**构造：**
```python
toast = ToastLabel(parent)
```

**方法：**

#### show_message(message) -> None

显示提示消息。

**参数：**
- message (str): 提示文本

**示例：**
```python
toast.show_message("已复制")
# 2 秒后自动消失
```

### class ContentBlock

内容块基类。

**方法：**

#### render() -> QWidget

渲染内容。

**返回：**
- QWidget: 顶层组件

#### update(data: NetworkInfo) -> None

更新数据。

**参数：**
- data (NetworkInfo): 网络数据

#### hide() -> None

隐藏内容。

#### show_widget() -> None

显示内容。