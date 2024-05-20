import typing
from strawberry.types import Info
from strawberry.permission import BasePermission
from app.graphql.resolvers.users_resolver import getCurrentUser

class IsAuthenticated(BasePermission):
    message = "User is not Authenticated"

    def has_permission(self, source: typing.Any, info: Info, **kwargs) -> bool:
        request = info.context["request"]
        # Access headers authentication
        authentication = request.headers["Authorization"]
        if authentication:
            token = authentication.split("Bearer ")[-1]
            user = getCurrentUser(token)
            if user:
                return True
        return False