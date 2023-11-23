DROP TABLE IF EXISTS sign_requests;
CREATE TABLE sign_requests (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  key TEXT NOT NULL,
  value TEXT NOT NULL,
  dt DATETIME DEFAULT current_timestamp
);