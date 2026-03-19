FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies (legacy-peer-deps recommended for Next/Rasa combinations if needed, but standard install is fine)
RUN npm install

# Copy all frontend code (including public/ images/brosur)
COPY . .

# Build the Next.js production app
RUN npm run build

EXPOSE 3000

# Start command
CMD ["npm", "start"]
