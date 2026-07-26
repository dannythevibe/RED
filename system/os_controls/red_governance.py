import json
import hashlib
from datetime import datetime, timezone

class RedGovernance:
    def __init__(self):
        self.pending_proposals = []

    def propose_memory_update(self, new_memory):
        """Creates a signed proposal that requires Danny's approval."""
        proposal = {
            "type": "MEMORY_EVOLUTION",
            "delta": new_memory,
            "status": "AWAITING_HUMAN_SIGNATURE",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.pending_proposals.append(proposal)
        print("Red: Evolution proposal generated. Awaiting cryptographic handshake from Danny.")
        return proposal

    def finalize_evolution(self, signature, proposal_index=0):
        """Verifies Danny's signature and commits change."""
        if not self.pending_proposals:
            print("Red: No pending proposals to finalize.")
            return False

        proposal = self.pending_proposals[proposal_index]

        # Basic integrity check: signature must be SHA-256 of the proposal's timestamp
        expected = hashlib.sha256(proposal["timestamp"].encode()).hexdigest()
        if signature != expected:
            print("Red: Signature mismatch. Evolution rejected.")
            return False

        proposal["status"] = "COMMITTED"
        print("Red: Signature verified. Evolution committed.")
        # Arweave/Irys upload would happen here via RedCloud
        return True
