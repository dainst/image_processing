USE image_processing_db;

CREATE TABLE `image_names` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `file_name` varchar(256) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `file_name_UNIQUE` (`file_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8