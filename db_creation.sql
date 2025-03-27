-- sample commit by Ethan (comment)


-- create login table

CREATE TABLE IF NOT EXISTS Login (
	loginID SERIAL PRIMARY KEY,
	Username TEXT NOT NULL UNIQUE,
	Password TEXT NOT NULL
);


