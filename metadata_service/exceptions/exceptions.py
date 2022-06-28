class DataNotFoundException(Exception):

    def __init__(self, dataset_name):
        super().__init__()
        self.message = {
            'type': 'DATA_NOT_FOUND',
            'code': 105,
            'service': 'data-store',
            'data': dataset_name,
            'message': f"No data structure named {dataset_name} was found"
        }

    def to_dict(self):
        return self.message
