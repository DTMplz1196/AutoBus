"""
Module: singletonmeta.py
Description: A thread-safe Metaclass that ensures only one instance of a class exists.
"""

import threading
from typing import Dict, Any, Type


class SingletonMeta(type):
    """
    Metaclass that ensures only one instance of a class exists.

    This implementation is critical for game automation since it prevents
    conflicts. For example, Controller object(Only one mouse and one game screen)
    and Screen object (Only one handle to the game window).
    """

    # use _ underscore prefix as "private" flag, this Dic is private implementation detail
    _instances: Dict[Type, Any] = {}

    # Thread lock object to prevent race conditions in multi-threaded environments
    # Not needed since my script is procedural, single-threaded where task1(Battle) finishes before task2(Shop)
    # Still keeping it for thread-safe of singleton
    _lock: threading.Lock = threading.Lock()

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        """
        Overrides class instantiation process.

        If the instance does not exist, it acquires a lock to create it safely.
        If it does exist, it returns the cached instance immediately.
        """

        # Fist check, to avoid locking if instance exists
        if cls not in cls._instances:
            # Ensure only one thread can execute creation logic
            with cls._lock:
                # Second check, double check to ensure another thread didn't create while waiting for lock
                if cls not in cls._instances:
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance
        return cls._instances[cls]

