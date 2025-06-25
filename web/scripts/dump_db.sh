#!/bin/bash

# Имя дампа по текущей дате и времени
NOW=$(date +"%Y-%m-%d_%H-%M-%S")
DUMP_FILE="backups/db_dump_$NOW.sql"

# Создание дампа
docker exec -i mysql-server sh -c 'exec mysqldump -uroot -prootpassword mydatabase' > "$DUMP_FILE"

echo "✅ Дамп сохранён в $DUMP_FILE"
