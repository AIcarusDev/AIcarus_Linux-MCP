import pyautogui  # type: ignore
from typing import Tuple


# 简单的日志记录
def log(message: str):
    print(f"[Action] {message}")


def click_tool(loc: Tuple[int, int]):
    """在指定坐标执行鼠标左键单击。"""
    if not isinstance(loc, (list, tuple)) or len(loc) != 2:
        raise ValueError("loc 必须是一个包含两个整数的元组或列表")
    x, y = loc
    log(f"Clicking at ({x}, {y})")
    pyautogui.click(x=x, y=y)
    return {"status": "success", "message": f"Clicked at ({x}, {y})"}


def type_tool(loc: Tuple[int, int], text: str):
    """先点击指定坐标以聚焦，然后输入文本。"""
    if not isinstance(loc, (list, tuple)) or len(loc) != 2:
        raise ValueError("loc 必须是一个包含两个整数的元组或列表")
    if not isinstance(text, str):
        raise ValueError("text 必须是字符串")
    x, y = loc
    log(f"Typing at ({x}, {y}): '{text[:50]}...'")
    pyautogui.click(x=x, y=y)
    pyautogui.typewrite(text, interval=0.01)  # 加入微小延迟以提高稳定性
    return {"status": "success", "message": f"Typed text at ({x}, {y})"}


def key_tool(key: str):
    """按下指定的单个按键。"""
    if not isinstance(key, str):
        raise ValueError("key 必须是字符串")
    log(f"Pressing key: {key}")
    pyautogui.press(key)
    return {"status": "success", "message": f"Pressed key: {key}"}


# 可以在这里添加 scroll_tool, shortcut_tool 等其他动作
