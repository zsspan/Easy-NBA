import random
from time import sleep
import requests

# manual for now
names = ["hakeem olajuwon", "andre iguodala",
    "hasheem thabeet", "luc longley", "ja morant", "zion williamson", "chris paul",
    "kevin mchale", "scottie pippen", "trae young", "julius erving", "jalen brunson",
    "karl-anthony towns", "goran dragić", "devin booker", "chris bosh", "muggsy bogues",
    "antawn jamison", "guerschon yabusele", "al horford", "nik stauskas", "norman powell",
    "erick dampier", "t.j. warren", "herbert jones", "mark williams", "marvin williams",
    "james wiseman", "anthony bennett", "jj redick", "kyle korver", "pete maravich",
    "carmelo anthony", "nate thurmond", "jarrett allen", "andrew bynum", "jason terry",
    "elgin baylor", "t.j. leaf", "darius garland", "marvin bagley", "bob mcadoo",
    "gilbert arenas", "yao ming", "paul george", "donovan mitchell", "kyle lowry",
    "amar'e stoudemire", "anthony davis", "cj mccollum", "zach randolph", "jalen rose",
    "jabari parker", "hal greer", "malik monk", "bruce brown", "bruce bowen",
    "jamychal green", "norm nixon", "george hill", "larry bird", "larry nance", "wilt chamberlain"
]

url = "http://127.0.0.1:5000/"

# send POST requests
for name in names:
    delay_time = random.uniform(7, 13)
    sleep(delay_time)

    response = requests.post(url, data={"player": name})
    
    if response.status_code == 200:
        print(f"Successfully sent: {name}")
    else:
        print(f"Failed to send: {name}, Status Code: {response.status_code}")