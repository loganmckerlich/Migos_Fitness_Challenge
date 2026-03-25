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
individually authorise the app.  Follow these steps for every athlete in the
challenge:

1. Direct each athlete to the following URL (replace `<CLIENT_ID>` with your
   app's Client ID):

   ```
   https://www.strava.com/oauth/authorize?client_id=<CLIENT_ID>&response_type=code&redirect_uri=http://localhost&approval_prompt=force&scope=activity:read_all
   ```

2. After the athlete clicks **Authorize**, Strava will redirect to
   `http://localhost?code=<AUTH_CODE>&scope=...`.
   Copy the `code` value from the URL.

3. Exchange the code for a refresh token by running this curl command
   (replace placeholders):

   ```bash
   curl -X POST https://www.strava.com/oauth/token \
     -d client_id=<CLIENT_ID> \
     -d client_secret=<CLIENT_SECRET> \
     -d code=<AUTH_CODE> \
     -d grant_type=authorization_code
   ```

4. From the JSON response, copy the `refresh_token` value.

5. Repeat steps 1–4 for every athlete.

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
