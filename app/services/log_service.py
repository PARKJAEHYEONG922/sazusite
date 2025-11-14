"""
로그 조회 서비스
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from app.models.log import ErrorLog, APIUsageLog, AccessLog, RateLimitLog


class LogService:
    """로그 조회 및 통계 서비스"""

    def __init__(self, db: Session):
        self.db = db

    # ===== 에러 로그 =====
    def get_recent_errors(self, limit: int = 100, offset: int = 0) -> List[ErrorLog]:
        """최근 에러 목록 조회"""
        return self.db.query(ErrorLog)\
            .order_by(desc(ErrorLog.timestamp))\
            .offset(offset)\
            .limit(limit)\
            .all()

    def get_error_count(self, hours: Optional[int] = None) -> int:
        """에러 개수 (전체 또는 특정 시간 내)"""
        query = self.db.query(func.count(ErrorLog.id))
        if hours:
            since = datetime.now() - timedelta(hours=hours)
            query = query.filter(ErrorLog.timestamp >= since)
        return query.scalar()

    def get_error_stats_by_type(self, hours: int = 24) -> List[Dict]:
        """에러 타입별 통계"""
        since = datetime.now() - timedelta(hours=hours)
        results = self.db.query(
            ErrorLog.error_type,
            func.count(ErrorLog.id).label('count')
        ).filter(
            ErrorLog.timestamp >= since
        ).group_by(
            ErrorLog.error_type
        ).order_by(
            desc('count')
        ).all()

        return [{"type": r.error_type, "count": r.count} for r in results]

    # ===== API 사용 로그 =====
    def get_recent_api_usage(self, limit: int = 100, offset: int = 0) -> List[APIUsageLog]:
        """최근 API 사용 내역"""
        return self.db.query(APIUsageLog)\
            .order_by(desc(APIUsageLog.timestamp))\
            .offset(offset)\
            .limit(limit)\
            .all()

    def get_api_usage_stats(self, days: int = 7) -> Dict:
        """API 사용 통계"""
        since = datetime.now() - timedelta(days=days)

        total_calls = self.db.query(func.count(APIUsageLog.id))\
            .filter(APIUsageLog.timestamp >= since)\
            .scalar()

        cache_hits = self.db.query(func.count(APIUsageLog.id))\
            .filter(APIUsageLog.timestamp >= since, APIUsageLog.cache_hit == True)\
            .scalar()

        total_cost = self.db.query(func.sum(APIUsageLog.estimated_cost))\
            .filter(APIUsageLog.timestamp >= since)\
            .scalar() or 0.0

        avg_response_time = self.db.query(func.avg(APIUsageLog.response_time_ms))\
            .filter(APIUsageLog.timestamp >= since)\
            .scalar() or 0

        return {
            "total_calls": total_calls or 0,
            "cache_hits": cache_hits or 0,
            "cache_hit_rate": (cache_hits / total_calls * 100) if total_calls > 0 else 0,
            "total_cost": round(total_cost, 4),
            "avg_response_time_ms": round(avg_response_time, 2)
        }

    def get_api_usage_by_service(self, days: int = 7) -> List[Dict]:
        """서비스별 API 사용량"""
        since = datetime.now() - timedelta(days=days)

        results = self.db.query(
            APIUsageLog.service_code,
            func.count(APIUsageLog.id).label('count'),
            func.sum(APIUsageLog.estimated_cost).label('cost')
        ).filter(
            APIUsageLog.timestamp >= since
        ).group_by(
            APIUsageLog.service_code
        ).order_by(
            desc('count')
        ).all()

        return [
            {
                "service": r.service_code,
                "count": r.count,
                "cost": round(r.cost or 0, 4)
            }
            for r in results
        ]

    # ===== 접속 로그 =====
    def get_recent_access(self, limit: int = 100, offset: int = 0) -> List[AccessLog]:
        """최근 접속 로그"""
        return self.db.query(AccessLog)\
            .order_by(desc(AccessLog.timestamp))\
            .offset(offset)\
            .limit(limit)\
            .all()

    def get_access_stats(self, days: int = 7) -> Dict:
        """접속 통계"""
        since = datetime.now() - timedelta(days=days)

        total_requests = self.db.query(func.count(AccessLog.id))\
            .filter(AccessLog.timestamp >= since)\
            .scalar()

        fortune_requests = self.db.query(func.count(AccessLog.id))\
            .filter(AccessLog.timestamp >= since, AccessLog.is_fortune_request == True)\
            .scalar()

        unique_ips = self.db.query(func.count(func.distinct(AccessLog.client_ip)))\
            .filter(AccessLog.timestamp >= since)\
            .scalar()

        avg_response_time = self.db.query(func.avg(AccessLog.response_time_ms))\
            .filter(AccessLog.timestamp >= since)\
            .scalar() or 0

        return {
            "total_requests": total_requests or 0,
            "fortune_requests": fortune_requests or 0,
            "unique_visitors": unique_ips or 0,
            "avg_response_time_ms": round(avg_response_time, 2)
        }

    def get_popular_services(self, days: int = 7) -> List[Dict]:
        """인기 서비스 순위"""
        since = datetime.now() - timedelta(days=days)

        results = self.db.query(
            AccessLog.service_code,
            func.count(AccessLog.id).label('count')
        ).filter(
            AccessLog.timestamp >= since,
            AccessLog.is_fortune_request == True,
            AccessLog.service_code.isnot(None)
        ).group_by(
            AccessLog.service_code
        ).order_by(
            desc('count')
        ).all()

        return [{"service": r.service_code, "count": r.count} for r in results]

    # ===== Rate Limit 로그 =====
    def get_recent_rate_limit_violations(self, limit: int = 100, offset: int = 0) -> List[RateLimitLog]:
        """최근 Rate Limit 위반 내역"""
        return self.db.query(RateLimitLog)\
            .order_by(desc(RateLimitLog.timestamp))\
            .offset(offset)\
            .limit(limit)\
            .all()

    def get_rate_limit_stats(self, days: int = 7) -> Dict:
        """Rate Limit 위반 통계"""
        since = datetime.now() - timedelta(days=days)

        total_violations = self.db.query(func.count(RateLimitLog.id))\
            .filter(RateLimitLog.timestamp >= since)\
            .scalar()

        minute_violations = self.db.query(func.count(RateLimitLog.id))\
            .filter(RateLimitLog.timestamp >= since, RateLimitLog.limit_type == "minute")\
            .scalar()

        day_violations = self.db.query(func.count(RateLimitLog.id))\
            .filter(RateLimitLog.timestamp >= since, RateLimitLog.limit_type == "day")\
            .scalar()

        unique_ips = self.db.query(func.count(func.distinct(RateLimitLog.client_ip)))\
            .filter(RateLimitLog.timestamp >= since)\
            .scalar()

        return {
            "total_violations": total_violations or 0,
            "minute_violations": minute_violations or 0,
            "day_violations": day_violations or 0,
            "unique_violators": unique_ips or 0
        }

    def get_top_violators(self, days: int = 7, limit: int = 10) -> List[Dict]:
        """가장 많이 위반한 IP 목록"""
        since = datetime.now() - timedelta(days=days)

        results = self.db.query(
            RateLimitLog.client_ip,
            func.count(RateLimitLog.id).label('count')
        ).filter(
            RateLimitLog.timestamp >= since
        ).group_by(
            RateLimitLog.client_ip
        ).order_by(
            desc('count')
        ).limit(limit).all()

        return [{"ip": r.client_ip, "count": r.count} for r in results]

    # ===== 대시보드 요약 =====
    def get_dashboard_summary(self) -> Dict:
        """대시보드 요약 정보 (24시간 기준)"""
        # Get all stats
        api_stats = self.get_api_usage_stats(days=1)
        access_stats = self.get_access_stats(days=1)
        rate_limit_stats = self.get_rate_limit_stats(days=1)

        # Return flat structure for template
        return {
            "error_count": self.get_error_count(hours=24),
            "api_calls": api_stats['total_calls'],
            "api_cost": api_stats['total_cost'],
            "visitor_count": access_stats['unique_visitors'],
            "rate_limit_violations": rate_limit_stats['total_violations'],
            "avg_response_time_ms": access_stats['avg_response_time_ms']
        }

    # ===== 로그 정리 (개별 삭제) =====
    def delete_error_logs(self, days: int) -> int:
        """에러 로그 삭제"""
        cutoff = datetime.now() - timedelta(days=days)
        deleted = self.db.query(ErrorLog)\
            .filter(ErrorLog.timestamp < cutoff)\
            .delete(synchronize_session=False)
        self.db.commit()
        return deleted

    def delete_api_logs(self, days: int) -> int:
        """API 로그 삭제"""
        cutoff = datetime.now() - timedelta(days=days)
        deleted = self.db.query(APIUsageLog)\
            .filter(APIUsageLog.timestamp < cutoff)\
            .delete(synchronize_session=False)
        self.db.commit()
        return deleted

    def delete_access_logs(self, days: int) -> int:
        """접속 로그 삭제"""
        cutoff = datetime.now() - timedelta(days=days)
        deleted = self.db.query(AccessLog)\
            .filter(AccessLog.timestamp < cutoff)\
            .delete(synchronize_session=False)
        self.db.commit()
        return deleted

    def delete_rate_limit_logs(self, days: int) -> int:
        """Rate Limit 로그 삭제"""
        cutoff = datetime.now() - timedelta(days=days)
        deleted = self.db.query(RateLimitLog)\
            .filter(RateLimitLog.timestamp < cutoff)\
            .delete(synchronize_session=False)
        self.db.commit()
        return deleted

    def get_log_storage_info(self) -> Dict:
        """로그 데이터 저장 현황"""
        total_logs = {
            "access_logs": self.db.query(func.count(AccessLog.id)).scalar() or 0,
            "api_logs": self.db.query(func.count(APIUsageLog.id)).scalar() or 0,
            "error_logs": self.db.query(func.count(ErrorLog.id)).scalar() or 0,
            "rate_limit_logs": self.db.query(func.count(RateLimitLog.id)).scalar() or 0
        }

        # 가장 오래된 로그 날짜
        oldest_access = self.db.query(func.min(AccessLog.timestamp)).scalar()
        oldest_api = self.db.query(func.min(APIUsageLog.timestamp)).scalar()
        oldest_error = self.db.query(func.min(ErrorLog.timestamp)).scalar()
        oldest_rate_limit = self.db.query(func.min(RateLimitLog.timestamp)).scalar()

        return {
            "total_logs": total_logs,
            "oldest_dates": {
                "access": oldest_access.strftime('%Y-%m-%d') if oldest_access else None,
                "api": oldest_api.strftime('%Y-%m-%d') if oldest_api else None,
                "error": oldest_error.strftime('%Y-%m-%d') if oldest_error else None,
                "rate_limit": oldest_rate_limit.strftime('%Y-%m-%d') if oldest_rate_limit else None
            },
            "total_count": sum(total_logs.values())
        }
