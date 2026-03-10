TO RUN:

frontend: 

cd frontend
npm install
npm run dev or npm run build


backend

cd backend
pip install uvicorn
uvicorn main:app --reload


once both frontend and backend are started, localhost should display the working chatbot!

notes:

this runs a local llm, please make sure you have the same llm installed and running
feel free to switch out model

this also uses 2 public api's
to get FREE public keys visit the following

waqi: https://aqicn.org/data-platform/token/
climateiq: https://www.climatiq.io/docs


enjoy!
