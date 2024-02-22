## **Web for Docker Registry on kan-two.gis**

```
http://kan-two.gis:8080/
```

# **Push docker images to Docker Registry on kan-two.gis**
**1. Наявність образів**

На машині звідки будуть пушитись образи в локальний репозиторій мають бути вже збілджені образи
В ідеалі, має бути docker-compose.images_prod.yml яким будуть спулюватись образи з docker hub і docker-compose.preprod.yml (як в наступному пункті) в якому будуть прописані шляши до Docker Registry on kan-two.gis

**2. Приклад docker-compose.preprod.yml**

Відредагуйте ваш docker-compose.preprod.yml файл для вказання адреси Docker Registry для ваших сервісів:
```
version: '3.9'
services:
  web:
    image: kan-two.gis:5000/<image_name:tag>
    # інші налаштування сервісу
```

**3. daemon.json на всіх машинах, які будуть працювати з локальним репозиторієм**

створити, або змінити файл `etc/docker/daemon.json` 
```
{
  "insecure-registries": ["kan-two.gis:5000"],
  "registry-mirrors": [
    "https://kan-two.gis:5000",
    "http://kan-two.gis:5000"
  ]
}
```

**4. Оновлюємо/створюємо образи**
```
docker compose -f docker-compose.build_prod.yml up -d --build
docker compose -f docker-compose.build_prod.yml stop
docker compose -f docker-compose.build_preprod.yml up -d --build
docker compose -f docker-compose.build_preprod.yml stop
```

**5. Tag and push образів**

Запустіть скрипт `push_images.py` з кореня проекту для залиття образів у Docker Registry on kan-two.gis:
```
python -m /kan/push_images.py --tag <commit hash> --push --images front_prod front_preprod api ALL
python -m /kan/push_images.py --tag <commit hash> --push --images api celery-beat celery redis nginx backup postgres
```
скрипт змінить назви образів відповідно до правил для заливки в Docker Registry та зальє їх туди

**5. Піднімаєм проект на проді чи препроді**

На прод чи препрод сервері мають бути файли nginx.conf, envs/env_prod та docker-compose.preprod.yml (формату як в пункті 2)
```
docker-compose -f docker-compose.preprod.yml up -d
```
#

# **Налаштування Docker Registry для локального сервера**
**Крок 1: Встановлення Docker на машині з репозиторієм**

**Крок 2: Відкриття портів 5000 і 8080 для docker репозиторія для доступу з інших машин локальної мережі**

```
sudo ufw allow 5000/tcp
sudo ufw allow 8080/tcp
sudo ufw reload
```
**Крок 3: Створення  `docker-compose.yml` для Docker Registry та UI**

```
version: '3.9'
services:
  registry:
    container_name: registry
    image: registry:2
    ports:
      - 5000:5000
    restart: always
    volumes:
      - ./registry-data:/var/lib/registry
      - ./config.yml:/etc/docker/registry/config.yml
    environment:
      - REGISTRY_STORAGE_DELETE_ENABLED=true
    networks:
      - registry-ui-net

  ui:
    container_name: registry_ui
    image: joxit/docker-registry-ui:latest
    ports:
      - 8080:80
    restart: always
    environment:
      - REGISTRY_URL=http://kan-two.gis:5000
      - REGISTRY_TITLE=KAN Private Docker Registry
      - NGINX_PROXY_PASS_URL=http://registry:5000
      - SINGLE_REGISTRY=true
      - DELETE_IMAGES=true
    depends_on:
      - registry
    networks:
      - registry-ui-net

networks:
  registry-ui-net:
```

**Крок 4: Створення конфігураційного файлу `config.yml` для Docker Registry**

```
version: 0.1

log:
  level: debug
  fields:
    service: registry
storage:
  delete:
    enabled: true
  cache:
    blobdescriptor: inmemory
  filesystem:
    rootdirectory: /var/lib/registry
  redirect:
    disable: true
http:
  addr: 0.0.0.0:5000
  port: 5000
  headers:
    X-Content-Type-Options: [nosniff]
    Access-Control-Allow-Origin: ['http://kan-two.gis:8080']
    Access-Control-Allow-Methods: ['HEAD', 'GET', 'OPTIONS', 'DELETE']
    Access-Control-Allow-Headers: ['Authorization', 'Accept']
    Access-Control-Max-Age: [1728000]
    Access-Control-Allow-Credentials: [true]
    Access-Control-Expose-Headers: ['Docker-Content-Digest']
health:
  storagedriver:
    enabled: true
    interval: 10s
    threshold: 3
```
**Крок 5: Запуск Docker Registry та UI контейнерів**

```
docker-compose up -d
```