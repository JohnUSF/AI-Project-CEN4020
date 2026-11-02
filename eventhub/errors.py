"""Typed domain errors for testable, user-friendly purchase outcomes."""


class EventHubError(Exception):
    code = "invalid_request"
    status = 400

    def __init__(self, message=None):
        super().__init__(message or self.code.replace("_", " "))


class AuthRequired(EventHubError):
    code = "login_required"
    status = 401


class NotFound(EventHubError):
    code = "event_not_found"
    status = 404


class InvalidQuantity(EventHubError):
    code = "invalid_quantity"


class PurchaseLimit(EventHubError):
    code = "purchase_limit"


class SoldOut(EventHubError):
    code = "sold_out"


class UnsupportedCurrency(EventHubError):
    code = "unsupported_currency"


class ConfigurationPending(EventHubError):
    code = "configuration_pending"
    status = 503


class Forbidden(EventHubError):
    code = "forbidden"
    status = 403


class RateLimited(EventHubError):
    """Call 5 (Kenji finding 2): too many purchase requests from one account."""

    code = "rate_limited"
    status = 429

    def __init__(self, retry_after=1):
        self.retry_after = max(1, int(retry_after))
        super().__init__(
            f"Too many purchase requests. Please wait {self.retry_after} seconds and try again."
        )


class InvalidRequestToken(EventHubError):
    """Call 5 (Thuy, double purchase): the form's one-time purchase token is missing or malformed."""

    code = "invalid_request_token"


class DuplicateConflict(EventHubError):
    """The same purchase token was replayed for a different purchase."""

    code = "duplicate_conflict"
    status = 409
