# Создаём имя файла с текущей датой и временем
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$dumpPath = "backups\db_dump_$timestamp.sql"

# Выполняем дамп и сохраняем в переменную
Write-Host "⏳ Выполняется экспорт базы данных..."
$dump = docker exec -i mysql-server sh -c "exec mysqldump --default-character-set=utf8mb4 -uroot -prootpassword mydatabase"

# Кодировка UTF-8 без BOM
$utf8NoBomEncoding = New-Object System.Text.UTF8Encoding($false)

# Сохраняем дамп в файл
[System.IO.File]::WriteAllLines($dumpPath, $dump, $utf8NoBomEncoding)

Write-Host "✅ Дамп сохранён в $dumpPath (UTF-8 без BOM)"
