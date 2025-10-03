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


    with open(vars(args)['input-file.csv']) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        for row in reader:
            if row['IBAN'] != '':
                try:
                    iban = IBAN(row['IBAN'])
                    if row['SWIFT/BIC'] == '':
                        print(f"  - for {row['Name des Zahlungspflichtigen']}, given {iban}, BIC should be '{iban.bic}'")
                    elif row['SWIFT/BIC'] != iban.bic:
                        print(f"  - for {row['Name des Zahlungspflichtigen']}, given {iban}, BIC should be '{iban.bic}' instead of '{row['SWIFT/BIC']}'")
                    elif args.verbosity > 0: print(f"  - entry for {row['Name des Zahlungspflichtigen']} valid")

                except Exception as e:
                    print(f"  *** Caught exception {type(e)} / {e} while validating {row['Name des Zahlungspflichtigen']}")
            elif args.verbosity > 1: print(f"  - entry for {row['Name des Zahlungspflichtigen']} skipped due to invalid Matdatsreferenz ({row['Mandatsreferenz']})")
