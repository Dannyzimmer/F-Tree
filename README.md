# Fcodes GUI

A GUI for using the [Fcode](https://github.com/Dannyzimmer/fcodes/) library.

# Development environment

## Creating a conda environment

```sh
conda create -n fcodes_gui python=3.10
conda activate fcodes_gui
conda install pango
python3 -m pip install -r requirements.txt
```

## Creating a virtual environment

```sh
apt install -y pango1.0-tools tk
python3 -m .venv venv
./venv/bin/activate
python3 -m pip install -r requirements.txt
```

# Docker image

## Building

```sh
docker build ./ -t fcodes_gui
```

## Running

Replace `$(pwd)` by the path to the host directory you want to have available inside the Docker image:

```sh
xhost + && docker run --rm -ti -e USERID=$UID -e USER=$USER -e DISPLAY=$DISPLAY -v /var/db:/var/db:Z -v /tmp/.X11-unix:/tmp/.X11-unix -v $HOME/.Xauthority:/home/developer/.Xauthority -v "$(pwd):/data" -w /data fcodes_gui
```
