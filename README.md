# flask_projects
flask


#steps to install mysql in wsl/linux
sudo apt update
sudo apt install mysql-server
sudo service mysql start
sudo mysql_secure_installation
#to verify 
sudo systemctl status mysql
mysql -u root -p
sudo vim /etc/mysql/mysql.conf.d/mysqld.cnf
bind-address = 0.0.0.0
sudo systemctl restart mysql

to install all libraries to run the application --> pip install --no-cache-dir  -r  requirements.txt 


changed redis timeout  timing to 10 sec for testing please change as per your requirement 
#   h e a l t h s y n c  
 