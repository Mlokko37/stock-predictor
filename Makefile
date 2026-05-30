.PHONY: install test lint train serve

install:
	pip install -r requirements.txt

test:
	pytest tests/

lint:
	flake8 src/ tests/

train:
	python -m stock_predictor.models.trainer

serve:
	uvicorn stock_predictor.api.main:app --reload