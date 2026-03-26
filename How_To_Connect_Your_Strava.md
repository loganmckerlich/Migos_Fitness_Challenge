# 🏃 How to Connect Your Strava to the Migos Fitness Challenge

Hey! This is Logan. I'm building a little app to track our group fitness challenge
and I need a one-time piece of info from your Strava account so I can pull in your
workouts. It takes **less than 2 minutes** and you don't need to install anything.

---

## What you'll need

- A Strava account (you should already have one!)
- A phone or computer with a web browser

---

## Step 1 — Click the link Logan sent you

Logan will send you a personalized link that looks something like this:

```
https://www.strava.com/oauth/authorize?client_id=XXXXXX&response_type=code&redirect_uri=http://localhost&approval_prompt=force&scope=activity:read_all
```

**Open that link in your web browser.**

> ⚠️ The link will only work if you are logged in to Strava. If you're not logged
> in, Strava will ask you to log in first — that's totally normal.

---

## Step 2 — Authorize the app on Strava

You'll see a Strava page asking you to give the "Migos Fitness Challenge" app
permission to read your activities.

👉 Scroll down and click the orange **"Authorize"** button.

![Strava authorization screen — click the orange Authorize button]

---

## Step 3 — Copy the page address (URL) you land on

After you click Authorize, your browser will try to load a page that looks like
it's broken or blank. **That's completely normal — don't worry!**

What you need to do is look at the address bar at the top of your browser.
The address will look something like this:

```
http://localhost/?state=&code=abc123xyz789&scope=read,activity:read_all
```

**Copy the entire address** (tap/click the address bar, select all, then copy).

> 💡 **Tip on iPhone/Android:** tap the address bar, then tap "Select All", then
> tap "Copy".
>
> 💡 **Tip on a computer:** click the address bar, press Ctrl+A (Windows) or
> Cmd+A (Mac) to select all, then Ctrl+C / Cmd+C to copy.

---

## Step 4 — Send it to Logan

Paste the address into a text message or WhatsApp message and send it to Logan.
That's it — you're done! 🎉

Logan will take care of the rest. Your data stays private and is only used for
the challenge leaderboard.

---

## Frequently Asked Questions

**Q: Why does the page look broken after I click Authorize?**  
A: The app isn't deployed yet, so your browser tries to open `localhost` (your
own computer), which isn't running anything. That's expected — the important
info is already in the address bar URL.

**Q: What data does the app read?**  
A: Only your activity data (distances and dates). It cannot see your personal
profile details, followers, or anything private beyond workout data.

**Q: Can I revoke access later?**  
A: Yes. Go to your Strava settings →
[My Apps](https://www.strava.com/settings/apps) and disconnect the app at any
time.

**Q: I'm getting an error on the Strava page, what do I do?**  
A: Make sure you're using the exact link Logan sent you. If it still doesn't
work, just let Logan know and he'll help you sort it out.

---

*Thanks for being part of the challenge! 💪*
