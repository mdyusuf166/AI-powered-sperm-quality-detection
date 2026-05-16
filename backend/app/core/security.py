from fastapi import Depends, HTTPException, Request, status

from app.core.config import Settings, get_settings


def require_api_key(
    request: Request,
    settings: Settings = Depends(get_settings),
) -> None:
    """Require X-API-Key only when API_KEY is configured.

    Local research deployments often start without auth. Production deployments
    should set API_KEY or replace this dependency with OAuth/OIDC.
    """

    if not settings.api_key:
        return

    supplied_key = request.headers.get("X-API-Key")
    if supplied_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key.",
        )

