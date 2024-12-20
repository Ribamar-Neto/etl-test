# etl-test
This is a test that was applied by my surpevisor at Delfos.

# To run it, you could do it
cd docker
docker-compose build
docker-compose up

# But I'm fixing the docker
# So, do this

# Create a .env file likely the env-example
# After that, do it:

uvicorn src.main:app --reload --port 8000
python scripts/etl

# This will create the DBs and tables
