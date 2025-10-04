#!/usr/bin/env python3
#
# Example usage:
#   ./validate-csv.py input-file.csv
import argparse
import csv

from schwifty import IBAN



if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-v", "--verbosity", action="count", help="increase output verbosity", default=0)
    parser.add_argument("input-file.csv", help="the CSV file to be validated", type=str)

    args = parser.parse_args()


    SeenIBANs = { }
    SeenMandatsreferenz = { }
    with open(vars(args)['input-file.csv']) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        for row in reader:
            if row['IBAN'] != '' and row['Mandatsreferenz'][:4] == 'REF-':
                try:
                    if row['IBAN'] not in SeenIBANs:
                        SeenIBANs[row['IBAN']] = { 'Name': row['Name des Zahlungspflichtigen'], 'Count': 1 }
                    else:
                        SeenIBANs[row['IBAN']]['Count'] += 1
                    if row['Mandatsreferenz'] not in SeenMandatsreferenz:
                        SeenMandatsreferenz[row['Mandatsreferenz']] = { 'Name': row['Name des Zahlungspflichtigen'], 'Count': 1 }
                    else:
                        SeenMandatsreferenz[row['Mandatsreferenz']]['Count'] += 1

                    iban = IBAN(row['IBAN'])
                    if row['SWIFT/BIC'] == '':
                        print(f"  - for {row['Name des Zahlungspflichtigen']}, given {iban}, BIC should be '{iban.bic}'")
                    elif row['SWIFT/BIC'] != iban.bic:
                        print(f"  - for {row['Name des Zahlungspflichtigen']}, given {iban}, BIC should be '{iban.bic}' instead of '{row['SWIFT/BIC']}'")
                    elif args.verbosity > 0: print(f"  - entry for {row['Name des Zahlungspflichtigen']} valid")

                except Exception as e:
                    print(f"  *** Caught exception {type(e)} / {e} while validating {row['Name des Zahlungspflichtigen']}")
            else:
                print(f"  - entry for {row['Name des Zahlungspflichtigen']} skipped : Matdatsreferenz = '{row['Mandatsreferenz']}', IBAN = '{row['IBAN']}'")

    for key, val in SeenIBANs.items():
        if val['Count'] > 1:
            print(f"  - duplicate IBAN {key} found: {val}")
    for key, val in SeenMandatsreferenz.items():
        if val['Count'] > 1:
            print(f"  - duplicate Mandatsreferenz {key} found: {val}")            