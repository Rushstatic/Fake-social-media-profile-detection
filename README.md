# Fake Buster - AI-Powered Social Media Account Detector

A full-stack application that analyzes public Instagram and X profiles to detect fake accounts and bots in real-time using a custom-trained machine learning model and generative AI.


### Key Features
- **Live Data Analysis**: Scrapes live profile data using a Python backend and the ScrapingDog API.
- **Advanced ML Model**: Utilizes an XGBoost classifier with Natural Language Processing (NLP) to analyze profile statistics and bio text for nuanced detection.
- **Generative AI Reports**: Integrates Google's Gemini API to provide human-like explanations and points of caution for each prediction.
- **Dynamic Frontend**: A responsive, animated, and dark-mode-enabled frontend built with React.
- **Downloadable Reports**: Users can download a full analysis of any profile as a formatted PDF document.


### Application in Action

#### Main Interface
[Main Interface]
<img width="2736" height="1468" alt="Twitter with dark mode" src="https://github.com/user-attachments/assets/351fa158-db11-4b0a-ae1d-ce7be43d4520" />

<img width="2782" height="1484" alt="Instagram frontend" src="https://github.com/user-attachments/assets/0935b45a-ea17-4cc0-9b84-8514930dbafa" />

#### AI Analyst Report
[AI Analyst Report showing prediction and analysis in Dark and Light mode ]
<img width="2808" height="1496" alt="Final Result with report Dark mode" src="https://github.com/user-attachments/assets/fe94b005-2cdd-45a4-9d02-e1f8abac345d" />
<img width="2794" height="1502" alt="Final result with light mode" src="https://github.com/user-attachments/assets/2f6abedb-d86c-4a81-b8f1-15d33b684b33" />

![alt text](image.png)


### PDF Reprt
[User can download their report ]
<img width="1026" height="1450" alt="Report pdf" src="https://github.com/user-attachments/assets/779c3d60-6cab-4791-873a-db37bde30fe9" />


### Tech Stack
- **Backend**: Python, Flask, Pandas, Scikit-learn, XGBoost, NLTK
- **Frontend**: React, CSS, Framer Motion
- **APIs**: Google Gemini API, ScrapingDog API
- **Tools**: Git, GitHub, VS Code

---

### How to Run Locally

1.  **Backend Setup**
    ```bash
    # Navigate to the root folder
    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    python app.py
    ```
2.  **Frontend Setup**
    ```bash
    # Open a new terminal and navigate to the frontend folder
    cd frontend
    npm install
    npm start
    ```
