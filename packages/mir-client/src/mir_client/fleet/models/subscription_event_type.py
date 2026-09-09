from enum import StrEnum


class SubscriptionEventType(StrEnum):
    ALERT = "Alert"
    ERROR = "Error"
    GROUP = "Group"
    PAYLOAD = "Payload"
    RESOURCE = "Resource"
    ROBOTIDENTITY = "RobotIdentity"
    ROBOTRUNTIME = "RobotRuntime"
    ROBOTSTATE = "RobotState"
    SERIALORDERSTATUS = "SerialOrderStatus"
    SITE = "Site"
    SUBSCRIPTION = "Subscription"
    SYSTEM = "System"
    TOPMODULE = "TopModule"
    USERPROMPT = "UserPrompt"
    USERPROMPTRESOLVED = "UserPromptResolved"

    def __str__(self) -> str:
        return str(self.value)
