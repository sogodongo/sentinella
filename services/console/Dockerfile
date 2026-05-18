FROM node:20-alpine AS builder

WORKDIR /build
COPY package*.json ./
RUN npm ci --quiet

COPY . .
RUN npm run build

FROM node:20-alpine

WORKDIR /app
RUN addgroup --system sentinella && adduser --system --ingroup sentinella sentinella

COPY --from=builder /build/.next/standalone ./
COPY --from=builder /build/.next/static ./.next/static
COPY --from=builder /build/public ./public

USER sentinella
EXPOSE 3000

ENV NODE_ENV=production
ENV PORT=3000

CMD ["node", "server.js"]
