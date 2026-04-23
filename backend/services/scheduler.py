from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
import json
import asyncio

from database import SessionLocal
from models import User, Credential, CrawlRecord
from security import decrypt_password
from crawler import PMSCrawler
from services.pushplus import send_balance_alert

scheduler = AsyncIOScheduler()


async def crawl_user_data(user_id: int, db=None):
    """爬取单个用户的水电数据"""
    from database import SessionLocal

    should_close = False
    if db is None:
        db = SessionLocal()
        should_close = True

    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.credential:
            print(f"[爬取] 用户 {user_id} 不存在或未配置凭证")
            return False

        credential = user.credential
        password = decrypt_password(credential.pms_password_encrypted)

        print(f"[爬取] 开始爬取用户 {user.username} 的数据...")

        async with PMSCrawler() as crawler:
            # 使用 get_all_data 一次获取水电费所有数据
            all_data = await crawler.get_all_data(credential.pms_account, password)

        # 提取电费数据
        elec_balance = all_data.get("electricity", {}).get("balance")
        elec_details = all_data.get("electricity", {}).get("details")
        elec_energy = all_data.get("electricity", {}).get("energy")

        # 提取水费数据
        water_balance = all_data.get("water", {}).get("balance")
        water_details = all_data.get("water", {}).get("details")
        water_energy = all_data.get("water", {}).get("energy")

        # 检查是否有任何数据
        has_elec_data = elec_balance and elec_balance.get("balance") is not None
        has_water_data = water_balance and water_balance.get("balance") is not None

        if has_elec_data or has_water_data:
            record = CrawlRecord(
                user_id=user.id,
                # 电费数据
                balance=elec_balance.get("balance") if has_elec_data else None,
                details_data=json.dumps(elec_details, ensure_ascii=False) if elec_details else None,
                energy_data=json.dumps(elec_energy, ensure_ascii=False) if elec_energy else None,
                # 水费数据
                water_balance=water_balance.get("balance") if has_water_data else None,
                water_details_data=json.dumps(water_details, ensure_ascii=False) if water_details else None,
                water_energy_data=json.dumps(water_energy, ensure_ascii=False) if water_energy else None,
                is_cached=1
            )
            db.add(record)
            db.commit()

            # 更新房间信息
            if has_elec_data and elec_balance.get("room_info") and not credential.room_info:
                credential.room_info = elec_balance.get("room_info")
                db.commit()

            print(f"[爬取] 用户 {user.username} 数据爬取完成")
            if has_elec_data:
                print(f"  - 电费余额: {elec_balance.get('balance')}元")
            if has_water_data:
                print(f"  - 水费余额: {water_balance.get('balance')}元")
            return True
        else:
            print(f"[爬取] 用户 {user.username} 数据爬取失败")
            return False

    except Exception as e:
        print(f"[爬取] 用户 {user_id} 爬取异常: {e}")
        return False
    finally:
        if should_close:
            db.close()


async def crawl_all_users():
    """定时任务：爬取所有用户的水电数据"""
    print(f"[定时任务] 开始爬取所有用户数据 - {datetime.now()}")

    db = SessionLocal()
    try:
        # 获取所有有凭证的用户
        users_with_credentials = db.query(User).join(Credential).all()

        for user in users_with_credentials:
            try:
                credential = user.credential
                password = decrypt_password(credential.pms_password_encrypted)

                print(f"[定时任务] 爬取用户 {user.username} 的数据...")

                async with PMSCrawler() as crawler:
                    # 使用 get_all_data 一次获取水电费所有数据
                    all_data = await crawler.get_all_data(credential.pms_account, password)

                # 提取电费数据
                elec_balance = all_data.get("electricity", {}).get("balance")
                elec_details = all_data.get("electricity", {}).get("details")
                elec_energy = all_data.get("electricity", {}).get("energy")

                # 提取水费数据
                water_balance = all_data.get("water", {}).get("balance")
                water_details = all_data.get("water", {}).get("details")
                water_energy = all_data.get("water", {}).get("energy")

                # 检查是否有任何数据
                has_elec_data = elec_balance and elec_balance.get("balance") is not None
                has_water_data = water_balance and water_balance.get("balance") is not None

                if has_elec_data or has_water_data:
                    # 保存缓存记录
                    record = CrawlRecord(
                        user_id=user.id,
                        # 电费数据
                        balance=elec_balance.get("balance") if has_elec_data else None,
                        details_data=json.dumps(elec_details, ensure_ascii=False) if elec_details else None,
                        energy_data=json.dumps(elec_energy, ensure_ascii=False) if elec_energy else None,
                        # 水费数据
                        water_balance=water_balance.get("balance") if has_water_data else None,
                        water_details_data=json.dumps(water_details, ensure_ascii=False) if water_details else None,
                        water_energy_data=json.dumps(water_energy, ensure_ascii=False) if water_energy else None,
                        is_cached=1
                    )
                    db.add(record)
                    db.commit()

                    # 更新房间信息
                    if has_elec_data and elec_balance.get("room_info") and not credential.room_info:
                        credential.room_info = elec_balance.get("room_info")
                        db.commit()

                    # 发送余额提醒
                    alerts = []
                    if has_elec_data:
                        elec_balance_val = elec_balance.get("balance", 0)
                        if elec_balance_val < user.balance_threshold and user.pushplus_token:
                            alerts.append({
                                "type": "电费",
                                "balance": elec_balance_val,
                                "threshold": user.balance_threshold
                            })
                        print(f"[定时任务] 用户 {user.username} 电费余额: {elec_balance_val}元")

                    if has_water_data:
                        water_balance_val = water_balance.get("balance", 0)
                        if water_balance_val < user.water_balance_threshold and user.pushplus_token:
                            alerts.append({
                                "type": "水费",
                                "balance": water_balance_val,
                                "threshold": user.water_balance_threshold
                            })
                        print(f"[定时任务] 用户 {user.username} 水费余额: {water_balance_val}元")

                    # 发送提醒
                    if alerts and user.pushplus_token:
                        send_balance_alert(user.pushplus_token, alerts)
                        print(f"[定时任务] 用户 {user.username} 已发送余额不足提醒")
                else:
                    print(f"[定时任务] 用户 {user.username} 数据爬取失败")

                # 避免请求过快
                await asyncio.sleep(2)

            except Exception as e:
                print(f"[定时任务] 用户 {user.username} 爬取异常: {e}")
                continue

    except Exception as e:
        print(f"[定时任务] 异常: {e}")
    finally:
        db.close()

    print(f"[定时任务] 完成 - {datetime.now()}")


def get_server_cached_data(db, user_id: int, max_age_hours: int = 48):
    """获取服务器缓存数据（定时任务保存的数据，默认48小时内有效）"""
    cache_time = datetime.now() - timedelta(hours=max_age_hours)

    record = db.query(CrawlRecord).filter(
        CrawlRecord.user_id == user_id,
        CrawlRecord.is_cached == 1,
        CrawlRecord.crawled_at >= cache_time
    ).order_by(CrawlRecord.crawled_at.desc()).first()

    return record


def start_scheduler():
    """启动定时任务"""
    # 每天9点执行
    scheduler.add_job(
        crawl_all_users,
        CronTrigger(hour=9, minute=0),
        id="crawl_all_users",
        replace_existing=True
    )

    scheduler.start()
    print("[定时任务] 已启动，每天9:00自动获取数据")


def stop_scheduler():
    """停止定时任务"""
    scheduler.shutdown()
    print("[定时任务] 已停止")
