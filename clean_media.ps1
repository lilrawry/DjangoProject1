# Clean up media directory
Write-Host "Cleaning up media directory..." -ForegroundColor Green

# Path to the media directory
$mediaPath = "media"
$roomImagesPath = Join-Path $mediaPath "room_images"

# Remove all files in room_images directory
if (Test-Path $roomImagesPath) {
    Write-Host "Removing old images..." -ForegroundColor Yellow
    Remove-Item -Path $roomImagesPath\* -Force -Recurse
    Remove-Item -Path $roomImagesPath -Force -Recurse
}

Write-Host "Media cleanup completed!" -ForegroundColor Green 