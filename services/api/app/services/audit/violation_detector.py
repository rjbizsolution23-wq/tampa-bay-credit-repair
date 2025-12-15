from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class DetectedViolation:
    def __init__(self, violation: Dict[str, Any], evidence: str, field: str, bureau_reported_value: Any, expected_value: Optional[Any] = None):
        self.violation = violation
        self.evidence = evidence
        self.field = field
        self.bureauReportedValue = bureau_reported_value
        self.expectedValue = expected_value

    def to_dict(self):
        return {
            "violation": self.violation,
            "evidence": self.evidence,
            "field": self.field,
            "bureauReportedValue": self.bureauReportedValue,
            "expectedValue": self.expectedValue
        }

FCRA_VIOLATIONS = [
    # Section 1681e(b) - Accuracy Requirements
    {
        "code": "FCRA-1681e-01",
        "section": "1681e(b)",
        "title": "Inaccurate Balance Reporting",
        "description": "Balance reported does not match actual account balance. CRAs must follow reasonable procedures to assure maximum possible accuracy.",
        "severity": "MEDIUM"
    },
    {
        "code": "FCRA-1681e-02",
        "section": "1681e(b)",
        "title": "Incorrect Account Status",
        "description": "Account status (open/closed) is reported incorrectly.",
        "severity": "MEDIUM"
    },
    {
        "code": "FCRA-1681e-03",
        "section": "1681e(b)",
        "title": "Wrong Payment History",
        "description": "Payment history contains inaccurate late payment notations.",
        "severity": "HIGH"
    },
    {
        "code": "FCRA-1681e-04",
        "section": "1681e(b)",
        "title": "Incorrect Date of First Delinquency",
        "description": "The date of first delinquency is reported incorrectly, affecting the 7-year reporting period.",
        "severity": "HIGH"
    },
    {
        "code": "FCRA-1681e-05",
        "section": "1681e(b)",
        "title": "Duplicate Account Reporting",
        "description": "Same account appears multiple times on credit report.",
        "severity": "HIGH"
    },
    
    # Section 1681c - Obsolete Information
    {
        "code": "FCRA-1681c-01",
        "section": "1681c(a)",
        "title": "Obsolete Negative Information",
        "description": "Negative information older than 7 years is still being reported (10 years for bankruptcy).",
        "severity": "CRITICAL"
    },
    {
        "code": "FCRA-1681c-02",
        "section": "1681c(a)(2)",
        "title": "Obsolete Judgment",
        "description": "Civil judgment older than 7 years or the governing statute of limitations (whichever is longer) is still being reported.",
        "severity": "CRITICAL"
    },
    {
        "code": "FCRA-1681c-03",
        "section": "1681c(a)(5)",
        "title": "Obsolete Collection Account",
        "description": "Collection account older than 7 years from date of first delinquency is still being reported.",
        "severity": "CRITICAL"
    },
    
    # Section 1681s-2 - Furnisher Responsibilities
    {
        "code": "FCRA-1681s2-01",
        "section": "1681s-2(a)",
        "title": "Reporting Without Investigation",
        "description": "Furnisher continued reporting disputed information without conducting a reasonable investigation.",
        "severity": "HIGH"
    },
    {
        "code": "FCRA-1681s2-02",
        "section": "1681s-2(b)",
        "title": "Failure to Update After Investigation",
        "description": "Furnisher failed to update or delete inaccurate information after investigation.",
        "severity": "HIGH"
    },
    
    # Metro 2 Format Violations
    {
        "code": "METRO2-01",
        "section": "Metro 2 Format",
        "title": "Missing Required Fields",
        "description": "Account is missing required Metro 2 fields (Account Type, Account Status, etc.).",
        "severity": "MEDIUM"
    },
    {
        "code": "METRO2-03",
        "section": "Metro 2 Format",
        "title": "Inconsistent Reporting Across Bureaus",
        "description": "Account information is reported differently across the three credit bureaus.",
        "severity": "MEDIUM"
    },
    
    # Collection-Specific Violations
    {
        "code": "FDCPA-01",
        "section": "FDCPA + FCRA",
        "title": "Re-aging of Debt",
        "description": "Collection account date of first delinquency has been illegally re-aged to extend reporting period.",
        "severity": "CRITICAL"
    },
]

