# Reddy Linux tech channel: one-time setup

1. On your computer, in the repo folder, run:
   `python -m mahanavi.scripts.youtube_shorts_auth_setup --token-file data/youtube_token_reddy_linux.json`
   Sign in with the Google account that owns the Reddy Linux channel and pick the Reddy Linux channel at the picker.
2. Copy the whole content of `data/youtube_token_reddy_linux.json` into a GitHub repo secret named `LOCAL_REDDY_LINUX_TOKEN_JSON`.
3. Run the workflow "Setup | Upload Reddy Linux YouTube Token to Drive", then delete the secret.
4. Posting starts on its own: 2 Shorts a day (about 9 AM and 6:30 PM IST) from Mon 30 Nov 2026, 63 cards (about a month).
