drop database if exists robot;

create database robot;

use robot;

grant select, insert, update, delete on robot.* to 'www'@'localhost' identified by 'www';

create table users (
    `id` bigint not null auto_increment,
    `passwd` varchar(50) not null,
    `admin` bool not null,
    `name` varchar(50) not null,
	UNIQUE INDEX `name_user_UNIQUE` (`name` ASC),
    primary key (`id`)
) engine=innodb default charset=utf8;

create table robots (
    `id` bigint not null auto_increment,
    `name` varchar(50) not null,
    `passwd` varchar(50) not null,	
    `r_type` varchar(50) not null,
    primary key (`id`)
) engine=innodb default charset=utf8;

create table comments (
    `id` bigint not null auto_increment,
    `robot_id` varchar(50) not null,
    `robot_name` varchar(50) not null,
	`r_position` varchar(50) not null,
    `r_image` blob not null,
    `r_time` real not null,
    primary key (`id`)
) engine=innodb default charset=utf8;