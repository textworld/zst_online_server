## 产生大量测试数据

```mysql
set global log_bin_trust_function_creators=1;
use zst;
delimiter $$
CREATE FUNCTION rand_string(n int) RETURNS varchar(255)
begin        
  declare chars_str varchar(100) 
  default "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
  declare return_str varchar(255) default "";        
  declare i int default 0;
  while i < n do        
      set return_str=concat(return_str,substring(chars_str,floor(1+rand()*62),1));
      set i= i+1;        
  end while;        
  return return_str;    
end $$
delimiter ;

delimiter $$
CREATE  PROCEDURE `insert_data`(IN n int)
BEGIN
  DECLARE i INT DEFAULT 1;
    WHILE (i <= n ) DO
      INSERT into zst.slow_log_test (name, addr ) VALUEs (rand_string(20),rand_string(100));
            set i=i+1;
    END WHILE;
END $$
delimiter ;

call insert_data(1000000);

```