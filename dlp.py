import re
from schemas import SecurityViolation

_PATTERNS = [
    ("ARGENTINE_DNI", re.compile(r"\b(\d{1,2}\.?\d{3}\.?\d{3})\b")),
    ("CREDIT_CARD",   re.compile(
        r"\b(?:4[0-9]{12}(?:[0-9]{3})?"
        r"|5[1-5][0-9]{14}"
        r"|3[47][0-9]{13}"
        r"|(?:\d{4}[- ]){3}\d{4})\b"
    )),
    ("EMAIL",     re.compile(r"\b[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}\b")),
    ("CUIL_CUIT", re.compile(r"\b(20|23|24|27|30|33|34)-?\d{8}-?\d\b")),
    ("AR_PHONE",  re.compile(
        r"(?:\+54\s?9?\s?)?(?:\(?0?11\)?|\(?0?2\d{2,3}\)?)[\s\-]?\d{4}[\s\-]?\d{4}\b"
    )),
]

def _luhn_check(number: str) -> bool:
    digits = [int(d) for d in re.sub(r"\D", "", number)]
    if len(digits) < 13:
        return False
    digits.reverse()
    total = 0
    for i, d in enumerate(digits):
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0

def _redact(value: str) -> str:
    if "@" in value:
        local, domain = value.split("@", 1)
        return local[:2] + "***@" + domain[:2] + "***"
    clean = re.sub(r"\D", "", value)
    if len(clean) >= 6:
        return clean[:2] + "*" * (len(clean) - 4) + clean[-2:]
    return "****"

class PIIDetector:
    def scan(self, text: str) -> list[SecurityViolation]:
        violations = []
        for pii_type, pattern in _PATTERNS:
            for raw_match in pattern.findall(text):
                match_str = raw_match if isinstance(raw_match, str) else raw_match[0]
                if pii_type == "CREDIT_CARD" and not _luhn_check(match_str):
                    continue
                violations.append(SecurityViolation(
                    type=pii_type,
                    redacted_value=_redact(match_str)
                ))
        return violations