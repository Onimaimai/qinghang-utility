from playwright.async_api import async_playwright, Browser, Page
import asyncio
import re
from typing import Optional, Dict, List, Any


class PMSCrawler:
    """公寓管理系统爬虫"""

    BASE_URL = "https://pmsnm.zj-xzh.com"
    LOGIN_URL = f"{BASE_URL}/login?next=prepay"
    PREPAY_URL = f"{BASE_URL}/prepay"
    DETAIL_URL = f"{BASE_URL}/daybook?type=2"
    ENERGY_URL = f"{BASE_URL}/energyRecord"
    USER_MODE_URL = f"{BASE_URL}/userMode"

    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.playwright = None

    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.page = await self.browser.new_page()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def login(self, username: str, password: str) -> bool:
        """登录公寓管理系统"""
        try:
            await self.page.goto(self.LOGIN_URL)
            await self.page.wait_for_load_state("networkidle")
            await asyncio.sleep(1)

            # 填写登录表单
            await self.page.fill('input[name="name"]', username)
            await self.page.fill('input[name="password"]', password)
            await asyncio.sleep(0.5)

            # 点击登录按钮
            await self.page.click('button:has-text("登 录")')
            await asyncio.sleep(3)

            # 检查是否登录成功
            current_url = self.page.url
            return "login" not in current_url

        except Exception as e:
            print(f"登录异常: {e}")
            return False

    async def switch_user_mode(self, mode: str = "electricity") -> bool:
        """
        切换用户模式（电费/水费）

        Args:
            mode: 'electricity' 电费模式（第一个radio）, 'water' 水费模式（第二个radio）

        Returns:
            是否切换成功
        """
        try:
            await self.page.goto(self.USER_MODE_URL, timeout=30000)
            await self.page.wait_for_load_state("networkidle", timeout=30000)
            await asyncio.sleep(1)

            # 获取所有 radio 按钮
            radios = await self.page.query_selector_all('div[role="radio"]')

            if len(radios) < 2:
                print("未找到足够的radio选项")
                return False

            if mode == "water":
                # 选择第二个 radio（水费模式）
                await radios[1].click()
                await asyncio.sleep(0.5)
            else:
                # 电费模式，选择第一个 radio
                await radios[0].click()
                await asyncio.sleep(0.5)

            # 点击保存按钮
            save_button = await self.page.query_selector('button:has-text("保存")')
            if save_button:
                await save_button.click()
                await asyncio.sleep(3)  # 等待保存完成并生效
                return True
            else:
                print("未找到保存按钮")
                return False

        except asyncio.TimeoutError:
            print(f"切换用户模式超时")
            return False
        except Exception as e:
            print(f"切换用户模式异常: {e}")
            return False

    async def get_balance(self, username: str, password: str, mode: str = "electricity") -> Optional[Dict[str, Any]]:
        """
        获取水电费余额

        Args:
            username: 公寓系统账号
            password: 公寓系统密码
            mode: 'electricity' 电费, 'water' 水费
        """
        try:
            if not await self.login(username, password):
                return None

            # 如果是水费模式，需要先切换用户模式
            if mode == "water":
                if not await self.switch_user_mode("water"):
                    print("切换到水费模式失败")
                    return None

            await self.page.goto(self.PREPAY_URL)
            await self.page.wait_for_load_state("networkidle")
            await asyncio.sleep(2)

            page_text = await self.page.inner_text('body')

            # 提取余额（注意：切换后显示文本仍是"电费"，但实际数据是水费）
            balance_match = re.search(r'水电费余额[^\d]*(\d+\.?\d*)', page_text)
            balance = float(balance_match.group(1)) if balance_match else None

            # 提取房间信息
            room_match = re.search(r'(\d+-\d+)\s*扣费', page_text)
            if not room_match:
                room_match = re.search(r'(\d+-\d+)', page_text)
            room_info = room_match.group(1) if room_match else None

            return {
                "balance": balance,
                "room_info": room_info
            }

        except Exception as e:
            print(f"获取余额异常: {e}")
            return None
        finally:
            # 如果是水费模式，爬取完成后切回电费模式
            if mode == "water":
                await self.switch_user_mode("electricity")

    async def get_details(self, username: str, password: str, mode: str = "electricity") -> Optional[List[Dict[str, Any]]]:
        """
        获取余额明细

        Args:
            username: 公寓系统账号
            password: 公寓系统密码
            mode: 'electricity' 电费, 'water' 水费
        """
        try:
            if not await self.login(username, password):
                return None

            # 如果是水费模式，需要先切换用户模式
            if mode == "water":
                if not await self.switch_user_mode("water"):
                    print("切换到水费模式失败")
                    return None

            await self.page.goto(self.DETAIL_URL)
            await self.page.wait_for_load_state("networkidle")
            await asyncio.sleep(2)

            page_text = await self.page.inner_text('body')

            # 解析明细数据
            # 格式1(扣费): 房间号扣费\n类型\n- 金额\n时间\n余额:xxx元
            # 格式2(充值): 充值类型\n+ 金额\n时间\n余额:xxx元 (无房间号)
            details = []

            # 先尝试匹配扣费记录（有房间号）
            # 扣费: -金额元
            deduct_pattern = r'(\d+-\d+)扣费\s*\n\s*(\S+)\s*\n\s*-\s*(\d+\.?\d*)元\s*\n\s*(\d+年\d+月\d+日\s*\d+:\d+)\s*\n\s*余额[：:](\d+\.?\d*)元'
            deduct_matches = re.findall(deduct_pattern, page_text)

            for match in deduct_matches:
                details.append({
                    "room": match[0],
                    "type": match[1],
                    "amount": f"-{match[2]}",
                    "date": match[3],
                    "balance": match[4]
                })

            # 再匹配充值记录（无房间号，类型直接是"线上能源充值"等）
            # 充值: +金额元
            recharge_pattern = r'(线上能源充值|充值)\s*\n\s*\+\s*(\d+\.?\d*)元\s*\n\s*(\d+年\d+月\d+日\s*\d+:\d+)\s*\n\s*余额[：:](\d+\.?\d*)元'
            recharge_matches = re.findall(recharge_pattern, page_text)

            for match in recharge_matches:
                details.append({
                    "room": "-",  # 充值记录无房间号
                    "type": match[0],
                    "amount": f"+{match[1]}",
                    "date": match[2],
                    "balance": match[3]
                })

            return details

        except Exception as e:
            print(f"获取明细异常: {e}")
            return None
        finally:
            # 如果是水费模式，爬取完成后切回电费模式
            if mode == "water":
                await self.switch_user_mode("electricity")

    async def get_energy(self, username: str, password: str, mode: str = "electricity") -> Optional[List[Dict[str, Any]]]:
        """
        获取能耗记录

        Args:
            username: 公寓系统账号
            password: 公寓系统密码
            mode: 'electricity' 电费, 'water' 水费

        Note:
            水费模式下，页面显示的 "1kW·h" 实际表示 "1吨水"
        """
        try:
            if not await self.login(username, password):
                return None

            # 如果是水费模式，需要先切换用户模式
            if mode == "water":
                if not await self.switch_user_mode("water"):
                    print("切换到水费模式失败")
                    return None

            await self.page.goto(self.ENERGY_URL)
            await self.page.wait_for_load_state("networkidle")
            await asyncio.sleep(2)

            page_text = await self.page.inner_text('body')

            # 解析能耗数据
            # 格式: 电表-编号\n用电量\n时间\n金额
            # 注意：水费模式下页面显示的仍是"电表"和"kW·h"，但实际是水表和吨
            energy_records = []

            # 使用正则解析每条记录
            pattern = r'(电表-\d+)\s*\n\s*(\d+\.?\d*)kW·h\s*\n\s*(\d+年\d+月\d+日\s*\d+:\d+)\s*\n\s*(\d+\.?\d*)元'
            matches = re.findall(pattern, page_text)

            for match in matches:
                record = {
                    "meter": match[0],
                    "usage": match[1],  # 电费模式下是用电量(kW·h)，水费模式下是用水量(吨)
                    "date": match[2],
                    "amount": match[3]
                }
                energy_records.append(record)

            return energy_records

        except Exception as e:
            print(f"获取能耗记录异常: {e}")
            return None
        finally:
            # 如果是水费模式，爬取完成后切回电费模式
            if mode == "water":
                await self.switch_user_mode("electricity")

    async def _fetch_balance_without_login(self) -> Optional[Dict[str, Any]]:
        """内部方法：已登录状态下获取余额（假设已切换到正确模式）"""
        try:
            await self.page.goto(self.PREPAY_URL, timeout=30000)
            await self.page.wait_for_load_state("networkidle", timeout=30000)
            await asyncio.sleep(1)

            page_text = await self.page.inner_text('body')
            balance_match = re.search(r'水电费余额[^\d]*(\d+\.?\d*)', page_text)
            balance = float(balance_match.group(1)) if balance_match else None

            room_match = re.search(r'(\d+-\d+)\s*扣费', page_text)
            if not room_match:
                room_match = re.search(r'(\d+-\d+)', page_text)
            room_info = room_match.group(1) if room_match else None

            return {"balance": balance, "room_info": room_info}
        except asyncio.TimeoutError:
            print("获取余额超时")
            return None
        except Exception as e:
            print(f"获取余额异常: {e}")
            return None

    async def _fetch_details_without_login(self) -> Optional[List[Dict[str, Any]]]:
        """内部方法：已登录状态下获取明细（假设已切换到正确模式）"""
        try:
            await self.page.goto(self.DETAIL_URL, timeout=30000)
            await self.page.wait_for_load_state("networkidle", timeout=30000)
            await asyncio.sleep(1)

            page_text = await self.page.inner_text('body')
            details = []

            deduct_pattern = r'(\d+-\d+)扣费\s*\n\s*(\S+)\s*\n\s*-\s*(\d+\.?\d*)元\s*\n\s*(\d+年\d+月\d+日\s*\d+:\d+)\s*\n\s*余额[：:](\d+\.?\d*)元'
            deduct_matches = re.findall(deduct_pattern, page_text)

            for match in deduct_matches:
                details.append({
                    "room": match[0],
                    "type": match[1],
                    "amount": f"-{match[2]}",
                    "date": match[3],
                    "balance": match[4]
                })

            recharge_pattern = r'(线上能源充值|充值)\s*\n\s*\+\s*(\d+\.?\d*)元\s*\n\s*(\d+年\d+月\d+日\s*\d+:\d+)\s*\n\s*余额[：:](\d+\.?\d*)元'
            recharge_matches = re.findall(recharge_pattern, page_text)

            for match in recharge_matches:
                details.append({
                    "room": "-",
                    "type": match[0],
                    "amount": f"+{match[1]}",
                    "date": match[2],
                    "balance": match[3]
                })

            return details
        except asyncio.TimeoutError:
            print("获取明细超时")
            return None
        except Exception as e:
            print(f"获取明细异常: {e}")
            return None

    async def _fetch_energy_without_login(self) -> Optional[List[Dict[str, Any]]]:
        """内部方法：已登录状态下获取能耗记录（假设已切换到正确模式）"""
        try:
            await self.page.goto(self.ENERGY_URL, timeout=30000)
            await self.page.wait_for_load_state("networkidle", timeout=30000)
            await asyncio.sleep(1)

            page_text = await self.page.inner_text('body')
            energy_records = []

            pattern = r'(电表-\d+)\s*\n\s*(\d+\.?\d*)kW·h\s*\n\s*(\d+年\d+月\d+日\s*\d+:\d+)\s*\n\s*(\d+\.?\d*)元'
            matches = re.findall(pattern, page_text)

            for match in matches:
                energy_records.append({
                    "meter": match[0],
                    "usage": match[1],
                    "date": match[2],
                    "amount": match[3]
                })

            return energy_records
        except asyncio.TimeoutError:
            print("获取能耗记录超时")
            return None
        except Exception as e:
            print(f"获取能耗记录异常: {e}")
            return None

    async def get_all_data(self, username: str, password: str) -> Dict[str, Any]:
        """
        一次性获取电费和水费所有数据（只需登录一次）

        Returns:
            {
                "electricity": {"balance": ..., "details": ..., "energy": ...},
                "water": {"balance": ..., "details": ..., "energy": ...}
            }
        """
        result = {
            "electricity": {},
            "water": {}
        }

        try:
            # 只登录一次
            if not await self.login(username, password):
                print("登录失败")
                return result

            # 获取电费数据
            print("[爬虫] 切换到电费模式...")
            if not await self.switch_user_mode("electricity"):
                print("切换到电费模式失败")

            print("[爬虫] 获取电费数据...")
            result["electricity"]["balance"] = await self._fetch_balance_without_login()
            result["electricity"]["details"] = await self._fetch_details_without_login()
            result["electricity"]["energy"] = await self._fetch_energy_without_login()

            # 获取水费数据
            print("[爬虫] 切换到水费模式...")
            if not await self.switch_user_mode("water"):
                print("切换到水费模式失败")

            print("[爬虫] 获取水费数据...")
            result["water"]["balance"] = await self._fetch_balance_without_login()
            result["water"]["details"] = await self._fetch_details_without_login()
            result["water"]["energy"] = await self._fetch_energy_without_login()

            # 最后切回电费模式（保持系统原有状态）
            print("[爬虫] 切回电费模式...")
            await self.switch_user_mode("electricity")

            return result

        except Exception as e:
            print(f"获取所有数据异常: {e}")
            # 确保异常时也切回电费模式
            try:
                await self.switch_user_mode("electricity")
            except:
                pass
            return result
