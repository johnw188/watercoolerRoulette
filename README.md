# Watercooler Roulette

This is a project to match users for one minute video chats

## Get started

Install the dependencies...

```bash
cd frontend
npm install
```

...then start [Rollup](https://rollupjs.org):

```bash
npm run dev
```

Navigate to [localhost:5000](http://localhost:5000). You should see your app running. Edit a component file in `src`, save it, and reload the page to see your changes.

By default, the server will only respond to requests from localhost. To allow connections from other computers, edit the `sirv` commands in package.json to include the option `--host 0.0.0.0`.


## Building and running in production mode

To create an optimised version of the app:

```bash
npm run build
```

You can run the newly built app with `npm run start`. This uses [sirv](https://github.com/lukeed/sirv), which is included in your package.json's `dependencies` so that the app will work when you deploy to platforms like [Heroku](https://heroku.com).


## Single-page app mode

By default, sirv will only respond to requests that match files in `public`. This is to maximise compatibility with static fileservers, allowing you to deploy your app anywhere.

If you're building a single-page app (SPA) with multiple routes, sirv needs to be able to respond to requests for *any* path. You can make it so by editing the `"start"` command in package.json:

```js
"start": "sirv public --single"
```


## Deploying to the web

### With [now](https://zeit.co/now)

Install `now` if you haven't already:

```bash
npm install -g now
```

Then, from within your project folder:

```bash
cd public
now deploy --name my-project
```

As an alternative, use the [Now desktop client](https://zeit.co/download) and simply drag the unzipped project folder to the taskbar icon.

### With [surge](https://surge.sh/)

Install `surge` if you haven't already:

```bash
npm install -g surge
```

Then, from within your project folder:

```bash
npm run build
surge public my-project.surge.sh
```

## Backend testing

Running the backend tests requires `pytest` and `pytest-env` modules

```bash
cd backend
python3 -m pytest
```

## Sequence Diagram
![Diagram](https://sequencediagram.org/index.html#initialData=C4S2BsFMAIFkENgGMAWIB2BzaAxcB7AdwCgAHeAJ1CRHPWGgEFwQlIzLrb57oAhfACMOVVt14B1RJApJ8+KBRFc6DAMoAVAKoA5YsXiD8AD2j4AbjKYs2ALmgBhCpGnRSSaAF5oAKh8AFSBkHfHR0SCRQUIAKAEo-YmZWSABaAD5NXXs-dwA6JGdpAHkAMxKZOITMnXSkuwBveBtIAH18MpkAX31DEzNLCn4heycXYBh3L18AoIoQsIio9EqffQFBdOrsnzyCschS8ooV4mr09dt6o0E2jopuxOb0qXHZeUVbP38izT9oAHoALaIVDQertI72RrNW5HTrddbPaRvBQybbfX4+AHA5AoMEQtFg66wrrdXqmCxWF4yOSoij2OqQADkAGdoDwACZDQTs5zQHGoSAcgA66EZrLMd2gIDZLMgUEiQuI1JRilqzW2ACUAKJqfx-cF3QnACgAV0gABpJZCwU1kiT7t0VbS1WkLtMdXqDQTnPToCUmnKrT6oXa2A74QYjBSBtyGYJOaE2VchBHRcSeCzCFZvDkkPlCuNGOgsxV4qtiIi0s73oSvj8NH9-pns4MUzcW11Hskka8XXWfABxbWNrHNkut-Q1unq5Ja3X6rHtlqd+5RvqUwaM7akFm5OXATWQQH4cYAEUgLIKtCW0WXq86sQA3D1o-0rIyLe6JJBBJqNA40BqJeLIgKEQHAJwSqMucwxwEKIDwBBhSApWQiznY8EcohyEuICQA)