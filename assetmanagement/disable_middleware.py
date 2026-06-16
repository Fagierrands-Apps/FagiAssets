with open('assetmanager/settings.py', 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if 'SessionReliabilityMiddleware' in line and 'users.middleware' in line:
        new_lines.append("    # 'users.middleware.SessionReliabilityMiddleware',  # Disabled - causes session issues\n")
    else:
        new_lines.append(line)

with open('assetmanager/settings.py', 'w') as f:
    f.writelines(new_lines)

print("✓ SessionReliabilityMiddleware disabled")
