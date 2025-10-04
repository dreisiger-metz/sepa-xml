import datetime

# Example `Config` definition --- customise to suit
Config = {
    "SEPAProfile": {
        "first": {
            "msg_id": f"MSGID-PREFIX--{datetime.datetime.today().strftime('%Y%m%d-%H%M%S')}",
            "name": "Organisation Name",
            "IBAN": "DE09500103000092761290",
            "BIC": "FCBKDEFFXXX",
            "batch": True,
            "creditor_id": "DE6000000000000000",
            "currency": "EUR"
        },
        "second": {
            "msg_id": f"MSGID-SECOND-PREFIX--{datetime.datetime.today().strftime('%Y%m%d-%H%M%S')}",
            "name": "Organisation Name",
            "IBAN": "DE09500103000092761290",
            "BIC": "FCBKDEFFXXX",
            "batch": True,
            "creditor_id": "DE6000000000000000",
            "currency": "EUR"
        }
    },
    "Payment": { 
        "Description": "Zahlung für {args.for_period} - Herzlichen Dank"
    }
}
