"""
Python Event Bus implementation
Equivalent to Google Guava EventBus used in Java version
"""
import asyncio
import logging
from typing import Dict, List, Callable, Any, Type
from collections import defaultdict
from inspect import iscoroutinefunction

logger = logging.getLogger(__name__)


class EventBus:
    """
    Simple event bus implementation
    Python equivalent of Google Guava EventBus
    """
    
    def __init__(self, name: str = "EventBus"):
        self.name = name
        self._subscribers: Dict[Type, List[Callable]] = defaultdict(list)
        self._async_subscribers: Dict[Type, List[Callable]] = defaultdict(list)
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    def register(self, subscriber: Any):
        """
        Register an object's methods as event handlers
        Looks for methods decorated with @subscribe
        """
        for method_name in dir(subscriber):
            method = getattr(subscriber, method_name)
            if hasattr(method, '_event_subscriber_info'):
                event_type = method._event_subscriber_info['event_type']
                if iscoroutinefunction(method):
                    self._async_subscribers[event_type].append(method)
                    self.logger.info(f"Registered async subscriber: {subscriber.__class__.__name__}.{method_name} for {event_type.__name__}")
                else:
                    self._subscribers[event_type].append(method)
                    self.logger.info(f"Registered subscriber: {subscriber.__class__.__name__}.{method_name} for {event_type.__name__}")
    
    def unregister(self, subscriber: Any):
        """Unregister an object's event handlers"""
        for method_name in dir(subscriber):
            method = getattr(subscriber, method_name)
            if hasattr(method, '_event_subscriber_info'):
                event_type = method._event_subscriber_info['event_type']
                if method in self._subscribers[event_type]:
                    self._subscribers[event_type].remove(method)
                if method in self._async_subscribers[event_type]:
                    self._async_subscribers[event_type].remove(method)
    
    def post(self, event: Any):
        """
        Post an event to all registered synchronous subscribers
        """
        event_type = type(event)
        subscribers = self._subscribers.get(event_type, [])
        
        self.logger.debug(f"Posting {event_type.__name__} to {len(subscribers)} subscribers")
        
        for subscriber in subscribers:
            try:
                subscriber(event)
            except Exception as e:
                self.logger.error(f"Error in subscriber {subscriber}: {e}", exc_info=True)
    
    async def post_async(self, event: Any):
        """
        Post an event to all registered subscribers (both sync and async)
        """
        event_type = type(event)
        sync_subscribers = self._subscribers.get(event_type, [])
        async_subscribers = self._async_subscribers.get(event_type, [])
        
        total_subscribers = len(sync_subscribers) + len(async_subscribers)
        self.logger.debug(f"Posting {event_type.__name__} to {total_subscribers} subscribers")
        
        # Handle synchronous subscribers
        for subscriber in sync_subscribers:
            try:
                subscriber(event)
            except Exception as e:
                self.logger.error(f"Error in sync subscriber {subscriber}: {e}", exc_info=True)
        
        # Handle asynchronous subscribers
        if async_subscribers:
            tasks = []
            for subscriber in async_subscribers:
                try:
                    tasks.append(asyncio.create_task(subscriber(event)))
                except Exception as e:
                    self.logger.error(f"Error creating task for async subscriber {subscriber}: {e}", exc_info=True)
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)


def subscribe(event_type: Type):
    """
    Decorator to mark a method as an event subscriber
    Python equivalent of @Subscribe annotation in Java
    """
    def decorator(func):
        func._event_subscriber_info = {
            'event_type': event_type
        }
        return func
    return decorator


# Global event bus instance (equivalent to Spring Bean)
_global_event_bus: EventBus = None

def get_event_bus() -> EventBus:
    """Get the global event bus instance"""
    global _global_event_bus
    if _global_event_bus is None:
        _global_event_bus = EventBus("EthereumEventBus")
    return _global_event_bus