# Optimal Purchase Plan Estimator

A potential data product could be a forecasting and inventory management tool. The tool would allow companies to input historical receipt data and forecasted demand data and the tool would output an optimal purchase plan that minimizes total cost. The tool would allow for the customization of inventory and stockout costs per unit, as well as an assumed demand level. Users could vary the assumed demand level to find the minimum cost and optimal demand level for their specific needs. The tool would also provide visualizations of the past receipt data and forecasted demand data, allowing users to gain insights into trends and patterns that may be affecting their component's demand. Additionally, the tool would provide confidence intervals and probability distributions for the past receipt data, allowing users to better estimate the likelihood of future demand levels. 

The following flow-chart depicts these functions:
- Users can register their own accounts. Only registered users can use the system functionalities.
- Allows users to upload their products past monthly sales data to predict the future demand.
- Shows uploaded files to select the previously uploaded file.
- Shows selected file data after performing preprocessing and cleanup.
- Calculates Mean, Standard Deviation and Normal Distribution of sales data.
- Visualize the sales data using Seasonal Decompose Plots.
- Shows whether sales data is Stationary or Non-Stationary using plots.
- Shows the ARIMA model test results to explain whether the prediction values are reliable or not.
- Finally, shows the next 12 months predicted product demand.
- If additional product info file uploaded then shows the next 12 months shortfalls.
- If additional product info file uploaded then shows the additional cost incur because of shortfalls.

Application URL: https://purc-plan.wl.r.appspot.com/

***

**Home Page**

It is glance of product features

<img width="1417" alt="image" src="https://github.com/gramiset/purchase_planer/assets/54867104/4453baab-bf70-40d9-ae1e-c253ec94cb43">


**Sign Up**

To provide better data security, enabled the user signup functionality. Users can see only their data in the system. Sign up is must to use the system.
CAPTCHA included in below pages to ensure that humans are accessing the system, not the bots.
1) Sign Up 
2) Login
3) Forgot Password

<img width="1409" alt="image" src="https://github.com/gramiset/purchase_planer/assets/54867104/07dc1275-2b29-4619-8c03-7958fab584cd">


**OTP**

To enable further security, we have enabled Email OTP functionality. In all below cases, we sent OTP to verify the account.
1) New users
2) To reset password when forgot password
3) User trying to access from new IP address
4) Not logged in last 30 days

<img width="1414" alt="image" src="https://github.com/gramiset/purchase_planer/assets/54867104/814c5d81-3301-4fc3-8a83-4012c2555b42">


**Login**

Registered users can login into the system.

<img width="1413" alt="image" src="https://github.com/gramiset/purchase_planer/assets/54867104/58fceded-88fd-42a9-9c20-c85e0b9b4eb7">


**Forgot Password**

Users can reset the password if forgot. 

<img width="1416" alt="image" src="https://github.com/gramiset/purchase_planer/assets/54867104/436f5679-17d2-44da-9125-9fc632d3c831">


**User Home/Show Files**

As it is data analytics application, we need to select the data to use in subsequent functionalities. Whenever user logged in, application redirects to Show Files page where user can see their previously uploaded files. If no files uploaded, user redirects to File Upload Page. 

User must select one file from Show Files page to use subsequent features of the system. 

User can delete teh previously uploaded files also. 

<img width="1416" alt="image" src="https://github.com/gramiset/purchase_planer/assets/54867104/953d1e4c-430c-4d21-944d-9bcf0b616d88">


**File Upload**

User can input their products past monthly sales data along with some additional product info such as inventory cost, stockuout cost and expecting monthly stock in future to predict the future demand, shortfalls and adding cost because of shortfalls. 

We can download sample files from File Upload Page. 

<img width="1429" alt="image" src="https://github.com/gramiset/purchase_planer/assets/54867104/68d71bb7-727a-4ebf-bdc1-1a5d2d2b072c">

After upload, user redirects to Show Files page. File which uploaded will be showing as IN-PROGRESS state, once preprocessing completed, it will move to SUCCESS or FAIELD state. If it is success, user can select the file to see the data uploaded and results. 

<img width="1419" alt="Screenshot 2023-06-07 at 7 25 54 AM" src="https://github.com/gramiset/purchase_planer/assets/54867104/512a44df-8430-4a08-9c6c-3f9ef90d858e">

After preprocessing completed. 

<img width="1424" alt="image" src="https://github.com/gramiset/purchase_planer/assets/54867104/ff861227-6ba3-4cf3-bd04-10c80a836c47">


