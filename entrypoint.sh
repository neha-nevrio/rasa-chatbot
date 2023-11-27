#!/bin/bash

rasa train
rasa run --enable-api --cors "*" --debug
