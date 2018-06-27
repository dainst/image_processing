USE image_processing_db;

CREATE TABLE `image_name_mapping` (
  `id` int(11) NOT NULL,
  `filename` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1