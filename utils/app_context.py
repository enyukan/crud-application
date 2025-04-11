class AppContext:
    def __init__(self):
        self.logged_in_user = None

    def set_logged_in_user(self, user):
        self.logged_in_user = user

    def get_logged_in_user(self):
        return self.logged_in_user

# Create an instance of AppContext
app_context = AppContext()
