#!/bin/bash

if [ -f "../dist/tuner" ]; then
	cp ../dist/tuner ~/.local/bin/
fi

xdg-icon-resource install --size 64 --context apps --mode user k6gte-tuner.png k6gte-tuner

xdg-desktop-icon install k6gte-tuner.desktop

xdg-desktop-menu install k6gte-tuner.desktop

