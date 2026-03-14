from abc import ABC, abstractmethod

class Node[T](ABC):
    @abstractmethod
    def get_node_data(self) -> T:
        """Return the primary data of type T."""
        pass

    @abstractmethod
    def update_node_data(self, new_data: T) -> None:
        """Update the state using type T."""
        pass