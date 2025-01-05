import csv
import os

# 파일 경로
GROUP_DATA_FILE = "user_group_data.csv"
METADATA_FILE = ".group_permissions.metadata"

# 초기 설정: 메타데이터 파일 생성
def initialize_metadata():
    global METADATA_FILE
    directory = input("Enter the directory to store metadata file: ").strip()
    # 절대 경로 구하기
    absolute_directory = os.path.abspath(directory)

    # 파일명 제거 및 디렉토리 추출
    if os.path.isfile(absolute_directory):
        absolute_directory = os.path.dirname(absolute_directory)

    # 디렉토리 생성
    if not os.path.exists(absolute_directory):
        os.makedirs(absolute_directory)

    # 메타데이터 파일 경로 설정
    METADATA_FILE = os.path.join(absolute_directory, ".group_permissions.metadata")

    # 메타데이터 파일 생성
    if not os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "w") as file:
            file.write("")

# CSV 데이터 읽기
def read_csv_data(file_path):
    data = {}
    try:
        with open(file_path, "r") as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header
            for row in reader:
                user = row[0]
                groups = row[1].split(",") if len(row) > 1 and row[1] else []
                data[user] = groups
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    return data

# 메타데이터 읽기
def read_metadata(file_path):
    permissions = {}
    try:
        with open(file_path, "r") as file:
            for line in file:
                parts = line.strip().split(",")
                if len(parts) >= 2:
                    file_name = parts[0]
                    perms = parts[1:]
                    permissions[file_name] = perms
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    return permissions

# 메타데이터 쓰기
def write_metadata(file_path, data):
    with open(file_path, "w") as file:
        for file_name, perms in data.items():
            file.write(f"{file_name},{','.join(perms)}\n")

# 권한 형식 검증 함수
def validate_permissions(perm):
    if len(perm) > 3 or any(c not in "rwx" for c in perm):
        print("Invalid permissions. Must be up to 3 characters containing only 'r', 'w', or 'x'.")
        return None
    return ''.join(c if c in perm else '-' for c in "rwx")

# 그룹에 권한 부여
def assign_permissions():
    group_data = read_csv_data(GROUP_DATA_FILE)
    permissions = read_metadata(METADATA_FILE)

    file_name = os.path.basename(input("Enter the file name to assign permissions: "))
    group_name = input("Enter the group name to assign permissions: ")
    if group_name not in {group for groups in group_data.values() for group in groups}:
        print(f"Group '{group_name}' does not exist in '{GROUP_DATA_FILE}'.")
        return

    print("Assign permissions (read: r, write: w, execute: x). Enter permissions for each group:")
    while True:
        perm_input = input(f"Permissions for group '{group_name}': ").strip()
        validated_perm = validate_permissions(perm_input)
        if validated_perm is not None:
            break

    if file_name not in permissions:
        permissions[file_name] = []

    # Remove existing permissions for the same group
    permissions[file_name] = [p for p in permissions[file_name] if not p.endswith(group_name)]
    permissions[file_name].append(f"{validated_perm}{group_name}")

    write_metadata(METADATA_FILE, permissions)
    print(f"Permissions for file '{file_name}' and group '{group_name}' saved to '{METADATA_FILE}'.")

# 그룹 권한 확인
def check_permissions():
    permissions = read_metadata(METADATA_FILE)
    file_name = input("Enter the file name to check permissions: ")

    if file_name in permissions:
        print(f"Permissions for file '{file_name}':")
        for perm in permissions[file_name]:
            print(f"  {perm}")
    else:
        print(f"No permissions found for file '{file_name}'.")

# 모든 그룹 권한 출력
def list_all_permissions():
    permissions = read_metadata(METADATA_FILE)
    if not permissions:
        print("No permissions assigned yet.")
        return

    print("Permissions for all files:")
    for file_name, perms in permissions.items():
        print(f"- {file_name}: {', '.join(perms)}")

# 메인 메뉴
def main():
    initialize_metadata()
    while True:
        print("\nGroup Permission Manager")
        print("1. Assign Permissions to a Group")
        print("2. Check Permissions for a File")
        print("3. List All Permissions")
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
