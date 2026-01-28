# GitHub Pages Live Dashboard Deployment

- The only file that should be deployed to GitHub Pages is the generated `logs/index.html` (created by the workflow from the health check report).
- Do NOT use or commit the root `index.html` (the one with JavaScript fetching JSON) for GitHub Pages.
- The workflow will always overwrite `logs/index.html` with the latest report and deploy it as the live dashboard.
- The `logs` folder is kept in git with a `.gitkeep` file, but only `index.html` is deployed.

## Summary
- Edit your health check scripts and workflow as needed, but do not edit or use the root `index.html` for deployment.
- The live dashboard will always reflect the latest workflow run.
