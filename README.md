# Campus Social Engagement Recommender System

A hybrid recommendation system that suggests campus clubs and activities to students using Content-Based Filtering (CBF) and Collaborative Filtering (CF).

## Features

- **Hybrid Recommendation System**
  - Content-Based Filtering using TF-IDF and cosine similarity
  - User-based Collaborative Filtering with cosine similarity
  - Dynamic weighting between CBF and CF recommendations

- **User Interface**
  - Student-facing pages: Login, Registration, Home, Club Recommendations, Profile
  - Admin-facing pages: Dashboard, Student/Club Management, Application Management

## Tech Stack

- **Backend**: Django with Django REST Framework
- **Frontend**: Vue 3 with Vite
- **Machine Learning**: scikit-learn for CBF and CF computations

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Generate synthetic data:
```bash
python generate_data.py
```

4. Run Django migrations:
```bash
python manage.py migrate
```

5. Start the Django development server:
```bash
python manage.py runserver
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

## Project Structure

```
campus_recommender/
├── campus_recommender/  # Django project
├── recommender/         # Django app
├── models/             # Model files
├── data/              # Dataset files
├── frontend/          # Vue.js project
├── templates/         # Django templates
└── README.md
```

## API Endpoints

- `POST /api/recommend/`: Get club recommendations
- `GET /api/clubs/`: List all clubs
- `GET /api/users/`: List all users
- `POST /api/users/`: Create new user
- `PUT /api/users/<id>/`: Update user
- `DELETE /api/users/<id>/`: Delete user

## License

MIT 