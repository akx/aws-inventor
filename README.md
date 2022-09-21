# aws-inventor

Inventor-izes AWS resources for e.g. SOC2 compliance use.

## Usage

* `pip install -e .`
* `aws-inventor --help`

### Example: List KMS key access into Excel

* `aws-inventor list-keys > keys.jsonl`
* `aws-inventor format-keys -i keys.jsonl -o key-report.xlsx`
