import base64
import io
import time
from typing import Any, Dict, List

import atspi
import pyautogui
from gi.repository.Atspi import Accessible

# 简单的日志记录
def log(message: str):
    print(f"[Perception] {message}")

def traverse_desktop(node: Accessible, level: int = 0) -> List[Dict[str, Any]]:
    """递归遍历 AT-SPI 树，收集所有可交互的 UI 元素。"""
    elements = []
    try:
        # 过滤掉不可见或不可用的元素
        state_set = node.get_state_set()
        if not state_set.contains(atspi.STATE_VISIBLE) or not state_set.contains(atspi.STATE_ENABLED):
            return []

        role_name = node.get_role_name()
        name = node.get_name()

        # 过滤掉一些通常无用的容器或布局元素
        ignored_roles = {'filler', 'panel', 'scroll pane', 'viewport', 'tool bar', 'menu bar', 'frame'}
        if role_name in ignored_roles:
            pass # 仍然遍历其子节点
        else:
            # 获取元素的精确屏幕坐标和大小
            extents = node.get_extents(atspi.CoordType.SCREEN)
            if extents.width > 0 and extents.height > 0:
                # 计算中心点坐标
                center_x = extents.x + extents.width // 2
                center_y = extents.y + extents.height // 2

                element_info = {
                    "name": name or "Unnamed",
                    "type": role_name,
                    "coords": (center_x, center_y),
                    "size": (extents.width, extents.height),
                    "full_coords": (extents.x, extents.y, extents.width, extents.height)
                }
                elements.append(element_info)

        # 递归遍历子节点
        for i in range(node.get_child_count()):
            child = node.get_child_at_index(i)
            elements.extend(traverse_desktop(child, level + 1))

    except Exception as e:
        # AT-SPI 可能会对某些元素抛出异常，忽略它们
        # log(f"Error traversing node: {e}")
        pass

    return elements

def get_ui_state() -> Dict[str, Any]:
    """
    核心感知函数。获取当前桌面的完整状态，包括UI元素和屏幕截图。
    """
    log("Capturing UI state...")
    start_time = time.time()

    try:
        # 从桌面根节点开始遍历
        desktop = atspi.get_desktop(0)
        all_elements = traverse_desktop(desktop)

        # 对元素进行分类
        interactive_elements = []
        informative_elements = []

        interactive_roles = {'push button', 'check box', 'radio button', 'link', 'text', 'entry', 'password text'}

        label_counter = 0
        for el in all_elements:
            # 过滤掉没有名字且类型不重要的元素
            if el['name'] == 'Unnamed' and el['type'] not in interactive_roles:
                continue

            if el['type'] in interactive_roles:
                el['label'] = label_counter
                interactive_elements.append(el)
                label_counter += 1
            else:
                informative_elements.append(el)

        # 获取屏幕截图
        screenshot = pyautogui.screenshot()
        buffer = io.BytesIO()
        screenshot.save(buffer, format="PNG")
        screenshot_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

        end_time = time.time()
        log(f"UI state captured in {end_time - start_time:.2f} seconds. Found {len(interactive_elements)} interactive elements.")

        return {
            "focused_app_name": "Unknown", # AT-SPI 获取焦点应用较复杂，暂留
            "open_apps": [], # 同上
            "interactive_elements": interactive_elements,
            "informative_elements": informative_elements,
            "scrollable_elements": [], # 暂不实现
            "screenshot_b64": screenshot_b64
        }
    except Exception as e:
        log(f"FATAL: Failed to get UI state: {e}")
        return {"error": str(e)}