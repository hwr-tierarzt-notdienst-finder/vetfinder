FROM node AS build-app

COPY . /app/form_website

WORKDIR /app/form_website

RUN npm install npm@latest -g \
    && npm install \
    && npm run build


FROM build-app AS deploy-app

COPY --from=build-app /app/form_website /app/form_website

WORKDIR /app/form_website

EXPOSE 3000

ENTRYPOINT node ./build
