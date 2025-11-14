"""
환경 설정 검증 모듈 - 서버 시작 전 필수 설정 체크
"""
import os
from pathlib import Path
from typing import List, Tuple
import secrets
from dotenv import load_dotenv

# .env 파일 로드 (시스템 환경 변수보다 우선)
load_dotenv(override=True)


class EnvironmentValidator:
    """환경 설정 검증기"""

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_all(self) -> Tuple[bool, List[str], List[str]]:
        """
        모든 환경 설정 검증

        Returns:
            (is_valid, errors, warnings)
        """
        self._check_secret_key()
        self._check_gemini_api_key()
        self._check_database()
        self._check_environment_setting()
        self._check_cache_settings()
        self._check_admin_credentials()

        return (len(self.errors) == 0, self.errors, self.warnings)

    def _check_secret_key(self):
        """SECRET_KEY 검증"""
        secret_key = os.getenv("SECRET_KEY", "")

        # 1. SECRET_KEY가 설정되어 있는지
        if not secret_key:
            self.errors.append("❌ SECRET_KEY가 설정되지 않았습니다.")
            return

        # 2. 기본값 그대로 사용하는지
        default_keys = [
            "change-this-secret-key-in-production",
            "your-secret-key-here",
            "secret",
            "password"
        ]
        if secret_key in default_keys:
            self.errors.append(
                "❌ SECRET_KEY가 기본값입니다. 보안을 위해 반드시 변경하세요!\n"
                "   생성 방법: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
            )
            return

        # 3. 충분히 긴지 (최소 32자)
        if len(secret_key) < 32:
            self.warnings.append(
                f"⚠️  SECRET_KEY가 너무 짧습니다 (현재: {len(secret_key)}자, 권장: 32자 이상)."
            )

    def _check_gemini_api_key(self):
        """Gemini API KEY 검증"""
        api_key = os.getenv("GEMINI_API_KEY", "")

        if not api_key:
            self.errors.append("❌ GEMINI_API_KEY가 설정되지 않았습니다.")
            return

        if api_key in ["your-gemini-api-key-here", "test-key"]:
            self.errors.append("❌ GEMINI_API_KEY가 기본값입니다. 실제 API 키를 설정하세요.")
            return

        # Gemini API 키 형식 체크 (AIza로 시작)
        if not api_key.startswith("AIza"):
            self.warnings.append(
                "⚠️  GEMINI_API_KEY 형식이 올바르지 않을 수 있습니다. "
                "(일반적으로 'AIza'로 시작)"
            )

    def _check_database(self):
        """데이터베이스 설정 검증"""
        db_url = os.getenv("DATABASE_URL", "")

        if not db_url:
            self.errors.append("❌ DATABASE_URL이 설정되지 않았습니다.")
            return

        # SQLite 파일 경로 추출
        if db_url.startswith("sqlite:///"):
            db_path = db_url.replace("sqlite:///", "")

            # 상대 경로인 경우 절대 경로로 변환
            if not db_path.startswith("/") and not (len(db_path) > 1 and db_path[1] == ":"):
                db_path = Path.cwd() / db_path

            db_file = Path(db_path)

            # 데이터베이스 파일이 없으면 경고 (첫 실행시엔 정상)
            if not db_file.exists():
                self.warnings.append(
                    f"⚠️  데이터베이스 파일이 없습니다: {db_file}\n"
                    "   첫 실행이면 정상입니다. 'python -m app.init_db'로 초기화하세요."
                )

    def _check_environment_setting(self):
        """ENVIRONMENT 설정 검증"""
        env = os.getenv("ENVIRONMENT", "development")

        valid_environments = ["development", "production"]
        if env not in valid_environments:
            self.warnings.append(
                f"⚠️  ENVIRONMENT 값이 올바르지 않습니다: {env}\n"
                f"   유효한 값: {', '.join(valid_environments)}"
            )

        # 프로덕션인데 DEBUG=True면 경고
        if env == "production":
            debug = os.getenv("DEBUG", "False").lower() == "true"
            if debug:
                self.warnings.append(
                    "⚠️  프로덕션 환경에서 DEBUG=True는 권장하지 않습니다."
                )

    def _check_cache_settings(self):
        """캐시 설정 검증"""
        cache_enabled = os.getenv("CACHE_ENABLED", "True").lower()

        if cache_enabled not in ["true", "false"]:
            self.warnings.append(
                f"⚠️  CACHE_ENABLED 값이 올바르지 않습니다: {cache_enabled}\n"
                "   유효한 값: True, False"
            )

        try:
            cache_duration = int(os.getenv("CACHE_DURATION_HOURS", "24"))
            if cache_duration < 1:
                self.warnings.append(
                    "⚠️  CACHE_DURATION_HOURS가 너무 작습니다 (최소 1시간 권장)."
                )
        except ValueError:
            self.warnings.append(
                "⚠️  CACHE_DURATION_HOURS는 숫자여야 합니다."
            )

    def _check_admin_credentials(self):
        """관리자 계정 설정 검증"""
        admin_username = os.getenv("ADMIN_USERNAME", "")
        admin_password = os.getenv("ADMIN_PASSWORD", "")

        if not admin_username:
            self.errors.append("❌ ADMIN_USERNAME이 설정되지 않았습니다.")

        if not admin_password:
            self.errors.append("❌ ADMIN_PASSWORD가 설정되지 않았습니다.")

        # 프로덕션에서 기본 비밀번호 사용 경고
        env = os.getenv("ENVIRONMENT", "development")
        if env == "production":
            weak_passwords = ["admin", "password", "123456", "admin123!", "test"]
            if admin_password in weak_passwords:
                self.errors.append(
                    "❌ 프로덕션 환경에서 약한 ADMIN_PASSWORD를 사용 중입니다!\n"
                    "   반드시 강력한 비밀번호로 변경하세요."
                )


def validate_environment() -> None:
    """
    환경 설정 검증 및 출력

    Raises:
        SystemExit: 필수 설정이 누락되었을 경우
    """
    import sys
    import io

    # Windows 인코딩 문제 해결
    if sys.platform == 'win32':
        try:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        except (AttributeError, io.UnsupportedOperation):
            pass

    validator = EnvironmentValidator()
    is_valid, errors, warnings = validator.validate_all()

    print("\n" + "="*60)
    print("🔍 환경 설정 검증")
    print("="*60)

    # 에러 출력
    if errors:
        print("\n❌ 오류 발견:")
        for error in errors:
            print(f"  {error}")

    # 경고 출력
    if warnings:
        print("\n⚠️  경고:")
        for warning in warnings:
            print(f"  {warning}")

    # 결과
    if is_valid:
        if warnings:
            print("\n✅ 필수 설정은 완료되었으나, 경고 사항을 확인하세요.\n")
        else:
            print("\n✅ 모든 환경 설정이 정상입니다!\n")
    else:
        print("\n❌ 환경 설정 오류로 서버를 시작할 수 없습니다.")
        print("   .env 파일을 확인하고 누락된 설정을 추가하세요.\n")
        print("="*60 + "\n")
        raise SystemExit(1)

    print("="*60 + "\n")
