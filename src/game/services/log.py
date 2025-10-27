class MessageLog:
    def __init__(self, capacity=200):
        self.cap = capacity
        self.msgs = []
        self.repeat = 0

    def _wrap(self, msg, w):
        msg_len = len(msg)
        if msg_len > w:
            num_chunks = msg_len // w
            wrapped_msg = []
            for i in range(0, num_chunks + 1):
                wrapped_msg.append(msg[i*w: (i+1)*w])
            return wrapped_msg
        else:
            return [msg]

    def add(self, msg):
        if self.msgs and self.msgs[-1][:len(msg)] == msg:
            self.repeat += 1
            last_msg = self.msgs[-1][:len(msg)]
            last_msg += (f" x{self.repeat + 1}").ljust(5)
            self.msgs[-1] = last_msg
        else:
            self.msgs.append(msg)
            self.repeat = 0
        if len(self.msgs) >= self.cap:
            self.msgs = self.msgs[-self.cap:]
