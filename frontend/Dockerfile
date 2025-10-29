FROM node:24-alpine
WORKDIR /app
COPY package*.json ./

COPY . .

ENV NODE_ENV=production

EXPOSE 80
CMD ["pm2-runtime", "start", "server.js", "-i", "0"]
