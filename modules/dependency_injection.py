"""
Dependency Injection system for the Eternia project.

This module provides a simple dependency injection container that allows
components to be registered and retrieved, reducing tight coupling between
modules and making the system more modular and testable.
"""

from typing import Any, Callable, Dict, Optional, Type, TypeVar, cast

T = TypeVar('T')


class DependencyContainer:
    """
    A simple dependency injection container.
    
    This container allows components to be registered and retrieved by their type
    or by a string key. It supports registering instances, factories, and singletons.
    """
    
    def __init__(self):
        """Initialize an empty dependency container."""
        self._instances: Dict[str, Any] = {}
        self._factories: Dict[str, Callable[[], Any]] = {}
        self._singletons: Dict[str, Any] = {}
    
    def register_instance(self, key: str, instance: Any) -> None:
        """
        Register an instance with the container.
        
        Args:
            key: The key to register the instance under
            instance: The instance to register
        """
        self._instances[key] = instance
    
    def register_factory(self, key: str, factory: Callable[[], Any]) -> None:
        """
        Register a factory function with the container.
        
        Args:
            key: The key to register the factory under
            factory: A callable that creates a new instance when called
        """
        self._factories[key] = factory
    
    def register_singleton(self, key: str, factory: Callable[[], Any]) -> None:
        """
        Register a singleton factory with the container.
        
        The factory will be called only once, and the same instance will be
        returned for all subsequent requests.
        
        Args:
            key: The key to register the singleton under
            factory: A callable that creates the singleton instance when called
        """
        self._factories[key] = factory
    
    def get(self, key: str) -> Any:
        """
        Get a component from the container.
        
        Args:
            key: The key of the component to retrieve
            
        Returns:
            The requested component
            
        Raises:
            KeyError: If the key is not registered with the container
        """
        # Check if it's a registered instance
        if key in self._instances:
            return self._instances[key]
        
        # Check if it's a singleton that has already been created
        if key in self._singletons:
            return self._singletons[key]
        
        # Check if it's a factory or singleton factory
        if key in self._factories:
            instance = self._factories[key]()
            
            # If it's a singleton factory, store the instance
            if key in self._factories and key not in self._instances:
                self._singletons[key] = instance
            
            return instance
        
        raise KeyError(f"No component registered for key: {key}")
    
    def get_typed(self, key: str, expected_type: Type[T]) -> T:
        """
        Get a component from the container with type checking.
        
        Args:
            key: The key of the component to retrieve
            expected_type: The expected type of the component
            
        Returns:
            The requested component, cast to the expected type
            
        Raises:
            KeyError: If the key is not registered with the container
            TypeError: If the component is not of the expected type
        """
        instance = self.get(key)
        
        if not isinstance(instance, expected_type):
            raise TypeError(
                f"Component for key '{key}' is of type {type(instance).__name__}, "
                f"not {expected_type.__name__}"
            )
        
        return cast(T, instance)


# Create a global container instance for convenience
container = DependencyContainer()


def get_container() -> DependencyContainer:
    """
    Get the global dependency container.
    
    Returns:
        The global DependencyContainer instance
    """
    return container