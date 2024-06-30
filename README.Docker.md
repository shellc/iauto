### Building and running iauto

When you're ready, start iauto by running:
`docker compose up --build`.

iauto server will be available at http://localhost:2000.

### Deploying iauto server to the cloud

First, build your image, e.g.: `docker build -t iauto .`.
If your cloud uses a different CPU architecture than your development
machine (e.g., you are on a Mac M1 and your cloud provider is amd64),
you'll want to build the image for that platform, e.g.:
`docker build --platform=linux/amd64 -t iauto .`.

Then, push it to your registry, e.g. `docker push myregistry.com/iauto`.

Consult Docker's [getting started](https://docs.docker.com/go/get-started-sharing/)
docs for more detail on building and pushing.

### References
* [Docker's Python guide](https://docs.docker.com/language/python/)