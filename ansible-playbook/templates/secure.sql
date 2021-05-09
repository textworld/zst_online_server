alter user root@'localhost' identified by '{{ mysql_root_password | default("QTjT5Qq8ex3B0are") }}' ;
create user root@'127.0.0.1' identified by '{{ mysql_root_password | default("QTjT5Qq8ex3B0are") }}';
grant all on *.* to root@'127.0.0.1' with grant option;

create database {{mysql_schema}} DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;;
create user {{mysql_schema}}@'%' identified by '{{user_password|default("i_am_random_password,yeye")}}';
grant all on {{mysql_schema}}.* to {{mysql_schema}}@'%' with grant option;
