# Fortune Island Ellehacks 2026

Fortune Island is an interactive finance-based game designed to teach kids financial literacy through fun, scenario-based challenges. Players explore a virtual island, answer money-related questions and make decisions about saving, spending and investing to grow their in-game wealth.

The goal of Fortune Island is to make learning about budgeting, smart spending and financial responsibility engaging and accessible for younger audiences.

---
# Tech Stack

Backend: Django + Django Ninja (REST API)

Database: PostgreSQL (Neon)

Frontend/Game Engine: Phaser (JavaScript)

AI Integration: Gemini API (dynamic financial questions & explanations)

---
# Running the project 
To run the Fortune Island project locally, follow the setup instructions below.

## Clone the Repository

```bash
git clone https://github.com/xena-p/ellehacks-2026.git
cd ellehacks-2026
```

## Setup Backend
```bash
cd backend
```
### 1. Create the virtual environment
```bash
python -m venv venv
```

### 2. Activate the virtual environment  and install dependencies (windows)
```bash
venv\Scripts\activate
```
If on macOS / Linux:
```bash
source venv/bin/activate
```
### 3. Install the dependencies
```bash
pip install -r requirements.txt
```

## Environment Variables
In the file explorer, create a file called .env, inside of \backend.

Add the following variables:
```
DATABASE_URL=your_neon_postgres_connection_string

GEMINI_API_KEY=your_gemini_api_key
```
## Run migrations
```bash
python manage.py migrate
```

## Start Backend Server
```bash
python manage.py runserver
```

## The backend should now be running at:
```
http://127.0.0.1:8000/
```

---
# Frontend setup
Open a new terminal and navigate to the frontend folder:
```bash
cd frontend
```

Run the frontend:
```bash
npm install
npm run dev
```

---
# Features

🎮 Interactive island-based game environment

💰 Budgeting, saving, and spending challenges

🤖 AI-generated financial questions using Gemini

📊 Player progress tracking

🏆 Reward system for correct financial decisions

---
# Future Improvements

Leaderboards

Parent/Teacher dashboard

Expanded financial scenarios

More advanced investing simulations

