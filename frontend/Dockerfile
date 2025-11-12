FROM node:24-alpine
WORKDIR /app

COPY package*.json ./
RUN npm install

RUN chmod +x /app/node_modules/.bin/pm2-runtime

COPY . .

ENV NODE_ENV=production

EXPOSE 80
CMD ["/app/node_modules/.bin/pm2-runtime", "start", "server.js", "-i", "0"]
