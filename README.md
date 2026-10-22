# Patient Vitals API

A small REST API that takes patient vitals (blood pressure, glucose, age), checks them, stores them, and gives back the history and an average summary. Built with FastAPI. Records are kept in memory, so they disappear when the server stops.

## Setup (VS Code)

1. Open the `patient_vitals_api` folder in VS Code.
2. Make a virtual environment in the terminal:

   ```
   python -m venv .venv
   ```

3. Activate it:

   - Windows: `.venv\Scripts\activate`
   - Mac or Linux: `source .venv/bin/activate`

4. Install the packages:

   ```
   pip install -r requirements.txt
   ```

5. Press `Ctrl+Shift+P`, choose **Python: Select Interpreter** and pick the `.venv` one.

## Run

```
uvicorn app.main:app --reload
```

The API is now at http://127.0.0.1:8000. Swagger docs are at http://127.0.0.1:8000/docs, where you can also try every endpoint from the browser.

## Endpoints

| Method | Path | What it does |
| --- | --- | --- |
| GET | `/health` | Returns `{"status": "ok", "timestamp": ...}` with the current UTC time |
| POST | `/vitals` | Validates and saves one vitals record, returns it with status 201 |
| GET | `/patients/{patient_id}/vitals` | All records for a patient, newest first. Optional `?limit=N` |
| GET | `/patients/{patient_id}/summary` | Average systolic, diastolic, glucose and the record count |

Request body for `POST /vitals`:

```json
{
  "patient_id": "P-1001",
  "age": 45,
  "blood_pressure": { "systolic": 120, "diastolic": 80 },
  "glucose_level": 95.5
}
```

## Validation rules

Anything that breaks a rule gets **400 Bad Request** and nothing is saved. A wrong data type (for example `"age": "forty"`) is treated the same way.

| Field | Rule |
| --- | --- |
| patient_id | required, text, not empty (spaces are trimmed) |
| age | whole number, 0 to 120 |
| blood_pressure.systolic | whole number, 50 to 300 |
| blood_pressure.diastolic | whole number, 30 to 200 |
| glucose_level | number greater than 0 |

Every problem is listed, so one request shows all mistakes:

```json
{
  "detail": [
    { "field": "age", "message": "age must be an integer between 0 and 120 (got 150)" },
    { "field": "glucose_level", "message": "glucose_level must be a number greater than 0 (got 0)" }
  ]
}
```

## Try it with curl

Open a second terminal (the server keeps running in the first). The JSON bodies are in the `samples` folder, so the commands look the same on every system. On Windows PowerShell use `curl.exe` instead of `curl`.

```
curl http://127.0.0.1:8000/health

curl -X POST http://127.0.0.1:8000/vitals -H "Content-Type: application/json" -d @samples/valid.json

curl -X POST http://127.0.0.1:8000/vitals -H "Content-Type: application/json" -d @samples/valid_2.json

curl http://127.0.0.1:8000/patients/P-1001/vitals

curl "http://127.0.0.1:8000/patients/P-1001/vitals?limit=1"

curl http://127.0.0.1:8000/patients/P-1001/summary
```

Now the error cases. Add `-i` to see the status line.

```
curl -i -X POST http://127.0.0.1:8000/vitals -H "Content-Type: application/json" -d @samples/bad_range.json

curl -i -X POST http://127.0.0.1:8000/vitals -H "Content-Type: application/json" -d @samples/bad_types.json

curl -i "http://127.0.0.1:8000/patients/P-1001/vitals?limit=0"

curl -i http://127.0.0.1:8000/patients/nobody/summary
```

The summary for P-1001 after the two valid posts:

```json
{
  "patient_id": "P-1001",
  "record_count": 2,
  "averages": { "systolic": 127.5, "diastolic": 84.0, "glucose": 102.75 }
}
```

## Try it with Postman

1. New request, method **GET**, URL `http://127.0.0.1:8000/health`, press Send.
2. New request, method **POST**, URL `http://127.0.0.1:8000/vitals`. Under Body choose **raw** and **JSON**, paste the contents of `samples/valid.json`, press Send. You should get 201.
3. Change `age` to `150` and send again. You should get 400 with a message.
4. Make **GET** requests to `/patients/P-1001/vitals` and `/patients/P-1001/summary`.

If you use the VS Code REST Client extension, the file `requests.http` has all of these requests ready to click.

## Tests

```
pytest
```

- `tests/unit` tests the validation models, the error messages, the storage and the summary maths directly.
- `tests/integration` tests the real endpoints with FastAPI's test client: valid submissions, out-of-range values (including the exact limits), wrong data types, missing fields, broken JSON, `limit`, the summary and 404.

## Folder structure

```
patient_vitals_api/
  app/
    main.py          creates the app
    models.py        request and response models (the validation rules)
    errors.py        turns validation errors into readable messages
    handlers.py      makes validation errors return 400
    storage.py       in-memory storage
    summary.py       average calculation
    routes/
      health.py      GET /health
      vitals.py      POST /vitals and the two patient endpoints
  tests/
    helpers.py       sample payloads shared by the tests
    unit/
    integration/
  samples/           JSON bodies for curl and Postman
  .vscode/           run and test settings
  requests.http      ready-made requests
  requirements.txt
  pytest.ini
  README.md
```

## Choices I made

- FastAPI answers invalid input with 422 by default. The task asks for 400, so `handlers.py` changes that.
- `GET /patients/{id}/vitals` returns the newest record first, and `limit` keeps the newest ones.
- A patient with no records gets an empty list from the vitals endpoint and a 404 from the summary, because there is nothing to average.
- Averages are rounded to two decimals.
- `POST /vitals` returns 201 and the saved record, with an `id` and a UTC `recorded_at` time.

## Limits

- Everything is in memory, so a restart wipes the data.
- No login. Anyone who can reach the server can use it.
- Use made-up data only, not real patient information.
