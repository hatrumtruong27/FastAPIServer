"""Cover update endpoints — proxy to BedReadDriveSync."""

from __future__ import annotations

import os

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/cover-update", tags=["Drive Sync"])


def _ds_url() -> str:
    return os.environ.get("SERVICE_URLS_BedReadDriveSync", "http://localhost:8003").rstrip("/")


async def _proxy_get(path: str, params: dict | None = None, timeout: float = 60.0) -> JSONResponse:
    import httpx
    url = f"{_ds_url()}{path}"
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(url, params=params or {})
            try:
                resp.raise_for_status()
            except httpx.HTTPStatusError:
                try:
                    detail = resp.json()
                except Exception:
                    detail = {"detail": resp.text or resp.reason_phrase}
                return JSONResponse(status_code=resp.status_code, content=detail)
            return JSONResponse(content=resp.json())
    except Exception as exc:
        return JSONResponse(status_code=502, content={"detail": f"Upstream request failed: {exc}"})


async def _proxy_post(path: str, json_body: dict | None = None) -> JSONResponse:
    import httpx
    url = f"{_ds_url()}{path}"
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(url, json=json_body or {})
            try:
                resp.raise_for_status()
            except httpx.HTTPStatusError:
                try:
                    detail = resp.json()
                except Exception:
                    detail = {"detail": resp.text or resp.reason_phrase}
                return JSONResponse(status_code=resp.status_code, content=detail)
            return JSONResponse(content=resp.json())
    except Exception as exc:
        return JSONResponse(status_code=502, content={"detail": f"Upstream request failed: {exc}"})


@router.get("/check-all")
async def check_all() -> JSONResponse:
    return await _proxy_get("/api/drive-sync/cover-update/check-all", timeout=120.0)


@router.get("/check-updated")
async def check_updated() -> JSONResponse:
    return await _proxy_get("/api/drive-sync/cover-update/check-updated")


@router.post("/upload/{folder_id}/{story_id}")
async def upload_cover(folder_id: str, story_id: str) -> JSONResponse:
    return await _proxy_post(f"/api/drive-sync/cover-update/upload/{folder_id}/{story_id}")
