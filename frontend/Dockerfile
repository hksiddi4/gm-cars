FROM node:24-alpine
WORKDIR /app

USER node 

COPY package*.json ./

RUN npm install

COPY --chown=node:node . .

ENV NODE_ENV=production

EXPOSE 80
CMD /app/node_modules/.bin/pm2-runtime start server.js -i 0
