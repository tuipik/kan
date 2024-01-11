## **Налаштування Docker Registry для локального сервера**

**Крок 1: Встановлення Docker на машині з репозиторієм**
**Крок 2: Відкриття docker репозиторія для доступу з інших машин локальної мережі в налаштуваннях файрволу**
```
sudo ufw allow 5000/tcp
sudo ufw reload
```
**Крок 3: Створення Docker volume для Registry**
```
docker volume create registry_data
```
при цьому створиться дана папка за шляхом `./var/lib/docker/volumes/registry_data`
**Крок 4: Створення конфігураційного файлу `config.yml` для Docker Registry**
```
version: 0.1
log:
  fields:
    service: registry
storage:
  cache:
    blobdescriptor: inmemory
  filesystem:
    rootdirectory: /var/lib/registry
http:
  addr: 0.0.0.0:5000
  port: 5000

```
**Крок 5: Запуск Docker Registry контейнера**
Запустіть Docker Registry контейнер, монтувавши створений Docker volume та вказавши конфігураційний файл:
```
docker run -d -p 5000:5000 --restart=always --name registry -v registry_data:/var/lib/registry -v $(pwd)/config.yml:/etc/docker/registry/config.yml registry:2
```
**Крок 6: Наявність образів**
На машині звідки будуть пушитись образі в локальний репозиторій мають бути вже збілджені образи

**Крок 7: Зміна docker-compose.yml файлу**
Відредагуйте ваш docker-compose.yml файл для вказання адреси Docker Registry для ваших сервісів:
```
version: '3'
services:
  web:
    image: kan-two.gis/<image_name:tag>
    # інші налаштування сервісу
```
**Крок 8: daemon.json на всіх машинах, які будуть працювати локальним репозиторієм**
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

**Крок 9: Пуш та пул образів**
Запустіть скрипт push_docker_images_to_local_registry з кореня проекту для залиття образів у Docker Registry:
```
python /kan/push_docker_images_to_local_registry.py --tag --push
```

**Крок 10: Піднімаєм проект на проді чи препроді**
На прод чи препрод сервері мають бути файли nginx.conf, envs/env_prod та docker-compose.preprod.yml (формату як в пункті Крок 7: Зміна docker-compose.yml файлу)
```
docker-compose -f docker-compose.preprod.yml up
```