#!/usr/bin/env python3
import argparse
import csv
import os

import xmltodict


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-v", "--verbosity", action="count", help="increase output verbosity", default=0)
    parser.add_argument("input-file.xml", help="the XML file to be processed", type=str)
    parser.add_argument("monthly-summaries.csv", help="the CSV file to which monthly summaries will be appended", type=str)

    args = parser.parse_args()

    xmldoc = ""
    with open(vars(args)['input-file.xml']) as xmlfile:
        xmldoc = xmlfile.read()

    if args.verbosity > 0: print(f"  - Read {vars(args)['input-file.xml']}")


    xmldict = xmltodict.parse(xmldoc)['Document']

    data = { }
    data['GrpHdr'] = xmldict['CstmrDrctDbtInitn']['GrpHdr']
    data['NbOfTxs'] = xmldict['CstmrDrctDbtInitn']['PmtInf']['NbOfTxs']
    data['CtrlSum'] = xmldict['CstmrDrctDbtInitn']['PmtInf']['CtrlSum']
    data['ReqdColltnDt'] = xmldict['CstmrDrctDbtInitn']['PmtInf']['ReqdColltnDt']
    data['Ustrd'] = xmldict['CstmrDrctDbtInitn']['PmtInf']['DrctDbtTxInf'][0]['RmtInf']['Ustrd']
    data['Transactions'] = [ ]

    for tx in xmldict['CstmrDrctDbtInitn']['PmtInf']['DrctDbtTxInf']:
        if args.verbosity > 1:
            print(f"    - walking transaction {len(data['Transactions'])} for {tx['Dbtr']['Nm']}")
        data['Transactions'].append({'Name': tx['Dbtr']['Nm'],
                                     'Amt': tx['InstdAmt']['#text'],
                                     'Ustrd': tx['RmtInf']['Ustrd'],
                                     'IBAN': tx['DbtrAcct']['Id']['IBAN'],
                                     'MndtId': tx['DrctDbtTx']['MndtRltdInf']['MndtId'],
                                     'DtOfSgntr': tx['DrctDbtTx']['MndtRltdInf']['DtOfSgntr'],
                                    })
        
    with open(f"parsed-{data['GrpHdr']['MsgId']}.csv", "w") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['MsgId', 'ReqdColltnDt'] + list(data['Transactions'][0].keys()))

        writer.writeheader()
        for tx in data['Transactions']:
            writer.writerow({ **{'MsgId': data['GrpHdr']['MsgId'], 
                                 'ReqdColltnDt': data['ReqdColltnDt']}, **tx})

        if args.verbosity > 0:
            print(f"  - Wrote the data of interest to {data['GrpHdr']['MsgId']}.csv")
            print(f"      - MsgId        = {data['GrpHdr']['MsgId']}")
            print(f"      - ReqdColltnDt = {data['ReqdColltnDt']}")
            print(f"      - NbOfTxs      = {data['NbOfTxs']}")
            print(f"      - CtrlSum      = {data['CtrlSum']}")
            print(f"      - Ustrd        = {data['Ustrd']}")


    summary = {
        'SEPAXMLFile': vars(args)['input-file.xml'],
        'MsgId': data['GrpHdr']['MsgId'],
        'ReqdColltnDt': data['ReqdColltnDt'],
        'NbOfTxs': data['NbOfTxs'],
        'CtrlSum': data['CtrlSum'],
        'Ustrd': data['Ustrd'],
        'TransactionsCSVFile': f"parsed-{data['GrpHdr']['MsgId']}.csv"
    }
    summaryFileExists = os.path.exists(vars(args)['monthly-summaries.csv'])
    with open(vars(args)['monthly-summaries.csv'], 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=list(summary.keys()))
        if not summaryFileExists: writer.writeheader()
        writer.writerow(summary)

