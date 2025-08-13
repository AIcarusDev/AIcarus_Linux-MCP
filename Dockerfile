# 使用一个稳定且常见的 Ubuntu 基础镜像
FROM ubuntu:22.04

# 设置环境变量，避免安装过程中的交互式提示
ENV DEBIAN_FRONTEND=noninteractive

# 更新软件包列表并安装核心依赖
# - xvfb: 虚拟显示器
# - fluxbox: 轻量级窗口管理器
# - x11vnc: VNC 服务器，用于调试时查看桌面
# - firefox: 我们的目标测试应用
# - python3-pip: Python 包管理器
# - python3-gi, gir1.2-atspi-2.0: AT-SPI 的核心系统库，至关重要
# - scrot: pyautogui 截图功能可能需要的依赖
RUN apt-get update && apt-get install -y \
    xvfb \
    fluxbox \
    x11vnc \
    firefox \
    python3.11 \
    python3-pip \
    python3-gi \
    gir1.2-atspi-2.0 \
    scrot \
    --no-install-recommends && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制 Agent 的代码和依赖文件到容器中
COPY . /app

# 安装 Python 依赖
RUN pip3 install --no-cache-dir -r requirements.txt

# 暴露 VNC 端口，方便我们从外部连接进行调试
EXPOSE 5900

# 赋予启动脚本执行权限
RUN chmod +x /app/entrypoint.sh

# 设置容器的启动命令
ENTRYPOINT ["/app/entrypoint.sh"]