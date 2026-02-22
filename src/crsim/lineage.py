from dataclasses import dataclass

@dataclass(frozen=True)
class LineageNode:
    name: str
    description: str

def basic_lineage() -> list[LineageNode]:
    return [
        LineageNode("data/synthetic/loans_synthetic.parquet", "Synthetic credit portfolio (loan-level)"),
        LineageNode("DuckDB loans_raw", "Loaded raw loans into DuckDB"),
        LineageNode("loans_clean view", "Basic validity filters and cleaned view"),
        LineageNode("features matrix X", "Imputation + encoding + numeric features"),
        LineageNode("PD model", "Logistic regression PD model"),
        LineageNode("LGD baseline", "Rule-based LGD estimates"),
        LineageNode("EAD baseline", "Balance + CCF*undrawn for revolving"),
        LineageNode("EL (PD*LGD*EAD)", "Expected loss at loan-level"),
        LineageNode("reports/*.html", "Management-ready risk + data quality reports"),
    ]
