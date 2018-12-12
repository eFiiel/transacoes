import json
"""
d ={
    'asd':'sss',
    'sddw':'asd',
    'erd':'sd'
}
with open("../teste.txt", 'w+')as f:
    pass

with open("../teste.txt", 'r')as f:
    temp = f.read()
print(temp == "")
temp.append(d)
temp.append(d)
temp.append(d)
temp.append(d)
print(temp)
#with open("../teste.txt", 'w')as f:
#    f.write(json.dumps(temp, indent=4))
"""



class Transaction:
    idCounter = 0

    def __init__(self, timestamp, status, content, uid=None):
        """

        :param uid: id da transação
        :type uid: int
        :param timestamp: momento de criação da transação
        :type timestamp: datetime
        """
        if uid == None:
            Transaction.idCounter += 1
            self.id = Transaction.idCounter
        else:
            self.id = uid
        self.timestamp = timestamp
        self.status = status
        self.content = content

        try:
            with open('transactions.log', "r") as f:
                pass
        except FileNotFoundError:
            with open('transactions.log', "w+") as f:
                f.write("{}")

    def getTrans(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp,
            'status': self.status,
            'content': self.content
        }

    def log(self):
        with open('transactions.log', "r") as log:
            temp = json.load(log)

        temp[self.id] = self.getTrans()
        with open('transactions.log', 'w') as log:
            log.write(json.dumps(temp, indent=4))

a = Transaction(1,2,3)
b = Transaction(1,1,2,1)
print(Transaction.idCounter)