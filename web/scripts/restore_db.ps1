$latestDump = Get-ChildItem -Path "backups" -Filter "*.sql" | Sort-Object LastWriteTime -Descending | Select-Object -First 1

if ($latestDump) {
    Get-Content $latestDump.FullName | docker exec -i mysql-server mysql -uroot -prootpassword mydatabase
    Write-Host "Dамп $($latestDump.Name) восстановлен"
} else {
    Write-Host "Dамп не найден в папке backups"
}
