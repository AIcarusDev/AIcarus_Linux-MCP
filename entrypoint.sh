#!/bin/bash

# 1. 启动 Xvfb 虚拟显示器
#    -screen 0 1280x800x24: 创建一个 1280x800 分辨率、24位色深的屏幕
#    在后台运行 (&)
echo "Starting Xvfb..."
Xvfb :0 -screen 0 1280x800x24 &

# 2. 在虚拟显示器上启动窗口管理器 (Fluxbox)
#    DISPLAY=:0 指定了使用哪个显示器
#    在后台运行 (&)
echo "Starting Fluxbox Window Manager..."
DISPLAY=:0 fluxbox &

# 3. 启动 VNC 服务器，以便我们可以远程查看和调试
#    -display :0: 连接到 Xvfb 创建的显示器
#    -forever: 保持运行
#    -usepw: 使用密码（我们将不会设置密码，方便调试）
#    在后台运行 (&)
echo "Starting VNC Server on port 5900..."
x11vnc -display :0 -forever -nopw &

# 4. 确保 AT-SPI D-Bus 服务是可访问的
#    这是让 atspi 库工作的关键
export DISPLAY=:0
export DBUS_SESSION_BUS_ADDRESS=$(eval `dbus-launch --sh-syntax`)
/usr/lib/at-spi2-core/at-spi-bus-launcher --launch-immediately &

# 等待几秒钟，确保桌面环境完全启动
sleep 5

# 5. 启动我们的核心 Agent 程序
#    这将是前台进程，以保持容器持续运行
echo "Starting Linux-MCP Agent..."
python3 main.py