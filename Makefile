local/start: check-env install-hooks # Executa um server FastAPI (caso houver)
	uvicorn src.main:app --port 8000 --reload

test: # Executa os testes e retorna os erros e porcentagens de coverage.
	pytest --cov-report term-missing --cov-report html --cov-branch --cov .

lint: # Executa o lint para formatar e verificar erros.
	@echo
	ruff format .
	@echo
	ruff check --silent --exit-zero --fix .
	@echo
	ruff check .
	@echo
	mypy .
	@echo
	pip-audit

install-hooks:
	@ scripts/install_hooks.sh

check-env:
	@ if [ ! -f ".env" ]; then cp env.example .env; fi
