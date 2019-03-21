USE `radiodj`;

CREATE TABLE IF NOT EXISTS `setmetadata` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `metadata` varchar(1024) NOT NULL,
  `processed` bool NOT NULL DEFAULT 0,
  PRIMARY KEY (`ID`),
  INDEX(`processed`)
);