-- Login as root user
CREATE DATABASE radiodj;

CREATE USER 'radiodj'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON radiodj.* TO 'radiodj'@'localhost';

CREATE USER 'radiodj'@'%' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON radiodj.* TO 'radiodj'@'%';

-- Needed for RadioDJ front end
GRANT SELECT ON mysql.* TO 'radiodj'@'%';

DROP PROCEDURE IF EXISTS `komf_upsert_songs`;

DELIMITER //
CREATE PROCEDURE `komf_upsert_songs` (i_path varchar(255),
									  i_song_type tinyint(2),
                                      i_id_genre int(11),
                                      i_duration double(11,5),
                                      i_artist varchar(255),
                                      i_album varchar(255),
                                      i_year varchar(4),
                                      i_copyright varchar(255),
                                      i_title varchar(255),
                                      i_publisher varchar(255),
                                      i_composer varchar(255)
)
BEGIN
	INSERT INTO `radiodj`.`songs`
	(
	`path`,
	`enabled`,
	`song_type`,
	`id_subcat`,
	`id_genre`,
	`weight`,
	`duration`,
	`artist`,
	`album`,
	`year`,
	`copyright`,
	`original_artist`,
	`title`,
	`publisher`,
	`isrc`,
	`bpm`,
	`composer`
	)
	VALUES
	(i_path,
	1,
	i_song_type,
	11,
	i_id_genre,
	50,
	i_duration,
	i_artist,
	i_album,
	i_year,
	i_copyright,
	'Unknown',
	i_title,
	i_publisher,
	'Unknown',
	0,
	i_composer
	)
	ON DUPLICATE KEY UPDATE
		`path`      = i_path,
        enabled     = 1,
		`song_type` = i_song_type,
		`id_genre`  = i_id_genre,
		`duration`  = i_duration,
		`artist`    = i_artist,
		`album`     = i_album,
		`year`      = i_year,
		`copyright` = i_copyright,
	    `title`     = i_title,
	    `publisher` = i_publisher,
		`composer`  = i_composer;

END
//
DELIMITER ;


DROP PROCEDURE IF EXISTS `komf_delete_song`;

DELIMITER //
CREATE PROCEDURE `komf_delete_song` (i_path varchar(255))
BEGIN

	DELETE FROM songs WHERE path = i_path;

END
//
DELIMITER ;
