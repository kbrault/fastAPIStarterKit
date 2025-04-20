# fastAPIStartKit

## 1️⃣ **Local installation**

```sh
cd backend
python3 -m venv .venv
pip install -r requirements.txt
python3 run.py load && python3 run.py app
```

## 2️⃣ **Docker installation**

```sh
docker compose up --build -d \
&& docker exec -it fastapistarterkit_app python /app/run.py load \
&& docker exec -it fastapistarterkit_app python /app/run.py app \
&& docker exec -it fastapistarterkit_front
```
