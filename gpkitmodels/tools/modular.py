"""Base classes for modular physical modeling.

This module provides a foundation for modular physical modeling by separating:
1. Physical components (with fixed properties)
2. Performance models (which analyze components in specific conditions)

This separation enables:
- Independent definition of physical components
- Analysis of components in different contexts
- Composition of components into larger systems
- Swapping different performance models for the same component
"""

from gpkit import Model


class PhysicalComponent(Model):
    """Base class for physical components with fixed properties.

    A physical component represents a real-world object with fixed properties
    that don't change during operation (e.g., empty mass, dimensions, material
    properties).  These properties are used by performance models to analyze
    the component's behavior under different conditions.

    Example: A rocket stage with fixed empty mass, dimensions, and material
    properties.  These properties don't change during flight, but are used to
    analyze the stage's performance under different conditions (e.g., different
    propellant loads).
    """

    def setup(self):
        """This method should be overridden by subclasses to define the
        component's physical properties Variables and Constraints."""
        pass


class PerformanceModel(Model):
    """Base class for analyzing components in specific conditions.

    A performance model takes a physical component and analyzes its behavior
    under specific conditions (e.g., flight state, mission phase).  It uses the
    component's fixed properties along with the current state to compute
    performance metrics.

    Subclasses should override setup() to define their specific performance analysis
    using gpkit Variables and constraints. The setup method can take any keyword
    arguments needed for the analysis.
    """

    def setup(self, **kwargs):
        """Return constraints on performance

        Args:
            **kwargs: Model-specific parameters needed for performance analysis.
                     Common parameters include:
                     - component: A PhysicalComponent instance
                     - state: A Model instance representing operational state
                     - Other parameters specific to the performance model

        This method should be overridden by subclasses to define the
        performance analysis using gpkit Variables and constraints.
        """
        pass
