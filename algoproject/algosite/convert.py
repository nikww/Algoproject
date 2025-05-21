with open('data.json', 'r', encoding='latin1') as f:
    content = f.read()

with open('data_utf8.json', 'w', encoding='utf-8') as f:
    f.write(content)
