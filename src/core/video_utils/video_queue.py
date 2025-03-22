import threading
from collections import deque
from typing import Optional, Any


class VideoQueue:
    """
    A class-level (singleton-like) thread-safe queue for storing video frames.
    Automatically discards the oldest frame if maxlen is reached.
    """

    _queue = deque()
    _instance = None
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
    def enqueue(cls, frame: Any) -> None:
        """
        Enqueue a frame. If deque has a maxlen and is full, the oldest
        frame is automatically discarded by deque.

        Args:
            frame (Any): The video frame to add.
        """
        with cls._lock:
            cls._queue.append(frame)

    @classmethod
    def dequeue(cls) -> Optional[Any]:
        """
        Dequeue and returns the oldest frame or None if empty.

        Returns:
            The first frame if available, or None if the queue is empty.
        """
        with cls._lock:
            return cls._queue.popleft() if cls._queue else None

    @classmethod
    def peek(cls) -> Optional[Any]:
        """
        Returns the oldest frame without removing it, or None if empty.

        Returns:
            The first frame if available, or None if the queue is empty.
        """
        with cls._lock:
            return cls._queue[0] if cls._queue else None

    @classmethod
    def is_empty(cls) -> bool:
        """
        Checks if the queue is empty.

        Returns:
            True if the queue is empty, otherwise False.
        """
        with cls._lock:
            return len(cls._queue) == 0

    @classmethod
    def size(cls) -> int:
        """
        Returns the number of frames in the queue.

        Returns:
            An integer count of frames in the queue.
        """
        with cls._lock:
            return len(cls._queue)

    @classmethod
    def get(cls):
        """
        Returns all frames in the queue.

        Returns:
            A list of all frames in the queue.
        """
        with cls._lock:
            return list(cls._queue)

    @classmethod
    def clear(cls) -> None:
        """
        Clears all frames from the queue.
        """
        with cls._lock:
            cls._queue.clear()
