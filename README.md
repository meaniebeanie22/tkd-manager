# tkd-manager
## Environment variables
Either in a .env file, or as environment vars configured in the host.
### Sample .env (for railway)
```
DEBUG=False
DJANGO_SECRET_KEY=${{secret(50)}}
GOOGLE_APP_PASSWORD=****
GOOGLE_EMAIL_ADDRESS=****
PGDATABASE=${{Postgres.PGDATABASE}}
PGHOST=postgres.railway.internal
PGPASSWORD=${{Postgres.PGPASSWORD}}
PGPORT=5432
PGUSER=${{Postgres.PGUSER}}
REDISHOST=redis.railway.internal
REDISPASSWORD=${{Redis.REDISPASSWORD}}
REDISPORT=6379
REDISUSER=${{Redis.REDISUSER}}
REDIS_URL=${{Redis.REDIS_URL}}
RUN_MIGRATIONS=True
WEASYPRINT_API_DOMAIN=http://weasyprint-rest.railway.internal:${{weasyprint-rest.PORT}}
WEASYPRINT_API_KEY=${{weasyprint-rest.API_KEY}}
```
### Descriptions
#### DEBUG
Should Django run in debug mode? Don't use for production or anything publicly accessible!
#### DJANGO_SECRET_KEY
Django's secret key. Should be a long, cryptographically random string.
#### GOOGLE_APP_PASSWORD
Google app password - used for SMTP in the mean time.
#### GOOGLE_EMAIL_ADDRESS
Used for SMTP - needs to be the account that [[GOOGLE_APP_PASSWORD]] matches to.
#### PGDATABASE
Which Postgres DB contains the application's tables.
#### PGHOST
Where is Postgres located?
#### PGPASSWORD
Postgres password. Should be the same here as on your Postgres instance, and a long random string.
#### PGPORT
Which port Postgres is listening on. Should be the same here as on your Postgres instance.
#### PGUSER
Username that matches the [[PGPASSWORD]]
#### REDISHOST
Where redis is located.
#### REDISPASSWORD
Redis password. Should be the same here as on your Redis instance, and a long random string.
#### REDISPORT
Which port Redis is listening on. Should be the same here as on your Redis instance.
#### REDISUSER
Username that matches the [[REDISPASSWORD]]
#### REDIS_URL
Formatted redis URI, should look like ```redis://default:${{REDIS_PASSWORD}}@${{TCP_PROXY_DOMAIN}}:${{TCP_PROXY_PORT}}```
#### RUN_MIGRATIONS
Whether DB migrations should be run before starting the server
#### WEASYPRINT_API_DOMAIN
Where the weasyprint API is located. Needed for making pretty PDFs for grading invites and certificates.
#### WEASYPRINT_API_KEY
API key needed for [[WEASYPRINT_API_DOMAIN]]
