import threading
from collections import deque
from typing import Optional, Any


class VideoQueue:
    """
    A class-level (singleton-like) thread-safe queue for storing video frames.
    Automatically discards the oldest frame if maxlen is reached.
    """
    _queue = deque()
    _lock = threading.Lock()
    _max_size: Optional[int] = None

    @classmethod
    def configure(cls, max_size: Optional[int] = None) -> None:
        """
        Configures a maximum size for the shared queue.
        
        Args:
            max_size (Optional[int]): Maximum number of frames to store.
            If None, the queue grows dynamically. If set and the queue
            is full, the oldest frame is removed.
        """
        cls._max_size = max_size

    @classmethod
    def enqueue(self, frame: Any) -> None:
        """
        Enqueue a frame. If deque has a maxlen and is full, the oldest
        frame is automatically discarded by deque.

        Args:
            frame (Any): The video frame to add.
        """
        with self.lock:
            self.queue.append(frame)

    @classmethod
    def dequeue(self) -> Optional[Any]:
        """
        Dequeue and returns the oldest frame or None if empty.

        Returns:
            The first frame if available, or None if the queue is empty.
        """
        with self.lock:
            return self.queue.popleft() if self.queue else None

    @classmethod
    def peek(self) -> Optional[Any]:
        """
        Returns the oldest frame without removing it, or None if empty.

        Returns:
            The first frame if available, or None if the queue is empty.
        """
        with self.lock:
            return self.queue[0] if self.queue else None

    @classmethod
    def is_empty(self) -> bool:
        """
        Checks if the queue is empty.

        Returns:
            True if the queue is empty, otherwise False.
        """
        with self.lock:
            return len(self.queue) == 0
        
    @classmethod
    def size(self) -> int:
        """
        Returns the number of frames in the queue.

        Returns:
            An integer count of frames in the queue.
        """
        with self.lock:
            return len(self.queue)

    @classmethod
    def clear(self) -> None:
        """
        Clears all frames from the queue.
        """
        with self.lock:
            self.queue.clear()
