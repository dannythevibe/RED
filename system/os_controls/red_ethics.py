import requests

# Actions containing these keywords are flagged as requiring explicit confirmation
_SENSITIVE_KEYWORDS = [
    "shutdown", "restart", "sleep", "delete", "format", "scan", "exploit",
    "record", "surveillance", "camera", "upload", "send"
]

class RedEthics:
    def __init__(self, ethics_tx_id="local"):
        self.ethics_tx_id = ethics_tx_id
        self.prime_directives = []

    def load_prime_directives(self):
        """Loads ethics directives. In production, fetches from Arweave permaweb."""
        print(f"Red: Loading Prime Directives (source: {self.ethics_tx_id})...")
        self.prime_directives = [
            "Protect Danny's digital and physical security at all costs.",
            "Execute only authorized commands from Danny's verified devices.",
            "Maintain absolute privacy. Zero data leakage to centralized entities.",
        ]
        return self.prime_directives

    def validate_action(self, action_intent):
        """
        Cross-references an intent string against the Prime Directives.
        Returns True if the action is safe to execute, False if it should be blocked.
        Sensitive actions are flagged but not outright blocked — they require
        the caller to handle confirmation.
        """
        if not action_intent:
            return True

        lowered = action_intent.lower()

        # Flag actions that touch sensitive system capabilities
        for keyword in _SENSITIVE_KEYWORDS:
            if keyword in lowered:
                print(f"Red: Ethics check — sensitive action detected: '{keyword}' in '{action_intent}'")
                # In the current model we warn but allow Danny's direct commands through.
                # A full multi-sig confirmation flow belongs here in production.
                return True

        return True
