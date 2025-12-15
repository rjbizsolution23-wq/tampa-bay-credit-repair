from typing import List, Dict, Any, Optional
from app.services.audit.violation_detector import violation_detector
from app.services.audit.utilization_analyzer import utilization_analyzer
from app.services.audit.tradeline_analyzer import tradeline_analyzer
from datetime import datetime
import math

RESOLUTION_OPTIONS = [
  { "value": 'GENERAL_DISPUTE', "label": 'General Dispute', "description": 'Standard dispute challenging accuracy of the account' },
  { "value": 'FCRA_VIOLATION', "label": 'FCRA Violation', "description": 'Dispute based on identified FCRA violations' },
  { "value": 'IDENTITY_THEFT', "label": 'Identity Theft', "description": 'Account is result of identity theft/fraud' },
  { "value": 'DEBT_VALIDATION', "label": 'Debt Validation', "description": 'Request full validation of the debt from collector' },
  { "value": 'PAY_FOR_DELETE', "label": 'Pay for Delete', "description": 'Negotiate payment in exchange for removal' },
  { "value": 'GOODWILL_LETTER', "label": 'Goodwill Letter', "description": 'Request removal as a courtesy based on good history' },
  { "value": 'AUTHORIZED_USER_REMOVAL', "label": 'AU Removal', "description": 'Remove yourself as authorized user' },
  { "value": 'SETTLEMENT_NEGOTIATION', "label": 'Settlement', "description": 'Negotiate settlement for less than owed' },
  { "value": 'DO_NOT_DISPUTE', "label": 'Do Not Dispute', "description": 'Keep this account - beneficial for credit history' },
  { "value": 'MONITOR_ONLY', "label": 'Monitor Only', "description": 'No action needed, continue to monitor' }
]

