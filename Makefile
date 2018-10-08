# Variables -------------------------------------------------------------------

# Commands --------------------------------------------------------------------

help:
	@echo "Please use \`make <target>\` where <target> is one of"
	@echo "  pyc-clean                  to delete all temporary artifacts"
	@echo "  docs-html                  to generate HTML documentation"
	@echo "  docs-clean                 to remove documentation"
	@echo "  install                    to install in editable mode"
	@echo "  lint                       to run pylint on the entire codebase"

pyc-clean:
	$(info Removing unused Python compiled files, caches and ~ backups...)
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

docs-html:
	@cd docs; $(MAKE) html

docs-clean:
	@cd docs; $(MAKE) clean

docs-spelling:
	@cd docs; $(MAKE) spelling

install:
	pip install -e .

lint:
	flake8 .
