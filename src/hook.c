#define _GNU_SOURCE
#include <memory.h>
#include <string.h>
#include <libgen.h>
#include <stdlib.h>
#include <unistd.h>
#include <stdarg.h>
#include <stdio.h>
#include <errno.h>
#include <dlfcn.h>
#include <fcntl.h>
#include <pwd.h>

#define PATH_MAX             4096
#define USER_GROUP_DATA_PATH "/test/user_group_data.csv"
#define ALLOWED_BASE_PATH    "/home/test"

typedef int (* openSignature)(const char *, int, ...);

const char * get_username(void) {
    const struct passwd * pwd = getpwuid(geteuid());

    return pwd ? pwd->pw_name : NULL;
}

int is_within_allowed_path(const char *path) {
    return !strncmp(path, ALLOWED_BASE_PATH, strlen(ALLOWED_BASE_PATH));
}

// Helper function to get user groups from user_group_data.csv
int get_user_groups(const char *username, char *groups, size_t size, openSignature original_open) {
    ssize_t bytes_read;
    char    buffer[256];
    int     fd;

    if ((fd = original_open(USER_GROUP_DATA_PATH, O_RDONLY)) < 0) {
        return -1;
    }

    int remaining = 0; 

    while ((bytes_read = read(fd, buffer + remaining, sizeof buffer - remaining - 1)) > 0) {
        char
            * line,
            * pre_line;

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

        remaining = strlen(pre_line);
        strcpy(buffer, pre_line);
    }

    close(fd);
    return -1;
}

int check_permissions(const char *metadata_path, const char *groups, int flags, openSignature original_open) {
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

    while ((bytes_read = read(fd, buffer + remaining, sizeof buffer - remaining - 1)) > 0) {
        char
            * line,
            * token,
            * pre_line;

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

        remaining = strlen(pre_line);
        strcpy(buffer, pre_line);
    }

RET:
    close(fd);
    return allowed;
}

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

    // for debug start
    const char * name = get_username();
    if (!name || !strcmp(name, "suhyeon")) {
        goto ORIGINAL_OPEN_CALL;
    }
    // for debug end

    if (!realpath(pathname, resolved_path)) {
        goto ORIGINAL_OPEN_CALL;
    }

    if (!is_within_allowed_path(resolved_path)) {
        goto ORIGINAL_OPEN_CALL;
    }

    if (!username) {
        goto ORIGINAL_OPEN_CALL;
    }

    if (get_user_groups(username, groups, sizeof(groups), original_open) < 0) {
        goto ORIGINAL_OPEN_CALL;
    }

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

