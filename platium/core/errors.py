class PlatiumError(Exception):
    pass

class ValidationError(PlatiumError):
    pass

class ScannerError(PlatiumError):
    pass

class NetworkError(PlatiumError):
    pass

class APILimitError(PlatiumError):
    pass
