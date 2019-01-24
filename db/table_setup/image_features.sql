CREATE TABLE `image_features` (
  `image_id` int(10) unsigned NOT NULL,
  `features` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  PRIMARY KEY (`image_id`),
  UNIQUE KEY `image_id_UNIQUE` (`image_id`),
  CONSTRAINT `fk_image_features_to_image_files` FOREIGN KEY (`image_id`) REFERENCES `image_files` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8