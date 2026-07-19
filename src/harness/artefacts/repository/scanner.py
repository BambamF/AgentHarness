
class RepositoryScanner:

    def __init__(self):
        self.ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

    def get_root(self) -> str:
        return str(self.ROOT)
