# OnlyPark

A vehicle parking management system with separate admin and user experiences: admins manage lots and spots, users search for parking and book a spot in real time. Built as a full-stack project for the Modern Application Development 2 (MAD 2) course.

## Features

**For users**
- Register and log in with a JWT-secured account
- Browse parking lots with live availability (available vs occupied spot counts)
- Book a spot with one click — the system auto-allocates the first free spot in the chosen lot
- Release a spot when leaving, with cost computed from actual parking duration and the lot's hourly rate
- View active bookings (with a running estimated cost) and full booking history
- Personal analytics dashboard: total spend, average cost per booking, favorite lot, spending trends over time, and per-lot usage breakdown
- Request a CSV export of their full booking history, generated asynchronously and emailed as an attachment

**For admins**
- Create, edit, and delete parking lots, with spots generated (or removed) automatically to match the configured spot count
- Deletion and spot-count reduction are blocked while spots are still occupied, so occupied spots can't be silently dropped
- Live view of every spot across all lots, including which vehicle/user occupies it and since when
- Admin dashboard with totals for users, lots, spots, revenue, active reservations, and occupancy rate
- Admin analytics: revenue trends, per-lot performance (bookings, revenue, unique users), and booking activity by hour of day
- Cache inspection endpoints (stats, health check, manual warm-up/clear) for the Redis-backed caching layer

**Background jobs**
- Daily reminder emails via Celery Beat — new-lot alerts if any lot was added in the last 24 hours, otherwise a nudge to users who haven't parked in 7+ days
- Automated monthly activity report emailed to every user, with a full breakdown of that month's bookings
- Asynchronous CSV export of a user's parking history, emailed on completion

A default admin account (`admin@onlypark.com`) is seeded automatically on first run.

## Tech stack

**Backend**
- Flask
- Flask-SQLAlchemy (ORM) with SQLite
- Flask-JWT-Extended for authentication
- Flask-Caching with Redis as the cache backend
- Celery + Redis for background jobs and scheduled tasks (Celery Beat)
- Flask-Mail for email delivery
- Flask-CORS
- Pandas (CSV export handling)

**Frontend**
- Vue 3 (Composition API, `<script setup>` style views)
- Vue Router with navigation guards for auth and role-based access
- Axios for API calls
- Chart.js via vue-chartjs for the analytics dashboards (bar, line, and doughnut charts)
- Bootstrap 5 for layout and styling
- Vite as the build tool

---

**Ankit Singh**
[LinkedIn](https://www.linkedin.com/in/ankit-singh-117925249/)
