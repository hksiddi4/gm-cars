FROM node:24-alpine
WORKDIR /app

ENV NODE_ENV=production

COPY package*.json ./

RUN npm install --omit=dev

COPY . .

EXPOSE 80
CMD ["/app/node_modules/.bin/pm2-runtime", "start", "server.js", "-i", "0"]
