# Human action required: public repository and deployment

1. Confirm access to `coshaman/Anyang4D` and the pushed `main` branch.
2. Authenticate a hosting provider, build the `Dockerfile`, expose port `8080`, and run the HTTPS smoke checks.
4. Replace `public_url: null` in the final deployment evidence only with a URL observed by the smoke script.

Do not upload `artifacts/final/private-source/`, raw NGII files, `.env`, keys, or local caches.
