#!/bin/bash

for i in $(find ./target -type d); do echo $i; zip -9 $i.cbz $i/*; done
