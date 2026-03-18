# Simple Flask Web Server

This is a simple web server built with Python Flask that provides:
- Login page with username/password authentication
- Dashboard showing company structure and a button to view Telegram logs
- Logs page displaying concatenated content of all memory/*.md files

## Requirements

- Python 3.x
- Flask

## Installation

1. Install Flask if not already installed:
   ```bash
   pip install flask
   ```

## Usage

1. Navigate to the webserver directory:
   ```bash
   cd /path/to/webserver
   ```

2. Run the server:
   ```bash
   python app.py
   ```

3. Open your web browser and go to:
   ```
   http://localhost:8080
   ```

## Default Credentials

Upon starting the server, default credentials are printed to the console:
```
=== DEFAULT CREDENTIALS ===
vasiliy:vasiliy123
diego:diego123
user2:user2pass
user3:user3pass
user4:user4pass
===========================
```

These credentials can be used to log in to the web interface.

## Configuration

- The server runs on port 8080 and binds to 0.0.0.0 (accessible from any interface).
- To change the port or host, modify the `app.run()` call in `app.py`.

## Notes

- This is a simple example for demonstration purposes. In a production environment, you should:
  - Use proper password hashing (e.g., bcrypt)
  - Store credentials in a secure database
  - Use a strong secret key
  - Disable debug mode