class BlueprintService:
    
    async def run_audit(self, credit_report: object, db_session = None) -> Dict[str, Any]:
        """Run full audit on a credit report"""
        
        # In SQLAlchemy models, relations are attributes. 
        # creditReport.tradelines ...
        
        def get_attr(obj, attr):
             # Handle both dict and object
            if isinstance(obj, dict):
                return obj.get(attr)
            return getattr(obj, attr, None)
        
        tradelines = get_attr(credit_report, 'tradelines') or []
        inquiries = get_attr(credit_report, 'inquiries') or []
        public_records = get_attr(credit_report, 'publicRecords') or []
        
        # Separate by type
        regular_tradelines = [tl for tl in tradelines if str(get_attr(tl, 'accountType')).upper() != 'COLLECTION']
        collections = [tl for tl in tradelines if str(get_attr(tl, 'accountType')).upper() == 'COLLECTION']
        
        # Run analyses
        violation_results = self.analyze_violations(tradelines, collections)
        utilization_results = utilization_analyzer.analyze_utilization(regular_tradelines)
        tradeline_results = tradeline_analyzer.analyze_tradelines(regular_tradelines)
        
        # Build items for review
        items_for_review = self.build_items_for_review(
            tradelines,
            collections,
            inquiries,
            public_records,
            violation_results
        )
        
        # Generate recommendations
        recommendations = self.generate_recommendations(
            utilization_results,
            tradeline_results,
            collections,
            violation_results
        )
        
        # Check AU issues
        has_au_issues = False
        for a in utilization_results['accounts']:
            if a['isAuthorizedUser'] and a['utilization'] > 20:
                has_au_issues = True
                break
        
        return {
            "scores": {
                "transunion": get_attr(credit_report, 'transunionScore'),
                "equifax": get_attr(credit_report, 'equifaxScore'),
                "experian": get_attr(credit_report, 'experianScore')
            },
            "summary": {
                "totalViolationsFound": violation_results['total'],
                "totalNegativeItems": tradeline_results['totalNegative'],
                "totalCollections": len(collections),
                "totalInquiries": len(inquiries),
                "positiveTradelineCount": tradeline_results['totalPositive'],
                "utilizationPercentage": utilization_results['overallUtilization'],
                "amountToReach20Percent": utilization_results['amountToReach20Percent'],
                "needsStarterAccounts": tradeline_results['needsStarterAccounts'],
                "hasAuthorizedUserIssues": has_au_issues
            },
            "violationAnalysis": violation_results,
            "utilizationAnalysis": utilization_results,
            "tradelineAnalysis": tradeline_results,
            "itemsForReview": items_for_review,
            "recommendations": recommendations
        }

    def analyze_violations(self, tradelines: List[object], collections: List[object]):
        all_violations = []
        by_bureau = {
            "transunion": [],
            "equifax": [],
            "experian": []
        }
        
        def get_attr(obj, attr):
            if isinstance(obj, dict):
                return obj.get(attr)
            return getattr(obj, attr, None)
        
        # Analyze tradelines
        for tl in tradelines:
            violations = violation_detector.analyze_tradeline(tl, tradelines)
            all_violations.extend(violations)
            
            bureau = str(get_attr(tl, 'bureau') or 'TRANSUNION').lower()
            if bureau in by_bureau:
                by_bureau[bureau].extend(violations)
                
        # Analyze collections
        for coll in collections:
            violations = violation_detector.analyze_collection(coll)
            all_violations.extend(violations)
            
            bureau = str(get_attr(coll, 'bureau') or 'TRANSUNION').lower()
            if bureau in by_bureau:
                by_bureau[bureau].extend(violations)
                
        return {
            "violations": all_violations,
            "total": len(all_violations),
            "byBureau": by_bureau
        }

    def build_items_for_review(self, 
                               tradelines: List[object], 
                               collections: List[object], 
                               inquiries: List[object], 
                               public_records: List[object],
                               violation_results: Any) -> List[Dict]:
        items = []
        now = datetime.now()
        
        def get_attr(obj, attr):
            if isinstance(obj, dict):
                return obj.get(attr)
            return getattr(obj, attr, None)
            
        def months_between(d1, d2):
            return (d2.year - d1.year) * 12 + d2.month - d1.month
            
        # Process negative tradelines
        for tl in tradelines:
            is_neg = get_attr(tl, 'isNegative')
            account_type = str(get_attr(tl, 'accountType')).upper()
            
            # Simple check for negative indicators if flag not set, but assume flag is set by parser
            
            if not is_neg and account_type != 'COLLECTION':
                continue
                
            violations = violation_detector.analyze_tradeline(tl, tradelines)
            
            opened_raw = get_attr(tl, 'dateOpened')
            account_age = 0
            if opened_raw:
                opened = opened_raw if isinstance(opened_raw, datetime) else datetime.fromisoformat(str(opened_raw))
                account_age = months_between(opened, now)
                
            suggested_resolution = 'GENERAL_DISPUTE'
            do_not_dispute_warning = None
            
            if len(violations) > 0:
                suggested_resolution = 'FCRA_VIOLATION'
            
            if account_age > 120:
                do_not_dispute_warning = '⚠️ This is a very old account. Removing it may lower your average account age significantly.'
            
            items.append({
                "id": get_attr(tl, 'id'),
                "itemType": 'TRADELINE',
                "creditorName": get_attr(tl, 'creditorName'),
                "accountNumber": get_attr(tl, 'accountNumber'),
                "bureau": get_attr(tl, 'bureau'),
                "accountType": get_attr(tl, 'accountType'),
                "currentBalance": float(get_attr(tl, 'currentBalance') or 0),
                "creditLimit": float(get_attr(tl, 'creditLimit') or 0),
                "accountAge": account_age,
                "isAuthorizedUser": False, # Basic assumption
                "isNegative": is_neg,
                "negativeReason": get_attr(tl, 'negativeReason'),
                "detectedViolations": violations,
                "violationCount": len(violations),
                "suggestedResolution": suggested_resolution,
                "resolutionOptions": RESOLUTION_OPTIONS,
                "doNotDisputeWarning": do_not_dispute_warning,
                "priorityLevel": 5 if len(violations) > 0 else 3
            })
            
        # Process collections
        for coll in collections:
            violations = violation_detector.analyze_collection(coll)
            balance = float(get_attr(coll, 'currentBalance') or 0)
            estimated_settlement = round(balance * 0.35) if balance > 0 else 0
            
            suggested_resolution = 'DEBT_VALIDATION'
            if len(violations) > 0:
                suggested_resolution = 'FCRA_VIOLATION'
            
            items.append({
                "id": get_attr(coll, 'id'),
                "itemType": 'COLLECTION',
                "creditorName": get_attr(coll, 'creditorName'),
                "accountNumber": get_attr(coll, 'accountNumber'),
                "bureau": get_attr(coll, 'bureau'),
                "currentBalance": balance,
                "isAuthorizedUser": False,
                "isNegative": True,
                "negativeReason": 'Collection Account',
                "detectedViolations": violations,
                "violationCount": len(violations),
                "isSettleable": True,
                "originalCreditor": get_attr(coll, 'originalCreditor') or get_attr(coll, 'creditorName'), # Fallback
                "estimatedSettlement": estimated_settlement,
                "suggestedResolution": suggested_resolution,
                "resolutionOptions": RESOLUTION_OPTIONS,
                "priorityLevel": 4
            })
            
        # Process Hard Inquiries (assumed filter)
        for inq in inquiries:
            if str(get_attr(inq, 'inquiryType')).upper() != 'HARD':
                continue
                
            items.append({
                "id": get_attr(inq, 'id'),
                "itemType": 'INQUIRY',
                "creditorName": get_attr(inq, 'creditorName'),
                "accountNumber": 'N/A',
                "bureau": get_attr(inq, 'bureau'),
                "isAuthorizedUser": False,
                "isNegative": True,
                "negativeReason": 'Hard Inquiry',
                "detectedViolations": [],
                "violationCount": 0,
                "suggestedResolution": 'GENERAL_DISPUTE',
                "resolutionOptions": [
                    { "value": 'GENERAL_DISPUTE', "label": 'Dispute Inquiry', "description": 'Challenge unauthorized inquiry' },
                    { "value": 'DO_NOT_DISPUTE', "label": 'Do Not Dispute', "description": 'This was an authorized inquiry' }
                ],
                "priorityLevel": 1
            })
            
        # Process Public Records
        for pr in public_records:
            violations = []
            filing_date_raw = get_attr(pr, 'filingDate')
            
            if filing_date_raw:
                filing_date = filing_date_raw if isinstance(filing_date_raw, datetime) else datetime.fromisoformat(str(filing_date_raw))
                years_ago = (now - filing_date).days / 365
                record_type = str(get_attr(pr, 'recordType')).upper()
                
                if 'BANKRUPTCY' in record_type and years_ago > 10:
                     violations.append({
                         "violation": { "title": "Obsolete Bankruptcy", "description": "Older than 10 years" },
                         "evidence": f"Filed {int(years_ago)} years ago"
                     })
                elif years_ago > 7 and 'BANKRUPTCY' not in record_type:
                     violations.append({
                         "violation": { "title": "Obsolete Public Record", "description": "Older than 7 years" },
                         "evidence": f"Filed {int(years_ago)} years ago"
                     })

            items.append({
                "id": get_attr(pr, 'id'),
                "itemType": 'PUBLIC_RECORD',
                "creditorName": get_attr(pr, 'courtName') or 'Public Record',
                "accountNumber": get_attr(pr, 'caseNumber') or 'N/A',
                "bureau": get_attr(pr, 'bureau'),
                "currentBalance": float(get_attr(pr, 'amount') or 0),
                "isAuthorizedUser": False,
                "isNegative": True,
                "negativeReason": get_attr(pr, 'recordType'),
                "detectedViolations": violations,
                "violationCount": len(violations),
                "suggestedResolution": 'FCRA_VIOLATION' if len(violations) > 0 else 'GENERAL_DISPUTE',
                "resolutionOptions": RESOLUTION_OPTIONS,
                "priorityLevel": 5
            })
            
        items.sort(key=lambda x: x['priorityLevel'], reverse=True)
        return items

    def generate_recommendations(self, 
                                 utilization: Dict, 
                                 tradelines: Dict, 
                                 collections: List[object], 
                                 violations: Dict) -> List[Dict]:
        
        recommendations = []
        
        # Add generated recommendations from sub-analyzers
        for rec in utilization.get('recommendations', []):
            rec['category'] = 'UTILIZATION'
            rec['action'] = "See suggestion" # Fallback
            recommendations.append(rec)
            
        for rec in tradelines.get('recommendations', []):
            # category already set in tradeline analyzer
            rec['action'] = "See suggestion"
            recommendations.append(rec)
            
        # Collections Recs
        col_balance = sum([float(getattr(c, 'currentBalance', 0) or 0) for c in collections]) # Basic getattr if object
        if len(collections) > 0:
            recommendations.append({
                "category": 'COLLECTIONS',
                "priority": 3,
                "title": f"Address {len(collections)} Collection Account(s)",
                "description": f"You have {len(collections)} collection(s) totaling ${col_balance}. These may be settleable for 30-50% of the balance.",
                "action": 'Send debt validation letters, then negotiate pay-for-delete if valid',
                "estimatedImpact": '+50-100 points when removed'
            })
            
        # Violation Recs
        if violations['total'] > 0:
            recommendations.append({
                "category": 'DISPUTE',
                "priority": 1,
                "title": f"{violations['total']} FCRA Violation(s) Detected",
                "description": 'Multiple FCRA violations were detected. These provide strong grounds for dispute.',
                "action": 'File disputes citing specific FCRA violations',
                "estimatedImpact": 'High probability of removal'
            })
            
        recommendations.sort(key=lambda x: x['priority'])
        return recommendations

run_blueprint_audit = BlueprintService().run_audit
# Alias for compatibility with route import usage if needed, or expose class instance
blueprint_service = BlueprintService()
