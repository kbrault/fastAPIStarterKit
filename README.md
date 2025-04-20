# fastAPIStartKit

## **Deployment**

```sh
docker compose up --build -d \
&& docker exec -it fastapistarterkit_app python /app/run.py load \
&& docker exec -it fastapistarterkit_app python /app/run.py app \
&& docker exec -it fastapistarterkit_front
```
