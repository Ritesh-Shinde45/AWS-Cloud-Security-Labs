   #!/bin/bash
    sudo yum update -y
    
    #Install Apache web server (httpd)
    sudo yum install -y httpd
   
    sudo systemctl start httpd
    sudo systemctl enable httpd
    
    # Creating  a simple HTML file to verify the web server is running
    
    echo "<html><h1>Welcome to Apache Web Server on Amazon Linux!</h1><br> 
    <h1>My First EC2 Instance</h1> <br><br>
    Lab 02: Learning EC2 Service and setup alert on cost management </html>" >
     /var/www/html/index.html