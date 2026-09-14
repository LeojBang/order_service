from abc import ABC, abstractmethod


class InboxRepository(ABC):

    @abstractmethod
    async def exists(self, event_id: str) -> bool:
        pass

    @abstractmethod
    async def add(self, event_id: str, event_type: str) -> None:
        pass
