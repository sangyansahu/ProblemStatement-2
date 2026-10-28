from typing import Protocol, NamedTuple
import hashlib


class IdentityCheck(NamedTuple):
    status: str  # pending, verified, failed, unavailable
    reference: str
    reason: str


class ApaarProvider(Protocol):
    def verify(self, apaar_id: str) -> IdentityCheck:
        """Verify an APAAR identifier against identity authority."""
        ...


class MockApaarProvider:
    """Deterministic Mock Provider for synthetic APAAR testing.
    All data is SYNTHETIC. All APAAR checks are simulated.
    """

    TIMEOUT_DEMO_ID = "DEMO-TIMEOUT-9999"

    def verify(self, apaar_id: str) -> IdentityCheck:
        raw = str(apaar_id or "").strip().upper()

        if not raw:
            return IdentityCheck(
                status="failed",
                reference="MOCK-ERR-EMPTY",
                reason="APAAR identifier is missing or empty"
            )

        # Simulated Timeout test ID (A timeout = 'unavailable', never 'failed' or 'verified')
        if raw == self.TIMEOUT_DEMO_ID:
            return IdentityCheck(
                status="unavailable",
                reference="MOCK-TIMEOUT",
                reason="Provider connection timed out; marked unavailable"
            )

        # Synthetic DEMO- identifiers
        if raw.startswith("DEMO-"):
            if "INVALID" in raw or "FAIL" in raw:
                return IdentityCheck(
                    status="failed",
                    reference="MOCK-FAIL-001",
                    reason="Synthetic ID marked for rejection"
                )
            # Deterministic hash reference
            ref_hash = hashlib.sha256(raw.encode()).hexdigest()[:12].upper()
            return IdentityCheck(
                status="verified",
                reference=f"MOCK-APAAR-{ref_hash}",
                reason="Synthetic identifier verified in simulation sandbox"
            )

        # Numeric 12-digit simulated IDs
        if raw.isdigit() and len(raw) == 12:
            ref_hash = hashlib.sha256(raw.encode()).hexdigest()[:12].upper()
            return IdentityCheck(
                status="verified",
                reference=f"MOCK-APAAR-{ref_hash}",
                reason="Numeric identifier verified in simulation sandbox"
            )

        return IdentityCheck(
            status="failed",
            reference="MOCK-FORMAT-ERR",
            reason="Identifier failed format check"
        )


class OfficialApaarProvider:
    """Official National APAAR / ABC Identity Verification Provider Adapter.
    Unimplemented stub as per specification: do NOT invent real external government endpoints.
    """

    def verify(self, apaar_id: str) -> IdentityCheck:
        raise NotImplementedError(
            "OfficialApaarProvider is an unimplemented production stub. "
            "Use MockApaarProvider for the prototype and testing."
        )
