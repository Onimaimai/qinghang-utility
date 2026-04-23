import httpx
from typing import Optional, List, Dict


PUSHPLUS_URL = "http://www.pushplus.plus/send"


def send_balance_alert(token: str, alerts: List[Dict]) -> bool:
    """
    发送余额不足提醒（支持水电费）

    Args:
        token: PushPlus Token
        alerts: 提醒列表，每个元素包含:
            - type: 费用类型（电费/水费）
            - balance: 当前余额
            - threshold: 设定的阈值

    Returns:
        是否发送成功
    """
    if not token or not alerts:
        return False

    # 构建 HTML 内容
    content = """
    <h2>水电费余额不足提醒</h2>
    <p>您的以下费用余额已低于设定阈值，请及时充值。</p>
    <table style="border-collapse: collapse; margin: 20px 0;">
        <tr style="background: #f8fafc;">
            <th style="padding: 12px; border: 1px solid #ddd;">类型</th>
            <th style="padding: 12px; border: 1px solid #ddd;">当前余额</th>
            <th style="padding: 12px; border: 1px solid #ddd;">提醒阈值</th>
        </tr>
    """

    for alert in alerts:
        content += f"""
        <tr>
            <td style="padding: 10px; border: 1px solid #ddd;">{alert['type']}</td>
            <td style="padding: 10px; border: 1px solid #ddd; color: red; font-weight: bold;">
                {alert['balance']:.2f} 元
            </td>
            <td style="padding: 10px; border: 1px solid #ddd;">{alert['threshold']:.2f} 元</td>
        </tr>
        """

    content += """
    </table>
    <p>请登录公寓管理系统及时充值，以免影响正常使用。</p>
    """

    try:
        response = httpx.post(
            PUSHPLUS_URL,
            json={
                "token": token,
                "title": "水电费余额不足提醒",
                "content": content,
                "template": "html"
            },
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            return result.get("code") == 200
        return False
    except Exception as e:
        print(f"发送PushPlus通知失败: {e}")
        return False


def send_test_message(token: str) -> bool:
    """
    发送测试消息

    Args:
        token: PushPlus Token

    Returns:
        是否发送成功
    """
    if not token:
        return False

    try:
        response = httpx.post(
            PUSHPLUS_URL,
            json={
                "token": token,
                "title": "水电费查询面板 - 测试消息",
                "content": "这是一条测试消息，如果您收到此消息，说明PushPlus配置正确。",
                "template": "html"
            },
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            return result.get("code") == 200
        return False
    except Exception as e:
        print(f"发送测试消息失败: {e}")
        return False
