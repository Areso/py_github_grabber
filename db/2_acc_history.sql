use ghgrabberdb;
CREATE TABLE acc_history (
id_record int(8) NOT NULL AUTO_INCREMENT PRIMARY KEY,
username varchar(32) NOT NULL,
followers_list varchar(9000) NOT NULL,
followers int(8) NOT NULL DEFAULT 0,
hash varchar(256) NOT NULL UNIQUE,
dt timestamp
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;