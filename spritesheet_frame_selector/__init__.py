"""SpriteSheet Frame Selector addon package."""

def register() -> None:
    from .registration import register as register_addon

    register_addon()


def unregister() -> None:
    from .registration import unregister as unregister_addon

    unregister_addon()

__all__ = ("register", "unregister")
