class BBS:
    def __init__(self):
        self.messages = []  # Initialize message queue as an empty list

    def post_message(self, message_id, content):
        """
        Post a message to the BBS.
        """
        self.messages.append((message_id, content))  # Append the message ID and content tuple

    def get_message(self, message_id):
        """
        Get a message from the BBS.
        """
        messages = [msg for msg in self.messages if msg[0] == message_id]
        return messages

    def delete_message(self, message_id):
        """
        Delete a message from the BBS.
        """
        self.messages = [msg for msg in self.messages if msg[0] != message_id]

    def count_messages(self, message_id):
        """
        Count the number of messages for a given message ID.
        """
        return sum(1 for msg in self.messages if msg[0] == message_id)

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
