CREATE TABLE users
(
    sender_id        VARCHAR(255) PRIMARY KEY,
    message_id       INTEGER,
    schedule_counter INTEGER,
    homework_counter INTEGER,
    marks_counter    INTEGER,
    holidays_counter INTEGER,
    clear_counter    INTEGER,
    options_counter  INTEGER,
    help_counter     INTEGER,
    about_counter    INTEGER,
    inline_counter   INTEGER
);