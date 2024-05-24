import typer
from chefcito_cli.scripts.build import build_run
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

@app.command("install",
             help="Installs dependencies, use --no_dev to avoid installing dev dependencies\
                     if you need to use pip3 instead of pip, use the option --pip_name")
def install_dependencies(no_dev: bool = False, pip_name: str = "pip"):
    if not no_dev:
        os.system(f"{pip_name} install -r dev-requirements.txt")
    os.system(f"{pip_name} install -r requirements.txt")




if __name__ == "__main__":
    app()
