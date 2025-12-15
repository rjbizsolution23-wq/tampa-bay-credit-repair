from typing import List, Dict, Any, Optional
import math

class UtilizationAnalyzer:
    def analyze_utilization(self, tradelines: List[object]) -> Dict[str, Any]:
        """Analyze all revolving accounts for utilization"""
        
        def get_attr(obj, attr):
            if isinstance(obj, dict):
                return obj.get(attr)
            return getattr(obj, attr, None)

        # Filter to revolving accounts only
        revolving_accounts = []
        for tl in tradelines:
            t_type = str(get_attr(tl, 'accountType')).upper()
            t_limit = get_attr(tl, 'creditLimit')
            if 'REVOLVING' in t_type or 'CREDIT_CARD' in t_type or (t_limit and float(t_limit) > 0):
                 if t_limit and float(t_limit) > 0: # Ensure limit exists
                    revolving_accounts.append(tl)

        total_balance = 0.0
        total_credit_limit = 0.0
        accounts = []
        recommendations = []

        for account in revolving_accounts:
            balance = float(get_attr(account, 'currentBalance') or 0)
            limit = float(get_attr(account, 'creditLimit') or 0)
            
            if limit > 0:
                total_balance += balance
                total_credit_limit += limit
                
                utilization = round((balance / limit) * 100)
                amount_to_reach_20 = balance - (limit * 0.20)
                
                ownership = str(get_attr(account, 'accountOwnership')).upper()
                is_au = 'AUTHORIZED_USER' in ownership or 'AUTHORIZED USER' in ownership
                
                # Determine priority based on utilization and balance
                priority = 'LOW'
                if utilization > 50 or (is_au and utilization > 30):
                    priority = 'HIGH'
                elif utilization > 30:
                    priority = 'MEDIUM'
                
                # Generate recommendation for this account
                recommendation = ''
                creditor_name = get_attr(account, 'creditorName') or "Unknown Creditor"
                
                if is_au and utilization > 20:
                    recommendation = f"Remove yourself as authorized user to eliminate {utilization}% utilization impact"
                    recommendations.append({
                        "type": 'REMOVE_AU',
                        "account": creditor_name,
                        "description": f"Remove AU status from {creditor_name} - Currently at {utilization}% utilization",
                        "estimatedScoreImpact": '+10-30 points',
                        "priority": 1
                    })
                elif utilization > 30:
                    pay_amount = math.ceil(amount_to_reach_20)
                    recommendation = f"Pay down ${pay_amount} to reach 20% utilization"
                    recommendations.append({
                        "type": 'PAY_DOWN',
                        "account": creditor_name,
                        "amount": max(0, pay_amount),
                        "description": f"Pay {creditor_name} down by ${pay_amount} to reach 20%",
                        "estimatedScoreImpact": '+20-40 points' if utilization > 50 else '+10-20 points',
                        "priority": 1 if utilization > 50 else 2
                    })
                elif utilization > 10:
                    recommendation = 'Good utilization. Consider paying to under 10% for optimal score.'
                else:
                    recommendation = 'Excellent utilization! Keep it under 10%.'
                
                accounts.append({
                    "creditorName": creditor_name,
                    "accountNumber": get_attr(account, 'accountNumber'),
                    "balance": balance,
                    "creditLimit": limit,
                    "utilization": utilization,
                    "isAuthorizedUser": is_au,
                    "amountToReach20": max(0, math.ceil(amount_to_reach_20)),
                    "priority": priority,
                    "recommendation": recommendation
                })

        # Calculate overall metrics
        overall_utilization = round((total_balance / total_credit_limit) * 100) if total_credit_limit > 0 else 0
        
        amount_to_reach_30 = total_balance - (total_credit_limit * 0.30)
        amount_to_reach_20 = total_balance - (total_credit_limit * 0.20)
        amount_to_reach_10 = total_balance - (total_credit_limit * 0.10)
        amount_to_reach_optimal = total_balance - (total_credit_limit * 0.09)

        # Add overall recommendation if needed
        if overall_utilization > 30:
             recommendations.insert(0, {
                "type": 'PAY_DOWN',
                "amount": math.ceil(amount_to_reach_20),
                "description": f"Pay down ${math.ceil(amount_to_reach_20)} total across accounts to reach 20% overall utilization",
                "estimatedScoreImpact": '+30-50 points' if overall_utilization > 50 else '+15-30 points',
                "priority": 0
            })
        
        # Sort recommendations by priority (ascending, so 0 then 1 then 2)
        recommendations.sort(key=lambda x: x['priority'])
        
        # Sort accounts
        def account_sort_key(a):
            prio_map = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
            return (prio_map.get(a['priority'], 2), -a['utilization'])
        
        accounts.sort(key=account_sort_key)

        return {
            "totalBalance": total_balance,
            "totalCreditLimit": total_credit_limit,
            "overallUtilization": overall_utilization,
            "amountToReach30Percent": max(0, math.ceil(amount_to_reach_30)),
            "amountToReach20Percent": max(0, math.ceil(amount_to_reach_20)),
            "amountToReach10Percent": max(0, math.ceil(amount_to_reach_10)),
            "amountToReachOptimal": max(0, math.ceil(amount_to_reach_optimal)),
            "accounts": accounts,
            "recommendations": recommendations
        }

utilization_analyzer = UtilizationAnalyzer()