**View Data**

After user selecting the file in Show Files page, it redirects to View Data page. 

It is preprocessed data, where we done cleanup to add the missing months sales data, replaced missing values with "mean", etc. 

It shows Product Info and first 100 records of monthly sales data. 

<img width="1436" alt="image" src="https://github.com/gramiset/purchase_planer/assets/54867104/dd753ebd-54db-4ab0-8b1b-8af08061b579">


**Explore Data**

It provides stats of past sales data such as Mean, Standard Deviation and Normal Distribution (Probability Density Function)

These stats helps and gives some more details to users to understand their products past sales data. 

<img width="1434" alt="image" src="https://github.com/gramiset/purchase_planer/assets/54867104/f5202f2f-2496-4e0b-a703-db44ed719449">


**Visualize Data**

Users can see visually their past sales data trends in Seasonal Decompose Plots. 

<img width="1419" alt="image" src="https://github.com/gramiset/purchase_planer/assets/54867104/a263e6d6-3ccc-4a53-baaa-5b9582f804e0">


**Stationary Test Results**

Data Sets are 2 types 
1) Stationary 
2) Non-Stationary

System show the Stationary Test results (ADF and Adfuller Tests) along with plots, so user can understand the products past sales graph better. 

![image](https://github.com/gramiset/purchase_planer/assets/54867104/42b37d6a-5851-4d1c-9818-1fb9f7695bd5)


**ARIMA Model Test**

We are using Auto ARIMA to predict the future demand of product. 

System shows the ARIMA model which we used, RMSE error and Test results plot. 

It gives the more confidence on the results. User can decide whether he can trust the results or not based on RMSE error and Test results plot.

<img width="1414" alt="image" src="https://github.com/gramiset/purchase_planer/assets/54867104/d0d6404f-c5ba-4d88-a888-1bb2b4ac68c5">


**Product Demand Estimation**

It is main results page. System shows the next 12 months demand for each product. 

<img width="1414" alt="image" src="https://github.com/gramiset/purchase_planer/assets/54867104/d923ee17-73bd-4685-b867-89b4a828679d">

If user also uploaded the product info file with inventory cost, stockout cost and expecting monthly stock, then system shows the shortfalls and incur cost of shortfalls also in this page.

![image](https://github.com/gramiset/purchase_planer/assets/54867104/ab00c23b-dced-4a19-996c-8df03e3f0007)


**Update Profile**

Users can update their details. 

<img width="1419" alt="image" src="https://github.com/gramiset/purchase_planer/assets/54867104/c4aa9bd7-02cd-4db2-ac92-acaedb893d41">


**Change Password**

Users can change their password. 

<img width="1415" alt="image" src="https://github.com/gramiset/purchase_planer/assets/54867104/4acf7208-093c-4dba-874a-6476a1a0c4f3">


**Logout**

For security resons, we recommend users logout from system if they are not using. 


***

Below are the application deployment steps. If end user, user no need to worry about these details as it is website already deployed in Google Cloud to use. 

**Below steps only for developers who want to utilize this code.**

**Project Applications**

This project contaisn 2 application
1) Website App
2) API - which is helper and invokes by the website app whenever file uploaded by user to do the preprocessing as speperate process as it is High Latency Job, takes couple of minutes. 

- We need to deploy both the applications in Google cloud or we need to run both the applications in Local on different ports. 
- We need to **update the API url** in Website App config files. 
- We need **Google Cloud** account, please register one. 
- We need **Google Cloud Project**, please create one in Google Cloud Portal. 
- We need **Postgres** Database, please create one in Google Cloud SQL Page. 
- We need to create **Google cloud storage bucket**. Please upload bucket information in **util_file.py** file. 
- Please upload **sample** folder from **static** folder into **Google cloud storage bucket**
- We need **SENDINBLUE** account to send the OTP emails, please setup one. 
- We need **Google reCaptcha V2** account also, please setup one. 

***

**Database Tables**

System requires Postgres database, please update the postgres details in both Webiste APP and API config files. 

We need below tables

**1) user_profile**

