from aiohttp.abc import StreamResponse
from aiohttp.web_exceptions import HTTPUnauthorized
from aiohttp_session import get_session


class AuthRequiredMixin:
    async def _iter(self) -> StreamResponse:
        session = await get_session(self.request)
        if session.new:
            raise HTTPUnauthorized(reason="The user is not authorized")
        return await super()._iter()
