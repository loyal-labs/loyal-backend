class HTTPError(Exception):
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message

    def __str__(self):
        return f"HTTPError: {self.status} {self.message}"
