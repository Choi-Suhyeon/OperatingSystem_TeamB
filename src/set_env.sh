#!/usr/bin/env bash

set -e

for i in {1..7}; do
    user_name="user$i"

    sudo useradd -d "/home/$user_name" -s /bin/bash "$user_name" && echo "$user_name:$user_name" | sudo chpasswd 
done

sudo mkdir '/home/test'
sudo chmod 777 '/home/test'

mkdir -p '/home/test/src/bin'
mkdir -p '/home/test/management/gantt'
mkdir -p '/home/test/management/team_members'
mkdir -p '/home/test/project_planning'

echo '#include <stdio.h> int main(void) { puts("hello, world!"); }' > '/home/test/src/test.c'
echo -e '# README\nRead ME!!' > '/home/test/src/README.md'
echo 'This is a gantt chart' > '/home/test/management/gantt/gantt_chart'
echo -e 'programmer : A, B, C\nleader: D' > '/home/test/management/team_members/list'
echo 'Planning is boring...' > '/home/test/project_planning/planning'

chmod 666 '/home/test/src/test.c'
chmod 666 '/home/test/src/README.md'
chmod 666 '/home/test/management/gantt/gantt_chart'
chmod 666 '/home/test/management/team_members/list'
chmod 666 '/home/test/project_planning/planning'
