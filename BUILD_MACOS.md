# macOS App 构建指南

## 快速开始（3步）

### 方案 1: 使用自动化脚本（推荐）

```bash
# 1. 下载项目
git clone https://github.com/G-NO1/My-Work.git
cd My-Work

# 2. 运行构建脚本
chmod +x build_mac.sh
./build_mac.sh

# 3. 启动应用
open dist/EMall计划维护助手.app
```

### 方案 2: 手动构建

```bash
# 1. 安装依赖
python3 -m pip install -r requirements.txt

# 2. 构建应用
python3 -m PyInstaller \
  --onefile \
  --windowed \
  --name "EMall计划维护助手" \
  --osx-bundle-identifier com.emalplus.plan-maintenance \
  updateGUI.py

# 3. 运行应用
open dist/EMall计划维护助手.app
```

## 系统要求

- macOS 10.13 或更高版本
- Python 3.8 或更高版本
- 约 200MB 磁盘空间

## 故障排除

### 问题 1: "无法打开此应用"

```bash
# 解决方案：移除隔离属性
xattr -rd com.apple.quarantine /Applications/EMall计划维护助手.app
```

### 问题 2: 权限被拒绝

```bash
# 解决方案：赋予执行权限
chmod +x dist/EMall计划维护助手.app/Contents/MacOS/EMall计划维护助手
```

### 问题 3: 找不到 Python

确保已安装 Python 3.8+：
```bash
python3 --version
```

## 分发应用

### 创建 DMG 安装程序

```bash
# 安装 create-dmg 工具
brew install create-dmg

# 创建 DMG
create-dmg \
  --volname "EMall计划维护助手" \
  --window-pos 200 120 \
  --window-size 800 400 \
  --icon-size 100 \
  --texticonwindowbackground \
  --background background.png \
  --icon "EMall计划维护助手.app" 100 100 \
  "EMall计划维护助手.dmg" \
  dist/EMall计划维护助手.app
```

## 高级配置

### 自定义应用图标

1. 准备 1024x1024px 的 PNG 图片
2. 转换为 ICNS 格式：
```bash
# 使用在线工具或 ImageMagick
convert icon.png -define icon:auto-resize=256,128,96,64,48,32,16 icon.icns
```

3. 更新构建命令：
```bash
python3 -m PyInstaller \
  --onefile \
  --windowed \
  --icon=icon.icns \
  --name "EMall计划维护助手" \
  updateGUI.py
```

## 版本更新

构建新版本时：
```bash
rm -rf build dist *.spec
./build_mac.sh
```

---
最后更新：2026-03-04