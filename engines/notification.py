

from __future__ import annotations

from engines.base import BaseEngine
from provider.notification.base import NotificationMessage, NotificationAdapterBase


class NotificationEngine(BaseEngine):
    engine_name = "notification"

    def send(self, channel: str, message: NotificationMessage):
        if not self.registry:
            raise RuntimeError("NotificationEngine requires registry")

        adapter: NotificationAdapterBase = self.registry.get_provider(
            capability="notification",
            name=channel,
        )

        return adapter.send(message)
