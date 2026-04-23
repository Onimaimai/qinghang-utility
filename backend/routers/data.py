from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import json

from database import get_db
from models import User, Credential, CrawlRecord
from auth import get_current_user
from services.scheduler import get_server_cached_data

router = APIRouter(prefix="/api/data", tags=["数据获取"])


@router.get("/balance")
async def get_balance(
    type: str = Query("electricity", pattern="^(electricity|water)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取水电费余额（从数据库缓存获取）"""
    credential = db.query(Credential).filter(
        Credential.user_id == current_user.id
    ).first()

    if not credential:
        raise HTTPException(status_code=400, detail="请先配置公寓系统凭证")

    # 从数据库获取服务器缓存
    cached = get_server_cached_data(db, current_user.id)

    if cached:
        balance = cached.balance if type == "electricity" else cached.water_balance

        if balance is not None:
            return {
                "balance": balance,
                "room_info": credential.room_info,
                "crawled_at": cached.crawled_at.isoformat(),
                "has_data": True,
                "type": type
            }

    # 没有数据
    return {
        "balance": None,
        "room_info": credential.room_info,
        "crawled_at": None,
        "has_data": False,
        "type": type,
        "message": "暂无数据，系统每天9:00自动更新"
    }


@router.get("/details")
async def get_details(
    type: str = Query("electricity", pattern="^(electricity|water)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取余额明细（从数据库缓存获取）"""
    credential = db.query(Credential).filter(
        Credential.user_id == current_user.id
    ).first()

    if not credential:
        raise HTTPException(status_code=400, detail="请先配置公寓系统凭证")

    # 从数据库获取服务器缓存
    cached = get_server_cached_data(db, current_user.id)

    if cached:
        details_data = cached.details_data if type == "electricity" else cached.water_details_data

        if details_data:
            return {
                "details": json.loads(details_data),
                "crawled_at": cached.crawled_at.isoformat(),
                "has_data": True,
                "type": type
            }

    # 没有数据
    return {
        "details": [],
        "crawled_at": None,
        "has_data": False,
        "type": type,
        "message": "暂无数据，系统每天9:00自动更新"
    }


@router.get("/energy")
async def get_energy(
    type: str = Query("electricity", pattern="^(electricity|water)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取能耗记录（从数据库缓存获取）"""
    credential = db.query(Credential).filter(
        Credential.user_id == current_user.id
    ).first()

    if not credential:
        raise HTTPException(status_code=400, detail="请先配置公寓系统凭证")

    # 从数据库获取服务器缓存
    cached = get_server_cached_data(db, current_user.id)

    if cached:
        energy_data = cached.energy_data if type == "electricity" else cached.water_energy_data

        if energy_data:
            return {
                "energy": json.loads(energy_data),
                "crawled_at": cached.crawled_at.isoformat(),
                "has_data": True,
                "type": type,
                "unit": "吨" if type == "water" else "kW·h",
                "price": "2.4元/吨" if type == "water" else None
            }

    # 没有数据
    return {
        "energy": [],
        "crawled_at": None,
        "has_data": False,
        "type": type,
        "unit": "吨" if type == "water" else "kW·h",
        "message": "暂无数据，系统每天9:00自动更新"
    }


@router.get("/history")
def get_history(
    type: str = Query("electricity", pattern="^(electricity|water)$"),
    limit: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取历史余额记录"""
    records = db.query(CrawlRecord).filter(
        CrawlRecord.user_id == current_user.id,
        CrawlRecord.is_cached == 1  # 只返回服务器缓存记录
    ).order_by(CrawlRecord.crawled_at.desc()).limit(limit).all()

    result_records = []
    for r in records:
        balance = r.balance if type == "electricity" else r.water_balance
        if balance is not None:
            result_records.append({
                "id": r.id,
                "balance": balance,
                "crawled_at": r.crawled_at.isoformat()
            })

    return {
        "records": result_records,
        "type": type
    }


@router.get("/summary")
async def get_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取水电费汇总信息"""
    credential = db.query(Credential).filter(
        Credential.user_id == current_user.id
    ).first()

    if not credential:
        raise HTTPException(status_code=400, detail="请先配置公寓系统凭证")

    cached = get_server_cached_data(db, current_user.id)

    if not cached:
        return {
            "electricity": {"balance": None, "has_data": False},
            "water": {"balance": None, "has_data": False},
            "crawled_at": None
        }

    return {
        "electricity": {
            "balance": cached.balance,
            "has_data": cached.balance is not None
        },
        "water": {
            "balance": cached.water_balance,
            "has_data": cached.water_balance is not None
        },
        "crawled_at": cached.crawled_at.isoformat() if cached else None
    }
