import threading
import collections
from typing import Optional, Any

# This class uses 

class VideoQueue:
    def __init__(self, max_size: Optional[int] = None):
        """
        Initializes the VideoQueue class.

        Args:
            max_size (Optional[int]): Maximum number of frames to store.
            If None, the queue grows dynamically.
            If set and the queue is full, the oldest
            frame will be removed to make room.
        """
        self.queue = collections.deque()
        self.max_size = max_size
        self.lock = threading.Lock()

    def enqueue(self, frame: Any) -> None:
        """
        Adds a frame to the queue.
        If max_size is set and the queue is full, the oldest frame is dropped.

        Args:
            frame (Any): The video frame to add.
        """
        with self.lock:
            if self.max_size is not None and len(self.queue) >= self.max_size:
                # Remove the oldest frame if the queue has a max size and is full
                self.dequeue()
            self.queue.append(frame)

    def dequeue(self) -> Optional[Any]:
        """
        Removes and returns the first frame from the queue.

        Returns:
            The first frame if available, or None if the queue is empty.
        """
        with self.lock:
            if not self.queue:
                return None
            return self.queue.popleft()

    def peek(self) -> Optional[Any]:
        """
        Returns the first frame without removing it.

        Returns:
            The first frame if available, or None if the queue is empty.
        """
        with self.lock:
            if not self.queue:
                return None
            return self.queue[0]

    def is_empty(self) -> bool:
        """
        Checks if the queue is empty.

        Returns:
            True if the queue is empty, otherwise False.
        """
        with self.lock:
            return len(self.queue) == 0

    def size(self) -> int:
        """
        Returns the number of frames in the queue.

        Returns:
            An integer count of frames in the queue.
        """
        with self.lock:
            return len(self.queue)

    def clear(self) -> None:
        """
        Clears all frames from the queue.
        """
        with self.lock:
            self.queue.clear()
