use ghgrabberdb;
CREATE TABLE changes (
id_change int(8) NOT NULL AUTO_INCREMENT PRIMARY KEY,
username varchar(32) NOT NULL,
msg varchar(9000) NOT NULL,
sent boolean NOT NULL DEFAULT FALSE,
dt timestamp
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;