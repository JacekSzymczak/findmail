class MessageService:
    @staticmethod
    def list_messages(mailbox_id, page, page_size, sort_order):
        """List messages in a mailbox with pagination and sorting."""
        # TODO: Implement direct IMAP connection
        return []

    @staticmethod
    def get_message(mailbox_id, message_id):
        """Retrieve a single message by ID."""
        # TODO: Implement direct IMAP connection
        return None

    @staticmethod
    def delete_message(mailbox_id, message_id):
        """Permanently delete a message by ID."""
        # TODO: Implement direct IMAP connection
        return True
