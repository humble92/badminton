Badminton Activities in the City of Toronto
============================================

Provide drop-in adult badminton programs in the City of Toronto

## Features

- Location based search for nearest badminton programs
- Searching condition available on the count of retrieving recreation centres
- Excel downloads for the search result

## Prerequisites

- Google Chrome browser installed
- [ChromeDriver](https://chromedriver.chromium.org/)
  - Currently, used version: ChromeDriver 102.0.5005.61
- Google Maps Geocoding API secret key

## Installation

1. Clone repository and set up .env variables with your favorite editors.

```bash
git clone https://github.com/humble92/badminton.git
cd badminton
cp .env_example .env
vi .env
```

2. Enter the virtual environment, then you can install dependant pakages. 
You can use any other python virtual environment tools instead of `pipenv`.

```bash
pipenv shell
pipenv install
```

## Run Server

Boot the server and enjoy it.

```bash
flask run
```

## Tips

1. When a recreation centre would newly be built, you can just delete 
`Recreation_Centres_Info.json` in the repository root directory. That's it. 
Brand-new information should be reflected.
