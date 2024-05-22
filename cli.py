import typer
from scripts.build import build_run
import os

app = typer.Typer()

@app.command("build",
             help="Builds container images defined in containers/")
def build():
    build_run()

@app.command("up",
             help="Deploys the images in a local environment")
def run():
    workdir = os.getcwd() 
    os.chdir('dev-env')
    os.system('tofu apply -auto-approve')
    os.chdir(workdir)

@app.command("down",
             help="Tears down the deployed local environment")
def destroy():
    workdir = os.getcwd()
    os.chdir('dev-env')
    os.system('tofu destroy -auto-approve')
    os.chdir(workdir)

@app.command("run",
             help="Builds the images and deploys them locally")
def build_and_run():
    build()
    run()





if __name__ == "__main__":
    app()
