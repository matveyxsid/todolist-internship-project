FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json .
RUN npm install
COPY . .
RUN npm run build

ARG REACT_APP_VERSION
ENV REACT_APP_VERSION=$REACT_APP_VERSION

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]