from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import aiohttp


@dataclass(frozen=True)
class BackendClient:
    base_url: str
    internal_token: str

    def _headers(self) -> dict[str, str]:
        return {"X-Internal-Token": self.internal_token}

    async def list_applications(
        self,
        status: str,
        limit: int = 20,
        offset: int = 0,
    ) -> list[dict[str, Any]]:

        status = status.lower()
        url = f"{self.base_url}/api/internal/admin/applications"
        params = {"status": status, "limit": limit, "offset": offset}

        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                headers=self._headers(),
                params=params,
            ) as resp:
                resp.raise_for_status()
                return await resp.json()

    async def get_application(
        self,
        application_id: int,
    ) -> dict[str, Any]:

        url = f"{self.base_url}/api/internal/admin/applications/{application_id}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self._headers()) as resp:
                resp.raise_for_status()
                return await resp.json()

    async def set_status(
        self,
        application_id: int,
        status: str,
    ) -> dict[str, Any]:

        status = status.lower()
        url = f"{self.base_url}/api/internal/admin/applications/{application_id}/status"

        async with aiohttp.ClientSession() as session:
            async with session.patch(
                url, headers=self._headers(), json={"status": status}
            ) as resp:
                resp.raise_for_status()
                return await resp.json()

    async def get_employer(self, tg_user_id: int) -> dict:

        url = f"{self.base_url}/api/internal/employers/by-tg/{tg_user_id}"

        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                headers=self._headers(),
            ) as resp:
                if resp.status == 404:
                    return {"is_hr": False}

                resp.raise_for_status()
                return await resp.json()

    async def create_invite(
        self,
        tg_user_id: int,
        role: str = "RECRUITER",
    ) -> dict[str, Any]:

        url = f"{self.base_url}/api/internal/invites/create"

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                headers=self._headers(),
                json={"tg_user_id": tg_user_id, "role": role},
            ) as resp:
                resp.raise_for_status()
                return await resp.json()

    async def join_invite(
        self,
        tg_user_id: int,
        token: str,
    ) -> dict[str, Any]:

        url = f"{self.base_url}/api/internal/invites/join"

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                headers=self._headers(),
                json={"tg_user_id": tg_user_id, "token": token},
            ) as resp:
                resp.raise_for_status()
                return await resp.json()
