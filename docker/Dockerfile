# Fase de build para instalar o ambiente com o Rye
FROM python:3.11 AS builder

WORKDIR /builder

# Copiar arquivos necessários para o contexto de build
COPY ./requirements.lock ./requirements.lock
COPY ./pyproject.toml ./pyproject.toml

# Baixar e instalar o Rye
RUN curl -k -L -o /tmp/rye.gz https://github.com/astral-sh/rye/releases/latest/download/rye-x86_64-linux.gz \
    && gunzip /tmp/rye.gz \
    && chmod +x /tmp/rye \
    && mv /tmp/rye /usr/local/bin/rye \
    && rye --version

# Atualizar pip e instalar as dependências com o Rye
RUN pip install --upgrade pip \
    && rye sync

# Fase final para a imagem leve de produção
FROM python:3.11-slim

# Criar usuário e grupo não privilegiados
RUN addgroup --gid 1001 --system app && \
    adduser --no-create-home --shell /bin/false --disabled-password --uid 1001 --system --group app

# Variáveis de ambiente para evitar problemas de bytecode e buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONHTTPSVERIFY=1
ENV PYTHONBREAKPOINT=0

# Copiar o ambiente Python do builder para a imagem final
COPY --from=builder /usr/local /usr/local

# Copiar o código-fonte para o diretório da aplicação
WORKDIR /app
COPY ./src/ ./src

# Expor a porta 8000 para a aplicação
EXPOSE 8000

# Comando para rodar a aplicação com uvicorn
CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8000", "src.main:app"]
