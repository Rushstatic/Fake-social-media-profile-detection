# Fake Buster - AI-Powered Social Media Account Detector

A full-stack application that analyzes public Instagram and X profiles to detect fake accounts and bots in real-time using a custom-trained machine learning model and generative AI.
# Fake Buster - AI-Powered Social Media Account Detector  

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)  
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)  
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)  
![XGBoost](https://img.shields.io/badge/XGBoost-FF6600?style=for-the-badge&logo=xgboost&logoColor=white)  
![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black)  
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)  
![Framer Motion](https://img.shields.io/badge/Framer--Motion-E10098?style=for-the-badge&logo=framer&logoColor=white)  
![Google Gemini API](https://img.shields.io/badge/Google%20Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white)  
![ScrapingDog](https://img.shields.io/badge/ScrapingDog-FF5733?style=for-the-badge&logo=dog&logoColor=white)  
![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)  


## 🚀 Key Features
- **Live Data Analysis**: Scrapes live profile data using a Python backend and the ScrapingDog API.
- **Advanced ML Model**: Utilizes an XGBoost classifier with Natural Language Processing (NLP) to analyze profile statistics and bio text for nuanced detection.
- **Generative AI Reports**: Integrates Google's Gemini API to provide human-like explanations and points of caution for each prediction.
- **Dynamic Frontend**: A responsive, animated, and dark-mode-enabled frontend built with React.
- **Downloadable Reports**: Users can download a full analysis of any profile as a formatted PDF document.


## 🎯 Application in Action


### 📌 Main Interface
[Main Interface]  
<img width="2856" height="1536" alt="New Light mode Card" src="https://github.com/user-attachments/assets/39f658e3-add2-41de-8753-ef708abe7937" />

<img width="2858" height="1542" alt="New Dark mode Card" src="https://github.com/user-attachments/assets/a2a65c81-fdfc-4cc7-bc36-24407bec8b32" />


### 🤖 AI Analyst Report
[AI Analyst Report showing prediction and analysis in Dark and Light mode]  
<img width="2852" height="1534" alt="New Result light mode" src="https://github.com/user-attachments/assets/a2290c2c-2094-406c-a655-ac02ecfa1528" />

<img width="2852" height="1546" alt="New Result Dark Mode" src="https://github.com/user-attachments/assets/cb65becc-e3bc-496d-9776-150ada1b3262" />


### 📄 PDF Report
[User can download their report]  
<img width="1026" height="1450" alt="Report pdf" src="https://github.com/user-attachments/assets/779c3d60-6cab-4791-873a-db37bde30fe9" />


### 🌐 Website
<img width="2854" height="1536" alt="Website Title Page" src="https://github.com/user-attachments/assets/8439c717-8106-4da5-a1e4-aa6c4320ed2c" />

<img width="2854" height="1542" alt="Developers" src="https://github.com/user-attachments/assets/d65ec382-4c15-4216-a286-cf94db8f3ff9" />


## 🛠 Tech Stack
- **Backend**: Python, Flask, Pandas, Scikit-learn, XGBoost, NLTK  
- **Frontend**: React, CSS, Framer Motion  
- **APIs**: Google Gemini API, ScrapingDog API  
- **Tools**: Git, GitHub, VS Code  


## ⚡ How to Run Locally

### 🔹 Backend Setup
```bash
# Navigate to the root folder
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
