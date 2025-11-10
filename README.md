# RankStuff

A web app for group decision-making through ranked voting.

## What It Does

Create polls, share a link, and let people rank options in order of preference. Results are aggregated using the Borda Count algorithm.

## Tech Stack

- **Frontend**: Angular
- **Backend**: FastAPI (Python)
- **Database**: MongoDB
- **Server**: NGINX on DigitalOcean

## Running Locally

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 3000
```

### Frontend
```bash
cd frontend
npm install
ng serve
```

## Deployment

Hosted on DigitalOcean with NGINX serving the frontend on port 80 and proxying API requests to the FastAPI backend on port 3000.

See `design_doc.md` for detailed architecture and deployment configuration.

## License

MIT
