# Build frontend and copy dist to ../docs for GitHub Pages
# Usage: run from frontend folder: powershell -File deploy_docs.ps1

Write-Host "Starting deploy to docs/ (GitHub Pages)"

# Ensure node modules installed
if (-not (Test-Path "node_modules")) {
  Write-Host "Installing npm dependencies..."
  npm install
}

Write-Host "Building production bundle..."
npm run build

$distPath = Join-Path (Get-Location) "dist"
$repoRoot = Resolve-Path ".."
$docsPath = Join-Path $repoRoot "docs"

if (Test-Path $docsPath) {
  Write-Host "Removing existing docs/ folder..."
  Remove-Item -Recurse -Force $docsPath
}

Write-Host "Copying dist to docs/"
Copy-Item -Recurse -Force -Path $distPath -Destination $docsPath

Write-Host "Staging docs/ for commit..."
# Note: the script will not commit/push automatically. Run the following commands manually:
Write-Host "
Next steps (run in repository root):
  git add docs
  git commit -m 'chore(frontend): deploy site to docs/'
  git push origin main

Then in your GitHub repository settings -> Pages, set source to 'main branch /docs folder'.
"

Write-Host "Deploy script finished."
