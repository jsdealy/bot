class Queue:
    """A little roll-ur-own queue class just for practice"""
    def __init__(self, size):
        """Initialize the data"""
        self.data = []
        self.size = 5
        self.index = -1

    def __iter__(self):
        return self

    def __next__(self):
        self.index += 1
        if self.index >= len(self.data):
            raise StopIteration
        return self.data[self.index]

    def pop(self):
        """Pop off the first item"""
        self.data = self.data[1:]

    def push(self, thing):
        """Append a new element"""
        if len(self.data) == self.size:
            self.pop()
        self.data += [thing]
