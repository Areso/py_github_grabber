use ghgrabberdb;
CREATE TABLE repo_history (
id_record int(8) NOT NULL AUTO_INCREMENT PRIMARY KEY,
repourl varchar(128) NOT NULL,
watchers_count int(8) NOT NULL DEFAULT 0,
stargazers_count int(8) NOT NULL DEFAULT 0,
forks_count int(8) NOT NULL DEFAULT 0,
watchers varchar(1000) DEFAULT NULL,
stargazers varchar(10000) DEFAULT NULL,
forkers varchar(4000) DEFAULT NULL,
issues_count int(8) NOT NULL DEFAULT 0,
pr_count int(8) NOT NULL DEFAULT 0,
hash varchar(256) NOT NULL UNIQUE,
dt timestamp
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;