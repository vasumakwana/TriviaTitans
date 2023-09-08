FROM node:14-alpine as react-build
WORKDIR /app
COPY . ./
RUN npm install --legacy-peer-deps
# RUN npm run build
# FROM nginx:alpine
# COPY nginx.conf /etc/nginx/conf.d/configfile.template
# COPY --from=react-build /app/dist /usr/share/nginx/html
# ENV PORT 8080
# ENV HOST 0.0.0.0
# EXPOSE 8080
# CMD sh -c "envsubst '\$PORT \$HOST' < /etc/nginx/conf.d/configfile.template > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"
CMD sh -c "npm run dev -- --host 0.0.0.0 --port 8080"