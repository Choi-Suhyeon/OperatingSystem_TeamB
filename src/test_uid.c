#include <stdio.h>
#include <unistd.h>

int main() {
    // Get the real and effective user IDs
    uid_t uid = getuid();
    uid_t euid = geteuid();

    // Print the IDs
    printf("Real UID (uid): %d\n", uid);
    printf("Effective UID (euid): %d\n", euid);

    return 0;
}

