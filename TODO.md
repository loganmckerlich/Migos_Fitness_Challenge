# TODO.md — Manual setup steps for the Migos Fitness Challenge app
# Auto-generated: complete each step before switching USE_DUMMY_DATA to False.

## 1. Register a Strava API Application

1. Go to https://www.strava.com/settings/api and log in with your Strava account.
2. Click **Create & Manage Your App**.
3. Fill in:
   - **Application Name**: e.g. `Migos Fitness Challenge`
   - **Category**: choose `Data Importer` or similar
   - **Club**: optional
   - **Website**: your Streamlit app URL (you can update this later)
   - **Authorization Callback Domain**: `localhost` (for local testing); update to
     your Streamlit Community Cloud domain (e.g. `your-app.streamlit.app`) before
     deploying.
4. Note your **Client ID** and **Client Secret** — you will need them below.

---

## 2. Obtain Per-Athlete Refresh Tokens

Because the app fetches data for *multiple athletes*, each athlete must
individually authorise the app.  Use the **sign-in helper app**
(`sign_in_app/`) to do this — it handles the token exchange automatically so
athletes never need to run any commands.

### Prerequisites

Make sure `client_id` and `client_secret` are added to the sign-in app's
secrets on Streamlit Community Cloud (see the sign-in app's README for
deployment instructions).  With those credentials in place the app exchanges
the authorisation code for a refresh token on the athlete's behalf.

### Per-athlete steps

1. Send each athlete the public URL of the deployed sign-in helper app.

2. The athlete clicks **Authorize on Strava** inside the app, approves access,
   and pastes the resulting redirect URL (from their browser's address bar)
   back into the app.

3. The app automatically contacts Strava and displays the athlete's
   **Strava Athlete ID** and **Refresh Token**.

4. The athlete copies both values and sends them to Logan.

5. Repeat steps 2–4 for every athlete.

---

## 3. Configure Streamlit Secrets

### Local development

Create the file `.streamlit/secrets.toml` (it is git-ignored) with the
following structure:

```toml
[app]
password = "your_app_password_here"

[strava]
client_id     = "YOUR_CLIENT_ID"
client_secret = "YOUR_CLIENT_SECRET"

[athletes]

  [athletes."111111"]
  refresh_token = "REFRESH_TOKEN_FOR_ATHLETE_111111"

  [athletes."222222"]
  refresh_token = "REFRESH_TOKEN_FOR_ATHLETE_222222"

  [athletes."333333"]
  refresh_token = "REFRESH_TOKEN_FOR_ATHLETE_333333"

  [athletes."444444"]
  refresh_token = "REFRESH_TOKEN_FOR_ATHLETE_444444"

  [athletes."555555"]
  refresh_token = "REFRESH_TOKEN_FOR_ATHLETE_555555"
```

Replace the placeholder athlete IDs (`111111`, `222222`, …) with the real
Strava athlete IDs from `config.py`.

### Streamlit Community Cloud deployment

1. Push your code to a public GitHub repository.
2. Go to https://share.streamlit.io and connect your repository.
3. In the app settings on Streamlit Cloud, click **Secrets** and paste the
   same TOML content from above.

---

## 4. Update `config.py` with Real Athlete IDs

Replace the placeholder IDs in `config.py → ATHLETES` with the actual
Strava athlete IDs.  You can find an athlete's ID by calling:

```bash
curl -H "Authorization: Bearer <ACCESS_TOKEN>" \
     https://www.strava.com/api/v3/athlete
```

---

## 5. Set `USE_DUMMY_DATA = False`

Once all tokens are in place, open `strava.py` and change:

```python
USE_DUMMY_DATA: bool = True
```

to:

```python
USE_DUMMY_DATA: bool = False
```

---

## 6. Update Strava App Callback Domain (for Deployment)

After deploying to Streamlit Community Cloud, return to
https://www.strava.com/settings/api and update the
**Authorization Callback Domain** to match your deployed app's domain
(e.g. `your-app-name.streamlit.app`).

---

## 7. Scope Considerations

The token scope `activity:read_all` is required to read private activities.
If athletes only want to share public activities, use `activity:read` instead
(step 2 URL above).  Note that this may miss some activities.

---

*Any questions?  Open an issue in the repository.*
