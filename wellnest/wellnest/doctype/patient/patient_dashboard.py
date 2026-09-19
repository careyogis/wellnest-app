from frappe import _

def get_data():
    return {
        'fieldname': 'patient',
        'transactions': [
            {
                'label': _('Health Records'),
                'items': ['Health Vault']
            }
        ]
    }
