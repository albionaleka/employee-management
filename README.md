# Employee Management System

A web-based employee management system built with Python and HTML, featuring automated testing with Selenium.

## Features

- Employee data management
- Web-based interface
- Automated testing suite using Selenium
- Production deployment ready

## Tech Stack

- **Backend:** Python (Django)
- **Frontend:** HTML
- **Testing:** Selenium

## Installation

### Prerequisites

- Python 3.x
- pip (Python package manager)
- Chrome (for Selenium tests)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/albionaleka/employee-management.git
cd employee-management
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python manage.py runserver
```

## Project Structure
```bash
employee-management/
├── management/         # Core management module
├── .gitignore          # Git ignore rules
└── tests/              # Selenium automated tests
```

## Testing

Run automated tests using Selenium:
```bash
python manage.py test management_site.tests
```

# Contributing

1. Fork the repository
2. Create a feature branch: ```git checkout -b feature/YourFeature```
3. Commit your changes: 
```git commit -m 'Add some feature'```
4. Push to the branch: ```git push origin feature/YourFeature```
5. Open a Pull Request