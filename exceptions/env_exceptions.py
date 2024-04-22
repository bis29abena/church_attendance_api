class EnvironmentNotFound(Exception):
    """Raise an exception if the environment variable is none or not found

    Args:
        Exception (_type_): Inherits from the Exception class
    """    
    def __init__(self, exception_name: str):
        super().__init__(f"{exception_name} is none or not found in the .env file!!!")
        
        self.exception_name: str = exception_name