#!/usr/bin/env python3
#
# Example usage:
#   ./csv-to-sepa--freiwald.py --profile sobaschu --for-period AUG-2025 \
#        SoBaSchuMitglieder2025-Mitgliederinformation.csv SBS-2025-08.xml
import argparse
import csv
import datetime
import os
import sys

from sepapy import SepaDebit

sys.path.append(os.getcwd())
from config import Config

# Config = {
#     "SEPAProfile": {
#         "regular": {
#             "msg_id": f"FREIWALD-EV--{datetime.datetime.today().strftime('%Y%m%d-%H%M%S')}",
#             "name": "Freiwald e.V.",
#             "IBAN": "DE21430609671238727300",
#             "BIC": "GENODEM1GLS",
#             "batch": True,
#             # based on the Glauebiger-IdNr DE65ZZZ00002230866, here ZZZ = 000
#             "creditor_id": "DE6500000002230866",
#             "currency": "EUR"
#         },
#         "sobaschu": {
#             "msg_id": f"FREIWALD-SOBASCHU--{datetime.datetime.today().strftime('%Y%m%d-%H%M%S')}",
#             "name": "Freiwald e.V.",
#             "IBAN": "DE21430609671238727300",
#             "BIC": "GENODEM1GLS",
#             "batch": True,
#             "creditor_id": "DE6500100002230866",    # ZZZ = 001
#             "currency": "EUR"
#         }
#     },
#     "Payment": { 
#         "Description": "Förderbetrag Freiwald e.V. für {args.for_period} - Herzlichen Dank"
#     }
# }




if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--profile", type=str, required=True, help=f"the SEPA profile to use", choices=list(Config['SEPAProfile'].keys()))
    parser.add_argument("--for-period", type=str, required=True, help="the MMM-YYYY to which these transactions belong")
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
            reasons = []
            dateFor = datetime.datetime.strptime(args.for_period, '%b-%Y')
            dateNotBefore = datetime.datetime.strptime(row['Nicht vor'], '%Y-%m') if row['Nicht vor'] != '' else None
            dateNotAfter = datetime.datetime.strptime(row['Nicht nach'], '%Y-%m') if row['Nicht nach'] != '' else None
            if row["Mandatsreferenz"][:4] != "REF-":
                reasons.append(f"invalid Matdatsreferenz ({row['Mandatsreferenz']})")
            if dateNotBefore == None:
                reasons.append("empty 'Nicht vor' date")
            if dateNotBefore != None and dateFor < dateNotBefore:
                reasons.append(f"for-date {dateFor.strftime('%Y-%m')} is before not-before-date {row['Nicht vor']}")
            if dateNotAfter != None and dateFor > dateNotAfter:
                reasons.append(f"for-date {dateFor.strftime('%Y-%m')} falls after not-after-date {row['Nicht nach']}")
            if len(reasons) == 0:
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
                print(f"  - skipping entry for '{row['Name des Zahlungspflichtigen']}' due to reason{'s' if len(reasons)>1 else ''}: {', '.join(reasons)}")


    with open(vars(args)['output-file.xml'], 'w') as xmlfile:
        xmlfile.write(sepa.export(validate=True).decode('utf-8'))