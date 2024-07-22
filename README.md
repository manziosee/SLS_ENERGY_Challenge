# Twitter Analysis Web Service

## Overview

This Django-based web service analyzes Twitter data to provide user recommendations based on tweet interactions, hashtags, and keywords. It uses PostgreSQL for data storage and is optimized for performance with caching.

## Components

1. **ETL Process (`api/etl.py`)**
   - Extracts, transforms, and loads Twitter data from a JSON file into PostgreSQL.

2. **Data Models (`api/models.py`)**
   - **Tweet Model:** Stores tweet details.
   - **User Model:** Stores user information.

3. **API Endpoint (`api/views.py`)**
   - **`/api/q2`:** Provides user recommendations based on interaction, hashtag, and keyword scores.

4. **URL Configuration (`api/urls.py`)**
   - Maps API endpoint to the view.

5. **Settings (`twitter_analysis/settings.py`)**
   - Configures Django settings and PostgreSQL database.

6. **Testing (`api/tests.py`)**
   - Unit tests for the API endpoint.

## Setup

### Prerequisites

- Python 3.8+
- Django 4.2.5
- PostgreSQL

### Installation

1. Clone the repo:
   ```bash
   git clone https://github.com/yourusername/twitter_analysis.git
   cd twitter_analysis
   ```

2. Set up virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

3. Configure PostgreSQL in `twitter_analysis/settings.py`.

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

### Load Data

Run the ETL process to load data:
```bash
python manage.py load_tweets path/to/tweets.json
```

### Run Server

Start the development server:
```bash
python manage.py runserver
```

### Test

Run tests to check functionality:
```bash
python manage.py test
```

## API

- **Endpoint:** `/api/q2`
- **Method:** GET
- **Parameters:**
  - `user_id` (required): User ID for recommendations.
  - `type` (required): Interaction type (`reply`, `retweet`, `both`).
  - `phrase` (required): Keyword phrase.
  - `hashtag` (required): Hashtag.

- **Response:**

  ```json
  {
      "recommendations": [
          {
              "user_id": "12345",
              "screen_name": "user123",
              "description": "User description",
              "contact_tweet_text": "Latest tweet text"
          }
      ]
  }
  ```

---

