# NEXUS Gear Project

## Admin API

Headers:
- `X-Admin-User`: string (telegram id or admin id)
- `X-Admin-Token`: HMAC SHA256 of `X-Admin-User` with secret `APP_SECRET_TOKEN`

Pagination & search (server-side):
- Query: `?q=<search>&limit=<n>&offset=<m>`
- Response headers: `X-Total-Count`, `X-Limit`, `X-Offset`
- Body: JSON array of items (backward compatible)

Error format (unified):
```json
{ "error": { "code": "bad_request", "message": "...", "details": {"...": "..."} } }
```

Endpoints:
- Categories: `GET/POST/PUT/DELETE /api/v1/admin/categories`
- Products: `GET/POST/PUT/DELETE /api/v1/admin/products`
- Orders: `GET /api/v1/admin/orders`, `GET /api/v1/admin/orders/{id}`, `PATCH /api/v1/admin/orders/{id}`

See also `ROADMAP.md` for current status and next steps.

## Admin API — curl examples

Export common headers:
```bash
export ADMIN_USER=123
export SECRET=$(python - <<'PY'
import os, hmac, hashlib; s=os.getenv('APP_SECRET_TOKEN','secret'); u=os.getenv('ADMIN_USER',''); print(hmac.new(s.encode(), u.encode(), hashlib.sha256).hexdigest())
PY
)
export H1="X-Admin-User: $ADMIN_USER"
export H2="X-Admin-Token: $SECRET"
```

Products with pagination, search and category filter:
```bash
curl -sS -H "$H1" -H "$H2" \
  'http://localhost:8080/api/v1/admin/products?q=phone&category_id=2&limit=20&offset=0'
```

Orders with status and date range:
```bash
curl -sS -H "$H1" -H "$H2" \
  'http://localhost:8080/api/v1/admin/orders?status=paid&created_from=2025-01-01T00:00:00&created_to=2025-12-31T23:59:59&limit=50&offset=0'
```

Categories list with pagination:
```bash
curl -sS -H "$H1" -H "$H2" 'http://localhost:8080/api/v1/admin/categories?limit=10&offset=0'
```

Error responses follow unified format:
```json
{ "error": { "code": "bad_request", "message": "...", "details": { "errors": [ ... ] } } }
```
