import argparse as arg
from scripts.build import build_run
import os

def build(namespace: arg.Namespace):
    build_run()

def run(namespace: arg.Namespace):
    workdir = os.getcwd() 
    os.chdir('dev-env')
    os.system('tofu apply')
    os.chdir(workdir)

def destroy(namespace: arg.Namespace):
    workdir = os.getcwd()
    os.chdir('dev-env')
    os.system('tofu destroy')
    os.chdir(workdir)

def build_and_run(namespace: arg.Namespace):
    build(namespace)
    run(namespace)

def default_action(namespace: arg.Namespace):
    print("Invalid action")

parser = arg.ArgumentParser()

parser.add_argument('action')

actions = {
        'build': build,
        'run': run,
        'destroy': destroy,
        'build-run': build_and_run        
        }

if __name__ == "__main__":
    args = parser.parse_args()
    action = actions.get(args.action, default_action)
    action(args)

