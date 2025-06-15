## Credit Union Report Generator

### Run:

```bash
$ uv sync  
$ uv run main.py <<report_number>>
```

### Credentials:

Requires a '.env' file with the following Env Variables:

- ENCOMPASS_USERNAME=""
- ENCOMPASS_PASSWORD=""
- ENCOMPASS_CLIENT_ID=""
- ENCOMPASS_CLIENT_SECRET=""

For PDF export, requires a 'credentials.json' from Google Cloud / OAuth 2.0 to access Google APIs.
More information: https://developers.google.com/identity/protocols/oauth2#1.-obtain-oauth-2.0-credentials-from-the-dynamic_data.setvar.console_name.