import httpx
from config import config

import logging


class AuthService:
    def __init__(self):
        self.base_url = config.AUTH_SERVICE_URL
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)

    async def validate_token(self, token: str) -> bool:
        """Kiểm tra token với Auth Service"""
        try:
            # Sửa lại URL endpoint cho phù hợp với API Gateway
            url = f"{self.base_url}/auth/validate-token"  # Bỏ /api/v1 vì đã được định nghĩa trong API Gateway
            self.logger.debug(f"Validating token at URL: {url}")

            async with httpx.AsyncClient(verify=True) as client:  # Thêm verify=True vì dùng HTTPS
                response = await client.post(
                    url,
                    headers={"Authorization": f"Bearer {token}"}
                )
                self.logger.debug(f"Response status: {response.status_code}")
                return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Error validating token: {str(e)}")
            return Fals