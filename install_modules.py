import os


def install_modules():
    modules_to_install = ['pyjwt', 'hyper']

    for module in modules_to_install:
        print(f"Installing {module}")
        os.system(f"pip3 install {module}\n\n")


install_modules()
