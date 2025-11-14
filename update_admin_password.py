"""
관리자 비밀번호 업데이트 스크립트
.env 파일의 ADMIN_PASSWORD를 데이터베이스에 반영합니다.
"""
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.admin_user import AdminUser
from app.utils.security import get_password_hash
from app.config import settings

def update_admin_password():
    """관리자 비밀번호를 .env의 값으로 업데이트"""
    db = SessionLocal()

    try:
        # 관리자 계정 조회
        admin_user = db.query(AdminUser).filter(
            AdminUser.username == settings.admin_username
        ).first()

        if not admin_user:
            print(f"❌ 관리자 계정 '{settings.admin_username}'을 찾을 수 없습니다.")
            return

        # 비밀번호 업데이트
        new_password_hash = get_password_hash(settings.admin_password)
        admin_user.password_hash = new_password_hash
        db.commit()

        print("=" * 60)
        print("✅ 관리자 비밀번호가 성공적으로 업데이트되었습니다!")
        print("=" * 60)
        print(f"사용자명: {settings.admin_username}")
        print(f"새 비밀번호: {settings.admin_password}")
        print("=" * 60)
        print("\n⚠️ 중요: 이 비밀번호를 안전한 곳에 보관하세요!")

    except Exception as e:
        db.rollback()
        print(f"❌ 오류 발생: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    print("\n🔐 관리자 비밀번호 업데이트 시작...\n")
    update_admin_password()
