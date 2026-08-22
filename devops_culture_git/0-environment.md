=== Vérification de l'environnement ===
[ OK ] Docker installé et démon actif (Docker version 29.7.2)
[ OK ] Git installé (git version 2.50.1 (Apple Git-155))
[ OK ] git user.name configuré
[ OK ] git user.email configuré
[ OK ] Clé SSH GitHub fonctionnelle
[ OK ] Node.js présent (v20.19.6)
=======================================
Tout est pret. Bon cours !
yugz@MacBook-Yugz afcf590c603f62c269594bc80c4a039792cb9380 % docker run hello-world
Unable to find image 'hello-world:latest' locally
latest: Pulling from library/hello-world
58dee6a49ef1: Pull complete
c3bdf82c34d1: Download complete
Digest: sha256:5dd0d3e6e255913fc30f90b9f2b1d359cc2cbdb48090cc4b65f1676e203243cc
Status: Downloaded newer image for hello-world:latest

Hello from Docker!
This message shows that your installation appears to be working correctly.

To generate this message, Docker took the following steps:

1.  The Docker client contacted the Docker daemon.
2.  The Docker daemon pulled the "hello-world" image from the Docker Hub.
    (arm64v8)
3.  The Docker daemon created a new container from that image which runs the
    executable that produces the output you are currently reading.
4.  The Docker daemon streamed that output to the Docker client, which sent it
    to your terminal.

To try something more ambitious, you can run an Ubuntu container with:
$ docker run -it ubuntu bash

Share images, automate workflows, and more with a free Docker ID:
https://hub.docker.com/

For more examples and ideas, visit:
https://docs.docker.com/get-started/
