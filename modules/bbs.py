class BBS:
    def __init__(self):
        self.messages = {}

    def post_message(self, message_id, content):
        """
        Post a message to the BBS.
        """
        if message_id in self.messages:
            raise ValueError("Message ID already exists")
        self.messages[message_id] = content

    def get_message(self, message_id):
        """
        Get a message from the BBS.
        """
        return self.messages.get(message_id, None)

    def delete_message(self, message_id):
        """
        Delete a message from the BBS.
        """
        if message_id not in self.messages:
            raise ValueError("Message ID does not exist")
        del self.messages[message_id]

# Example usage
#bbs = BBS()

# Post a message
#bbs.post_message(1, "Hello, world!")

# Retrieve a message
#print(bbs.get_message(1))  # Output: Hello, world!

# Delete a message
#bbs.delete_message(1)

# Try to retrieve the deleted message
#print(bbs.get_message(1))  # Output: None
