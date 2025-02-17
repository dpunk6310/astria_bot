# Astria Bot

## Deploy

### Запуск проекта

#### 1. Запуск stage версии

#### Database

```bash
docker compose -f docker-compose.stage.db.yml up --build -d
```

#### Application Run

```bash
docker compose -f docker-compose.stage.yml up --build -d
```

#### Application Logs

```bash
docker compose -f docker-compose.stage.yml logs -f
```

#### Application Down

```bash
docker compose -f docker-compose.stage.yml down -v
```

#### Application All

```bash
docker compose -f docker-compose.stage.yml down -v && docker compose -f docker-compose.stage.yml up --build -d && docker compose -f docker-compose.stage.yml logs -f
```


#### 2. Запуск main версии

#### Nginx proxy and SSL

```bash
docker compose -f docker-compose.proxy.yml up --build -d
```

#### Database

```bash
docker compose -f docker-compose.db.yml up --build -d
```

#### Application Run

```bash
docker compose -f docker-compose.yml up --build -d
```

#### Application Logs

```bash
docker compose -f docker-compose.yml logs -f
```

#### Application Down

```bash
docker compose -f docker-compose.yml down -v
```

#### Application All

```bash
docker compose -f docker-compose.yml down -v && docker compose -f docker-compose.yml up --build -d && docker compose -f docker-compose.yml logs -f
```
