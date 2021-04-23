alter user root@'localhost' identified by '{{ mysql_root_password | default("QTjT5Qq8ex3B0are") }}' ;
create user root@'127.0.0.1' identified by '{{ mysql_root_password | default("QTjT5Qq8ex3B0are") }}';
grant all on *.* to root@'127.0.0.1' with grant option;

create database {{schema_name}} DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;;
create user {{schema_name}}@'%' identified by '{{user_password|default("i_am_random_password,yeye")}}';
grant all on {{schema_name}}.* to {{schema_name}}@'%' with grant option;
