class CycleError(Exception):
    """Base class so the router can map domain errors to HTTP responses."""


class FutureStartDateError(CycleError):
    pass


class DuplicateCycleError(CycleError):
    pass


class CycleOutOfOrderError(CycleError):
    pass


class CycleTooCloseError(CycleError):
    pass


class NothingToUndoError(CycleError):
    pass
