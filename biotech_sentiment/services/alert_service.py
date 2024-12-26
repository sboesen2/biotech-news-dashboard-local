class AlertService:
    def __init__(self):
        self.thresholds = {
            'price_change': 0.05,
            'trial_update': True,
            'patent_filing': True,
            'management_change': True
        }
        
    def check_alerts(self, company_id):
        """Check if any alert conditions are met"""
        updates = self.get_company_updates(company_id)
        return self.evaluate_alert_conditions(updates) 