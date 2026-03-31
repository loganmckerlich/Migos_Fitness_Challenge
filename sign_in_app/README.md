# Strava Sign-In Helper App

A tiny Streamlit app that makes it easy for challenge participants to hand
Logan the Strava authorisation code he needs — no technical knowledge required.

## What it does

1. Logan sends each athlete a personalised Strava authorisation URL.
2. The athlete clicks the link and authorises the app on Strava.
3. Strava redirects to a "broken" `localhost` URL — the code is hidden in that
   address.
4. The athlete opens **this app**, pastes the full redirect URL, and is shown
   just the short code they need to text to Logan.

## Deploying on Streamlit Community Cloud (free)

1. Push this repository to GitHub (already done).
2. Go to <https://share.streamlit.io> and sign in with your GitHub account.
3. Click **New app**.
4. Fill in:
   - **Repository**: `loganmckerlich/Migos_Fitness_Challenge`
   - **Branch**: `main`
   - **Main file path**: `sign_in_app/app.py`
5. Click **Deploy!** — Streamlit will give you a public URL you can share with
   athletes.

No secrets or environment variables are required for this app.

## Running locally

```bash
pip install streamlit
streamlit run sign_in_app/app.py
```
