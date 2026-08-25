# Human action required: public repository and deployment

1. Authenticate GitHub and create or select `coshaman/Anyang4D`.
2. Add the workspace as the repository remote and push branch `main` after running the public-release audit.
3. Authenticate a hosting provider, build the `Dockerfile`, expose port `8080`, and run the HTTPS smoke checks.
4. Replace `public_url: null` in the final deployment evidence only with a URL observed by the smoke script.

Do not upload `artifacts/final/private-source/`, raw NGII files, `.env`, keys, or local caches.
