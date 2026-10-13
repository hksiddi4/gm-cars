import sys

with open('backend/start.py', 'r', encoding='utf-8') as f:
    c = f.read()

old_code = '"PEH": ["v.modelYear = \'2020\'", "v.model = \'CAMARO\'", "v.body = \'COUPE\'", "v.trim IN (\'2SS\', \'ZL1\')", "t.transmission_type = \'A10\'", "c.color_name = \'BLACK\'"],'
new_code = old_code + '\n            "INDY26": ["EXISTS (SELECT 1 FROM SpecialEditions se WHERE se.vehicle_id = v.vehicle_id AND se.special_desc = \'2026 Indianapolis 500 Festival Vehicle\')"],'

if old_code in c:
    c = c.replace(old_code, new_code)
    with open('backend/start.py', 'w', encoding='utf-8') as f:
        f.write(c)
    print("Success")
else:
    print("Not found")
