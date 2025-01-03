import re
import json
import os

# 데이터 파일 경로
DATA_FILE = "user_group_data.json"
PASSWD_FILE = "/etc/passwd"

# 초기 데이터 생성
def initialize_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as file:
            json.dump({}, file)

# 데이터 읽기
def read_data():
    with open(DATA_FILE, "r") as file:
        return json.load(file)

# 데이터 쓰기
def write_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# /etc/passwd 파일에서 유저 정보 읽고 필터링
def read_and_filter_users(prefix="user"):
    """Read /etc/passwd and filter users with the specified prefix."""
    users = []
    try:
        with open(PASSWD_FILE, "r") as file:
            for line in file:
                if not line.strip():
                    continue
                parts = line.strip().split(":")
                if len(parts) < 7:
                    continue

                username, password, uid, gid, comment, home_dir, shell = parts
                if username.startswith(prefix):
                    users.append({
                        "username": username,
                        "password": password,
                        "uid": int(uid),
                        "gid": int(gid),
                        "comment": comment,
                        "home_dir": home_dir,
                        "shell": shell,
                    })
    except FileNotFoundError:
        print(f"Error: {PASSWD_FILE} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return users

# 그룹 생성
def create_group():
    data = read_data()
    group_name = input("Enter group name to create: ")
    if group_name in data:
        print(f"Group '{group_name}' already exists.")
    else:
        data[group_name] = []
        write_data(data)
        print(f"Group '{group_name}' created.")

# 그룹 삭제
def delete_group():
    data = read_data()
    group_name = input("Enter group name to delete: ")
    if group_name in data:
        del data[group_name]
        write_data(data)
        print(f"Group '{group_name}' deleted.")
    else:
        print(f"Group '{group_name}' does not exist.")

# 그룹에 사용자 추가
def add_user_to_group():
    users = read_and_filter_users()
    data = read_data()
    group_name = input("Enter group name: ")
    user_name = input("Enter username to add: ")

    if group_name not in data:
        print(f"Group '{group_name}' does not exist.")
        return

    if user_name not in [user["username"] for user in users]:
        print(f"User '{user_name}' does not exist in the system.")
        return

    if user_name in data[group_name]:
        print(f"User '{user_name}' is already in group '{group_name}'.")
    else:
        data[group_name].append(user_name)
        write_data(data)
        print(f"User '{user_name}' added to group '{group_name}'.")

# 그룹에서 사용자 삭제
def remove_user_from_group():
    data = read_data()
    group_name = input("Enter group name: ")
    user_name = input("Enter username to remove: ")

    if group_name not in data:
        print(f"Group '{group_name}' does not exist.")
        return

    if user_name in data[group_name]:
        data[group_name].remove(user_name)
        write_data(data)
        print(f"User '{user_name}' removed from group '{group_name}'.")
    else:
        print(f"User '{user_name}' is not in group '{group_name}'.")

# 그룹별 사용자 출력
def list_users_in_group():
    data = read_data()
    group_name = input("Enter group name: ")

    if group_name in data:
        users = data[group_name]
        if users:
            print(f"Users in group '{group_name}': {', '.join(users)}")
        else:
            print(f"No users in group '{group_name}'.")
    else:
        print(f"Group '{group_name}' does not exist.")

# 유저 목록 출력
def list_users():
    users = read_and_filter_users()
    if users:
        print("Users from /etc/passwd:")
        for user in users:
            print(f"- {user['username']} (UID: {user['uid']}, GID: {user['gid']})")
    else:
        print("No users matching the filter were found.")

# 메인 메뉴
def main():
    initialize_data()
    while True:
        print("\nUser-Group Manager")
        print("1. List Users")
        print("2. Create Group")
        print("3. Delete Group")
        print("4. Add User to Group")
        print("5. Remove User from Group")
        print("6. List Users in Group")
        print("7. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            list_users()
        elif choice == "2":
            create_group()
        elif choice == "3":
            delete_group()
        elif choice == "4":
            add_user_to_group()
        elif choice == "5":
            remove_user_from_group()
        elif choice == "6":
            list_users_in_group()
        elif choice == "7":
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
