# Study Planner

A personalized study planner application that uses machine learning to generate optimized study schedules based on user preferences and weaknesses.

## Features

- Personalized study plans based on subjects and weaknesses
- Time slot organization (Morning, Afternoon, Evening)
- Progress tracking with feedback system
- Clean and organized output format
- Modern web interface with Next.js frontend
- Flask backend with ML model integration

## Project Structure

```
├── backend/             # Flask backend server
│   ├── app.py          # Main Flask application
│   └── ml_model.py     # ML model implementation
├── study-planner-frontend/  # Next.js frontend
│   ├── pages/          # React pages
│   ├── styles/         # CSS styles
│   └── config/         # Configuration files
└── studoo/             # ML model directory
```

## Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/AsifaBeedi/studoo.git
cd studoo
```

2. Install backend dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Install frontend dependencies:
```bash
cd ../study-planner-frontend
npm install
```

4. Start the backend server:
```bash
cd ../backend
python app.py
```

5. Start the frontend development server:
```bash
cd ../study-planner-frontend
npm run dev
```

## Usage

1. Open http://localhost:3000 in your browser
2. Add subjects and weaknesses
3. Generate a study plan
4. View and track your progress

## Technologies Used

- Frontend: Next.js, React
- Backend: Flask
- ML Model: Python
- Database: SQLite
- Styling: CSS, Font Awesome Icons
