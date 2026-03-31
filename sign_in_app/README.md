# Strava Sign-In Helper App

A tiny Streamlit app that makes it easy for challenge participants to hand
Logan the Strava authorisation code he needs — no technical knowledge required.

## What it does

1. The app displays a **one-click Authorize button** that takes athletes directly
   to the Strava permission page (the link is stored securely in `secrets.toml`).
2. The athlete clicks the button and authorises the app on Strava.
3. Strava redirects to a "broken" `localhost` URL — the code is hidden in that
   address.
4. The athlete pastes the full redirect URL into **this app**.
5. If `client_id` and `client_secret` are configured the app automatically
   exchanges the code and shows the athlete their **Strava Athlete ID** and
   **refresh token** to send to Logan — no extra steps needed.
   Without those secrets the app falls back to showing the raw auth code and
   displays step-by-step instructions for finding the Athlete ID on Strava.

## Deploying on Streamlit Community Cloud (free)

1. Push this repository to GitHub (already done).
2. Go to <https://share.streamlit.io> and sign in with your GitHub account.
3. Click **New app**.
4. Fill in:
   - **Repository**: `loganmckerlich/Migos_Fitness_Challenge`
   - **Branch**: `main`
   - **Main file path**: `sign_in_app/app.py`
5. Under **Advanced settings → Secrets**, add the following (replacing the
   placeholders with real values):
   ```toml
   [strava]
   auth_url      = "https://www.strava.com/oauth/authorize?client_id=YOUR_CLIENT_ID&redirect_uri=http://localhost&response_type=code&scope=read,activity:read_all"
   client_id     = "YOUR_STRAVA_CLIENT_ID"
   client_secret = "YOUR_STRAVA_CLIENT_SECRET"
   ```
   `client_id` and `client_secret` are optional but strongly recommended —
   they allow the app to automatically retrieve and display the athlete's
   Strava Athlete ID and refresh token without any extra steps.
6. Click **Deploy!** — Streamlit will give you a public URL you can share with
   athletes.

If `auth_url` is not set in secrets the app falls back to asking athletes to
use a link Logan sent them separately, so it remains functional without secrets.

## Running locally

```bash
pip install -r sign_in_app/requirements.txt
streamlit run sign_in_app/app.py
```

To test the Authorize button locally, create `.streamlit/secrets.toml` at the
repo root (see `.streamlit/secrets.toml.example`) and add `auth_url`,
`client_id`, and `client_secret` under `[strava]`.
