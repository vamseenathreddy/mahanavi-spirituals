"""One-time Blogger sign-in, saved to data/blogger_token.json (scope: blogger only, never a YouTube scope).

Two steps so it also works from a cloud session with no browser:

  python -m mahanavi.scripts.blogger_auth_setup --url            # prints the Google sign-in URL
  python -m mahanavi.scripts.blogger_auth_setup --code "<the full http://localhost... address Google sent you to>"

Sign in with the Google account that OWNS the Blogger blogs. The OAuth client is read from --client (a
client_secrets.json) or, by default, from the client_id/client_secret already inside data/youtube_token.json."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCOPES = ["https://www.googleapis.com/auth/blogger"]
REDIRECT = "http://localhost:8080/"


def _flow(client: Path):
    from google_auth_oauthlib.flow import Flow

    d = json.loads(client.read_text(encoding="utf-8"))
    if "installed" not in d and "web" not in d:
        d = {"installed": {"client_id": d["client_id"], "client_secret": d["client_secret"],
                           "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                           "token_uri": "https://oauth2.googleapis.com/token", "redirect_uris": [REDIRECT]}}
    return Flow.from_client_config(d, SCOPES, redirect_uri=REDIRECT, autogenerate_code_verifier=False)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--client", default="data/youtube_token.json")
    ap.add_argument("--token-file", default="data/blogger_token.json")
    ap.add_argument("--url", action="store_true")
    ap.add_argument("--code", default=None, help="the full address (or just the code) Google redirected to")
    args = ap.parse_args()
    flow = _flow(Path(args.client))
    if args.url:
        url, _ = flow.authorization_url(access_type="offline", prompt="consent select_account", include_granted_scopes="false")
        print(url)
        return 0
    if args.code:
        from urllib.parse import parse_qs, urlparse

        code = parse_qs(urlparse(args.code).query).get("code", [args.code])[0]
        flow.fetch_token(code=code)
        Path(args.token_file).parent.mkdir(parents=True, exist_ok=True)
        Path(args.token_file).write_text(flow.credentials.to_json(), encoding="utf-8")
        print(f"Saved {args.token_file}")
        return 0
    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
