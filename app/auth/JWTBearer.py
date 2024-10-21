import typing

from fastapi import HTTPException, status
from strawberry.permission import BasePermission
from strawberry.types import Info

from app.graphql.resolvers.users_resolver import getCurrentUser


class IsAuthenticated(BasePermission):
    message = "User is not Authenticated"

    def has_permission(self, source: typing.Any, info: Info, **kwargs) -> bool:
        request = info.context["request"]
        # Access headers authentication
        if "Authorization" not in info.context["request"].headers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not authenticated",
            )

        if (
            info.context["request"].headers["Authorization"].split("Bearer ")[-1]
            is None
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not authenticated",
            )

        authentication = request.headers["Authorization"]
        if authentication:
            token = authentication.split("Bearer ")[-1]
            user = getCurrentUser(token)
            if user:
                return True
        return False
