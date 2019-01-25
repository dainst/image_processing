CREATE TABLE `image_files` (
 `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
 `name` varchar(256) NOT NULL,
 `path` varchar(256) NOT NULL,
 `url` varchar(256),
 PRIMARY KEY (`id`),
 UNIQUE KEY `id_UNIQUE` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8