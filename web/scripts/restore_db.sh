#!/bin/bash

if [ -z "$1" ]; then
  echo "❌ Укажи путь к .sql файлу. Пример:"
  echo "./scripts/restore_db.sh backups/db_dump_2025-06-23_15-42-00.sql"
  exit 1
fi

DUMP_FILE="$1"

if [ ! -f "$DUMP_FILE" ]; then
  echo "❌ Файл не найден: $DUMP_FILE"
  exit 1
fi

# Восстановление
cat "$DUMP_FILE" | docker exec -i mysql-server mysql -uroot -prootpassword mydatabase

echo "✅ База восстановлена из $DUMP_FILE"
