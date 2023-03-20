from typing import Callable, Optional


def flask_route(
        *args,
        **kwargs
) -> Optional[Callable]:
    """

    """

    def warp(
            func: Optional[Callable]
    ) -> Optional[Callable]:
        setattr(func, 'flask_route_flag', {
            'args': args,
            'kwargs': kwargs,
        })
        return func

    return warp
