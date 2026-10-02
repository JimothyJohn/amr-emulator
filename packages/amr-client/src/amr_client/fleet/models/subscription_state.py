from enum import StrEnum


class SubscriptionState(StrEnum):
    SUBSCRIBED = "Subscribed"
    UNSUBSCRIBED = "Unsubscribed"

    def __str__(self) -> str:
        return str(self.value)
