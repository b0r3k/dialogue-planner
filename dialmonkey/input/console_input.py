class ConsoleInput:
    def __call__(self, *args, **kwargs):
        return input('USER INPUT> ').strip().lower()
