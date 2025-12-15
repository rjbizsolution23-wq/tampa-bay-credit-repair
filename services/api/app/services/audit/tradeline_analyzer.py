from typing import List, Dict, Any, Optional
from datetime import datetime
from dateutil.relativedelta import relativedelta
import re
import math

STARTER_PRODUCTS = {
  "securedCards": [
    {
      "name": 'Chime Secured Credit Builder',
      "url": 'https://www.chime.com/credit-builder/?affiliate=RickJeffersonSolutions',
      "description": 'No credit check, no annual fee, reports to all 3 bureaus'
    },
    {
      "name": 'OpenSky Secured Visa',
      "url": 'https://www.openskycc.com/?affiliate=RickJeffersonSolutions',
      "description": 'No credit check required, $200 minimum deposit'
    },
    {
      "name": 'Discover it Secured',
      "url": 'https://www.discover.com/credit-cards/secured/?affiliate=RickJeffersonSolutions',
      "description": 'Earn cashback, automatic reviews for graduation'
    }
  ],
  "creditBuilderLoans": [
    {
      "name": 'Self Credit Builder',
      "url": 'https://www.self.inc/?affiliate=RickJeffersonSolutions',
      "description": 'Credit builder loan, reports to all 3 bureaus'
    },
    {
      "name": 'MoneyLion Credit Builder Plus',
      "url": 'https://www.moneylion.com/?affiliate=RickJeffersonSolutions',
      "description": 'Credit builder membership with 0% APR loan'
    }
  ],
  "rentalReporting": [
    {
      "name": 'Boom Pay',
      "url": 'https://www.boompay.app/?affiliate=RickJeffersonSolutions',
      "description": 'Report rent payments to all 3 bureaus'
    },
    {
      "name": 'Rental Kharma',
      "url": 'https://www.rentalkharma.com/?affiliate=RickJeffersonSolutions',
      "description": 'Add up to 24 months of rent history'
    },
    {
      "name": 'LevelCredit',
      "url": 'https://www.levelcredit.com/?affiliate=RickJeffersonSolutions',
      "description": 'Report rent, utilities, and subscriptions'
    }
  ]
}

