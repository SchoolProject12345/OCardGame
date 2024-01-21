import pygame


class SingleExecKey():
    def __init__(self, target_key):
        self.key_blocked = False
        self.target_key = target_key

    def handle_key(self, keys):
        if keys[self.target_key] and not self.key_blocked:
            self.key_blocked = True
            return True
        elif not keys[self.target_key]:
            self.key_blocked = False
            return False


class KeyToggle(SingleExecKey):
    def __init__(self, target_key, init_val: bool):
        super().__init__(target_key)
        self.init_val = init_val
    
    def toggle(self):
        self.init_val = not self.init_val

    def update(self, keys):
        if self.handle_key(keys):
            self.toggle()
            return self.init_val
        else:
            return self.init_val
