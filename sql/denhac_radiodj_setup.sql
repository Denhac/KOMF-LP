-- Login as root user
CREATE DATABASE radiodj;

CREATE USER 'radiodj'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON radiodj.* TO 'radiodj'@'localhost';

CREATE USER 'radiodj'@'%' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON radiodj.* TO 'radiodj'@'%';

-- Needed for RadioDJ front end
GRANT SELECT ON mysql.* TO 'radiodj'@'%';
