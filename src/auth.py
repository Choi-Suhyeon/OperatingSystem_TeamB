import json
import os

# 파일 경로
GROUP_DATA_FILE = "user_group_data.json"
METADATA_FILE = "group_permissions.metadata"

# 초기 설정: 메타데이터 파일 생성
def initialize_metadata():
    if not os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "w") as file:
            json.dump({}, file)

# 데이터 읽기
def read_data(file_path):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return {}

# 데이터 쓰기
def write_data(file_path, data):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)

# 그룹에 권한 부여
def assign_permissions():
    """
    Assign permissions to a group based on the existing group data.
    """
    group_data = read_data(GROUP_DATA_FILE)
    permissions = read_data(METADATA_FILE)

    group_name = input("Enter the group name to assign permissions: ")
    if group_name not in group_data:
        print(f"Group '{group_name}' does not exist in '{GROUP_DATA_FILE}'.")
        return

    print("Assign permissions (read, write, execute). Enter 'yes' or 'no':")
    read_perm = input("Read: ").strip().lower() == "yes"
    write_perm = input("Write: ").strip().lower() == "yes"
    execute_perm = input("Execute: ").strip().lower() == "yes"

    permissions[group_name] = {
        "read": read_perm,
        "write": write_perm,
        "execute": execute_perm
    }

    write_data(METADATA_FILE, permissions)
    print(f"Permissions for group '{group_name}' saved to '{METADATA_FILE}'.")

# 그룹 권한 확인
def check_permissions():
    """
    Check permissions for a specific group.
    """
    permissions = read_data(METADATA_FILE)
    group_name = input("Enter the group name to check permissions: ")

    if group_name in permissions:
        perms = permissions[group_name]
        print(f"Permissions for group '{group_name}':")
        print(f"  Read: {perms['read']}")
        print(f"  Write: {perms['write']}")
        print(f"  Execute: {perms['execute']}")
    else:
        print(f"No permissions found for group '{group_name}'.")

# 모든 그룹 권한 출력
def list_all_permissions():
    """
    List permissions of all groups.
    """
    permissions = read_data(METADATA_FILE)
    if not permissions:
        print("No permissions assigned yet.")
        return

    print("Permissions for all groups:")
    for group, perms in permissions.items():
        print(f"- {group}: Read = {perms['read']}, Write = {perms['write']}, Execute = {perms['execute']}")

# 메인 메뉴
def main():
    initialize_metadata()
    while True:
        print("\nGroup Permission Manager")
        print("1. Assign Permissions to a Group")
        print("2. Check Permissions for a Group")
        print("3. List All Group Permissions")
        print("4. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            assign_permissions()
        elif choice == "2":
            check_permissions()
        elif choice == "3":
            list_all_permissions()
        elif choice == "4":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
