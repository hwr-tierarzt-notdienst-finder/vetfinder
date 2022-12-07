FROM node

COPY . /app/form_website

WORKDIR /app/form_website

EXPOSE 3000

ENTRYPOINT node ./build
