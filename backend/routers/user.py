from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import asyncio
import threading
from datetime import datetime
from collections import defaultdict

from database import get_db
from models import User, Credential
from schemas import CredentialCreate, CredentialResponse, UserSettingsUpdate
from security import encrypt_password
from auth import get_current_user
from services.pushplus import send_test_message
from services.scheduler import crawl_user_data

router = APIRouter(prefix="/api/user", tags=["用户设置"])

# 全局日志存储 (用户ID -> 日志列表)
_crawl_logs = defaultdict(list)


def add_crawl_log(user_id: int, message: str):
    """添加爬取日志"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    _crawl_logs[user_id].append(log_entry)
    # 只保留最近50条日志
    if len(_crawl_logs[user_id]) > 50:
        _crawl_logs[user_id] = _crawl_logs[user_id][-50:]
    print(f"[用户{user_id}] {message}")


def run_crawl_in_thread(user_id: int):
    """在新线程中运行异步爬取"""
    add_crawl_log(user_id, "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    add_crawl_log(user_id, "开始爬取水电费数据")
    add_crawl_log(user_id, "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    try:
        # 创建新的事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # 运行爬取
        result = loop.run_until_complete(crawl_user_data_with_logs(user_id))

        if result:
            add_crawl_log(user_id, "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            add_crawl_log(user_id, "✓ 数据爬取完成")
            add_crawl_log(user_id, "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        else:
            add_crawl_log(user_id, "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            add_crawl_log(user_id, "✗ 数据爬取失败，请检查账号密码是否正确")
            add_crawl_log(user_id, "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        loop.close()
    except Exception as e:
        add_crawl_log(user_id, f"✗ 爬取异常: {str(e)}")


async def crawl_user_data_with_logs(user_id: int):
    """包装爬取函数以添加日志"""
    from database import SessionLocal
    from models import User, Credential, CrawlRecord
    from security import decrypt_password
    from crawler import PMSCrawler
    import json

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.credential:
            add_crawl_log(user_id, "✗ 未找到凭证信息，请先保存凭证")
            return False

        credential = user.credential
        add_crawl_log(user_id, f"账号: {credential.pms_account}")

        try:
            password = decrypt_password(credential.pms_password_encrypted)
        except Exception as e:
            add_crawl_log(user_id, "✗ 密码解密失败，请重新保存凭证")
            return False

        async with PMSCrawler() as crawler:
            # 登录
            add_crawl_log(user_id, "正在登录...")
            login_success = await crawler.login(credential.pms_account, password)
            if not login_success:
                add_crawl_log(user_id, "✗ 登录失败，请检查账号密码")
                return False
            add_crawl_log(user_id, "✓ 登录成功")

            # 获取电费数据
            add_crawl_log(user_id, "━━━━━ 电费数据 ━━━━━")

            add_crawl_log(user_id, "切换电费模式...")
            await crawler.switch_user_mode("electricity")

            add_crawl_log(user_id, "获取余额...")
            elec_balance = await crawler._fetch_balance_without_login()
            if elec_balance and elec_balance.get("balance") is not None:
                add_crawl_log(user_id, f"✓ 余额: {elec_balance.get('balance')} 元")
            else:
                add_crawl_log(user_id, "✗ 未获取到余额")
                elec_balance = None

            add_crawl_log(user_id, "获取明细...")
            elec_details = await crawler._fetch_details_without_login()
            if elec_details:
                add_crawl_log(user_id, f"✓ 明细: {len(elec_details)} 条")
            else:
                add_crawl_log(user_id, "- 暂无明细")

            add_crawl_log(user_id, "获取能耗记录...")
            elec_energy = await crawler._fetch_energy_without_login()
            if elec_energy:
                add_crawl_log(user_id, f"✓ 能耗: {len(elec_energy)} 条")
            else:
                add_crawl_log(user_id, "- 暂无能耗记录")

            # 获取水费数据
            add_crawl_log(user_id, "━━━━━ 水费数据 ━━━━━")

            add_crawl_log(user_id, "切换水费模式...")
            if not await crawler.switch_user_mode("water"):
                add_crawl_log(user_id, "✗ 切换水费模式失败")
                water_balance = None
                water_details = None
                water_energy = None
            else:
                add_crawl_log(user_id, "获取余额...")
                water_balance = await crawler._fetch_balance_without_login()
                if water_balance and water_balance.get("balance") is not None:
                    add_crawl_log(user_id, f"✓ 余额: {water_balance.get('balance')} 元")
                else:
                    add_crawl_log(user_id, "✗ 未获取到余额")
                    water_balance = None

                add_crawl_log(user_id, "获取明细...")
                water_details = await crawler._fetch_details_without_login()
                if water_details:
                    add_crawl_log(user_id, f"✓ 明细: {len(water_details)} 条")
                else:
                    add_crawl_log(user_id, "- 暂无明细")

                add_crawl_log(user_id, "获取能耗记录...")
                water_energy = await crawler._fetch_energy_without_login()
                if water_energy:
                    add_crawl_log(user_id, f"✓ 能耗: {len(water_energy)} 条")
                else:
                    add_crawl_log(user_id, "- 暂无能耗记录")

            # 恢复电费模式
            add_crawl_log(user_id, "恢复电费模式...")
            await crawler.switch_user_mode("electricity")

            # 保存到数据库
            add_crawl_log(user_id, "保存数据...")
            record = CrawlRecord(
                user_id=user.id,
                # 电费数据
                balance=elec_balance.get("balance") if elec_balance else None,
                details_data=json.dumps(elec_details, ensure_ascii=False) if elec_details else None,
                energy_data=json.dumps(elec_energy, ensure_ascii=False) if elec_energy else None,
                # 水费数据
                water_balance=water_balance.get("balance") if water_balance else None,
                water_details_data=json.dumps(water_details, ensure_ascii=False) if water_details else None,
                water_energy_data=json.dumps(water_energy, ensure_ascii=False) if water_energy else None,
                is_cached=1
            )
            db.add(record)
            db.commit()
            add_crawl_log(user_id, "✓ 保存成功")

            # 更新房间信息
            if elec_balance and elec_balance.get('room_info') and not credential.room_info:
                credential.room_info = elec_balance.get('room_info')
                db.commit()

            return True

    except Exception as e:
        add_crawl_log(user_id, f"✗ 爬取异常: {str(e)}")
        return False
    finally:
        db.close()


@router.put("/credentials", response_model=CredentialResponse)
def save_credentials(
    cred_data: CredentialCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 检查是否已有凭证
    existing = db.query(Credential).filter(
        Credential.user_id == current_user.id
    ).first()

    user_id = current_user.id

    if existing:
        existing.pms_account = cred_data.pms_account
        existing.pms_password_encrypted = encrypt_password(cred_data.pms_password)
        db.commit()
        db.refresh(existing)
        # 在后台线程触发爬取
        print(f"[凭证] 用户 {user_id} 更新凭证，触发后台爬取")
        thread = threading.Thread(target=run_crawl_in_thread, args=(user_id,), daemon=True)
        thread.start()
        return existing

    credential = Credential(
        user_id=current_user.id,
        pms_account=cred_data.pms_account,
        pms_password_encrypted=encrypt_password(cred_data.pms_password)
    )
    db.add(credential)
    db.commit()
    db.refresh(credential)

    # 在后台线程触发爬取
    print(f"[凭证] 用户 {user_id} 创建凭证，触发后台爬取")
    thread = threading.Thread(target=run_crawl_in_thread, args=(user_id,), daemon=True)
    thread.start()

    return credential


@router.get("/credentials", response_model=CredentialResponse)
def get_credentials(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    credential = db.query(Credential).filter(
        Credential.user_id == current_user.id
    ).first()

    if not credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到凭证信息"
        )

    return credential


@router.delete("/credentials")
def delete_credentials(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    credential = db.query(Credential).filter(
        Credential.user_id == current_user.id
    ).first()

    if not credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到凭证信息"
        )

    db.delete(credential)
    db.commit()

    return {"message": "凭证已删除"}


@router.put("/settings")
def update_settings(
    settings: UserSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if settings.pushplus_token is not None:
        current_user.pushplus_token = settings.pushplus_token
    if settings.balance_threshold is not None:
        current_user.balance_threshold = settings.balance_threshold
    if settings.water_balance_threshold is not None:
        current_user.water_balance_threshold = settings.water_balance_threshold

    db.commit()

    return {"message": "设置已更新"}


@router.post("/test-push")
def test_push_notification(
    current_user: User = Depends(get_current_user)
):
    if not current_user.pushplus_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请先配置PushPlus Token"
        )

    success = send_test_message(current_user.pushplus_token)

    if success:
        return {"message": "测试消息已发送"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="发送测试消息失败，请检查Token是否正确"
        )


@router.post("/crawl")
def trigger_crawl(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """手动触发数据爬取"""
    # 检查是否配置了凭证
    credential = db.query(Credential).filter(
        Credential.user_id == current_user.id
    ).first()

    if not credential:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请先配置公寓系统凭证"
        )

    # 清除旧日志
    _crawl_logs[current_user.id] = []
    add_crawl_log(current_user.id, "手动触发数据爬取...")

    # 在后台线程触发爬取
    thread = threading.Thread(target=run_crawl_in_thread, args=(current_user.id,), daemon=True)
    thread.start()

    return {"message": "数据爬取已启动"}


@router.get("/crawl/logs")
def get_crawl_logs(
    current_user: User = Depends(get_current_user)
):
    """获取爬取日志"""
    logs = _crawl_logs.get(current_user.id, [])
    return {"logs": logs}


@router.delete("/crawl/logs")
def clear_crawl_logs(
    current_user: User = Depends(get_current_user)
):
    """清除爬取日志"""
    _crawl_logs[current_user.id] = []
    return {"message": "日志已清除"}
