

from __future__ import annotations

from engines.base import BaseEngine
from providers.notification.base import NotificationMessage, NotificationProviderProtocol


class NotificationEngine(BaseEngine):
    engine_name = "notification"

    def send(self, channel: str, message: NotificationMessage):
        if not self.registry:
            raise RuntimeError("NotificationEngine requires registry")

        provider: NotificationProviderProtocol = self.registry.get_provider(
            capability="notification",
            name=channel,
        )

        return provider.send(message)
