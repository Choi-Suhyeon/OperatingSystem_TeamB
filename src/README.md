# Group-Based File Access Control System

시스템에 속한 유저와 유저가 속한 그룹(룰) 간의 관계 및 그룹과 자원(파일) 간 관계를 정의하고 이를 바탕으로 access control을 수행하는 시스템을 구현하였다.
유저와 그룹 간 관계는 `/test/user_group_data.csv`에 존재한다.
그룹과 자원 간 관계는 자원이 속한 디렉터리의 `.group_permissions.metadata` (csv 형식)에 존재한다.

## set\_env.sh
`set_env.sh`을 실행시키면, 사용자 user1부터 user7, 테스트에 사용할 데이터를 담고 있는 `/home/test` 디렉터리, 테스트에 필요한 여러 파일을 담고 있는 `/test` 디렉터리가 생성된다.

## grouping.py

아래는 --help 옵션을 주고 grouping.py를 실행시켰을 때의 모습이다.

```
usage: grouping.py [-h] {list,add,rem} {usr,grp} [args ...]

Process user and group commands.

positional arguments:
  {list,add,rem}  The command to execute.
  {usr,grp}       The target type (user or group).
  args            Additional arguments based on the command and target.

options:
  -h, --help      show this help message and exit
```

group을 생성 및 삭제하고 사용자와 그룹 간 관계를 설정하는 스크립트이다. 
만약 명령이 list일 경우 추가적인 args가 있으면 안 되며, 명령이 add 또는 rem이면 추가적인 args가 반드시 필요하다.
아래는 사용 예시이다.

```bash
./grouping.py list usr # username을 기준으로 관계 출력.
./grouping.py add usr user1 GroupA GroupB # user1을 GroupA와 GroupB에 추가.
./grouping.py add grp GroupC user1 user3 user4 # GroupC를 추가. GroupC에 속한 사용자는 user1, user3, user4.
```
## auth.py

실행시키면 먼저 `.group_permissions.metadata` 파일을 어디에 저장할지 경로를 받는다. 파일에 대한 권한을 설정할 생각이라면 이 경로는 반드시 해당 파일과 같은 경로여야 한다.
3개의 기능적 메뉴가 주어진다.

1. Assign Permissions to a Group
1. Check Permissions for a File
1. List All Permissions

- 첫 번째 메뉴는 파일과 그룹, 권한을 받아 `.group_permissions.metadata`를 수정하는 기능을 한다.
- 두 번째 메뉴는 파일 하나를 입력받아 해당 파일과 그룹별 권한과의 관계를 출력한다.
- 마지막 메뉴는 처음 설정한 디렉터리 내의 모든 파일들의 그룹별 권한과의 관계를 출력한다.

## 테스트 방법 

원래는 `/etc/environment` 파일에 `LD_PLELOAD`를 추가해야 하지만, 시스템 전반에 영향이 갈 수 있으므로, 아래의 예시처럼 실행시키는 것을 권장한다.
```bash
LD_PRELOAD='/test/hook.so' cat /home/test/src/README.md
```
`su` 명령어를 이용해 유저를 전환해가며 이 시스템을 테스트해볼 수 있다.
