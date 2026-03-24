# Script para limpiar comillas de la variable Path
Write-Host "=== Limpieza de Variable Path ===" -ForegroundColor Cyan
Write-Host ""

# Obtener Path actual del usuario
$currentPath = [Environment]::GetEnvironmentVariable('Path', 'User')

# Mostrar rutas con problemas
Write-Host "Rutas con comillas encontradas:" -ForegroundColor Yellow
$currentPath -split ';' | ForEach-Object {
    if ($_ -match '"') {
        Write-Host "  - $_" -ForegroundColor Red
    }
}
Write-Host ""

# Limpiar comillas
$cleanedPath = $currentPath -replace '"', ''

# Mostrar cambios
Write-Host "Actualizando variable Path..." -ForegroundColor Green

# Actualizar la variable de entorno del usuario
[Environment]::SetEnvironmentVariable('Path', $cleanedPath, 'User')

Write-Host "✓ Variable Path limpiada exitosamente!" -ForegroundColor Green
Write-Host ""
Write-Host "IMPORTANTE: Cierra y vuelve a abrir VSCode para que los cambios surtan efecto." -ForegroundColor Yellow
Write-Host ""

# Verificar
Write-Host "Verificando..." -ForegroundColor Cyan
$newPath = [Environment]::GetEnvironmentVariable('Path', 'User')
$quotesFound = ($newPath -match '"')

if ($quotesFound) {
    Write-Host "⚠ Aún hay comillas en Path. Puede que necesites permisos de administrador." -ForegroundColor Red
} else {
    Write-Host "✓ No se encontraron comillas en Path. ¡Problema resuelto!" -ForegroundColor Green
}
