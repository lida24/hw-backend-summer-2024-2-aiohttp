from aiohttp.web_exceptions import HTTPForbidden
from aiohttp_apispec import request_schema, response_schema, docs
from aiohttp_session import new_session

from app.admin.schemes import AdminSchema
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


class AdminLoginView(View):
    @docs(tags=["admin"], summary="Login for admin")
    @request_schema(AdminSchema)
    @response_schema(AdminSchema)
    async def post(self):
        email = self.data["email"]
        password = self.data["password"]
        admin = await self.store.admins.get_by_email(email)
        if not admin or not admin.is_password_valid(password):
            raise HTTPForbidden(
                reason="Admin with such email or password doesn't exists"
            )
        raw_admin = AdminSchema().dump(admin)
        session = await new_session(request=self.request)
        session["admin"] = raw_admin
        return json_response(data=raw_admin)


class AdminCurrentView(AuthRequiredMixin, View):
    @docs(tags=["admin"], summary="Check current admin")
    @response_schema(AdminSchema)
    async def get(self):
        return json_response(data=AdminSchema().dump(self.request.admin))
