#!/usr/bin/env python3
#
# Example usage:
#   ./csv-convert-to-sepa-xml.py --profile first --for-period OCT-2025 \
#        input-file.csv output-file.xml
import argparse
import csv
import datetime

from sepapy import SepaDebit


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




if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--profile", type=str, required=True, help=f"the SEPA profile to use", choices=list(Config['SEPAProfile'].keys()))
    parser.add_argument("--for-period", type=str, help="the MMM-YYYY to which these transactions belong", default=datetime.date.today().strftime("%b-%Y").upper())
    parser.add_argument("--collection-date", type=str, help="when the transactions should fall due", default=datetime.date.today().strftime("%Y-%m-%d"))
    parser.add_argument("--description", type=str, help="the transactions' descriptions", default=Config['Payment']['Description'])
    parser.add_argument("-v", "--verbosity", action="count", help="increase output verbosity", default=0)
    parser.add_argument("input-file.csv", help="the CSV file to be processed", type=str)
    parser.add_argument("output-file.xml", help="the desired XML output file", type=str)

    args = parser.parse_args()

    Config['Payment']['CollectionDate'] = datetime.datetime.strptime(args.collection_date, "%Y-%m-%d").date()
    Config['Payment']['Description'] = eval(f'f"""{args.description}"""')

    sepa = SepaDebit(Config['SEPAProfile'][args.profile], schema="pain.008.001.02", clean=True)


    with open(vars(args)['input-file.csv']) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        for row in reader:
            if row["Mandatsreferenz"][:4] == "REF-":
                try:
                    if args.verbosity > 0: print(f"  - about to process '{row}'")
                    payment = {
                        "name": row["Name des Zahlungspflichtigen"],
                        "IBAN": row["IBAN"],
                        "BIC": row["SWIFT/BIC"],
                        "amount": int(row["Betrag"])*100,  # in cents
                        "type": "FRST",  # FRST,RCUR,OOFF,FNAL
                        "collection_date": Config['Payment']['CollectionDate'],
                        "mandate_id": row["Mandatsreferenz"],
                        "mandate_date": datetime.datetime.strptime(row["Datum Mandatsunterschrift"], "%Y-%m-%d").date(),
                        "description": Config['Payment']['Description'],
                    }
                    sepa.add_payment(payment)
                except Exception as e:
                    print(f"   *** Caught exception {type(e)} / {e}")
            else:
                print(f"  - skipping entry for '{row['Name des Zahlungspflichtigen']}' due to invalid Matdatsreferenz ({row['Mandatsreferenz']})")


    with open(vars(args)['output-file.xml'], 'w') as xmlfile:
        xmlfile.write(sepa.export(validate=True).decode('utf-8'))
