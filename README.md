# Projecs

A collection of various projects including surveys, car recommendation systems, DevOps studies, and more.

## Projects Overview

### Survey System
- **Directory**: `surveys/` & `survey_project/`
- **Description**: Django-based survey application with multi-question types, user/group management, image uploads, RTL Hebrew support, and results analytics dashboard with weighted scoring

### Bot Car System
- **Directory**: `bot_car_system/`
- **Description**: Telegram bot for car search and recommendations using OpenAI GPT models with Hebrew/English support

### FastAPI Car System
- **Directory**: `fastapi_car_system/`
- **Description**: FastAPI-based car recommendation REST API with OpenAI integration and JWT authentication

### Car Details API
- **Directory**: `car_details_api/`
- **Description**: APIs for retrieving car ownership details and traffic information with Hebrew/English mappings

### The Floor Game
- **Directory**: `the_floor/`
- **Description**: Discord bot game (The Floor) with 4×4 grid territories, player challenges, and duel resolution system

### Mapper
- **Directory**: `mapper/`
- **Description**: Backend and frontend application for mapping and location services using Google Maps API

### DevOps Study
- **Directory**: `devops_study/`
- **Description**: Kubernetes YAML configurations for deploying services (MongoDB, MySQL, Nginx) with monitoring dashboards

### Tests
- **Directory**: `tests/`
- **Description**: Test utilities and Google Docs integration helpers

### Configuration Files
- **`.env.example`** - Template for environment variables (API keys, tokens, secrets)
- **`manage.py`** - Django management script
- **`requirements.txt`** - Python dependencies
- **`survey_project/settings.py`** - Django settings with MEDIA configuration

## Security

All API keys and tokens are stored in environment variables. See `.env.example` for required variables. Never commit `.env` file.

## Setup

1. Copy `.env.example` to `.env` and fill in your API keys
2. Install dependencies: `pip install -r requirements.txt`
3. Set up Django: `python manage.py migrate`
4. Run server: `python manage.py runserver`
