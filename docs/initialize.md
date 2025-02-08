```
sudo mysql -u root -p
```

```
use mysql
```

```
UPDATE user SET plugin='mysql_native_password' WHERE user='root';
flush privileges;
```

```
ALTER user 'root'@'localhost' identified by 'my_password';
```

```
python src/init_db.py
```
