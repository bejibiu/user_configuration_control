from typing import Callable
from aiohttp import web
from aiomongodel.errors import DocumentNotFoundError


def token_auth_middleware(
    check_token: Callable,
    auth_scheme: str = "Token",
    request_property: str = "user",
):
    @web.middleware
    async def middleware(request, handler):
        try:
            scheme, token = request.headers["Authorization"].strip().split(" ")
        except KeyError:
            raise web.HTTPUnauthorized(
                reason="Missing authorization header",
            )
        except ValueError:
            raise web.HTTPForbidden(
                reason="Invalid authorization header",
            )

        if auth_scheme.lower() != scheme.lower():
            raise web.HTTPForbidden(
                reason="Invalid token scheme",
            )
        try:
            user = await check_token(request, token)
        except DocumentNotFoundError:
            raise web.HTTPUnauthorized(reason="Insvalid token")
        except Exception as e:
            raise web.HTTPForbidden()
        if user:
            request[request_property] = user
        else:
            raise web.HTTPForbidden(reason="Token doesn't exist")

        return await handler(request)

    return middleware