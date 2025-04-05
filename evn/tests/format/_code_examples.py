############################## test spacing unchanged ###############################
@dataclass
class FormatHistory:
    """Tracks original and formatted code for all files being processed."""
    buffers: dict[str, dict[str, str]] = field(default_factory=dict)

    def add(self, filename: str, original_code: str):
        """Initialize a new file in history with its original code."""
        self.buffers[filename] = {"original": original_code}

    def update(self, filename: str, new_code: str):
        """Update the formatted code for a given file."""
        self.buffers[filename]["formatted"] = new_code

    def get_original(self, filename: str) -> str:
        """Retrieve the original code."""
        return self.buffers[filename]["original"]

    def get_formatted(self, filename: str) -> str:
        """Retrieve the formatted code."""
        return self.buffers[filename]["formatted"]

############################## test oneline spaces ###############################
with open('/tmp/test.txt'):     pass
#----------------------------- ↑ original ↓ formatted ----------------------------
with open('/tmp/test.txt'): pass
################################################################################


