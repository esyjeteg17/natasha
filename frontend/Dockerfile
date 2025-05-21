FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci          # dev+prod зависимости, без кеша npm

COPY . .
RUN npm run build   # создаёт .output

#############################################
# 2-я стадия: рантайм + PM2                 #
#############################################
FROM node:20-alpine

WORKDIR /app
COPY --from=builder /app/.output ./.output
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json .

RUN npm install -g pm2       # ← именно эта строка ставит pm2

EXPOSE 3000
CMD ["pm2-runtime", "start", "node", "--name", "nuxt", "--", ".output/server/index.mjs", "-i", "max"]