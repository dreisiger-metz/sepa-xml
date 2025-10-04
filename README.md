# SEPA-XML Utilities
A collection of some simple scripts which can be used to generate, validate and summarise SEPA XML files.

Script                         | Description
------                         | -----------
`csv-validate.py`              | Validates the key columns in the input CSV file (in particular the IBAN and BIC values)
`csv-convert-to-sepa-xml.py`   | Generates a PAIN.008.001.02 XML file which can be used to schedule bulk SEPA transfers
`sepa-xml-summarise.py`        | Parses PAIN.008.001.02 XML files and generates per-input and aggregate summary CSV files


Depends upon the [sepapy](https://pypi.org/project/sepapy/) and [schwifty](https://pypi.org/project/schwifty/) libraries.