CREATE TABLE user_profile (
	id serial,
	fname VARCHAR (50) NOT NULL,
	lname VARCHAR (50) NOT NULL,
	email VARCHAR (255) UNIQUE NOT NULL,
	dob DATE NOT NULL,
	country VARCHAR (3) NOT NULL,
	gender VARCHAR (1) NOT NULL,
	password TEXT NOT NULL,
	is_verified boolean NOT NULL default false,
	is_admin boolean NOT NULL default false,
	otp VARCHAR (6),
	ip_addr TEXT [],
	last_logged_on TIMESTAMP,
	inc_login_att integer default 0,
	created_on TIMESTAMP default current_timestamp,
	updated_on TIMESTAMP default current_timestamp,
	PRIMARY KEY(id)
);

**2) files**

CREATE TABLE files (
	id serial,
	user_id integer NOT NULL,
	file_id VARCHAR (255) UNIQUE NOT NULL,
	is_prod_info_avl boolean NOT NULL,
	status VARCHAR (20) NOT NULL,
	created_on TIMESTAMP default current_timestamp,
	updated_on TIMESTAMP default current_timestamp,
	PRIMARY KEY(id),
    CONSTRAINT fk_user_id
      FOREIGN KEY(user_id)
      REFERENCES user_profile(id)
);

**3) system_secrets**

CREATE TABLE system_secrets (
	function VARCHAR (255) NOT NULL,
	name VARCHAR (255) NOT NULL,
	value VARCHAR (255) NOT NULL,
	created_on TIMESTAMP default current_timestamp,
	updated_on TIMESTAMP default current_timestamp,
    PRIMARY KEY(function, name)
)

Insert below secrets before start application deployment. 

INSERT INTO system_secrets (function, name, value) VALUES ('CAPTCHA', 'site_key', '<Replace Value>')
INSERT INTO system_secrets (function, name, value) VALUES ('CAPTCHA', 'secret_key', '<Replace Value>')
INSERT INTO system_secrets (function, name, value) VALUES ('SENDINBLUE_EMAIL', 'email', '<Replace Value>')
INSERT INTO system_secrets (function, name, value) VALUES ('SENDINBLUE_EMAIL', 'api_key', '<Replace Value>')


***

**Google Cloud Deployment Steps**
  
**Step 1: Install Google Cloud CLI**
  
Go To: https://cloud.google.com/sdk/docs/install
Download: https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-433.0.1-darwin-x86_64.tar.gz
  
**Step 2:** Move tar file to some location where we need to keep
Extract Tar file
go to google-cloud-sdk folder after extract
Then Run ./install.sh
Then Run ./bin/gcloud init
Then Run source ~/.zshrc

**Step 3: Install App Engine**
gcloud components install app-engine-python
  
**Step 4: Set project**
gcloud config set project <project id>
  
**step 5: Enable the Cloud APIs. **
gcloud services enable cloudbuild.googleapis.com
gcloud services enable sqladmin.googleapis.com

**Step 6:** Update the below configuration in app.yaml in api folder
  
env_variables:
  APP_ENV: 'gcp'
  PGDB_USER: '<postgres user name>'
  PGDB_PWD: '<postgres password>'
 
**Step 7: Deploy API code** 
Go to api folder and run below command

gcloud app deploy

At the end, it prints below output

Deployed service [api] to [https://api-dot-<project id>.wl.r.appspot.com]

You can stream logs from the command line by running:
  $ gcloud app logs tail -s api

To view your application in the web browser run:
  $ gcloud app browse -s api

**Step 8:** Update the below configuration in app.yaml in app folder
  
env_variables:
  APP_ENV: 'gcp'
  PGDB_USER: '<postgres user name>'
  PGDB_PWD: '<postgres password>'

**Step 9:** Update the above api url in gcp.config file in app/config folder
  
**Step 10: Deploy Web App**
Go to app folder and run below command
  
At the end, it prints below output

Deployed service [default] to [https://<project id>.wl.r.appspot.com]

You can stream logs from the command line by running:
  $ gcloud app logs tail -s default

To view your application in the web browser run:
  $ gcloud app browse -s default
  
  
***

**Google Cloud Service Logs**
 
We can stream both APP and API logs using below commands
  
gcloud app logs tail -s default  
gcloud app logs tail -s api

***
  
**Local Running Steps in Mac**

Install software
  
- brew install git
- brew install python
- pip3 install flask
- pip3 install flask-reCaptcha
- pip3 install pandas
- pip3 install bcrypt
- pip3 install psycopg2
- pip3 install gunicorn
- pip3 install sib_api_v3_sdk
- pip3 install google-cloud-storage

If any missing packages, application shows error, please install them also.
  
Update the main.py with ports in both app and api

run both main.py files


