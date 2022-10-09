USE ghgrabberdb;
CREATE USER IF NOT EXISTS 'ghgrabberuser'@'%' IDENTIFIED BY 'SuperPassword_2022';
/*--MySQL 5.7.6 or less --GRANT ALL ON `ghgrabberdb`.* TO 'ghgrabberuser'@'%' IDENTIFIED BY 'SuperPassword';*/
GRANT USAGE ON *.* TO 'ghgrabberuser'@'%' REQUIRE NONE WITH MAX_QUERIES_PER_HOUR 0;
GRANT ALL PRIVILEGES ON `ghgrabberdb`.* TO 'ghgrabberuser'@'%';

USE ghgrabberdb;
CREATE USER IF NOT EXISTS 'ghgrabberuser'@'localhost' IDENTIFIED BY 'SuperPassword_2022';
/*--MySQL 5.7.6 or less --GRANT ALL ON `ghgrabberdb`.* TO 'ghgrabberuser'@'localhost' IDENTIFIED BY 'SuperPassword';*/
GRANT USAGE ON *.* TO 'ghgrabberuser'@'localhost' REQUIRE NONE WITH MAX_QUERIES_PER_HOUR 0;
GRANT ALL PRIVILEGES ON `ghgrabberdb`.* TO 'ghgrabberuser'@'localhost';