class ViolationDetector:
    
    def analyze_tradeline(self, tradeline: object, all_tradelines: List[object]) -> List[Dict]:
        """Analyze a tradeline for FCRA violations (expecting SQLAlchemy models or dicts)"""
        violations = []
        
        # Helper to get attribute safely
        def get_attr(obj, attr):
            if isinstance(obj, dict):
                return obj.get(attr)
            return getattr(obj, attr, None)

        tl_id = get_attr(tradeline, 'id')
        tl_creditor = get_attr(tradeline, 'creditorName') or ""
        tl_account_num = get_attr(tradeline, 'accountNumber') or ""
        tl_dofd = get_attr(tradeline, 'dateOfFirstDelinquency')
        tl_date_opened = get_attr(tradeline, 'dateOpened')
        tl_balance = get_attr(tradeline, 'currentBalance')
        tl_limit = get_attr(tradeline, 'creditLimit')
        tl_status = get_attr(tradeline, 'accountStatus')
        tl_type = get_attr(tradeline, 'accountType')
        tl_is_negative = get_attr(tradeline, 'isNegative')

        # Check for obsolete information (7-year rule)
        if tl_is_negative and tl_dofd:
            dofd = tl_dofd if isinstance(tl_dofd, datetime) else datetime.fromisoformat(str(tl_dofd))
            seven_years_ago = datetime.now() - relativedelta(years=7)
            
            if dofd < seven_years_ago:
                v = next((v for v in FCRA_VIOLATIONS if v["code"] == "FCRA-1681c-01"), None)
                if v:
                    violations.append(DetectedViolation(
                        violation=v,
                        evidence=f"Date of first delinquency ({dofd.strftime('%Y-%m-%d')}) is more than 7 years old",
                        field="dateOfFirstDelinquency",
                        bureau_reported_value=dofd.strftime('%Y-%m-%d'),
                        expected_value="Should be removed from report"
                    ).to_dict())

        # Check for duplicate accounts
        # Note: This checks against 'all_tradelines' list
        duplicates = [
            tl for tl in all_tradelines 
            if get_attr(tl, 'id') != tl_id and
            str(get_attr(tl, 'creditorName')).lower() == str(tl_creditor).lower() and
            str(get_attr(tl, 'accountNumber')) == str(tl_account_num)
        ]
        
        if len(duplicates) > 0:
            v = next((v for v in FCRA_VIOLATIONS if v["code"] == "FCRA-1681e-05"), None)
            if v:
                violations.append(DetectedViolation(
                    violation=v,
                    evidence=f"Account appears {len(duplicates) + 1} times on credit report",
                    field="accountNumber",
                    bureau_reported_value=tl_account_num,
                    expected_value="Should appear only once"
                ).to_dict())

        # Check for invalid/missing required fields
        if not tl_date_opened:
            v = next((v for v in FCRA_VIOLATIONS if v["code"] == "METRO2-01"), None)
            if v:
                violations.append(DetectedViolation(
                    violation=v,
                    evidence="Date Opened field is missing",
                    field="dateOpened",
                    bureau_reported_value=None,
                    expected_value="Valid date required"
                ).to_dict())

        # Check for balance inconsistencies
        if tl_balance and tl_limit:
            # Convert decimal to float for comparison if needed
            balance = float(tl_balance)
            limit = float(tl_limit)
            if limit > 0 and balance > limit * 1.5:
                v = next((v for v in FCRA_VIOLATIONS if v["code"] == "FCRA-1681e-01"), None)
                if v:
                    violations.append(DetectedViolation(
                        violation=v,
                        evidence=f"Balance (${balance}) exceeds credit limit (${limit}) by more than 50%",
                        field="currentBalance",
                        bureau_reported_value=balance,
                        expected_value="Should not significantly exceed credit limit"
                    ).to_dict())

        # Check account status consistency
        if tl_status == 'CLOSED' and tl_balance and float(tl_balance) > 0 and tl_type != 'COLLECTION':
            v = next((v for v in FCRA_VIOLATIONS if v["code"] == "FCRA-1681e-02"), None)
            if v:
                violations.append(DetectedViolation(
                    violation=v,
                    evidence=f"Account marked as CLOSED but shows balance of ${tl_balance}",
                    field="accountStatus",
                    bureau_reported_value="CLOSED with balance",
                    expected_value="Status or balance may be incorrect"
                ).to_dict())

        return violations

    def analyze_collection(self, collection: object) -> List[Dict]:
        """Analyze a collection account for violations"""
        violations = []
        
        def get_attr(obj, attr):
            if isinstance(obj, dict):
                return obj.get(attr)
            return getattr(obj, attr, None)

        col_dofd = get_attr(collection, 'dateOfFirstDelinquency')
        col_date_opened = get_attr(collection, 'dateOpened')
        col_orig_creditor = get_attr(collection, 'originalCreditor') # Assuming field exists or mapped
        # Note: 'originalCreditor' wasn't in the Tradeline model explicitly in the schema before, 
        # but User code implies it exists or is mapped from raw remarks?
        # The new 'AuditItem' has 'originalCreditor'. The 'Tradeline' model has 'remarks'.
        # We'll assume the object passed in might have it or we skip if missing.
        
        # Check for obsolete collection (7-year rule from DOFD)
        if col_dofd:
            dofd = col_dofd if isinstance(col_dofd, datetime) else datetime.fromisoformat(str(col_dofd))
            seven_years_ago = datetime.now() - relativedelta(years=7)
            
            if dofd < seven_years_ago:
                v = next((v for v in FCRA_VIOLATIONS if v["code"] == "FCRA-1681c-03"), None)
                if v:
                    violations.append(DetectedViolation(
                        violation=v,
                        evidence=f"Collection DOFD ({dofd.strftime('%Y-%m-%d')}) is more than 7 years old",
                        field="dateOfFirstDelinquency",
                        bureau_reported_value=dofd.strftime('%Y-%m-%d'),
                        expected_value="Should be removed from report"
                    ).to_dict())

        # Check for re-aging (collection date newer than original DOFD)
        if col_date_opened and col_dofd:
            opened = col_date_opened if isinstance(col_date_opened, datetime) else datetime.fromisoformat(str(col_date_opened))
            dofd = col_dofd if isinstance(col_dofd, datetime) else datetime.fromisoformat(str(col_dofd))
            
            if opened < dofd:
                v = next((v for v in FCRA_VIOLATIONS if v["code"] == "FDCPA-01"), None)
                if v:
                    violations.append(DetectedViolation(
                        violation=v,
                        evidence=f"Collection open date ({opened.strftime('%Y-%m-%d')}) is before DOFD ({dofd.strftime('%Y-%m-%d')})",
                        field="dateOpened",
                        bureau_reported_value=opened.strftime('%Y-%m-%d'),
                        expected_value="Open date should be after original DOFD"
                    ).to_dict())

        return violations

violation_detector = ViolationDetector()
