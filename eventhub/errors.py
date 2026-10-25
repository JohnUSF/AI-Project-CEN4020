"""Typed domain errors for testable, user-friendly purchase outcomes."""

class EventHubError(Exception):
    code = 'invalid_request'
    status = 400

    def __init__(self, message=None):
        super().__init__(message or self.code.replace('_', ' '))


class AuthRequired(EventHubError):
    code = 'login_required'
    status = 401


class NotFound(EventHubError):
    code = 'event_not_found'
    status = 404


class InvalidQuantity(EventHubError):
    code = 'invalid_quantity'


class PurchaseLimit(EventHubError):
    code = 'purchase_limit'


class SoldOut(EventHubError):
    code = 'sold_out'


class UnsupportedCurrency(EventHubError):
    code = 'unsupported_currency'


class ConfigurationPending(EventHubError):
    code = 'configuration_pending'
    status = 503


class Forbidden(EventHubError):
    code = 'forbidden'
    status = 403
