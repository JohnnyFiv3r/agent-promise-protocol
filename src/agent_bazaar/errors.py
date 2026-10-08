class ProtocolError(ValueError):
    """A typed failed protocol guard, never permission to drop a requirement."""

    def __init__(self, code: str, detail: str = ""):
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}" if detail else code)
