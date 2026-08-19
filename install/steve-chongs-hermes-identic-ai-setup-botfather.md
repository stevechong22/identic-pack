# BotFather — Step-by-Step for Complete Beginners

> **Version:** 1.0 · **Last updated:** 2026-08-17

> A bot is just a special Telegram account that a computer controls. @BotFather is
> the Telegram account that *makes* bots. You only ever do this once. It takes
> about 2 minutes.

---

## 1. Open Telegram and find BotFather

1. Open the Telegram app on your phone or computer.
2. Tap the **search icon** (magnifying glass, top of the screen).
3. Type exactly: `BotFather`
4. Tap the result that has a **blue verified tick** ✓ next to it. (There are fakes —
   the real one has the tick.)

---

## 2. Start a conversation

1. Tap the **Start** button (or type `/start` and send).
2. BotFather replies with a long list of commands it understands. That's normal.

---

## 3. Create your bot

1. Type this and send:

   ```
   /newbot
   ```

2. BotFather asks: **"Alright, a new bot. How are we going to call it?"**
   Type a display name — this can be anything, with spaces. It's what people see.
   Example: `My Assistant`

3. BotFather asks: **"Good. Now let's choose a username for your bot."**
   Type a username. **Rules:**
   - Must end in the word `bot`
   - Lowercase, no spaces
   - Must be unique (if it's taken, BotFather tells you and you try another)
   - Example: `my_assistant_123_bot`

---

## 4. Copy your token

BotFather replies with a message that includes a line like:

```
Use this token to access the HTTP API:
1234567890:AAH...a-long-string-of-letters-and-numbers
```

**That long string is your bot token. It's the password to your bot.**

1. Tap and hold the token, then **copy** it.
2. **Do not share it** with anyone. Anyone with the token controls your bot.

---

## 5. Put the token into Hermes

Paste it into the Hermes `.env` file as the value for `TELEGRAM_BOT_TOKEN`:

```
TELEGRAM_BOT_TOKEN=1234567890:AAH...your-token-here
```

Then start the gateway (your agent will do this for you).

---

## If you ever need the token again

Type this to BotFather:

```
/token
```

It lists your bots, you tap the one you want, and it re-sends the token.

## If you made a mistake

- Wrong name? Doesn't matter — the display name is cosmetic.
- Wrong username? Type `/mybots` → tap your bot → **Edit Bot** → change it.
- Lost the token? `/token` (above).

## Quick reference

| You type | It does |
|---|---|
| `/newbot` | Create a new bot |
| `/token` | Re-send a bot's token |
| `/mybots` | List your bots and edit them |
| `/setdescription` | Change the "What can this bot do?" text |
| `/setuserpic` | Change the bot's profile picture |

That's the whole thing. You now have a bot, and your agent takes over from here.
