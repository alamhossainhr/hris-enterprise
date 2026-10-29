class BusinessLogicError(Exception):
    """Base exception for all domain and service-layer business rule violations."""
    pass


class DynamicTableError(BusinessLogicError):
    """Raised when dynamic table validation, creation, or resolution fails."""
    pass


class PeriodLockedError(BusinessLogicError):
    """Raised when an operation is attempted on a locked period."""
    pass