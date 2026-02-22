.PHONY: setup run dq report clean

setup:
	python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

run:
	python -m src.crsim.report

dq:
	python -m src.crsim.dq_checks

report:
	python -m src.crsim.report

clean:
	rm -rf data/synthetic reports/*.html reports/figures || true
