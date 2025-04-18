
# TManage - Task Management System

## 💡 Objective

Develop a task management system with Role-Based Access Control (Admin, Manager, User) and JWT Authentication. Managers can assign tasks with deadlines, receive notifications for missed tasks, and automatically deactivate users who repeatedly fail to complete tasks. Managers can also manually reactivate users.

---

## 🔗 Problem Statement

Build a secure, role-based web application with the following core features:

### 1. User Management
- CRUD operations for users with roles: **Admin**, **Manager**, and **User**.
- JWT-based authentication (Register, Login, Logout).

### 2. Role-Based Access
- **Admin**: Full access to all endpoints.
- **Manager**:
  - Assign tasks with deadlines.
  - View task progress.
  - Receive notifications on missed deadlines.
  - Manually activate/deactivate users.
- **User**:
  - View assigned tasks.
  - Update task status (mark complete/incomplete).

### 3. Task Management
- Assign tasks with deadlines.
- Mark tasks as completed or missed.
- Notify managers via email when a task is missed.
- Automatically deactivate users who miss 5 tasks.
- Managers can manually reactivate deactivated users.

---

## ⚙️ Technical Stack

### Backend
- **Language**: Python
- **Framework**: Django, Django REST Framework
- **Database**: SQLite
- **Authentication**: JWT (with refresh token support)

### APIs
- RESTful endpoints for user and task management
- Role-based permission checks using custom middleware/permissions

### Notifications
- Email notification to manager when a user misses a task deadline

### Deactivation Logic
- Automatic: User is deactivated after missing 5 tasks
- Manual: Manager can activate/deactivate users from the system

---

## 📁 Project Structure

```
tmanage/
│
├── manage.py
├── requirements.txt
├── README.md
│
├── users/               # User CRUD, role management, JWT auth
│   └── views.py
│   └── models.py
│   └── permissions.py
│
├── tasks/               # Task creation, updates, status tracking
│   └── views.py
│   └── models.py
│   └── notifications.py
│
└── tmanage/             # Main Django settings and config
    └── settings.py
    └── urls.py
```


## 🧠 Apps Overview

- **users**: Manages authentication, registration, profiles, and permissions.
- **tasks**: Core task management logic — creation, assignment, deadline dates and status


---

## ✅ Setup Instructions

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd tmanage
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

6. Start the development server:
   ```bash
   python manage.py runserver
   ```

---

## 📬 Postman Collection

A sample Postman collection with:
- JWT Authentication (register, login)
- User CRUD
- Task assignment and updates
- Notification demo

> *(Exported file located in the postman folder)

---