class TradelineAnalyzer:
    def analyze_tradelines(self, tradelines: List[object]) -> Dict[str, Any]:
        """Analyze tradelines for positive accounts and make recommendations"""
        
        def get_attr(obj, attr):
            if isinstance(obj, dict):
                return obj.get(attr)
            return getattr(obj, attr, None)
            
        now = datetime.now()
        positive_accounts = []
        warning_accounts = []
        recommendations = []
        
        total_positive = 0
        total_negative = 0
        oldest_account_age = 0
        total_age = 0
        accounts_with_age = 0
        
        # Calculate months between dates
        def months_between(d1, d2):
            return (d2.year - d1.year) * 12 + d2.month - d1.month
        
        # Find oldest account first
        for tl in tradelines:
            opened_raw = get_attr(tl, 'dateOpened')
            if opened_raw:
                opened = opened_raw if isinstance(opened_raw, datetime) else datetime.fromisoformat(str(opened_raw))
                age_months = months_between(opened, now)
                if age_months > oldest_account_age:
                    oldest_account_age = age_months
        
        # Helper to check negative
        def has_negative_indicators(tl):
            status = str(get_attr(tl, 'accountStatus') or '').upper()
            neg_statuses = ['COLLECTION', 'CHARGE_OFF', 'CHARGEOFF', 'DELINQUENT', 'REPOSSESSION', 'FORECLOSURE', 'BANKRUPTCY']
            return any(ns in status for ns in neg_statuses)
            
        def has_late_payments(tl):
            history = str(get_attr(tl, 'paymentHistory') or '')
            return bool(re.search(r'[1-5]', history))
            
        def get_latest_late_payment_age(tl):
            history = str(get_attr(tl, 'paymentHistory') or '')
            # Assuming history is latest first
            match = re.search(r'[1-5]', history)
            if match:
                return match.start() # Index as approx months ago
            return None

        # Analyze each tradeline
        for tl in tradelines:
            is_negative_attr = get_attr(tl, 'isNegative')
            is_negative = is_negative_attr if is_negative_attr is not None else has_negative_indicators(tl)
            
            if is_negative:
                total_negative += 1
            else:
                total_positive += 1
                
                account_age = 0
                opened_raw = get_attr(tl, 'dateOpened')
                if opened_raw:
                    opened = opened_raw if isinstance(opened_raw, datetime) else datetime.fromisoformat(str(opened_raw))
                    account_age = months_between(opened, now)
                    total_age += account_age
                    accounts_with_age += 1
                
                has_lates = has_late_payments(tl)
                late_payment_age = None
                if has_lates:
                    late_payment_age = get_latest_late_payment_age(tl)
                
                is_oldest = (account_age == oldest_account_age) and (account_age > 0)
                
                recommendation = 'Keep this account in good standing.'
                creditor_name = get_attr(tl, 'creditorName') or "Unknown"
                account_number = get_attr(tl, 'accountNumber') or ""
                
                if is_oldest and has_lates:
                    if late_payment_age and late_payment_age > 60:
                        recommendation = '⚠️ CAUTION: This is your oldest tradeline. The late payment is old. Consider sending a goodwill letter instead of disputing.'
                        warning_accounts.append({
                            "creditorName": creditor_name,
                            "accountNumber": account_number,
                            "warning": f"Oldest tradeline ({math.floor(account_age / 12)} years) with late payment from {math.floor(late_payment_age / 12)} years ago",
                            "recommendation": 'Send goodwill letter - do NOT dispute to avoid losing account history'
                        })
                    else:
                        recommendation = '⚠️ This is your oldest tradeline with a recent late payment. Weigh the benefit of disputing vs. keeping the account age.'
                elif is_oldest:
                     recommendation = '✅ This is your oldest account - it helps your average account age. Keep it open!'
                
                positive_accounts.append({
                    "creditorName": creditor_name,
                    "accountNumber": account_number,
                    "accountAge": account_age,
                    "creditLimit": float(get_attr(tl, 'creditLimit') or 0),
                    "hasLatePayments": has_lates,
                    "latePaymentAge": late_payment_age,
                    "isOldestAccount": is_oldest,
                    "recommendation": recommendation
                })

        average_account_age = round(total_age / accounts_with_age) if accounts_with_age > 0 else 0
        needs_starter_accounts = total_positive < 3
        needs_rental_tradelines = total_positive < 3
        
        if needs_starter_accounts:
            recommendations.append({
                "category": 'TRADELINES', # Mapped from type in TS
                "type": 'SECURED_CARD',
                "title": 'Open a Secured Credit Card',
                "description": f"You only have {total_positive} positive tradeline(s). Opening a secured credit card will help build positive history.",
                "productName": STARTER_PRODUCTS['securedCards'][0]['name'],
                "productUrl": STARTER_PRODUCTS['securedCards'][0]['url'],
                "estimatedImpact": '+15-30 points over 3-6 months',
                "priority": 1
            })
            recommendations.append({
                "category": 'TRADELINES',
                "type": 'CREDIT_BUILDER',
                "title": 'Open a Credit Builder Loan',
                "description": 'A credit builder loan adds installment account diversity to your credit mix.',
                "productName": STARTER_PRODUCTS['creditBuilderLoans'][0]['name'],
                "productUrl": STARTER_PRODUCTS['creditBuilderLoans'][0]['url'],
                "estimatedImpact": '+10-20 points over 6-12 months',
                "priority": 2
            })
            
        if needs_rental_tradelines:
             recommendations.append({
                "category": 'TRADELINES',
                "type": 'RENTAL_TRADELINE',
                "title": 'Add Your Rent Payments',
                "description": 'If you pay rent, you can add up to 24 months of payment history to your credit report.',
                "productName": STARTER_PRODUCTS['rentalReporting'][0]['name'],
                "productUrl": STARTER_PRODUCTS['rentalReporting'][0]['url'],
                "estimatedImpact": '+20-40 points with 24 months of history',
                "priority": 1
            })
            
        # Sort positive accounts by age descending
        positive_accounts.sort(key=lambda x: x['accountAge'], reverse=True)
        
        return {
            "totalPositive": total_positive,
            "totalNegative": total_negative,
            "needsStarterAccounts": needs_starter_accounts,
            "needsRentalTradelines": needs_rental_tradelines,
            "oldestAccountAge": oldest_account_age,
            "averageAccountAge": average_account_age,
            "recommendations": recommendations,
            "positiveAccounts": positive_accounts,
            "warningAccounts": warning_accounts
        }

tradeline_analyzer = TradelineAnalyzer()
