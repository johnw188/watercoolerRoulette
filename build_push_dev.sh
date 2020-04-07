source SECRET.env

cd backend
sls deploy --stage dev

cd ..
cd frontend
yarn build
cd ..
cd backend
sls client deploy
