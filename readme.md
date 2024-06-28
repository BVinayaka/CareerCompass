## Overview
The Career Compass project is an innovative tool designed to support individuals in their career development journey. It is especially beneficial for students and early-career professionals who are exploring their career options and seeking guidance in a competitive job market. By providing personalized insights and practical resources, Career Compass empowers users to enhance their job application materials and identify suitable job opportunities. This comprehensive approach not only simplifies the complex process of career planning but also increases the chances of users finding fulfilling and relevant career opportunities.

## Features

### Career Recommendation
The career recommendation functionality utilizes a comprehensive quiz to assess users' skills, interests, and personality traits. By analyzing the responses, the system generates tailored career suggestions that align with the user's unique profile. This feature not only broadens the users' understanding of potential career paths but also provides a clear rationale for each recommendation, helping users make informed decisions about their professional futures.

### Resume Builder
The resume builder component is designed to streamline the resume creation process. It offers a variety of templates suitable for different industries and experience levels, ensuring that users can present their credentials in a polished and professional manner. The tool provides step-by-step guidance and practical examples for each section of the resume, such as the summary, work experience, and skills. Additionally, it allows for customization, enabling users to tailor their resumes to reflect their individual achievements and career aspirations accurately.

### Job Recommendation
The job recommendation feature leverages the information from the users' resumes to suggest relevant job opportunities. By parsing the resume content, the system identifies key skills and experiences, matching them with suitable job listings. This targeted approach not only enhances the efficiency of the job search process but also increases the likelihood of users finding positions that closely match their career goals and qualifications.

## Installation Instructions

### Prerequisites
- **Python 3.11**: Ensure Python 3.11 is installed. Download it from [Python.org](https://www.python.org/downloads/release/python-3111/).
- **pip**: Python package installer. It is included with Python 3.11.
- **Visual Studio**: Recommended for development and debugging.

### Python Packages
To install the necessary Python packages, run the following commands:

```bash
pip install Flask
pip install Flask-Mail
pip install Flask-SQLAlchemy
pip install gunicorn
pip install pandas
pip install pytz
pip install bcrypt
pip install pymongo
pip install opencv-python
pip install tqdm
pip install openpyxl
pip install scikit-learn
pip install python-dotenv
pip install requests
pip install spacy
pip install PyPDF2
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-2.3.1/en_core_web_lg-2.3.1.tar.gz
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_md-2.3.1/en_core_web_md-2.3.1.tar.gz
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-2.3.1/en_core_web_sm-2.3.1.tar.gz
```


## Usage Instructions

### Running the Application
1. **Clone the Repository**: Clone the project repository to your local machine.
2. **Set Up Environment Variables**: Create a `.env` file in the root directory of the project and configure the necessary environment variables.
3. **Initialize Database**: Ensure that the database (MongoDB) is running and properly configured. Run `mongodb.py` to set up the database from the xlsx file.
4. **Start the Application**: Run the application using the following command:
   ```bash
   python main.py
   ```

### Compiling Procedure
There is no explicit compiling needed as this is a Python-based project. Ensure all dependencies are installed, and the application can be run directly using the above command.

## Hardware/Software Requirements
- **Operating System**: Windows, macOS, or Linux
- **Processor**: 1 GHz or faster
- **RAM**: 4 GB or more
- **Python**: Version 3.11
- **Dependencies**: Listed in the Python Packages section

## Acknowledgments
- **Spacy Models**:
  - [en_core_web_lg-2.3.1](https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-2.3.1/en_core_web_lg-2.3.1.tar.gz)
  - [en_core_web_md-2.3.1](https://github.com/explosion/spacy-models/releases/download/en_core_web_md-2.3.1/en_core_web_md-2.3.1.tar.gz)
  - [en_core_web_sm-2.3.1](https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-2.3.1/en_core_web_sm-2.3.1.tar.gz)