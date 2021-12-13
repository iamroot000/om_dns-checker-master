import mysql.connector

mydb = mysql.connector.connect(
  host="10.167.11.205",
  user="yrollrei",
  passwd="s22-C350",
  database="argus_v2"
)

mycursor = mydb.cursor()

mycursor.execute("CREATE TABLE domain_dnspoisonedchecker (id INT AUTO_INCREMENT PRIMARY KEY, domain VARCHAR(255), expectedresponse VARCHAR(255), beijing VARCHAR(255), shenzhen VARCHAR(255), inner_mongolia VARCHAR(255), heilongjiang VARCHAR(255), yunnan VARCHAR(255))")

