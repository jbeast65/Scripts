import os
from typing import Optional
from dotenv import load_dotenv

# Load .env if present
load_dotenv()


class Settings:
	# Core app settings
	APP_NAME: str = os.getenv("APP_NAME", "Whisper Local API")
	APP_ENV: str = os.getenv("APP_ENV", "development")
	API_PREFIX: str = os.getenv("API_PREFIX", "")
	SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-change-me")
	ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))
	ALGORITHM: str = os.getenv("ALGORITHM", "HS256")

	# CORS
	CORS_ALLOW_ORIGINS: str = os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
	CORS_ALLOW_CREDENTIALS: bool = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
	CORS_ALLOW_METHODS: str = os.getenv("CORS_ALLOW_METHODS", "*")
	CORS_ALLOW_HEADERS: str = os.getenv("CORS_ALLOW_HEADERS", "*")

	# Google OAuth
	GOOGLE_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")
	GOOGLE_CLIENT_SECRET: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET")
	OAUTH_REDIRECT_URI: str = os.getenv("OAUTH_REDIRECT_URI", "http://localhost:8000/auth/callback")

	# Whisper model settings
	MODEL_NAME: str = os.getenv("MODEL_NAME", "tiny")
	DEVICE: str = os.getenv("DEVICE", "cpu")  # cpu or cuda
	COMPUTE_TYPE: str = os.getenv("COMPUTE_TYPE", "int8")  # float16, int8, int8_float16, etc.

	# File upload limits
	MAX_UPLOAD_MB: int = int(os.getenv("MAX_UPLOAD_MB", "100"))

	# Session
	SESSION_COOKIE_NAME: str = os.getenv("SESSION_COOKIE_NAME", "session")

	def cors_origins(self) -> list[str]:
		return [o.strip() for o in self.CORS_ALLOW_ORIGINS.split(",") if o.strip()]


settings = Settings()