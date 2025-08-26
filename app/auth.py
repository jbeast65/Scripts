from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from jose import jwt
from authlib.integrations.starlette_client import OAuth

from .config import settings
from .schemas import User
from .deps import get_current_user


oauth = OAuth()
oauth.register(
	name="google",
	server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
	client_id=settings.GOOGLE_CLIENT_ID,
	client_secret=settings.GOOGLE_CLIENT_SECRET,
	client_kwargs={"scope": "openid email profile"},
)


router = APIRouter()


@router.get("/login/google")
async def login_via_google(request: Request):
	if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
		raise HTTPException(status_code=500, detail="Google OAuth is not configured")
	redirect_uri = settings.OAUTH_REDIRECT_URI
	return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/auth/callback")
async def auth_callback(request: Request):
	if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
		raise HTTPException(status_code=500, detail="Google OAuth is not configured")
	token = await oauth.google.authorize_access_token(request)
	# Extract ID token claims
	id_token = token.get("id_token")
	if not id_token:
		raise HTTPException(status_code=400, detail="Missing id_token from Google")
	claims = await oauth.google.parse_id_token(request, token)
	# Build our JWT
	expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
	exp = datetime.now(tz=timezone.utc) + expires_delta
	payload = {
		"sub": claims.get("sub"),
		"email": claims.get("email"),
		"name": claims.get("name"),
		"picture": claims.get("picture"),
		"exp": int(exp.timestamp()),
	}
	access_token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
	response = RedirectResponse(url="/auth/success")
	# Secure cookie in production with secure/httponly/samesite
	response.set_cookie(
		key="access_token",
		value=access_token,
		http_only=True,
		secure=False if settings.APP_ENV == "development" else True,
		samesite="lax",
		max_age=int(expires_delta.total_seconds()),
	)
	return response


@router.get("/auth/success", response_class=HTMLResponse)
async def auth_success():
	# Simple page to indicate success. In a real app you would redirect to your UI.
	html = """
	<!DOCTYPE html>
	<html><head><title>Login Successful</title></head>
	<body>
		<h2>Login successful</h2>
		<p>Your session cookie has been set. You can now call protected endpoints.</p>
	</body></html>
	"""
	return HTMLResponse(content=html)


@router.post("/logout")
async def logout(response: Response):
	response = JSONResponse({"detail": "Logged out"})
	response.delete_cookie("access_token")
	return response


@router.get("/me")
async def me(user: User = Depends(get_current_user)):
	return user