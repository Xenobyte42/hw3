test:
	python -m unittest
	pylint text_history.py
	pycodestyle text_history.py

.PHONY: test
