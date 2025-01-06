#define _GNU_SOURCE
#include <libgen.h>
#include <memory.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <stdarg.h>
#include <stdio.h>
#include <dlfcn.h>
#include <errno.h>
#include <fcntl.h>
#include <pwd.h>

#define USER_GROUP_DATA_PATH "/test/user_group_data.csv" // user와 group(role)간 관계를 정의한 csv파일의 경로
#define ALLOWED_BASE_PATH    "/home/test"                // test를 진행할 디렉터리 경로

typedef int (* openSignature)(const char *, int, ...);

// euid를 이용하여 effective username을 찾는 함수.
// return : username 또는 NULL.
const char * get_username(void) {
    const struct passwd * pwd = getpwuid(geteuid());

    return pwd ? pwd->pw_name : NULL;
}

// 절대 경로를 받아 파일이 테스트에 사용할 디렉터리 또는 이의 하위 디렉터리 내부에 존재하는지 여부를 반환하는 함수.
// return : 1(내부에 존재) or 0(내부에 존재 X)
int is_within_allowed_path(const char * path) {
    return !strncmp(path, ALLOWED_BASE_PATH, strlen(ALLOWED_BASE_PATH));
}

// username을 받아 user가 속한 그룹을 찾는 함수.
// open을 호출하면 LD_PRELOAD로 인해 hooking을 위한 open이 호출될 수 있음. 재귀로 인해 callstack overflow가 발생하여, original_open으로 open 함수의 주소를 따로 받아야 함.
// return : -1(실패) or 0(성공) / groups 매개변수는 user가 속한 그룹을 문자열로 받을 out 포인터.
int get_user_groups(const char * username, char * groups, size_t size, openSignature original_open) {
    ssize_t bytes_read;
    char    buffer[256];
    int     fd;

    if ((fd = original_open(USER_GROUP_DATA_PATH, O_RDONLY)) < 0) {
        return -1;
    }

    int remaining = 0; 

    memset(buffer, 0, sizeof buffer);

    while ((bytes_read = read(fd, buffer + remaining, sizeof buffer - remaining - 1)) > 0) {
        char
            * line     = NULL,
            * pre_line = NULL;

        buffer[bytes_read] = '\0';

        for (char * buffer_ptr = buffer; (line = strsep(&buffer_ptr, "\n"));) {
            char 
                user[128]       = { 0 },
                group_list[256] = { 0 };

            pre_line = line;

            if (NULL
                || sscanf(line, "%127[^,],\"%255[^\"]\"", user, group_list) == 2
                || sscanf(line, "%127[^,],%255[^,]", user, group_list) == 2
            ) {

                if (strcmp(user, username)) {
                    continue;
                }

                strncpy(groups, group_list, size);
                close(fd);
                return 0;
            }
        }

        if (!pre_line) {
            remaining = 0;
            continue;
        }

        remaining = strlen(pre_line);
        strcpy(buffer, pre_line);
    }

    close(fd);
    return -1;
}

// 디렉터리마다 들어있는 metadata 파일의 경로와 속한 그룹, open으로 열었을 때의 flags를 받아 user가 속한 그룹의 권한 이상으로 flags에 설정되어 있지 않은지 검사. 
// return : -1 (함수 수행 실패), 0(권한 X), 1(권한 O)
int check_permissions(const char * metadata_path, const char * groups, int flags, openSignature original_open) {
    ssize_t bytes_read;
    char    buffer[512];
    int     fd;

    const int access_mode = flags & O_ACCMODE;

    if ((fd = original_open(metadata_path, O_RDONLY)) < 0) {
        return -1;
    }

    int
        allowed   = 0, 
        remaining = 0;

    memset(buffer, 0, sizeof buffer);

    while ((bytes_read = read(fd, buffer + remaining, sizeof buffer - remaining - 1)) > 0) {
        char
            * line     = NULL,
            * token    = NULL,
            * pre_line = NULL;

        buffer[remaining + bytes_read] = '\0';

        for (char * buffer_ptr = buffer; (line = strsep(&buffer_ptr, "\n"));) {
            char
                permission[8] = { 0 },
                group[128]    = { 0 };

            pre_line = line;

            for (char * line_ptr = line; (token = strsep(&line_ptr, ","));) {
                if (sscanf(token, "%3[rwx-]%127s", permission, group) == 2 && strstr(groups, group)) {
                    const int
                        can_read  = !!strchr(permission, 'r'),
                        can_write = !!strchr(permission, 'w');

                    if (NULL
                        || (access_mode == O_RDONLY && can_read)
                        || (access_mode == O_WRONLY && can_write)
                        || (access_mode == O_RDWR   && can_read && can_write)
                    ) {
                        allowed = 1;
                        goto RET;
                    }
                }
            }
        }

        if (!pre_line) {
            remaining = 0;
            continue;
        }

        remaining = strlen(pre_line);
        strcpy(buffer, pre_line);
    }

RET:
    close(fd);
    return allowed;
}

// hooking을 위한 open 함수.
// return : 권한이 있거나 여러 이유로 확인에 실패하면 기존 open 함수 호출 후 결과 반환, 권한 없으면 -1 반환.
int open(const char *pathname, int flags, ...) {
    openSignature original_open = NULL;

    const char * username = get_username();

    char resolved_path[BUFSIZ];
    char metadata_path[BUFSIZ];
    char groups[256];

    memset(resolved_path, 0, sizeof resolved_path);
    memset(metadata_path, 0, sizeof metadata_path);
    memset(groups, 0, sizeof groups);

    if (!(original_open = dlsym(RTLD_NEXT, "open"))) {
        goto FAILED;
    }

    if (!username) {
        goto ORIGINAL_OPEN_CALL;
    }

    if (!realpath(pathname, resolved_path)) {
        goto ORIGINAL_OPEN_CALL;
    }

    if (!is_within_allowed_path(resolved_path)) {
        goto ORIGINAL_OPEN_CALL;
    }

    if (get_user_groups(username, groups, sizeof(groups), original_open) < 0) {
        goto ORIGINAL_OPEN_CALL;
    }

    snprintf(metadata_path, sizeof metadata_path, "%s/.group_permissions.metadata", dirname(resolved_path));

    switch (check_permissions(metadata_path, groups, flags, original_open)) {
    case -1:
        goto ORIGINAL_OPEN_CALL;
    case 0:
        goto FAILED;
    case 1:
        goto ALLOW_ACCESS;
    }

ORIGINAL_OPEN_CALL:
ALLOW_ACCESS:
    if (!(flags & O_CREAT)) {
        return original_open(pathname, flags);
    }

    va_list args;

    va_start(args, flags);
    mode_t mode = va_arg(args, mode_t);
    va_end(args);

    return original_open(pathname, flags, mode);

FAILED:
    errno = EACCES;
    return -1;
}

