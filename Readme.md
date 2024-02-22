
```
docker build -t kan-api:latest .
docker-compose -f docker-compose.prod.yml up
```


## Restore db
db backups are availeble on:

backup.gis/kan_backups/backups/

kan.gis/kan_db_backups/

### Restore db:
Copy dump to server where restore should be done
```
scp back_up@backup.gis:/home/back_up/kan_backups/backups/last/kan-20240222-145942.sql.gz /home/preprod/
```

### Delete postgres volume 
```
docker stop kan_db
sudo rm -rf postgres_data/
docker start kan_db
```

### Restore db
```
gunzip -c /home/preprod/kan-20240222-145942.sql.gz | docker exec -i kan_db psql -U kan -d kan
```
