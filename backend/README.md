# BizPadi

WhatsApp AI Companion for Nigerian SMEs. Finds funding, guides applications, tracks deadlines.

## Structure

```
bizpadi/
├── landing/         Static landing page (index.html)
├── app/             FastAPI application
├── data/            Seed funding opportunities
├── main.py          Server entry point
├── requirements.txt Python dependencies
└── render.yaml      Render deployment config
```

## Landing Page

Open `landing/index.html` in a browser — no build step needed.

To host it free: drag the `landing/` folder to Netlify Drop at app.netlify.com/drop.

## Backend Setup

```bash
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows

pip install -r requirements.txt
cp .env.example .env
# Fill in your keys in .env

uvicorn main:app --reload --port 8000
```

Open `http://localhost:8000/docs` to test.

## Environment Variables

| Key | Description |
|-----|-------------|
| `GROQ_API_KEY` | LLM + Whisper transcription |
| `TWILIO_ACCOUNT_SID` | WhatsApp gateway |
| `TWILIO_AUTH_TOKEN` | WhatsApp gateway |
| `TWILIO_WHATSAPP_NUMBER` | Sandbox number |
| `DATABASE_URL` | PostgreSQL connection string |
| `TONATIVE_API_KEY` | Multilingual layer (when released) |
| `ELEVENLABS_API_KEY` | Voice replies (optional) |

## Deployment

Render reads `render.yaml` automatically. Add env vars in the Render dashboard and deploy.

Webhook URL: `https://your-app.onrender.com/webhook/whatsapp`
