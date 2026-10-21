# PeopleDesk Frontend

## Run
Start the FastAPI application, then serve this directory on a CORS-enabled origin:

```powershell
python -m http.server 5500 --directory frontend
```

Open `http://127.0.0.1:5500`. The API defaults to `http://127.0.0.1:8000`. To use another API origin, set `window.PEOPLEDESK_API_BASE` before `script.js` loads.

## Connected API
- Authentication: `POST /user/login`, `POST /user/logout`
- Account: `PUT /user/update-account`
- Employee directory: `GET /employee/`, `GET /employee/{employee_id}`, `POST /employee/create_employee`, `PUT /employee/update_employee/{employee_id}`, `GET /employee/me`
- Managers: `POST /manager/create_manager`, `GET /manager/`, `GET /manager/me`
- Attendance: `GET /attendance/me`, `GET /attendance/employee/{employee_id}`, `GET /attendance/`, `POST /attendance/check-in`, `PUT /attendance/check-out`, `POST /attendance/employee/{employee_id}/check-in`, `PUT /attendance/employee/{employee_id}/check-out`
- Leave: `POST /leave/apply`, `GET /leave/me`, `GET /leave/`, `PUT /leave/{leave_id}/review`
- Salary: `POST /salary/generate/{employee_id}?year=...&month=...`, `GET /salary/salary/{employee_id}?month=...&year=...`, `GET /salary/`

The frontend uses role checks to tailor navigation and actions. Backend authorization remains authoritative. Employee self-service requests use the authenticated session; employee IDs are only sent for manager/admin lookups where the API permits them.
