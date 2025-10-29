FROM node:24-alpine AS builder
WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

RUN npm prune --production

FROM node:24-alpine
WORKDIR /app

ENV NODE_ENV=production

COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app ./

EXPOSE 80
CMD ["pm2-runtime", "start", "server.js", "-i", "0"]
