# csvdiff

A CLI tool to semantically diff two CSV files and output human-readable change summaries.

---

## Installation

```bash
pip install csvdiff
```

Or install from source:

```bash
git clone https://github.com/yourname/csvdiff.git
cd csvdiff && pip install .
```

---

## Usage

```bash
csvdiff old.csv new.csv
```

By default, `csvdiff` compares rows by the first column as the key. You can specify a key column explicitly:

```bash
csvdiff old.csv new.csv --key id
```

### Example Output

```
~ Row 3 (id=42): "email" changed from "alice@old.com" → "alice@new.com"
+ Row added (id=99): name=Bob, email=bob@example.com, age=30
- Row removed (id=17): name=Carol, email=carol@example.com, age=25

Summary: 1 added, 1 removed, 1 modified
```

### Options

| Flag | Description |
|------|-------------|
| `--key COLUMN` | Column to use as the unique row identifier |
| `--ignore COLUMN` | Ignore a column when comparing (repeatable) |
| `--output FORMAT` | Output format: `text` (default), `json`, or `csv` |
| `--no-color` | Disable colored terminal output |

---

## Requirements

- Python 3.8+

---

## License

This project is licensed under the [MIT License](LICENSE).