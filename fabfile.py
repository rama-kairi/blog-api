from fabric.api import cd, env, local, prefix, run

env.hosts = ["ubuntu@159.100.241.165"]
env.BASE_DIR = "blog-api"


def deploy():
    with cd(env.BASE_DIR):
        run("git pull")
        run("docker-compose -f docker-compose.yml up -d --build")
        run("docker exec -it webapp alembic upgrade head")
