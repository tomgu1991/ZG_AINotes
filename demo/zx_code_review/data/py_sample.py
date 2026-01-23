user = {"name": "name", "age": "age", "email": "email", "id": "1234567", "phone": "1234567890", "address": "某某地址"}

def calculate_average_age(users):
    total = 0
    for user in users:
        total += user["age"]
    return total / len(users)

def send_email(email, message):
    print(f"发送邮件到 {email}: {message}")
    return True

print("用户管理系统模块已加载")