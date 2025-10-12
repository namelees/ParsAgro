# GitHub Actions для Docker

Этот workflow автоматически собирает и публикует Docker образ в GitHub Container Registry (ghcr.io).

## Триггеры

Workflow запускается при:
- Push в ветки `main` или `master`
- Push тегов в формате `v*` (например, `v1.0.0`)
- Pull Request в ветки `main` или `master`

## Тегирование

Образы автоматически тегируются:
- `latest` - для основной ветки
- `v1.0.0` - для семантических версий
- `v1.0` - для мажорных.минорных версий
- `main` - для ветки main
- `pr-123` - для pull request'ов

## Использование

После успешной сборки образ будет доступен в GitHub Container Registry:

```bash
# Скачать образ
docker pull ghcr.io/ваш-username/parsagro:latest

# Запустить контейнер
docker run ghcr.io/ваш-username/parsagro:latest
```

## Права доступа

Убедитесь, что в настройках репозитория включены права:
- `contents: read` - для чтения кода
- `packages: write` - для публикации пакетов

## Переменные окружения

- `REGISTRY` - ghcr.io
- `IMAGE_NAME` - имя репозитория GitHub
