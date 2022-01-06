This file belongs to [Kaggle](https://www.kaggle.com/rohankayan/years-of-experience-and-salary-dataset). 

You can !wget it for the exercises presented by Luka

```
!wget -O salary_dataset.zip https://github.com/AlexanderLavelle/ALWorks/blob/main/TensorFlow%20Dev%20Cert/Luka/2%20-%20Regression/Years%20of%20experience%20and%20Salary%20dataset.zip?raw=true  
import zipfile
# Unzip the downloaded file
zip_ref = zipfile.ZipFile('salary_dataset.zip', "r")
zip_ref.extractall()
zip_ref.close()
```
