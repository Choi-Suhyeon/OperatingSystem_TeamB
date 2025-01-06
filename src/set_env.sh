#!/usr/bin/env bash

set -e

# user1부터 user7까지 생성
for i in {1..7}; do
    user_name="user$i"

    sudo useradd -d "/home/$user_name" -s /bin/bash "$user_name" && echo "$user_name:$user_name" | sudo chpasswd 
done

# 테스트에 사용할 파일들을 담을 디렉터리 생성
sudo mkdir '/home/test'
sudo chmod 777 '/home/test'

# 관리를 위한 파일들을 담을 디렉터리 생성
sudo mkdir '/test'
sudo chmod 777 '/test'

make # hook.c로부터 hook.so 생성. Makefile 필요.
cp 'user_group_data.csv' 'grouping.py' 'auth.py' 'hook.so' '/test'

# 아래 한 줄은 시스템 전반에 대해 hook.so를 적용시키는 명령어. 굉장히 위험하니 조심히 사용할 것.
# 이거 만든 사람은 이것 때문에 가상 머신 두 개 날림.
# echo 'LD_PRELOAD=/test/hook.so' | sudo tee /etc/environment > /dev/null

# /home/test의 하위 디렉터리로 디렉터리 생성
mkdir -p '/home/test/src/bin'
mkdir -p '/home/test/management/gantt'
mkdir -p '/home/test/management/team_members'
mkdir -p '/home/test/project_planning'

# 디렉터리 접근 권한 설정
chmod 777 '/home/test/src'
chmod 777 '/home/test/src/bin'
chmod 777 '/home/test/management'
chmod 777 '/home/test/management/gantt'
chmod 777 '/home/test/management/team_members'
chmod 777 '/home/test/project_planning'

# 테스트 파일 생성
echo '#include <stdio.h> int main(void) { puts("hello, world!"); }' > '/home/test/src/test.c'
echo -e '# README\nRead ME!!' > '/home/test/src/README.md'
echo 'This is a gantt chart' > '/home/test/management/gantt/gantt_chart'
echo -e 'programmer : A, B, C\nleader: D' > '/home/test/management/team_members/list'
echo 'Planning is boring...' > '/home/test/project_planning/planning'

# 테스트 파일 접근 권한 설정 (RBAC을 테스트하는 것이 목적이므로 리눅스의 권한 때문에 파일 읽기 쓰기가 막히면 안 됨)
chmod 666 '/home/test/src/test.c'
chmod 666 '/home/test/src/README.md'
chmod 666 '/home/test/management/gantt/gantt_chart'
chmod 666 '/home/test/management/team_members/list'
chmod 666 '/home/test/project_planning/planning'
