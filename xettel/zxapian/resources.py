
attributes_dict = {
        "abstract": "B",
        "date": "D",
        "filename": "F",
        "hash": "H",
        "jdproject": "JD",
        "tag": "K",
        "tags": "K",
        "backlinks": "LI",
        "links": "LO",
        "filepath": "P",
        "uid": "Q",
        "text": "T",
        "title": "S",
        }

tr_attributes_dict = {}
for k in attributes_dict:
    tr_attributes_dict[attributes_dict[k]]=k

def dict_from_termlist(termlist, ignore=['T']):
    retdict = {}
    for item in termlist:
        item=item.term.decode()
        i=0
        prefix = item[:1]
        if [ p for p in tr_attributes_dict.keys() if p.startswith(prefix) ] == [] or prefix in ignore:
            break
        while prefix not in tr_attributes_dict.keys():
            i+=1
            prefix = item[:i]
        
        attr = tr_attributes_dict[prefix]
        if attr not in retdict.keys():
            retdict[tr_attributes_dict[prefix]] = [item[max(i,1):]] 
        else:
            retdict[tr_attributes_dict[prefix]].append(item[max(i,1):]) 
    return retdict

def int36(num):
    digits="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    base36=""
    if num == 0:
        return "0"
    while num != 0:
        base36 = digits[num % 36] + base36
        num = num // 36
    return base36

